"""
配置文件加载模块
负责加载和管理应用的配置信息
"""

# 导入标准库
import threading  # 线程相关功能
from functools import lru_cache  # LRU缓存装饰器

# 导入第三方库
import yaml  # YAML文件解析库
import os  # 操作系统相关功能

# 导入项目模块
from env import get_app_root  # 获取应用根目录的函数


class Config(object):
    """
    配置管理类
    使用单例模式和线程锁确保配置实例的唯一性和线程安全
    """
    
    # 类变量初始化
    __instance = None  # 单例实例
    __lock = threading.Lock()  # 线程锁

    def __init__(self):
        """
        初始化配置对象
        """
        self._config = None  # 配置数据

    @classmethod
    def get_instance(cls):
        """
        获取配置管理器的单例实例
        
        Returns:
            Config: 配置管理器实例
        """
        with cls.__lock:  # 使用线程锁确保线程安全
            if cls.__instance is None:
                cls.__instance = cls._load_config()  # 加载配置
            return cls.__instance  # 返回实例

    @classmethod
    def _load_config(cls):
        """
        加载配置文件
        
        Returns:
            Config: 配置实例
        """
        instance = Config()  # 创建配置实例
        root = get_app_root()  # 获取应用根目录
        env = os.environ.get("PY_ENVIRONMENT")  # 获取环境变量
        print(env)  # 打印环境变量
        
        # 打开并加载配置文件
        with open(os.path.join(root, "config", f"config-{env}.yaml"), "r", encoding="utf-8") as f:
            setattr(instance, "_config", yaml.load(f, Loader=yaml.FullLoader))  # 设置配置数据

        return instance  # 返回配置实例

    @lru_cache(maxsize=128)
    def get_with_nested_params(self, *params):
        """
        根据嵌套参数获取配置值
        
        Args:
            *params: 嵌套的配置键名
            
        Returns:
            Any: 配置值
            
        Raises:
            AssertionError: 当配置未加载时抛出
            KeyError: 当配置键不存在时抛出
        """
        assert self._config is not None, "please load config first"  # 确保配置已加载
        conf = self._config  # 获取配置数据
        
        # 遍历参数路径查找配置值
        for param in params:
            if param in conf:
                conf = conf[param]  # 进入下一级配置
            else:
                raise KeyError(f"{param} not found in config")  # 抛出键不存在异常

        return conf  # 返回配置值


if __name__ == "__main__":
    # 测试代码
    print(get_app_root())  # 打印应用根目录