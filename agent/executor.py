"""
Executor Agent（执行代理）
负责调用工具，执行具体任务，返回结果
"""
from llm import call_llm_with_system, call_llm_stream
from prompts_loader import build_prompt


class ExecutorAgent:
    """执行代理：根据任务类型调用对应功能"""

    def __init__(self):
        self.task_handlers = {
            "career": self._handle_career,
            "resume": self._handle_resume,
            "job": self._handle_job
        }

    def execute(self, task_type: str, params: dict) -> str:
        """
        执行指定类型的任务

        Args:
            task_type: 任务类型（career/resume/job）
            params: 任务参数字典

        Returns:
            任务执行结果
        """
        handler = self.task_handlers.get(task_type)
        if handler:
            return handler(params)
        return "未知任务类型"

    def stream_execute(self, task_type: str, params: dict):
        """流式执行，返回生成器，供 st.write_stream() 使用"""
        handler = self._stream_handlers.get(task_type)
        if handler:
            return handler(params)
        return None

    @property
    def _stream_handlers(self):
        return {
            "career": self._handle_career_stream,
            "career_followup": self._handle_career_followup_stream,
            "resume": self._handle_resume_stream,
            "job": self._handle_job_stream,
        }

    def _handle_career(self, params: dict) -> str:
        """处理职业规划任务"""
        prompt = build_prompt("career_prompt", params)
        return call_llm_with_system("", prompt)

    def _handle_career_stream(self, params: dict):
        """流式处理职业规划"""
        prompt = build_prompt("career_prompt", params)
        return call_llm_stream("", prompt)

    def _handle_career_followup_stream(self, params: dict):
        """流式处理职业规划追问"""
        prompt = build_prompt("career_followup_prompt", params)
        return call_llm_stream("", prompt)

    def _handle_resume(self, params: dict) -> str:
        """处理简历诊断任务"""
        prompt = build_prompt("resume_prompt", params)
        return call_llm_with_system("", prompt)

    def _handle_resume_stream(self, params: dict):
        """流式处理简历诊断"""
        prompt = build_prompt("resume_prompt", params)
        return call_llm_stream("", prompt)

    def _handle_job(self, params: dict) -> str:
        """处理岗位推荐任务"""
        prompt = build_prompt("job_prompt", params)
        return call_llm_with_system("", prompt)

    def _handle_job_stream(self, params: dict):
        """流式处理岗位推荐"""
        prompt = build_prompt("job_prompt", params)
        return call_llm_stream("", prompt)

    def execute_with_tools(self, task_type: str, params: dict, tools: list = None) -> str:
        """
        带工具调用的执行（未来扩展用）

        Args:
            task_type: 任务类型
            params: 任务参数
            tools: 可用工具列表（如查数据库、调用API等）

        Returns:
            执行结果
        """
        # 目前先调用基础执行，后续可扩展工具调用
        return self.execute(task_type, params)
