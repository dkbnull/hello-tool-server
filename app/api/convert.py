#  Copyright (c) 2017-2026 null. All rights reserved.
import os

from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Request

from app.core.pdf2docx import convert_pdf_to_word
from app.core.pdf2excel import convert_pdf_table_to_excel, convert_pdf_text_to_excel
from app.utils.api_utils import ApiUtils
from app.utils.limiter import limiter
from app.utils.logger import logger

# 创建路由对象
router = APIRouter(prefix="/convert", tags=["文件转换"])


async def handle_conversion_request(request: Request, file: UploadFile, conversion_func, output_ext: str,
                                    operation_name: str):
    """处理转换请求的通用函数"""
    # 记录请求开始
    logger.info(f"{operation_name}请求开始，文件名: {file.filename}")

    # 处理上传的文件
    pdf_filename, pdf_path, _ = await ApiUtils.process_uploaded_file(file, [".pdf"])

    # 执行转换
    try:
        output_filename = ApiUtils.get_unique_filename(file.filename, output_ext)
        logger.info(f"开始{operation_name}，输出文件名: {output_filename}")

        conversion_func(pdf_filename, output_filename)

        # 转换完成后删除原PDF文件
        ApiUtils.cleanup_file(pdf_path, pdf_filename)

        # 返回下载链接
        return ApiUtils.create_response(output_filename, operation_name)
    except Exception as e:
        # 清理临时文件
        ApiUtils.cleanup_file(pdf_path, pdf_filename)
        logger.error(f"{operation_name}失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- PDF转Word接口 -------------------
@router.post("/pdf-to-word", summary="PDF转Word")
@limiter.limit("60/minute")
async def pdf_to_word(request: Request, file: UploadFile = File(...)):
    return await handle_conversion_request(
        request, file, convert_pdf_to_word, ".docx", "PDF转Word"
    )


# ------------------- PDF表格转Excel接口 -------------------
@router.post("/pdf-to-excel", summary="PDF表格转Excel（结构化表格）")
@limiter.limit("60/minute")
async def pdf_table_to_excel(request: Request, file: UploadFile = File(...)):
    return await handle_conversion_request(
        request, file, convert_pdf_table_to_excel, ".xlsx", "PDF表格转Excel"
    )


# ------------------- PDF文字转Excel接口 -------------------
@router.post("/pdf-text-to-excel", summary="PDF纯文字转Excel")
@limiter.limit("60/minute")
async def pdf_text_to_excel(request: Request, file: UploadFile = File(...)):
    return await handle_conversion_request(
        request, file, convert_pdf_text_to_excel, ".xlsx", "PDF文字转Excel"
    )


# ------------------- 文件下载接口 -------------------
@router.get("/download/{filename}", summary="下载转换后的文件")
@limiter.limit("60/minute")
async def download_file(request: Request, filename: str, response: Response):
    # 记录请求开始
    logger.info(f"文件下载请求开始，文件名: {filename}")

    file_path = ApiUtils.get_file_path(filename)
    if not os.path.exists(file_path):
        logger.warning(f"文件不存在，文件名: {filename}")
        raise HTTPException(status_code=404, detail="文件不存在")

    # 读取文件内容
    with open(file_path, "rb") as f:
        file_content = f.read()
    logger.info(f"文件读取成功，文件名: {filename}，大小: {len(file_content) / 1024 / 1024:.2f}MB")

    # 删除文件
    os.remove(file_path)
    logger.info(f"文件已删除: {filename}")

    # 返回文件内容
    response = Response(
        content=file_content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
    logger.info(f"文件下载完成，文件名: {filename}")
    return response
