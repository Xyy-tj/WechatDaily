from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging

from app.models.chat import ChatRequest, ChatResponse, Message
from app.services.chat_service import ChatService
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def get_chat_service() -> ChatService:
    """依赖注入：获取聊天服务实例"""
    return ChatService(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL
    )

@router.post("/chat", response_model=ChatResponse)
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
