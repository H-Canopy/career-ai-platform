"""
文本向量化模块
使用轻量级Embedding模型对文本进行向量化
"""
import hashlib


class Embedder:
    """文本向量化器（简化版）"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        初始化向量化器

        Args:
            model_name: 使用的 Embedding 模型名称
        """
        self.model_name = model_name
        self._client = None

    def _get_client(self):
        """延迟加载模型客户端"""
        if self._client is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._client = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")
        return self._client

    def embed(self, text: str) -> list:
        """
        将单条文本转换为向量

        Args:
            text: 输入文本

        Returns:
            向量列表
        """
        client = self._get_client()
        embedding = client.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: list) -> list:
        """
        批量将文本转换为向量

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        client = self._get_client()
        embeddings = client.encode(texts)
        return embeddings.tolist()

    @staticmethod
    def simple_hash(text: str) -> str:
        """简单的文本哈希（用于快速判断文本是否相同）"""
        return hashlib.md5(text.encode()).hexdigest()


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 20) -> list:
    """
    文本分块（滑动窗口）

    Args:
        text: 输入文本
        chunk_size: 每块字数
        overlap: 块间重叠字数

    Returns:
        文本块列表
    """
    words = list(text)
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = "".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
