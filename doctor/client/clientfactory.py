"""
客户端工厂类
向外部构建不同大模型代理的接口，构建完成后返回一个大模型代理
"""

# 导入项目模块
from client.ourAPI.client import OurAPI  # 我们的API客户端
from client.zhipuAPI.client import Image_generate_client, Image_describe_client  # 智谱AI图片客户端
from client.zhipuAPI.client import Video_generate_client  # 智谱AI视频客户端
from env import get_env_value  # 获取环境变量值的函数
from question_answer.purpose_type import userPurposeType  # 用户问题类型枚举


class Clientfactory:
    """
    客户端工厂类
    负责根据需求创建不同类型的大语言模型客户端
    """
    
    # 初始化client字典，使用环境变量中的LLM_BASE_URL
    map_client_dict = {get_env_value("LLM_BASE_URL")}

    def __init__(self):
        """
        初始化客户端工厂
        """
        self._client_url = get_env_value("LLM_BASE_URL")  # 客户端URL
        self._api_key = get_env_value("LLM_API_KEY")  # API密钥

    def get_client(self):
        """
        获取默认的客户端实例
        
        Returns:
            OurAPI: 我们自己的API客户端实例
        """
        return OurAPI()  # 返回我们自己的API客户端实例

    @staticmethod
    def get_special_client(client_type: str):
        """
        根据客户端类型获取特定的客户端实例
        
        Args:
            client_type (str): 客户端类型
            
        Returns:
            对应的客户端实例
        """
        print("get_special_client")  # 打印调试信息
        
        # 根据客户端类型返回对应的客户端实例
        if client_type == userPurposeType.ImageGeneration:
            return Image_generate_client  # 图片生成客户端
        if client_type == userPurposeType.ImageDescribe:
            return Image_describe_client  # 图片描述客户端
        if client_type == userPurposeType.Video:
            return Video_generate_client  # 视频生成客户端

        # 默认情况下使用文本生成模型
        return OurAPI()