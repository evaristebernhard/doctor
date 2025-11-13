'''edge-tts调用接口'''
# 导入标准库
import os  # 操作系统接口模块，用于文件和目录操作
import asyncio  # 异步I/O模块，用于异步执行任务

# 导入项目模块
from env import get_app_root  # 获取应用根目录的函数
import hashlib  # 哈希算法模块，用于生成文件名
import edge_tts  # Edge TTS库，用于文本转语音

# 定义音频文件输出目录路径，将音频文件保存在应用根目录下的data/cache/audio文件夹中
_OUTPUT_DIR = os.path.join(get_app_root(), "data/cache/audio")

# 如果文件夹路径不存在，先创建该目录
if not os.path.exists(_OUTPUT_DIR):
    os.makedirs(_OUTPUT_DIR)


def get_file_path(text):
    """
    根据文本生成唯一的音频文件路径
    
    Args:
        text (str): 用于生成文件名的文本
        
    Returns:
        str: 完整的音频文件路径
    """
    # 使用SHA256哈希算法对文本进行哈希，生成唯一的文件名
    file_name = hashlib.sha256(text.encode("utf-8")).hexdigest()
    # 返回完整的文件路径，文件扩展名为.mp3
    return os.path.join(_OUTPUT_DIR, f"{file_name}.mp3")


def audio_generate(text: str, model_name : str) -> str:
    """
    使用Edge TTS生成音频文件
    
    Args:
        text (str): 要转换为语音的文本
        model_name (str): TTS模型名称
        
    Returns:
        str: 生成的音频文件路径
    """
    # 根据文本生成输出文件路径
    _output_file = get_file_path(text)

    # 异步调用_generating函数，使得I/O时可以进行其他操作
    async def _generating() -> None:
        # 创建Communicate对象，传入文本和模型名称
        communicate = edge_tts.Communicate(text, model_name)
        # 异步保存音频文件
        await communicate.save(_output_file)

    # 运行异步函数
    asyncio.run(_generating())

    # 返回生成的音频文件路径
    return _output_file