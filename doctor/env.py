"""
环境配置文件
封装读取.env文件的接口
"""

# 导入标准库
import os  # 操作系统相关功能

# 导入第三方库
from dotenv import load_dotenv, dotenv_values  # 环境变量加载库

def get_app_root():
    """
    获取应用根目录路径
    
    Returns:
        str: 当前工作目录路径
    """
    return os.getcwd()  # 返回当前工作目录


def get_env_value(key):
    """
    获取环境变量的值
    
    Args:
        key (str): 环境变量键名
        
    Returns:
        str or None: 环境变量的值，如果不存在则返回None
    """
    return os.environ.get(key)  # 从环境变量中获取指定键的值


# 加载环境变量
load_dotenv(".env", override=False)  # 从.env文件加载环境变量
print(f"setting environment variables: {dotenv_values('.env')}")  # 打印加载的环境变量


if __name__ == '__main__':
    # 测试环境变量读取功能
    print("app root is: " + get_app_root())  # 打印应用根目录
    print("your API key is: " + get_env_value('LLM_API_KEY'))  # 打印API密钥
    print("your url is: " + get_env_value('MODEL_NAME'))  # 打印模型名称