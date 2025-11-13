"""
通用大语言模型客户端实现
封装调用大模型代理的API接口的函数
"""

# 导入标准库
from typing import List, Dict  # 类型提示

# 导入第三方库
from openai.types.chat import ChatCompletion, ChatCompletionChunk  # 聊天完成类型
from openai import Stream  # 流式响应

# 导入项目模块
from client.LLMclientbase import LLMclientbase  # 大语言模型客户端基类
from overrides import override  # 覆写注解


class LLMclientgeneric(LLMclientbase):
    """
    通用大语言模型客户端实现类
    继承自LLMclientbase，实现具体的API调用逻辑
    """

    def __init__(self, *args, **kwargs):
        """
        初始化通用大语言模型客户端
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__()  # 调用父类初始化方法

    # 该函数只负责单轮对话交流，不支持流式输出，无历史输入
    @override
    def chat_with_ai(self, prompt: str) -> str | None:
        """
        与AI进行单轮对话，返回AI的回复
        
        Args:
            prompt (str): 用户输入的提示信息
            
        Returns:
            str | None: AI的回复，可能为None
        """
        # 调用OpenAI API进行聊天完成
        response = self.client.chat.completions.create(
            model=self.model_name,  # 使用的模型名称
            messages=[
                {"role": "user", "content": prompt},  # 用户消息
            ],
            top_p=0.7,  # 核采样参数
            temperature=0.95,  # 温度参数，控制随机性
            max_tokens=1024,  # 最大生成令牌数
        )
        return response.choices[0].message.content  # 返回AI回复内容

    # 该函数支持流式输出并且可以输入历史，是主要功能函数
    @override
    def chat_with_ai_stream(
        self, prompt: str, history: List[List[str]] | None = None
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        与AI进行流式对话，支持历史记录
        
        Args:
            prompt (str): 用户输入的提示信息
            history (List[List[str]] | None): 聊天历史记录，默认为None
            
        Returns:
            ChatCompletion | Stream[ChatCompletionChunk]: 流式聊天完成或流式聊天块
        """
        # 调用OpenAI API进行流式聊天完成
        response = self.client.chat.completions.create(
            model=self.model_name,  # 使用的模型名称
            messages=self.construct_message(prompt, history if history else []),  # 构造消息
            top_p=0.7,  # 核采样参数
            temperature=0.95,  # 温度参数，控制随机性
            max_tokens=1024,  # 最大生成令牌数
            stream=True,  # 启用流式输出
        )
        return response  # 返回流式响应

    # 该函数用于构造消息，进行提示词工程
    @override
    def construct_message(
        self, prompt: str, history: List[List[str]] | None = None
    ) -> List[Dict[str, str]] | str | None:
        """
        构造消息列表，用于与AI进行聊天
        
        Args:
            prompt (str): 用户输入的提示信息
            history (List[List[str]] | None): 聊天历史记录，默认为None
            
        Returns:
            List[Dict[str, str]] | str | None: 构造的消息列表或字符串，可能为None
        """
        # 初始化消息列表，添加系统角色
        messages = [
            {
                "role": "system",
                "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的回答。",
            }
        ]

        # 添加历史对话记录
        for user_input, ai_response in history:
            messages.append({"role": "user", "content": user_input})  # 用户消息
            messages.append({"role": "assistant", "content": ai_response.__repr__()})  # AI回复

        # 添加当前用户提示
        messages.append({"role": "user", "content": prompt})
        return messages  # 返回构造的消息列表

    # 该函数用于直接输入消息进行对话，在ppt/word生成中作用
    @override
    def chat_using_messages(self, messages: List[Dict]) -> str | None:
        """
        使用消息列表与AI进行聊天，返回AI的回复
        
        Args:
            messages (List[Dict]): 消息列表
            
        Returns:
            str | None: AI的回复，可能为None
        """
        # 调用OpenAI API进行聊天完成
        response = self.client.chat.completions.create(
            model=self.model_name,  # 使用的模型名称
            messages=messages,  # 消息列表
            top_p=0.7,  # 核采样参数
            temperature=0.95,  # 温度参数，控制随机性
            max_tokens=1024,  # 最大生成令牌数
        )

        return response.choices[0].message.content  # 返回AI回复内容