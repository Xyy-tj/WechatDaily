#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 转图片服务测试脚本

提供了多种测试用例，展示如何使用 HTML 转图片服务。
"""

import os
import time
import webbrowser
from html_to_image import convert_html_string, convert_html_file, HtmlToImageConverter

# 测试 HTML 内容
TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>测试页面</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .chart-container { margin-top: 20px; height: 300px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <h1>测试模块界面</h1>

        <div class="chart-container">
            <canvas id="myChart"></canvas>
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>状态</th>
                    <th>日期</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>测试项目1</td>
                    <td>完成</td>
                    <td>2025-04-22</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>测试项目2</td>
                    <td>进行中</td>
                    <td>2025-04-23</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>测试项目3</td>
                    <td>未开始</td>
                    <td>2025-04-24</td>
                </tr>
            </tbody>
        </table>
    </div>

    <script>
        // 初始化图表
        const ctx = document.getElementById('myChart').getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['一月', '二月', '三月', '四月', '五月', '六月'],
                datasets: [{
                    label: '完成任务数',
                    data: [12, 19, 3, 5, 2, 3],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

def test_convert_html_string():
    """测试从 HTML 字符串生成图片"""
    print("测试 1: 从 HTML 字符串生成图片")
    
    # 使用便捷函数
    image_path = convert_html_string(
        TEST_HTML, 
        output_path="output/images/test_string.png",
        wait_time=8000  # 等待更长时间以确保图表渲染完成
    )
    
    if image_path:
        print(f"成功生成图片: {image_path}")
        try:
            webbrowser.open(image_path)
        except:
            print("无法自动打开图片，请手动查看。")
    else:
        print("图片生成失败")
        
    print("-" * 50)

def test_convert_html_file():
    """测试从 HTML 文件生成图片"""
    print("测试 2: 从 HTML 文件生成图片")
    
    # 创建临时 HTML 文件
    html_file_path = "output/html_files/test_file.html"
    os.makedirs(os.path.dirname(html_file_path), exist_ok=True)
    
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(TEST_HTML)
        
    # 使用便捷函数
    image_path = convert_html_file(
        html_file_path, 
        output_path="output/images/test_file.png",
        wait_time=8000
    )
    
    if image_path:
        print(f"成功生成图片: {image_path}")
        try:
            webbrowser.open(image_path)
        except:
            print("无法自动打开图片，请手动查看。")
    else:
        print("图片生成失败")
        
    print("-" * 50)

def test_converter_class():
    """测试使用 HtmlToImageConverter 类"""
    print("测试 3: 使用 HtmlToImageConverter 类")
    
    # 创建转换器实例
    converter = HtmlToImageConverter(
        output_dir="output",
        image_dir="output/images",
        html_dir="output/html_files"
    )
    
    # 从字符串生成图片
    success, image_path = converter.convert_html_string(
        TEST_HTML,
        image_name="test_class.png",
        viewport_width=1000,
        viewport_height=800,
        scale_factor=2.0,
        wait_time=8000
    )
    
    if success:
        print(f"成功生成图片: {image_path}")
        try:
            webbrowser.open(image_path)
        except:
            print("无法自动打开图片，请手动查看。")
    else:
        print("图片生成失败")
        
    print("-" * 50)

def test_advanced_options():
    """测试高级选项"""
    print("测试 4: 使用高级选项")
    
    # 创建转换器实例
    converter = HtmlToImageConverter()
    
    # 使用高级选项
    success, image_path = converter.convert_html_string(
        TEST_HTML,
        image_name="test_advanced.png",
        viewport_width=1600,  # 更宽的视口
        viewport_height=1200,  # 更高的视口
        scale_factor=2.0,      # 更高的缩放因子，提高清晰度
        wait_time=10000,       # 等待更长时间
        full_page=True         # 截取整个页面
    )
    
    if success:
        print(f"成功生成图片: {image_path}")
        try:
            webbrowser.open(image_path)
        except:
            print("无法自动打开图片，请手动查看。")
    else:
        print("图片生成失败")
        
    print("-" * 50)

def test_web_service_client():
    """测试 Web 服务客户端"""
    print("测试 5: Web 服务客户端")
    print("注意: 此测试需要先启动 Web 服务")
    print("请先运行: python html_to_image_service.py")
    
    try:
        import requests
        
        # 检查服务是否运行
        try:
            response = requests.get("http://localhost:5000/health")
            if response.status_code != 200:
                print("Web 服务未运行或无法访问")
                return
        except:
            print("Web 服务未运行或无法访问")
            return
            
        # 测试 JSON 请求
        print("测试 JSON 请求...")
        response = requests.post(
            "http://localhost:5000/convert",
            json={
                "html": TEST_HTML,
                "options": {
                    "viewport_width": 1200,
                    "viewport_height": 800,
                    "scale_factor": 1.5,
                    "wait_time": 8000
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"成功生成图片: {result.get('image_path')}")
                
                # 获取图片
                image_filename = os.path.basename(result.get('image_path'))
                image_url = f"http://localhost:5000/image/{image_filename}"
                
                try:
                    webbrowser.open(image_url)
                except:
                    print(f"无法自动打开图片，请手动访问: {image_url}")
            else:
                print(f"图片生成失败: {result.get('error')}")
        else:
            print(f"请求失败: {response.status_code} - {response.text}")
            
        # 测试直接下载
        print("\n测试直接下载...")
        response = requests.post(
            "http://localhost:5000/convert_and_download",
            json={
                "html": TEST_HTML,
                "options": {
                    "viewport_width": 1200,
                    "viewport_height": 800,
                    "scale_factor": 1.5,
                    "wait_time": 8000
                }
            }
        )
        
        if response.status_code == 200:
            # 保存下载的图片
            download_path = "output/images/downloaded.png"
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            
            with open(download_path, 'wb') as f:
                f.write(response.content)
                
            print(f"成功下载图片: {download_path}")
            
            try:
                webbrowser.open(download_path)
            except:
                print("无法自动打开图片，请手动查看。")
        else:
            print(f"下载失败: {response.status_code} - {response.text}")
            
    except ImportError:
        print("未安装 requests 库，无法测试 Web 服务客户端")
        print("请使用 'pip install requests' 安装")
    except Exception as e:
        print(f"测试 Web 服务客户端时出错: {str(e)}")
        
    print("-" * 50)

def main():
    """运行所有测试"""
    print("HTML 转图片服务测试")
    print("=" * 50)
    
    # 确保输出目录存在
    os.makedirs("output/images", exist_ok=True)
    os.makedirs("output/html_files", exist_ok=True)
    
    # 运行测试
    test_convert_html_string()
    time.sleep(1)  # 避免并发问题
    
    test_convert_html_file()
    time.sleep(1)
    
    test_converter_class()
    time.sleep(1)
    
    test_advanced_options()
    time.sleep(1)
    
    test_web_service_client()
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    main()
