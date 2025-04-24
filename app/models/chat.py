from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    """聊天消息模型"""
    role: str
    content: str

class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 100000
    stream: bool = False

class ChatResponse(BaseModel):
    """聊天响应模型"""
    content: str
    model: str

class HTMLConversionRequest(BaseModel):
    """HTML转换请求模型"""
    html_content: Optional[str] = None
    html_file_path: Optional[str] = None
    png_file_path: Optional[str] = None

class HTMLConversionResponse(BaseModel):
    """HTML转换响应模型"""
    success: bool
    png_file_path: str
    message: Optional[str] = None

class DailyReportRequest(BaseModel):
    """日报生成请求模型"""
    chat_content: str
    chat_file_name: Optional[str] = None  # 聊天文件名，用于提取群聊名称
    template_name: Optional[str] = "default_template.txt"
    model: Optional[str] = None
    convert_to_image: bool = True

class DailyReportResponse(BaseModel):
    """日报生成响应模型"""
    html_content: str
    html_file_path: Optional[str] = None
    png_file_path: Optional[str] = None
    success: bool = True
    message: Optional[str] = None
