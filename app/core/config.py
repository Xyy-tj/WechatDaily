import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """应用配置类"""
    # 应用设置
    APP_NAME: str = "微信群聊日报生成器"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API设置
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.environ.get("OPENAI_BASE_URL")
    
    # 默认模型
    DEFAULT_MODEL: str = "gemini-2.5-pro-exp-03-25"
    
    # 目录设置
    OUTPUT_DIR: str = "output"
    TEMPLATES_DIR: str = "templates"
    
    # HTML转图片服务设置
    HTML_TO_IMAGE_SERVICE_URL: str = "http://localhost:8001"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局设置对象
settings = Settings()
