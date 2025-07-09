# pdf_trans
https://readonly.link/books/https://raw.githubusercontent.com/qig123/pdf_trans/refs/heads/main/mybook/book.json

# 配置
"font_size_multiplier": 1.2：如果一个文本块的字体大小是页面主流字体大小的 1.2倍 或以上，它就被认为是潜在的浅层标题。您可以根据需要调整这个值（比如 1.3 或 1.4）。
"min_heading_level_for_text_match": 3：从 第3层 标题开始，我们启用精确的文本内容匹配。第1层和第2层将使用字体大小来识别。
"shallow_heading_level": 2：所有通过字体大小识别出的浅层标题，都将被格式化为 H2（##）。