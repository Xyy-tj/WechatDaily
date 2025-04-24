import openai
from openai import OpenAI
import dotenv
import os
import glob
import re
import subprocess
import datetime
import time
import webbrowser
import sys
import json
import traceback
import importlib.util

# 全局变量
DEBUG_MODE = False  # 调试模式，可通过命令行参数--debug启用
ARGS = None  # 命令行参数

class ChatBot:
    def __init__(self, api_key, base_url=None):
        # 如果提供了base_url，则使用它，否则使用默认的OpenAI API URL
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

        # 保存base_url用于日志
        self.base_url = base_url if base_url else "https://api.openai.com/v1"
        print(f"使用API基础URL: {self.base_url}")

    def create_chat(self, messages, model=None, stream=False):
        """
        创建聊天完成

        Args:
            messages: 消息列表
            model: 模型名称，如果为None则使用默认模型
            stream: 是否使用流式响应

        Returns:
            如果stream=False，返回完整响应文本
            如果stream=True，返回响应流对象
        """
        try:
            # 如果没有指定模型，根据base_url选择默认模型
            if model is None:
                if "rcouyi.com" in self.base_url:
                    model = "gemini-2.5-pro-exp-03-25"
                else:
                    model = "gemini-2.5-pro-exp-03-25"  # 默认使用OpenAI的gemini-2.5-pro-exp-03-25模型

            print(f"使用模型: {model}")

            # 创建聊天完成
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=100000,
                stream=stream
            )

            if not stream:
                # 检查响应格式是否符合预期
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                        return response.choices[0].message.content
                    else:
                        return f"响应格式异常: {response}"
                else:
                    return f"响应没有choices字段: {response}"
            else:
                return response  # 返回流对象
        except Exception as e:
            error_msg = f"创建聊天时出错: {str(e)}"
            if not stream:
                return error_msg
            else:
                # 在流式模式下，我们需要抛出异常，让调用者处理
                raise Exception(error_msg)

def debug_object(obj, prefix=""):
    """
    调试函数，打印对象的属性和方法

    Args:
        obj: 要调试的对象
        prefix: 打印时的前缀
    """
    try:
        print(f"{prefix}类型: {type(obj)}")

        # 尝试转换为字典
        if hasattr(obj, "__dict__"):
            print(f"{prefix}属性: {json.dumps(obj.__dict__, default=str, ensure_ascii=False, indent=2)}")
        elif hasattr(obj, "model_dump"):
            # Pydantic模型
            print(f"{prefix}属性: {json.dumps(obj.model_dump(), default=str, ensure_ascii=False, indent=2)}")
        else:
            # 尝试获取所有属性
            attrs = dir(obj)
            print(f"{prefix}属性列表: {attrs}")

            # 打印一些常见属性
            for attr in ["choices", "delta", "content", "message"]:
                if hasattr(obj, attr):
                    value = getattr(obj, attr)
                    print(f"{prefix}属性 {attr}: {value}")
    except Exception as e:
        print(f"{prefix}调试对象时出错: {str(e)}")
        traceback.print_exc()

def extract_html_from_response(response_text):
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

def find_browser_path():
    """
    尝试查找常见浏览器的路径

    Returns:
        找到的浏览器路径，如果没有找到则返回None
    """
    # 常见的浏览器路径
    browser_paths = {
        'chrome': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ],
        'edge': [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        ],
        'firefox': [
            r'C:\Program Files\Mozilla Firefox\firefox.exe',
            r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
        ]
    }

    # 检查每个浏览器路径
    for browser, paths in browser_paths.items():
        for path in paths:
            if os.path.exists(path):
                return browser, path

    return None, None

def html_to_png_with_playwright(html_file_path, png_file_path):
    """
    使用Playwright将HTML文件转换为PNG图像

    Args:
        html_file_path: HTML文件路径
        png_file_path: 输出PNG文件路径

    Returns:
        转换是否成功
    """
    # 检查Playwright是否已安装
    if not importlib.util.find_spec("playwright"):
        print("Playwright未安装，无法使用此方法")
        return False

    try:
        # 动态导入playwright以避免未安装时的导入错误
        from playwright.sync_api import sync_playwright

        print("使用Playwright转换HTML到PNG...")
        with sync_playwright() as p:
            # 启动浏览器（优先使用Chromium，因为它是跨平台的）
            browser = p.chromium.launch()
            page = browser.new_page()

            # 使用file://协议加载本地HTML文件
            page.goto(f"file://{os.path.abspath(html_file_path)}")

            # 等待页面加载完成
            page.wait_for_load_state("networkidle")

            # 截图并保存
            page.screenshot(path=png_file_path, full_page=True)

            # 关闭浏览器
            browser.close()

            if os.path.exists(png_file_path):
                print(f"使用Playwright成功将HTML转换为PNG: {png_file_path}")
                return True
            else:
                print("Playwright执行成功但未生成PNG文件")
                return False
    except Exception as e:
        print(f"使用Playwright转换失败: {str(e)}")
        traceback.print_exc()
        return False

def convert_html_to_png(html_file_path, png_file_path):
    """
    将HTML文件转换为PNG图像

    Args:
        html_file_path: HTML文件路径
        png_file_path: 输出PNG文件路径

    Returns:
        转换是否成功
    """
    try:
        # 首先尝试使用Playwright（如果已安装）
        if html_to_png_with_playwright(html_file_path, png_file_path):
            return True

        # 尝试查找浏览器路径
        browser_name, browser_path = find_browser_path()
        print(f"找到浏览器: {browser_name}, 路径: {browser_path}")

        # 尝试使用wkhtmltoimage（如果已安装）
        try:
            print("尝试使用wkhtmltoimage...")
            subprocess.run(
                ["wkhtmltoimage", "--quality", "100", html_file_path, png_file_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if os.path.exists(png_file_path):
                print(f"使用wkhtmltoimage成功将HTML转换为PNG: {png_file_path}")
                return True
            else:
                print("wkhtmltoimage执行成功但未生成PNG文件")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"wkhtmltoimage不可用: {str(e)}")

        # 如果wkhtmltoimage不可用，尝试使用Chrome/Edge的无头模式
        if browser_name == 'chrome' and browser_path:
            try:
                print("尝试使用Chrome...")
                # 使用找到的Chrome路径
                chrome_cmd = [
                    browser_path, "--headless", "--disable-gpu",
                    f"--screenshot={png_file_path}",
                    f"file://{os.path.abspath(html_file_path)}"
                ]
                subprocess.run(chrome_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists(png_file_path):
                    print(f"使用Chrome成功将HTML转换为PNG: {png_file_path}")
                    return True
                else:
                    print("Chrome执行成功但未生成PNG文件")
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"使用Chrome转换失败: {str(e)}")
        elif browser_name == 'edge' and browser_path:
            try:
                print("尝试使用Edge...")
                # 使用找到的Edge路径 - 修改命令行参数以适应Edge
                edge_cmd = [
                    browser_path, "--headless", "--disable-gpu",
                    "--screenshot", png_file_path,  # Edge可能需要不同的参数格式
                    f"file://{os.path.abspath(html_file_path)}"
                ]
                print(f"Edge命令: {' '.join(edge_cmd)}")
                result = subprocess.run(edge_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(f"Edge输出: {result.stdout.decode('utf-8', errors='ignore')}")
                print(f"Edge错误: {result.stderr.decode('utf-8', errors='ignore')}")

                if os.path.exists(png_file_path):
                    print(f"使用Edge成功将HTML转换为PNG: {png_file_path}")
                    return True
                else:
                    print("Edge执行成功但未生成PNG文件")

                # 尝试另一种Edge参数格式
                print("尝试使用Edge的另一种参数格式...")
                edge_cmd2 = [
                    browser_path, "--headless", "--disable-gpu",
                    "--screenshot=" + png_file_path,
                    f"file://{os.path.abspath(html_file_path)}"
                ]
                print(f"Edge命令2: {' '.join(edge_cmd2)}")
                result = subprocess.run(edge_cmd2, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if os.path.exists(png_file_path):
                    print(f"使用Edge成功将HTML转换为PNG: {png_file_path}")
                    return True
                else:
                    print("Edge第二种参数格式执行成功但未生成PNG文件")
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"使用Edge转换失败: {str(e)}")

        # 如果没有找到浏览器或使用找到的浏览器失败，尝试使用命令行方式
        try:
            print("尝试使用Chrome命令行...")
            # 尝试使用Chrome命令行
            chrome_cmd = [
                "chrome", "--headless", "--disable-gpu",
                f"--screenshot={png_file_path}",
                f"file://{os.path.abspath(html_file_path)}"
            ]
            subprocess.run(chrome_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(png_file_path):
                print(f"使用Chrome命令行成功将HTML转换为PNG: {png_file_path}")
                return True
            else:
                print("Chrome命令行执行成功但未生成PNG文件")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"使用Chrome命令行失败: {str(e)}")
            try:
                print("尝试使用Edge命令行...")
                # 尝试使用Microsoft Edge命令行
                edge_cmd = [
                    "msedge", "--headless", "--disable-gpu",
                    f"--screenshot={png_file_path}",
                    f"file://{os.path.abspath(html_file_path)}"
                ]
                subprocess.run(edge_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.exists(png_file_path):
                    print(f"使用Edge命令行成功将HTML转换为PNG: {png_file_path}")
                    return True
                else:
                    print("Edge命令行执行成功但未生成PNG文件")
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"使用Edge命令行失败: {str(e)}")

        # 如果所有自动方法都失败，尝试使用webbrowser模块打开HTML文件
        print("所有自动转换方法都失败，尝试使用默认浏览器打开HTML文件...")
        print(f"HTML文件已保存到: {html_file_path}")
        print("请手动截图保存为PNG图像")

        # 使用绝对路径构建文件URL
        file_url = f"file://{os.path.abspath(html_file_path)}"

        # 尝试打开浏览器
        try:
            webbrowser.open(file_url)
            print(f"已在浏览器中打开HTML文件，请手动截图")
            return False
        except Exception as e:
            print(f"无法打开浏览器: {str(e)}")
            print("无法将HTML转换为PNG。请安装wkhtmltoimage、Playwright或确保Chrome/Edge浏览器可用。")
            return False
    except Exception as e:
        print(f"转换HTML到PNG时出错: {str(e)}")
        traceback.print_exc()
        return False

def html_to_png(html_content=None, html_file_path=None, png_file_path=None):
    """
    将HTML内容或HTML文件转换为PNG图像

    Args:
        html_content: HTML内容字符串，如果提供则会创建临时HTML文件
        html_file_path: HTML文件路径，如果html_content为None则必须提供
        png_file_path: 输出PNG文件路径，如果为None则自动生成

    Returns:
        (bool, str): 转换是否成功，以及PNG文件路径
    """
    # 参数验证
    if html_content is None and html_file_path is None:
        raise ValueError("必须提供html_content或html_file_path参数")

    # 如果提供了HTML内容，创建临时HTML文件
    temp_file = None
    if html_content is not None:
        # 生成时间戳作为文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 确保输出目录存在
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 创建临时HTML文件
        temp_file = os.path.join(output_dir, f"temp_{timestamp}.html")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        html_file_path = temp_file

    # 如果没有提供PNG文件路径，自动生成
    if png_file_path is None:
        # 从HTML文件路径生成PNG文件路径
        png_file_path = os.path.splitext(html_file_path)[0] + ".png"

    # 调用转换函数
    success = convert_html_to_png(html_file_path, png_file_path)

    # 如果创建了临时文件并且转换成功，删除临时文件
    if temp_file is not None and success and os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"删除临时HTML文件时出错: {str(e)}")

    return success, png_file_path

def print_usage():
    """
    打印使用说明
    """
    print("""
微信群聊日报生成器 - 使用说明
-----------------------------
该工具可以根据微信群聊天记录生成HTML格式的日报，并可选择性地将其转换为PNG图像。

命令行参数:
  --debug            启用调试模式，显示详细的处理信息
  --model MODEL      指定要使用的AI模型，如gemini-2.5-pro-exp-03-25
  --input FILE       指定聊天记录文件路径
  --template FILE    指定模板文件名（位于templates目录下）
  --html-to-png      仅将HTML文件转换为PNG图像，需要与--input一起使用

示例:
  python app.py --input chat.txt --template default_template.txt
  python app.py --debug --model gpt-4o --input chat.txt
  python app.py --html-to-png --input report.html
    """)

def main():
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='微信群聊日报生成器')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--model', type=str, help='指定要使用的模型')
    parser.add_argument('--input', type=str, help='指定聊天记录文件路径')
    parser.add_argument('--template', type=str, help='指定模板文件名')
    parser.add_argument('--help-more', action='store_true', help='显示更多帮助信息')
    args = parser.parse_args()

    # 如果请求显示更多帮助信息
    if args.help_more:
        print_usage()
        sys.exit(0)

    # 全局调试模式标志
    global DEBUG_MODE
    DEBUG_MODE = args.debug

    # 将args保存为全局变量，以便在其他函数中使用
    global ARGS
    ARGS = args

    # 获取API密钥和基础URL
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "")  # 默认为空字符串而不是None

    if not OPENAI_API_KEY:
        print("请设置OPENAI_API_KEY环境变量")
        sys.exit(1)

    # 创建ChatBot实例
    # 如果OPENAI_BASE_URL为空字符串，则传递None给ChatBot
    base_url = OPENAI_BASE_URL if OPENAI_BASE_URL else None
    chatbot = ChatBot(OPENAI_API_KEY, base_url)

    # 如果启用了调试模式，打印一些系统信息
    if DEBUG_MODE:
        print(f"Python版本: {sys.version}")
        print(f"OpenAI库版本: {openai.__version__}")
        print(f"操作系统: {os.name}, {sys.platform}")
        print(f"调试模式: 已启用")

    # 加载模板函数
    def load_template(template_name="default_template.txt"):
        """
        从templates目录加载指定的模板文件

        Args:
            template_name: 模板文件名，默认为default_template.txt

        Returns:
            模板内容字符串
        """
        template_path = os.path.join("templates", template_name)
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"加载模板文件时出错: {str(e)}")
            return None

    # 获取可用模板列表
    def get_available_templates():
        """
        获取templates目录中所有可用的模板文件

        Returns:
            模板文件名列表
        """
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)

        template_files = glob.glob(os.path.join(templates_dir, "*.txt"))
        return [os.path.basename(f) for f in template_files]

    # 显示可用模板并让用户选择
    available_templates = get_available_templates()
    if not available_templates:
        print("未找到任何模板文件，将使用默认模板。")
        # 如果没有模板文件，创建默认模板
        default_template_content = """任务：根据提供的微信群聊天记录（txt格式）生成今日群日报，输出为风格固定、一致的HTML页面，适合截图分享
# 此处应该有完整的模板内容，但由于已经保存到文件中，这里省略
"""
        with open(os.path.join("templates", "default_template.txt"), 'w', encoding='utf-8') as f:
            f.write(default_template_content)
        available_templates = ["default_template.txt"]

    print("可用的模板文件:")
    for i, template in enumerate(available_templates):
        print(f"{i+1}. {template}")

    # 选择模板
    selected_template = "default_template.txt"  # 默认模板

    # 使用全局ARGS变量

    # 优先使用命令行参数指定的模板
    if ARGS and ARGS.template:
        template_name = ARGS.template
        # 检查指定的模板是否存在
        if template_name in available_templates:
            selected_template = template_name
            print(f"使用命令行指定的模板: {selected_template}")
        else:
            print(f"命令行指定的模板 '{template_name}' 不存在，将使用默认模板。")
    else:
        # 如果没有通过命令行指定模板，则让用户选择
        try:
            choice = input("请选择模板编号 (直接回车使用默认模板): ")
            if choice.strip():
                index = int(choice) - 1
                if 0 <= index < len(available_templates):
                    selected_template = available_templates[index]
                else:
                    print("无效的选择，将使用默认模板。")
        except ValueError:
            print("无效的输入，将使用默认模板。")

    # 加载选定的模板
    SYSTEM_PROMPT = load_template(selected_template)
    if not SYSTEM_PROMPT:
        print("模板加载失败，将使用内置默认模板。")
        SYSTEM_PROMPT = """任务：根据提供的微信群聊天记录（txt格式）生成今日群日报，输出为风格固定、一致的HTML页面，适合截图分享
# 此处应该有完整的模板内容，但作为备用方案，这里省略详细内容
"""

    # 从文件读取聊天记录
    try:
        # 优先使用命令行参数指定的文件路径
        if ARGS and ARGS.input:
            file_path = ARGS.input
            print(f"使用命令行指定的聊天记录文件: {file_path}")
        else:
            file_path = input("请输入聊天记录文件路径: ")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            chat_content = file.read()
            print(f"成功读取聊天记录文件: {file_path} ({len(chat_content)} 字节)")
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        raise e

    # 创建对话
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请根据以下聊天记录生成群日报：\n{chat_content}"}
    ]

    # 确保输出目录存在
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 使用流式响应
    try:
        # 使用命令行参数中指定的模型，如果有的话
        model = ARGS.model if ARGS else None  # 从命令行参数获取模型名称
        if model:
            print(f"使用命令行指定的模型: {model}")
        response_stream = chatbot.create_chat(messages, model=model, stream=True)
        print("Assistant: ", end="", flush=True)  # 不换行，立即显示

        # 用于收集完整响应
        full_response = ""

        # 逐步处理流式响应
        for chunk in response_stream:
            try:
                # 在调试模式下打印chunk的详细信息
                if DEBUG_MODE:
                    debug_object(chunk, "响应块: ")

                # 检查chunk是否有choices属性，以及choices列表是否非空
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    # 在调试模式下打印choices[0]的详细信息
                    if DEBUG_MODE:
                        debug_object(chunk.choices[0], "  choices[0]: ")

                    # 从delta中提取内容
                    if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                        content = chunk.choices[0].delta.content
                        if content is not None:
                            full_response += content
                            print(content, end="", flush=True)  # 不换行，立即显示
                    # 如果没有delta.content，尝试从message.content获取
                    elif hasattr(chunk.choices[0], 'message') and hasattr(chunk.choices[0].message, 'content'):
                        content = chunk.choices[0].message.content
                        if content is not None:
                            full_response += content
                            print(content, end="", flush=True)  # 不换行，立即显示
            except Exception as e:
                print(f"\n处理响应块时出错: {str(e)}", end="", flush=True)
                if DEBUG_MODE:
                    traceback.print_exc()
                # 继续处理下一个块，不中断整个流程

        print()  # 最后添加一个换行

        # 提取HTML内容
        html_content = extract_html_from_response(full_response)

        if html_content:
            # 生成时间戳作为文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # 保存HTML文件
            html_file_path = os.path.join(output_dir, f"report_{timestamp}.html")
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML已保存到: {html_file_path}")

            # 将HTML转换为PNG图像
            png_file_path = os.path.join(output_dir, f"report_{timestamp}.png")
            convert_html_to_png(html_file_path, png_file_path)
            print(f"PNG图像已保存到: {png_file_path}")
        else:
            print("未在响应中找到HTML内容")

    except Exception as e:
        print(f"\n处理响应时出错: {str(e)}")

if __name__ == "__main__":
    main()
