"""
Flask Backend for sjsZp Web
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime

from api.shop import shop_bp
from api.module import module_bp
from api.task import task_bp
from api.settings import settings_bp

app = Flask(__name__)
CORS(app)  # 允许跨域

# 注册蓝图
app.register_blueprint(shop_bp, url_prefix='/api/shops')
app.register_blueprint(module_bp, url_prefix='/api/modules')
app.register_blueprint(task_bp, url_prefix='/api/tasks')
app.register_blueprint(settings_bp, url_prefix='/api/settings')

# 数据目录
DATA_DIR = Path(__file__).parent / 'data'


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
