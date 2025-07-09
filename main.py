import fitz  # PyMuPDF - PDF处理库
import os
import re
import json
import shutil
from urllib.parse import quote
from datetime import datetime

# 清理文件名中的非法字符
def clean_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)  # 替换特殊字符为下划线
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)  # 移除控制字符
    name = name.strip(' .')  # 去除首尾空格和点
    return (name[:100] if len(name) > 100 else name) or "untitled"  # 截断长文件名

# 判断文本块是否位于页眉或页脚区域
def is_header_or_footer(block_bbox, page_rect, header_margin=0.12, footer_margin=0.12):
    header_boundary = page_rect.y0 + page_rect.height * header_margin  # 计算页眉边界
    footer_boundary = page_rect.y1 - page_rect.height * footer_margin  # 计算页脚边界
    if block_bbox.y1 < header_boundary: return True  # 在页眉区域
    if block_bbox.y0 > footer_boundary: return True  # 在页脚区域
    return False

# 为标题查找对应的图像
def find_image_for_caption(doc, page, blocks, caption_block_idx, image_dir, processed_blocks):
    # 检查前一个块是否是图像
    if caption_block_idx > 0:
        prev_block = blocks[caption_block_idx - 1]
        if prev_block["type"] == 1:  # 类型1表示图像块
            xref = prev_block["number"]
            if xref not in processed_blocks:
                try:
                    # 提取图像并保存
                    base_image = doc.extract_image(xref)
                    if not base_image: return None
                    filename = f"page_{page.number+1}_img_{xref}.{base_image['ext']}"
                    with open(os.path.join(image_dir, filename), "wb") as f: f.write(base_image["image"])
                    processed_blocks.add(xref)
                    return {"filename": filename, "bbox": fitz.Rect(prev_block["bbox"])}
                except Exception: return None
    
    # 如果在前面没找到图像，则搜索标题上方的区域
    caption_bbox = fitz.Rect(blocks[caption_block_idx]["bbox"])
    search_area = fitz.Rect(page.rect.x0, caption_bbox.y0 - 400, page.rect.x1, caption_bbox.y0 - 5)
    search_area.intersect(page.rect)
    
    if not search_area.is_empty and search_area.height > 10:
        # 将搜索区域保存为图片
        filename = f"page_{page.number+1}_vector_{int(caption_bbox.y0)}.png"
        pix = page.get_pixmap(clip=search_area, dpi=150)
        pix.save(os.path.join(image_dir, filename))
        return {"filename": filename, "bbox": search_area}
    return None

# 主处理函数
def run_extraction_stable(pdf_path, output_dir="mybook"):
    """
    处理PDF文件，提取1级和2级书签内容，生成Markdown文件和图片
    """
    # 清理并创建输出目录
    if os.path.exists(output_dir):
        print(f"发现旧输出目录 '{output_dir}'。正在删除...")
        shutil.rmtree(output_dir)
        print("旧目录已删除。")
    os.makedirs(output_dir)

    # 打开PDF文件
    doc = fitz.open(pdf_path)
    original_toc = doc.get_toc()  # 获取原始目录
    if not original_toc:
        print("错误: 未找到书签。")
        return

    # 关键修改：只处理1级和2级书签
    toc = [item for item in original_toc if item[0] <= 2]
    print(f"处理 {len(toc)} 个书签(从原始 {len(original_toc)} 个过滤到最多2级)。")

    markdown_files_list = []  # 存储生成的Markdown文件路径
    level_paths = {}  # 存储各级路径
    CAPTION_REGEX = re.compile(r'^(Figure|Fig\.?|Table|Chart|图|表)\s+[\d\.\-A-Za-z]+', flags=re.IGNORECASE)

    # 处理每个书签项
    for i, item in enumerate(toc):
        level, title, start_page = item
        safe_title = clean_filename(title)
        level_paths[level] = safe_title
        print(f"{'  ' * (level-1)}-> 处理: {title}")

        # 判断是否是父节点(是否有子节点)
        is_parent_node = (i + 1 < len(toc)) and (toc[i+1][0] > level)
        
        # 确定内容结束页
        end_page = doc.page_count + 1
        for next_item in toc[i+1:]:
            if next_item[0] <= level:
                end_page = next_item[2]
                break

        if start_page >= end_page:
            print(f"{'  ' * (level-1)}  - 跳过空章节。")
            if is_parent_node: 
                current_content_dir = os.path.join(output_dir, safe_title)
                os.makedirs(current_content_dir, exist_ok=True)
            continue
        
        # 构建父目录路径
        parent_dir_parts = [level_paths[l] for l in range(1, level)]
        parent_dir = os.path.join(output_dir, *parent_dir_parts)

        # 1级书签创建目录和摘要文件，2级书签创建Markdown文件
        if level == 1:
            current_content_dir = os.path.join(parent_dir, safe_title)
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")
        else: # level == 2
            current_content_dir = parent_dir
            output_filepath = os.path.join(current_content_dir, f"{safe_title}.md")

        # 创建图片目录
        md_file_containing_dir = os.path.dirname(output_filepath)
        current_image_dir = os.path.join(md_file_containing_dir, "images")
        os.makedirs(current_image_dir, exist_ok=True)
        
        # 初始化章节内容
        chapter_content = f"# {title}\n\n"
        processed_img_xrefs = set()  # 记录已处理的图片

        # 处理每一页
        for page_num in range(start_page - 1, end_page - 1):
            if page_num >= doc.page_count: continue
            page = doc.load_page(page_num)
            
            # 获取页面文本块并排序
            page_data = page.get_text("dict")
            blocks = sorted(page_data["blocks"], key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            ignored_text_areas = []  # 需要忽略的文本区域(如图像区域)
            page_content_parts = {}  # 存储页面各部分内容

            # 查找并处理标题块
            caption_blocks_indices = {idx for idx, b in enumerate(blocks) if b["type"] == 0 and "lines" in b and CAPTION_REGEX.match(''.join(s["text"] for s in b["lines"][0]["spans"]).strip())}
            for idx in sorted(list(caption_blocks_indices)):
                b = blocks[idx]
                full_caption = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                short_alt = ' '.join(full_caption.split()[:4]) + "..."
                # 查找标题对应的图像
                image_info = find_image_for_caption(doc, page, blocks, idx, current_image_dir, processed_img_xrefs)
                content = ""
                if image_info:
                    relative_path = os.path.join("images", quote(image_info["filename"]))
                    content = f"![{short_alt}]({relative_path})\n*{full_caption}*\n\n"
                    if image_info.get("bbox"):
                        ignored_text_areas.append(image_info["bbox"])
                else:
                    content = f"*{full_caption}*\n\n"
                page_content_parts[idx] = content

            # 处理普通文本块
            for idx, b in enumerate(blocks):
                if b["type"] == 0 and idx not in caption_blocks_indices:
                    block_bbox = fitz.Rect(b["bbox"])
                    if is_header_or_footer(block_bbox, page.rect): continue
                    is_in_image = False
                    for area in ignored_text_areas:
                        if area.intersects(block_bbox):
                            is_in_image = True
                            break
                    if not is_in_image:
                        plain_text = ' '.join(''.join(s["text"] for s in l["spans"]) for l in b["lines"]).replace('\n', ' ').strip()
                        if plain_text:
                           page_content_parts[idx] = plain_text + "\n\n"

            # 处理未加标题的图片
            for img in page.get_images(full=True):
                xref = img[0]
                if xref not in processed_img_xrefs:
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
                            content = f"![未加标题的图片 第{page_num+1}页 xref {xref}]({relative_path})\n\n"
                            page_content_parts[img_block_idx] = content
                            processed_img_xrefs.add(xref)
                        except Exception as e:
                            print(f"警告: 无法处理未加标题的图片 xref {xref} 在第 {page_num+1} 页。错误: {e}")

            # 按顺序组合页面内容
            for idx in sorted(page_content_parts.keys()):
                chapter_content += page_content_parts[idx]

        # 写入Markdown文件
        with open(output_filepath, "w", encoding="utf-8") as f: f.write(chapter_content)
        relative_md_path = os.path.relpath(output_filepath, output_dir).replace(os.sep, '/')
        markdown_files_list.append(relative_md_path)

    # 生成书籍元数据
    metadata = doc.metadata
    book_title = metadata.get('title') or os.path.splitext(os.path.basename(pdf_path))[0]
    book_authors = [metadata.get('author')] if metadata.get('author') else ["未知作者"]
    book_data = {
        "kind": "Book",
        "title": book_title,
        "version": "0.1.0",
        "authors": book_authors,
        "translators": ["由脚本生成"],
        "year": str(datetime.now().year),
        "src": ".",
        "contents": markdown_files_list
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