#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信群聊日报生成器 - FastAPI版本
使用微服务架构，将HTML转图片功能分离为独立服务
"""

import os
import argparse
import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Depends, Body, Request, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 导入应用模块
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.chat_service import ChatService
from app.services.template_service import TemplateService
from app.models.chat import (
    ChatRequest, ChatResponse,
    HTMLConversionRequest, HTMLConversionResponse,
    DailyReportRequest, DailyReportResponse
)
from app.utils.helpers import extract_html_from_response, save_html_content, convert_html_to_image

# 设置日志
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="微信群聊日报生成器API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="app/templates")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入
def get_chat_service() -> ChatService:
    """获取聊天服务实例"""
    return ChatService(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )

def get_template_service() -> TemplateService:
    """获取模板服务实例"""
    return TemplateService(templates_dir=settings.TEMPLATES_DIR)

# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# 聊天API
@app.post("/api/chat", response_model=ChatResponse, tags=["聊天"])
async def create_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    创建聊天完成

    Args:
        request: 聊天请求
        chat_service: 聊天服务实例

    Returns:
        聊天响应
    """
    try:
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # 调用聊天服务
        content = chat_service.create_chat(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False
        )

        # 返回响应
        return ChatResponse(
            content=content,
            model=request.model or settings.DEFAULT_MODEL
        )

    except Exception as e:
        logger.error(f"处理聊天请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 模板API
@app.get("/api/templates", response_model=list[str], tags=["模板"])
async def get_templates(
    template_service: TemplateService = Depends(get_template_service)
):
    """
    获取所有可用的模板

    Returns:
        模板文件名列表
    """
    return template_service.get_available_templates()

# HTML转图片API
@app.post("/api/html/convert", response_model=HTMLConversionResponse, tags=["HTML处理"])
async def convert_html(
    request: HTMLConversionRequest = Body(...)
):
    """
    将HTML内容或HTML文件转换为PNG图像

    Args:
        request: HTML转换请求

    Returns:
        HTML转换响应
    """
    # 参数验证
    if request.html_content is None and request.html_file_path is None:
        raise HTTPException(status_code=400, detail="必须提供html_content或html_file_path参数")

    # 调用HTML转图片服务
    success, png_file_path = convert_html_to_image(
        html_content=request.html_content,
        html_file_path=request.html_file_path,
        png_file_path=request.png_file_path
    )

    if success:
        return HTMLConversionResponse(
            success=True,
            png_file_path=png_file_path,
            message="HTML转换为图片成功"
        )
    else:
        raise HTTPException(status_code=500, detail="HTML转换为图片失败")

# 日报生成API
@app.post("/api/daily-report", response_model=DailyReportResponse, tags=["日报"])
async def generate_daily_report(
    request: DailyReportRequest,
    chat_service: ChatService = Depends(get_chat_service),
    template_service: TemplateService = Depends(get_template_service)
):
    """
    生成群聊日报

    Args:
        request: 日报生成请求
        chat_service: 聊天服务实例
        template_service: 模板服务实例

    Returns:
        日报生成响应
    """
    try:
        # 加载模板
        template = template_service.load_template(request.template_name)
        if not template:
            raise HTTPException(status_code=404, detail=f"模板 {request.template_name} 不存在")

        # 提取群聊名称（如果有）
        chat_group_name = "未知群聊"
        if request.chat_file_name:
            # 从文件名中提取群聊名称（去掉扩展名）
            chat_group_name = os.path.splitext(request.chat_file_name)[0]
            logger.info(f"从文件名提取的群聊名称: {chat_group_name}")

        # 创建消息
        messages = [
            {"role": "system", "content": template},
            {"role": "user", "content": f"请根据以下聊天记录生成完整版本的群日报，群聊名称为「{chat_group_name}」：\n{request.chat_content}"}
        ]

        # 调用聊天服务
        response_text = chat_service.create_chat(
            messages=messages,
            model=request.model,
            stream=False
        )

        # 提取HTML内容
        html_content = extract_html_from_response(response_text)
        if not html_content:
            return DailyReportResponse(
                html_content=response_text,
                success=False,
                message="未在响应中找到HTML内容"
            )

        # 保存HTML文件
        html_file_path = save_html_content(html_content)

        # 如果需要转换为图片
        png_file_path = None
        if request.convert_to_image:
            logger.info(f"开始将HTML转换为图片，HTML文件路径: {html_file_path}")
            success, png_file_path = convert_html_to_image(html_file_path=html_file_path)

            if success and png_file_path:
                logger.info(f"HTML转图片成功，图片路径: {png_file_path}")
                # 确保返回的是相对路径，便于前端处理
                if os.path.isabs(png_file_path):
                    # 获取文件名
                    png_filename = os.path.basename(png_file_path)
                    logger.info(f"图片文件名: {png_filename}")
                    # 更新png_file_path为相对路径
                    png_file_path = os.path.join(settings.OUTPUT_DIR, png_filename)
                    logger.info(f"更新后的图片路径: {png_file_path}")
            else:
                logger.error("HTML转图片失败")
                return DailyReportResponse(
                    html_content=html_content,
                    html_file_path=html_file_path,
                    success=True,
                    message="HTML生成成功，但转换为图片失败"
                )

        # 返回响应
        return DailyReportResponse(
            html_content=html_content,
            html_file_path=html_file_path,
            png_file_path=png_file_path,
            success=True,
            message="日报生成成功"
        )

    except Exception as e:
        logger.error(f"生成日报时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 获取图片API
@app.get("/api/image/{filename}", tags=["HTML处理"])
async def get_image(filename: str):
    """
    获取生成的图片

    Args:
        filename: 图片文件名

    Returns:
        图片文件
    """
    # 首先尝试在输出目录中查找
    image_path = os.path.join(settings.OUTPUT_DIR, filename)
    if os.path.exists(image_path):
        logger.info(f"找到图片: {image_path}")
        return FileResponse(image_path, media_type="image/png")

    # 如果没有找到，尝试在输出目录的子目录中查找
    for root, dirs, files in os.walk(settings.OUTPUT_DIR):
        for file in files:
            if file == filename:
                full_path = os.path.join(root, file)
                logger.info(f"在子目录中找到图片: {full_path}")
                return FileResponse(full_path, media_type="image/png")

    # 如果仍然没有找到，返回404错误
    logger.error(f"图片不存在: {filename}")
    raise HTTPException(status_code=404, detail="图片不存在")

# Web界面路由
@app.get("/", tags=["Web界面"])
async def index(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/templates", tags=["Web界面"])
async def templates_page(request: Request):
    """模板管理页面"""
    return templates.TemplateResponse("templates.html", {"request": request})

# 模板管理API
@app.post("/api/template", tags=["模板"])
async def create_template(
    template_name: str = Form(...),
    template_content: str = Form(...),
    template_service: TemplateService = Depends(get_template_service)
):
    """
    创建新模板

    Args:
        template_name: 模板名称
        template_content: 模板内容
        template_service: 模板服务实例

    Returns:
        创建结果
    """
    try:
        # 确保模板名称有.txt后缀
        if not template_name.endswith(".txt"):
            template_name += ".txt"

        # 保存模板
        template_path = os.path.join(settings.TEMPLATES_DIR, template_name)
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)

        return {"success": True, "message": "模板创建成功"}
    except Exception as e:
        logger.error(f"创建模板时出错: {str(e)}")
        return {"success": False, "message": str(e)}

@app.get("/api/template/{template_name}", tags=["模板"])
async def get_template(
    template_name: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """
    获取模板内容

    Args:
        template_name: 模板名称
        template_service: 模板服务实例

    Returns:
        模板内容
    """
    content = template_service.load_template(template_name)
    if not content:
        raise HTTPException(status_code=404, detail=f"模板 {template_name} 不存在")

    return {"content": content}

@app.put("/api/template/{template_name}", tags=["模板"])
async def update_template(
    template_name: str,
    template_content: str = Form(...),
    template_service: TemplateService = Depends(get_template_service)
):
    """
    更新模板内容

    Args:
        template_name: 模板名称
        template_content: 新的模板内容
        template_service: 模板服务实例

    Returns:
        更新结果
    """
    try:
        # 检查模板是否存在
        template_path = os.path.join(settings.TEMPLATES_DIR, template_name)
        if not os.path.exists(template_path):
            return {"success": False, "message": f"模板 {template_name} 不存在"}

        # 更新模板
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)

        return {"success": True, "message": "模板更新成功"}
    except Exception as e:
        logger.error(f"更新模板时出错: {str(e)}")
        return {"success": False, "message": str(e)}

@app.delete("/api/template/{template_name}", tags=["模板"])
async def delete_template(
    template_name: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """
    删除模板

    Args:
        template_name: 模板名称
        template_service: 模板服务实例

    Returns:
        删除结果
    """
    try:
        # 检查模板是否存在
        template_path = os.path.join(settings.TEMPLATES_DIR, template_name)
        if not os.path.exists(template_path):
            return {"success": False, "message": f"模板 {template_name} 不存在"}

        # 删除模板
        os.remove(template_path)

        return {"success": True, "message": "模板删除成功"}
    except Exception as e:
        logger.error(f"删除模板时出错: {str(e)}")
        return {"success": False, "message": str(e)}

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的事件"""
    # 确保输出目录存在
    if not os.path.exists(settings.OUTPUT_DIR):
        os.makedirs(settings.OUTPUT_DIR)
        logger.info(f"创建输出目录: {settings.OUTPUT_DIR}")

    # 确保模板目录存在
    if not os.path.exists(settings.TEMPLATES_DIR):
        os.makedirs(settings.TEMPLATES_DIR)
        logger.info(f"创建模板目录: {settings.TEMPLATES_DIR}")

    logger.info(f"{settings.APP_NAME} 启动完成")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的事件"""
    logger.info(f"{settings.APP_NAME} 关闭")

# 命令行入口
def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='微信群聊日报生成器')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听主机')
    parser.add_argument('--port', type=int, default=8000, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

    # 更新调试模式设置
    if args.debug:
        settings.DEBUG = True
        setup_logging(debug=True)

    logger.info(f"启动 {settings.APP_NAME}，监听 {args.host}:{args.port}")
    uvicorn.run("app_soa:app", host=args.host, port=args.port, reload=settings.DEBUG)

if __name__ == "__main__":
    main()
