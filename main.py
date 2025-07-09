import fitz  # PyMuPDF
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime
from collections import Counter

# ==================== Configuration Loading ====================
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
            "heading_detection": {
                "font_size_multiplier": 1.2,
                "min_heading_level_for_text_match": 3,
                "shallow_heading_level": 2
            }
        }

CONFIG = load_config()
HD_CONFIG = CONFIG.get("heading_detection", {})

# ==================== Helper Functions ====================
def clean_filename(name):
    # ... (unchanged)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    name = name.strip(' .')
    return (name[:100] if len(name) > 100 else name) or "untitled"

CAPTION_REGEX = re.compile(CONFIG['regex']['caption'], flags=re.IGNORECASE)
KEYWORD_HEADING_REGEX = re.compile(CONFIG['regex']['keyword_heading'], flags=re.IGNORECASE)

def is_header_or_footer(block_bbox, page_rect):
    # ... (unchanged)
    header_margin = CONFIG['margins']['header']
    footer_margin = CONFIG['margins']['footer']
    header_boundary = page_rect.y0 + page_rect.height * header_margin
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin
    return block_bbox.y1 < header_boundary or block_bbox.y0 > footer_boundary

def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    # ... (unchanged)
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

# --- NEW HELPER: Font Analysis ---
def find_dominant_font_size(page):
    """Analyzes the page to find the most common font size."""
    sizes = Counter()
    for block in page.get_text("dict").get("blocks", []):
        if block['type'] == 0: # text blocks
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    sizes[round(span['size'])] += 1
    if not sizes:
        return 12.0 # A reasonable default
    return sizes.most_common(1)[0][0]

def normalize_text(text):
    return ' '.join(text.split())

# --- CORE PROCESSING LOGIC (REFACTORED) ---
def _process_text_chunk(text_chunk):
    """Processes a chunk of text that is NOT a heading."""
    text_chunk = text_chunk.strip()
    if not text_chunk: return ""
    if CAPTION_REGEX.match(text_chunk):
        return f"*{text_chunk.replace(chr(10), ' ')}*\n\n"
    if KEYWORD_HEADING_REGEX.match(text_chunk):
        return f"## {text_chunk.replace(chr(10), ' ')}\n\n"
    if len(text_chunk.splitlines()) > 1 and ('  ' in text_chunk or any(kw in text_chunk for kw in ['def ', 'import ', 'class '])):
         return f"```\n{text_chunk}\n```\n\n"
    if re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', text_chunk):
        lines = text_chunk.split('\n')
        output_lines = []
        for line in lines:
            clean_line = line.strip()
            if not clean_line: continue
            if re.match(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', clean_line):
                output_lines.append(re.sub(r'^\s*([•*-]|\d+\.|[a-zA-Z]\))\s+', '* ', clean_line))
            else: output_lines.append("  " + clean_line)
        return "\n".join(output_lines) + "\n\n"
    return text_chunk.replace('\n', ' ').replace('\r', '') + "\n\n"


def get_markdown_from_block(block, deep_headings_info_list, font_size_threshold):
    """
    Hybrid markdown converter. Uses font size for shallow headings and text match for deep ones.
    """
    if block['type'] != 0 or not block.get('lines'): return ""
    full_text = "\n".join("".join(s['text'] for s in l['spans']) for l in block['lines'])
    full_text = full_text.strip()
    if not full_text: return ""

    # --- STRATEGY 1: FONT-BASED HEADING DETECTION (for Level 1 & 2) ---
    first_line_spans = block['lines'][0]['spans']
    avg_font_size = sum(s['size'] for s in first_line_spans) / len(first_line_spans)
    
    if avg_font_size >= font_size_threshold:
        # Check if it's a false positive (like a caption or just a number)
        is_just_number = full_text.isdigit()
        is_caption = CAPTION_REGEX.match(full_text)
        
        # To be a shallow heading, it must not contain a more specific deep heading.
        contains_deep_heading = False
        if deep_headings_info_list:
            # A simple check is enough here
            if any(normalize_text(h['original']) in normalize_text(full_text) for h in deep_headings_info_list):
                 contains_deep_heading = True

        if not is_just_number and not is_caption and not contains_deep_heading:
            shallow_level = HD_CONFIG.get("shallow_heading_level", 2)
            return f"{'#' * shallow_level} {full_text.replace(chr(10), ' ')}\n\n"

    # --- STRATEGY 2: TEXT-BASED HEADING DETECTION (for Level 3+) ---
    if not deep_headings_info_list:
        return _process_text_chunk(full_text)

    normalized_map = {normalize_text(h['original']): (h['level'], h['original']) for h in deep_headings_info_list}
    sorted_headings = sorted(deep_headings_info_list, key=lambda x: len(x['original']), reverse=True)
    flexible_patterns = [r'\s+'.join(re.escape(word) for word in h['original'].split()) for h in sorted_headings]
    master_pattern = "|".join(flexible_patterns)
    
    last_end = 0
    output_parts = []
    for match in re.finditer(master_pattern, full_text):
        output_parts.append(_process_text_chunk(full_text[last_end:match.start()]))
        found_heading_text = match.group(0)
        normalized_found = normalize_text(found_heading_text)
        if normalized_found in normalized_map:
            level, original_text = normalized_map[normalized_found]
            output_parts.append(f"{'#' * level} {original_text.replace(chr(10), ' ')}\n\n")
        else:
            output_parts.append(_process_text_chunk(found_heading_text))
        last_end = match.end()
    output_parts.append(_process_text_chunk(full_text[last_end:]))
    return "".join(output_parts)


# ==================== Main Extraction Function ====================
def run_extraction(pdf_path, output_dir="mybook"):
    if os.path.exists(output_dir): shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    doc = fitz.open(pdf_path)
    original_toc = doc.get_toc()
    if not original_toc: print("Error: No bookmarks (TOC) found."); doc.close(); return
    chapter_toc = [item for item in original_toc if item[0] == 1]
    if not chapter_toc: print("Error: No Level 1 bookmarks found."); doc.close(); return
    
    print(f"Found {len(chapter_toc)} top-level chapters to process.")
    markdown_files_list = []
    
    min_level_for_text = HD_CONFIG.get("min_heading_level_for_text_match", 3)
    font_multiplier = HD_CONFIG.get("font_size_multiplier", 1.2)

    for i, chapter_item in enumerate(chapter_toc):
        level, title, start_page = chapter_item
        safe_title = clean_filename(title)
        print(f"\nProcessing Chapter: '{title}' (Page {start_page})")

        end_page = doc.page_count + 1
        if i + 1 < len(chapter_toc): end_page = chapter_toc[i+1][2]
        print(f"  - Content spans from page {start_page} to {end_page - 1}.")

        # Split headings into deep (text-match) and shallow (font-match)
        deep_headings_info_list = []
        try:
            start_index = original_toc.index(chapter_item)
            for j in range(start_index + 1, len(original_toc)):
                sub_item = original_toc[j]
                if sub_item[0] < min_level_for_text: continue # Skip shallow headings
                if sub_item[0] >= min_level_for_text:
                    deep_headings_info_list.append({"original": sub_item[1], "level": sub_item[0]})
                if sub_item[0] <= level: break
        except ValueError: print(f"  - Warning: Could not find chapter '{title}' in the main TOC.")

        if deep_headings_info_list: print(f"  - Using text-match for {len(deep_headings_info_list)} deep headings (Level {min_level_for_text}+).")
        else: print(f"  - No deep headings found for text-matching.")
        
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
            
            # Analyze page for font-based heading detection
            dominant_size = find_dominant_font_size(page)
            font_size_threshold = dominant_size * font_multiplier
            
            page_data = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            page_content_parts = {}
            ignored_text_areas = []

            for idx, b in enumerate(blocks):
                if b['type'] != 0: continue
                block_bbox = fitz.Rect(b["bbox"])
                if is_header_or_footer(block_bbox, page.rect): continue
                if any(area.intersects(block_bbox) for area in ignored_text_areas): continue
                
                image_md = ""
                text_for_caption = "".join("".join(s['text'] for s in l['spans']) for l in b.get('lines', [])).strip()
                if CAPTION_REGEX.match(text_for_caption):
                    image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                    if image_info:
                        relative_path = os.path.join("images", quote(image_info["filename"]))
                        short_alt = ' '.join(text_for_caption.split()[:5]) + "..."
                        image_md = f"![{short_alt}]({relative_path})\n"
                        if image_info.get("bbox"): ignored_text_areas.append(image_info["bbox"])
                
                # Pass all necessary info to the hybrid markdown converter
                markdown_text = get_markdown_from_block(b, deep_headings_info_list, font_size_threshold)
                
                if markdown_text:
                    page_content_parts[idx] = image_md + markdown_text

            # Uncaptioned image processing
            for img in page.get_images(full=True):
                # ... (unchanged)
                xref = img[0]
                if xref not in processed_img_xrefs:
                    img_block_idx = -1
                    for idx, b in enumerate(blocks):
                        if b.get("type") == 1 and b.get("number") == xref: img_block_idx = idx; break
                    if img_block_idx != -1 and img_block_idx not in page_content_parts:
                        try:
                            base_image = doc.extract_image(xref)
                            if not base_image: continue
                            image_filename = f"page_{page_num+1}_uncaptioned_img_{xref}.{base_image['ext']}"
                            relative_path = os.path.join("images", quote(image_filename))
                            with open(os.path.join(current_image_dir, image_filename), "wb") as f: f.write(base_image["image"])
                            page_content_parts[img_block_idx] = f"![Uncaptioned image on page {page_num+1}]({relative_path})\n\n"
                            processed_img_xrefs.add(xref)
                        except Exception as e: print(f"Warning: Could not process uncaptioned image xref {xref} on page {page_num+1}. Error: {e}")

            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]

        chapter_content = re.sub(r'\n{3,}', '\n\n', chapter_content)
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)
    
    # Metadata generation
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["Unknown Author"]
    book_data = {"kind": "Book", "title": book_title, "version": "0.1.0", "authors": book_authors, "translators": ["Generated by Script"], "year": str(datetime.now().year), "src": ".", "contents": markdown_files_list}
    with open(os.path.join(output_dir, "book.json"), 'w', encoding='utf-8') as f: json.dump(book_data, f, ensure_ascii=False, indent=2)

    doc.close()
    print("\nExtraction complete!")

if __name__ == "__main__":
    pdf_file = "your_file.pdf" 
    if os.path.exists(pdf_file):
        run_extraction(pdf_file)
    else:
        print(f"Error: File '{pdf_file}' not found.")