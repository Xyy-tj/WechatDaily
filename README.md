# 微信群聊日报生成器 - 微服务架构版本

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0%2B-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/) [![Playwright](https://img.shields.io/badge/Playwright-1.30.0%2B-2EAD33?style=flat&logo=playwright)](https://playwright.dev/) [![OpenAI](https://img.shields.io/badge/OpenAI_API-GPT--4-412991?style=flat&logo=openai)](https://openai.com/) [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


<div align="center">
<h3>这个项目是一个微信群聊日报生成器，但远不止于此</h3>
</div>

<table align="center">
  <tr>
    <td>
      <h3 align="center">✨ 核心功能</h3>
      <ul>
        <li>🔍 识别群聊的 <b>关键决策</b> </b>（而不是99+"收到"）</li>
        <li>🏆 标记群聊的 <b>"抽象整活哥"</b> 和 <b>"最佳贡献者"</b></li>
        <li>📝 记录当天的 <b>"本群记忆和黑话烂梗"</b></li>
        <li>📊 生成美观的日报，一目了然群聊精华</li>
      </ul>
    </td>
    <td>
      <h3 align="center">🛠️ 技术栈</h3>
      <ul>
        <li>⚡ 用 <b>FastAPI</b> 快速搭建高性能服务</li>
        <li>🧠 <b>AI驱动</b> 自动过滤无效信息</li>
        <li>🖼️ 输出支持HTML/图片格式</li>
        <li>🔄 微服务架构，模块化设计</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <h3 align="center">💡 最适合</h3>
      <div align="center">
        <b>👨‍💻 每天被100+群消息轰炸的互联网打工人</b> &nbsp;|&nbsp;
        <b>🕵️ 想看看群里谁在说"正确的废话"的好奇宝宝</b> &nbsp;|&nbsp;
        <b>📋 需要写周报但不想看聊天记录的懒人</b> &nbsp;|&nbsp;
        <b>👔 想要高效管理团队沟通的管理者</b>
      </div>
    </td>
  </tr>
</table>

<!-- <div align="center">
  <img src="screenshots/banner.jpg" alt="项目横幅" width="800">
</div> -->

## 📋 目录

- [微信群聊日报生成器 - 微服务架构版本](#微信群聊日报生成器---微服务架构版本)
  - [📋 目录](#-目录)
  - [🚀 项目特点](#-项目特点)
  - [🏁 快速开始](#-快速开始)
  - [项目结构](#项目结构)
  - [功能特点](#功能特点)
  - [服务组件](#服务组件)
  - [安装依赖](#安装依赖)
  - [启动服务](#启动服务)
    - [1. 填好env文件](#1-填好env文件)
    - [2. 使用启动脚本](#2-使用启动脚本)
    - [3. 打开浏览器访问](#3-打开浏览器访问)
  - [API接口](#api接口)
    - [主应用服务](#主应用服务)
    - [HTML转图片服务](#html转图片服务)
  - [使用方式](#使用方式)
    - [通过Web界面使用](#通过web界面使用)
    - [关于wechat聊天记录如何导出](#关于wechat聊天记录如何导出)
  - [注意事项](#注意事项)
  - [截图](#截图)
    - [首页](#首页)
    - [模板管理](#模板管理)
    - [生成结果](#生成结果)

## 🚀 项目特点

- **🤖 AI驱动**：利用OpenAI的GPT模型分析聊天记录，提取关键信息
- **🌐 微服务架构**：模块化设计，服务间松耦合，易于扩展
- **⚡ 高性能**：基于FastAPI的异步处理，响应迅速
- **🎨 美观输出**：生成结构化、美观的HTML和图片格式日报
- **🔧 易于使用**：提供Web界面和API接口，满足不同用户需求
- **📱 移动友好**：生成的日报适合在手机上查看和分享

## 🏁 快速开始

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/WechatDaily.git
   cd WechatDaily
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

3. 设置环境变量
   ```bash
   # Linux/macOS
   export OPENAI_API_KEY=your_api_key

   # Windows
   set OPENAI_API_KEY=your_api_key
   ```

4. 启动服务
   ```bash
   python start_services.py
   ```

5. 打开浏览器访问 http://localhost:8000


## Wechat聊天记录相关项目
微信记录导出可以参考MemoTrace项目（官方已删库），也可以考虑用基于MemoTrace二开的一个小工具项目：https://github.com/Xyy-tj/WeChatMsg


## 项目结构

```
WechatDaily/
├── app/                      # 主应用目录
│   ├── api/                  # API路由
│   ├── core/                 # 核心配置
│   ├── models/               # 数据模型
│   ├── services/             # 服务层
│   └── utils/                # 工具函数
├── html_to_image.py          # HTML转图片核心功能
├── html_to_image_service.py  # 原Flask版HTML转图片服务
├── html_to_image_service_fastapi.py  # FastAPI版HTML转图片服务
├── app.py                    # 原单体应用入口
├── app_soa.py                # 微服务架构主应用入口
├── start_services.py         # 服务启动脚本
├── templates/                # 模板目录
└── output/                   # 输出目录
```

## 功能特点

1. **微服务架构**：将HTML转图片功能分离为独立服务，提高系统可扩展性和可维护性
2. **FastAPI框架**：使用现代化的FastAPI框架，提供自动生成的API文档和类型检查
3. **异步支持**：支持异步处理请求，提高系统性能
4. **模块化设计**：将功能分解为多个模块，便于维护和扩展
5. **Web界面**：提供友好的Web用户界面，方便用户直接在浏览器中使用系统功能

## 服务组件

1. **主应用服务**：提供聊天、模板管理和日报生成功能
   - 端口：8000
   - Web界面：http://localhost:8000/
   - API文档：http://localhost:8000/docs
   - 功能：
     - 生成群聊日报
     - 管理模板
     - 提供RESTful API

2. **HTML转图片服务**：提供HTML内容或文件转换为PNG图片的功能
   - 端口：8001
   - API文档：http://localhost:8001/docs
   - 功能：
     - 将HTML内容转换为PNG图片
     - 将HTML文件转换为PNG图片

## 安装依赖

```bash
pip install fastapi uvicorn pydantic pydantic-settings openai playwright requests jinja2 python-multipart
playwright install  # 安装Playwright浏览器
```

## 启动服务
### 1. 填好env文件
在文件夹内复制.env.example 为 .env，填入你的openai api key，但是此处模型默认使用gemini-2.5-pro-exp-03-25

环境变量目前包括：
- `OPENAI_API_KEY` - OpenAI API密钥
- `OPENAI_BASE_URL` - OpenAI API基础URL（可选）

```bash
# linux环境下bash
cp .env.example .env
# windows环境下cmd
copy .env.example .env
```


### 2. 使用启动脚本

```bash
python start_services.py
```
### 3. 打开浏览器访问
http://localhost:8000/



## API接口

### 主应用服务

- `GET /health` - 健康检查
- `POST /api/chat` - 创建聊天
- `GET /api/templates` - 获取可用模板列表
- `POST /api/html/convert` - 将HTML转换为图片
- `POST /api/daily-report` - 生成群聊日报
- `GET /api/image/{filename}` - 获取生成的图片

### HTML转图片服务

- `GET /health` - 健康检查
- `POST /convert` - 将HTML内容转换为图片
- `POST /convert/file` - 将上传的HTML文件转换为图片
- `GET /image/{filename}` - 获取生成的图片
- `POST /convert_and_download` - 将HTML内容转换为图片并直接下载

## 使用方式

### 通过Web界面使用

1. 启动服务后，打开浏览器访问 http://localhost:8000/
2. 在首页可以上传聊天记录文件，选择模板，生成日报
3. 在模板管理页面可以查看、创建、编辑和删除模板


### 关于wechat聊天记录如何导出

建议使用MEMOTrace（留痕）软件进行群记录导出，一般的组织形式如![示例2](screenshots/群聊名称.txt)为：

MEMOTrace开源地址：https://github.com/LC044/WeChatMsg

```
2025-04-23 13:13:45 张三
为什么不给我打码
2025-04-23 13:13:51 李四
我要发声
2025-04-23 13:15:58 张三
哦忘了
2025-04-23 13:20:21 王五
怎么都这么厉害呢
```




## 注意事项

1. 确保两个服务都正常运行，主应用服务依赖于HTML转图片服务
2. 使用`start_services.py`脚本可以同时启动和监控所有服务
3. 服务启动后，可以通过Web界面或API文档页面使用系统功能
4. Web界面提供了更友好的用户体验，推荐普通用户使用
5. API接口适合开发者集成到自己的应用中

## 截图

### 首页
![首页](screenshots/homepage.jpg)

### 模板管理
![模板管理](screenshots/template.jpg)

### 生成结果
![示例1](screenshots/img1.jpg)
![示例2](screenshots/img2.jpg)

<div align="center">
  <h2>👨‍💻 贡献者</h2>
</div>

<div align="center">
  <a href="https://github.com/Xyy-tj">
    <img src="https://github.com/Xyy-tj.png" width="70" height="70" alt="开发者头像" style="border-radius: 50%; margin: 0 10px;">
  </a>
  <!-- 可以添加更多贡献者 -->
</div>

<div align="center">
  <p>感谢所有为这个项目做出贡献的开发者！</p>
  <p>欢迎提交 Pull Request 或创建 Issue 来帮助改进这个项目。</p>
</div>

<div align="center">
  <h2>📄 许可证</h2>
  <p>本项目采用 <a href="LICENSE">MIT 许可证</a>。</p>
</div>

<div align="center">
  <h2>🙏 致谢</h2>
</div>

<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://fastapi.tiangolo.com/">
          <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="100" alt="FastAPI">
          <br>
          <b>FastAPI</b>
          <br>
          <sub>高性能的Python Web框架</sub>
        </a>
      </td>
      <td align="center">
        <a href="https://playwright.dev/">
          <img src="https://playwright.dev/img/playwright-logo.svg" width="100" alt="Playwright">
          <br>
          <b>Playwright</b>
          <br>
          <sub>现代化的Web测试和自动化库</sub>
        </a>
      </td>
      <td align="center">
        <a href="https://openai.com/">
          <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/OpenAI_Logo.svg/1024px-OpenAI_Logo.svg.png" width="100" alt="OpenAI">
          <br>
          <b>OpenAI API</b>
          <br>
          <sub>强大的AI语言模型</sub>
        </a>
      </td>
      <td align="center">
        <a href="https://jinja.palletsprojects.com/">
          <img src="https://jinja.palletsprojects.com/en/3.1.x/_images/jinja-logo.png" width="100" alt="Jinja2">
          <br>
          <b>Jinja2</b>
          <br>
          <sub>现代化的Python模板引擎</sub>
        </a>
      </td>
    </tr>
  </table>
</div>

<div align="center">
  <br>
  <p>
    <sub>
      Made with ❤️ by developers for developers
    </sub>
  </p>
</div>
