import fitz  # PyMuPDF - PDF处理库
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime

# ==================== Configuration Loading (Unchanged) ====================
def load_config(path="config.json"):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: Configuration file '{path}' not found or malformed. Using default settings.")
        return {
            "margins": {"header": 0.08, "footer": 0.08},
            "regex": {
                "caption": "^(Figure|Fig\\.?|Table|Chart|图|表)\\s+[\\d\\.\\-A-Za-z]+",
                "keyword_heading": "^\\s*(Introduction|Conclusion|Summary|Abstract|References|Appendix)\\s*$"
            },
            "fonts": {"monospace_keywords": ["mono", "courier"]},
        }

CONFIG = load_config()

# --- Helper Functions (Largely Unchanged) ---
def clean_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

# Compile regexes from config
CAPTION_REGEX = re.compile(CONFIG['regex']['caption'], flags=re.IGNORECASE)
KEYWORD_HEADING_REGEX = re.compile(CONFIG['regex']['keyword_heading'], flags=re.IGNORECASE)

def is_header_or_footer(block_bbox, page_rect):
    header_margin = CONFIG['margins']['header']
    footer_margin = CONFIG['margins']['footer']
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin
    return block_bbox.y1 < header_boundary or block_bbox.y0 > footer_boundary

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    # This function is unchanged, so omitted for brevity in explanation
    # but included in the final script.
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1: # It's an image block
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

# ==================== ↓↓↓ CORE CHANGE 1: Final, Robust Markdown Block Generation ↓↓↓ ====================
def _process_text_chunk(text_chunk):
    """
    A helper function to process a non-heading chunk of text.
    It now ALSO identifies and formats captions.
    """
    text_chunk = text_chunk.strip()
    if not text_chunk:
        return ""

    # 1. Check if this chunk is a caption
    if CAPTION_REGEX.match(text_chunk):
        # Format as an italicized paragraph
        return f"*{text_chunk.replace(chr(10), ' ')}*\n\n"

    # 2. Check for special keyword headings (fallback)
    if KEYWORD_HEADING_REGEX.match(text_chunk):
        return f"## {text_chunk.replace(chr(10), ' ')}\n\n"

    # 3. Check for code blocks
    mono_fonts = CONFIG.get('fonts', {}).get('monospace_keywords', [])
    # A simple heuristic for code: multiple lines with significant indentation or keywords
    if len(text_chunk.splitlines()) > 1 and ('  ' in text_chunk or any(kw in text_chunk for kw in ['def ', 'import ', 'class '])):
         return f"```\n{text_chunk}\n```\n\n"

    # 4. Check for lists
    if re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', text_chunk):
        lines = text_chunk.split('\n')
        output_lines = []
        for line in lines:
            clean_line = line.strip()
            if not clean_line: continue
            if re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', clean_line):
                output_lines.append(re.sub(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', '* ', clean_line))
            else:
                output_lines.append("  " + clean_line)
        return "\n".join(output_lines) + "\n\n"
        
    # 5. Default to a plain paragraph
    return text_chunk.replace('\n', ' ').replace('\r', '') + "\n\n"

def normalize_text(text):
    """Collapses all whitespace into single spaces for consistent matching."""
    return ' '.join(text.split())




# ==================== ↓↓↓ CORE CHANGE 1: Updated Markdown Block Generation ↓↓↓ ====================
# ==================== ↓↓↓ CORE REFACTOR 2: get_markdown_from_block with flexible matching ↓↓↓ ====================
def get_markdown_from_block(block, headings_info_list=None):
    """
    Converts a text block to Markdown, using a robust, flexible matching and
    splitting mechanism for headings.
    """
    if headings_info_list is None: headings_info_list = []
    if block['type'] != 0 or not block.get('lines'): return ""

    full_text = "\n".join("".join(s['text'] for s in l['spans']) for l in block['lines'])
    if not full_text.strip(): return ""

    if not headings_info_list:
        return _process_text_chunk(full_text)

    # --- Build flexible matching tools ---
    # 1. A map from a NORMALIZED heading to its level and ORIGINAL text
    # e.g., {"1.1 a title": (2, "1.1  A Title")}
    normalized_map = {normalize_text(h['original']): (h['level'], h['original']) for h in headings_info_list}

    # 2. A master regex pattern to FIND any of the headings, tolerating whitespace differences.
    # We sort by length to ensure "1.1.1" is matched before "1.1"
    sorted_headings = sorted(headings_info_list, key=lambda x: len(x['original']), reverse=True)
    flexible_patterns = []
    for h in sorted_headings:
        # Create a pattern that matches words with any whitespace in between
        pattern = r'\s+'.join(re.escape(word) for word in h['original'].split())
        flexible_patterns.append(pattern)
    
    master_pattern = "|".join(flexible_patterns)
    
    # --- Find all heading occurrences and split the block accordingly ---
    last_end = 0
    output_parts = []
    
    for match in re.finditer(master_pattern, full_text):
        # Part 1: The text *before* this heading
        preceding_text = full_text[last_end:match.start()]
        output_parts.append(_process_text_chunk(preceding_text))
        
        # Part 2: The heading itself
        found_heading_text = match.group(0)
        normalized_found = normalize_text(found_heading_text)
        
        if normalized_found in normalized_map:
            level, original_text = normalized_map[normalized_found]
            # Use the original text from the TOC for consistency, but format with correct level
            output_parts.append(f"{'#' * level} {original_text.replace(chr(10), ' ')}\n\n")
        else:
            # This should not happen if patterns are generated correctly, but as a fallback:
            output_parts.append(_process_text_chunk(found_heading_text))

        last_end = match.end()

    # Part 3: The final chunk of text *after* the last heading
    remaining_text = full_text[last_end:]
    output_parts.append(_process_text_chunk(remaining_text))

    return "".join(output_parts)


def run_extraction(pdf_path, output_dir="mybook"):
    """
    Processes a PDF file based on its Table of Contents (TOC).
    - Level 1 TOC items create chapters (.md files).
    - Level 2+ TOC items become sub-headings within those files, using a
      robust and flexible matching system.
    - Correctly handles captions and headings that appear in the same text block.
    """
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    original_toc = doc.get_toc()
    if not original_toc:
        print("Error: No bookmarks (TOC) found in the document. Cannot proceed.")
        doc.close()
        return

    chapter_toc = [item for item in original_toc if item[0] == 1]
    if not chapter_toc:
        print("Error: No Level 1 bookmarks found to define chapters. Cannot proceed.")
        doc.close()
        return

    print(f"Found {len(chapter_toc)} top-level chapters to process.")
    markdown_files_list = []

    for i, chapter_item in enumerate(chapter_toc):
        level, title, start_page = chapter_item
        safe_title = clean_filename(title)
        
        print(f"\nProcessing Chapter: '{title}' (Page {start_page})")

        # --- Determine Page Range for this Chapter ---
        end_page = doc.page_count + 1
        if i + 1 < len(chapter_toc):
            end_page = chapter_toc[i+1][2]
        print(f"  - Content spans from page {start_page} to {end_page - 1}.")

        # --- Build Sub-Heading Whitelist for this Chapter ---
        headings_info_list = []
        try:
            start_index = original_toc.index(chapter_item)
            for j in range(start_index + 1, len(original_toc)):
                sub_item = original_toc[j]
                if sub_item[0] > level:
                    headings_info_list.append({
                        "original": sub_item[1], 
                        "level": sub_item[0]
                    })
                else:
                    break
        except ValueError:
            print(f"  - Warning: Could not find chapter '{title}' in the main TOC.")

        if headings_info_list:
            print(f"  - Found {len(headings_info_list)} sub-headings to use as a whitelist.")
        
        # --- Setup File and Directory Structure ---
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
            # Using TEXTFLAGS_SEARCH is beneficial for more consistent spacing
            page_data = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            page_content_parts = {}
            ignored_text_areas = []

            # --- Final, Corrected Processing Logic ---
            for idx, b in enumerate(blocks):
                # We only care about text blocks in this main loop.
                if b['type'] != 0:
                    continue
                
                block_bbox = fitz.Rect(b["bbox"])
                if is_header_or_footer(block_bbox, page.rect):
                    continue
                if any(area.intersects(block_bbox) for area in ignored_text_areas):
                    continue
                
                # Step 1: Potentially find an image associated with this block
                image_md = ""
                full_text_for_caption_check = "".join("".join(s['text'] for s in l['spans']) for l in b.get('lines', [])).strip()
                if CAPTION_REGEX.match(full_text_for_caption_check):
                    image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                    if image_info:
                        relative_path = os.path.join("images", quote(image_info["filename"]))
                        short_alt = ' '.join(full_text_for_caption_check.split()[:5]) + "..."
                        image_md = f"![{short_alt}]({relative_path})\n"
                        if image_info.get("bbox"):
                             ignored_text_areas.append(image_info["bbox"])
                
                # Step 2: ALWAYS process the block with the master splitter function.
                # This function will correctly separate headings from other text (like captions).
                markdown_text = get_markdown_from_block(b, headings_info_list)
                
                # Step 3: Combine the image markdown (if any) and the processed text.
                if markdown_text:
                    page_content_parts[idx] = image_md + markdown_text

            # --- Uncaptioned image processing (unchanged) ---
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
                            page_content_parts[img_block_idx] = f"![Uncaptioned image on page {page_num+1}]({relative_path})\n\n"
                            processed_img_xrefs.add(xref)
                        except Exception as e:
                            print(f"  - Warning: Could not process uncaptioned image xref {xref} on page {page_num+1}. Error: {e}")

            # Assemble page content in correct vertical order
            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]

        # --- Finalize and write chapter content ---
        chapter_content = re.sub(r'\n{3,}', '\n\n', chapter_content)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(chapter_content)
        
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)
    
    # --- Metadata generation at the end ---
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    book_data = {
        "kind": "Book",
        "title": book_title,
        "version": "0.1.0",
        "authors": book_authors,
        "translators": ["Generated by Script"],
        "year": str(datetime.now().year),
        "src": ".",
        "contents": markdown_files_list
    }
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: 
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    doc.close()
    print("\nExtraction complete!")

if __name__ == "__main__":
    # 替换为你的PDF文件路径
    pdf_file = "your_file.pdf" 
    if os.path.exists(pdf_file):
        # 注意：函数名已改为 run_extraction
        run_extraction(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")