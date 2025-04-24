#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 转图片服务

这个模块提供了将 HTML 内容或 HTML 文件转换为 PNG 图片的功能。
使用 Playwright 作为渲染引擎，支持高质量的图片生成。
"""

import os
import time
import logging
import traceback
from typing import Optional, Tuple, Dict, Any, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('html_to_image')

class HtmlToImageConverter:
    """HTML 转图片转换器类"""

    def __init__(self, output_dir: str = "output",
                 image_dir: str = "images",
                 html_dir: str = "html_files"):
        """
        初始化 HTML 转图片转换器

        Args:
            output_dir: 输出根目录
            image_dir: 图片保存目录（相对于 output_dir 或绝对路径）
            html_dir: HTML 文件保存目录（相对于 output_dir 或绝对路径）
        """
        self.output_dir = output_dir

        # 处理相对路径和绝对路径
        if os.path.isabs(image_dir):
            self.image_dir = image_dir
        else:
            self.image_dir = os.path.join(output_dir, image_dir)

        if os.path.isabs(html_dir):
            self.html_dir = html_dir
        else:
            self.html_dir = os.path.join(output_dir, html_dir)

        # 确保目录存在
        for directory in [self.output_dir, self.image_dir, self.html_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        logger.info(f"初始化 HTML 转图片服务，输出目录: {self.output_dir}")
        logger.info(f"图片保存目录: {self.image_dir}")
        logger.info(f"HTML 文件保存目录: {self.html_dir}")

    def convert_html_string(self, html_content: str,
                           image_name: Optional[str] = None,
                           delete_html: bool = True,
                           **kwargs) -> Tuple[bool, Optional[str]]:
        """
        将 HTML 字符串转换为图片

        Args:
            html_content: HTML 内容字符串
            image_name: 输出图片文件名（不含路径），如果为 None 则自动生成
            delete_html: 转换完成后是否删除临时 HTML 文件
            **kwargs: 传递给 _convert_html_to_image 的其他参数

        Returns:
            (成功标志, 图片路径) 元组
        """
        # 生成临时 HTML 文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        temp_html_name = f'temp_{timestamp}.html'
        temp_html_path = os.path.join(self.html_dir, temp_html_name)

        # 如果未指定图片名称，则自动生成
        if image_name is None:
            image_name = f'image_{timestamp}.png'
        elif not image_name.lower().endswith('.png'):
            image_name += '.png'

        img_path = os.path.join(self.image_dir, image_name)

        # 保存 HTML 内容到临时文件
        try:
            with open(temp_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"已保存 HTML 内容到临时文件: {temp_html_path}")
        except Exception as e:
            logger.error(f"保存 HTML 内容到临时文件时出错: {str(e)}")
            return False, None

        # 转换 HTML 文件为图片
        success, image_path = self._convert_html_to_image(
            temp_html_path, img_path, **kwargs
        )

        # 如果需要删除临时 HTML 文件
        if delete_html and os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
                logger.info(f"已删除临时 HTML 文件: {temp_html_path}")
            except Exception as e:
                logger.warning(f"删除临时 HTML 文件时出错: {str(e)}")

        return success, image_path

    def convert_html_file(self, html_file_path: str,
                         png_file_path: Optional[str] = None,
                         image_name: Optional[str] = None,
                         **kwargs) -> Tuple[bool, Optional[str]]:
        """
        将 HTML 文件转换为图片（同步版本，用于兼容性）

        Args:
            html_file_path: HTML 文件路径
            png_file_path: 完整的输出图片路径，优先级高于image_name
            image_name: 输出图片文件名（不含路径），如果为 None 则自动生成
            **kwargs: 传递给 _convert_html_to_image 的其他参数

        Returns:
            (成功标志, 图片路径) 元组
        """
        if not os.path.exists(html_file_path):
            logger.error(f"HTML 文件不存在: {html_file_path}")
            return False, None

        # 确定输出图片路径
        if png_file_path:
            # 使用指定的完整路径
            img_path = png_file_path
            # 确保输出目录存在
            output_dir = os.path.dirname(img_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            logger.info(f"使用指定的PNG文件路径: {img_path}")
        else:
            # 如果未指定图片名称，则从 HTML 文件名生成
            if image_name is None:
                base_name = os.path.basename(html_file_path)
                name_without_ext = os.path.splitext(base_name)[0]
                image_name = f'{name_without_ext}.png'
            elif not image_name.lower().endswith('.png'):
                image_name += '.png'

            img_path = os.path.join(self.image_dir, image_name)
            logger.info(f"生成的PNG文件路径: {img_path}")

        # 转换 HTML 文件为图片
        return self._convert_html_to_image(html_file_path, img_path, **kwargs)

    async def convert_html_file_async(self, html_file_path: str,
                                    png_file_path: Optional[str] = None,
                                    image_name: Optional[str] = None,
                                    **kwargs) -> Tuple[bool, Optional[str]]:
        """
        将 HTML 文件转换为图片（异步版本）

        Args:
            html_file_path: HTML 文件路径
            png_file_path: 完整的输出图片路径，优先级高于image_name
            image_name: 输出图片文件名（不含路径），如果为 None 则自动生成
            **kwargs: 传递给 _convert_html_to_image_async 的其他参数

        Returns:
            (成功标志, 图片路径) 元组
        """
        if not os.path.exists(html_file_path):
            logger.error(f"HTML 文件不存在: {html_file_path}")
            return False, None

        # 确定输出图片路径
        if png_file_path:
            # 使用指定的完整路径
            img_path = png_file_path
            # 确保输出目录存在
            output_dir = os.path.dirname(img_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            logger.info(f"使用指定的PNG文件路径: {img_path}")
        else:
            # 如果未指定图片名称，则从 HTML 文件名生成
            if image_name is None:
                base_name = os.path.basename(html_file_path)
                name_without_ext = os.path.splitext(base_name)[0]
                image_name = f'{name_without_ext}.png'
            elif not image_name.lower().endswith('.png'):
                image_name += '.png'

            img_path = os.path.join(self.image_dir, image_name)
            logger.info(f"生成的PNG文件路径: {img_path}")

        # 转换 HTML 文件为图片
        return await self._convert_html_to_image_async(html_file_path, img_path, **kwargs)

    async def _convert_html_to_image_async(self, html_file_path: str,
                                   img_path: str,
                                   viewport_width: int = 1200,
                                   viewport_height: int = 800,
                                   scale_factor: float = 1.5,
                                   timeout: int = 60000,
                                   wait_time: int = 5000,
                                   full_page: bool = True) -> Tuple[bool, Optional[str]]:
        """
        使用 Playwright 异步API将 HTML 文件转换为图片的核心方法

        Args:
            html_file_path: HTML 文件路径
            img_path: 输出图片路径
            viewport_width: 视口宽度
            viewport_height: 视口高度
            scale_factor: 设备缩放因子，影响图片清晰度
            timeout: 页面加载超时时间（毫秒）
            wait_time: 等待页面渲染的时间（毫秒）
            full_page: 是否截取整个页面

        Returns:
            (成功标志, 图片路径) 元组
        """
        try:
            # 动态导入 playwright，避免强制依赖
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                logger.error("未安装 playwright 库，请使用 'pip install playwright' 安装")
                logger.error("安装后，还需要运行 'playwright install' 安装浏览器")
                return False, None

            logger.info(f"开始将 HTML 文件 {html_file_path} 转换为图片")

            # 使用绝对路径
            abs_html_path = os.path.abspath(html_file_path)
            abs_img_path = os.path.abspath(img_path)

            async with async_playwright() as p:
                # 使用 chromium 启动无头浏览器，设置更高的截图质量
                browser = await p.chromium.launch(
                    args=['--disable-web-security', '--allow-file-access-from-files']
                )

                # 创建新页面，设置视口尺寸
                page = await browser.new_page(
                    viewport={"width": viewport_width, "height": viewport_height},
                    device_scale_factor=scale_factor  # 提高 DPI 使图片更清晰
                )

                # 导航到 HTML 文件，使用 file:// 协议
                try:
                    await page.goto(f"file://{abs_html_path}",
                             timeout=timeout,
                             wait_until="domcontentloaded")

                    # 等待页面加载和网络活动完成
                    await page.wait_for_load_state("networkidle", timeout=timeout)
                except Exception as e:
                    logger.warning(f"HTML 加载超时或出错，尝试继续处理: {e}")

                # 等待页面渲染完成
                await page.wait_for_timeout(wait_time)

                # 等待图表元素(如果存在)
                with open(abs_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                if "<canvas" in html_content:
                    try:
                        await page.wait_for_selector("canvas", timeout=5000)
                    except:
                        logger.warning("未找到 Canvas 元素或等待超时")

                # 注入脚本以确认所有图像已加载
                await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        // 检查所有图片是否加载完成
                        const allImagesLoaded = Array.from(document.images).every(img => img.complete);
                        if (allImagesLoaded) {
                            resolve();
                        } else {
                            // 如果有未加载完的图片，等待 'load' 事件
                            window.addEventListener('load', resolve);
                        }
                    });
                }
                """)

                # 截取全页面截图，确保高质量
                await page.screenshot(
                    path=abs_img_path,
                    full_page=full_page,
                    omit_background=False  # 保留背景以确保完整视图
                )

                await browser.close()

            # 检查图片是否生成成功
            if os.path.exists(abs_img_path):
                logger.info(f"成功生成图片: {abs_img_path}")
                return True, abs_img_path
            else:
                logger.error(f"图片生成失败，未找到文件: {abs_img_path}")
                return False, None

        except Exception as e:
            logger.error(f"HTML 转图片时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return False, None

    def _convert_html_to_image(self, html_file_path: str,
                              img_path: str,
                              viewport_width: int = 1200,
                              viewport_height: int = 800,
                              scale_factor: float = 1.5,
                              timeout: int = 60000,
                              wait_time: int = 5000,
                              full_page: bool = True) -> Tuple[bool, Optional[str]]:
        """
        使用 Playwright 将 HTML 文件转换为图片的核心方法
        这是一个兼容性方法，用于支持同步调用

        Args:
            html_file_path: HTML 文件路径
            img_path: 输出图片路径
            viewport_width: 视口宽度
            viewport_height: 视口高度
            scale_factor: 设备缩放因子，影响图片清晰度
            timeout: 页面加载超时时间（毫秒）
            wait_time: 等待页面渲染的时间（毫秒）
            full_page: 是否截取整个页面

        Returns:
            (成功标志, 图片路径) 元组
        """
        try:
            # 动态导入 playwright，避免强制依赖
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                logger.error("未安装 playwright 库，请使用 'pip install playwright' 安装")
                logger.error("安装后，还需要运行 'playwright install' 安装浏览器")
                return False, None

            logger.info(f"开始将 HTML 文件 {html_file_path} 转换为图片")

            # 使用绝对路径
            abs_html_path = os.path.abspath(html_file_path)
            abs_img_path = os.path.abspath(img_path)

            with sync_playwright() as p:
                # 使用 chromium 启动无头浏览器，设置更高的截图质量
                browser = p.chromium.launch(
                    args=['--disable-web-security', '--allow-file-access-from-files']
                )

                # 创建新页面，设置视口尺寸
                page = browser.new_page(
                    viewport={"width": viewport_width, "height": viewport_height},
                    device_scale_factor=scale_factor  # 提高 DPI 使图片更清晰
                )

                # 导航到 HTML 文件，使用 file:// 协议
                try:
                    page.goto(f"file://{abs_html_path}",
                             timeout=timeout,
                             wait_until="domcontentloaded")

                    # 等待页面加载和网络活动完成
                    page.wait_for_load_state("networkidle", timeout=timeout)
                except Exception as e:
                    logger.warning(f"HTML 加载超时或出错，尝试继续处理: {e}")

                # 等待页面渲染完成
                page.wait_for_timeout(wait_time)

                # 等待图表元素(如果存在)
                with open(abs_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                if "<canvas" in html_content:
                    try:
                        page.wait_for_selector("canvas", timeout=5000)
                    except:
                        logger.warning("未找到 Canvas 元素或等待超时")

                # 注入脚本以确认所有图像已加载
                page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        // 检查所有图片是否加载完成
                        const allImagesLoaded = Array.from(document.images).every(img => img.complete);
                        if (allImagesLoaded) {
                            resolve();
                        } else {
                            // 如果有未加载完的图片，等待 'load' 事件
                            window.addEventListener('load', resolve);
                        }
                    });
                }
                """)

                # 截取全页面截图，确保高质量
                page.screenshot(
                    path=abs_img_path,
                    full_page=full_page,
                    omit_background=False  # 保留背景以确保完整视图
                )

                browser.close()

            # 检查图片是否生成成功
            if os.path.exists(abs_img_path):
                logger.info(f"成功生成图片: {abs_img_path}")
                return True, abs_img_path
            else:
                logger.error(f"图片生成失败，未找到文件: {abs_img_path}")
                return False, None

        except Exception as e:
            logger.error(f"HTML 转图片时出错: {str(e)}")
            logger.error(traceback.format_exc())
            return False, None

def convert_html_string(html_content: str,
                       output_path: Optional[str] = None,
                       **kwargs) -> Optional[str]:
    """
    将 HTML 字符串转换为图片的便捷函数

    Args:
        html_content: HTML 内容字符串
        output_path: 输出图片路径，如果为 None 则自动生成
        **kwargs: 其他参数传递给 HtmlToImageConverter

    Returns:
        生成的图片路径，失败则返回 None
    """
    # 提取输出目录和文件名
    if output_path:
        output_dir = os.path.dirname(output_path)
        if not output_dir:
            output_dir = "output"
        image_name = os.path.basename(output_path)
    else:
        output_dir = "output"
        image_name = None

    # 创建转换器并执行转换
    converter = HtmlToImageConverter(output_dir=output_dir)
    success, image_path = converter.convert_html_string(
        html_content, image_name=image_name, **kwargs
    )

    return image_path if success else None

def convert_html_file(html_file_path: str,
                     output_path: Optional[str] = None,
                     png_file_path: Optional[str] = None,
                     **kwargs) -> Optional[str]:
    """
    将 HTML 文件转换为图片的便捷函数

    Args:
        html_file_path: HTML 文件路径
        output_path: 输出图片路径，如果为 None 则自动生成
        png_file_path: 完整的输出图片路径，优先级高于output_path
        **kwargs: 其他参数传递给 HtmlToImageConverter

    Returns:
        生成的图片路径，失败则返回 None
    """
    # 如果提供了png_file_path，直接使用它
    if png_file_path:
        # 提取输出目录
        output_dir = os.path.dirname(png_file_path)
        if not output_dir:
            output_dir = "output"

        # 创建转换器并执行转换
        converter = HtmlToImageConverter(output_dir=output_dir)
        success, image_path = converter.convert_html_file(
            html_file_path, png_file_path=png_file_path, **kwargs
        )

        return image_path if success else None

    # 否则，使用output_path
    # 提取输出目录和文件名
    if output_path:
        output_dir = os.path.dirname(output_path)
        if not output_dir:
            output_dir = "output"
        image_name = os.path.basename(output_path)
    else:
        output_dir = "output"
        image_name = None

    # 创建转换器并执行转换
    converter = HtmlToImageConverter(output_dir=output_dir)
    success, image_path = converter.convert_html_file(
        html_file_path, image_name=image_name, **kwargs
    )

    return image_path if success else None

def main():
    """命令行入口函数"""
    import argparse

    parser = argparse.ArgumentParser(description='HTML 转图片工具')
    parser.add_argument('--html', type=str, help='HTML 文件路径')
    parser.add_argument('--string', type=str, help='HTML 字符串内容')
    parser.add_argument('--output', type=str, help='输出图片路径')
    parser.add_argument('--width', type=int, default=1200, help='视口宽度')
    parser.add_argument('--height', type=int, default=800, help='视口高度')
    parser.add_argument('--scale', type=float, default=1.5, help='设备缩放因子')
    parser.add_argument('--wait', type=int, default=5000, help='等待渲染时间(毫秒)')
    parser.add_argument('--timeout', type=int, default=60000, help='页面加载超时时间(毫秒)')
    parser.add_argument('--no-full-page', action='store_false', dest='full_page',
                       help='不截取整个页面，只截取视口区域')

    args = parser.parse_args()

    # 检查参数
    if not args.html and not args.string:
        parser.error("必须提供 --html 或 --string 参数")

    if args.html and args.string:
        parser.error("--html 和 --string 参数不能同时使用")

    # 准备参数
    kwargs = {
        'viewport_width': args.width,
        'viewport_height': args.height,
        'scale_factor': args.scale,
        'wait_time': args.wait,
        'timeout': args.timeout,
        'full_page': args.full_page
    }

    # 执行转换
    if args.html:
        image_path = convert_html_file(args.html, args.output, **kwargs)
    else:
        image_path = convert_html_string(args.string, args.output, **kwargs)

    if image_path:
        print(f"成功生成图片: {image_path}")
        return 0
    else:
        print("图片生成失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
