
"""
项目入口文件，构建Gradio界面，处理多模态信息
"""

# 导入标准库
import base64  # 用于图片编码
import os  # 用于系统相关操作
from typing import List, Tuple, Any  # 类型提示

# 导入第三方库
import gradio as gr  # Gradio界面库
from icecream import ic  # 调试打印工具
from PIL import Image  # 图片处理库
import PyPDF2  # PDF处理库
import chardet  # 字符编码检测库
import mimetypes  # MIME类型处理库
from docx import Document  # Word文档处理库
from pydub import AudioSegment  # 音频处理库
import speech_recognition as sr  # 语音识别库
from opencc import OpenCC  # 中文繁简转换库

# 导入项目模块
from question_answer.answer import get_answer  # 获取答案的函数
from question_answer.question_parser import parse_question  # 解析问题类型的函数
from question_answer.function_tool import process_image_describe_tool  # 图片描述工具
from question_answer.purpose_type import userPurposeType  # 用户问题类型枚举

# 导入音频相关模块
from audio.audio_generate import audio_generate  # 音频生成函数

# 设置头像路径
AVATAR = ("resource/user.png", "resource/bot.jpg")

# 设置环境变量以解决多线程问题
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def convert_to_simplified(text: str) -> str:
    """
    将繁体中文转换为简体中文
    
    Args:
        text (str): 输入的繁体中文文本
        
    Returns:
        str: 转换后的简体中文文本
    """
    converter = OpenCC("t2s")  # 创建繁简转换器实例，使用t2s模式（繁体转简体）
    return converter.convert(text)  # 执行繁简转换并返回结果


def convert_audio_to_wav(audio_file_path: str) -> str:
    """
    将音频文件转换为WAV格式
    
    Args:
        audio_file_path (str): 原始音频文件路径
        
    Returns:
        str: 转换后的WAV文件路径
    """
    audio = AudioSegment.from_file(audio_file_path)  # 使用pydub加载音频文件
    wav_file_path = audio_file_path.rsplit(".", 1)[0] + ".wav"  # 构造WAV文件路径，替换文件扩展名为.wav
    audio.export(wav_file_path, format="wav")  # 将音频导出为WAV格式
    return wav_file_path  # 返回转换后的WAV文件路径


def audio_to_text(audio_file_path: str) -> str:
    """
    将音频文件转换为文本
    
    Args:
        audio_file_path (str): 音频文件路径
        
    Returns:
        str: 识别出的文本内容
    """
    # 如果不是WAV格式，先转换为WAV格式
    if not audio_file_path.endswith(".wav"):
        audio_file_path = convert_audio_to_wav(audio_file_path)

    recognizer = sr.Recognizer()  # 创建语音识别器实例
    with sr.AudioFile(audio_file_path) as source:  # 打开音频文件
        audio_data = recognizer.record(source)  # 从音频文件中读取音频数据
        text = recognizer.recognize_whisper(audio_data, language="zh")  # 使用Whisper模型识别中文语音
        text_simplified = convert_to_simplified(text)  # 将识别结果转换为简体中文
    return text_simplified  # 返回识别出的简体中文文本


def pdf_to_str(pdf_file: str) -> str:
    """
    将PDF文件转换为文本字符串
    
    Args:
        pdf_file (str): PDF文件路径
        
    Returns:
        str: 提取的文本内容
    """
    reader = PyPDF2.PdfReader(pdf_file)  # 创建PDF读取器实例
    text = ""  # 初始化空字符串用于存储提取的文本
    for page in reader.pages:  # 遍历PDF中的每一页
        text += page.extract_text()  # 提取当前页的文本并添加到结果中
    return text  # 返回提取的所有文本


def docx_to_str(file_path: str) -> str:
    """
    将Word文档转换为文本字符串
    
    Args:
        file_path (str): Word文档路径
        
    Returns:
        str: 提取的文本内容
    """
    doc = Document(file_path)  # 打开Word文档
    text = [paragraph.text for paragraph in doc.paragraphs]  # 提取所有段落的文本
    return "\n".join(text)  # 用换行符连接所有段落文本并返回


def text_file_to_str(text_file: str) -> str:
    """
    读取文本文件内容
    
    Args:
        text_file (str): 文本文件路径
        
    Returns:
        str: 文件内容
    """
    with open(text_file, "rb") as file:  # 以二进制模式打开文件用于检测编码
        raw_data = file.read()  # 读取文件的原始数据
        encoding = chardet.detect(raw_data)["encoding"]  # 使用chardet库检测文件编码
    with open(text_file, "r", encoding=encoding) as file:  # 以检测到的编码重新打开文件
        return file.read()  # 读取并返回文件内容


def image_to_base64(image_path: str) -> str:
    """
    将图片转换为base64编码
    
    Args:
        image_path (str): 图片文件路径
        
    Returns:
        str: base64编码的图片数据
    """
    img = Image.open(image_path)  # 打开图片文件
    max_width = 800  # 设置图片最大宽度为800像素
    if img.width > max_width:  # 如果图片宽度超过最大宽度
        ratio = max_width / img.width  # 计算缩放比例
        new_height = int(img.height * ratio)  # 根据比例计算新的高度
        img = img.resize((max_width, new_height))  # 调整图片尺寸
    
    temp_path = "temp_img.jpg"  # 定义临时文件路径
    img.save(temp_path)  # 保存调整尺寸后的图片到临时文件
    
    with open(temp_path, "rb") as f:  # 以二进制模式打开临时图片文件
        encoded_string = base64.b64encode(f.read()).decode("utf-8")  # 将图片编码为base64字符串
    
    os.remove(temp_path)  # 删除临时文件
    return encoded_string  # 返回base64编码的图片数据


def grodio_view(chatbot: List, chat_input: dict) -> List:
    """
    处理文本聊天界面的函数
    
    Args:
        chatbot (List): 聊天历史记录
        chat_input (dict): 用户输入内容，包括文本和文件
        
    Yields:
        List: 更新后的聊天记录
    """
    # 获取用户输入的文本
    user_message = chat_input["text"]
    # 初始化机器人回复
    bot_response = "loading..."
    # 将用户消息和初始回复添加到聊天记录
    chatbot.append([user_message, bot_response])
    yield chatbot  # 返回更新后的聊天记录

    # 处理上传的文件
    files = chat_input["files"]
    audios = []  # 音频文件列表
    images = []  # 图片文件列表
    pdfs = []  # PDF文件列表
    docxs = []  # Word文档列表
    texts = []  # 文本文件列表

    # 分类处理不同类型的文件
    for file in files:
        file_type, _ = mimetypes.guess_type(file)  # 获取文件MIME类型
        if file_type.startswith("audio/"):  # 音频文件
            audios.append(file)
        elif file_type.startswith("image/"):  # 图片文件
            images.append(file)
        elif file_type.startswith("application/pdf"):  # PDF文件
            pdfs.append(file)
        elif file_type.startswith(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):  # Word文档
            docxs.append(file)
        elif file_type.startswith("text/"):  # 文本文件
            texts.append(file)
        else:  # 不支持的文件类型
            user_message += "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'该文件为不支持的文件类型'"
            print(f"Unknown file type: {file_type}")

    # 处理图片文件
    if images:
        image_url = images
        image_base64 = [image_to_base64(image) for image in image_url]  # 转换为base64
        for image in image_base64:
            # 在聊天界面中显示图片
            chatbot[-1][0] += f"""
                <div>
                    <img src="data:image/png;base64,{image}" alt="Uploaded Image" style="max-width: 100%; height: auto; border-radius: 8px; margin: 8px 0;" />
                </div>
                """
            yield chatbot
    else:
        image_url = None

    # 解析问题类型
    question_type = parse_question(user_message, image_url)
    ic(question_type)  # 调试输出问题类型

    # 处理音频文件
    if audios:
        for i, audio in enumerate(audios):
            audio_message = audio_to_text(audio)  # 音频转文本
            if not audio_message:  # 音频识别失败
                user_message += "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'音频识别失败，请稍后再试'"
            elif "作曲" in audio_message:  # 识别为音乐
                user_message += "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'不好意思，我无法理解音乐'"
            else:  # 正常识别
                user_message += f"音频{i + 1}内容：{audio_message}"

    # 处理PDF文件
    if pdfs:
        for i, pdf in enumerate(pdfs):
            user_message += f"PDF{i + 1}内容：{pdf_to_str(pdf)}"  # 添加PDF内容

    # 处理Word文档
    if docxs:
        for i, docx in enumerate(docxs):
            user_message += f"DOCX{i + 1}内容：{docx_to_str(docx)}"  # 添加Word内容

    # 处理文本文件
    if texts:
        for i, text in enumerate(texts):
            user_message += f"文本{i + 1}内容：{text_file_to_str(text)}"  # 添加文本内容

    # 如果没有用户消息，设置默认消息
    if not user_message:
        user_message = "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'请问您有什么想了解的，我将尽力为您服务'"
    
    # 获取答案
    answer = get_answer(user_message, chatbot, question_type, image_url)
    bot_response = ""  # 初始化机器人回复

    # 处理不同类型的回复
    if (
            answer[1] == userPurposeType.text
            or answer[1] == userPurposeType.RAG
            or answer[1] == userPurposeType.KnowledgeGraph
    ):
        # 处理文本回复
        for chunk in answer[0]:
            bot_response += chunk.choices[0].delta.content or ""
            chatbot[-1][1] = bot_response
            yield chatbot

    if answer[1] == userPurposeType.ImageGeneration:
        # 处理图片生成回复
        image_url = answer[0]
        describe = process_image_describe_tool(
            question_type=userPurposeType.ImageDescribe,
            question="描述这个图片，不要识别'AI生成'",
            history="",
            image_url=[image_url],
        )
        combined_message = f"""
            **生成的图片:**
            ![Generated Image]({image_url})
            {describe[0]}
            """
        chatbot[-1][1] = combined_message
        yield chatbot

    if answer[1] == userPurposeType.ImageDescribe:
        # 处理图片描述回复
        for i in range(len(answer[0])):
            bot_response += answer[0][i:i + 1]
            chatbot[-1][1] = bot_response
            yield chatbot

    if answer[1] == userPurposeType.Video:
        # 处理视频回复
        chatbot[-1][1] = answer[0] if answer[0] else "抱歉，视频生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.PPT:
        # 处理PPT回复
        chatbot[-1][1] = answer[0] if answer[0] else "抱歉，PPT生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.Docx:
        # 处理Word文档回复
        chatbot[-1][1] = answer[0] if answer[0] else "抱歉，文档生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.Audio:
        # 处理音频回复
        chatbot[-1][1] = answer[0] if answer[0] else "抱歉，音频生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.InternetSearch:
        # 处理网络搜索回复
        if not answer[3]:
            output_message = "由于网络问题，访问互联网失败，下面由我根据现有知识给出回答："
        else:
            links = "\n".join(f"[{title}]({link})" for link, title in answer[2].items())
            output_message = f"参考资料：{links}\n"
        for i in range(len(output_message)):
            bot_response = output_message[:i + 1]
            chatbot[-1][1] = bot_response
            yield chatbot
        for chunk in answer[0]:
            bot_response += chunk.choices[0].delta.content or ""
            chatbot[-1][1] = bot_response
            yield chatbot


def gradio_audio_view(chatbot: List, audio_input: str, lang_choice: str) -> List:
    """
    处理语音聊天界面的函数
    
    Args:
        chatbot (List): 聊天历史记录
        audio_input (str): 音频输入文件路径
        lang_choice (str): 选择的语言类型
        
    Yields:
        List: 更新后的聊天记录
    """
    # 处理用户音频输入
    user_message = (audio_input, "audio") if audio_input else ""
    bot_response = "loading..."  # 初始化机器人回复
    chatbot.append([user_message, bot_response])  # 添加到聊天记录
    yield chatbot

    # 音频转文本
    audio_message = audio_to_text(audio_input) if audio_input else "无音频"
    chatbot[-1][0] = audio_message  # 更新用户消息

    user_message = ""  # 重置用户消息
    if audio_message == "无音频":  # 没有音频输入
        user_message += "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'欢迎与我对话，我将用语音回答您'"
    elif not audio_message:  # 音频识别失败
        user_message += "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'音频识别失败，请稍后再试'"
    elif "作曲 作曲" in audio_message:  # 识别为音乐
        user_message += "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'不好意思，我无法理解音乐'"
    else:  # 正常识别
        user_message += audio_message

    # 如果没有用户消息，设置默认消息
    if not user_message:
        user_message = "请你将下面的句子修饰后输出，不要包含额外的文字，句子:'请问您有什么想了解的，我将尽力为您服务'"

    # 解析问题类型
    question_type = parse_question(user_message)
    ic(question_type)  # 调试输出问题类型
    answer = get_answer(user_message, chatbot, question_type)  # 获取答案
    bot_response = ""  # 初始化机器人回复

    # 处理不同类型的回复
    if (
            answer[1] == userPurposeType.text
            or answer[1] == userPurposeType.RAG
            or answer[1] == userPurposeType.KnowledgeGraph
    ):
        # 处理文本回复
        for chunk in answer[0]:
            bot_response += chunk.choices[0].delta.content or ""
        try:
            # 根据选择的方言生成对应语音
            model_map = {
                "普通话（男）": "zh-CN-YunxiNeural",
                "普通话（女）": "zh-CN-XiaoxiaoNeural",
                "陕西话": "zh-CN-shaanxi-XiaoniNeural",
                "东北话": "zh-CN-liaoning-XiaobeiNeural",
                "粤语（男）": "zh-HK-WanLungNeural",
                "粤语（女）": "zh-HK-HiuMaanNeural"
            }
            # 生成音频并返回
            chatbot[-1][1] = (audio_generate(text=bot_response, model_name=model_map[lang_choice]), "audio")
        except Exception as e:
            print(f"音频生成失败: {str(e)}")
            chatbot[-1][1] = bot_response
        yield chatbot

    if answer[1] == userPurposeType.ImageGeneration:
        # 处理图片生成回复
        image_url = answer[0]
        describe = process_image_describe_tool(
            question_type=userPurposeType.ImageDescribe,
            question="描述这个图片，不要识别'AI生成'",
            history=" ",
            image_url=[image_url],
        )
        combined_message = f"""
            **生成的图片:**
            ![Generated Image]({image_url})
            {describe[0]}
            """
        chatbot[-1][1] = combined_message
        yield chatbot

    if answer[1] == userPurposeType.Video:
        # 处理视频回复
        if answer[0]:
            chatbot[-1][1] = answer[0]
        else:
            try:
                chatbot[-1][1] = (
                audio_generate(text="抱歉，视频生成失败，请稍后再试", model_name="zh-CN-YunxiNeural"), "audio")
            except:
                chatbot[-1][1] = "抱歉，视频生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.PPT:
        # 处理PPT回复
        if answer[0]:
            chatbot[-1][1] = answer[0]
        else:
            try:
                chatbot[-1][1] = (
                audio_generate(text="抱歉，PPT生成失败，请稍后再试", model_name="zh-CN-YunxiNeural"), "audio")
            except:
                chatbot[-1][1] = "抱歉，PPT生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.Docx:
        # 处理Word文档回复
        if answer[0]:
            chatbot[-1][1] = answer[0]
        else:
            try:
                chatbot[-1][1] = (
                audio_generate(text="抱歉，文档生成失败，请稍后再试", model_name="zh-CN-YunxiNeural"), "audio")
            except:
                chatbot[-1][1] = "抱歉，文档生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.Audio:
        # 处理音频回复
        if answer[0]:
            chatbot[-1][1] = answer[0]
        else:
            try:
                chatbot[-1][1] = (
                audio_generate(text="抱歉，音频生成失败，请稍后再试", model_name="zh-CN-YunxiNeural"), "audio")
            except:
                chatbot[-1][1] = "抱歉，音频生成失败，请稍后再试"
        yield chatbot

    if answer[1] == userPurposeType.InternetSearch:
        # 处理网络搜索回复
        if not answer[3]:
            bot_response = "由于网络问题，访问互联网失败，下面由我根据现有知识给出回答："
        for chunk in answer[0]:
            bot_response += chunk.choices[0].delta.content or ""
        try:
            chatbot[-1][1] = (audio_generate(text=bot_response, model_name="zh-CN-YunxiNeural"), "audio")
        except:
            chatbot[-1][1] = bot_response
        yield chatbot


# 示例对话
examples = [
    {"text": "您好", "files": []},  # 示例1：简单问候
    {"text": "还熬夜啊？", "files": []},  # 示例2：日常对话
    {"text": "用语音重新回答我一次", "files": []},  # 示例3：语音回复请求
    {"text": "帮我搜索一下养生知识", "files": []},  # 示例4：网络搜索请求
    {"text": "秃头怎么办", "files": []},  # 示例5：健康咨询
    {"text": "请根据我给的参考资料，给我一个合理的饮食建议", "files": []},  # 示例6：基于资料的建议
    {"text": "请生成一段老人打太极的视频", "files": []},  # 示例7：多媒体内容生成
]


# 创建Gradio界面
with gr.Blocks(title="Doctor Strange 🩺", theme=gr.themes.Soft()) as demo:
    # 自定义CSS样式
    gr.HTML("""
        <style>
            .gr-chatbot { 
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .gr-button-primary { 
                background-color: #4CAF50; 
                border-radius: 8px;
            }
            .gr-button { 
                border-radius: 8px;
                margin: 0 4px;
            }
            .gr-textbox, .gr-audio { 
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            .tab-content {
                padding: 16px;
            }
        </style>
    """)

    # 全局聊天状态（跨标签页共享对话历史）
    chatbot = gr.Chatbot(
        height=500,  # 设置聊天窗口高度为500像素
        avatar_images=AVATAR,  # 设置用户和机器人的头像
        show_copy_button=True,  # 显示复制按钮
        latex_delimiters=[  # 支持的LaTeX数学公式分隔符
            {"left": "\\(", "right": "\\)", "display": True},
            {"left": "\\[", "right": "\\]", "display": True},
            {"left": "$$", "right": "$$", "display": True},
            {"left": "$", "right": "$", "display": True},
        ],
        placeholder="开始对话吧...",  # 聊天窗口占位符文本
    )

    # 标签页布局
    with gr.Tabs():
        # 1. 文本对话标签页
        with gr.Tab("文本交流", id="text-tab"):
            with gr.Row():
                chat_input = gr.MultimodalTextbox(
                    interactive=True,  # 启用交互
                    file_count="multiple",  # 允许上传多个文件
                    placeholder="输入消息或上传文件（支持图片、音频、PDF等）...",  # 输入框占位符
                    show_label=False,  # 不显示标签
                    scale=9  # 占据9个单位宽度
                )
                submit_text = gr.Button("发送", variant="primary", scale=1)  # 发送按钮

            # 文本区功能按钮
            with gr.Row():
                clear = gr.ClearButton([chatbot, chat_input], value="清除记录")  # 清除记录按钮
                audio_from_text_btn = gr.Button("语音回复当前内容")  # 语音回复按钮

        # 2. 语音对话标签页
        with gr.Tab("语音对话", id="voice-tab"):
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone", "upload"],  # 支持麦克风录音和文件上传
                    label="录音/上传音频",  # 标签文本
                    type="filepath",  # 返回文件路径
                    scale=8  # 占据8个单位宽度
                )
                lang_choice = gr.Dropdown(
                    choices=["普通话（男）", "普通话（女）", "陕西话", "东北话", "粤语（男）", "粤语（女）"],  # 可选项
                    label="语音类型",  # 标签文本
                    value="普通话（男）",  # 默认值
                    scale=2  # 占据2个单位宽度
                )

            with gr.Row():
                submit_audio = gr.Button("发送语音", variant="primary")  # 发送语音按钮
                text_from_audio_btn = gr.Button("转为文字")  # 转为文字按钮

        # 3. 功能说明标签页
        with gr.Tab("功能指南", id="help-tab"):
            gr.Markdown("""
            ### 功能说明
            - **文本交流**：支持输入文字、上传文件（图片/音频/PDF等），可获取文本或多媒体回复
            - **语音对话**：通过麦克风录音或上传音频，支持多种方言输出
            - **文件处理**：自动识别并解析PDF、Word、图片中的内容
            - **多模态生成**：支持生成图片、视频、PPT、Word文档

            ### 使用示例
            - 上传病历图片，提问"请分析这份病历的关键信息"
            - 发送语音"帮我生成一份糖尿病饮食计划"
            - 输入文字"用知识库内容介绍高血压预防措施"
            """)
            # 折叠式示例
            with gr.Accordion("查看对话示例", open=False):
                gr.Examples(examples=examples, inputs=chat_input, examples_per_page=5)

    # 事件绑定
    # 文本提交
    submit_text.click(
        fn=grodio_view,  # 点击事件处理函数
        inputs=[chatbot, chat_input],  # 输入参数
        outputs=[chatbot]  # 输出参数
    )
    #
    chat_input.submit(
        fn=grodio_view,  # 回车提交事件处理函数
        inputs=[chatbot, chat_input],  # 输入参数
        outputs=[chatbot]  # 输出参数
    )

    # 语音提交
    submit_audio.click(
        fn=gradio_audio_view,  # 点击事件处理函数
        inputs=[chatbot, audio_input, lang_choice],  # 输入参数
        outputs=[chatbot]  # 输出参数
    )


    # 快捷功能：文本转语音回复
    def text_to_audio_reply(chatbot):
        if not chatbot:
            return chatbot
        last_bot_msg = chatbot[-1][1]
        if isinstance(last_bot_msg, tuple) and last_bot_msg[1] == "audio":
            return chatbot  # 已为语音
        try:
            audio_path = audio_generate(text=last_bot_msg, model_name="zh-CN-YunxiNeural")
            chatbot[-1][1] = (audio_path, "audio")
        except:
            pass
        return chatbot


    audio_from_text_btn.click(
        fn=text_to_audio_reply,  # 点击事件处理函数
        inputs=[chatbot],  # 输入参数
        outputs=[chatbot]  # 输出参数
    )


    # 快捷功能：语音转文字
    def audio_to_text_shortcut(audio_input):
        if not audio_input:
            return ""
        return audio_to_text(audio_input)


    text_from_audio_btn.click(
        fn=audio_to_text_shortcut,  # 点击事件处理函数
        inputs=[audio_input],  # 输入参数
        outputs=[chat_input]  # 输出参数
    )


def start_gradio():
    """
    启动Gradio应用
    """
    demo.launch(server_port=10086, share=True)  # 启动应用并分享


# 程序入口点
if __name__ == "__main__":
    start_gradio()  # 运行应用