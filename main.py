import fitz  # PyMuPDF 库，用于处理PDF文件
import os
import re
import json
import shutil  # 用于文件和目录操作，如删除目录树
from urllib.parse import quote  # 用于URL编码，确保文件名在URL中安全
from datetime import datetime

# ==================== 配置加载 ====================
def load_config(path="config.json"):
    """加载JSON配置文件。如果文件不存在或格式错误，则使用默认配置。"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"警告: 配置文件 '{path}' 未找到或格式错误。将使用默认设置。")
        # 简化后的默认配置，只保留必要部分
        return {
            "margins": {"header": 0.08, "footer": 0.08},
            "regex": {
                "caption": "^(Figure|Fig\\.?|Table|Chart|图|表)\\s+[\\d\\.\\-A-Za-z]+"
            }
        }

CONFIG = load_config()

# ==================== 辅助函数 (保留核心部分) ====================
def clean_filename(name):
    """清理字符串，使其成为一个安全的文件名。"""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

# 编译正则表达式以提高效率
# (已简化) 只保留图表标题的正则表达式
CAPTION_REGEX = re.compile(CONFIG['regex']['caption'], flags=re.IGNORECASE)

def is_header_or_footer(block_bbox, page_rect):
    """根据块的位置判断它是否位于页眉或页脚区域。"""
    header_margin = CONFIG['margins']['header']
    footer_margin = CONFIG['margins']['footer']
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin
    return block_bbox.y1 < header_boundary or block_bbox.y0 > footer_boundary

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_xrefs):
    """为给定的图表标题寻找关联的图像或图表。 (此函数逻辑不变，非常核心)"""
    # 策略一：检查紧邻标题之前的块是否是光栅图像
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1:  # type 1 表示图像块
            xref = prev_block["number"]
            if xref not in processed_xrefs:
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image: return None
                    filename = f"page_{page.number+1}_img_{xref}.{base_image['ext']}"
                    with open(os.path.join(image_dir, filename), "wb") as f: f.write(base_image["image"])
                    processed_xrefs.add(xref)
                    return {"filename": filename, "bbox": fitz.Rect(prev_block["bbox"])}
                except Exception: return None

    # 策略二：如果前面不是图像，则假定是矢量图，在标题上方区域进行截图
    caption_bbox = fitz.Rect(blocks[caption_block_idx]["bbox"])
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
    search_area.intersect(page.rect)

    if not search_area.is_empty and search_area.height > 10:
        filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
        pix = page.get_pixmap(clip=search_area, dpi=150)
        pix.save(os.path.join(image_dir, filename))
        return {"filename": filename, "bbox": search_area}
    
    return None

# ==================== 新增的启发式检测函数 ====================
def is_likely_diagram_block(block_text):
    """
    通过启发式规则猜测一个文本块是否为图表的一部分。
    """
    # 规则1: 文本中包含多个箭头符号 "->" 或 "-->"
    if block_text.count('->') >= 2 or block_text.count('-->') >= 2:
        return True
    
    # 规则2: 文本中包含多个方框绘制字符
    box_chars = ['|', '├', '─', '└', '┌']
    if sum(block_text.count(c) for c in box_chars) > 5:
        return True
        
    # 规则3: 文本非常稀疏（空格比例很高），且不止一行
    lines = block_text.split('\n')
    if len(lines) > 2:
        non_space_chars = len(block_text.replace(' ', '').replace('\n', ''))
        total_chars = len(block_text)
        if total_chars > 0 and non_space_chars / total_chars < 0.4:
            return True

    return False


# --- 核心处理逻辑 (已大幅简化) ---
def process_block_to_markdown(block):
    """
    极简的块到Markdown转换器。
    只处理图表标题和普通段落。
    """
    if block['type'] != 0 or not block.get('lines'): return ""
    
    # 提取块内的全部文本
    full_text = "\n".join("".join(s['text'] for s in l['spans']) for l in block['lines']).strip()
    if not full_text: return ""

    # 检查是否为图表标题
    if CAPTION_REGEX.match(full_text):
        # 如果是图表标题，用斜体表示，并替换换行符
        return f"*{full_text.replace(chr(10), ' ')}*\n\n"
    else:
        # 其他所有文本都视为普通段落，将换行符替换为空格
        return full_text.replace('\n', ' ').replace('\r', '') + "\n\n"

# ==================== 主提取函数 (已简化) ====================
def run_extraction(pdf_path, output_dir="mybook"):
    """执行PDF提取的主函数。"""
    if os.path.exists(output_dir): shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    doc = fitz.open(pdf_path)
    original_toc = doc.get_toc()
    if not original_toc: print("错误: 未找到书签(TOC)。"); doc.close(); return
    
    # (已简化) 只使用一级书签作为章节划分依据
    chapter_toc = [item for item in original_toc if item[0] == 1]
    if not chapter_toc: print("错误: 未找到一级书签。"); doc.close(); return
    
    print(f"找到 {len(chapter_toc)} 个顶级章节待处理。")
    markdown_files_list = []
    
    for i, chapter_item in enumerate(chapter_toc):
        level, title, start_page = chapter_item
        safe_title = clean_filename(title)
        print(f"\n正在处理章节: '{title}' (第 {start_page} 页)")

        end_page = doc.page_count + 1
        if i + 1 < len(chapter_toc): end_page = chapter_toc[i+1][2]
        print(f"  - 内容范围从第 {start_page} 页到第 {end_page - 1} 页。")

        # (已简化) 不再需要复杂的标题检测，所以这部分逻辑已移除

        current_chapter_dir = os.path.join(output_dir, safe_title)
        os.makedirs(current_chapter_dir, exist_ok=True)
        output_filepath = os.path.join(current_chapter_dir, f"{safe_title}.md")
        current_image_dir = os.path.join(current_chapter_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)
        chapter_content = f"# {title}\n\n"
        processed_img_xrefs = set()
        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            page_data = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
            blocks = sorted(page_data.get("blocks", []), key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            # 阶段一: 识别所有图像/图表区域以忽略其内部文本 (逻辑不变)
            ignored_areas = []
            caption_image_map = {}

            for b in blocks:
                if b['type'] == 1:
                    ignored_areas.append(fitz.Rect(b['bbox']))
            
            for idx, b in enumerate(blocks):
                if b['type'] == 0:
                    text = "".join("".join(s['text'] for s in l['spans']) for l in b.get('lines', [])).strip()
                    if CAPTION_REGEX.match(text):
                        image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                        if image_info and image_info.get("bbox"):
                            caption_image_map[idx] = image_info
                            area_to_ignore = fitz.Rect(image_info["bbox"])
                            area_to_ignore += (-5, -5, 5, 5)
                            ignored_areas.append(area_to_ignore)
          
            # 阶段二: 生成Markdown, 跳过忽略区域内的文本
            page_content_parts = {}

            for idx, b in enumerate(blocks):
                if b['type'] != 0: continue
                block_bbox = fitz.Rect(b['bbox'])
                if is_header_or_footer(block_bbox, page.rect): continue
                
                if any(area.intersects(block_bbox) for area in ignored_areas):
                    if idx not in caption_image_map:
                         continue # 是图表内部的文本，跳过
                
                image_md = ""
                if idx in caption_image_map:
                    image_info = caption_image_map[idx]
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    caption_text = "".join("".join(s['text'] for s in l['spans']) for l in b.get('lines', [])).strip()
                    short_alt = ' '.join(caption_text.split()[:5]) + "..."
                    image_md = f"![{short_alt}]({relative_path})\n"

                # (已简化) 直接调用简化的块处理函数
                markdown_text = process_block_to_markdown(b)
                
                if markdown_text:
                    page_content_parts[idx] = image_md + markdown_text
            
            # 处理无标题的图片 (逻辑不变)
            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_img_xrefs:
                    img_block_idx = -1
                    for idx, b in enumerate(blocks):
                        if b.get("type") == 1 and b.get("number") == xref: img_block_idx = idx; break
                    if img_block_idx != -1 and img_block_idx not in page_content_parts:
                        try:
                            base_image = doc.extract_image(xref)
                            if not base_image: continue
                            image_filename = f"page_{page_num+1}_uncaptioned_img_{xref}.{base_image['ext']}"
                            relative_path = os.path.join("images", quote(image_filename))
                            with open(os.path.join(current_image_dir, image_filename), "wb") as f: f.write(base_image["image"])
                            page_content_parts[img_block_idx] = f"![Uncaptioned image on page {page_num+1}]({relative_path})\n\n"
                            processed_img_xrefs.add(xref)
                        except Exception as e: print(f"警告: 无法处理无标题图片 xref {xref} 在页面 {page_num+1}。错误: {e}")

            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]

        chapter_content = re.sub(r'\n{3,}', '\n\n', chapter_content) # 清理多余的空行
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)
    
    # 生成 book.json 元数据 (逻辑不变)
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    book_data = {"kind": "Book", "title": book_title, "version": "0.1.0", "authors": book_authors, "translators": ["Generated by Script"], "year": str(datetime.now().year), "src": ".", "contents": markdown_files_list}
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: json.dump(book_data, f, ensure_ascii=False, indent=2)

    doc.close()
    print("\n提取完成！")

if __name__ == "__main__":
    pdf_file = "your_file.pdf" 
    if os.path.exists(pdf_file):
        run_extraction(pdf_file)
    else:
        print(f"错误: 文件 '{pdf_file}' 未找到。")