'''大模型特征工程，让大模型输出json格式的数据'''
# 导入标准库
import json  # JSON处理模块，用于处理JSON数据
import re  # 正则表达式模块，用于文本格式处理
from typing import List, Dict  # 类型提示，用于列表和字典类型注解

# 导入项目模块
from client.clientfactory import Clientfactory  # 客户端工厂，用于创建与AI模型通信的客户端

# 模拟一个用于生成 docx 内容的 JSON 模板
__output_format_docx = json.dumps({
    "title": "example title",  # Word文档标题
    "sections": [  # 文档章节列表
        {
            "heading": "Section 1",  # 第一章节标题
            "paragraphs": [  # 章节内段落列表
                {
                    "heading": "Paragraph 1",  # 第一段标题
                    "content": "Details of paragraph 1"  # 第一段详细内容
                },
                {
                    "heading": "Paragraph 2",  # 第二段标题
                    "content": "Details of paragraph 2"  # 第二段详细内容
                }
            ]
        },
        {
            "heading": "Section 2",  # 第二章节标题
            "paragraphs": [  # 章节内段落列表
                {
                    "heading": "Paragraph 1",  # 第一段标题
                    "content": "Details of paragraph 1"  # 第一段详细内容
                },
                {
                    "heading": "Paragraph 2",  # 第二段标题
                    "content": "Details of paragraph 2"  # 第二段详细内容
                },
                {
                    "heading": "Paragraph 3",  # 第三段标题
                    "content": "Details of paragraph 3"  # 第三段详细内容
                }
            ]
        }
    ]
}, ensure_ascii=True)  # 确保ASCII字符正确编码

# 定义一个 prompt 用于生成 docx 内容
_GENERATE_DOCX_PROMPT_ = f'''请你根据用户要求生成docx的详细内容，不要省略。按这个JSON格式输出{__output_format_docx}，只能返回JSON，且JSON不要用```包裹，不要返回markdown格式'''

# 构造消息函数，历史记录被包括在内
def __construct_messages_docx(question: str, history: List[List | None]) -> List[Dict[str, str]]:
    """
    构造发送给AI模型的消息列表，用于生成Word文档内容
    
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
    # 添加生成Word文档的提示词
    messages.append({"role": "user", "content": _GENERATE_DOCX_PROMPT_})

    # 返回构造好的消息列表
    return messages

# 生成 docx 内容的函数
def generate_docx_content(question: str,
                         history: List[List | None] | None = None) -> str:
    """
    生成Word文档的文字内容，并对格式进行检查和修正
    
    Args:
        question (str): 用户问题
        history (List[List | None] | None): 对话历史记录
        
    Returns:
        str: 生成的Word文档内容（JSON格式字符串）
    """
    # 构造消息列表，如果history为None则使用空列表
    messages = __construct_messages_docx(question, history or [])
    # 打印消息列表到控制台用于调试
    print(messages)
    # 使用客户端工厂创建客户端，并通过消息列表与AI模型交互
    result = Clientfactory().get_client().chat_using_messages(messages)
    # 打印AI模型返回的结果到控制台用于调试
    print(result)
    # 打印结果类型到控制台用于调试
    print(type(result))

    # 处理生成内容中的多余部分，比如"json"关键字或者反引号
    # 使用正则表达式移除结果中的"json"关键词
    result = re.sub(r'\bjson\b', '', result)
    # 使用正则表达式移除结果中的反引号字符
    result = re.sub(r'`', '', result)

    # 检查生成内容的结尾是否正确
    # 查找最后一个双引号的位置
    index_of_last = result.rfind('"')
    # 初始化最终结果变量
    total_result = None
    # 打印处理后的结果到控制台用于调试
    print(result)

    # 检查结果格式是否正确（以"}]}]}"结尾）
    if index_of_last != -1 and result[index_of_last + 1:] == '}]}]}':
        # 如果格式正确，不做改变
        total_result = result
        # 打印最终结果到控制台用于调试
        print(total_result)
        # 返回最终结果
        return total_result
    else:
        # 如果格式不正确，修复 JSON 的结尾
        total_result = result[:index_of_last + 1] + '}]}]}'
        # 打印修复后的结果到控制台用于调试
        print(total_result)
        # 返回修复后的结果
        return total_result