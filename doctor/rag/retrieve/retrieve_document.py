# 该文件实现了文档检索功能，用于从知识库中检索与用户问题相关的文档
# 并将检索到的文档格式化为文本形式供后续处理

# 从typing模块导入List和Tuple类型，用于类型注解
from typing import List, Tuple

# 从langchain_core.documents模块导入Document类，用于表示文档对象
from langchain_core.documents import Document

# 从model.RAG.retrieve_service模块导入retrieve函数，用于实际执行文档检索操作
from model.RAG.retrieve_service import retrieve


def format_docs(docs: List[Document]) -> str:
    """
    将文档列表格式化为字符串形式
    
    Args:
        docs (List[Document]): 文档对象列表
        
    Returns:
        str: 格式化后的文档内容字符串，各文档之间用分隔线分隔
    """
    # 使用分隔线连接所有文档的内容，每个文档的内容通过doc.page_content获取
    return "\n-------------分割线--------------\n".join(doc.page_content for doc in docs)


def retrieve_docs(question: str) -> Tuple[List[Document], str]:
    """
    检索与问题相关的文档并返回文档列表和格式化后的文本
    
    Args:
        question (str): 用户提出的问题
        
    Returns:
        Tuple[List[Document], str]: 包含文档列表和格式化文本的元组
    """
    # 调用retrieve函数检索与问题相关的文档，返回文档列表
    docs = retrieve(question)  # 这里的到的是文件
    
    # 调用format_docs函数将文档列表格式化为文本形式
    _context = format_docs(docs)  # 这里处理成文本
    
    # 打印格式化后的文档内容到控制台
    print(_context)
    
    # 返回包含原始文档列表和格式化文本的元组
    return (docs, _context)