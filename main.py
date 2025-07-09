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

def is_header_or_footer(block_bbox, page_rect, header_margin=0.12, footer_margin=0.12):
    """
    Checks if a text block is likely a header or footer based on its position.

    :param block_bbox: The bounding box of the text block (fitz.Rect).
    :param page_rect: The bounding box of the entire page (fitz.Rect).
    :param header_margin: Percentage of page height to consider as header area (e.g., 0.12 = top 12%).
    :param footer_margin: Percentage of page height to consider as footer area (e.g., 0.12 = bottom 12%).
    :return: True if the block is in the header or footer area, False otherwise.
    """
    # Calculate the y-coordinates for the header and footer boundaries
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin

    # Check if the entire block is above the header boundary
    if block_bbox.y1 < header_boundary:
        return True
    
    # Check if the entire block is below the footer boundary
    if block_bbox.y0 > footer_boundary:
        return True
        
    return False

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    """
    Helper function to find and save the image associated with a caption.
    NOW RETURNS the BBOX of the image area to allow ignoring text within it.
    """
    # Look for a raster image block right above
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1: # This is a raster image block
            xref = prev_block["number"]
            if xref not in processed_blocks:
                try:
                    base_image = doc.extract_image(xref)
                    if not base_image: return None
                    filename = f"page_{page.number+1}_img_{xref}.{base_image['ext']}"
                    with open(os.path.join(image_dir, filename), "wb") as f: f.write(base_image["image"])
                    processed_blocks.add(xref)
                    # Return filename AND the image's bounding box
                    return {"filename": filename, "bbox": fitz.Rect(prev_block["bbox"])}
                except Exception:
                    return None

    # If not found, assume vector and take a screenshot of the area above
    caption_bbox = fitz.Rect(blocks[caption_block_idx]["bbox"])
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
    search_area.intersect(page.rect) # Ensure the area is within the page bounds
    
    if not search_area.is_empty and search_area.height > 10: # Only capture significant areas
        filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
        pix = page.get_pixmap(clip=search_area, dpi=150)
        pix.save(os.path.join(image_dir, filename))
        # Return filename AND the screenshot's bounding box
        return {"filename": filename, "bbox": search_area}
    
    return None

def run_extraction_stable(pdf_path, output_dir="mybook"):
    # (The beginning of the function remains the same, up to the page loop)
    # ... (code for setup, directory deletion, main TOC loop) ...
    # I will paste the full function for clarity.

    """
    Extracts content with refined hierarchical logic and image-text de-duplication.
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

    print("Starting extraction with image-text de-duplication...")
    markdown_files_list = []
    level_paths = {}
    CAPTION_REGEX = re.compile(r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+', flags=re.IGNORECASE)

    for i, item in enumerate(toc):
        level, title, start_page = item
        # (This part for path logic and page range calculation remains the same as your last version)
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        print(f"{'  ' * (level-1)}-> Processing: {title}")
        is_parent_node = (i + 1 < len(toc)) and (toc[i+1][0] > level)
        end_page = doc.page_count + 1
        found_next = False
        if is_parent_node:
            end_page = toc[i+1][2]
            found_next = True
        if not found_next:
            for next_item in toc[i+1:]:
                if next_item[0] <= level:
                    end_page = next_item[2]
                    break
        if start_page >= end_page:
            print(f"{'  ' * (level-1)}  - Skipping empty section.")
            if is_parent_node and level < 3:
                parent_dir_parts = [level_paths[l] for l in range(1, level)]
                parent_dir = os.path.join(output_dir, *parent_dir_parts)
                current_content_dir = os.path.join(parent_dir, safe_title)
                os.makedirs(current_content_dir, exist_ok=True)
            continue
        create_new_directory = is_parent_node and level < 3
        parent_dir_parts = [level_paths[l] for l in range(1, level)]
        parent_dir = os.path.join(output_dir, *parent_dir_parts)
        if create_new_directory:
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

        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            # --- START: REVISED PER-PAGE LOGIC ---
            
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            ignored_text_areas = [] # Store bboxes of handled images on this page
            page_content_parts = {} # Store content parts to assemble in order

            # 1. First pass: Identify all captions and their corresponding images
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
                        ignored_text_areas.append(image_info["bbox"]) # CRITICAL: Record the image area
                else:
                    content = f"*{full_caption}*\n\n" # Caption without a found image
                
                page_content_parts[idx] = content

           # 2. Second pass: Process all text blocks, skipping those in image areas AND headers/footers
            for idx, b in enumerate(blocks):
                if b["type"] == 0 and idx not in caption_blocks_indices: # Is a text block and not a caption
                    block_bbox = fitz.Rect(b["bbox"])
                    
                    # --- START: NEW HEADER/FOOTER CHECK ---
                    if is_header_or_footer(block_bbox, page.rect):
                        continue # Skip this block if it's a header or footer
                    # --- END: NEW HEADER/FOOTER CHECK ---

                    is_in_image = False
                    for area in ignored_text_areas:
                        if area.intersects(block_bbox):
                            is_in_image = True
                            break
                    
                    if not is_in_image:
                        plain_text = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                        if plain_text:
                           page_content_parts[idx] = plain_text + "\n\n"

            # 3. Third pass (optional but good): Catch uncaptioned raster images
            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_img_xrefs:
                    # Find which block corresponds to this image to get its position
                    img_block_idx = -1
                    for idx, b in enumerate(blocks):
                        if b["type"] == 1 and b["number"] == xref:
                            img_block_idx = idx
                            break
                    
                    if img_block_idx != -1:
                        try:
                            base_image = doc.extract_image(xref)
                            if not base_image: continue
                            image_filename = f"page_{page_num+1}_uncaptioned_img_{xref}.{base_image['ext']}"
                            relative_path = os.path.join("images", quote(image_filename))
                            with open(os.path.join(current_image_dir, image_filename), "wb") as f: f.write(base_image["image"])
                            
                            content = f"![Uncaptioned Image page {page_num+1} xref {xref}]({relative_path})\n\n"
                            page_content_parts[img_block_idx] = content
                            processed_img_xrefs.add(xref)
                        except Exception as e:
                            print(f"Warning: Could not process uncaptioned image xref {xref} on page {page_num+1}. Error: {e}")

            # 4. Assemble all content parts for the page in their correct vertical order
            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]
            
            # --- END: REVISED PER-PAGE LOGIC ---

        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)

    # (Code for generating book.json remains the same)
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    book_data = {"kind":"Book","title":book_title,"version":"0.1.0","authors":book_authors,"translators":["Generated by Script"],"year":str(datetime.now().year),"src":".","contents":markdown_files_list}
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: json.dump(book_data, f, ensure_ascii=False, indent=2)

    print("\nExtraction complete!")
    doc.close()

# The __main__ block remains the same
if __name__ == "__main__":
    pdf_file = "your_document.pdf"
    if os.path.exists(pdf_file):
        run_extraction_stable(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")