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

def are_bboxes_close(rect1, rect2, max_gap=40):
    """
    检查两个矩形边界框是否足够接近。
    如果它们之间的水平或垂直间隙小于 max_gap，则认为它们是接近的。
    """
    # 计算水平间隙
    h_gap = max(0, rect1.x0 - rect2.x1, rect2.x0 - rect1.x1)
    # 计算垂直间隙
    v_gap = max(0, rect1.y0 - rect2.y1, rect2.y0 - rect1.y1)
    
    # 如果一个矩形在另一个的水平或垂直投影范围内，且另一个维度的间隙不大，则认为接近
    return (h_gap < max_gap and v_gap < rect1.height + rect2.height + max_gap) or \
           (v_gap < max_gap and h_gap < rect1.width + rect2.width + max_gap)



# ==================== ↓↓↓ 新的、更智能的图片查找函数 ↓↓↓ ====================
# ==================== ↓↓↓ 更健壮、更智能的图片查找函数 ↓↓↓ ====================
# ==================== ↓↓↓ 最终版、兼容旧库的图片查找函数 ↓↓↓ ====================
# ==================== ↓↓↓ 最终优化版：引入聚类算法的图片查找函数 ↓↓↓ ====================
def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """
    一个高度智能的函数，使用聚类算法来精确定位复杂图表的边界。
    """
    # (步骤 1: 查找常规图片 的代码保持不变)
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

    # (步骤 2: 智能截图模式 的代码进行优化)
    caption_block = blocks[caption_block_idx]
    caption_bbox = fitz.Rect(caption_block["bbox"])
    
    # 缩小初始搜索范围，提高效率
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - page.rect.height * 0.4, page.rect.x1, caption_bbox.y0)
    search_area.intersect(page.rect)

    # 收集所有潜在的图表组件
    potential_components = []
    potential_blocks = page.get_text("dict", clip=search_area)["blocks"]
    for block in potential_blocks:
        if block["type"] == 0:
            block_text = "".join("".join(s['text'] for s in l['spans']) for l in block['lines'])
            if len(block_text.split()) > 20: continue
            potential_components.append(fitz.Rect(block["bbox"]))
    
    drawings = page.get_drawings()
    for draw in drawings:
        if draw['rect'].intersects(search_area) and draw['rect'].width < page.rect.width * 0.9:
            potential_components.append(draw['rect'])

    if not potential_components:
        return None

    # ↓↓↓ 核心优化：聚类算法，找到与图注最相关的组件集群 ↓↓↓
    
    # 1. 找到离图注最近的“种子”组件
    try:
        seed_component = min(potential_components, key=lambda r: abs(r.y1 - caption_bbox.y0))
    except ValueError:
        return None

    # 2. 使用广度优先搜索（BFS）或类似的逻辑进行聚类
    cluster = [seed_component]
    to_process = [seed_component]
    potential_components.remove(seed_component)
    
    head = 0
    while head < len(to_process):
        current_comp = to_process[head]
        head += 1
        
        remaining_components = []
        for other_comp in potential_components:
            # 使用我们新的辅助函数来判断是否足够近
            if are_bboxes_close(current_comp, other_comp, max_gap=40): # max_gap可以微调
                cluster.append(other_comp)
                to_process.append(other_comp)
            else:
                remaining_components.append(other_comp)
        potential_components = remaining_components
    
    # 3. 计算最终集群的边界框
    if not cluster:
        return None
        
    final_image_bbox = fitz.Rect(cluster[0])
    for bbox in cluster[1:]:
        final_image_bbox.include_rect(bbox)
        
    # (后续代码保持不变，但现在 final_image_bbox 会非常精准)
    if final_image_bbox.is_empty or final_image_bbox.width == 0 or final_image_bbox.height == 0:
        return None
        
    # 手动实现 'inflate' 功能
    delta = 8 # 可以给精准的框多一点边距
    final_image_bbox.x0 -= delta
    final_image_bbox.y0 -= delta
    final_image_bbox.x1 += delta
    final_image_bbox.y1 += delta
    
    final_image_bbox.intersect(page.rect)

    if final_image_bbox.is_empty or final_image_bbox.height < 5:
        return None

    filename = f"page_{page.number+1}_vector_cluster_{int(caption_bbox.y0)}.png"
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
# ==================== ↓↓↓ 最终版：带有“否决权”上下文检查的主函数 ↓↓↓ ====================
# ==================== ↓↓↓ 最终版：支持合并子章节的完整主函数 ↓↓↓ ====================
def run_extraction_stable(pdf_path, output_dir="mybook"):
    """
    处理PDF文件。根据配置，可以选择将子章节合并到父章节中，
    并包含所有最新的修复和优化。
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

    # --- 1. 新增：读取配置 ---
    extraction_opts = CONFIG.get("extraction_options", {})
    max_toc_level = extraction_opts.get("max_toc_level", 2)
    merge_subchapters = extraction_opts.get("merge_subchapters_into_parent", False)

    # --- 2. 核心修改：根据配置决定要处理的目录项 ---
    if merge_subchapters:
        # 如果要合并，我们只关心第1级目录。它们将成为我们唯一的处理单元。
        file_structure_toc = [item for item in original_toc if item[0] == 1]
        print("Info: Merging subchapters enabled. Processing level-1 chapters only.")
    else:
        # 保持原有行为，处理1级和2级目录。
        file_structure_toc = [item for item in original_toc if item[0] <= max_toc_level]
        print("Info: Merging subchapters disabled. Creating separate files for subchapters.")

    markdown_files_list = []
    level_paths = {}

    # 遍历我们决定要处理的目录项 (file_structure_toc)
    for i, item in enumerate(file_structure_toc):
        level, title, start_page = item
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        print(f"{'  ' * (level-1)}-> Processing Chapter/File: {title}")

        # --- 3. 核心修改：更鲁棒地计算页面范围 ---
        # 无论是否合并，都在原始TOC中寻找下一个同级或更高级的目录，以确定结束页
        end_page = doc.page_count + 1
        try:
            current_item_index_in_original = original_toc.index(item)
            for next_item in original_toc[current_item_index_in_original + 1:]:
                if next_item[0] <= level:
                    end_page = next_item[2]
                    break
        except ValueError:
            # 如果在原始TOC中找不到，这是一个不太可能发生的边缘情况，但为了安全还是处理一下
            print(f"Warning: Could not find '{title}' in original TOC for end-page calculation.")


        # --- 标题白名单逻辑保持不变，它依然非常有用！---
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
        
        # --- 文件和目录的创建逻辑保持不变，它足够健壮 ---
        parent_dir_parts = [level_paths[l] for l in range(1, level)]
        parent_dir = os.path.join(output_dir, *parent_dir_parts)

        if level == 1:
            current_content_dir = os.path.join(parent_dir, safe_title)
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")
        else: # (仅在不合并时会进入此分支)
            current_content_dir = parent_dir
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")

        md_file_containing_dir = os.path.dirname(output_filepath)
        current_image_dir = os.path.join(md_file_containing_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)
        
        chapter_content = f"# {title}\n\n"
        processed_img_xrefs = set()

        # --- 4. 内部页面处理循环：完全保留您现有的、经过验证的完美逻辑 ---
        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            processed_block_indices = set()
            page_content_parts = {}
            ignored_text_areas = []

            caption_blocks_indices = set()
            for idx, b in enumerate(blocks):
                if b["type"] == 0 and "lines" in b:
                    block_text = "\n".join("".join(s['text'] for s in l['spans']) for l in b['lines'])
                    if CAPTION_REGEX.search(block_text.strip()):
                        caption_blocks_indices.add(idx)

            for idx in sorted(list(caption_blocks_indices)):
                b = blocks[idx]
                is_false_positive = False
                for line in b["lines"]:
                    line_text = "".join(s["text"] for s in line["spans"]).strip()
                    match = re.search(r'\s*\([\d\.\-A-Za-z]+\)$', line_text)
                    if match:
                        preceding_text = line_text[:match.start()].strip()
                        if len(preceding_text) > 5:
                            is_false_positive = True
                            break
                if is_false_positive:
                    print(f"Info: Vetoed potential false-positive caption on page {page_num+1}: '{line_text[:50]}...'")
                    continue

                full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                caption_match = CAPTION_REGEX.search(full_caption)
                clean_caption = caption_match.group(0).strip() if caption_match else full_caption
                short_alt = ' '.join(clean_caption.split()[:5]) + "..."
                image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                if image_info:
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    page_content_parts[idx] = f"![{short_alt}]({relative_path})\n*{clean_caption}*\n\n"
                    if image_info.get("bbox"): 
                        ignored_text_areas.append(image_info["bbox"])
                        ignored_text_areas.append(fitz.Rect(b["bbox"]))
                else:
                    page_content_parts[idx] = f"*{clean_caption}*\n\n"
                processed_block_indices.add(idx)

            for idx, b in enumerate(blocks):
                if idx in processed_block_indices or b['type'] != 0: continue
                block_bbox = fitz.Rect(b["bbox"])
                if is_header_or_footer(block_bbox, page.rect): continue
                if any(area.intersects(block_bbox) for area in ignored_text_areas): continue
                markdown_text = get_markdown_from_block(b, true_headings=true_heading_whitelist)
                if markdown_text:
                    page_content_parts[idx] = markdown_text
                processed_block_indices.add(idx)

            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_img_xrefs:
                    img_block_idx = -1
                    for idx_b, block_img in enumerate(blocks):
                        if block_img.get("type") == 1 and block_img.get("number") == xref:
                            img_block_idx = idx_b
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

            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]
        
        chapter_content = re.sub(r'\n{3,}', '\n\n', chapter_content)
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)

    # --- 5. 元数据生成：保持不变 ---
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