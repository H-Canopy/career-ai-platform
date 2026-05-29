"""
检索引擎模块
基于向量相似度实现文档检索
"""
import numpy as np
from typing import Optional


class RetrievalEngine:
    """轻量级检索引擎（基于简单向量相似度）"""

    def __init__(self):
        self.documents = []  # 文档列表
        self.vectors = []    # 向量列表
        self.metadatas = []  # 元数据列表

    def add_document(self, text: str, metadata: dict = None):
        """
        添加文档到检索库

        Args:
            text: 文档文本
            metadata: 文档元数据（如来源、标题等）
        """
        from .embed import Embedder
        embedder = Embedder()

        vector = embedder.embed(text)
        self.documents.append(text)
        self.vectors.append(vector)
        self.metadatas.append(metadata or {})

    def add_documents(self, texts: list, metadatas: list = None):
        """
        批量添加文档

        Args:
            texts: 文档文本列表
            metadatas: 元数据列表
        """
        from .embed import Embedder
        embedder = Embedder()

        vectors = embedder.embed_batch(texts)
        for i, text in enumerate(texts):
            self.documents.append(text)
            self.vectors.append(vectors[i])
            self.metadatas.append(metadatas[i] if metadatas else {})

    def search(self, query: str, top_k: int = 3) -> list:
        """
        检索最相关的文档

        Args:
            query: 查询文本
            top_k: 返回的最相关文档数量

        Returns:
            相关文档列表，每项包含 text、metadata、score
        """
        if not self.documents:
            return []

        from .embed import Embedder
        embedder = Embedder()
        query_vector = embedder.embed(query)

        # 计算余弦相似度
        scores = []
        for vec in self.vectors:
            score = self._cosine_similarity(query_vector, vec)
            scores.append(score)

        # 取 top_k
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0.3:  # 相似度阈值
                results.append({
                    "text": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "score": float(scores[idx])
                })
        return results

    @staticmethod
    def _cosine_similarity(vec1: list, vec2: list) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))


# 全局检索引擎实例（用于简历和岗位数据）
resume_engine = RetrievalEngine()
job_engine = RetrievalEngine()


def init_resume_engine():
    """初始化简历检索引擎（示例数据）"""
    sample_resumes = [
        "精通Python编程，熟悉Django/Flask框架，有Web开发经验",
        "熟悉机器学习算法，使用TensorFlow/PyTorch实现过项目",
        "擅长Java开发，了解Spring生态系统，有后台系统开发经验",
        "熟悉前端技术Vue/React，掌握HTML/CSS/JavaScript",
        "有数据库设计经验，精通MySQL/PostgreSQL，了解Redis"
    ]
    for resume in sample_resumes:
        resume_engine.add_document(resume, {"source": "sample"})


def init_job_engine():
    """初始化岗位检索引擎（示例数据）"""
    sample_jobs = [
        {"text": "Python开发工程师 - 互联网金融 - 15k-25k - 掌握Python、SQL、Django", "meta": {"city": "北京", "salary": "15k-25k"}},
        {"text": "机器学习工程师 - 人工智能 - 20k-35k - 掌握Python、TensorFlow、数据分析", "meta": {"city": "上海", "salary": "20k-35k"}},
        {"text": "Java后台开发 - 电商平台 - 12k-20k - 掌握Java、Spring、MySQL", "meta": {"city": "深圳", "salary": "12k-20k"}},
        {"text": "前端开发工程师 - 在线教育 - 10k-18k - 掌握Vue/React、HTML/CSS", "meta": {"city": "杭州", "salary": "10k-18k"}},
        {"text": "数据分析师 - 咨询公司 - 8k-15k - 掌握Python、SQL、Excel", "meta": {"city": "广州", "salary": "8k-15k"}},
    ]
    for job in sample_jobs:
        job_engine.add_document(job["text"], job["meta"])
