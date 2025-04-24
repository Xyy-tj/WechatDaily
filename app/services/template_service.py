import os
import glob
import logging
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

class TemplateService:
    """模板服务类，负责管理和加载模板"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        初始化模板服务
        
        Args:
            templates_dir: 模板目录，如果为None则使用配置中的目录
        """
        self.templates_dir = templates_dir or settings.TEMPLATES_DIR
        
        # 确保模板目录存在
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            logger.info(f"创建模板目录: {self.templates_dir}")
        
        logger.info(f"模板服务初始化完成，使用目录: {self.templates_dir}")
    
    def get_available_templates(self) -> List[str]:
        """
        获取所有可用的模板文件
        
        Returns:
            模板文件名列表
        """
        template_files = glob.glob(os.path.join(self.templates_dir, "*.txt"))
        templates = [os.path.basename(f) for f in template_files]
        
        # 如果没有找到模板，创建默认模板
        if not templates:
            logger.info("未找到任何模板文件，将创建默认模板")
            self.create_default_template()
            templates = ["default_template.txt"]
        
        return templates
    
    def load_template(self, template_name: str = "default_template.txt") -> Optional[str]:
        """
        加载指定的模板文件
        
        Args:
            template_name: 模板文件名，默认为default_template.txt
            
        Returns:
            模板内容字符串，如果加载失败则返回None
        """
        template_path = os.path.join(self.templates_dir, template_name)
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                content = file.read()
                logger.info(f"成功加载模板: {template_name}")
                return content
        except Exception as e:
            logger.error(f"加载模板文件时出错: {str(e)}")
            return None
    
    def create_default_template(self) -> bool:
        """
        创建默认模板文件
        
        Returns:
            创建是否成功
        """
        default_template_path = os.path.join(self.templates_dir, "default_template.txt")
        default_template_content = """任务：根据提供的微信群聊天记录（txt格式）生成今日群日报，输出为风格固定、一致的HTML页面，适合截图分享

要求：
1. 分析聊天记录，提取今日的主要话题、讨论内容和重要信息
2. 将内容整理为结构化的日报形式
3. 生成美观、专业的HTML页面，具有良好的视觉层次和排版
4. 页面应包含标题、日期、主要内容摘要、详细讨论等部分
5. 使用适当的字体、颜色和间距，确保可读性
6. 设计应简洁大方，适合在手机上查看
7. 输出完整的HTML代码，可直接用于截图分享

HTML设计风格：
- 使用现代、简洁的设计
- 主色调使用蓝色系(#3498db)，搭配白色背景
- 标题使用22px大小，内容使用16px大小
- 使用卡片式布局，有适当的阴影和圆角
- 包含群名称、日期、主要话题、讨论要点等内容
- 可以添加简单的图标来增强视觉效果

请直接输出完整的HTML代码，不需要解释。
"""
        try:
            with open(default_template_path, 'w', encoding='utf-8') as f:
                f.write(default_template_content)
            logger.info(f"成功创建默认模板: {default_template_path}")
            return True
        except Exception as e:
            logger.error(f"创建默认模板时出错: {str(e)}")
            return False
