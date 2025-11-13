"""
大语言模型客户端基类
定义与大语言模型交互的抽象接口
"""

# 导入标准库
from abc import abstractmethod  # 抽象基类相关功能
from typing import List, Dict  # 类型提示

# 导入第三方库
from openai import OpenAI  # OpenAI客户端
from openai import Stream  # 流式响应
from openai.types.chat import ChatCompletion, ChatCompletionChunk  # 聊天完成类型

# 导入项目模块
from env import get_env_value  # 获取环境变量值的函数


class LLMclientbase(object):
    """
    大语言模型客户端基类
    定义与大语言模型交互的通用接口
    """

    def __init__(self):
        """
        初始化LLM客户端基类
        """
        # 使用环境变量中的API密钥和基础URL初始化OpenAI客户端
        self.__client = OpenAI(
            api_key=get_env_value("LLM_API_KEY"),  # API密钥
            base_url=get_env_value("LLM_BASE_URL"),  # 基础URL
        )
        self.__model_name = get_env_value("MODEL_NAME")  # 使用环境变量中的模型名称

    @property
    def client(self):
        """
        获取OpenAI客户端实例
        
        Returns:
            OpenAI: OpenAI客户端实例
        """
        return self.__client

    @property
    def model_name(self):
        """
        获取模型名称
        
        Returns:
            str: 模型名称
        """
        return self.__model_name

    # 以下全都是抽象函数
    @abstractmethod
    def chat_with_ai(self, prompt: str) -> str | None:
        """
        与AI进行聊天，返回AI的回复
        
        Args:
            prompt (str): 用户输入的提示信息
            
        Returns:
            str | None: AI的回复，可能为None
        """
        raise NotImplementedError()  # 抽象方法，需要子类实现

    @abstractmethod
    def chat_with_ai_stream(
        self, prompt: str, history: List[List[str]] | None = None
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        与AI进行流式聊天，返回流式回复
        
        Args:
            prompt (str): 用户输入的提示信息
            history (List[List[str]] | None): 聊天历史记录，默认为None
            
        Returns:
            ChatCompletion | Stream[ChatCompletionChunk]: 流式聊天完成或流式聊天块
        """
        raise NotImplementedError()  # 抽象方法，需要子类实现

    @abstractmethod
    def construct_message(
        self, prompt: str, history: List[List[str]] | None = None
    ) -> List[Dict[str, str]] | str | None:
        """
        构造消息，用于与AI进行聊天
        
        Args:
            prompt (str): 用户输入的提示信息
            history (List[List[str]] | None): 聊天历史记录，默认为None
            
        Returns:
            List[Dict[str, str]] | str | None: 构造的消息列表或字符串，可能为None
        """
        raise NotImplementedError()  # 抽象方法，需要子类实现

    @abstractmethod
    def chat_using_messages(self, messages: List[Dict]) -> str | None:
        """
        使用消息列表与AI进行聊天，返回AI的回复
        
        Args:
            messages (List[Dict]): 消息列表
            
        Returns:
            str | None: AI的回复，可能为None
        """
        raise NotImplementedError()  # 抽象方法，需要子类实现