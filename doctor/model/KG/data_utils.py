"""
知识图谱数据工具模块
提供与知识图谱节点实体相关的数据处理功能
"""

# 导入标准库
from dataclasses import dataclass, field  # 数据类相关功能
from typing import List, Dict  # 类型提示

# 导入项目模块
from config.config import Config  # 配置管理器
from knowledge_graph.Graph import GraphDao  # 知识图谱数据访问对象


@dataclass
class NodeEntities(object):
    """
    节点实体类
    负责与Graph类交互，获取节点信息
    """
    
    # 图数据库访问对象，默认使用GraphDao工厂方法创建
    dao: GraphDao = field(default_factory=lambda: GraphDao(), init=True, compare=False)

    def get_entities_iterator(self) -> List[Dict]:
        """
        获取节点实体迭代器
        
        Returns:
            List[Dict]: 节点实体列表，每个实体是一个字典
        """
        # 定义你要查询的标签类型，比如疾病、症状、药物等
        labels_to_query = Config.get_instance().get_with_nested_params("database", "neo4j", "node-label")

        node_list = []  # 存储节点列表

        # 动态查询不同标签类型的节点
        for label in labels_to_query:
            # 查询带有特定标签的节点
            nodes = self.dao.query_node(label)

            for node in nodes:
                # 根据节点的标签和属性创建字典
                node_dict = {
                    'label': label,  # 使用当前查询的标签
                    **dict(node)  # 解包节点的属性
                }
                node_list.append(node_dict)  # 添加到节点列表

        return node_list  # 返回节点列表
        
    def __call__(self, *args, **kwargs):
        """
        使对象可调用，返回节点实体迭代器
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            List[Dict]: 节点实体列表
        """
        return self.get_entities_iterator()  # 调用获取实体迭代器方法