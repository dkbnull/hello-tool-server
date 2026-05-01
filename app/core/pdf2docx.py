#  Copyright (c) 2017-2026 null. All rights reserved.
"""PDF转Word模块，使用pdf2docx库将PDF文件转换为Word文档"""
from pdf2docx import Converter

from app.utils.file_utils import get_file_path


def convert_pdf_to_word(pdf_filename: str, word_filename: str) -> str:
    """
    执行PDF转Word

    :param pdf_filename: 上传的PDF文件名（仅文件名，不含路径）
    :param word_filename: 输出的Word文件名（仅文件名，不含路径）
    :return: Word文件的完整路径
    :raises RuntimeError: 转换过程失败时抛出
    """
    pdf_path = get_file_path(pdf_filename)
    word_path = get_file_path(word_filename)

    try:
        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()
        return word_path
    except Exception as e:
        raise RuntimeError(f"PDF转Word失败：{str(e)}")
