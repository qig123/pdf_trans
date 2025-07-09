import fitz  # PyMuPDF
import os
import re
from urllib.parse import quote # 用于URL编码文件名

def clean_filename(name):
    """Cleans a string to be safely used as a file or directory name."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

def extract_with_relative_paths(pdf_path, output_dir="extracted_markdown"):
    """
    Extracts content and images, creating Markdown files with correct relative image paths.
    """
    CAPTION_REGEX = re.compile(
        r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+',
        flags=re.IGNORECASE
    )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    toc = doc.get_toc()

    if not toc:
        print("Error: This PDF file has no bookmarks.")
        return

    print(f"Found {len(toc)} bookmarks. Generating Markdown with relative paths...")

    level_paths = {}

    for i, item in enumerate(toc):
        level, title, start_page = item
        if level > 3: continue

        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        parent_path_parts = [level_paths[l] for l in range(1, level)]
        
        # current_text_dir 是文本文件所在的目录
        current_text_dir = os.path.join(output_dir, *parent_path_parts)
        
        # --- NEW: Define a dedicated image directory for each text file's location ---
        # 图片将被保存在和文本文件同级的 'images' 子目录中
        current_image_dir = os.path.join(current_text_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)

        if level < 3:
             # 为子章节创建目录
            os.makedirs(os.path.join(current_text_dir, safe_title), exist_ok=True)

        print(f"{'  ' * (level-1)}-> Processing: {title}")

        end_page = doc.page_count + 1
        for next_item in toc[i+1:]:
            if next_item[0] <= level:
                end_page = next_item[2]
                break
        
        start_page_index = start_page - 1
        end_page_index = end_page - 1
        
        chapter_content = ""
        processed_image_xrefs = set()

        for page_num in range(start_page_index, end_page_index):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))

            for block_idx, b in enumerate(blocks):
                if b[6] == 0: # Text block
                    text = b[4].strip()
                    if CAPTION_REGEX.match(text):
                        clean_caption = text.replace('\n', ' ').strip()
                        safe_caption_title = clean_filename(clean_caption)
                        image_filename_base = f"page_{page_num+1}_caption_{safe_caption_title}"
                        image_save_path = ""
                        image_ext = "png" # Default to png for screenshots

                        # Strategy: Find associated graphic
                        prev_block = blocks[block_idx - 1] if block_idx > 0 else None
                        if prev_block and prev_block[6] == 1:
                            image_xref = prev_block[5]
                            if image_xref not in processed_image_xrefs:
                                print(f"  - Found real image for caption '{safe_caption_title}'")
                                base_image = doc.extract_image(image_xref)
                                image_ext = base_image["ext"]
                                image_filename_base = f"page_{page_num+1}_img_{image_xref}"
                                image_save_path = os.path.join(current_image_dir, f"{image_filename_base}.{image_ext}")
                                with open(image_save_path, "wb") as f: f.write(base_image["image"])
                                processed_image_xrefs.add(image_xref)
                        
                        if not image_save_path: # Vector graphic detected
                            print(f"  - Vector graphic detected for '{safe_caption_title}'. Taking screenshot.")
                            caption_bbox = fitz.Rect(b[:4])
                            search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
                            search_area.intersect(page.rect)
                            if not search_area.is_empty:
                                image_save_path = os.path.join(current_image_dir, f"{image_filename_base}.{image_ext}")
                                pix = page.get_pixmap(clip=search_area, dpi=150)
                                pix.save(image_save_path)
                        
                        if image_save_path:
                            # --- CORE CHANGE: Generate correct relative path ---
                            final_image_filename = f"{image_filename_base}.{image_ext}"
                            # URL-encode the filename to handle spaces and special characters
                            relative_path = os.path.join("images", quote(final_image_filename))
                            chapter_content += f"\n\n![{clean_caption}]({relative_path})\n\n"
                    else:
                        chapter_content += b[4] # Normal text

            # Extract any uncaptioned "real" images
            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_image_xrefs:
                    base_image = doc.extract_image(xref)
                    image_ext = base_image["ext"]
                    image_filename = f"page_{page_num+1}_img_{xref}.{image_ext}"
                    image_save_path = os.path.join(current_image_dir, image_filename)
                    relative_path = os.path.join("images", quote(image_filename))
                    
                    print(f"  - Extracting uncaptioned image: {image_filename}")
                    with open(image_save_path, "wb") as f: f.write(base_image["image"])
                    
                    # Add a placeholder for the uncaptioned image in the text
                    chapter_content += f"\n\n![Uncaptioned Image page {page_num+1} xref {xref}]({relative_path})\n\n"
                    processed_image_xrefs.add(xref)

        # --- Save the collected text as a .md file ---
        # We now save as .md to indicate it's Markdown
        output_filepath = os.path.join(current_text_dir, f"{safe_title}.md") 
        if os.path.isdir(output_filepath): output_filepath += ".md"
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)

    print(f"\nExtraction complete! Markdown files and images saved to '{output_dir}'.")
    doc.close()

# --- USAGE EXAMPLE ---
if __name__ == "__main__":
    pdf_file = "your_document.pdf"
    if os.path.exists(pdf_file):
        extract_with_relative_paths(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")