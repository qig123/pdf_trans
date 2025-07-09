import fitz  # PyMuPDF
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime

# clean_filename 和 find_image_for_caption 函数保持不变
def clean_filename(name):
    """Cleans a string to be safely used as a file or directory name."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """Helper function to find and save the image associated with a caption."""
    # Look for a raster image block right above
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
                    return {"filename": filename}
                except Exception: return None
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

def run_extraction_stable(pdf_path, output_dir="mybook"):
    """
    Extracts content with refined hierarchical logic.
    - Parent items (like "Part I", "Chapter 1") get their own intro .md file.
    - Content for a parent item stops at the beginning of its first child.
    - File structure correctly mirrors the book's nested structure.
    """
    if os.path.exists(output_dir):
        print(f"Old output directory '{output_dir}' found. Deleting it...")
        shutil.rmtree(output_dir)
        print("Old directory deleted.")
    
    os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    if not toc:
        print("Error: No bookmarks found.")
        return

    print("Starting extraction with refined hierarchical processing...")
    markdown_files_list = []
    level_paths = {}
    CAPTION_REGEX = re.compile(r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+', flags=re.IGNORECASE)

    for i, item in enumerate(toc):
        level, title, start_page = item
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        
        print(f"{'  ' * (level-1)}-> Processing: {title}")

        # --- START: REFINED PATH AND PAGE RANGE LOGIC ---

        is_parent_node = (i + 1 < len(toc)) and (toc[i+1][0] > level)

        # **CRITICAL CHANGE**: Determine the correct end_page
        if is_parent_node:
            # For a parent, its "intro" content ends where its FIRST CHILD begins.
            end_page = toc[i+1][2] 
        else:
            # For a leaf node, its content ends where the NEXT SIBLING or UNCLE begins.
            end_page = doc.page_count + 1 # Default to end of document
            for next_item in toc[i+1:]:
                if next_item[0] <= level:
                    end_page = next_item[2]
                    break
        
        # If a parent bookmark is purely structural (no pages between it and its child), skip creating a file.
        if start_page >= end_page:
            print(f"{'  ' * (level-1)}  - Skipping empty section.")
            # We still need to create the directory for its children
            if is_parent_node:
                parent_dir_parts = [level_paths[l] for l in range(1, level)]
                parent_dir = os.path.join(output_dir, *parent_dir_parts)
                current_content_dir = os.path.join(parent_dir, safe_title)
                os.makedirs(current_content_dir, exist_ok=True)
            continue
            
        # Path logic from before is mostly correct, let's keep it.
        parent_dir_parts = [level_paths[l] for l in range(1, level)]
        parent_dir = os.path.join(output_dir, *parent_dir_parts)

        if is_parent_node:
            # A parent gets its own directory.
            current_content_dir = os.path.join(parent_dir, safe_title)
            # Its intro .md file goes inside that directory.
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")
        else:
            # A leaf file goes into its parent's directory.
            current_content_dir = parent_dir
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")

        md_file_containing_dir = os.path.dirname(output_filepath)
        current_image_dir = os.path.join(md_file_containing_dir, "images")
        
        os.makedirs(current_image_dir, exist_ok=True)
        
        # --- END: REFINED PATH AND PAGE RANGE LOGIC ---
        
        chapter_content = f"# {title}\n\n"
        processed_img_xrefs = set()

        # Page range is 1-based, exclusive at the end.
        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            # (Content extraction loop remains the same)
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            caption_blocks_indices = {idx for idx, b in enumerate(blocks) if b["type"] == 0 and "lines" in b and CAPTION_REGEX.match(''.join(s["text"] for s in b["lines"][0]["spans"]).strip())}
            
            for idx in sorted(list(caption_blocks_indices)):
                b = blocks[idx]
                full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                short_alt = ' '.join(full_caption.split()[:4]) + "..."
                image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                if image_info:
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    chapter_content += f"![{short_alt}]({relative_path})\n*{full_caption}*\n\n"
                else:
                    chapter_content += f"*{full_caption}*\n\n"

            for idx, b in enumerate(blocks):
                if b["type"] == 0 and idx not in caption_blocks_indices:
                    plain_text = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                    if plain_text:
                        chapter_content += plain_text + "\n\n"

            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_img_xrefs:
                    try:
                        base_image = doc.extract_image(xref)
                        if not base_image: continue
                        image_filename = f"page_{page_num+1}_uncaptioned_img_{xref}.{base_image['ext']}"
                        relative_path = os.path.join("images", quote(image_filename))
                        with open(os.path.join(current_image_dir, image_filename), "wb") as f: f.write(base_image["image"])
                        chapter_content += f"![Uncaptioned Image page {page_num+1} xref {xref}]({relative_path})\n\n"
                        processed_img_xrefs.add(xref)
                    except Exception as e:
                        print(f"Warning: Could not process uncaptioned image xref {xref} on page {page_num+1}. Error: {e}")

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
        run_extraction_stable(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")