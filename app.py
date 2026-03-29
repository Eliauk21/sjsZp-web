"""
sjsZp Web 应用 - Streamlit 版本
一条命令启动：streamlit run app.py
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import sys

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from core.sjsZp_core import SjsZpCore
from services.notify_service import send_wechat_notify, send_task_notify, load_webhook, save_webhook

# 页面配置
st.set_page_config(
    page_title="sjsZp 管理工具",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .stAlert {margin-bottom: 0.5rem;}
    .block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)

# 初始化 session state
if "task_history" not in st.session_state:
    st.session_state.task_history = []
if "current_task_log" not in st.session_state:
    st.session_state.current_task_log = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# 数据文件路径
SHOP_ALL_CONFIG = ROOT_DIR / "shopAllConfig.json"
MODULE_CONFIG = ROOT_DIR / "moduleConfig.json"
SHOP_CONFIG = ROOT_DIR / "zipdist" / "shopConfig.json"
TASK_HISTORY_FILE = ROOT_DIR / "data" / "task_history.json"


def load_json_file(path: Path) -> list:
    """加载 JSON 文件"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"加载文件失败：{e}")
        return []


def save_json_file(path: Path, data: list) -> bool:
    """保存 JSON 文件"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存文件失败：{e}")
        return False


def add_task_record(record: dict):
    """添加任务记录"""
    # 加载历史
    try:
        with open(TASK_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        history = []

    history.append(record)
    with open(TASK_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    st.session_state.task_history = history


def log_message(message: str):
    """日志输出"""
    st.session_state.current_task_log.append(message)


# 侧边栏菜单
st.sidebar.title("🛒 sjsZp 管理工具")

menu = st.sidebar.radio(
    "导航",
    ["📊 数据面板", "📁 数据维护", "⚙️ 任务操作", "🔧 系统设置"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# 显示 webhook 配置状态
webhook = load_webhook()
if webhook:
    st.sidebar.success("✅ 企微通知已配置")
else:
    st.sidebar.warning("⚠️ 企微通知未配置")


# ==================== 数据面板 ====================
if menu == "📊 数据面板":
    st.title("📊 数据面板")

    # 加载任务历史
    try:
        with open(TASK_HISTORY_FILE, "r", encoding="utf-8") as f:
            task_history = json.load(f)
        st.session_state.task_history = task_history
    except:
        task_history = []

    # 统计卡片
    col1, col2, col3 = st.columns(3)
    total_tasks = len(task_history)
    success_tasks = len([t for t in task_history if t.get("status") == "success"])
    failed_tasks = len([t for t in task_history if t.get("status") == "failed"])

    col1.metric("总任务数", total_tasks)
    col2.metric("成功", success_tasks, delta_color="normal")
    col3.metric("失败", failed_tasks, delta="-inverse")

    st.markdown("---")

    # 历史任务表格
    st.subheader("历史任务记录")
    if task_history:
        # 反转显示（最新的在前）
        for task in reversed(task_history):
            with st.expander(
                f"**{task.get('task_name', '未知任务')}** - {task.get('start_time', '')} - "
                f"{'✅' if task.get('status') == 'success' else '❌' if task.get('status') == 'failed' else '⏳'}"
            ):
                st.write(f"**操作类型**: {task.get('operation', '')}")
                st.write(f"**涉及店铺**: {task.get('shop_count', 0)} 家")
                st.write(f"**开始时间**: {task.get('start_time', '')}")
                st.write(f"**结束时间**: {task.get('end_time', '')}")
                st.code(task.get('log', ''), language="text")
    else:
        st.info("暂无任务记录")

    # 当前任务进度
    st.markdown("---")
    st.subheader("当前任务进度")
    if st.session_state.is_running:
        st.warning("⏳ 任务执行中...")
        st.progress(100, text="正在执行")
        if st.session_state.current_task_log:
            st.code("\n".join(st.session_state.current_task_log[-50:]), language="text")
    else:
        st.info("暂无执行中的任务")


# ==================== 数据维护 ====================
elif menu == "📁 数据维护":
    submenu = st.sidebar.selectbox(
        "数据维护",
        ["➕ 新增入驻店铺", "📜 历史入驻店铺", "🧩 模块一览"]
    )

    # --- 新增入驻店铺 ---
    if submenu == "➕ 新增入驻店铺":
        st.title("➕ 新增入驻店铺")
        st.markdown("管理当前任务店铺配置 (`zipdist/shopConfig.json`)")

        shops = load_json_file(SHOP_CONFIG)

        # JSON 导入
        with st.expander("📥 JSON 一键导入"):
            uploaded_file = st.file_uploader("上传 JSON 文件", type=["json"])
            if uploaded_file:
                try:
                    imported_data = json.load(uploaded_file)
                    if st.button("确认导入"):
                        if save_json_file(SHOP_CONFIG, imported_data):
                            st.success("导入成功！")
                            shops = imported_data
                except Exception as e:
                    st.error(f"导入失败：{e}")

        # 可编辑表格
        st.markdown("### 店铺列表")
        edited_shops = st.data_editor(
            shops,
            num_rows="dynamic",
            use_container_width=True,
            height=400
        )

        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存修改", type="primary", use_container_width=True):
                if save_json_file(SHOP_CONFIG, edited_shops.to_dict('records')):
                    st.success("保存成功！")
                    shops = edited_shops.to_dict('records')

        with col2:
            if st.button("➕ 添加一行", use_container_width=True):
                # 添加空行逻辑由 data_editor 处理
                pass

    # --- 历史入驻店铺 ---
    elif submenu == "📜 历史入驻店铺":
        st.title("📜 历史入驻店铺")
        st.markdown("管理历史店铺配置 (`shopAllConfig.json`)")

        all_shops = load_json_file(SHOP_ALL_CONFIG)

        # 同步按钮
        if st.button("🔄 同步新增店铺到历史"):
            current_shops = load_json_file(SHOP_CONFIG)
            # 合并逻辑：将新增店铺添加到历史（如果不存在）
            existing_ids = {s["shopId"] for s in all_shops}
            for shop in current_shops:
                if shop["shopId"] not in existing_ids:
                    all_shops.append(shop)
            if save_json_file(SHOP_ALL_CONFIG, all_shops):
                st.success("同步成功！")

        st.markdown("### 历史店铺列表")
        edited_all_shops = st.data_editor(
            all_shops,
            num_rows="dynamic",
            use_container_width=True,
            height=500
        )

        if st.button("💾 保存修改", type="primary"):
            if save_json_file(SHOP_ALL_CONFIG, edited_all_shops.to_dict('records')):
                st.success("保存成功！")
                all_shops = edited_all_shops.to_dict('records')

    # --- 模块一览 ---
    elif submenu == "🧩 模块一览":
        st.title("🧩 模块一览")
        st.markdown("管理模块配置 (`moduleConfig.json`)")

        modules = load_json_file(MODULE_CONFIG)

        st.markdown("### 模块列表")
        edited_modules = st.data_editor(
            modules,
            num_rows="dynamic",
            use_container_width=True,
            height=400
        )

        # 文件上传
        st.markdown("### 上传模块文件")
        shop_select = st.selectbox(
            "选择店铺",
            [s["shopId"] for s in load_json_file(SHOP_CONFIG)],
            format_func=lambda x: f"{x}"
        )
        uploaded_zip = st.file_uploader("上传 zip 文件", type=["zip"])
        if uploaded_zip and st.button("上传"):
            save_path = ROOT_DIR.parent / "zipdist" / shop_select / uploaded_zip.name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded_zip.getvalue())
            st.success(f"已上传到 {save_path}")

        if st.button("💾 保存修改", type="primary"):
            if save_json_file(MODULE_CONFIG, edited_modules.to_dict('records')):
                st.success("保存成功！")
                modules = edited_modules.to_dict('records')

        # 模块图片预览
        if modules:
            st.markdown("### 模块图片预览")
            cols = st.columns(min(5, len(modules)))
            for i, module in enumerate(modules):
                with cols[i % len(cols)]:
                    st.image(module.get("img", ""), caption=module.get("name", ""), use_container_width=True)


# ==================== 任务操作 ====================
elif menu == "⚙️ 任务操作":
    submenu = st.sidebar.selectbox(
        "任务操作",
        ["🖼️ 图片生成",
         "📋 店铺订单预审",
         "🏪 创建店铺模板",
         "📦 创建 v3 版本模块",
         "🔍 模块状态检查",
         "🆕 创建 v4 版本模块",
         "🗑️ 删除指定模块",
         "✅ 提交审核"]
    )

    # 任务执行区域
    def execute_task_wrapper(task_name: str, operation: str, func, *args, **kwargs):
        """任务执行包装器"""
        st.session_state.is_running = True
        st.session_state.current_task_log = []

        log_area = st.empty()
        progress_bar = st.progress(0, text="准备执行...")

        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # 发送开始通知
            send_wechat_notify(f"🚀 任务开始：{task_name}\n时间：{start_time}")

            # 创建核心实例
            core = SjsZpCore(log_callback=lambda msg: log_message(msg))

            # 执行任务
            result = func(*args, **kwargs)

            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 更新日志显示
            log_area.code("\n".join(st.session_state.current_task_log[-50:]), language="text")
            progress_bar.progress(100, text="执行完成")

            # 记录任务
            record = {
                "task_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "task_name": task_name,
                "operation": operation,
                "shop_count": kwargs.get("shop_count", 0),
                "status": "success",
                "start_time": start_time,
                "end_time": end_time,
                "log": "\n".join(st.session_state.current_task_log)
            }
            add_task_record(record)

            # 发送完成通知
            send_task_notify(task_name, "success", kwargs.get("shop_count", 0),
                           len(result.get("success", [])) if isinstance(result, dict) else 0,
                           len(result.get("failed", [])) if isinstance(result, dict) else 0)

            st.success(f"✅ 任务完成！")
            return result

        except Exception as e:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message(f"❌ 错误：{e}")
            log_area.code("\n".join(st.session_state.current_task_log[-50:]), language="text")

            # 记录失败
            record = {
                "task_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "task_name": task_name,
                "operation": operation,
                "shop_count": kwargs.get("shop_count", 0),
                "status": "failed",
                "start_time": start_time,
                "end_time": end_time,
                "log": "\n".join(st.session_state.current_task_log)
            }
            add_task_record(record)

            # 发送失败通知
            send_task_notify(task_name, "failed", kwargs.get("shop_count", 0), 0, 1, str(e))

            st.error(f"❌ 任务失败：{e}")
            return None

        finally:
            st.session_state.is_running = False
            core.close_driver()

    # --- 图片生成 ---
    if submenu == "🖼️ 图片生成":
        st.title("🖼️ 图片生成")

        mode = st.radio("生成模式", ["批量生成", "单张生成"])

        if mode == "批量生成":
            shops = load_json_file(SHOP_CONFIG)
            selected_shops = st.multiselect(
                "选择店铺",
                [s["shopName"] for s in shops],
                default=[s["shopName"] for s in shops]
            )

            if st.button("开始生成", type="primary"):
                core = SjsZpCore(log_callback=lambda msg: log_message(msg))
                st.session_state.is_running = True
                st.session_state.current_task_log = []

                log_area = st.empty()
                files = core.generate_batch(selected_shops=selected_shops)

                log_area.code("\n".join(st.session_state.current_task_log), language="text")
                st.success(f"生成完成！共 {len(files)} 张图片")

                st.session_state.is_running = False
                core.close_driver()

                # 显示生成的图片
                if files:
                    st.markdown("### 生成的图片")
                    cols = st.columns(5)
                    for i, f in enumerate(files[:10]):  # 只显示前 10 张
                        with cols[i % 5]:
                            st.image(f, use_container_width=True)

        else:
            st.text_input("店铺名称", key="single_shop_name")
            st.color_picker("背景颜色", "#ffffff", key="bg_color")
            st.color_picker("文字颜色", "#000000", key="text_color")
            st.color_picker("围边颜色", "#000000", key="border_color")
            st.slider("围边宽度", 0, 50, 20, key="border_width")
            st.slider("字体大小", 20, 100, 40, key="font_size")

            if st.button("生成图片"):
                core = SjsZpCore()
                shop_name = st.session_state.get("single_shop_name", "Test")
                filepath = core.create_image(
                    text=shop_name,
                    bg_color=st.session_state.bg_color,
                    text_color=st.session_state.text_color,
                    border_color=st.session_state.border_color,
                    border_width=st.session_state.border_width,
                    font_size=st.session_state.font_size,
                )
                if filepath:
                    st.image(str(filepath), use_container_width=True)
                core.close_driver()

    # --- 店铺订单预审 ---
    elif submenu == "📋 店铺订单预审":
        st.title("📋 店铺订单预审")

        shops = load_json_file(SHOP_CONFIG)
        st.warning(f"当前操作对象为新增入驻店铺，共 {len(shops)} 家")

        with st.expander("📝 预览店铺数据"):
            st.dataframe(shops)

        if st.button("开始审核", type="primary"):
            result = execute_task_wrapper(
                "店铺订单预审",
                "check_orderId",
                lambda: SjsZpCore(log_callback=lambda msg: log_message(msg)).check_orderId(),
                shop_count=len(shops)
            )
            if result:
                st.json(result)

    # --- 创建店铺模板 ---
    elif submenu == "🏪 创建店铺模板":
        st.title("🏪 创建店铺模板")

        shops = load_json_file(SHOP_CONFIG)
        st.warning(f"当前操作对象为新增入驻店铺，共 {len(shops)} 家")

        with st.expander("📝 预览店铺数据"):
            st.dataframe(shops)

        if st.button("开始创建", type="primary"):
            st.info("将逐个为店铺创建模板，请勿关闭浏览器")
            # 需要用户手动在浏览器中完成验证码

    # --- 创建 v3 版本模块 ---
    elif submenu == "📦 创建 v3 版本模块":
        st.title("📦 创建 v3 版本模块")

        modules = load_json_file(MODULE_CONFIG)
        shops = load_json_file(SHOP_CONFIG)

        st.warning(f"将使用模块一览的配置，为 {len(shops)} 家店铺创建模块")

        selected_modules = st.multiselect(
            "选择要创建的模块",
            [m["name"] for m in modules],
            default=[m["name"] for m in modules]
        )

        if st.button("开始创建", type="primary"):
            st.info("需要登录并手动完成验证码")

    # --- 模块状态检查 ---
    elif submenu == "🔍 模块状态检查":
        st.title("🔍 模块状态检查")
        st.info("检查新增店铺模块的创建情况，删除打包失败的模块并重新创建")

        shops = load_json_file(SHOP_CONFIG)
        st.warning(f"当前操作对象为新增入驻店铺，共 {len(shops)} 家")

        if st.button("开始检查", type="primary"):
            st.info("需要先在浏览器中打开模板编辑页面")

    # --- 创建 v4 版本模块 ---
    elif submenu == "🆕 创建 v4 版本模块":
        st.title("🆕 创建 v4 版本模块")
        st.info("编辑高版本模块（v4 版本）")

        shops = load_json_file(SHOP_CONFIG)
        st.warning(f"当前操作对象为新增入驻店铺，共 {len(shops)} 家")

        if st.button("开始创建", type="primary"):
            st.info("需要登录并手动完成验证码")

    # --- 删除指定模块 ---
    elif submenu == "🗑️ 删除指定模块":
        st.title("🗑️ 删除指定模块")

        modules = load_json_file(MODULE_CONFIG)
        selected_modules = st.multiselect(
            "选择要删除的模块",
            [m["name"] for m in modules]
        )

        if selected_modules:
            st.warning(f"将删除所有店铺中选中的 {len(selected_modules)} 个模块，确认继续？")
            if st.button("确认删除", type="primary"):
                st.info("需要登录并在浏览器中执行")

    # --- 提交审核 ---
    elif submenu == "✅ 提交审核":
        st.title("✅ 提交审核")

        all_shops = load_json_file(SHOP_ALL_CONFIG)
        st.warning(f"当前操作对象为历史入驻店铺，共 {len(all_shops)} 家")

        with st.expander("📝 预览店铺数据"):
            st.dataframe(all_shops)

        if st.button("开始提审", type="primary"):
            st.info("需要登录并在浏览器中执行提审操作")


# ==================== 系统设置 ====================
elif menu == "🔧 系统设置":
    st.title("🔧 系统设置")

    st.markdown("### 企业微信通知配置")

    current_webhook = load_webhook()
    new_webhook = st.text_input(
        "企业微信机器人 Webhook URL",
        value=current_webhook,
        placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
        help="在企业微信中创建群机器人，获取 Webhook 地址"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存配置"):
            if save_webhook(new_webhook):
                st.success("保存成功！")
            else:
                st.error("保存失败")

    with col2:
        if st.button("🧪 测试通知"):
            if new_webhook:
                result = send_wechat_notify("## sjsZp 测试通知\n这是一条测试消息")
                if result:
                    st.success("发送成功！")
                else:
                    st.error("发送失败，请检查 Webhook URL")
            else:
                st.warning("请先输入 Webhook URL")

    st.markdown("---")
    st.markdown("### 浏览器配置")
    st.info("Edge 浏览器路径：`C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe`")
    st.info("Edge Driver 路径：项目根目录下的 `msedgedriver.exe`")
