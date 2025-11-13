# 从项目模块导入所需功能
from Internet.Internet_prompt import extract_question  # 从问题中提取关键词的函数
from Internet.retrieve_Internet import retrieve_html  # 从互联网检索HTML内容的函数
from client.clientfactory import Clientfactory  # 客户端工厂，用于创建AI客户端
from env import get_app_root  # 获取应用根目录的函数

# 导入标准库和第三方库
import re  # 正则表达式模块，用于字符串处理
import os  # 操作系统接口模块，用于文件和目录操作
import requests  # HTTP库，用于发送网络请求
import shutil  # 高级文件操作模块，用于删除目录等操作
import threading  # 线程模块，用于并发执行任务
from typing import List  # 类型提示，用于列表类型注解
from bs4 import BeautifulSoup  # HTML解析库，用于解析和提取网页内容
from urllib3.exceptions import InsecureRequestWarning  # 禁用SSL警告的异常类

# 定义互联网搜索结果的保存路径
_SAVE_PATH = os.path.join(get_app_root(), "data/cache/internet")


def InternetSearchChain(question, history):
    """
    互联网搜索链，执行完整的互联网搜索流程
    
    Args:
        question: 用户问题
        history: 对话历史
        
    Returns:
        tuple: 包含响应、链接和成功状态的元组
    """
    # 如果保存路径已存在，删除该目录及其内容
    if os.path.exists(_SAVE_PATH):
        shutil.rmtree(_SAVE_PATH)

    # 如果保存路径不存在，创建该目录
    if not os.path.exists(_SAVE_PATH):
        os.makedirs(_SAVE_PATH)

    # 从问题和历史中提取完整问题
    whole_question = extract_question(question, history)
    # 使用分号分割问题为多个子问题
    question_list = re.split(r"[;；]", whole_question)

    # 禁用SSL请求警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # 初始化线程列表和链接字典
    threads = []
    links = {}

    # 为每个问题创建单独的线程
    for question in question_list:
        # 每个线程执行Bing搜索操作
        thread = threading.Thread(target=search_bing, args=(question, links, 3))
        threads.append(thread)
        thread.start()
        # 每个线程执行百度搜索操作
        thread = threading.Thread(target=search_baidu, args=(question, links, 3))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 检查是否下载了HTML文件
    if has_html_files(_SAVE_PATH):
        # 如果有HTML文件，检索HTML内容
        docs, _context = retrieve_html(question)
        # 构造包含搜索资料的提示词
        prompt = f"根据你现有的知识，辅助以搜索到的文件资料：\n{_context}\n 回答问题：\n{question}\n 尽可能多的覆盖到文件资料"
    else:
        # 如果没有HTML文件，直接使用原问题作为提示词
        prompt = question

    # 使用客户端工厂创建客户端并获取流式响应
    response = Clientfactory().get_client().chat_with_ai_stream(prompt)

    # 返回响应、链接字典和是否有HTML文件的检查结果
    return response, links, has_html_files(_SAVE_PATH)


def search_bing(query, links, num_results=3):
    """
    使用Bing搜索引擎搜索并下载结果页面
    
    Args:
        query: 搜索查询
        links: 链接字典，用于存储搜索到的链接
        num_results: 需要获取的结果数量，默认为3
    """
    # 设置请求头，模拟浏览器访问
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, compress",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0",
    }
    # Bing搜索引擎的搜索URL列表
    search_urls = [
        f"https://cn.bing.com/search?q={query}",
        f"https://www.bing.com/search?q={query}",
    ]
    # 遍历搜索URL
    for search_url in search_urls:
        flag = 0  # 已下载文件计数器
        # 发送GET请求获取搜索结果
        response = requests.get(search_url, headers=headers)

        # 如果请求成功
        if response.status_code == 200:
            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(response.text, "html.parser")

            # 查找所有搜索结果项
            for item in soup.find_all("li", class_="b_algo"):
                # 如果已达到所需结果数量，停止下载
                if flag >= num_results:
                    break
                # 提取标题和链接
                title = item.find("h2").text
                link = item.find("a")["href"].split("#")[0]  # 删除 '#' 后的部分

                try:
                    # 禁用 SSL 验证的警告
                    # 发送GET请求下载网页内容
                    response = requests.get(link, timeout=10)
                    # 如果下载成功
                    if response.status_code == 200:
                        # 构造保存文件名
                        filename = f"{_SAVE_PATH}/{title}.html"
                        # 如果响应内容不为空
                        if response.text is not None:
                            # 将网页内容保存到文件
                            with open(filename, "w", encoding="utf-8") as f:
                                links[link] = title  # 将链接和标题添加到链接字典
                                f.write(response.text)  # 写入网页内容
                                flag += 1  # 增加计数器
                            print(f"Downloaded and saved: {link} as {filename}")
                        else:
                            print(f"Failed to download {link}: Empty content")
                    else:
                        print(
                            f"Failed to download {link}: Status code {response.status_code}"
                        )
                except Exception as e:
                    print(f"Error downloading {link}: {e}")
            # 检查是否达到了期望的结果数
            if flag < num_results:
                print("访问bing失败，请检查网络代理")
        else:
            print("Error: ", response.status_code)


def search_baidu(query, links, num_results=3):
    """
    使用百度搜索引擎搜索并下载结果页面
    
    Args:
        query: 搜索查询
        links: 链接字典，用于存储搜索到的链接
        num_results: 需要获取的结果数量，默认为3
    """
    # 设置请求头，模拟浏览器访问
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, compress",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0",
    }
    # 百度搜索引擎的搜索URL
    search_url = f"https://www.baidu.com/s?wd={query}"  # 百度搜索URL

    flag = 0  # 已下载文件计数器
    # 发送GET请求获取搜索结果
    response = requests.get(search_url, headers=headers)

    # 如果请求成功
    if response.status_code == 200:
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, "html.parser")

        # 百度搜索结果的条目
        for item in soup.find_all("div", class_="result"):
            # 如果已达到所需结果数量，停止下载
            if flag >= num_results:
                break
            try:
                # 获取标题和链接
                title = item.find("h3").text
                link = item.find("a")["href"].split("#")[0]  # 删除 '#' 后的部分

                # 禁用 SSL 验证的警告
                # 发送GET请求下载网页内容
                response = requests.get(link, timeout=10)

                # 如果下载成功
                if response.status_code == 200:
                    # 构造保存文件名
                    filename = f"{_SAVE_PATH}/{title}.html"
                    # 如果响应内容不为空
                    if response.text is not None:
                        # 将网页内容保存到文件
                        with open(filename, "w", encoding="utf-8") as f:
                            links[link] = title  # 将链接和标题添加到链接字典
                            f.write(response.text)  # 写入网页内容
                            flag += 1  # 增加计数器
                        print(f"Downloaded and saved: {link} as {filename}")
                    else:
                        print(f"Failed to download {link}: Empty content")
                else:
                    print(
                        f"Failed to download {link}: Status code {response.status_code}"
                    )
            except Exception as e:
                print(f"Error downloading {link}: {e}")

        # 检查是否达到了期望的结果数
        if flag < num_results:
            print("访问百度失败，请检查网络代理制")
    else:
        print("Error: ", response.status_code)


def has_html_files(directory_path):
    """
    检查目录中是否存在HTML文件
    
    Args:
        directory_path: 要检查的目录路径
        
    Returns:
        bool: 如果目录中存在HTML文件返回True，否则返回False
    """
    # 检查目录是否存在
    if os.path.exists(directory_path):
        # 遍历目录中的文件
        for file_name in os.listdir(directory_path):
            # 如果文件以.html结尾，返回True
            if file_name.endswith(".html"):
                return True
        # 如果遍历完所有文件都没有找到HTML文件，返回False
        return False
    else:
        # 如果目录不存在，返回False
        return False