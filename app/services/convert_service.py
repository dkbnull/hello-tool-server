#  Copyright (c) 2017-2026 null. All rights reserved.
"""文件转换服务模块，处理PDF转Word/Excel等业务逻辑"""
import os

from fastapi import UploadFile

from app.core.exceptions import NotFoundException, BusinessException
from app.core.pdf2docx import convert_pdf_to_word
from app.core.pdf2excel import convert_pdf_table_to_excel, convert_pdf_text_to_excel
from app.core.pdf_scan2docx import convert_pdf_scan_to_word
from app.utils.api_utils import process_uploaded_file, cleanup_file, create_response
from app.utils.file_utils import get_unique_filename, get_file_path
from app.utils.logger import logger


class ConvertService:
    """文件转换服务，负责PDF文件转换的业务逻辑处理"""

    ALLOWED_PDF_EXTENSIONS = [".pdf"]
    DEFAULT_SCAN_DPI = 200

    @staticmethod
    async def handle_conversion(
            file: UploadFile,
            conversion_func,
            output_ext: str,
            operation_name: str,
    ) -> dict:
        """
        处理转换请求的通用方法

        :param file: 上传的文件对象
        :param conversion_func: 转换函数
        :param output_ext: 输出文件后缀
        :param operation_name: 操作名称（用于日志记录）
        :return: 转换结果响应字典
        :raises ValidationError: 文件类型错误或大小超限
        :raises BusinessException: 转换过程失败
        """
        logger.info("%s请求开始，文件名: %s", operation_name, file.filename)

        pdf_filename, pdf_path, _ = await process_uploaded_file(
            file, ConvertService.ALLOWED_PDF_EXTENSIONS
        )

        try:
            output_filename = get_unique_filename(file.filename, output_ext)
            logger.info("开始%s，输出文件名: %s", operation_name, output_filename)

            conversion_func(pdf_filename, output_filename)

            cleanup_file(pdf_path, pdf_filename)

            return create_response(output_filename, operation_name)
        except Exception as e:
            cleanup_file(pdf_path, pdf_filename)
            logger.error("%s失败: %s", operation_name, str(e), exc_info=True)
            raise BusinessException(message=f"{operation_name}失败：{str(e)}")

    @staticmethod
    async def pdf_to_word(file: UploadFile) -> dict:
        """
        PDF转Word

        :param file: 上传的PDF文件
        :return: 转换结果响应字典
        """
        return await ConvertService.handle_conversion(
            file, convert_pdf_to_word, ".docx", "PDF转Word"
        )

    @staticmethod
    async def pdf_table_to_excel(file: UploadFile) -> dict:
        """
        PDF表格转Excel（结构化表格）

        :param file: 上传的PDF文件
        :return: 转换结果响应字典
        """
        return await ConvertService.handle_conversion(
            file, convert_pdf_table_to_excel, ".xlsx", "PDF表格转Excel"
        )

    @staticmethod
    async def pdf_text_to_excel(file: UploadFile) -> dict:
        """
        PDF纯文字转Excel

        :param file: 上传的PDF文件
        :return: 转换结果响应字典
        """
        return await ConvertService.handle_conversion(
            file, convert_pdf_text_to_excel, ".xlsx", "PDF文字转Excel"
        )

    @staticmethod
    async def pdf_scan_to_word(file: UploadFile) -> dict:
        """
        PDF扫描件转Word（OCR识别图片文字）

        :param file: 上传的PDF文件
        :return: 转换结果响应字典
        """
        return await ConvertService.handle_conversion(
            file, convert_pdf_scan_to_word, ".docx", "PDF扫描件转Word"
        )

    @staticmethod
    def download_file(filename: str) -> tuple[bytes, str]:
        """
        下载转换后的文件

        :param filename: 文件名
        :return: (文件内容字节, 文件名) 元组
        :raises NotFoundException: 文件不存在
        """
        logger.info("文件下载请求开始，文件名: %s", filename)

        file_path = get_file_path(filename)
        if not os.path.exists(file_path):
            logger.warning("文件不存在，文件名: %s", filename)
            raise NotFoundException(message="文件不存在")

        with open(file_path, "rb") as f:
            file_content = f.read()
        logger.info("文件读取成功，文件名: %s，大小: %.2fMB", filename, len(file_content) / 1024 / 1024)

        os.remove(file_path)
        logger.info("文件已删除: %s", filename)

        return file_content, filename
