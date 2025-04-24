#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML 转图片 Web 服务

提供 RESTful API 接口，将 HTML 内容转换为 PNG 图片。
支持通过 POST 请求提交 HTML 内容或上传 HTML 文件。
"""

import os
import json
import logging
import tempfile
from flask import Flask, request, jsonify, send_file, abort
from html_to_image import HtmlToImageConverter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('html_to_image_service')

# 创建 Flask 应用
app = Flask(__name__)

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

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'service': 'html-to-image',
        'version': '1.0.0'
    })

@app.route('/convert', methods=['POST'])
def convert_html():
    """
    将 HTML 内容转换为图片
    
    接受 JSON 格式的请求体，包含以下字段：
    - html: HTML 内容字符串
    - options: 可选的转换选项
    
    或者接受 multipart/form-data 格式的表单，包含以下字段：
    - html_file: HTML 文件
    - options: 可选的转换选项（JSON 字符串）
    
    返回 JSON 格式的响应，包含以下字段：
    - success: 是否成功
    - image_path: 生成的图片路径
    - error: 错误信息（如果失败）
    """
    try:
        # 解析请求参数
        options = {}
        
        # 检查是否是 JSON 请求
        if request.is_json:
            data = request.get_json()
            
            if 'html' not in data:
                return jsonify({
                    'success': False,
                    'error': '缺少 html 字段'
                }), 400
                
            html_content = data['html']
            
            if 'options' in data and isinstance(data['options'], dict):
                options = data['options']
                
            # 生成图片
            success, image_path = converter.convert_html_string(
                html_content=html_content, **options
            )
            
        # 检查是否是表单请求
        elif 'html_file' in request.files:
            html_file = request.files['html_file']
            
            # 检查文件是否为空
            if html_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'HTML 文件为空'
                }), 400
                
            # 解析选项
            if 'options' in request.form:
                try:
                    options = json.loads(request.form['options'])
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'options 参数不是有效的 JSON'
                    }), 400
            
            # 保存上传的文件到临时文件
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.html', dir=HTML_DIR, delete=False
            )
            temp_file_path = temp_file.name
            temp_file.close()
            
            html_file.save(temp_file_path)
            
            # 生成图片
            success, image_path = converter.convert_html_file(
                html_file_path=temp_file_path, **options
            )
            
            # 删除临时文件
            try:
                os.remove(temp_file_path)
            except:
                pass
                
        # 检查是否是表单中的 HTML 内容
        elif 'html' in request.form:
            html_content = request.form['html']
            
            # 解析选项
            if 'options' in request.form:
                try:
                    options = json.loads(request.form['options'])
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'options 参数不是有效的 JSON'
                    }), 400
            
            # 生成图片
            success, image_path = converter.convert_html_string(
                html_content=html_content, **options
            )
            
        else:
            return jsonify({
                'success': False,
                'error': '请求必须包含 html 字段或 html_file 文件'
            }), 400
            
        # 返回结果
        if success:
            return jsonify({
                'success': True,
                'image_path': image_path
            })
        else:
            return jsonify({
                'success': False,
                'error': '图片生成失败'
            }), 500
            
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/image/<path:filename>', methods=['GET'])
def get_image(filename):
    """
    获取生成的图片
    
    Args:
        filename: 图片文件名
    """
    try:
        image_path = os.path.join(IMAGE_DIR, filename)
        
        if not os.path.exists(image_path):
            abort(404)
            
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"获取图片时出错: {str(e)}")
        abort(500)

@app.route('/convert_and_download', methods=['POST'])
def convert_and_download():
    """
    将 HTML 内容转换为图片并直接下载
    
    与 /convert 接口类似，但直接返回图片文件而不是 JSON 响应
    """
    try:
        # 解析请求参数
        options = {}
        
        # 检查是否是 JSON 请求
        if request.is_json:
            data = request.get_json()
            
            if 'html' not in data:
                return jsonify({
                    'success': False,
                    'error': '缺少 html 字段'
                }), 400
                
            html_content = data['html']
            
            if 'options' in data and isinstance(data['options'], dict):
                options = data['options']
                
            # 生成图片
            success, image_path = converter.convert_html_string(
                html_content=html_content, **options
            )
            
        # 检查是否是表单请求
        elif 'html_file' in request.files:
            html_file = request.files['html_file']
            
            # 检查文件是否为空
            if html_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'HTML 文件为空'
                }), 400
                
            # 解析选项
            if 'options' in request.form:
                try:
                    options = json.loads(request.form['options'])
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'options 参数不是有效的 JSON'
                    }), 400
            
            # 保存上传的文件到临时文件
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.html', dir=HTML_DIR, delete=False
            )
            temp_file_path = temp_file.name
            temp_file.close()
            
            html_file.save(temp_file_path)
            
            # 生成图片
            success, image_path = converter.convert_html_file(
                html_file_path=temp_file_path, **options
            )
            
            # 删除临时文件
            try:
                os.remove(temp_file_path)
            except:
                pass
                
        # 检查是否是表单中的 HTML 内容
        elif 'html' in request.form:
            html_content = request.form['html']
            
            # 解析选项
            if 'options' in request.form:
                try:
                    options = json.loads(request.form['options'])
                except json.JSONDecodeError:
                    return jsonify({
                        'success': False,
                        'error': 'options 参数不是有效的 JSON'
                    }), 400
            
            # 生成图片
            success, image_path = converter.convert_html_string(
                html_content=html_content, **options
            )
            
        else:
            return jsonify({
                'success': False,
                'error': '请求必须包含 html 字段或 html_file 文件'
            }), 400
            
        # 返回结果
        if success:
            # 获取文件名
            filename = os.path.basename(image_path)
            
            # 直接返回图片文件
            return send_file(
                image_path, 
                mimetype='image/png',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({
                'success': False,
                'error': '图片生成失败'
            }), 500
            
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='HTML 转图片 Web 服务')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听主机')
    parser.add_argument('--port', type=int, default=5000, help='监听端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    logger.info(f"启动 HTML 转图片 Web 服务，监听 {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
