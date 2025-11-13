"""
答案获取模块
根据问答类型选择对应的工具函数进行处理
"""

# 导入标准库
from typing import Tuple, List, Any  # 类型提示

# 导入项目模块
from question_answer.function_tool import map_question_to_function  # 问题类型到函数的映射，用于根据问题类型获取对应的处理函数
from question_answer.purpose_type import userPurposeType  # 用户问题类型枚举，定义了各种问题类型


def get_answer(
    question: str, history: List[List | None] = None, question_type=None, image_url=None
) -> Tuple[Any, userPurposeType]:
    """
    根据问题类型调用对应的函数获取结果
    
    Args:
        question (str): 用户问题，即用户输入的文本内容
        history (List[List | None]): 对话历史记录，包含之前的问答记录
        question_type: 问题类型，用于确定使用哪种处理函数
        image_url: 图片URL，当问题涉及图片时提供图片路径或URL
        
    Returns:
        Tuple[Any, userPurposeType]: 包含答案和问题类型的元组，答案的类型根据问题类型而不同
    """
    # 根据问题类型获取对应的处理函数，通过映射函数找到适合处理该问题类型的函数
    function = map_question_to_function(question_type)

    # 构造函数参数，将所有必要参数组成列表传递给处理函数
    args = [question_type, question, history, image_url]
    
    # 调用处理函数获取结果，使用解包操作将参数列表传递给函数
    result = function(*args)

    # 返回处理函数的结果，通常包含答案内容和问题类型
    return result  # 返回结果