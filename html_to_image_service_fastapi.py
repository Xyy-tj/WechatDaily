#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 转图片 Web 服务 - FastAPI版本

提供 RESTful API 接口，将 HTML 内容转换为 PNG 图片。
支持通过 POST 请求提交 HTML 内容或上传 HTML 文件。
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入HTML转图片功能
from html_to_image import HtmlToImageConverter, convert_html_string, convert_html_file

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('html_to_image_service')

# 创建 FastAPI 应用
app = FastAPI(
    title="HTML转图片服务",
    description="将HTML内容或文件转换为PNG图片的服务",
    version="1.0.0",
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

# 配置
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
IMAGE_DIR = os.environ.get('IMAGE_DIR', os.path.join(OUTPUT_DIR, 'images'))
HTML_DIR = os.environ.get('HTML_DIR', os.path.join(OUTPUT_DIR, 'html_files'))

# 确保目录存在
for directory in [OUTPUT_DIR, IMAGE_DIR, HTML_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 创建转换器实例
converter = HtmlToImageConverter(
    output_dir=OUTPUT_DIR,
    image_dir=IMAGE_DIR,
    html_dir=HTML_DIR
)

# 请求和响应模型
class HTMLContentRequest(BaseModel):
    """HTML内容请求模型"""
    html: str
    options: Optional[Dict[str, Any]] = {}

class HTMLFilePathRequest(BaseModel):
    """HTML文件路径请求模型"""
    html_file_path: str
    png_file_path: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}

class HTMLConversionResponse(BaseModel):
    """HTML转换响应模型"""
    success: bool
    image_path: Optional[str] = None
    error: Optional[str] = None

# 健康检查接口
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "html-to-image",
        "version": "1.0.0"
    }

# HTML内容转图片接口
@app.post("/convert", response_model=HTMLConversionResponse, tags=["转换"])
async def convert_html_content(request: HTMLContentRequest = Body(...)):
    """
    将HTML内容转换为图片

    Args:
        request: 包含HTML内容和选项的请求

    Returns:
        转换结果
    """
    try:
        # 生成图片
        success, image_path = converter.convert_html_string(
            html_content=request.html, **request.options
        )

        # 返回结果
        if success:
            return HTMLConversionResponse(
                success=True,
                image_path=image_path
            )
        else:
            return HTMLConversionResponse(
                success=False,
                error="图片生成失败"
            )
    except Exception as e:
        logger.error(f"处理HTML内容转换请求时出错: {str(e)}")
        return HTMLConversionResponse(
            success=False,
            error=str(e)
        )

# HTML文件路径转图片接口
@app.post("/convert/path", response_model=HTMLConversionResponse, tags=["转换"])
async def convert_html_file_path(request: HTMLFilePathRequest = Body(...)):
    """
    将指定路径的HTML文件转换为图片

    Args:
        request: 包含HTML文件路径和选项的请求

    Returns:
        转换结果
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(request.html_file_path):
            logger.error(f"HTML文件不存在: {request.html_file_path}")
            return HTMLConversionResponse(
                success=False,
                error=f"HTML文件不存在: {request.html_file_path}"
            )

        # 设置输出路径
        png_file_path = request.png_file_path
        if not png_file_path:
            # 从HTML文件路径生成PNG文件路径
            png_file_path = os.path.splitext(request.html_file_path)[0] + ".png"

        logger.info(f"开始转换HTML文件: {request.html_file_path} -> {png_file_path}")

        # 使用异步API生成图片
        success, image_path = await converter.convert_html_file_async(
            html_file_path=request.html_file_path,
            png_file_path=png_file_path,
            **request.options
        )

        # 返回结果
        if success:
            logger.info(f"HTML文件转换成功: {image_path}")
            return HTMLConversionResponse(
                success=True,
                image_path=image_path
            )
        else:
            logger.error(f"HTML文件转换失败")
            return HTMLConversionResponse(
                success=False,
                error="图片生成失败"
            )
    except Exception as e:
        logger.error(f"处理HTML文件路径转换请求时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return HTMLConversionResponse(
            success=False,
            error=str(e)
        )

# HTML文件上传转图片接口
@app.post("/convert/file", response_model=HTMLConversionResponse, tags=["转换"])
async def convert_html_file_upload(
    html_file: UploadFile = File(...),
    options: Optional[str] = Form("{}")
):
    """
    将上传的HTML文件转换为图片

    Args:
        html_file: 上传的HTML文件
        options: JSON格式的选项字符串

    Returns:
        转换结果
    """
    try:
        import json

        # 解析选项
        try:
            options_dict = json.loads(options)
        except json.JSONDecodeError:
            return HTMLConversionResponse(
                success=False,
                error="options参数不是有效的JSON"
            )

        # 保存上传的文件到临时文件
        with tempfile.NamedTemporaryFile(
            suffix='.html', dir=HTML_DIR, delete=False
        ) as temp_file:
            temp_file_path = temp_file.name

            # 写入上传的文件内容
            content = await html_file.read()
            temp_file.write(content)

        # 生成图片
        success, image_path = converter.convert_html_file(
            html_file_path=temp_file_path, **options_dict
        )

        # 删除临时文件
        try:
            os.remove(temp_file_path)
        except:
            pass

        # 返回结果
        if success:
            return HTMLConversionResponse(
                success=True,
                image_path=image_path
            )
        else:
            return HTMLConversionResponse(
                success=False,
                error="图片生成失败"
            )
    except Exception as e:
        logger.error(f"处理HTML文件转换请求时出错: {str(e)}")
        return HTMLConversionResponse(
            success=False,
            error=str(e)
        )

# 获取图片接口
@app.get("/image/{filename}", tags=["图片"])
async def get_image(filename: str):
    """
    获取生成的图片

    Args:
        filename: 图片文件名

    Returns:
        图片文件
    """
    try:
        image_path = os.path.join(IMAGE_DIR, filename)

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="图片不存在")

        return FileResponse(image_path, media_type="image/png")

    except Exception as e:
        logger.error(f"获取图片时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 直接下载转换后的图片
@app.post("/convert_and_download", tags=["转换"])
async def convert_and_download(request: HTMLContentRequest = Body(...)):
    """
    将HTML内容转换为图片并直接下载

    Args:
        request: 包含HTML内容和选项的请求

    Returns:
        图片文件
    """
    try:
        # 生成图片
        success, image_path = converter.convert_html_string(
            html_content=request.html, **request.options
        )

        # 返回结果
        if success:
            # 获取文件名
            filename = os.path.basename(image_path)

            # 直接返回图片文件
            return FileResponse(
                image_path,
                media_type="image/png",
                filename=filename
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "图片生成失败"}
            )
    except Exception as e:
        logger.error(f"处理HTML内容转换并下载请求时出错: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# 命令行入口
def main():
    """命令行入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description='HTML 转图片 Web 服务')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听主机')
    parser.add_argument('--port', type=int, default=8001, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

    logger.info(f"启动 HTML 转图片 Web 服务，监听 {args.host}:{args.port}")
    uvicorn.run("html_to_image_service_fastapi:app", host=args.host, port=args.port, reload=args.debug)

if __name__ == "__main__":
    main()
