import logging
import sys
from typing import List, Dict, Any

def setup_logging(debug: bool = False) -> None:
    """
    设置日志配置
    
    Args:
        debug: 是否启用调试模式
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # 如果不是调试模式，降低一些库的日志级别
    if not debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        
    logging.info(f"日志系统已初始化，级别: {'DEBUG' if debug else 'INFO'}")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)
