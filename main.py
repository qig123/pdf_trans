import fitz  # PyMuPDF - PDF处理库
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime

# --- 辅助函数 ---

def clean_filename(name):
    """清理文件名中的非法字符"""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

# ==================== ↓↓↓ 这里是修改的部分 ↓↓↓ ====================

# REGEX for matching numbered heading formats. Now this is our PRIMARY heading detector.
# --- 修改说明 ---
# 旧版的问题: r'^\s*((\d+(\.\d+)*\.?)|...)' 会错误地匹配 "1. item", "2. item" 这样的列表。
# 新版的核心改动: 使用 \d+\.\d+ 来要求至少有两级数字（如 "3.1"），从而避免与简单列表冲突。
# [\d\.]* 允许匹配更深的层级如 "3.1.2"。
TITLE_REGEX = re.compile(
    # Matches patterns like "3.1", "3.2.1", "A.1", etc. followed by text.
    # It now specifically AVOIDS matching simple lists like "1. text".
    r'^\s*((\d+\.\d+[\d\.]*)|([A-Z]\.[\d\.]*))\s+[A-Za-z].*'
)

# REGEX for un-numbered, but likely headings (like "Introduction", "Conclusion")
KEYWORD_HEADING_REGEX = re.compile(r'^\s*(Introduction|Conclusion|Summary|Abstract|References|Appendix)\s*$', flags=re.IGNORECASE)


def is_header_or_footer(block_bbox, page_rect, header_margin=0.12, footer_margin=0.12):
    """判断文本块是否位于页眉或页脚区域"""
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin
    return block_bbox.y1 < header_boundary or block_bbox.y0 > footer_boundary

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """为标题查找对应的图像"""
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
    
    caption_bbox = fitz.Rect(blocks[caption_block_idx]["bbox"])
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
    search_area.intersect(page.rect)
    if not search_area.is_empty and search_area.height > 10:
        filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
        pix = page.get_pixmap(clip=search_area, dpi=150)
        pix.save(os.path.join(image_dir, filename))
        return {"filename": filename, "bbox": search_area}
    return None

# --- 全新简化的Markdown格式推断函数 ---
def get_markdown_from_block(block):
    """
    根据文本块的内容模式推断其Markdown格式。
    新版: 通过正则预分割，解决内嵌标题不换行的问题。
    """
    # ... (此函数无需变动)
    if block['type'] != 0 or not block.get('lines'):
        return ""

    full_text = "\n".join("".join(s['text'] for s in l['spans']) for l in block['lines'])
    if not full_text.strip():
        return ""

    split_marker = "<\r\n_SPLIT_HERE_\r\n>"
    processed_text = re.sub(
        r'(?m)(^|(?<=\n))(\s*((\d+\.\d+[\d\.]*)|([A-Z]\.[\d\.]*))\s+[A-Za-z].*)',
        lambda m: f"{split_marker}{m.group(2)}",
        full_text
    )
    
    sub_blocks_text = processed_text.split(split_marker)

    output_parts = []
    for sub_text in sub_blocks_text:
        sub_text = sub_text.strip()
        if not sub_text:
            continue

        if (TITLE_REGEX.match(sub_text) and len(sub_text) < 200) or KEYWORD_HEADING_REGEX.match(sub_text):
            output_parts.append(f"## {sub_text.replace(chr(10), ' ')}\n\n")
            continue

        is_monospace_block = all(
            ("mono" in span['font'].lower() or "courier" in span['font'].lower())
            for line in block['lines'] for span in line['spans'] if 'font' in span
        )
        if is_monospace_block and len(sub_text.splitlines()) > 1:
            output_parts.append(f"```\n{sub_text}\n```\n\n")
            continue

        list_match = re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', sub_text)
        if list_match:
            lines = sub_text.split('\n')
            # 将所有行都作为列表项处理，以支持多行列表项
            output_lines = []
            for i, line in enumerate(lines):
                # 检查每一行是否是新的列表项
                if re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', line):
                    # 是新的列表项，使用 *
                    output_lines.append(re.sub(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', '* ', line))
                else:
                    # 不是新的列表项，作为上一项的延续，进行缩进
                    output_lines.append("  " + line.strip())
            output_parts.append("\n".join(output_lines) + "\n\n")
            continue
            
        output_parts.append(sub_text.replace('\n', ' ') + "\n\n")

    return "".join(output_parts)


# --- 主处理函数 (已更新) ---
def run_extraction_stable(pdf_path, output_dir="mybook"):
    """
    处理PDF文件。使用书签作为H1标题，使用内容模式匹配作为H2标题。
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
            if is_parent_node:
                current_content_dir = os.path.join(output_dir, safe_title)
                os.makedirs(current_content_dir, exist_ok=True)
            continue
        
        parent_dir_parts = [level_paths[l] for l in range(1, level)]
        parent_dir = os.path.join(output_dir, *parent_dir_parts)

        if level == 1:
            current_content_dir = os.path.join(parent_dir, safe_title)
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")
        else: # level == 2
            current_content_dir = parent_dir
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")

        md_file_containing_dir = os.path.dirname(output_filepath)
        current_image_dir = os.path.join(md_file_containing_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)
        
        # --- 恢复使用书签作为H1标题 ---
        chapter_content = f"# {title}\n\n"
        processed_img_xrefs = set()

        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            # --- 移除字体分析 ---
            # body_size, heading_map = analyze_page_fonts(page)
            
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            processed_block_indices = set()
            page_content_parts = {}
            ignored_text_areas = []

            # 1. 优先处理图片和图注 (逻辑不变)
            caption_blocks_indices = {idx for idx, b in enumerate(blocks) if b["type"] == 0 and "lines" in b and CAPTION_REGEX.match(''.join(s["text"] for s in b["lines"][0]["spans"]).strip())}
            for idx in sorted(list(caption_blocks_indices)):
                b = blocks[idx]
                full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                short_alt = ' '.join(full_caption.split()[:4]) + "..."
                image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                if image_info:
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    page_content_parts[idx] = f"![{short_alt}]({relative_path})\n*{full_caption}*\n\n"
                    if image_info.get("bbox"): ignored_text_areas.append(image_info["bbox"])
                else:
                    page_content_parts[idx] = f"*{full_caption}*\n\n"
                processed_block_indices.add(idx)

            # 2. 处理所有文本块
            for idx, b in enumerate(blocks):
                if idx in processed_block_indices or b['type'] != 0: continue
                block_bbox = fitz.Rect(b["bbox"])
                if is_header_or_footer(block_bbox, page.rect): continue
                if any(area.intersects(block_bbox) for area in ignored_text_areas): continue

                # --- 调用新的、简化的格式化函数 ---
                markdown_text = get_markdown_from_block(b)
                if markdown_text:
                    page_content_parts[idx] = markdown_text
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
    pdf_file = "your_file.pdf"
    if os.path.exists(pdf_file):
        run_extraction_stable(pdf_file)
    else:
        print(f"错误: 文件 '{pdf_file}' 未找到。")