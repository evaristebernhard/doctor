'''大模型特征工程，让大模型输出json格式的数据'''
# 导入标准库
import json  # JSON处理模块，用于处理JSON数据
from typing import List, Dict  # 类型提示，用于列表和字典类型注解
import re  # 正则表达式模块，用于文本格式处理

# 导入项目模块
from client.clientfactory import Clientfactory  # 客户端工厂，用于创建与AI模型通信的客户端

# 输出格式示例，定义了PPT内容的标准JSON结构
__output_format = json.dumps({
    "title": "example title",  # PPT标题
    "pages": [  # PPT页面列表
        {
            "title": "title for page 1",  # 第一页标题
            "content": [  # 第一页内容列表
                {
                    "title": "title for paragraph 1",  # 第一段标题
                    "description": "detail for paragraph 1",  # 第一段详细内容
                },
                {
                    "title": "title for paragraph 2",  # 第二段标题
                    "description": "detail for paragraph 2",  # 第二段详细内容
                },
            ],
        },
        {
            "title": "title for page 2",  # 第二页标题
            "content": [  # 第二页内容列表
                {
                    "title": "title for paragraph 1",  # 第一段标题
                    "description": "detail for paragraph 1",  # 第一段详细内容
                },
                {
                    "title": "title for paragraph 2",  # 第二段标题
                    "description": "detail for paragraph 2",  # 第二段详细内容
                },
                {
                    "title": "title for paragraph 3",  # 第三段标题
                    "description": "detail for paragraph 3",  # 第三段详细内容
                },
            ],
        },
    ],
}, ensure_ascii=True)  # 确保ASCII字符正确编码

# 生成PPT的提示词模板，指导大模型按指定格式输出JSON
_GENERATE_PPT_PROMPT_ = f'''请你根据用户要求生成ppt的详细内容，不要省略。按这个JSON格式输出{__output_format}，只能返回JSON，且JSON不要用```包裹，不要返回markdown格式'''

def __construct_messages(question: str, history: List[List | None]) -> List[Dict[str, str]]:
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
        {"role": "system",
         "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息。"}]

    # 遍历对话历史，将用户输入和AI回复添加到消息列表中
    for user_input, ai_response in history:
        messages.append({"role": "user", "content": user_input})  # 添加用户输入
        messages.append(
            {"role": "assistant", "content": repr(ai_response)})  # 添加AI回复
    # 添加当前问题作为系统内容
    messages.append({"role": "system", "content": question})
    # 添加生成PPT的提示词
    messages.append({"role": "user", "content": _GENERATE_PPT_PROMPT_})

    # 返回构造好的消息列表
    return messages

#生成ppt的文字内容，并对格式进行检查修改
def generate_ppt_content(question: str,
                         history: List[List | None] | None = None) -> str:
    """
    生成PPT的文字内容，并对格式进行检查和修正
    
    Args:
        question (str): 用户问题
        history (List[List | None] | None): 对话历史记录
        
    Returns:
        str: 生成的PPT内容（JSON格式字符串）
    """
    # 构造消息列表，如果history为None则使用空列表
    messages = __construct_messages(question, history or [])
    # 打印消息列表到控制台用于调试
    print(messages)
    # 使用客户端工厂创建客户端，并通过消息列表与AI模型交互
    result = Clientfactory().get_client().chat_using_messages(messages)
    # 打印AI模型返回的结果到控制台用于调试
    print(result)
    # 打印结果类型到控制台用于调试
    print(type(result))

    # 使用正则表达式移除结果中的"json"关键词
    result = re.sub(r'\bjson\b', '', result)
    # 使用正则表达式移除结果中的反引号字符
    result = re.sub(r'`','',result)

    # 查找最后一个双引号的位置
    index_of_last = result.rfind('"')
    # 初始化最终结果变量
    total_result=None
    # 打印处理后的结果到控制台用于调试
    print(result)

    # 检查结果格式是否正确（以"}]}]}"结尾）
    if index_of_last!= -1 and result[index_of_last + 1:] == '}]}]}':
        # 如果已经是正确的，则不做任何改变
        total_result = result
        # 打印最终结果到控制台用于调试
        print(total_result)
        # 返回最终结果
        return total_result
    else:
        # 如果格式不正确，则尝试修复格式
        total_result = result[:index_of_last + 1] + '}]}]}'
        # 打印修复后的结果到控制台用于调试
        print(total_result)
        # 返回修复后的结果
        return total_result