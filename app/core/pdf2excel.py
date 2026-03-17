#  Copyright (c) 2017-2026 null. All rights reserved.
import pdfplumber
import tabula
from openpyxl import Workbook

from app.utils.file_utils import get_file_path


def convert_pdf_table_to_excel(pdf_filename: str, excel_filename: str) -> str:
    """
    PDF表格转Excel（结构化表格）
    :param pdf_filename: 上传的PDF文件名
    :param excel_filename: 输出的Excel文件名
    :return: Excel文件完整路径
    """
    pdf_path = get_file_path(pdf_filename)
    excel_path = get_file_path(excel_filename)

    try:
        # 提取所有表格
        tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
        if not tables:
            raise RuntimeError("未在PDF中检测到结构化表格")

        wb = Workbook()
        wb.remove(wb.active)  # 删除默认工作表

        # 逐个表格写入不同工作表
        for i, table in enumerate(tables):
            ws = wb.create_sheet(title=f"表格{i + 1}")
            for row in table.values.tolist():
                ws.append(row)

        wb.save(excel_path)
        return excel_path
    except Exception as e:
        raise RuntimeError(f"PDF表格转Excel失败：{str(e)}")


def convert_pdf_text_to_excel(pdf_filename: str, excel_filename: str) -> str:
    """
    PDF纯文字转Excel（无表格场景）
    :param pdf_filename: 上传的PDF文件名
    :param excel_filename: 输出的Excel文件名
    :return: Excel文件完整路径
    """
    pdf_path = get_file_path(pdf_filename)
    excel_path = get_file_path(excel_filename)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            wb = Workbook()
            ws = wb.active
            ws.title = "PDF文字内容"

            # 逐页提取文字
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    ws.append([f"==== 第{page_num}页 ===="])
                    for line in text.split("\n"):
                        ws.append([line])
                    ws.append([""])  # 空行分隔

        wb.save(excel_path)
        return excel_path
    except Exception as e:
        raise RuntimeError(f"PDF文字转Excel失败：{str(e)}")
