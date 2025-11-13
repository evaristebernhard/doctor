"""
问答处理工具函数模块
存放处理不同问答类型的工具函数，是项目的核心文件
"""

# 导入标准库
import base64  # Base64编码解码，用于图片编码
from typing import Callable, List, Dict, Tuple  # 类型提示，用于函数和变量的类型注解
import time  # 时间相关功能，用于视频生成时的轮询等待
import json  # JSON处理，用于解析生成的PPT和Word内容
from pathlib import Path  # 路径处理，用于检查文件路径是否存在

# 导入项目模块
from client.clientfactory import Clientfactory  # 客户端工厂，用于创建与AI模型通信的客户端
from question_answer.purpose_type import userPurposeType  # 用户问题类型枚举，定义了各种问题类型
from ppt_docx.ppt_generation import generate as generate_ppt  # PPT生成函数，用于创建PPT文件
from ppt_docx.ppt_content import generate_ppt_content  # PPT内容生成函数，用于生成PPT内容文本
from ppt_docx.docx_generation import generate_docx_content as generate_docx  # Word文档生成函数，用于创建Word文件
from ppt_docx.docx_content import generate_docx_content  # Word内容生成函数，用于生成Word内容文本
from rag import rag_chain  # RAG链，用于检索增强生成
from audio.audio_extract import (  # 音频相关处理函数
    extract_text,  # 从问题中提取需要转换为语音的文本
    extract_language,  # 从问题中提取目标语言类型
    extract_gender,  # 从问题中提取目标性别类型
    get_tts_model_name,  # 获取TTS模型名称
)
from audio.audio_generate import audio_generate  # 音频生成函数，用于生成音频文件
from model.KG.search_service import search  # 知识图谱搜索服务，用于搜索实体
from Internet.Internet_chain import InternetSearchChain  # 联网搜索链，用于执行网络搜索
from knowledge_graph.Graph import GraphDao  # 知识图谱数据访问对象，用于查询知识图谱
from config.config import Config  # 配置管理器，用于获取配置信息
from env import get_env_value  # 获取环境变量值的函数，用于获取模型名称等配置

# 创建知识图谱数据访问对象实例，用于后续查询知识图谱
_dao = GraphDao()


def is_file_path(path: str) -> bool:
    """
    判断给定路径是否为有效文件路径
    
    Args:
        path (str): 文件路径
        
    Returns:
        bool: 如果路径存在且为文件则返回True，否则返回False
    """
    # 使用Path对象检查路径是否存在
    return Path(path).exists()  # 检查路径是否存在


def relation_tool(entities: List[Dict] | None) -> str | None:
    """
    处理实体关系，从知识图谱中提取实体间的关系信息
    
    Args:
        entities (List[Dict] | None): 实体列表
        
    Returns:
        str | None: 关系信息字符串，如果没有实体则返回None
    """
    # 如果没有实体，直接返回None
    if not entities or len(entities) == 0:
        return None

    relationships = set()  # 使用集合来避免重复关系
    relationship_match = []  # 存储匹配到的关系

    # 从配置中获取搜索键，用于获取实体的名称字段
    searchKey = Config.get_instance().get_with_nested_params("model", "graph-entity", "search-key")
    
    # 遍历每个实体并查询与其他实体的关系
    for entity in entities:
        entity_name = entity[searchKey]  # 获取实体名称
        # 添加实体属性关系，将实体的每个属性构造成"实体名 属性名: 属性值"的形式
        for k, v in entity.items():
            relationships.add(f"{entity_name} {k}: {v}")

        # 查询每个实体与其他实体的关系a-r-b，查找当前实体相关的所有关系
        relationship_match.append(_dao.query_relationship_by_name(entity_name))
        
    # 抽取并记录每个实体与其他实体的关系
    for i in range(len(relationship_match)):
        for record in relationship_match[i]:
            # 获取起始节点和结束节点的名称
            start_name = record["r"].start_node[searchKey]  # 获取关系起始节点的名称
            end_name = record["r"].end_node[searchKey]  # 获取关系结束节点的名称

            # 获取关系类型
            rel = type(record["r"]).__name__  # 获取关系名称，比如 CAUSES

            # 构建关系字符串并添加到集合，确保不会重复添加
            relationships.add(f"{start_name} {rel} {end_name}")

    # 返回关系集合的内容
    if relationships:
        # 用分号连接所有关系，形成一个字符串
        return "；".join(relationships)  # 用分号连接所有关系
    else:
        return None


def check_entity(question: str) -> List[Dict]:
    """
    检查问题中的实体
    
    Args:
        question (str): 用户问题
        
    Returns:
        List[Dict]: 实体列表
    """
    # 调用搜索函数查找问题中的实体
    code, result = search(question)  # 调用搜索函数
    # 如果搜索成功，返回实体列表
    if code == 0:  # 搜索成功
        return result
    else:  # 搜索失败
        return None


def KG_tool(
    question_type: userPurposeType,
    question: str,
    history: List[List | None] = None,
    image_url=None,
):
    """
    知识图谱工具函数
    
    Args:
        question_type (userPurposeType): 问题类型
        question (str): 用户问题
        history (List[List | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含响应和问题类型的元组
    """
    kg_info = None  # 初始化知识图谱信息为空
    try:
        # 此处在使用知识图谱之前，需先检查问题的实体
        entities = check_entity(question)  # 检查问题中的实体
        kg_info = relation_tool(entities)  # 获取实体间的关系信息
    except:
        pass

    # 如果获取到知识图谱信息，则将其添加到问题中
    if kg_info is not None:
        # 打印知识图谱信息到控制台
        print(f"KG_tool: \n {kg_info}")
        # 将知识图谱信息附加到问题中，引导模型基于知识图谱信息回答
        question = f"{question}\n从知识图谱中检索到的信息如下{kg_info}\n请你基于知识图谱的信息去回答,并给出知识图谱检索到的信息"

    # 调用客户端获取响应，使用流式方式与AI模型交互
    response = Clientfactory().get_client().chat_with_ai_stream(question, history)
    # 返回响应和问题类型的元组
    return (response, question_type)


def process_text_tool(
    question_type: userPurposeType,
    question: str,
    history: List[List | None] = None,
    image_url=None,
):
    """
    处理文本问题的函数
    
    Args:
        question_type (userPurposeType): 问题类型
        question (str): 用户问题
        history (List[List | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含响应和问题类型的元组
    """
    # 调用客户端获取响应，使用流式方式与AI模型交互
    response = Clientfactory().get_client().chat_with_ai_stream(question, history)
    # 返回响应和问题类型的元组
    return (response, question_type)


def RAG_tool(
    question_type: userPurposeType,
    question: str,
    history: List[List | None] = None,
    image_url=None,
):
    """
    处理RAG问题的函数
    
    Args:
        question_type (userPurposeType): 问题类型
        question (str): 用户问题
        history (List[List | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含响应和问题类型的元组
    """
    # 先利用question去检索得到docs，调用RAG链处理问题
    response = rag_chain.invoke(question, history)
    # 返回响应和问题类型的元组
    return (response, question_type)


def process_images_tool(question_type, question, history, image_url=None):
    """
    处理图片生成问题的函数
    
    Args:
        question_type: 问题类型
        question (str): 用户问题
        history: 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含图片URL和问题类型的元组
    """
    # 获取特殊客户端，用于图片生成
    client = Clientfactory.get_special_client(client_type=question_type)
    
    # 调用图片生成API，使用指定的模型和提示词生成图片
    response = client.images.generations(
        model=get_env_value("IMAGE_GENERATE_MODEL"),  # 填写需要调用的模型编码，从环境变量获取
        prompt=question,  # 使用用户问题作为图片生成的提示词
    )
    # 打印生成的图片URL到控制台
    print(response.data[0].url)  # 打印生成的图片URL
    # 返回生成的图片URL和问题类型的元组
    return (response.data[0].url, question_type)


def process_image_describe_tool(question_type, question, history, image_url=None):
    """
    处理图片描述问题的函数
    
    Args:
        question_type: 问题类型
        question (str): 用户问题
        history: 对话历史
        image_url: 图片URL列表
        
    Returns:
        tuple: 包含描述内容和问题类型的元组
    """
    # 如果是默认问候语，替换为图片描述提示
    if question == "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'请问您有什么想了解的，我将尽力为您服务'":
        # 替换为更合适的图片描述提示
        question = "描述这个图片，说明这个图片的主要内容"
    
    image_bases = []  # 存储图片的base64编码
    # 遍历所有图片URL
    for img_url in image_url:
        # 如果是本地文件路径
        if is_file_path(img_url):  # 如果是本地文件路径
            # 以二进制模式打开图片文件
            with open(img_url, "rb") as img_file:
                # 将图片编码为base64字符串
                image_base = base64.b64encode(img_file.read()).decode("utf-8")
                # 添加到图片编码列表
                image_bases.append(image_base)
        else:  # 如果是URL
            # 直接添加URL到列表
            image_bases.append(img_url)

    # 构建 messages 内容
    message_content = []  # 初始化消息内容列表
    # 遍历所有图片编码
    for image_base in image_bases:
        # 为每张图片添加图片URL内容
        message_content.append({"type": "image_url", "image_url": {"url": image_base}})
    # 添加问题的文本内容到最后
    message_content.append({"type": "text", "text": question})

    # 获取特殊客户端，用于图片描述
    client = Clientfactory.get_special_client(client_type=question_type)
    
    # 发送请求到AI模型
    response = client.chat.completions.create(
        model=get_env_value("IMAGE_DESCRIBE_MODEL"),  # 从环境变量获取图片描述模型
        messages=[
            {
                "role": "user",  # 用户角色
                "content": message_content,  # 包含图片和文本的消息内容
            }
        ],
    )
    # 返回模型的响应内容和问题类型
    return (response.choices[0].message.content, question_type)


def process_ppt_tool(
    question_type, question: str, history: List[List[str] | None] = None, image_url=None
) -> Tuple[Tuple[str, str], userPurposeType]:
    """
    处理PPT生成问题的函数
    
    Args:
        question_type: 问题类型
        question (str): 用户问题
        history (List[List[str] | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        Tuple[Tuple[str, str], userPurposeType]: 包含PPT文件路径和问题类型的元组
    """
    # 生成PPT内容，调用专门的函数生成PPT内容文本
    raw_text: str = generate_ppt_content(question, history)
    try:
        # 解析JSON格式的内容，将生成的文本解析为JSON对象
        ppt_content = json.loads(raw_text)
    except:
        # 如果解析失败，返回None和PPT问题类型
        return None, userPurposeType.PPT
    
    # 生成PPT文件，使用解析后的内容生成实际的PPT文件
    ppt_file: str = generate_ppt(
        ppt_content
    )  # 这个语句由于模型能力有限，可能不会按照格式输出，会导致冲突，要用str正则语句修改，删除一些异常符号，否则会出bug
    # 返回包含PPT文件路径和"ppt"标识的元组，以及问题类型
    return (ppt_file, "ppt"), userPurposeType.PPT


def process_docx_tool(
    question_type, question: str, history: List[List[str] | None] = None, image_url=None
) -> Tuple[Tuple[str, str], userPurposeType]:
    """
    处理Word文档生成问题的函数
    
    Args:
        question_type: 问题类型
        question (str): 用户问题
        history (List[List[str] | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        Tuple[Tuple[str, str], userPurposeType]: 包含Word文档路径和问题类型的元组
    """
    # 先生成word的文案，调用专门的函数生成Word内容文本
    raw_text: str = generate_docx_content(question, history)
    try:
        # 解析JSON格式的内容，将生成的文本解析为JSON对象
        docx_content = json.loads(raw_text)
    except:
        # 如果解析失败，返回None和Word问题类型
        return None, userPurposeType.Docx
    
    # 生成Word文档，使用解析后的内容生成实际的Word文件
    docx_file: str = generate_docx(docx_content)
    # 返回包含Word文档路径和"docx"标识的元组，以及问题类型
    return (docx_file, "docx"), userPurposeType.Docx


def process_text_video_tool(question_type, question, history, image_url=None):
    """
    处理视频生成问题的函数
    
    Args:
        question_type: 问题类型
        question (str): 用户问题
        history: 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含视频URL和问题类型的元组
    """
    # 获取特殊客户端，用于视频生成
    client = Clientfactory.get_special_client(client_type=question_type)
    try:
        # 调用视频生成API，使用指定的模型和提示词生成视频
        chatRequest = client.videos.generations(
            model=get_env_value("VIDEO_GENERATE_MODEL"),  # 从环境变量获取视频生成模型
            prompt=question,  # 使用用户问题作为视频生成的提示词
        )
        # 打印视频生成请求信息到控制台
        print(chatRequest)

        start_time = time.time()  # 开始计时，用于超时控制
        video_url = None  # 初始化视频URL为空
        timeout = 120  # 超时时间2分钟
        # 轮询检查视频生成状态
        while time.time() - start_time < timeout:
            # 请求视频生成结果
            print(chatRequest.id)  # 打印任务ID
            # 根据任务ID获取视频生成结果
            response = client.videos.retrieve_videos_result(id=chatRequest.id)

            # 检查任务状态是否成功且有视频结果
            if response.task_status == "SUCCESS" and response.video_result:
                # 获取视频URL
                video_url = response.video_result[0].url
                # 打印视频URL到控制台
                print("视频URL:", video_url)
                # 返回包含视频URL和问题类型的元组
                return ((video_url, "视频"), question_type)
            else:
                # 打印任务未完成提示
                print("任务未完成，请等待...")

            # 等待一段时间再请求，每次请求后等待2秒再继续
            time.sleep(2)  # 每次请求后等待2秒再继续

    except:
        # 如果出现异常，返回None和问题类型
        return (None, question_type)


def process_audio_tool(
    question_type: userPurposeType,
    question: str,
    history: List[List | None] = None,
    image_url=None,
):
    """
    处理音频生成问题的函数
    
    Args:
        question_type (userPurposeType): 问题类型
        question (str): 用户问题
        history (List[List | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含音频文件路径和问题类型的元组
    """
    # 先让大语言模型生成需要转换成语音的文字
    text = extract_text(question, history)  # 从问题和历史中提取需要转语音的文本
    # 判断需要生成哪种语言（东北、陕西、粤...）
    lang = extract_language(question)  # 从问题中提取目标语言
    # 判断需要生成男声还是女声
    gender = extract_gender(question)  # 从问题中提取目标性别
    # 上面三步均与大语言模型进行交互

    # 选择用于生成的模型
    model_name, success = get_tts_model_name(lang=lang, gender=gender)  # 获取TTS模型名称
    # 如果成功获取模型名称
    if success:
        # 生成音频文件
        audio_file = audio_generate(text, model_name)
    else:
        # 如果获取模型名称失败，使用默认模型并添加提示信息
        audio_file = audio_generate(
            "由于目标语言包缺失，我将用普通话回复您。" + text, model_name
        )
    # 返回包含音频文件路径和问题类型的元组
    return ((audio_file, "audio"), question_type)


def process_InternetSearch_tool(
    question_type: userPurposeType,
    question: str,
    history: List[List | None] = None,
    image_url=None,
):
    """
    处理联网搜索问题的函数
    
    Args:
        question_type (userPurposeType): 问题类型
        question (str): 用户问题
        history (List[List | None]): 对话历史
        image_url: 图片URL
        
    Returns:
        tuple: 包含响应、链接和成功状态的元组
    """
    # 调用联网搜索链执行搜索
    response, links, success = InternetSearchChain(question, history)
    # 返回包含响应、问题类型、链接和成功状态的元组
    return (response, question_type, links, success)


# 问题类型到处理函数的映射，将每种问题类型映射到对应的处理函数
QUESTION_TO_FUNCTION = {
    userPurposeType.text: process_text_tool,  # 文本问题映射到文本处理函数
    userPurposeType.RAG: RAG_tool,  # RAG问题映射到RAG处理函数
    userPurposeType.ImageGeneration: process_images_tool,  # 图片生成问题映射到图片生成处理函数
    userPurposeType.Audio: process_audio_tool,  # 音频问题映射到音频处理函数
    userPurposeType.InternetSearch: process_InternetSearch_tool,  # 联网搜索问题映射到联网搜索处理函数
    userPurposeType.ImageDescribe: process_image_describe_tool,  # 图片描述问题映射到图片描述处理函数
    userPurposeType.PPT: process_ppt_tool,  # PPT问题映射到PPT处理函数
    userPurposeType.Docx: process_docx_tool,  # Word问题映射到Word处理函数
    userPurposeType.Video: process_text_video_tool,  # 视频问题映射到视频处理函数
    userPurposeType.KnowledgeGraph: KG_tool,  # 知识图谱问题映射到知识图谱处理函数
}


def map_question_to_function(purpose: userPurposeType) -> Callable:
    """
    根据用户不同的意图选择不同的函数
    
    Args:
        purpose (userPurposeType): 用户意图类型
        
    Returns:
        Callable: 对应的处理函数
        
    Raises:
        ValueError: 当没有找到意图对应的函数时抛出
    """
    # 检查意图类型是否在映射字典中
    if purpose in QUESTION_TO_FUNCTION:
        # 如果找到，返回对应的处理函数
        return QUESTION_TO_FUNCTION[purpose]
    else:
        # 如果未找到，抛出异常
        raise ValueError("没有找到意图对应的函数")