"""
Planner Agent（规划代理）
负责分析用户意图，判断任务类型，并拆解子任务
"""
from llm import call_llm_with_system


class PlannerAgent:
    """规划代理：分析用户需求，决定任务类型"""

    SYSTEM_PROMPT = """你是一个智能任务规划助手。

当用户描述他们的需求时，你需要：
1. 判断用户想要的服务类型（考研/就业/考公决策、简历诊断、岗位推荐）
2. 提取用户提供的关键信息（专业、技能、兴趣等）
3. 将任务分解为子任务步骤
4. 以结构化的 JSON 格式输出分析结果

输出格式：
{
    "task_type": "career|resume|job",
    "key_info": {"提取的关键信息字典"},
    "sub_tasks": ["子任务1", "子任务2"],
    "confidence": 0.0-1.0
}"""

    def analyze(self, user_input: str) -> dict:
        """
        分析用户输入，判断任务类型

        Args:
            user_input: 用户的自然语言描述

        Returns:
            包含任务类型、关键信息、子任务的字典
        """
        prompt = f"用户需求：{user_input}\n\n请分析并输出JSON格式结果。"
        result = call_llm_with_system(self.SYSTEM_PROMPT, prompt)

        try:
            import json
            # 尝试从返回结果中提取 JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            # 如果 JSON 解析失败，返回默认结构
            return {
                "task_type": self._fallback_classify(user_input),
                "key_info": {},
                "sub_tasks": ["调用执行代理完成任务"],
                "confidence": 0.5
            }

    def _fallback_classify(self, user_input: str) -> str:
        """当 LLM 调用失败时的备用分类逻辑"""
        input_lower = user_input.lower()
        if any(k in input_lower for k in ["考研", "考公", "就业", "方向", "规划"]):
            return "career"
        elif any(k in input_lower for k in ["简历", "诊断", "修改"]):
            return "resume"
        elif any(k in input_lower for k in ["岗位", "工作", "推荐", "技能"]):
            return "job"
        return "career"
