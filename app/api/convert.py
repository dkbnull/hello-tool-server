#  Copyright (c) 2017-2026 null. All rights reserved.
import os

from fastapi import APIRouter, UploadFile, File, HTTPException, Response, Request

from app.core.pdf2docx import convert_pdf_to_word
from app.core.pdf2excel import convert_pdf_table_to_excel, convert_pdf_text_to_excel
from app.utils.file_utils import (
    get_unique_filename,
    validate_file,
    get_file_path
)
from app.utils.limiter import limiter
from app.utils.logger import logger

# 定义文件大小限制（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 创建路由对象
router = APIRouter(prefix="/convert", tags=["文件转换"])


# ------------------- PDF转Word接口 -------------------
@router.post("/pdf-to-word", summary="PDF转Word")
@limiter.limit("10/second")
async def pdf_to_word(request: Request, file: UploadFile = File(...)):
    # 记录请求开始
    logger.info(f"PDF转Word请求开始，文件名: {file.filename}")

    # 1. 校验文件
    if not validate_file(file, [".pdf"]):
        logger.warning(f"文件类型错误，文件名: {file.filename}")
        raise HTTPException(status_code=400, detail="仅支持PDF格式文件")

    # 2. 检查文件大小
    content = await file.read()
    file_size = len(content)
    logger.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB")

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"文件大小超过限制，文件名: {file.filename}，大小: {file_size / 1024 / 1024:.2f}MB")
        raise HTTPException(status_code=400, detail="文件大小超过限制，最大支持10MB")

    # 3. 保存上传的PDF文件
    pdf_filename = get_unique_filename(file.filename, ".pdf")
    pdf_path = get_file_path(pdf_filename)
    with open(pdf_path, "wb") as f:
        f.write(content)
    logger.info(f"PDF文件保存成功，文件名: {pdf_filename}")

    # 4. 执行转换
    try:
        word_filename = get_unique_filename(file.filename, ".docx")
        logger.info(f"开始转换PDF到Word，输出文件名: {word_filename}")

        word_path = convert_pdf_to_word(pdf_filename, word_filename)

        # 5. 转换完成后删除原PDF文件
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"原PDF文件已删除: {pdf_filename}")

        # 6. 返回下载链接
        response = {
            "code": 200,
            "message": "转换成功",
            "data": {
                "download_url": f"/download/{word_filename}",
                "filename": word_filename
            }
        }
        logger.info(f"PDF转Word成功，输出文件名: {word_filename}")
        return response
    except Exception as e:
        # 清理临时文件
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"转换失败，清理临时文件: {pdf_filename}")
        logger.error(f"PDF转Word失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- PDF表格转Excel接口 -------------------
@router.post("/pdf-to-excel", summary="PDF表格转Excel（结构化表格）")
@limiter.limit("10/second")
async def pdf_table_to_excel(request: Request, file: UploadFile = File(...)):
    # 记录请求开始
    logger.info(f"PDF表格转Excel请求开始，文件名: {file.filename}")

    # 1. 校验文件
    if not validate_file(file, [".pdf"]):
        logger.warning(f"文件类型错误，文件名: {file.filename}")
        raise HTTPException(status_code=400, detail="仅支持PDF格式文件")

    # 2. 检查文件大小
    content = await file.read()
    file_size = len(content)
    logger.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB")

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"文件大小超过限制，文件名: {file.filename}，大小: {file_size / 1024 / 1024:.2f}MB")
        raise HTTPException(status_code=400, detail="文件大小超过限制，最大支持10MB")

    # 3. 保存PDF文件
    pdf_filename = get_unique_filename(file.filename, ".pdf")
    pdf_path = get_file_path(pdf_filename)
    with open(pdf_path, "wb") as f:
        f.write(content)
    logger.info(f"PDF文件保存成功，文件名: {pdf_filename}")

    # 4. 执行转换
    try:
        excel_filename = get_unique_filename(file.filename, ".xlsx")
        logger.info(f"开始转换PDF表格到Excel，输出文件名: {excel_filename}")

        excel_path = convert_pdf_table_to_excel(pdf_filename, excel_filename)

        # 5. 转换完成后删除原PDF文件
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"原PDF文件已删除: {pdf_filename}")

        response = {
            "code": 200,
            "message": "转换成功",
            "data": {
                "download_url": f"/download/{excel_filename}",
                "filename": excel_filename
            }
        }
        logger.info(f"PDF表格转Excel成功，输出文件名: {excel_filename}")
        return response
    except Exception as e:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"转换失败，清理临时文件: {pdf_filename}")
        logger.error(f"PDF表格转Excel失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- PDF文字转Excel接口 -------------------
@router.post("/pdf-text-to-excel", summary="PDF纯文字转Excel")
@limiter.limit("10/second")
async def pdf_text_to_excel(request: Request, file: UploadFile = File(...)):
    # 记录请求开始
    logger.info(f"PDF文字转Excel请求开始，文件名: {file.filename}")

    # 1. 校验文件
    if not validate_file(file, [".pdf"]):
        logger.warning(f"文件类型错误，文件名: {file.filename}")
        raise HTTPException(status_code=400, detail="仅支持PDF格式文件")

    # 2. 检查文件大小
    content = await file.read()
    file_size = len(content)
    logger.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB")

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"文件大小超过限制，文件名: {file.filename}，大小: {file_size / 1024 / 1024:.2f}MB")
        raise HTTPException(status_code=400, detail="文件大小超过限制，最大支持10MB")

    # 3. 保存PDF文件
    pdf_filename = get_unique_filename(file.filename, ".pdf")
    pdf_path = get_file_path(pdf_filename)
    with open(pdf_path, "wb") as f:
        f.write(content)
    logger.info(f"PDF文件保存成功，文件名: {pdf_filename}")

    # 4. 执行转换
    try:
        excel_filename = get_unique_filename(file.filename, ".xlsx")
        logger.info(f"开始转换PDF文字到Excel，输出文件名: {excel_filename}")

        excel_path = convert_pdf_text_to_excel(pdf_filename, excel_filename)

        # 5. 转换完成后删除原PDF文件
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"原PDF文件已删除: {pdf_filename}")

        response = {
            "code": 200,
            "message": "转换成功",
            "data": {
                "download_url": f"/download/{excel_filename}",
                "filename": excel_filename
            }
        }
        logger.info(f"PDF文字转Excel成功，输出文件名: {excel_filename}")
        return response
    except Exception as e:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"转换失败，清理临时文件: {pdf_filename}")
        logger.error(f"PDF文字转Excel失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- 文件下载接口 -------------------
@router.get("/download/{filename}", summary="下载转换后的文件")
@limiter.limit("10/second")
async def download_file(request: Request, filename: str, response: Response):
    # 记录请求开始
    logger.info(f"文件下载请求开始，文件名: {filename}")

    file_path = get_file_path(filename)
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
