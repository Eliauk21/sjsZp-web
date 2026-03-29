"""
店铺管理 API
"""
from flask import Blueprint, jsonify, request
import json
from pathlib import Path

shop_bp = Blueprint('shops', __name__)

# 数据文件路径
BASE_DIR = Path(__file__).parent.parent.parent
SHOP_CONFIG = BASE_DIR / 'zipdist' / 'shopConfig.json'
SHOP_ALL_CONFIG = BASE_DIR / 'shopAllConfig.json'


def load_json(path: Path) -> list:
    """加载 JSON 文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return []


def save_json(path: Path, data: list) -> bool:
    """保存 JSON 文件"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False


@shop_bp.route('/current', methods=['GET'])
def get_current_shops():
    """获取新增入驻店铺"""
    shops = load_json(SHOP_CONFIG)
    return jsonify({'success': True, 'data': shops})


@shop_bp.route('/current', methods=['POST'])
def save_current_shops():
    """保存新增入驻店铺"""
    data = request.json
    if save_json(SHOP_CONFIG, data):
        return jsonify({'success': True, 'message': '保存成功'})
    return jsonify({'success': False, 'message': '保存失败'}), 500


@shop_bp.route('/history', methods=['GET'])
def get_history_shops():
    """获取历史入驻店铺"""
    shops = load_json(SHOP_ALL_CONFIG)
    return jsonify({'success': True, 'data': shops})


@shop_bp.route('/history', methods=['POST'])
def save_history_shops():
    """保存历史入驻店铺"""
    data = request.json
    if save_json(SHOP_ALL_CONFIG, data):
        return jsonify({'success': True, 'message': '保存成功'})
    return jsonify({'success': False, 'message': '保存失败'}), 500


@shop_bp.route('/sync', methods=['POST'])
def sync_shops():
    """同步新增店铺到历史"""
    current_shops = load_json(SHOP_CONFIG)
    history_shops = load_json(SHOP_ALL_CONFIG)

    existing_ids = {s['shopId'] for s in history_shops}
    new_count = 0

    for shop in current_shops:
        if shop['shopId'] not in existing_ids:
            history_shops.append(shop)
            new_count += 1

    if save_json(SHOP_ALL_CONFIG, history_shops):
        return jsonify({
            'success': True,
            'message': f'同步成功，新增 {new_count} 家店铺'
        })
    return jsonify({'success': False, 'message': '同步失败'}), 500


@shop_bp.route('/import', methods=['POST'])
def import_shops():
    """导入店铺数据"""
    data = request.json.get('data')
    target = request.json.get('target', 'current')  # current or history

    if target == 'current':
        path = SHOP_CONFIG
    else:
        path = SHOP_ALL_CONFIG

    if save_json(path, data):
        return jsonify({'success': True, 'message': '导入成功'})
    return jsonify({'success': False, 'message': '导入失败'}), 500
