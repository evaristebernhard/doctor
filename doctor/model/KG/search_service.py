"""
知识图谱搜索服务模块
提供统一的知识图谱实体搜索接口
"""

# 导入标准库
from typing import Tuple, List, Dict  # 类型提示

# 导入项目模块
from model.KG.search_model import INSTANCE  # 实体搜索器实例


def search(query: str) -> Tuple[int, List[Dict] | None]:
    """
    搜索知识图谱中的实体
    
    Args:
        query (str): 查询字符串
        
    Returns:
        Tuple[int, List[Dict] | None]: 搜索结果元组，包含状态码和结果列表
            - 状态码：0表示成功，-1表示失败
            - 结果列表：成功时返回实体列表，失败时返回None
    """
    result = INSTANCE.search(query)  # 调用实体搜索器进行搜索
    if result is not None:  # 搜索成功
        return 0, result
    else:  # 搜索失败
        return -1, None