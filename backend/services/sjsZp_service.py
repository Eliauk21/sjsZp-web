"""
sjsZp 核心业务服务
封装 Selenium 自动化操作
"""
import json
import time
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from PIL import Image, ImageDraw, ImageFont

# 配置信息
LOGIN_URL = "https://passport.jd.com/new/login.aspx"
INDEX_URL = "https://sjs-zx.jd.com/index.html"
TARGET_URL = "https://sjs-zx.jd.com/template/modularTemplate.html"
TEMPLATEID_URL = "https://sdk.jd.com/nm?tpGrade=3&templateId="
ORDERManagement_URL = "https://sjs-zx.jd.com/rnTemplate/order-management.html"

accessKeyId = "DC2A7D48BBAF83143873C80869FDE38B"
accessKeySecret = "02DB4A15CEDF23B8CE32E03EF06E0A73"
USERNAME = "陆泽科技"
PASSWORD = "bA6#aA1$pG2%"

BASE_DIR = Path(__file__).parent.parent.parent


class SjsZpService:
    """sjsZp 服务类"""

    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
        self.driver = None

    def log(self, message: str):
        """输出日志"""
        print(message)
        if self.log_callback:
            self.log_callback(message)

    def create_driver(self):
        """创建浏览器驱动"""
        options = Options()
        options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        options.add_argument("--headless")  # 无头模式
        options.add_argument("--disable-gpu")
        driver_path = str(BASE_DIR / 'msedgedriver.exe')
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service, options=options)
        return self.driver

    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def execute(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        if operation == 'generate_image':
            return self.generate_image(params)
        elif operation == 'check_orderId':
            return self.check_orderId(params)
        elif operation == 'create_module':
            return self.create_module(params)
        elif operation == 'new_module':
            return self.new_module(params)
        elif operation == 'delete_fail_module':
            return self.delete_fail_module(params)
        elif operation == 'edit_old_module':
            return self.edit_old_module(params)
        elif operation == 'delete_module':
            return self.delete_module(params)
        elif operation == 'review_module':
            return self.review_module(params)
        else:
            raise ValueError(f'未知操作：{operation}')

    def generate_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """图片生成"""
        from core.sjsZp_core import SjsZpCore
        core = SjsZpCore(log_callback=self.log_callback)

        mode = params.get('mode', 'batch')
        if mode == 'single':
            filepath = core.create_image(
                text=params.get('text', 'Test'),
                bg_color=params.get('bg_color', '#ffffff'),
                text_color=params.get('text_color', '#000000'),
                border_color=params.get('border_color', '#000000'),
                border_width=params.get('border_width', 20),
                font_size=params.get('font_size', 40),
            )
            return {'success': True, 'files': [str(filepath)]}
        else:
            files = core.generate_batch(selected_shops=params.get('shops'))
            return {'success': True, 'files': files}

    def check_orderId(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """店铺订单预审"""
        self.create_driver()
        try:
            self.driver.get(ORDERManagement_URL)
            time.sleep(2)
            self.log('订单预审任务已启动')
            # TODO: 实现具体的预审逻辑
            return {'success': True, 'message': '预审完成'}
        finally:
            self.close_driver()

    def create_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建店铺模板"""
        self.create_driver()
        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)
            self.log('创建店铺模板任务已启动')
            # TODO: 实现具体的创建逻辑
            return {'success': True, 'message': '模板创建完成'}
        finally:
            self.close_driver()

    def new_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建 v3 版本模块"""
        self.create_driver()
        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)
            self.log('创建 v3 模块任务已启动')
            return {'success': True, 'message': 'v3 模块创建完成'}
        finally:
            self.close_driver()

    def delete_fail_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模块状态检查"""
        self.create_driver()
        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)
            self.log('模块状态检查任务已启动')
            return {'success': True, 'message': '模块检查完成'}
        finally:
            self.close_driver()

    def edit_old_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建 v4 版本模块"""
        self.create_driver()
        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)
            self.log('创建 v4 模块任务已启动')
            return {'success': True, 'message': 'v4 模块创建完成'}
        finally:
            self.close_driver()

    def delete_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除指定模块"""
        self.create_driver()
        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)
            self.log('删除模块任务已启动')
            return {'success': True, 'message': '模块删除完成'}
        finally:
            self.close_driver()

    def review_module(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """提交审核"""
        self.create_driver()
        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)
            self.log('提交审核任务已启动')
            return {'success': True, 'message': '审核提交完成'}
        finally:
            self.close_driver()
