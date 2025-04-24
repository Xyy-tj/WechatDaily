import os
import re
import logging
import datetime
import requests
from typing import Optional, Tuple, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

def extract_html_from_response(response_text: str) -> Optional[str]:
    """
    从AI响应中提取HTML内容

    Args:
        response_text: AI的完整响应文本

    Returns:
        提取的HTML内容，如果没有找到则返回None
    """
    # 使用正则表达式查找HTML内容
    # 查找完整的HTML文档
    html_pattern = re.compile(r'<!DOCTYPE html>[\s\S]*?<\/html>', re.IGNORECASE)
    match = html_pattern.search(response_text)

    if match:
        return match.group(0)

    # 如果没有找到完整的HTML文档，尝试查找<html>标签
    html_pattern = re.compile(r'<html[\s\S]*?<\/html>', re.IGNORECASE)
    match = html_pattern.search(response_text)

    if match:
        return "<!DOCTYPE html>\n" + match.group(0)

    # 如果仍然没有找到，尝试查找<body>标签
    body_pattern = re.compile(r'<body[\s\S]*?<\/body>', re.IGNORECASE)
    match = body_pattern.search(response_text)

    if match:
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>群聊日报</title>
</head>
{match.group(0)}
</html>"""

    return None

def save_html_content(html_content: str, output_dir: str = "output") -> str:
    """
    保存HTML内容到文件

    Args:
        html_content: HTML内容
        output_dir: 输出目录

    Returns:
        保存的HTML文件路径
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 生成时间戳作为文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file_path = os.path.join(output_dir, f"report_{timestamp}.html")

    # 保存HTML文件
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"HTML已保存到: {html_file_path}")
    return html_file_path

def convert_html_to_image(html_content: Optional[str] = None,
                         html_file_path: Optional[str] = None,
                         png_file_path: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    调用HTML转图片服务将HTML内容或文件转换为PNG图像

    Args:
        html_content: HTML内容字符串，如果提供则会创建临时HTML文件
        html_file_path: HTML文件路径，如果html_content为None则必须提供
        png_file_path: 输出PNG文件路径，如果为None则自动生成

    Returns:
        (bool, str): 转换是否成功，以及PNG文件路径
    """
    # 参数验证
    if html_content is None and html_file_path is None:
        logger.error("必须提供html_content或html_file_path参数")
        return False, None

    try:
        # 准备请求数据
        request_data = {}
        if html_content is not None:
            request_data["html_content"] = html_content
        if html_file_path is not None:
            request_data["html_file_path"] = os.path.abspath(html_file_path)
        if png_file_path is not None:
            request_data["png_file_path"] = os.path.abspath(png_file_path)

        # 确定使用哪个API接口
        if html_file_path is not None:
            # 使用文件路径接口
            service_url = f"{settings.HTML_TO_IMAGE_SERVICE_URL}/convert/path"
            logger.info(f"调用HTML转图片服务(文件路径): {service_url}")
            logger.info(f"请求数据: {request_data}")
        else:
            # 使用HTML内容接口
            service_url = f"{settings.HTML_TO_IMAGE_SERVICE_URL}/convert"
            logger.info(f"调用HTML转图片服务(HTML内容): {service_url}")
            logger.info(f"请求数据: {request_data}")

        response = requests.post(service_url, json=request_data)

        # 检查响应
        if response.status_code == 200:
            result = response.json()
            logger.info(f"HTML转图片服务响应: {result}")

            if result.get("success"):
                # 注意：HTML转图片服务返回的字段是image_path，而不是png_file_path
                png_path = result.get("image_path")
                logger.info(f"HTML转图片成功: {png_path}")

                # 确保返回的路径是绝对路径
                if png_path and not os.path.isabs(png_path):
                    png_path = os.path.abspath(png_path)

                return True, png_path
            else:
                logger.error(f"HTML转图片失败: {result.get('message')}")
                return False, None
        else:
            logger.error(f"HTML转图片服务返回错误: {response.status_code}, {response.text}")
            return False, None

    except Exception as e:
        logger.error(f"调用HTML转图片服务时出错: {str(e)}")
        logger.error(f"异常详情: {e.__class__.__name__}: {str(e)}")
        import traceback
        logger.error(f"堆栈跟踪: {traceback.format_exc()}")
        return False, None
