"""
模型基类模块
定义可能用到的模型状态枚举和模型基类
"""

# 导入标准库
from enum import Enum  # 枚举类


class ModelStatus(str, Enum):
    """
    模型状态枚举类
    定义模型可能的各种状态
    """
    INITIAL = "initial"  # 初始状态
    BUILDING = "building"  # 构建中
    READY = "ready"  # 就绪
    FAILED = "failed"  # 失败
    INVALID = "invalid"  # 无效
    DELETED = "deleted"  # 已删除
    UNKNOWN = "unknown"  # 未知


class Modelbase(object):
    """
    模型基类
    所有模型类的基类，提供通用的模型状态管理和用户ID管理功能
    """
    
    def __init__(self, id=None, *args, **kwargs):
        """
        初始化模型基类
        
        Args:
            id: 用户ID
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._model_status = ModelStatus.FAILED  # 初始化模型状态为失败
        self._user_id = id  # 设置用户ID

    @property
    def model_status(self):
        """
        获取模型状态
        
        Returns:
            ModelStatus: 当前模型状态
        """
        return self._model_status

    @property
    def user_id(self):
        """
        获取用户ID
        
        Returns:
            用户ID
        """
        return self._user_id

    def set_user_id(self, new_id):
        """
        修改用户ID
        
        Args:
            new_id: 新的用户ID
        """
        self._user_id = new_id