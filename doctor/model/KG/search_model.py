"""
知识库实体检索模型类
负责构建和使用Aho-Corasick自动机进行实体检索
"""

# 导入标准库
from typing import Tuple, Optional, List, Dict  # 类型提示

# 导入项目模块
from model.model_base import Modelbase, ModelStatus  # 模型基类和状态枚举
from config.config import Config  # 配置管理器
from model.KG.data_utils import NodeEntities  # 节点实体工具

# 导入第三方库
import ahocorasick as pyahocorasick  # Aho-Corasick字符串匹配算法库


class EntitySearcher(Modelbase):
    """
    实体搜索器类
    继承自Modelbase，使用Aho-Corasick自动机实现高效的实体检索
    """

    def __init__(self, *args, **kwargs):
        """
        初始化实体搜索器
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__(*args, **kwargs)  # 调用父类初始化方法
        self._node_entities = NodeEntities()  # 节点实体对象
        # 从配置中获取搜索键
        self._search_key = Config.get_instance().get_with_nested_params("model", "graph-entity", "search-key")
        self.build()  # 构建模型

    def build(self, *args, **kwargs):
        """
        构建实体搜索模型
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self._model_status = ModelStatus.BUILDING  # 设置模型状态为构建中

        try:
            self._build_model()  # 实际构建模型
        except Exception as e:
            self._model_status = ModelStatus.FAILED  # 构建失败
            return

        self._model_status = ModelStatus.READY  # 构建成功，设置状态为就绪

    def _build_model(self, *args, **kwargs):
        """
        实际构建Aho-Corasick自动机模型
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        """
        automaton = pyahocorasick.Automaton()  # 创建Aho-Corasick自动机

        # 在这里的self._node_entities 包含图数据库的节点信息
        for i, entity in enumerate(self._node_entities()):
            # 从字典 entity 中提取搜索键对应的值
            # values = [entity[fn] for fn in FIELD_NAMES]  # 通过 FIELD_NAMES 获取对应的值
            # value = _Value(*values)
            automaton.add_word(entity[self._search_key], (i, entity))  # 添加词到自动机

        automaton.make_automaton()  # 构建自动机
        self._model = automaton  # 将自动机模型保存到实例变量中

    def search(self, query: str) -> Tuple[Optional[List[Dict]]]:
        """
        在查询文本中搜索实体
        
        Args:
            query (str): 查询文本
            
        Returns:
            Tuple[Optional[List[Dict]]]: 搜索结果元组
        """
        results = []  # 存储搜索结果
        # 遍历自动机匹配结果
        for end_index, (insert_order, original_value) in self._model.iter(query):
            results.append(original_value)  # 添加匹配到的实体

        return results  # 返回搜索结果


# 创建实体搜索器实例
INSTANCE = EntitySearcher()