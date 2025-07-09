import fitz  # PyMuPDF
import os
import re
import json
from urllib.parse import quote
from datetime import datetime

def clean_filename(name):
    """Cleans a string to be safely used as a file or directory name."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

def extract_and_generate_book(pdf_path, output_dir="mybook"):
    """
    Extracts content, images, and generates a book.json file for the project.
    """
    CAPTION_REGEX = re.compile(
        r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+',
        flags=re.IGNORECASE
    )

    if not os.path.exists(output_dir): os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    toc = doc.get_toc()

    if not toc:
        print("Error: This PDF file has no bookmarks.")
        return

    print(f"Found {len(toc)} bookmarks. Generating book project...")
    
    # --- NEW: Initialize list to hold markdown file paths for book.json ---
    markdown_files_list = []
    level_paths = {}

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

        # ... (The core extraction logic for pages, text, and images remains the same) ...
        end_page = doc.page_count + 1
        for next_item in toc[i+1:]:
            if next_item[0] <= level:
                end_page = next_item[2]; break
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
                if b[6] == 0:
                    text = b[4].strip()
                    if CAPTION_REGEX.match(text):
                        clean_caption = text.replace('\n', ' ').strip()
                        short_alt = ' '.join(clean_caption.split()[:4]) + "..."
                        safe_caption_title = clean_filename(clean_caption)
                        image_filename_base = f"page_{page_num+1}_caption_{safe_caption_title}"
                        image_save_path, image_ext = "", "png"
                        prev_block = blocks[block_idx - 1] if block_idx > 0 else None
                        if prev_block and prev_block[6] == 1:
                            image_xref = prev_block[5]
                            if image_xref not in processed_image_xrefs:
                                base_image = doc.extract_image(image_xref)
                                image_ext = base_image["ext"]
                                image_filename_base = f"page_{page_num+1}_img_{image_xref}"
                                image_save_path = os.path.join(current_image_dir, f"{image_filename_base}.{image_ext}")
                                with open(image_save_path, "wb") as f: f.write(base_image["image"])
                                processed_image_xrefs.add(image_xref)
                        if not image_save_path:
                            caption_bbox = fitz.Rect(b[:4])
                            search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
                            search_area.intersect(page.rect)
                            if not search_area.is_empty:
                                image_save_path = os.path.join(current_image_dir, f"{image_filename_base}.{image_ext}")
                                pix = page.get_pixmap(clip=search_area, dpi=150); pix.save(image_save_path)
                        if image_save_path:
                            final_image_filename = f"{image_filename_base}.{image_ext}"
                            relative_path = os.path.join("images", quote(final_image_filename))
                            chapter_content += f"\n\n![{short_alt}]({relative_path})\n*{clean_caption}*\n\n"
                    else: chapter_content += b[4]
            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_image_xrefs:
                    base_image = doc.extract_image(xref)
                    image_filename = f"page_{page_num+1}_img_{xref}.{base_image['ext']}"
                    relative_path = os.path.join("images", quote(image_filename))
                    with open(os.path.join(current_image_dir, image_filename), "wb") as f: f.write(base_image["image"])
                    chapter_content += f"\n\n![Uncaptioned Image page {page_num+1} xref {xref}]({relative_path})\n\n"
                    processed_image_xrefs.add(xref)

        output_filepath = os.path.join(current_text_dir, f"{safe_title}.md") 
        if os.path.isdir(output_filepath): output_filepath += ".md"
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        
        # --- NEW: Add the relative path of the created file to our list ---
        relative_md_path = os.path.relpath(output_filepath, output_dir)
        # Ensure forward slashes for cross-platform compatibility in JSON
        markdown_files_list.append(relative_md_path.replace(os.sep, '/'))

    # --- NEW: After the loop, create the book.json file ---
    print("\nAll files extracted. Generating book.json...")

    # Try to get metadata, with fallbacks
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    
    book_data = {
        "kind": "Book",
        "title": book_title,
        "version": "0.1.0",
        "authors": book_authors,
        "translators": ["Generated by Script"], # Placeholder
        "year": str(datetime.now().year), # Use current year as placeholder
        "src": ".", # Indicates that paths in 'contents' are relative to this file
        "contents": markdown_files_list
    }
    
    book_json_path = os.path.join(output_dir, "book.json")
    with open(book_json_path, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully created '{book_json_path}'!")
    print("\nExtraction complete!")
    doc.close()

# --- USAGE EXAMPLE ---
if __name__ == "__main__":
    pdf_file = "your_document.pdf"
    if os.path.exists(pdf_file):
        extract_and_generate_book(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")