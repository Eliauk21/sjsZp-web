"""
任务执行 API
"""
from flask import Blueprint, jsonify, request, Response
import json
from pathlib import Path
from datetime import datetime
import threading
import time

from services.sjsZp_service import SjsZpService

task_bp = Blueprint('tasks', __name__)

# 数据文件路径
BASE_DIR = Path(__file__).parent.parent.parent
TASK_HISTORY_FILE = BASE_DIR / 'backend' / 'data' / 'task_history.json'

# 存储运行中的任务
running_tasks = {}


def load_task_history() -> list:
    """加载任务历史"""
    try:
        with open(TASK_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_task_record(record: dict):
    """保存任务记录"""
    history = load_task_history()
    history.append(record)
    with open(TASK_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


@task_bp.route('/execute', methods=['POST'])
def execute_task():
    """执行任务"""
    data = request.json
    operation = data.get('operation')
    params = data.get('params', {})

    if not operation:
        return jsonify({'success': False, 'message': '缺少操作类型'}), 400

    task_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    task_name = {
        'generate_image': '图片生成',
        'check_orderId': '店铺订单预审',
        'create_module': '创建店铺模板',
        'new_module': '创建 v3 版本模块',
        'delete_fail_module': '模块状态检查',
        'edit_old_module': '创建 v4 版本模块',
        'delete_module': '删除指定模块',
        'review_module': '提交审核'
    }.get(operation, operation)

    # 创建任务记录
    record = {
        'task_id': task_id,
        'task_name': task_name,
        'operation': operation,
        'shop_count': len(params.get('shops', [])),
        'status': 'running',
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': None,
        'log': []
    }

    # 创建服务实例
    service = SjsZpService(log_callback=lambda msg: record['log'].append(msg))
    running_tasks[task_id] = {'service': service, 'record': record}

    # 在新线程中执行任务
    def run_task():
        try:
            result = service.execute(operation, params)
            record['status'] = 'success'
            record['result'] = result
        except Exception as e:
            record['status'] = 'failed'
            record['log'].append(f'错误：{str(e)}')
            record['result'] = {'error': str(e)}
        finally:
            record['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_task_record(record)
            running_tasks.pop(task_id, None)

    thread = threading.Thread(target=run_task)
    thread.start()

    return jsonify({
        'success': True,
        'task_id': task_id,
        'message': '任务已启动'
    })


@task_bp.route('/history', methods=['GET'])
def get_task_history():
    """获取任务历史"""
    history = load_task_history()
    # 按时间倒序
    history.reverse()
    return jsonify({'success': True, 'data': history})


@task_bp.route('/<task_id>/logs', methods=['GET'])
def get_task_logs(task_id):
    """获取任务日志（SSE 流式传输）"""
    def generate():
        while task_id in running_tasks:
            record = running_tasks[task_id]['record']
            yield f'data: {json.dumps({"logs": record["log"]})}\n\n'
            time.sleep(1)

        # 任务结束后发送最终日志
        history = load_task_history()
        for record in history:
            if record['task_id'] == task_id:
                yield f'data: {json.dumps({"logs": record["log"], "status": record["status"]})}\n\n'
                break

    return Response(generate(), mimetype='text/event-stream')


@task_bp.route('/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id in running_tasks:
        record = running_tasks[task_id]['record']
        return jsonify({
            'success': True,
            'status': 'running',
            'logs': record['log']
        })

    # 查找历史记录
    history = load_task_history()
    for record in history:
        if record['task_id'] == task_id:
            return jsonify({
                'success': True,
                'status': record['status'],
                'logs': record['log'],
                'result': record.get('result')
            })

    return jsonify({'success': False, 'message': '任务不存在'}), 404
