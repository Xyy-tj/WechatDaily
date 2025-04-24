from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import logging
import os

from app.models.chat import HTMLConversionRequest, HTMLConversionResponse, DailyReportRequest, DailyReportResponse, Message
from app.services.chat_service import ChatService
from app.services.template_service import TemplateService
from app.utils.helpers import extract_html_from_response, save_html_content, convert_html_to_image
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def get_chat_service() -> ChatService:
    """依赖注入：获取聊天服务实例"""
    return ChatService(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )

def get_template_service() -> TemplateService:
    """依赖注入：获取模板服务实例"""
    return TemplateService(templates_dir=settings.TEMPLATES_DIR)

@router.get("/templates", response_model=List[str])
async def get_templates(
    template_service: TemplateService = Depends(get_template_service)
):
    """
    获取所有可用的模板
    
    Returns:
        模板文件名列表
    """
    return template_service.get_available_templates()

@router.post("/convert", response_model=HTMLConversionResponse)
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

@router.post("/daily-report", response_model=DailyReportResponse)
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
        
        # 创建消息
        messages = [
            {"role": "system", "content": template},
            {"role": "user", "content": f"请根据以下聊天记录生成群日报：\n{request.chat_content}"}
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
            success, png_file_path = convert_html_to_image(html_file_path=html_file_path)
            if not success:
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

@router.get("/image/{filename}")
async def get_image(filename: str):
    """
    获取生成的图片
    
    Args:
        filename: 图片文件名
        
    Returns:
        图片文件
    """
    image_path = os.path.join(settings.OUTPUT_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    
    return FileResponse(image_path, media_type="image/png")
