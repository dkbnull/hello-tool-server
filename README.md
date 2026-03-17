<h1 align="center">Hello Tool Server</h1>

<p align="center">
    <a href="https://github.com/dkbnull/hello-tool-server" target="_blank">
       <img src="https://img.shields.io/badge/GitHub-访问地址-blue?logo=github">
    </a>
    <a href="https://gitee.com/dkbnull/hello-tool-server" target="_blank">
       <img src="https://img.shields.io/badge/Gitee-访问地址-red?logo=gitee">
    </a>
</p>

一个基于FastAPI的工具类服务，提供PDF转Word、PDF表格转Excel、PDF纯文字转Excel等功能。

## 项目功能

- ✅ PDF转Word（完整保留格式）
- ✅ PDF表格转Excel（结构化表格）
- ✅ PDF纯文字转Excel（文本内容提取）
- ✅ 健康检查接口
- ✅ 限流保护
- ✅ 定时任务管理

## API文档

服务启动后，可以访问以下地址查看API文档：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

## 配置说明

- **文件大小限制**：最大支持10MB文件
- **限流配置**：默认限制10次请求/秒
- **临时文件**：转换完成后自动清理

**注意**：本服务仅用于测试和学习目的，生产环境使用请自行评估风险。