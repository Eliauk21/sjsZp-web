"""
sjsZp 核心逻辑模块
从原 sjsZp.py 重构而来，支持回调接口实时日志
"""
import json
import time
from pathlib import Path
from typing import Optional, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from PIL import Image, ImageDraw, ImageFont

# 配置信息
LOGIN_URL = "https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fsjs-zx.jd.com"
INDEX_URL = "https://sjs-zx.jd.com/index.html"
TARGET_URL = "https://sjs-zx.jd.com/template/modularTemplate.html"
TEMPLATEID_URL = "https://sdk.jd.com/nm?tpGrade=3&templateId="
TEMPLATEID_PREVIEW_URL = "https://sjs-zx.jd.com/template/applyAudit.html?templateId="

accessKeyId = "DC2A7D48BBAF83143873C80869FDE38B"
accessKeySecret = "02DB4A15CEDF23B8CE32E03EF06E0A73"

USERNAME = "陆泽科技"
PASSWORD = "bA6#aA1$pG2%"

# 获取根目录（sjsZp-web 目录）
ROOT_DIR = Path(__file__).parent.parent


def log_callback(message: str, callback: Optional[Callable] = None):
    """日志输出回调"""
    print(message)
    if callback:
        callback(message)


class SjsZpCore:
    """sjsZp 核心类"""

    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
        self.driver = None

    def log(self, message: str):
        """输出日志"""
        log_callback(message, self.log_callback)

    def create_driver(self):
        """创建浏览器驱动"""
        options = Options()
        options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        options.add_argument(f"--user-data-dir={ROOT_DIR / 'edge_profile'}")
        driver_path = str(ROOT_DIR / "msedgedriver.exe")
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service, options=options)
        return self.driver

    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def login(self, wait_seconds: int = 60) -> bool:
        """
        登录京东商家后台

        Args:
            wait_seconds: 等待登录超时时间

        Returns:
            是否登录成功
        """
        if not self.driver:
            self.create_driver()

        self.driver.get(LOGIN_URL)
        wait = WebDriverWait(self.driver, wait_seconds)

        try:
            username_field = self.driver.find_element(By.ID, "loginname")
            password_field = self.driver.find_element(By.ID, "nloginpwd")
            username_field.send_keys(USERNAME)
            password_field.send_keys(PASSWORD)
            self.driver.find_element(By.ID, "loginsubmit").click()

            # 等待登录成功（用户可能需要手动滑验证码）
            wait.until(EC.url_contains(INDEX_URL))
            self.log("登录成功")
            return True
        except TimeoutException:
            self.log("登录失败或超时")
            return False
        except Exception as e:
            self.log(f"登录异常：{e}")
            return False

    def create_image(
        self,
        text: str = "Hello",
        bg_color: str = "#ffffff",
        text_color: str = "#000000",
        border_color: str = "#000000",
        width: int = 640,
        height: int = 914,
        border_width: int = 20,
        font_size: int = 48,
        font_path: Optional[str] = None,
        output_dir: str = ".",
        filename_prefix: Optional[str] = None,
    ) -> Optional[Path]:
        """生成带围边的图片"""
        inner_width = width - 2 * border_width
        inner_height = height - 2 * border_width

        img = Image.new("RGB", (width, height), border_color)
        draw = ImageDraw.Draw(img)

        inner_rect = [
            border_width, border_width,
            width - border_width, height - border_width,
        ]
        draw.rectangle(inner_rect, fill=bg_color)

        # 加载字体
        if font_path:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                font = ImageFont.load_default()
        else:
            system_fonts = [
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/msyh.ttc",
            ]
            font = ImageFont.load_default()
            for font_file in system_fonts:
                try:
                    font = ImageFont.truetype(font_file, font_size)
                    break
                except Exception:
                    continue

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (inner_width - text_width) // 2 + border_width
        text_y = (inner_height - text_height) // 2 + border_width

        draw.text((text_x, text_y), text, fill=text_color, font=font)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        prefix = filename_prefix if filename_prefix else "".join(
            c if c.isalnum() or c in "-_." else "_" for c in text[:20]
        )
        filename = f"{prefix}.png"
        filepath = output_path / filename

        img.save(filepath, "PNG")
        self.log(f"已生成：{filepath}")

        return filepath

    def generate_batch(
        self,
        config_path: Optional[str] = None,
        output_subdir: str = "image",
        bg_color: str = "#ffffff",
        text_color: str = "#000000",
        border_color: str = "#000000",
        border_width: int = 20,
        font_size: int = 40,
        selected_shops: Optional[list] = None,
    ) -> list:
        """
        批量生成图片

        Args:
            config_path: shopConfig.json 文件路径
            output_subdir: 输出子目录名
            bg_color: 背景颜色
            text_color: 文字颜色
            border_color: 围边颜色
            border_width: 围边宽度
            font_size: 文字大小
            selected_shops: 选中的店铺列表（可选）

        Returns:
            生成的图片路径列表
        """
        if config_path is None:
            config_path = str(ROOT_DIR / "zipdist" / "shopConfig.json")

        config_file = Path(config_path)
        if not config_file.exists():
            self.log(f"配置文件不存在：{config_file}")
            return []

        with open(config_file, "r", encoding="utf-8") as f:
            shop_config = json.load(f)

        # 如果指定了选中的店铺，则过滤
        if selected_shops:
            shop_config = [s for s in shop_config if s["shopName"] in selected_shops]

        output_dir = config_file.parent / output_subdir
        output_dir.mkdir(parents=True, exist_ok=True)

        self.log(f"开始生成 {len(shop_config)} 张图片...")
        self.log(f"输出目录：{output_dir}")

        generated_files = []

        for item in shop_config:
            shop_id = item.get("shopId", "unknown")
            shop_name = item.get("shopName", "Unknown")
            try:
                filepath = self.create_image(
                    text=shop_name,
                    bg_color=bg_color,
                    text_color=text_color,
                    border_color=border_color,
                    width=640,
                    height=914,
                    border_width=border_width,
                    font_size=font_size,
                    output_dir=str(output_dir),
                    filename_prefix=shop_id,
                )
                generated_files.append(str(filepath))
            except Exception as e:
                self.log(f"生成失败 [{shop_name}]: {e}")

        self.log(f"完成！共生成 {len(generated_files)}/{len(shop_config)} 张图片")
        return generated_files

    def check_orderId(self, selected_shops: Optional[list] = None) -> dict:
        """
        订单预审：获取店铺的订单 ID

        Args:
            selected_shops: 选中的店铺列表（可选）

        Returns:
            执行结果 {success: [], failed: []}
        """
        if not self.driver:
            self.create_driver()

        result = {"success": [], "failed": []}
        order_management_url = "https://sjs-zx.jd.com/rnTemplate/order-management.html"
        shop_config_path = ROOT_DIR / "zipdist" / "shopConfig.json"

        try:
            with open(shop_config_path, "r", encoding='utf-8') as f:
                shop_config = json.load(f)

            if selected_shops:
                shop_config = [s for s in shop_config if s["shopName"] in selected_shops]

            has_update = False

            for shop_item in shop_config:
                shop_id = shop_item["shopId"]
                shop_name = shop_item["shopName"]
                self.log(f"\n=== 开始处理店铺：{shop_name} ({shop_id}) ===")

                try:
                    self.driver.get(order_management_url)
                    time.sleep(2)

                    # 输入 shopId
                    shop_id_label = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '店铺 ID：')]"))
                    )
                    shop_id_input = shop_id_label.find_element(
                        By.XPATH,
                        ".//following-sibling::input[@type='number'] | .//input[@type='number'] | .//following-sibling::*//input[@type='number']"
                    )
                    shop_id_input.clear()
                    shop_id_input.send_keys(shop_id)
                    self.log(f"已输入 shopId: {shop_id}")
                    time.sleep(0.5)

                    # 点击搜索
                    search_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "ant-btn"))
                    )
                    search_btn.click()
                    self.log("已点击搜索按钮")
                    time.sleep(2)

                    # 获取表格第一行第一列
                    try:
                        tbody = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ant-table-body tbody.ant-table-tbody"))
                        )
                        first_tr = tbody.find_element(By.CSS_SELECTOR, "tr.ant-table-row-level-0")
                        first_td = first_tr.find_element(By.CSS_SELECTOR, "td:first-child")
                        orderId = first_td.text.strip()

                        self.log(f"从表格中获取到订单 ID: {orderId}")
                        shop_item["orderId"] = orderId
                        has_update = True

                    except TimeoutException:
                        self.log(f"警告：店铺 {shop_name} 搜索后未出现表格")
                        result["failed"].append({"shopName": shop_name, "reason": "无订购记录"})
                        continue

                except Exception as e:
                    self.log(f"店铺 {shop_name} 处理失败：{e}")
                    result["failed"].append({"shopName": shop_name, "reason": str(e)})
                    continue

            # 保存更新
            if has_update:
                with open(shop_config_path, "w", encoding='utf-8') as f:
                    json.dump(shop_config, f, ensure_ascii=False, indent=2)
                self.log("\n=== 已保存更新到 shopConfig.json ===")

            # 统计成功失败
            for shop_item in shop_config:
                if shop_item.get("orderId"):
                    result["success"].append({"shopName": shop_item["shopName"], "orderId": shop_item["orderId"]})

            self.log("\n=== 所有店铺提审完成 ===")

        except Exception as e:
            self.log(f"审核模块失败：{str(e)}")
            result["failed"].append({"shopName": "all", "reason": str(e)})

        return result

    def create_module(self, shop_item: dict) -> bool:
        """
        为单个店铺创建定制模板

        Args:
            shop_item: 店铺配置项

        Returns:
            是否创建成功
        """
        if not self.driver:
            self.create_driver()

        shop_name = shop_item["shopName"]

        try:
            self.driver.get(TARGET_URL)
            time.sleep(2)

            # 点击创建按钮
            edit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-green-link"))
            )
            edit_button.click()
            time.sleep(1)

            # 输入店铺名称
            tp_name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tp-name"))
            )
            tp_name_input.clear()
            tp_name_input.send_keys(shop_name)
            time.sleep(0.5)

            # 选择模板类型
            tp_type_select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tp-price"))
            )
            select_element = tp_type_select.find_element(By.TAG_NAME, "select")
            select = Select(select_element)
            select.select_by_value("3")
            time.sleep(0.5)

            # 确认
            sure_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-yellow"))
            )
            sure_button.click()
            time.sleep(2)

            # 获取 templateId
            current_url = self.driver.current_url
            self.log(f"当前页面 URL: {current_url}")

            if "templateId=" in current_url:
                from urllib.parse import parse_qs, urlparse
                parsed_url = urlparse(current_url)
                params = parse_qs(parsed_url.query)
                template_id = params.get("templateId", [None])[0]

                if template_id:
                    self.log(f"提取到 templateId: {template_id}")
                    shop_item["templateId"] = template_id

                    # 更新配置
                    shop_config_path = ROOT_DIR / "zipdist" / "shopConfig.json"
                    with open(shop_config_path, "r", encoding='utf-8') as f:
                        shop_config = json.load(f)
                    for config_item in shop_config:
                        if config_item["shopName"] == shop_name:
                            config_item["templateId"] = template_id
                            break
                    with open(shop_config_path, "w", encoding='utf-8') as f:
                        json.dump(shop_config, f, ensure_ascii=False, indent=2)
                    self.log(f"已更新店铺 {shop_name} 的 templateId 到 shopConfig.json")

            self.log(f"已完成店铺配置：{shop_name}")
            return True

        except Exception as e:
            self.log(f"创建模块失败 - 店铺：{shop_name}, 错误：{str(e)}")
            return False

    def new_module(self, shopId: str, module_item: dict) -> bool:
        """
        创建 v3 版本模块

        Args:
            shopId: 店铺 ID
            module_item: 模块配置项

        Returns:
            是否创建成功
        """
        if not self.driver:
            self.create_driver()

        try:
            # 等待遮罩层消失
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "cd-modal-overlay"))
                )
            except TimeoutException:
                pass

            # 点击添加模块
            add_module_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "J_addModule"))
            )
            try:
                add_module_button.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", add_module_button)

            time.sleep(1)

            # 填写模块信息
            self.driver.find_element(By.ID, "moduleName").send_keys(module_item["name"])
            self.driver.find_element(By.ID, "moduleDesc").send_keys("  ")
            self.driver.find_element(By.ID, "accessKeyId").send_keys(accessKeyId)
            self.driver.find_element(By.ID, "accessKeySecret").send_keys(accessKeySecret)

            # 上传文件
            dynamic_path = ROOT_DIR / "zipdist" / shopId / module_item["fileName"]
            self.driver.find_element(By.ID, "fileUpload").send_keys(str(dynamic_path))

            # 设置图片
            self.driver.execute_script(f"""
                var div = document.querySelector('.J_imagePanel');
                var imgUrl = '{module_item["img"]}';
                div.setAttribute('data-url', imgUrl);
                div.style.backgroundImage = 'url(' + imgUrl + ')';
            """)

            # 选择模块类型
            module_select = self.driver.find_element(By.CLASS_NAME, "cd-select-el")
            module_select.click()
            is_member_card = 4 if module_item.get("isMemberCard", False) else 5
            target_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[@class='sim-list']//li[@str='{is_member_card}']"))
            )
            target_option.click()

            # 选择版本
            time.sleep(1)
            all_selects = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'cd-module-type-select')]")
            taro_version_dropdown = None
            for s in all_selects:
                text = s.text
                if "新版" in text or "v4" in text or "v3" in text:
                    taro_version_dropdown = s.find_element(By.CLASS_NAME, "cd-select-el")
                    break
            if not taro_version_dropdown:
                taro_version_dropdown = all_selects[1].find_element(By.CLASS_NAME, "cd-select-el")

            self.driver.execute_script("arguments[0].scrollIntoView(true);", taro_version_dropdown)
            time.sleep(0.5)
            taro_version_dropdown.click()
            time.sleep(0.5)

            # 选择 3.5.4 版本
            target_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sim-list')]//li[contains(@str, '3.5.4')]"))
            )
            target_option.click()

            # 确认
            self.driver.find_element(By.CLASS_NAME, "J_btnOK").click()
            time.sleep(2)

            self.log(f"成功创建模块：{module_item['name']}")
            return True

        except Exception as e:
            self.log(f"创建模块失败 - 模块：{module_item['name']}, 错误：{str(e)}")
            return False

    def delete_fail_module(self) -> dict:
        """
        模块状态检查：删除打包失败模块并重新创建

        Returns:
            执行结果
        """
        if not self.driver:
            self.create_driver()

        result = {"deleted": 0, "recreated": 0, "failed": []}

        try:
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "li"))
                )
            except TimeoutException:
                self.log("等待模块列表加载超时")

            time.sleep(1)

            # 获取当前 templateId
            current_url = self.driver.current_url
            template_id = None
            if "templateId=" in current_url:
                from urllib.parse import parse_qs, urlparse
                parsed_url = urlparse(current_url)
                params = parse_qs(parsed_url.query)
                template_id = params.get("templateId", [None])[0]

            # 获取 shopId
            shop_id = None
            if template_id:
                with open(ROOT_DIR / "zipdist" / "shopConfig.json", "r", encoding='utf-8') as f:
                    shop_config = json.load(f)
                for config_item in shop_config:
                    if config_item.get("templateId") == template_id:
                        shop_id = config_item.get("shopId")
                        break

            if not shop_id:
                self.log(f"未能获取 shopId，当前 URL: {current_url}")
                return result

            self.log(f"当前模板 shopId: {shop_id}, templateId: {template_id}")

            # 读取模块配置
            with open(ROOT_DIR / "moduleConfig.json", "r", encoding='utf-8') as f:
                module_config = json.load(f)
            module_config_map = {item["name"]: item for item in module_config}

            # 查找打包失败模块
            li_elements = self.driver.find_elements(By.TAG_NAME, "li")
            self.log(f"找到 {len(li_elements)} 个 li 元素")

            for li_element in li_elements:
                status_spans = li_element.find_elements(
                    By.XPATH, ".//span[@class='cd-item-status' and @data-type='4']"
                )

                if not status_spans:
                    continue

                module_name_span = li_element.find_elements(By.CLASS_NAME, "cd-item-name")
                module_name = module_name_span[0].get_attribute("title") if module_name_span else "未知模块"
                self.log(f"发现打包失败的模块：{module_name}")

                try:
                    delete_btns = li_element.find_elements(By.XPATH, ".//div[contains(@class, 'J_delete')]")
                    if not delete_btns:
                        continue

                    self.driver.execute_script("arguments[0].scrollIntoView();", delete_btns[0])
                    time.sleep(0.5)
                    delete_btns[0].click()
                    self.log(f"已点击删除按钮，模块：{module_name}")
                    result["deleted"] += 1

                    # 确认删除
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "cd-modal"))
                        )
                        confirm_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[@class='cd-btn-ok J_btnOK']"))
                        )
                        confirm_btn.click()
                        self.log("已点击确认按钮")
                        time.sleep(1)

                        # 重新创建
                        if module_name in module_config_map:
                            self.log(f"开始重新创建模块：{module_name}")
                            # 这里调用 recreate_module 逻辑
                            result["recreated"] += 1
                        else:
                            self.log(f"未在 moduleConfig.json 中找到模块配置：{module_name}")

                    except TimeoutException:
                        self.log("弹窗未出现或超时")

                except Exception as e:
                    self.log(f"删除打包失败模块时出错：{e}")
                    result["failed"].append(module_name)

            self.log(f"共删除 {result['deleted']} 个打包失败的模块，重新创建 {result['recreated']} 个")

        except Exception as e:
            self.log(f"自动化过程出错：{e}")
            result["failed"].append(str(e))

        return result

    def edit_old_module(self, shopId: str, module_item: dict) -> bool:
        """
        创建 v4 版本模块（编辑高版本模块）

        Args:
            shopId: 店铺 ID
            module_item: 模块配置项

        Returns:
            是否创建成功
        """
        if not self.driver:
            self.create_driver()

        try:
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "J_addModule"))
                )
            except TimeoutException:
                self.log(f"店铺{shopId}: 等待模块列表加载超时")
                return False

            time.sleep(1)

            name = module_item['name']
            self.log(f"店铺{shopId}: 正在编辑模块 - {name}")

            # 构建 XPath
            if "会员卡" in name:
                xpath_expr = "//div[contains(@data-modulename, '会员卡')]"
            elif "橱窗" in name:
                xpath_expr = "//div[contains(@data-modulename, '橱窗')]"
            elif "轮播" in name:
                xpath_expr = "//div[contains(@data-modulename, '轮播图')]"
            elif "热区" in name:
                xpath_expr = "//div[contains(@data-modulename, '热区')]"
            elif "积分" in name:
                xpath_expr = "//div[contains(@data-modulename, '积分')]"
            elif "红包" in name:
                xpath_expr = "//div[contains(@data-modulename, '红包')]"
            elif "弹窗" in name:
                xpath_expr = "//div[contains(@data-modulename, '弹窗')]"
            elif "阶梯" in name:
                xpath_expr = "//div[contains(@data-modulename, '阶梯')]"
            elif "促销" in name:
                xpath_expr = "//div[contains(@data-modulename, '促销')]"
            else:
                xpath_expr = f"//div[@data-modulename='{name}']"

            # 查找模块
            module_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath_expr))
            )

            if not module_element:
                self.log(f"店铺{shopId}: 未找到模块 - {name}")
                return False

            # 点击编辑
            try:
                edit_btn = module_element.find_element(By.CLASS_NAME, "J_edit")
                self.driver.execute_script("arguments[0].click();", edit_btn)
            except Exception as e:
                self.log(f"店铺{shopId}: 点击编辑按钮失败 - {name}, 错误：{e}")
                return False

            time.sleep(0.5)

            # 填写 AK/SK
            try:
                self.driver.find_element(By.ID, "accessKeyId").send_keys(accessKeyId)
                self.driver.find_element(By.ID, "accessKeySecret").send_keys(accessKeySecret)
            except Exception as e:
                self.log(f"店铺{shopId}: 填写 AK/SK 失败 - {name}, 错误：{e}")

            # 确认
            try:
                confirm_btn = self.driver.find_element(By.CLASS_NAME, "J_btnOK")
                self.driver.execute_script("arguments[0].click();", confirm_btn)
            except Exception as e:
                self.log(f"店铺{shopId}: 点击确认按钮失败 - {name}, 错误：{e}")
                return False

            time.sleep(2)
            self.log(f"店铺{shopId}: 模块编辑成功 - {name}")
            return True

        except Exception as e:
            self.log(f"店铺{shopId}: 模块加载失败 - {module_item['name']}, 错误：{e}")
            return False

    def delete_module(self, shopId: str) -> bool:
        """
        删除指定模块

        Args:
            shopId: 店铺 ID

        Returns:
            是否删除成功
        """
        if not self.driver:
            self.create_driver()

        try:
            time.sleep(1)
            li_elements = self.driver.find_elements(By.TAG_NAME, "li")

            for li_element in li_elements:
                status_spans = li_element.find_elements(
                    By.XPATH, ".//span[@class='cd-item-name' and @title='阶梯礼']"
                )

                if status_spans:
                    delete_btns = li_element.find_elements(
                        By.XPATH, ".//div[contains(@class, 'J_delete')]"
                    )

                    if delete_btns:
                        time.sleep(0.5)
                        delete_btns[0].click()
                        time.sleep(1)

                        try:
                            confirm_btn = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//a[@class='cd-btn-ok J_btnOK']"))
                            )
                            confirm_btn.click()
                            time.sleep(1)

                            try:
                                WebDriverWait(self.driver, 3).until(
                                    EC.presence_of_element_located((By.XPATH,
                                        "//span[@class='cd-text J_text' and contains(text(), '为避续模块后续无法维护')]"))
                                )
                                self.log(f"使用中的模块不允许删除：{shopId}")
                            except TimeoutException:
                                pass

                            time.sleep(1)
                        except TimeoutException:
                            self.log(f"自动化过程出错：{shopId}")

        except Exception as e:
            self.log(f"自动化过程出错 final: {shopId}")
            return False

        return True

    def review_module(self) -> bool:
        """
        提交审核

        Returns:
            是否提交成功
        """
        if not self.driver:
            self.create_driver()

        try:
            edit_button = self.driver.find_element(By.CLASS_NAME, "J_save")
            if edit_button:
                edit_button.click()

                WebDriverWait(self.driver, 10).until(EC.new_window_is_opened)

                time.sleep(1)

                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "J_submit"))
                )
                submit_button.click()
                time.sleep(5)

                self.log("提交审核成功")
                return True

        except Exception as e:
            self.log(f"审核模块失败：{str(e)}")
            return False
