# HTML 转图片服务

这个项目提供了一个将 HTML 内容或 HTML 文件转换为 PNG 图片的服务。它使用 Playwright 作为渲染引擎，支持高质量的图片生成。

## 功能特点

- 支持从 HTML 字符串生成图片
- 支持从 HTML 文件生成图片
- 支持自定义视口大小、缩放因子等参数
- 提供命令行工具、Python API 和 Web 服务接口
- 支持等待图表和图片加载完成后再截图
- 高质量图片输出

## 安装

### 依赖项

- Python 3.8+
- Playwright

### 安装步骤

1. 安装 Python 依赖项：

```bash
pip install -r requirements.txt
```

2. 安装 Playwright 浏览器：

```bash
playwright install
```

## 使用方法

### 作为 Python 模块使用

```python
from html_to_image import convert_html_string, convert_html_file

# 从 HTML 字符串生成图片
html_content = "<html><body><h1>Hello World</h1></body></html>"
image_path = convert_html_string(html_content, output_path="output.png")

# 从 HTML 文件生成图片
image_path = convert_html_file("input.html", output_path="output.png")
```

### 使用高级选项

```python
from html_to_image import HtmlToImageConverter

# 创建转换器实例
converter = HtmlToImageConverter(
    output_dir="output",
    image_dir="images",
    html_dir="html_files"
)

# 从 HTML 字符串生成图片
success, image_path = converter.convert_html_string(
    html_content="<html><body><h1>Hello World</h1></body></html>",
    image_name="output.png",
    viewport_width=1200,
    viewport_height=800,
    scale_factor=2.0,
    wait_time=5000,
    full_page=True
)
```

### 命令行使用

```bash
# 从 HTML 文件生成图片
python html_to_image.py --html input.html --output output.png

# 从 HTML 字符串生成图片
python html_to_image.py --string "<html><body><h1>Hello World</h1></body></html>" --output output.png

# 使用高级选项
python html_to_image.py --html input.html --output output.png --width 1600 --height 1200 --scale 2.0 --wait 10000
```

### 启动 Web 服务

```bash
python html_to_image_service.py --host 0.0.0.0 --port 5000
```

### Web 服务 API

#### 健康检查

```
GET /health
```

响应：

```json
{
  "status": "ok",
  "service": "html-to-image",
  "version": "1.0.0"
}
```

#### 转换 HTML 为图片

```
POST /convert
```

请求体 (JSON)：

```json
{
  "html": "<html><body><h1>Hello World</h1></body></html>",
  "options": {
    "viewport_width": 1200,
    "viewport_height": 800,
    "scale_factor": 1.5,
    "wait_time": 5000,
    "full_page": true
  }
}
```

响应：

```json
{
  "success": true,
  "image_path": "output/images/image_20230501_123456.png"
}
```

#### 转换并下载图片

```
POST /convert_and_download
```

请求体与 `/convert` 相同，但直接返回图片文件而不是 JSON 响应。

#### 获取图片

```
GET /image/{filename}
```

直接返回图片文件。

## 测试

运行测试脚本：

```bash
python test_html_to_image.py
```

## 配置选项

### 转换选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| viewport_width | 视口宽度（像素） | 1200 |
| viewport_height | 视口高度（像素） | 800 |
| scale_factor | 设备缩放因子，影响图片清晰度 | 1.5 |
| timeout | 页面加载超时时间（毫秒） | 60000 |
| wait_time | 等待页面渲染的时间（毫秒） | 5000 |
| full_page | 是否截取整个页面 | true |

### 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| OUTPUT_DIR | 输出根目录 | output |
| IMAGE_DIR | 图片保存目录 | output/images |
| HTML_DIR | HTML 文件保存目录 | output/html_files |

## 注意事项

- 确保 HTML 内容中的外部资源（如 CSS、JavaScript、图片等）可以正常加载
- 对于包含图表或动态内容的 HTML，可能需要增加 wait_time 参数
- 如果遇到权限问题，请确保输出目录有写入权限

## 许可证

MIT
