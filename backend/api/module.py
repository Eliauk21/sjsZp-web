"""
模块管理 API
"""
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import json
from pathlib import Path
import os

module_bp = Blueprint('modules', __name__)

# 数据文件路径
BASE_DIR = Path(__file__).parent.parent.parent
MODULE_CONFIG = BASE_DIR / 'moduleConfig.json'
ZIPDIST_DIR = BASE_DIR / 'zipdist'


def load_json(path: Path) -> list:
    """加载 JSON 文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_json(path: Path, data: list) -> bool:
    """保存 JSON 文件"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


@module_bp.route('', methods=['GET'])
def get_modules():
    """获取模块列表"""
    modules = load_json(MODULE_CONFIG)
    return jsonify({'success': True, 'data': modules})


@module_bp.route('', methods=['POST'])
def save_modules():
    """保存模块配置"""
    data = request.json
    if save_json(MODULE_CONFIG, data):
        return jsonify({'success': True, 'message': '保存成功'})
    return jsonify({'success': False, 'message': '保存失败'}), 500


@module_bp.route('/upload', methods=['POST'])
def upload_module():
    """上传模块文件"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未选择文件'}), 400

    file = request.files['file']
    shop_id = request.form.get('shopId')

    if not shop_id:
        return jsonify({'success': False, 'message': '缺少店铺 ID'}), 400

    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400

    if not file.filename.endswith('.zip'):
        return jsonify({'success': False, 'message': '请上传 zip 文件'}), 400

    # 保存文件
    shop_dir = ZIPDIST_DIR / shop_id
    shop_dir.mkdir(parents=True, exist_ok=True)

    filename = secure_filename(file.filename)
    save_path = shop_dir / filename

    file.save(str(save_path))

    return jsonify({
        'success': True,
        'message': f'文件已保存到 {save_path}'
    })
