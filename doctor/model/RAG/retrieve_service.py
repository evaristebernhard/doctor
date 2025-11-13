# 该函数用于对外界提供retreive服务，调用的是retrieve_model 中的接口
# 这是一个检索服务模块，用于根据查询从知识库中检索相关文档

# 从typing模块导入List类型，用于类型提示
from typing import List

# 从model.RAG.retrieve_model模块导入INSTANCE单例对象，用于访问检索器实例
from model.RAG.retrieve_model import INSTANCE

# 从langchain_core.documents模块导入Document类，用于表示检索到的文档
from langchain_core.documents import Document

def retrieve(query: str) -> List[Document]:
    """
    根据查询字符串检索相关文档
    
    Args:
        query (str): 查询字符串
        
    Returns:
        List[Document]: 检索到的文档列表
    """
    # 检查实例是否有关联的用户ID
    if INSTANCE.user_id is None:
        # 如果没有用户ID，使用默认检索器进行检索
        doc = INSTANCE.retriever.invoke(query)
    else:
        # 如果有用户ID，获取用户特定的检索器进行检索
        doc = INSTANCE.get_user_retriever().invoke(query)
        
    # 返回检索到的文档列表
    return doc