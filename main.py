import fitz  # PyMuPDF - PDF处理库
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime

# ==================== Configuration Loading (Unchanged) ====================
def load_config(path="config.json"):
    # ... (code is identical to previous version, so omitted for brevity)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Configuration file '{path}' not found. Using default settings.")
        return {
            "margins": {"header": 0.08, "footer": 0.08},
            "regex": {
                "title": "^\\s*((\\d+\\.\\d+[\\d\\.]*)|([A-Z]\\.[\\d\\.]*))\\s+[A-Za-z].*",
                "caption": "^(Figure|Fig\\.?|Table|Chart|图|表)\\s+[\\d\\.\\-A-Za-z]+",
                "keyword_heading": "^\\s*(Introduction|Conclusion|Summary|Abstract|References|Appendix)\\s*$"
            },
            "fonts": {"monospace_keywords": ["mono", "courier"]},
            "extraction_options": {"max_toc_level": 2}
        }
    except json.JSONDecodeError:
        print(f"Warning: Configuration file '{path}' is malformed. Using default settings.")
        return {
            "margins": {"header": 0.08, "footer": 0.08},
            "regex": {
                "title": "^\\s*((\\d+\\.\\d+[\\d\\.]*)|([A-Z]\\.[\\d\\.]*))\\s+[A-Za-z].*",
                "caption": "^(Figure|Fig\\.?|Table|Chart|图|表)\\s+[\\d\\.\\-A-Za-z]+",
                "keyword_heading": "^\\s*(Introduction|Conclusion|Summary|Abstract|References|Appendix)\\s*$"
            },
            "fonts": {"monospace_keywords": ["mono", "courier"]},
            "extraction_options": {"max_toc_level": 2}
        }

CONFIG = load_config()

# --- Helper Functions (Unchanged) ---
def clean_filename(name):
    # ... (unchanged)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

TITLE_REGEX = re.compile(CONFIG['regex']['title'])
CAPTION_REGEX = re.compile(CONFIG['regex']['caption'], flags=re.IGNORECASE)
KEYWORD_HEADING_REGEX = re.compile(CONFIG['regex']['keyword_heading'], flags=re.IGNORECASE)

def is_header_or_footer(block_bbox, page_rect):
    # ... (unchanged)
    header_margin = CONFIG['margins']['header']
    footer_margin = CONFIG['margins']['footer']
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin
    return block_bbox.y1 < header_boundary or block_bbox.y0 > footer_boundary

# ==================== ↓↓↓ 新的、更智能的图片查找函数 ↓↓↓ ====================
# ==================== ↓↓↓ 更健壮、更智能的图片查找函数 ↓↓↓ ====================
# ==================== ↓↓↓ 最终版、兼容旧库的图片查找函数 ↓↓↓ ====================
def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """
    一个更智能的函数，用于定位和截取与图注关联的图片。
    它能处理常规图片，也能处理由文本和矢量图形构成的复杂图表。
    """
    # 1. 尝试查找紧邻的上一个“图片块”(type 1)
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1:
            xref = prev_block["number"]
            if xref not in processed_blocks:
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image: return None
                    filename = f"page_{page.number+1}_img_{xref}.{base_image['ext']}"
                    with open(os.path.join(image_dir, filename), "wb") as f:
                        f.write(base_image["image"])
                    processed_blocks.add(xref)
                    return {"filename": filename, "bbox": fitz.Rect(prev_block["bbox"])}
                except Exception:
                    pass

    # 2. 启动“智能截图”模式，处理矢量图/文本图
    caption_block = blocks[caption_block_idx]
    caption_bbox = fitz.Rect(caption_block["bbox"])

    # 初始搜索区域
    search_area = fitz.Rect(
        page.rect.x0, caption_bbox.y0 - page.rect.height * 0.5,
        page.rect.x1, caption_bbox.y1
    )
    search_area.intersect(page.rect)

    # 收集所有可能是图表组件的边界框
    component_bboxes = []

    # 查找此区域内的所有文本块
    potential_blocks = page.get_text("dict", clip=search_area)["blocks"]
    for block in potential_blocks:
        if block["type"] == 0:
            block_text = "".join("".join(s['text'] for s in l['spans']) for l in block['lines'])
            # 过滤掉普通段落和图注自身
            if len(block_text.split()) > 20 or fitz.Rect(block['bbox']) == caption_bbox:
                continue
            component_bboxes.append(fitz.Rect(block["bbox"]))

    # 查找此区域内的所有矢量绘图
    drawings = page.get_drawings()
    for draw in drawings:
        if draw['rect'].intersects(search_area):
            if draw['rect'].width < page.rect.width * 0.9:
                component_bboxes.append(draw['rect'])

    if not component_bboxes:
        return None

    # 更安全的边界框合并方法
    final_image_bbox = fitz.Rect()
    for bbox in component_bboxes:
        final_image_bbox.include_rect(bbox)

    # 确保合并后的边界框是有效的
    if final_image_bbox.is_empty or final_image_bbox.width == 0 or final_image_bbox.height == 0:
        return None

    # ==================== ↓↓↓ 关键修复：兼容旧版 PyMuPDF ↓↓↓ ====================
    # 为兼容旧版PyMuPDF，手动实现 'inflate' 的功能，即向外扩展边界
    delta = 5
    final_image_bbox.x0 -= delta
    final_image_bbox.y0 -= delta
    final_image_bbox.x1 += delta
    final_image_bbox.y1 += delta
    # ==================== ↑↑↑ 修复结束 ↑↑↑ ====================
    
    final_image_bbox.intersect(page.rect) # 确保不超过页面

    if final_image_bbox.is_empty or final_image_bbox.height < 5:
        return None

    filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
    pix = page.get_pixmap(clip=final_image_bbox, dpi=200)
    pix.save(os.path.join(image_dir, filename))

    return {"filename": filename, "bbox": final_image_bbox}

def get_markdown_from_block(block, true_headings=None):
    # ... (This function is now perfect and requires no changes)
    if true_headings is None:
        true_headings = set()
        
    if block['type'] != 0 or not block.get('lines'):
        return ""

    full_text = "\n".join("".join(s['text'] for s in l['spans']) for l in block['lines'])
    if not full_text.strip():
        return ""
        
    split_marker = "<\r\n_SPLIT_HERE_\r\n>"
    processed_text = re.sub(
        r'(?m)(^|(?<=\n))(' + CONFIG['regex']['title'] + r')',
        lambda m: f"{split_marker}{m.group(2)}",
        full_text
    )
    
    sub_blocks_text = processed_text.split(split_marker)

    output_parts = []
    for sub_text in sub_blocks_text:
        sub_text = sub_text.strip()
        if not sub_text:
            continue

        clean_sub_text = re.sub(r'^\s*[\d\.\sA-Z]+[a-z]?\s*', '', sub_text).strip()
        
        is_true_heading = False
        if clean_sub_text and true_headings:
            for true_heading in true_headings:
                if true_heading in clean_sub_text and len(clean_sub_text) < (len(true_heading) + 30):
                    is_true_heading = True
                    break
        
        if is_true_heading:
            output_parts.append(f"## {sub_text.replace(chr(10), ' ')}\n\n")
            continue

        if KEYWORD_HEADING_REGEX.match(sub_text):
            output_parts.append(f"## {sub_text.replace(chr(10), ' ')}\n\n")
            continue

        mono_fonts = CONFIG['fonts']['monospace_keywords']
        is_monospace_block = all(
            any(keyword in span['font'].lower() for keyword in mono_fonts)
            for line in block['lines'] for span in line['spans'] if 'font' in span
        )
        if is_monospace_block and len(sub_text.splitlines()) > 1:
            output_parts.append(f"```\n{sub_text}\n```\n\n")
            continue

        list_match = re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', sub_text)
        if list_match:
            lines = sub_text.split('\n')
            output_lines = []
            for line in lines:
                clean_line = line.strip()
                if not clean_line: continue
                if re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', clean_line):
                    output_lines.append(re.sub(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', '* ', clean_line))
                else:
                    output_lines.append("  " + clean_line)
            output_parts.append("\n".join(output_lines) + "\n\n")
            continue
            
        output_parts.append(sub_text.replace('\n', ' ').replace('\r', '') + "\n\n")

    return "".join(output_parts)


# --- Main Processing Function (Updated) ---
# --- Main Processing Function (Updated and Corrected) ---
def run_extraction_stable(pdf_path, output_dir="mybook"):
    """
    处理PDF文件，使用所有书签级别获取准确的标题白名单，
    同时保持一个2级的目录结构。
    """
    if os.path.exists(output_dir):
        print(f"Old output directory '{output_dir}' found. Deleting...")
        shutil.rmtree(output_dir)
        print("Old directory deleted.")
    os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    original_toc = doc.get_toc()
    if not original_toc:
        print("Error: No bookmarks (TOC) found in the document.")
        return

    # CORE CHANGE 1: 使用过滤后的TOC仅用于文件结构
    file_structure_toc = [item for item in original_toc if item[0] <= CONFIG.get("extraction_options", {}).get("max_toc_level", 2)]
    print(f"Processing {len(file_structure_toc)} bookmarks for file structure (from original {len(original_toc)}).")
    
    markdown_files_list = []
    level_paths = {}

    # 遍历 file_structure_toc 来创建文件和文件夹
    for i, item in enumerate(file_structure_toc):
        level, title, start_page = item
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        print(f"{'  ' * (level-1)}-> Processing Chapter/File: {title}")

        # 确定当前章节的页面范围
        end_page = doc.page_count + 1
        for next_item in file_structure_toc[i+1:]:
            if next_item[0] <= level:
                end_page = next_item[2]
                break
        
        # CORE CHANGE 2: 从完整的 original_toc 构建白名单
        true_heading_whitelist = set()
        try:
            original_toc_index = original_toc.index(item)
            for j in range(original_toc_index + 1, len(original_toc)):
                sub_item = original_toc[j]
                if sub_item[0] > level:
                    clean_title = re.sub(r'^\s*[\d\.\sA-Z]+[a-z]?\s*', '', sub_item[1]).strip()
                    if len(clean_title) > 4:
                        true_heading_whitelist.add(clean_title)
                elif sub_item[0] <= level:
                    break
        except ValueError:
            print(f"Warning: Could not find item '{title}' in original TOC. Whitelist may be incomplete.")

        if true_heading_whitelist:
             print(f"    - Found {len(true_heading_whitelist)} sub-headings for whitelist (e.g., {list(true_heading_whitelist)[:3]}...).")

        if start_page >= end_page:
            is_parent_node = (i + 1 < len(file_structure_toc)) and (file_structure_toc[i+1][0] > level)
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
        
        chapter_content = f"# {title}\n\n"
        processed_img_xrefs = set()

        # ==================== ↓↓↓ 关键修复区：所有页面处理逻辑必须在此循环内 ↓↓↓ ====================
        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            processed_block_indices = set()
            page_content_parts = {}
            ignored_text_areas = []

            # 图片和图注处理 (更新后的复杂情况处理逻辑)
            caption_blocks_indices = set()
            for idx, b in enumerate(blocks):
                if b["type"] == 0 and "lines" in b:
                    block_text = "\n".join("".join(s['text'] for s in l['spans']) for l in b['lines'])
                    if CAPTION_REGEX.search(block_text.strip()):
                        caption_blocks_indices.add(idx)

            # 现在，处理找到的图注块
            for idx in sorted(list(caption_blocks_indices)):
                b = blocks[idx]
                full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                # 从完整文本中提取干净的图注（移除图表内容）
                caption_match = CAPTION_REGEX.search(full_caption)
                clean_caption = caption_match.group(0).strip() if caption_match else full_caption
                short_alt = ' '.join(clean_caption.split()[:5]) + "..."
                
                image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                
                if image_info:
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    page_content_parts[idx] = f"![{short_alt}]({relative_path})\n*{clean_caption}*\n\n"
                    if image_info.get("bbox"): 
                        ignored_text_areas.append(image_info["bbox"])
                        # 确保图注本身的文本块也被忽略
                        ignored_text_areas.append(fitz.Rect(b["bbox"]))
                else:
                    page_content_parts[idx] = f"*{clean_caption}*\n\n"
                
                processed_block_indices.add(idx)

            # 文本块处理
            for idx, b in enumerate(blocks):
                if idx in processed_block_indices or b['type'] != 0: continue
                block_bbox = fitz.Rect(b["bbox"])
                if is_header_or_footer(block_bbox, page.rect): continue
                if any(area.intersects(block_bbox) for area in ignored_text_areas): continue
                
                markdown_text = get_markdown_from_block(b, true_headings=true_heading_whitelist)
                
                if markdown_text:
                    page_content_parts[idx] = markdown_text
                processed_block_indices.add(idx)

            # 无图注图片处理 (逻辑不变)
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
                            content = f"![Uncaptioned image on page {page_num+1} xref {xref}]({relative_path})\n\n"
                            page_content_parts[img_block_idx] = content
                            processed_img_xrefs.add(xref)
                        except Exception as e:
                            print(f"Warning: Could not process uncaptioned image xref {xref} on page {page_num+1}. Error: {e}")

            # 按顺序组合页面内容
            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]
        
        # ==================== ↑↑↑ 关键修复区结束 ↑↑↑ ====================

        chapter_content = re.sub(r'\n{3,}', '\n\n', chapter_content)
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)

    # 元数据生成 (逻辑不变)
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    book_data = {
        "kind": "Book", "title": book_title, "version": "0.1.0",
        "authors": book_authors, "translators": ["Generated by Script"],
        "year": str(datetime.now().year), "src": ".", "contents": markdown_files_list
    }
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: 
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    print("\nExtraction complete!")
    doc.close()

if __name__ == "__main__":
    pdf_file = "your_file.pdf"
    if os.path.exists(pdf_file):
        run_extraction_stable(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")