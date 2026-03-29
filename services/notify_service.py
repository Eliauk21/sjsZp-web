"""
企微通知服务
"""
import requests
import json
from pathlib import Path

# 获取 data 目录路径（相对于当前文件）
DATA_DIR = Path(__file__).parent.parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"


def load_webhook() -> str:
    """加载企业微信 webhook URL"""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        return settings.get("wechat_webhook", "")
    except Exception as e:
        print(f"加载 webhook 配置失败：{e}")
        return ""


def save_webhook(webhook: str) -> bool:
    """保存企业微信 webhook URL"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"wechat_webhook": webhook}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存 webhook 配置失败：{e}")
        return False


def send_wechat_notify(message: str, markdown: bool = True) -> bool:
    """
    发送企微通知

    Args:
        message: 通知内容
        markdown: 是否使用 markdown 格式

    Returns:
        是否发送成功
    """
    webhook = load_webhook()
    if not webhook:
        print("未配置企业微信 webhook，跳过通知发送")
        return False

    if markdown:
        payload = {
            "msgtype": "markdown",
            "markdown": {"content": message}
        }
    else:
        payload = {
            "msgtype": "text",
            "text": {"content": message}
        }

    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("errcode") == 0:
                return True
        print(f"发送企微通知失败：{resp.text}")
        return False
    except Exception as e:
        print(f"发送企微通知异常：{e}")
        return False


def send_task_notify(
    task_name: str,
    status: str,
    shop_count: int = 0,
    success_count: int = 0,
    fail_count: int = 0,
    log_summary: str = ""
) -> bool:
    """
    发送任务通知

    Args:
        task_name: 任务名称
        status: 状态 (running/success/failed)
        shop_count: 涉及店铺数
        success_count: 成功数
        fail_count: 失败数
        log_summary: 日志摘要

    Returns:
        是否发送成功
    """
    # 状态映射
    status_map = {
        "running": "⏳ 进行中",
        "success": "✅ 完成",
        "failed": "❌ 失败"
    }
    status_text = status_map.get(status, status)

    # 构建通知内容
    content = f"""## sjsZp 任务通知
**任务**: {task_name}
**状态**: {status_text}
**时间**: {get_current_time()}
**涉及店铺**: {shop_count} 家
**结果**: 成功 {success_count} 家，失败 {fail_count} 家"""

    if log_summary:
        content += f"\n**详情**: {log_summary}"

    return send_wechat_notify(content, markdown=True)


def get_current_time() -> str:
    """获取当前时间字符串"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
