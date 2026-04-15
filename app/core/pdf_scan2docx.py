#  Copyright (c) 2017-2026 null. All rights reserved.
import fitz
from docx import Document
from rapidocr_onnxruntime import RapidOCR

from app.utils.file_utils import get_file_path

_ocr_engine = None


def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine


def _pdf_page_to_image(page, dpi=200):
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    return pix.tobytes("png")


def _ocr_image(image_bytes: bytes) -> str:
    ocr = _get_ocr_engine()
    result, _ = ocr(image_bytes)
    if not result:
        return ""
    lines = []
    for item in result:
        lines.append(item[1])
    return "\n".join(lines)


def convert_pdf_scan_to_word(pdf_filename: str, word_filename: str, dpi: int = 200) -> str:
    """
    PDF扫描件（图片）转Word，通过OCR识别图片中的文字
    :param pdf_filename: 上传的PDF文件名（仅文件名，不含路径）
    :param word_filename: 输出的Word文件名（仅文件名，不含路径）
    :param dpi: PDF转图片的DPI，值越大识别精度越高但速度越慢，默认200
    :return: Word文件的完整路径
    """
    pdf_path = get_file_path(pdf_filename)
    word_path = get_file_path(word_filename)

    try:
        doc = Document()
        pdf_doc = fitz.open(pdf_path)

        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            image_bytes = _pdf_page_to_image(page, dpi=dpi)
            text = _ocr_image(image_bytes)

            if page_num > 0:
                doc.add_page_break()

            heading = doc.add_heading(f"第 {page_num + 1} 页", level=2)
            heading.alignment = 0

            if text.strip():
                for line in text.split("\n"):
                    doc.add_paragraph(line)
            else:
                doc.add_paragraph("（此页未识别到文字内容）")

        pdf_doc.close()
        doc.save(word_path)
        return word_path
    except Exception as e:
        raise RuntimeError(f"PDF扫描件转Word失败：{str(e)}")
