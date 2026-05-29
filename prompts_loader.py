"""
提示词加载模块
从 YAML 文件加载提示词配置，支持角色、任务、格式约束、示例等
"""
import yaml
import os


def load_prompt(prompt_name: str) -> dict:
    """
    加载指定提示词配置

    Args:
        prompt_name: 提示词文件名（不含扩展名）

    Returns:
        包含提示词配置的字典
    """
    prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
    prompt_path = os.path.join(prompt_dir, f"{prompt_name}.yaml")

    with open(prompt_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_prompt(prompt_name: str, user_input: dict) -> str:
    """
    根据提示词模板和用户输入构建完整提示词

    Args:
        prompt_name: 提示词名称
        user_input: 用户输入的参数字典

    Returns:
        构建好的提示词字符串
    """
    config = load_prompt(prompt_name)

    # 构建基础提示词
    parts = []
    parts.append(f"角色：{config['role']}")
    parts.append(f"\n任务：{config['task']}")

    # 添加格式约束
    if "constraints" in config:
        parts.append("\n约束条件：")
        for constraint in config["constraints"]:
            parts.append(f"- {constraint}")

    # 添加示例（few-shot）
    if "examples" in config and config["examples"]:
        parts.append("\n参考示例：")
        for ex in config["examples"]:
            parts.append(f"输入：{ex['input']}")
            parts.append(f"输出：{ex['output']}")

    # 添加步骤指引
    if "steps" in config:
        parts.append("\n执行步骤：")
        for step in config["steps"]:
            parts.append(f"- {step}")

    # 添加用户输入
    parts.append("\n用户信息：")
    for key, value in user_input.items():
        parts.append(f"- {key}：{value}")

    return "\n".join(parts)


def get_role_prompt(prompt_name: str) -> str:
    """获取角色的系统提示词"""
    config = load_prompt(prompt_name)
    return f"{config['role']}\n{config['task']}"
