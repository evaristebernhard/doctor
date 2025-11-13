# retrieve类型有很多种,这个文件用于调用不同RAG类型接口
# 这是一个RAG（Retrieval-Augmented Generation）链模块，用于处理基于检索的问答流程

# 从本地模块导入检索文档的函数，用于从知识库中检索相关文档
from rag.retrieve.retrieve_document import retrieve_docs

# 从typing模块导入List类型，用于类型提示
from typing import List

# 从openai库导入Stream类，用于处理流式响应
from openai import Stream

# 从openai库导入ChatCompletionChunk类，用于处理聊天完成的块数据
from openai.types.chat import ChatCompletionChunk

# 从项目client模块导入Clientfactory类，用于创建客户端实例
from client.clientfactory import Clientfactory


def invoke(question: str, history: List[List]) -> Stream[ChatCompletionChunk]:
    """
    调用RAG链处理问答
    
    Args:
        question (str): 用户提出的问题
        history (List[List]): 对话历史记录，每个元素是包含[用户消息, AI回复]的列表
        
    Returns:
        Stream[ChatCompletionChunk]: 流式响应对象，包含AI的回答
    """
    try:
        # 尝试检索与问题相关的文档和上下文
        docs, _context = retrieve_docs(
            question
        )  # 此处得到的是检索到的文件片段和文件处理后的文本
    except Exception as e:
        # 如果检索过程中出现异常，将上下文设置为空字符串
        _context = ""

    # 构造提示词，包含检索到的上下文信息和用户问题
    prompt = f"请根据搜索到的文件信息\n{_context}\n 回答问题：\n{question}"
    
    # 使用客户端工厂创建客户端实例，并调用流式聊天接口获取响应
    response = Clientfactory().get_client().chat_with_ai_stream(prompt)

    # 返回流式响应结果
    return response