# Internet_prompt.py: 联网搜索关键词提取提示词
# 该文件用于构造提示词，指导大模型从用户问题中提取可用于网络搜索的关键词

# 模块文档字符串，说明该模块的作用
'''大模型特征工程，提取搜索关键词'''

# 导入类型提示所需模块
from typing import List, Dict

# 导入客户端工厂类，用于获取大模型客户端
from client.clientfactory import Clientfactory

# 定义用于提取搜索关键词的提示词
_GENERATE_Internet_PROMPT_ = (
    "请根据用户的提问，提取出一个可以在搜索引擎上搜索的问题（不要有多余的内容）"
)


# 构造发送给大模型的消息列表
def __construct_messages(
    question: str, history: List[List | None]
) -> List[Dict[str, str]]:
    # 初始化消息列表，设置系统角色和任务说明
    messages = [
        {
            "role": "system",
            "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息，无需包含提示文字",
        }
    ]

    # 添加用户提问内容
    messages.append({"role": "user", "content": f"用户提问：{question}"})
    
    # 添加提取搜索关键词的指令
    messages.append({"role": "user", "content": _GENERATE_Internet_PROMPT_})

    # 返回构造好的消息列表
    return messages


# 提取用户问题中的搜索关键词
def extract_question(question: str, history: List[List | None] | None = None) -> str:
    # 构造消息列表，如果history为None则使用空列表
    messages = __construct_messages(question, history or [])
    
    # 使用大模型客户端发送消息并获取结果
    result = Clientfactory().get_client().chat_using_messages(messages)

    # 返回提取到的搜索关键词
    return result
