'''联网搜索的RAG检索模型类'''
# 导入标准库
from model.model_base import Modelbase  # 基础模型类，提供模型的基本功能
from model.model_base import ModelStatus  # 模型状态枚举，定义模型的不同状态

import os  # 操作系统接口模块，用于文件和目录操作
from env import get_app_root  # 获取应用根目录的函数

# 导入第三方库
from langchain_community.embeddings import ModelScopeEmbeddings  # ModelScope嵌入模型，用于文本向量化
from langchain_core.vectorstores import VectorStoreRetriever  # 向量存储检索器基类
from langchain_community.document_loaders import DirectoryLoader, MHTMLLoader, UnstructuredHTMLLoader  # 文档加载器
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 递归字符文本分割器，用于分割文档
from langchain_community.vectorstores.faiss import FAISS  # FAISS向量存储，用于高效相似性搜索

# 导入项目模块
from config.config import Config  # 配置管理器，用于读取配置信息

# 检索模型
class InternetModel(Modelbase):
    """
    联网搜索的RAG检索模型类
    用于处理从互联网搜索获取的HTML和MHTML文档，构建向量库以支持检索增强生成
    """
    
    # 声明_retriever属性，类型为VectorStoreRetriever
    _retriever: VectorStoreRetriever

    def __init__(self,*args,**krgs):
        """
        初始化联网搜索检索模型
        """
        # 调用父类初始化方法
        super().__init__(*args,**krgs)

        # 此处请自行改成下载embedding模型的位置
        # 从配置中获取嵌入模型的路径
        self._embedding_model_path =Config.get_instance().get_with_nested_params("model", "embedding", "model-name")
        # 设置文本分割器为递归字符分割器
        self._text_splitter = RecursiveCharacterTextSplitter
        #self._embedding = OpenAIEmbeddings()
        # 设置嵌入模型为ModelScope嵌入模型
        self._embedding = ModelScopeEmbeddings(model_id=self._embedding_model_path)
        # 构建数据路径，指向应用根目录下的data/cache/internet文件夹
        self._data_path = os.path.join(get_app_root(), "data/cache/internet")
        
        #self._logger: Logger = Logger("rag_retriever")

    # 建立向量库
    def build(self):
        """
        建立向量库，加载HTML和MHTML文档并构建向量存储
        """
        # 加载html文件
        html_loader = DirectoryLoader(self._data_path, glob="**/*.html", loader_cls=UnstructuredHTMLLoader, silent_errors=True, use_multithreading=True)
        html_docs = html_loader.load()
        
        # 加载mhtml文件
        mhtml_loader = DirectoryLoader(self._data_path, glob="**/*.mhtml", loader_cls=MHTMLLoader, silent_errors=True, use_multithreading=True)
        mhtml_docs = mhtml_loader.load()
        
        
        #合并文档
        docs =  html_docs + mhtml_docs
        
        # 创建一个 RecursiveCharacterTextSplitter 对象，用于将文档分割成块，chunk_size为最大块大小，chunk_overlap块之间可以重叠的大小
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)
        
        # 使用 FAISS 创建一个向量数据库，存储分割后的文档及其嵌入向量
        vectorstore = FAISS.from_documents(documents=splits, embedding=self._embedding)
        # 将向量存储转换为检索器，设置检索参数 k 为 6，即返回最相似的 6 个文档
        self._retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
        

        
    @property
    def retriever(self)-> VectorStoreRetriever:
        """
        获取检索器属性，每次访问时都会重新构建向量库
        
        Returns:
            VectorStoreRetriever: 向量存储检索器
        """
        # 每次获取retriever时都重新构建向量库
        self.build()
        # 返回检索器
        return self._retriever

# 创建InternetModel类的单例实例
INSTANCE = InternetModel()