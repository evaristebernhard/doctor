"""
问题解析模块
问答类型判断函数，根据特定输入和大模型进行分类分类
"""

# 导入标准库
from typing import List, Dict  # 类型提示

# 导入第三方库
from icecream import ic  # 调试打印工具

# 导入项目模块
from client.clientfactory import Clientfactory  # 客户端工厂，用于创建与AI模型通信的客户端
from question_answer.prompt_templates import get_question_parser_prompt  # 获取问题解析提示词的函数
from question_answer.purpose_type import purpose_map  # 问题类型映射字典，将字符串映射到枚举值
from question_answer.purpose_type import userPurposeType  # 用户问题类型枚举，定义了各种问题类型


def parse_question(question: str, image_url=None) -> userPurposeType:
    """
    解析用户问题类型
    
    Args:
        question (str): 用户问题
        image_url: 图片URL，用于判断是否涉及图片相关问题
        
    Returns:
        userPurposeType: 问题类型枚举值
    """
    # 根据关键词判断问题类型
    # 如果问题中包含"根据知识库"关键词，则判断为基于知识库的问题类型
    if "根据知识库" in question:
        return purpose_map["基于知识库"]
    
    # 如果问题中包含"根据知识图谱"关键词，则判断为基于知识图谱的问题类型
    if "根据知识图谱" in question:
        return purpose_map["基于知识图谱"]

    # 如果问题中包含"搜索"关键词，则判断为网络搜索的问题类型
    if "搜索" in question:
        return purpose_map["网络搜索"]
    
    # 如果问题中包含word相关关键词且包含生成或制作关键词，则判断为Word生成的问题类型
    if ("word" in question or "Word" in question or "WORD" in question) and ("生成" in question or "制作" in question):
        return purpose_map["Word生成"]
    
    # 如果问题中包含ppt相关关键词且包含生成或制作关键词，则判断为PPT生成的问题类型
    if ("ppt" in question or "PPT" in question or "PPT" in question) and ("生成" in question or "制作" in question):
        return purpose_map["PPT生成"]
    
    # 如果提供了图片URL，则判断为图片描述的问题类型
    if image_url is not None:
        return purpose_map["图片描述"]

    # 在这个函数中我们使用大模型去判断问题类型
    # 获取用于问题分类的提示词模板，并填入具体问题内容
    prompt = get_question_parser_prompt(question)  # 构造提示词
    
    # 使用客户端工厂创建客户端实例，并调用AI模型进行问题分类
    response = Clientfactory().get_client().chat_with_ai(prompt)  # 调用大模型判断
    
    # 使用icecream调试工具输出大模型的分类结果
    ic("大模型分类结果：" + response)  # 调试输出分类结果

    # 根据大模型返回结果映射到具体问题类型
    # 如果模型返回"图片生成"且问题长度大于0，则判断为图片生成类型
    if response == "图片生成" and len(question) > 0:
        return purpose_map["图片生成"]
    
    # 如果模型返回"视频生成"且问题长度大于0，则判断为视频生成类型
    if response == "视频生成" and len(question) > 0:
        return purpose_map["视频生成"]
    
    # 如果模型返回"PPT生成"且问题长度大于0，则判断为PPT生成类型
    if response == "PPT生成" and len(question) > 0:
        return purpose_map["PPT生成"]
    
    # 如果模型返回"Word生成"且问题长度大于0，则判断为Word生成类型
    if response == "Word生成" and len(question) > 0:
        return purpose_map["Word生成"]
    
    # 如果模型返回"音频生成"且问题长度大于0，则判断为音频生成类型
    if response == "音频生成" and len(question) > 0:
        return purpose_map["音频生成"]
    
    # 如果模型返回"文本生成"，则判断为文本生成类型
    if response == "文本生成":
        return purpose_map["文本生成"]
    
    # 如果以上条件都不满足，则默认返回其他类型
    return purpose_map["其他"]  # 默认返回其他类型