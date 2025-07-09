import fitz  # PyMuPDF - PDF处理库
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime
from collections import Counter

# --- 辅助函数 ---

def clean_filename(name):
    """清理文件名中的非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"
# REGEX for matching typical heading formats like "1.2", "1.2.3", "A.1", "Chapter 1" etc.
TITLE_REGEX = re.compile(
    r'^\s*('
    r'(Chapter|Part|Section|Appendix|Kapitel|Teil)\s+[\dIVXLC]+\s*[:.\-]?|'  # "Chapter 1", "Part A"
    r'(\d+(\.\d+)*\.?)|'  # "3.1", "3.2.1", "4.2."
    r'[A-Z]\.[\d\.]*'  # "A.1", "B.2.3"
    r')\s+', 
    flags=re.IGNORECASE
)

def is_header_or_footer(block_bbox, page_rect, header_margin=0.12, footer_margin=0.12):
    """判断文本块是否位于页眉或页脚区域"""
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin
    return block_bbox.y1 < header_boundary or block_bbox.y0 > footer_boundary

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """为标题查找对应的图像"""
    # 检查前一个块是否是图像
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1:
            xref = prev_block["number"]
            if xref not in processed_blocks:
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image: return None
                    filename = f"page_{page.number+1}_img_{xref}.{base_image['ext']}"
                    with open(os.path.join(image_dir, filename), "wb") as f: f.write(base_image["image"])
                    processed_blocks.add(xref)
                    return {"filename": filename, "bbox": fitz.Rect(prev_block["bbox"])}
                except Exception: return None
    
    # 在标题上方搜索矢量图或组合图
    caption_bbox = fitz.Rect(blocks[caption_block_idx]["bbox"])
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
    search_area.intersect(page.rect)
    
    if not search_area.is_empty and search_area.height > 10:
        filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
        pix = page.get_pixmap(clip=search_area, dpi=150)
        pix.save(os.path.join(image_dir, filename))
        return {"filename": filename, "bbox": search_area}
    return None

# --- 新增的Markdown格式推断函数 ---

def analyze_page_fonts(page):
    """
    分析页面上的字体大小，确定正文和各级标题的字体大小。
    返回: (正文字体大小, {标题字体大小: 标题级别})
    """
    sizes = []
    for block in page.get_text("dict")["blocks"]:
        if block['type'] == 0: # 文本块
            for line in block['lines']:
                for span in line['spans']:
                    sizes.append(round(span['size']))
    
    if not sizes:
        return 12, {} # 默认值

    # 计算最常见的字体大小作为正文大小
    most_common_size = Counter(sizes).most_common(1)[0][0]
    
    # 找出所有比正文大的字体大小，作为标题大小
    heading_sizes = sorted([s for s in set(sizes) if s > most_common_size + 1], reverse=True)
    
    # 创建标题级别映射
    heading_map = {size: f"##{'#' * i}" for i, size in enumerate(heading_sizes)}
    
    return most_common_size, heading_map

def get_markdown_from_block(block, body_size, heading_map):
    """
    根据文本块的属性（字体、大小、内容）推断其Markdown格式。
    **New:** Now includes logic to split a block if its first line is a heading.
    """
    if block['type'] != 0 or not block.get('lines'):
        return ""

    # --- NEW: Block Splitting Logic ---
    # Check if the first line of the block looks like a standalone heading.
    first_line = block['lines'][0]
    first_line_spans = first_line.get('spans', [])
    if not first_line_spans:
        return "" # Empty line

    first_line_text = "".join(s['text'] for s in first_line_spans).strip()
    first_line_size = round(first_line_spans[0]['size'])
    is_first_line_bold = all(s['flags'] & 16 for s in first_line_spans) # Check if all spans are bold

    # Heuristic for a heading-like first line:
    # 1. It matches our title regex, OR it's significantly larger than body text.
    # 2. It's relatively short.
    # 3. It doesn't look like a list item starting a long paragraph.
    is_potential_heading = (
        (TITLE_REGEX.match(first_line_text) and is_first_line_bold) or 
        (first_line_size in heading_map)
    ) and len(first_line_text) < 150 and not first_line_text.endswith(('.', ','))

    if is_potential_heading and len(block['lines']) > 1:
        # This block contains a heading AND a subsequent paragraph. Split them.
        heading_level = heading_map.get(first_line_size, '##') # Use ## as default for regex match
        
        # Format the heading
        heading_md = f"{heading_level} {first_line_text}\n\n"
        
        # Format the rest of the block as a normal paragraph
        rest_of_block = {'type': 0, 'lines': block['lines'][1:]}
        # Recursively call this function for the rest, but it will now fail the split-check
        # and be treated as a normal paragraph block.
        paragraph_md = get_markdown_from_block(rest_of_block, body_size, heading_map)
        
        return heading_md + paragraph_md

    # --- Fallback to Original Logic (if no split is needed) ---
    # This handles blocks that are entirely a heading, entirely a paragraph, a list, etc.
    
    full_text_parts = []
    is_monospace_block = all(
        ("mono" in span['font'].lower() or "courier" in span['font'].lower())
        for line in block['lines'] for span in line['spans']
    )

    for line in block['lines']:
        line_parts = []
        for span in line['spans']:
            text = span['text']
            if span['flags'] & 16: text = f"**{text}**" # Bold
            if span['flags'] & 2: text = f"*{text}*"   # Italic
            line_parts.append(text)
        full_text_parts.append("".join(line_parts))
    
    full_text = "\n".join(full_text_parts).strip()
    if not full_text: return ""

    # Code block detection
    if is_monospace_block and len(full_text.splitlines()) > 1:
        return f"```\n{full_text}\n```\n\n"

    # Whole-block heading detection (for cases like "Introduction")
    block_size = round(block['lines'][0]['spans'][0]['size'])
    if block_size in heading_map and len(full_text) < 150 and not full_text.strip().endswith('.'):
        return f"{heading_map[block_size]} {full_text}\n\n"

    # List detection
    list_match = re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', full_text)
    if list_match:
        lines = full_text.split('\n')
        first_line = lines[0][list_match.end():].strip()
        rest_of_lines = "\n".join(["  " + l.strip() for l in lines[1:]])
        return f"* {first_line}\n{rest_of_lines}\n"

    # Default paragraph
    return full_text.replace('\n', ' ') + "\n\n"


# --- 主处理函数 (已更新) ---
def run_extraction_stable(pdf_path, output_dir="mybook"):
    """
    处理PDF文件，提取1级和2级书签内容，并智能推断Markdown格式。
    """
    if os.path.exists(output_dir):
        print(f"发现旧输出目录 '{output_dir}'。正在删除...")
        shutil.rmtree(output_dir)
        print("旧目录已删除。")
    os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    original_toc = doc.get_toc()
    if not original_toc:
        print("错误: 未找到书签。")
        return

    toc = [item for item in original_toc if item[0] <= 2]
    print(f"处理 {len(toc)} 个书签(从原始 {len(original_toc)} 个过滤到最多2级)。")

    markdown_files_list = []
    level_paths = {}
    CAPTION_REGEX = re.compile(r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+', flags=re.IGNORECASE)

    for i, item in enumerate(toc):
        level, title, start_page = item
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        print(f"{'  ' * (level-1)}-> 处理: {title}")

        is_parent_node = (i + 1 < len(toc)) and (toc[i+1][0] > level)
        end_page = doc.page_count + 1
        for next_item in toc[i+1:]:
            if next_item[0] <= level:
                end_page = next_item[2]
                break

        if start_page >= end_page:
            print(f"{'  ' * (level-1)}  - 跳过空章节。")
            if is_parent_node: 
                current_content_dir = os.path.join(output_dir, safe_title)
                os.makedirs(current_content_dir, exist_ok=True)
            continue
        
        parent_dir_parts = [level_paths[l] for l in range(1, level)]
        parent_dir = os.path.join(output_dir, *parent_dir_parts)

        if level == 1:
            current_content_dir = os.path.join(parent_dir, safe_title)
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")
        else:
            current_content_dir = parent_dir
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")

        md_file_containing_dir = os.path.dirname(output_filepath)
        current_image_dir = os.path.join(md_file_containing_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)
        
        chapter_content = ""
        processed_img_xrefs = set()

        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            # **核心改动：先分析字体，再处理内容**
            body_size, heading_map = analyze_page_fonts(page)
            
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            processed_block_indices = set()
            page_content_parts = {}
            ignored_text_areas = []

            # 1. 优先处理图片和图注
            caption_blocks_indices = {idx for idx, b in enumerate(blocks) if b["type"] == 0 and "lines" in b and CAPTION_REGEX.match(''.join(s["text"] for s in b["lines"][0]["spans"]).strip())}
            for idx in sorted(list(caption_blocks_indices)):
                b = blocks[idx]
                full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                short_alt = ' '.join(full_caption.split()[:4]) + "..."
                image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                content = ""
                if image_info:
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    content = f"![{short_alt}]({relative_path})\n*{full_caption}*\n\n"
                    if image_info.get("bbox"):
                        ignored_text_areas.append(image_info["bbox"])
                else:
                    content = f"*{full_caption}*\n\n"
                page_content_parts[idx] = content
                processed_block_indices.add(idx)

            # 2. 处理所有文本块 (使用新的格式化函数)
            for idx, b in enumerate(blocks):
                # 如果块已经被处理过（比如，被识别为图注），或者不是文本块，就跳过
                if idx in processed_block_indices or b['type'] != 0:
                    continue
                
                block_bbox = fitz.Rect(b["bbox"])

                # 忽略页眉页脚
                if is_header_or_footer(block_bbox, page.rect):
                    continue

                # 忽略图片区域内的文本
                if any(area.intersects(block_bbox) for area in ignored_text_areas):
                    continue

                # **核心逻辑：直接将块转换为Markdown**
                markdown_text = get_markdown_from_block(b, body_size, heading_map)
                if markdown_text:
                    page_content_parts[idx] = markdown_text
                
                # 标记此块已处理
                processed_block_indices.add(idx)
            # 3. 处理未被图注关联的图片
            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_img_xrefs:
                    img_block_idx = -1
                    for idx, b in enumerate(blocks):
                        if b.get("type") == 1 and b.get("number") == xref:
                            img_block_idx = idx
                            break
                    
                    if img_block_idx != -1 and img_block_idx not in page_content_parts:
                        try:
                            base_image = doc.extract_image(xref)
                            if not base_image: continue
                            image_filename = f"page_{page_num+1}_uncaptioned_img_{xref}.{base_image['ext']}"
                            relative_path = os.path.join("images", quote(image_filename))
                            with open(os.path.join(current_image_dir, image_filename), "wb") as f: f.write(base_image["image"])
                            content = f"![未加标题的图片 第{page_num+1}页 xref {xref}]({relative_path})\n\n"
                            page_content_parts[img_block_idx] = content
                            processed_img_xrefs.add(xref)
                        except Exception as e:
                            print(f"警告: 无法处理未加标题的图片 xref {xref} 在第 {page_num+1} 页。错误: {e}")

            # 4. 按顺序组合页面内容
            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]

        # 写入Markdown文件
        # 清理多余的换行符，但保留代码块中的
        chapter_content = re.sub(r'\n{3,}', '\n\n', chapter_content)
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)

    # 生成书籍元数据
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["未知作者"]
    book_data = {
        "kind": "Book", "title": book_title, "version": "0.1.0",
        "authors": book_authors, "translators": ["由脚本生成"],
        "year": str(datetime.now().year), "src": ".", "contents": markdown_files_list
    }
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: 
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    print("\n提取完成!")
    doc.close()

if __name__ == "__main__":
    pdf_file = "your_file.pdf" # 请将这里替换成你的PDF文件名
    if os.path.exists(pdf_file):
        run_extraction_stable(pdf_file)
    else:
        print(f"错误: 文件 '{pdf_file}' 未找到。请确保文件在当前目录下，或者提供完整路径。")