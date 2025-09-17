import PyPDF2


def read_pdf(file_path: str, start_page: int, end_page: int, chunk_size: int = 2000):
    # 加载 PDF 文件
    pdf_reader = PyPDF2.PdfReader(file_path)

    text = ""
    for page_no in range(start_page, end_page + 1):
        page = pdf_reader.pages[page_no]
        text += page.extract_text()
    return text


if __name__ == '__main__':
    pdf = read_pdf("F:\Download\认知觉醒：开启自我改变的原动力.pdf", 1, 10)
    print(pdf)
