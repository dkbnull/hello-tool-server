<h1 align="center">Hello Tool Server</h1>

<p align="center">
    <a href="https://github.com/dkbnull/hello-tool-server" target="_blank">
       <img src="https://img.shields.io/badge/GitHub-访问地址-blue?logo=github">
    </a>
    <a href="https://gitee.com/dkbnull/hello-tool-server" target="_blank">
       <img src="https://img.shields.io/badge/Gitee-访问地址-red?logo=gitee">
    </a>
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue">
</p>

一个基于 FastAPI 的工具类服务，提供 PDF 转 Word、PDF 表格/文字转 Excel、PDF 扫描件 OCR 转 Word 等功能。

## 功能特性

- PDF 转 Word（完整保留格式）
- PDF 表格转 Excel（结构化表格提取）
- PDF 纯文字转 Excel（文本内容提取）
- PDF 扫描件转 Word（OCR 识别图片文字）
- 健康检查接口
- IP 访问控制（白名单/黑名单）
- CSRF 防护
- 多层限流保护
- 定时清理过期文件

## API 文档

服务启动后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 使用示例

```bash
# 1. 获取 CSRF Token（首次访问自动设置 cookie）
curl -c cookies.txt http://localhost:8000/

# 2. 提取 CSRF Token
CSRF_TOKEN=$(grep csrf_token cookies.txt | awk '{print $7}')

# 3. 上传文件转换（PDF 转 Word）
curl -X POST http://localhost:8000/convert/pdf-to-word \
  -b cookies.txt \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -F "file=@example.pdf"

# 4. 上传文件转换（PDF 扫描件转 Word）
curl -X POST http://localhost:8000/convert/pdf-scan-to-word \
  -b cookies.txt \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -F "file=@scan.pdf"

# 5. 下载转换结果
curl -O http://localhost:8000/convert/download/<filename>
```

## 项目结构

```
hello-tool-server/
├── app/
│   ├── api/                    # API 路由层
│   │   ├── auth.py             # 认证相关接口
│   │   └── convert.py          # 文件转换接口
│   ├── core/                   # 核心业务层
│   │   ├── config.py           # 集中配置管理
│   │   ├── exceptions.py       # 自定义异常体系
│   │   ├── pdf2docx.py         # PDF 转 Word 实现
│   │   ├── pdf2excel.py        # PDF 转 Excel 实现
│   │   └── pdf_scan2docx.py    # PDF 扫描件转 Word（OCR）实现
│   ├── schemas/                # 数据模型层
│   │   ├── auth.py             # 认证相关模型
│   │   └── convert.py          # 转换相关模型
│   ├── services/               # 业务服务层
│   │   ├── auth_service.py     # 认证服务
│   │   └── convert_service.py  # 文件转换服务
│   ├── utils/                  # 工具层
│   │   ├── api_utils.py        # API 通用处理函数
│   │   ├── file_utils.py       # 文件操作工具
│   │   ├── limiter.py          # 限流配置
│   │   ├── logger.py           # 日志配置
│   │   ├── request.py          # 请求工具函数
│   │   ├── scheduler.py        # 定时任务调度
│   │   └── security.py         # 安全中间件
│   └── main.py                 # 应用入口
└── requirements.txt            # Python 依赖
```

## 配置说明

所有配置均通过环境变量管理，支持 `.env` 文件。配置集中定义在 `app/core/config.py` 中。

### 基础配置

| 环境变量                       | 默认值        | 说明                   |
|----------------------------|------------|----------------------|
| `MAX_FILE_SIZE`            | `10485760` | 上传文件大小上限（字节），默认 10MB |
| `FILE_EXPIRY_MINUTES`      | `10`       | 临时文件过期时间（分钟）         |
| `CLEANUP_INTERVAL_MINUTES` | `5`        | 定时清理间隔（分钟）           |

### 安全配置

| 环境变量                | 默认值    | 说明                              |
|---------------------|--------|---------------------------------|
| `ALLOWED_IPS`       | （空）    | IP 白名单，逗号分隔，为空则不限制              |
| `BLOCKED_IPS`       | （空）    | IP 黑名单，逗号分隔                     |
| `RATE_LIMIT_PER_IP` | `5`    | 每个 IP 在时间窗口内的最大请求数              |
| `RATE_LIMIT_WINDOW` | `1`    | 速率限制时间窗口（秒）                     |
| `CSRF_TOKEN_EXPIRY` | `3600` | CSRF Token 过期时间（秒）              |
| `SECURE_COOKIE`     | `True` | 是否启用 Secure Cookie（生产环境应为 True） |

### CORS 配置

| 环境变量                     | 默认值    | 说明               |
|--------------------------|--------|------------------|
| `CORS_ORIGINS`           | `*`    | 允许的来源，逗号分隔       |
| `CORS_ALLOW_CREDENTIALS` | `True` | 是否允许携带凭证         |
| `CORS_ALLOW_METHODS`     | `*`    | 允许的 HTTP 方法，逗号分隔 |
| `CORS_ALLOW_HEADERS`     | `*`    | 允许的请求头，逗号分隔      |

## 安全机制

- **IP 访问控制**：支持白名单和黑名单
- **速率限制**：中间件级 + 路由级双重限流
- **CSRF 防护**：基于 Token 的跨站请求伪造防护
- **请求头校验**：检查 User-Agent 和 Content-Type
- **安全 Cookie**：HttpOnly + Secure + SameSite

## 技术栈

| 类别     | 技术                                    |
|--------|---------------------------------------|
| Web 框架 | FastAPI + Uvicorn                     |
| PDF 处理 | pdf2docx、tabula-py、pdfplumber、PyMuPDF |
| OCR 识别 | RapidOCR (rapidocr-onnxruntime)       |
| Excel  | openpyxl                              |
| Word   | python-docx                           |
| 限流     | slowapi                               |
| 定时任务   | APScheduler                           |
| 配置管理   | pydantic-settings                     |

## 注意事项

- 本服务仅用于测试和学习目的，生产环境使用请自行评估风险
- 文件上传后会在配置的过期时间后自动清理
- 下载后的文件会立即从服务器删除
- PDF 扫描件转 Word 使用 OCR 技术，识别精度取决于扫描件质量
- 建议在生产环境启用 HTTPS 和 Secure Cookie

## 许可证

Apache License 2.0

---

<p align="center">
  <a href="https://github.com/dkbnull">
    <img src="https://img.shields.io/badge/Author-null-42b883?style=flat-square">
  </a>
</p>