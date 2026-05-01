#  Copyright (c) 2017-2026 null. All rights reserved.
"""文件转换API端点，提供PDF转Word/Excel及文件下载功能"""
from fastapi import APIRouter, UploadFile, File, Request, Response

from app.services.convert_service import ConvertService
from app.utils.limiter import limiter

router = APIRouter(prefix="/convert", tags=["文件转换"])


@router.post(
    "/pdf-to-word",
    summary="PDF转Word",
    description="将PDF文件转换为Word文档，保留原始排版和格式",
)
@limiter.limit("60/minute")
async def pdf_to_word(request: Request, file: UploadFile = File(...)):
    return await ConvertService.pdf_to_word(file)


@router.post(
    "/pdf-to-excel",
    summary="PDF表格转Excel（结构化表格）",
    description="提取PDF中的结构化表格数据并转换为Excel文件",
)
@limiter.limit("60/minute")
async def pdf_table_to_excel(request: Request, file: UploadFile = File(...)):
    return await ConvertService.pdf_table_to_excel(file)


@router.post(
    "/pdf-text-to-excel",
    summary="PDF纯文字转Excel",
    description="提取PDF中的纯文字内容并转换为Excel文件",
)
@limiter.limit("60/minute")
async def pdf_text_to_excel(request: Request, file: UploadFile = File(...)):
    return await ConvertService.pdf_text_to_excel(file)


@router.post(
    "/pdf-scan-to-word",
    summary="PDF扫描件转Word（OCR识别图片文字）",
    description="通过OCR技术识别PDF扫描件中的图片文字，转换为可编辑的Word文档",
)
@limiter.limit("30/minute")
async def pdf_scan_to_word(request: Request, file: UploadFile = File(...)):
    return await ConvertService.pdf_scan_to_word(file)


@router.get(
    "/download/{filename}",
    summary="下载转换后的文件",
    description="根据文件名下载转换后的文件，下载完成后自动删除服务端临时文件",
)
@limiter.limit("60/minute")
async def download_file(request: Request, filename: str):
    file_content, downloaded_filename = ConvertService.download_file(filename)
    return Response(
        content=file_content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={downloaded_filename}"
        }
    )
