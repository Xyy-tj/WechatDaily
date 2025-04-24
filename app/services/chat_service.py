import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
import traceback

from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    """聊天服务类，负责与OpenAI API交互"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化聊天服务
        
        Args:
            api_key: OpenAI API密钥，如果为None则使用环境变量
            base_url: API基础URL，如果为None则使用默认URL
        """
        # 使用提供的API密钥或环境变量
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("未提供API密钥，请设置OPENAI_API_KEY环境变量或在初始化时提供")
        
        # 如果提供了base_url，则使用它，否则使用默认的OpenAI API URL
        self.base_url = base_url or settings.OPENAI_BASE_URL
        
        # 初始化OpenAI客户端
        if self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = OpenAI(api_key=self.api_key)
            
        logger.info(f"聊天服务初始化完成，使用API基础URL: {self.base_url or 'https://api.openai.com/v1'}")
    
    def create_chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, 
                   temperature: float = 0.7, max_tokens: int = 100000, 
                   stream: bool = False) -> Any:
        """
        创建聊天完成
        
        Args:
            messages: 消息列表
            model: 模型名称，如果为None则使用默认模型
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数
            stream: 是否使用流式响应
            
        Returns:
            如果stream=False，返回完整响应文本
            如果stream=True，返回响应流对象
        """
        try:
            # 如果没有指定模型，根据base_url选择默认模型
            if model is None:
                if self.base_url and "rcouyi.com" in self.base_url:
                    model = "gemini-2.5-pro-exp-03-25"
                else:
                    model = settings.DEFAULT_MODEL
            
            logger.info(f"使用模型: {model}")
            
            # 创建聊天完成
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if not stream:
                # 检查响应格式是否符合预期
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                        return response.choices[0].message.content
                    else:
                        error_msg = f"响应格式异常: {response}"
                        logger.error(error_msg)
                        return error_msg
                else:
                    error_msg = f"响应没有choices字段: {response}"
                    logger.error(error_msg)
                    return error_msg
            else:
                return response  # 返回流对象
        except Exception as e:
            error_msg = f"创建聊天时出错: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            if not stream:
                return error_msg
            else:
                # 在流式模式下，我们需要抛出异常，让调用者处理
                raise Exception(error_msg)
