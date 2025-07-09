import fitz  # PyMuPDF
import os
import re
import json
import shutil # <--- 1. 导入 shutil 模块
from collections import Counter

from urllib.parse import quote
from datetime import datetime

# ... (clean_filename and get_dominant_font_info functions remain exactly the same) ...
def clean_filename(name):
    """Cleans a string to be safely used as a file or directory name."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

def get_dominant_font_info(page):
    """Analyzes the page to find the most common font size and name (body text)."""
    spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block for line in block["lines"] for span in line["spans"]]
    if not spans: return 12, "sans-serif"
    font_sizes = Counter(span["size"] for span in spans)
    font_names = Counter(span["font"] for span in spans)
    body_size = font_sizes.most_common(1)[0][0] if font_sizes else 12
    body_font = font_names.most_common(1)[0][0] if font_names else "sans-serif"
    return body_size, body_font

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """Helper function to find and save the image associated with a caption."""
    # Look for a raster image block right above
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1 and prev_block["number"] not in processed_blocks:
            xref = prev_block["number"]
            try:
                base_image = doc.extract_image(xref)
                if not base_image: return None
                filename = f"page_{page.number+1}_img_{xref}.{base_image['ext']}"
                with open(os.path.join(image_dir, filename), "wb") as f: f.write(base_image["image"])
                processed_blocks.add(prev_block["number"])
                return {"filename": filename}
            except Exception:
                return None # Ignore images that fail to extract

    # If not found, assume vector and take a screenshot of the area above
    caption_bbox = fitz.Rect(blocks[caption_block_idx]["bbox"])
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
    search_area.intersect(page.rect)
    if not search_area.is_empty:
        filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
        pix = page.get_pixmap(clip=search_area, dpi=150)
        pix.save(os.path.join(image_dir, filename))
        return {"filename": filename}
    
    return None
    
def run_extraction(pdf_path, output_dir="mybook"): # <--- 2. 确认输出目录为 'mybook'
    """
    Final, robust script to extract PDF content into rich Markdown,
    handle images, and generate a book.json file.
    """
    # --- 3. 新增：在开始前清理旧的输出目录 ---
    if os.path.exists(output_dir):
        print(f"Old output directory '{output_dir}' found. Deleting it for a fresh start...")
        shutil.rmtree(output_dir)
        print("Old directory deleted.")
    
    # 脚本现在可以确保在一个干净的环境下创建新目录
    os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    if not toc: print("Error: No bookmarks found."); return

    print("Starting full extraction process...")
    markdown_files_list = []
    level_paths = {}
    CAPTION_REGEX = re.compile(r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+', flags=re.IGNORECASE)

    for i, item in enumerate(toc):
        level, title, start_page = item
        if level > 3: continue
        
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        parent_path_parts = [level_paths[l] for l in range(1, level)]
        current_text_dir = os.path.join(output_dir, *parent_path_parts)
        current_image_dir = os.path.join(current_text_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)
        if level < 3: os.makedirs(os.path.join(current_text_dir, safe_title), exist_ok=True)
        
        print(f"{'  ' * (level-1)}-> Processing: {title}")

        end_page = doc.page_count + 1
        for next_item in toc[i+1:]:
            if next_item[0] <= level:
                end_page = next_item[2]; break
        
        chapter_content = f"# {title}\n\n"
        processed_block_nums = set()

        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            body_size, _ = get_dominant_font_info(page)
            
            blocks = page.get_text("dict")["blocks"]
            for block_idx, b in enumerate(blocks):
                block_num = b["number"]
                if block_num in processed_block_nums: continue

                if b["type"] == 0 and "lines" in b:
                    first_line_text = ''.join(span["text"] for span in b["lines"][0]["spans"]).strip()
                    if CAPTION_REGEX.match(first_line_text):
                        full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                        short_alt = ' '.join(full_caption.split()[:4]) + "..."
                        image_info = find_image_for_caption(doc, page, blocks, block_idx, current_image_dir, processed_block_nums)
                        if image_info:
                            relative_path = os.path.join("images", quote(image_info["filename"]))
                            chapter_content += f"\n![{short_alt}]({relative_path})\n*{full_caption}*\n\n"
                        else:
                             chapter_content += f"*{full_caption}*\n\n"
                        processed_block_nums.add(block_num)
                        continue

                if b["type"] == 0 and "lines" in b:
                    if any("mono" in s["font"].lower() for l in b["lines"] for s in l["spans"]):
                        code_text = '\n'.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"])
                        chapter_content += f"```\n{code_text}\n```\n\n"
                    else:
                        is_heading = False
                        for line in b["lines"]:
                            line_text, span_sizes = "", [s["size"] for s in line["spans"]]
                            avg_size = sum(span_sizes) / len(span_sizes) if span_sizes else body_size
                            for span in line["spans"]:
                                text = span["text"]
                                if span["flags"] & 2**4: text = f"**{text}**"
                                elif span["flags"] & 2**1: text = f"*{text}*"
                                line_text += text
                            if avg_size > body_size * 1.5: chapter_content += f"## {line_text.strip()}\n\n"; is_heading = True
                            elif avg_size > body_size * 1.2: chapter_content += f"### {line_text.strip()}\n\n"; is_heading = True
                            else: chapter_content += line_text + "\n"
                        if not is_heading: chapter_content += "\n"
                    processed_block_nums.add(block_num)

        output_filepath = os.path.join(current_text_dir, f"{safe_title}.md")
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)

    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    book_data = {"kind":"Book","title":book_title,"version":"0.1.0","authors":book_authors,"translators":["Generated by Script"],"year":str(datetime.now().year),"src":".","contents":markdown_files_list}
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: json.dump(book_data, f, ensure_ascii=False, indent=2)

    print("\nExtraction complete!")
    doc.close()

if __name__ == "__main__":
    pdf_file = "your_document.pdf"
    if os.path.exists(pdf_file):
        run_extraction(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")