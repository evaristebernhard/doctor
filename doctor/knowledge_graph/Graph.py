"""
知识图谱模块
实例化知识图谱对象，提供知识图谱相关的数据访问功能
"""

# 导入项目模块
from config.config import Config  # 配置管理器

# 导入第三方库
from py2neo import Graph, NodeMatcher, RelationshipMatcher, ConnectionUnavailable  # Neo4j图数据库操作库


class GraphDao(object):
    """
    知识图谱数据访问对象类
    负责与Neo4j图数据库进行交互，提供知识图谱相关的数据访问功能
    """

    def __init__(self):
        """
        初始化知识图谱数据访问对象
        """
        # 读取yaml配置
        self.__url = Config.get_instance().get_with_nested_params("database", "neo4j", "url")  # 数据库URL
        self.__username = Config.get_instance().get_with_nested_params("database", "neo4j", "username")  # 用户名
        self.__password = Config.get_instance().get_with_nested_params("database", "neo4j", "password")  # 密码
        self.__connect_graph()  # 连接图数据库

        # 创建节点匹配器
        self.__node_matcher = NodeMatcher(self.__graph) if self.__graph else None

        # 创建关系匹配器
        self.__relationship_matcher = RelationshipMatcher(self.__graph) if self.__graph else None

    def __connect_graph(self):
        """
        连接图数据库
        """
        try:
            # 尝试连接Neo4j图数据库
            self.__graph = Graph(self.__url, auth=(self.__username, self.__password))
        except ConnectionUnavailable:
            # 连接失败时设置为None
            self.__graph = None
            print("无法连接到Neo4j数据库")

    @staticmethod
    def ensure_connection(function):
        """
        确保数据库连接的装饰器
        
        Args:
            function: 被装饰的函数
            
        Returns:
            wrapper: 装饰器包装函数
        """
        def wrapper(*args, **kwargs):
            # 检查数据库连接是否有效
            if not args[0].__graph:
                return None
            return function(*args, **kwargs)

        return wrapper