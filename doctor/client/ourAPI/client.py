"""
自定义API客户端实现
继承自通用大语言模型客户端
"""

# 导入第三方库
from openai import OpenAI  # OpenAI客户端

# 导入项目模块
from client.LLMclientgeneric import LLMclientgeneric  # 通用大语言模型客户端


class OurAPI(LLMclientgeneric):
    """
    自定义API客户端类
    继承自LLMclientgeneric，用于实现我们自己的API客户端
    """
    
    def __init__(self, *args, **kwargs):
        """
        初始化自定义API客户端
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)  # 调用父类初始化方法