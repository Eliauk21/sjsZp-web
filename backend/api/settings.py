"""
设置 API
"""
from flask import Blueprint, jsonify, request
import json
from pathlib import Path
import requests

settings_bp = Blueprint('settings', __name__)

# 配置文件路径
BASE_DIR = Path(__file__).parent.parent.parent
SETTINGS_FILE = BASE_DIR / 'backend' / 'data' / 'settings.json'


def load_settings() -> dict:
    """加载配置"""
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'wechat_webhook': ''}


def save_settings(data: dict) -> bool:
    """保存配置"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


@settings_bp.route('', methods=['GET'])
def get_settings():
    """获取配置"""
    settings = load_settings()
    return jsonify({'success': True, 'data': settings})


@settings_bp.route('', methods=['POST'])
def save_settings_route():
    """保存配置"""
    data = request.json
    if save_settings(data):
        return jsonify({'success': True, 'message': '保存成功'})
    return jsonify({'success': False, 'message': '保存失败'}), 500


@settings_bp.route('/webhook/test', methods=['POST'])
def test_webhook():
    """测试企业微信 webhook"""
    settings = load_settings()
    webhook = settings.get('wechat_webhook')

    if not webhook:
        return jsonify({
            'success': False,
            'message': '请先配置 webhook URL'
        }), 400

    from datetime import datetime
    # 发送测试消息
    payload = {
        'msgtype': 'markdown',
        'markdown': {
            'content': f'## sjsZp 测试通知\n这是一条测试消息\n时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        }
    }

    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get('errcode') == 0:
                return jsonify({'success': True, 'message': '测试成功'})
        return jsonify({
            'success': False,
            'message': f'发送失败：{resp.text}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送异常：{str(e)}'
        }), 500
