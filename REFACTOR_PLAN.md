# sjsZp Web 重构计划

## 技术栈
- **前端**: Vite + React + TypeScript + Ant Design + Fusion Design
- **后端**: Flask (REST API)
- **通信**: Axios + WebSocket (实时日志)

## 项目结构

```
sjsZp-web/
├── backend/                    # Flask 后端
│   ├── app.py                  # Flask 主应用
│   ├── api/                    # API 路由
│   │   ├── shop.py             # 店铺管理 API
│   │   ├── module.py           # 模块管理 API
│   │   ├── task.py             # 任务执行 API
│   │   └── settings.py         # 设置 API
│   ├── services/
│   │   ├── sjsZp_service.py    # 核心业务逻辑
│   │   └── notify_service.py   # 企微通知
│   ├── models/
│   │   └── schema.py           # 数据模型
│   └── data/                   # 数据文件
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/         # 可复用组件
│   │   ├── pages/              # 页面组件
│   │   │   ├── Dashboard.tsx   # 数据面板
│   │   │   ├── NewShops.tsx    # 新增入驻店铺
│   │   │   ├── HistoryShops.tsx # 历史入驻店铺
│   │   │   ├── Modules.tsx     # 模块一览
│   │   │   ├── Tasks/          # 任务操作页面
│   │   │   └── Settings.tsx    # 系统设置
│   │   ├── services/           # API 服务
│   │   ├── store/              # 状态管理
│   │   ├── types/              # TypeScript 类型
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
└── start.bat                   # 启动脚本
```

## API 设计

### 店铺管理
- GET /api/shops/current - 获取新增入驻店铺
- POST /api/shops/current - 保存新增入驻店铺
- GET /api/shops/history - 获取历史入驻店铺
- POST /api/shops/history - 保存历史入驻店铺
- POST /api/shops/sync - 同步新增到历史

### 模块管理
- GET /api/modules - 获取模块列表
- POST /api/modules - 保存模块配置
- POST /api/modules/upload - 上传模块文件

### 任务执行
- POST /api/tasks/execute - 执行任务
- GET /api/tasks/history - 获取任务历史
- GET /api/tasks/:id/logs - 获取任务日志 (WebSocket)

### 设置
- GET /api/settings - 获取配置
- POST /api/settings - 保存配置
- POST /api/settings/webhook/test - 测试 webhook

## UI 设计

### 布局
- 左侧：侧边栏菜单 (Ant Design Menu)
- 顶部：面包屑 + 用户信息
- 中间：内容区域

### 菜单结构
```
📊 数据面板
📁 数据维护
  ├── ➕ 新增入驻店铺
  ├── 📜 历史入驻店铺
  └── 🧩 模块一览
⚙️ 任务操作
  ├── 🖼️ 图片生成
  ├── 📋 店铺订单预审
  ├── 🏪 创建店铺模板
  ├── 📦 创建 v3 版本模块
  ├── 🔍 模块状态检查
  ├── 🆕 创建 v4 版本模块
  ├── 🗑️ 删除指定模块
  └── ✅ 提交审核
🔧 系统设置
```

### 数据面板
- 统计卡片 (Ant Design Statistic)
- 任务历史表格 (Ant Design Table)
- 实时日志区 (Ant Design Typography)

### 数据维护页面
- 可编辑表格 (Ant Design EditableTable)
- 导入导出按钮 (Ant Design Upload)
- 模块图片预览 (Ant Design Image)

### 任务操作页面
- 表单配置 (Ant Design Form)
- 进度条 (Ant Design Progress)
- 实时日志 (Ant Design Console)
- 结果展示 (Ant Design Result)
