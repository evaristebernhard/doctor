'''大模型特征工程，提取要进行tts的文本和语种'''
# 从typing模块导入List和Dict类型，用于类型提示
from typing import List, Dict

# 从client.clientfactory模块导入Clientfactory类，用于创建AI客户端
from client.clientfactory import Clientfactory

# 定义生成音频的提示词，用于指导AI从对话中提取需要转成语音的文本
_GENERATE_AUDIO_PROMPT_ = (
    "请从上述对话中帮我提取出即将要转成语音的文本，不要包含提示文字"
)


def __construct_messages(
    question: str, history: List[List | None]
) -> List[Dict[str, str]]:
    """
    构造发送给AI模型的消息列表
    
    Args:
        question (str): 用户当前的问题
        history (List[List | None]): 对话历史记录
        
    Returns:
        List[Dict[str, str]]: 构造好的消息列表
    """
    # 初始化消息列表，添加系统角色的提示信息
    messages = [
        {
            "role": "system",
            "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息，无需包含提示文字",
        }
    ]

    # 遍历对话历史，将用户输入和AI回复添加到消息列表中
    for user_input, ai_response in history:
        messages.append({"role": "user", "content": user_input})  # 添加用户输入
        messages.append({"role": "assistant", "content": repr(ai_response)})  # 添加AI回复

    # 添加当前问题
    messages.append({"role": "user", "content": question})
    # 添加生成音频的提示词
    messages.append({"role": "user", "content": _GENERATE_AUDIO_PROMPT_})

    # 返回构造好的消息列表
    return messages


def extract_text(question: str, history: List[List | None] | None = None) -> str:
    """
    从问题和对话历史中提取需要转成语音的文本
    
    Args:
        question (str): 用户问题
        history (List[List | None] | None): 对话历史记录
        
    Returns:
        str: 提取到的需要转成语音的文本
    """
    # 构造消息列表，如果history为None则使用空列表
    messages = __construct_messages(question, history or [])
    # 使用客户端工厂创建客户端，并通过消息列表与AI模型交互获取结果
    result = Clientfactory().get_client().chat_using_messages(messages)

    # 返回提取到的文本
    return result


def extract_language(text: str) -> str:
    """
    从文本中提取语音合成的语言类型
    
    Args:
        text (str): 输入文本
        
    Returns:
        str: 提取到的语言类型
    """
    # 构造消息列表，用于指导AI提取语言类型
    messages = [
        {
            "role": "system",
            "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息，不要复述，无需包含提示文字",
        },
        {
            "role": "user",
            "content": f"""
            请从如下文本中提取出文本转语音的语种，提取结果只有5种可能（普通话，陕西话，东北话，粤语，台湾话），
            如果文本中有语种信息，但不是以上5种，如英语、日语...则直接返回一个词：其他，
            如果如下文本不包含语种信息，直接返回一个字：无。
            （注意：结果中不要包含任何符号和提示信息）：\n{text}
            """,
        },
    ]
    # 使用客户端工厂创建客户端，并通过消息列表与AI模型交互获取结果
    result = Clientfactory().get_client().chat_using_messages(messages)
    # 返回提取到的语言类型
    return result


def get_tts_model_name(lang: str, gender: str) -> str:
    """
    根据语言和性别获取对应的TTS模型名称
    
    Args:
        lang (str): 语言类型
        gender (str): 性别类型
        
    Returns:
        str: TTS模型名称和是否成功的元组
    """
    # 如果语言为"无"且性别为"无"或"男声"，返回普通话男声模型
    if lang == "无" and (gender == "无" or gender == "男声"):
        return "zh-CN-YunxiNeural", True  # 返回普通话男声

    # 如果语言为"无"且性别为"女声"，返回普通话女声模型
    if lang == "无" and gender == "女声":
        return "zh-CN-XiaoxiaoNeural", True  # 返回普通话女声

    # 如果语言为"陕西话"且性别为"女声"或"无"，返回陕西话女声模型
    if lang == "陕西话" and (gender == "女声" or gender == "无"):
        return "zh-CN-shaanxi-XiaoniNeural", True  # 返回陕西话女声

    # 如果语言为"东北话"且性别为"女声"或"无"，返回东北话女声模型
    if lang == "东北话" and (gender == "女声" or gender == "无"):
        return "zh-CN-liaoning-XiaobeiNeural", True  # 返回东北话女声

    # 如果语言为"粤语"且性别为"女声"，返回粤语女声模型
    if lang == "粤语" and gender == "女声":
        return "zh-HK-HiuMaanNeural", True  # 返回粤语女声

    # 如果语言为"粤语"且性别为"男声"或"无"，返回粤语男声模型
    if lang == "粤语" and (gender == "男声" or gender == "无"):
        return "zh-HK-WanLungNeural", True  # 返回粤语男声

    # 如果语言为"台湾话"且性别为"男声"，返回台湾话男声模型
    if lang == "台湾话" and gender == "男声":
        return "zh-TW-YunJheNeural", True  # 返回台湾话男声

    # 如果语言为"台湾话"且性别为"女声"或"无"，返回台湾话女声模型
    if lang == "台湾话" and (gender == "女声" or gender == "无"):
        return "zh-TW-HsiaoChenNeural", True  # 返回台湾话女声

    # 默认返回普通话男声模型和失败标志
    return "zh-CN-YunxiNeural", False  # 可设置一个默认返回值，防止未匹配的情况


def extract_gender(text: str) -> str:
    """
    从文本中提取语音合成的性别类型
    
    Args:
        text (str): 输入文本
        
    Returns:
        str: 提取到的性别类型
    """
    # 构造消息列表，用于指导AI提取性别类型
    messages = [
        {
            "role": "system",
            "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息，不要复述，无需包含提示文字",
        },
        {
            "role": "user",
            "content": f"请从如下文本中提取出文本转语音的声音性别，提取的结果只有两种可能，男声和女声，如果如下文本不包含声音性别，"
            f"直接返回一个字：无。（注意：结果中不要包含任何符号和提示信息）：\n{text}",
        },
    ]

    # 使用客户端工厂创建客户端，并通过消息列表与AI模型交互获取结果
    result = Clientfactory().get_client().chat_using_messages(messages)

    # 返回提取到的性别类型
    return result