from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import uvicorn

from app.api.routes import chat, html
from app.core.config import settings
from app.core.logging import setup_logging

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

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
app.include_router(html.router, prefix="/api/html", tags=["HTML处理"])

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )

# 健康检查端点
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# 确保必要的目录存在
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

if __name__ == "__main__":
    import argparse
    
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
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=settings.DEBUG)
