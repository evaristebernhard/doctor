"""
智谱AI客户端实现
用于图片生成、图片描述和视频生成等功能
"""

# 导入第三方库
from zhipuai import ZhipuAI  # 智谱AI客户端

# 导入项目模块
from env import get_env_value  # 获取环境变量值的函数

# 创建图片生成客户端实例
Image_generate_client = ZhipuAI(api_key=get_env_value("IMAGE_GENERATE_API"))

# 创建图片描述客户端实例
Image_describe_client = ZhipuAI(api_key=get_env_value("IMAGE_DESCRIBE_API"))

# 创建视频生成客户端实例
Video_generate_client = ZhipuAI(api_key=get_env_value("VIDEO_GENERATE_API"))