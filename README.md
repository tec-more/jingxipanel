# 井溪畅联管理后台 (AIPanelAdmin)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![openGauss](https://img.shields.io/badge/openGauss-3.0+-E5A20E?style=for-the-badge)](https://opengauss.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

**井溪畅联管理后台**是一个基于 FastAPI + Vue 3 构建的企业级 AI 应用管理平台，集成了智能体开发、大模型管理、CRM、MES、财务、审批、审计等丰富的业务模块，采用插件化架构，支持灵活扩展。

---

## ✨ 功能特性

### 🤖 AI 智能体平台
- **智能体管理**: 创建、配置和管理 AI Agent，支持多种类型
- **工作流 & 对话流**: 可视化构建 Agent 工作流和对话流程图
- **技能管理**: 为 Agent 定义可复用的技能
- **工具系统**: 内置工具注册表，支持自定义工具扩展
- **记忆管理**: Agent 长期/短期记忆存储
- **RAG 知识库**: 检索增强生成，支持向量数据库（Qdrant）
- **LangGraph 集成**: 基于 LangGraph 的复杂 Agent 编排

### 🧠 大模型管理
- **多厂商支持**: OpenAI、百度千帆、阿里通义、腾讯混元、火山方舟、本地模型等
- **模型配置**: 统一管理模型参数和 API 密钥
- **用量统计**: 实时追踪 Token 消耗和成本计算
- **语音服务**: 支持 TTS/ASR 语音合成与识别

### 💼 业务模块
| 模块 | 功能说明 |
|------|---------|
| **CRM** | 线索、商机、活动、联系人、跟进任务、统计分析 |
| **销售管理** | 订单管理、销售统计 |
| **产品管理** | 产品信息、分类、属性、变体 |
| **客户管理** | 客户档案、会员管理、VIP 等级 |
| **采购管理** | 采购订单、供应商管理 |
| **库存管理** | 批次管理、库存量化 |
| **财务管理** | 总账、应收应付、资产、存货成本、资金票据、报表、费用报销、税务发票 |
| **MES 制造** | 基础数据、生产计划、生产执行、生产报工、物料流转、生产追溯、异常管理 |
| **MRP2** | 物料需求计划、主生产计划、能力需求计划 |
| **设备管理** | 设备台账、维护保养、故障管理 |
| **质量管理** | 质量检测与管理 |
| **审批流程** | 多级审批引擎、流程规则配置、全局审批拦截 |
| **消息中心** | 站内消息、关注者、通知、事件映射 |
| **文档管理** | 文档上传、版本控制、分类目录、在线预览 |
| **审计追踪** | 全链路追踪、审计日志、数据变更、登录审计、风险审计 |
| **支付集成** | 支付宝、微信支付、七象支付 |
| **第三方对接** | Dify、Coze 等第三方平台对接 |

### 🏗️ 平台能力
- **插件化架构**: 所有业务模块以插件形式动态加载，支持启用/禁用
- **RBAC 权限**: 基于角色的细粒度权限控制，支持按钮级权限
- **部门管理**: 组织架构管理
- **系统安装向导**: Web 端可视化安装，5 步完成部署
- **API 文档**: 自动生成 OpenAPI 文档，支持 Swagger UI / ReDoc
- **多数据库**: 同时支持 PostgreSQL 和 openGauss
- **监控集成**: Prometheus + OpenTelemetry 全链路监控
- **消息队列**: RabbitMQ 事件总线
- **缓存支持**: Redis 缓存可选

---

## 📁 目录结构

```
jingxipanel/
├── base/                          # 后端核心代码
│   ├── cli/                      # 命令行工具
│   ├── common/                   # 公共模块
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── security.py           # 安全认证
│   │   ├── middleware.py         # 中间件
│   │   ├── response.py           # 统一响应格式
│   │   ├── cache.py              # 缓存管理
│   │   ├── log.py                # 日志配置
│   │   └── plugin_manager.py     # 插件管理器
│   ├── core/                     # 核心业务模块
│   │   ├── dept/                 # 部门管理
│   │   ├── install/              # 系统安装向导
│   │   ├── extension/            # 插件扩展
│   │   └── users/                # 用户与权限（RBAC）
│   └── plugins/                  # 业务插件（22+ 模块）
│       ├── agent/                # AI 智能体
│       ├── llm/                  # 大模型管理
│       ├── crm/                  # 客户关系管理
│       ├── finance/              # 财务管理
│       ├── mes/                  # 制造执行系统
│       ├── audit/                # 审计追踪
│       ├── approval/             # 审批流程
│       ├── mail/                 # 消息中心
│       ├── document/             # 文档管理
│       ├── sales/                # 销售管理
│       ├── customer/             # 客户管理
│       ├── product/              # 产品管理
│       ├── purchase/             # 采购管理
│       ├── inventory/            # 库存管理
│       ├── mrp2/                 # MRP 物料需求
│       ├── equipment/            # 设备管理
│       ├── quality/              # 质量管理
│       ├── subcontracting/       # 分包管理
│       ├── thirdparty/           # 第三方对接
│       ├── alipay/               # 支付宝
│       ├── wechat_pay/           # 微信支付
│       └── qixiang_pay/          # 七象支付
├── web/                          # 前端代码（Vue 3 + Element Plus）
│   ├── src/
│   │   ├── api/                  # API 接口封装
│   │   ├── components/           # 公共组件
│   │   ├── views/                # 页面视图
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── router/               # 路由配置
│   │   └── utils/                # 工具函数
│   └── package.json
├── deploy/                       # 部署配置
│   └── openguass/                # openGauss Docker 配置
├── migrations/                  # 数据库迁移脚本
├── monitoring/                   # 监控配置（Prometheus 等）
├── rabbitmq/                     # RabbitMQ Docker 配置
├── config.conf                   # 系统配置文件（自动生成）
├── requirements.txt              # Python 依赖
├── run.py                        # 启动入口
└── pyproject.toml                # 项目配置（含 Aerich 迁移配置）
```

---

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| FastAPI | 0.115+ | Web 框架 |
| Tortoise ORM | 0.23+ | 异步 ORM |
| asyncpg | - | PostgreSQL/openGauss 驱动 |
| Pydantic | 2.x | 数据验证 |
| Loguru | 0.7+ | 日志框架 |
| python-jose | 3.5+ | JWT 认证 |
| passlib[bcrypt] | - | 密码加密 |
| LangChain | 0.3+ | LLM 应用框架 |
| LangGraph | 1.2+ | Agent 编排 |
| psycopg | 3.x | PostgreSQL 驱动（LangGraph 用） |
| uvicorn | 0.34+ | ASGI 服务器 |
| Prometheus Client | - | 指标监控 |
| OpenTelemetry | - | 链路追踪 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.4+ | 前端框架 |
| Element Plus | 2.4+ | UI 组件库 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.6+ | HTTP 客户端 |
| ECharts | 6.x | 数据可视化 |
| Vue Flow | 1.x | 流程图绘制 |
| Vite | 5.x | 构建工具 |
| Sass | 1.x | CSS 预处理 |

### 数据库 & 基础设施

| 技术 | 用途 |
|------|------|
| PostgreSQL 12+ / openGauss 3.0+ | 关系型数据库 |
| Redis | 缓存（可选） |
| RabbitMQ | 消息队列（可选） |
| Qdrant | 向量数据库（可选） |
| Docker | 容器化部署 |

---

## 📋 环境要求

| 软件 | 最低版本 | 推荐版本 | 说明 |
|------|---------|---------|------|
| Python | 3.8 | 3.10+ | 后端运行环境 |
| PostgreSQL | 12 | 14+ | 数据库（也支持 openGauss） |
| openGauss | 3.0 | 5.0+ | 国产数据库替代方案 |
| Node.js | 16 | 18+ | 前端构建环境 |
| npm | 8 | 9+ | 前端包管理 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd jingxipanel
```

### 2. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt
```

### 3. 配置数据库

#### 方式一：Docker 快速部署 openGauss（推荐）

```bash
cd deploy/openguass
docker-compose up -d
```

openGauss 将在 `15432` 端口启动，默认密码 `Admin@123456`。

#### 方式二：使用已有 PostgreSQL/openGauss

确保数据库已创建且用户拥有相应权限。

### 4. 启动后端服务

```bash
python run.py
```

服务默认启动在 `http://127.0.0.1:9998`。

首次启动时访问 `http://127.0.0.1:9998/install` 进入安装向导。

### 5. 构建/启动前端（可选）

#### 开发模式

```bash
cd web
npm install
npm run dev
```

前端开发服务默认启动在 `http://127.0.0.1:3000`。

#### 生产构建

```bash
cd web
npm install
npm run build
```

构建产物输出到 `web/dist` 目录，后端会自动托管静态文件。

---

## 🌱 系统安装向导

本系统提供了友好的 Web 安装向导，可通过浏览器访问完成系统初始化配置。

### 安装前准备

- ✅ Python 3.8+ 已安装
- ✅ PostgreSQL 或 openGauss 数据库已部署且可访问
- ✅ 数据库用户拥有创建数据库和表的权限
- ✅ `config.conf` 文件所在目录有写入权限

### 启动安装向导

1. **首次启动服务**
   ```bash
   python run.py
   ```

2. **访问安装页面**

   打开浏览器，访问：`http://127.0.0.1:9998/install`

   如果使用前端开发服务器：`http://127.0.0.1:3000/install`

3. **按步骤完成安装**

### 安装步骤详解

#### 第一步：环境检测

安装向导自动检测运行环境：
- 操作系统版本与兼容性
- Python 版本
- 配置目录、存储目录、日志目录的写入权限
- 数据库连接性提示

如果检测项显示异常 ❌，请根据提示解决问题后再继续。

#### 第二步：数据库配置

填写数据库连接信息：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| 主机地址 | `127.0.0.1` | 数据库服务器 IP |
| 端口 | `15432` | PostgreSQL 默认 5432，openGauss 默认 15432 |
| 数据库名 | `jingxipanel` | 系统数据库名称 |
| 用户名 | `admin` | 数据库用户名 |
| 密码 | - | 数据库密码 |
| 最小连接数 | `5` | 连接池最小连接数 |
| 最大连接数 | `20` | 连接池最大连接数 |
| 超时时间 | `30` | 连接超时秒数 |
| 命令超时 | `30` | 命令执行超时秒数 |

配置完成后，点击 **"测试连接"** 按钮验证数据库连接是否正常。

#### 第三步：管理员设置

配置系统管理员账户：

- **用户名**: 登录用户名（3-20 字符）
- **密码**: 登录密码（至少 8 位）
- **确认密码**: 再次输入密码
- **昵称**: 管理员显示名称
- **邮箱**: 管理员邮箱地址

#### 第四步：完成安装

点击 **"开始安装"** 按钮，系统将自动执行：
1. 写入配置文件 `config.conf`
2. 初始化数据库连接
3. 创建系统数据表
4. 同步插件模型与菜单
5. 创建管理员账户
6. 标记系统为已安装
7. 触发系统重启

安装过程大约需要 30 秒，请耐心等待。

#### 第五步：安装完成

看到成功页面即表示安装完成，点击 **"前往登录"** 按钮进入登录页面。

### 重新安装

如需重新安装，有两种方式：

**方式一：API 重置**
```bash
# 调用重置接口
curl -X POST http://127.0.0.1:9998/api/v1/install/reset
```

**方式二：手动清除**
```bash
# 删除安装标记文件
rm -f .installed
# 清空数据库（谨慎操作！）
```

---

## ⚙️ 配置文件说明

`config.conf` 包含系统所有配置项，安装完成后自动生成。

### 完整配置示例

```ini
[app]
name = 井溪畅联管理后台
version = v0.1.0
debug = false                # 调试模式，生产环境建议关闭
frontend_name = 井溪畅联
backend_name = 井溪畅联管理后台

[db]
db_host = 127.0.0.1          # 数据库主机
db_port = 15432              # 数据库端口
db_name = jingxipanel        # 数据库名
db_user = admin              # 用户名
db_password = Admin@123      # 密码
minsize = 5                  # 最小连接数
maxsize = 20                 # 最大连接数
timeout = 30                 # 连接超时（秒）
command_timeout = 30         # 命令超时（秒）

[storage]
path = ./storage             # 文件存储路径

[log]
path = ./logs                # 日志路径

[redis]
enabled = false              # 是否启用 Redis
host = 127.0.0.1
port = 6379
password =
db = 0

[email]
enabled = true              # 邮件服务
smtp_host = smtp.example.com
smtp_port = 465
smtp_use_tls = false
sender_email = admin@example.com
sender_password = your-password
sender_name = AIPanelAdmin

[qdrant]
enabled = false             # 向量数据库
host = http://localhost:6333
api_key =
timeout = 300

[audit]
enabled = true             # 审计日志
retention_days = 90
log_http_requests = true
log_data_changes = true
log_login = true

[monitoring]
prometheus_enabled = false  # Prometheus 监控
prometheus_port = 9090

[rabbitmq]
enabled = false             # 消息队列
host = 127.0.0.1
port = 5672
virtual_host = /
username = admin
password = Admin@123
```

### 配置模块说明

| 模块 | 说明 | 是否必填 |
|------|------|---------|
| `[app]` | 应用名称、版本、调试模式 | 是 |
| `[db]` | 数据库连接配置 | 是 |
| `[storage]` | 文件存储路径 | 是 |
| `[log]` | 日志路径 | 是 |
| `[redis]` | Redis 缓存 | 否 |
| `[email]` | 邮件服务 | 否 |
| `[qdrant]` | 向量数据库 | 否 |
| `[audit]` | 审计日志配置 | 是 |
| `[monitoring]` | Prometheus 监控 | 否 |
| `[rabbitmq]` | 消息队列 | 否 |

---

## 🔌 插件系统

本系统采用插件化架构设计，所有业务模块以独立插件形式存在。

### 插件结构

```
plugins/<plugin_name>/
├── api/v1/           # API 路由
├── models/           # 数据模型
├── schemas/          # 请求/响应结构
├── services/         # 业务逻辑
├── manifest.json     # 插件清单（元数据、菜单、权限、路由等）
└── __init__.py
```

### 插件清单 (manifest.json)

每个插件通过 `manifest.json` 声明自身元数据：

```json
{
    "name": "my_plugin",
    "display_name": "我的插件",
    "version": "1.0.0",
    "description": "插件描述",
    "author": "author",
    "route_prefix": "/v1/my-plugin",
    "routes": ["api/v1"],
    "models": ["my_model"],
    "schemas": ["my_schema"],
    "menus": [...],
    "permissions": [...],
    "hooks": {
        "on_enable": "on_enable",
        "on_disable": "on_disable",
        "on_startup": "on_startup",
        "on_shutdown": "on_shutdown"
    },
    "config": {}
}
```

### 插件功能

- **动态加载**: 启动时自动扫描并加载 `plugins/` 目录下的所有插件
- **启用/禁用**: 通过后台管理界面或 API 动态启用/禁用插件
- **菜单注册**: 插件自动注册前端菜单到侧边栏
- **权限注册**: 插件自动注册权限码到 RBAC 系统
- **数据库迁移**: 插件模型自动同步到数据库
- **生命周期钩子**: `on_startup` / `on_shutdown` / `on_enable` / `on_disable`

### 已有插件一览

| 插件 | 显示名称 | 路由前缀 | 说明 |
|------|---------|---------|------|
| agent | 智能体管理 | /v1/agent | Agent 开发平台 |
| llm | 大模型管理 | /v1/llm | 多厂商 LLM 管理 |
| crm | CRM 管理 | /v1/crm | 线索/商机/联系人 |
| finance | 财务管理 | /v1/finance | 总账/报表/资产/税务 |
| mes | 制造管理 | /v1/mes | 生产执行/追溯 |
| audit | 审计管理 | /v1/audit | 全链路审计 |
| approval | 审批管理 | /v1/approval | 多级审批流程 |
| mail | 消息中心 | /v1/mail | 站内消息通知 |
| document | 文档管理 | /v1/document | 文档/版本管理 |
| sales | 销售管理 | /v1/sales | 订单/统计 |
| customer | 客户管理 | /v1/customer | 客户/会员 |
| product | 产品管理 | /v1/product | 产品/属性/变体 |
| purchase | 采购管理 | /v1/purchase | 采购/供应商 |
| inventory | 库存管理 | /v1/inventory | 批次/量化 |
| mrp2 | MRP 管理 | /v1/mrp2 | 物料需求计划 |
| equipment | 设备管理 | /v1/equipment | 台账/维护/故障 |
| quality | 质量管理 | /v1/quality | 质量检测 |
| subcontracting | 分包管理 | /v1/subcontracting | 分包业务 |
| thirdparty | 第三方对接 | /v1/thirdparty | Dify/Coze 等 |
| alipay | 支付宝 | /v1/alipay | 支付宝支付 |
| wechat_pay | 微信支付 | /v1/wechat/pay | 微信支付 |
| qixiang_pay | 七象支付 | /v1/qixiang | 七象支付 |

---

## 📡 API 文档

启动服务后访问：

- **Swagger UI**: `http://127.0.0.1:9998/docs`
- **ReDoc**: `http://127.0.0.1:9998/redoc`
- **OpenAPI JSON**: `http://127.0.0.1:9998/openapi.json`

### 认证方式

API 使用 JWT Bearer Token 认证：

```bash
# 登录获取 Token
curl -X POST http://127.0.0.1:9998/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# 使用 Token 访问 API
curl http://127.0.0.1:9998/api/v1/users/me \
  -H "Authorization: Bearer <your-token>"
```

### 统一响应格式

所有 API 响应使用标准格式：

```json
{
    "code": 200,
    "data": { ... },
    "msg": "success",
    "success": true
}
```

---

## 🏛️ 架构设计

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue 3)                       │
│         Element Plus · Pinia · Vue Router            │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP / WebSocket
┌─────────────────────▼───────────────────────────────┐
│              ASGIAppWithPrefix 中间件                │
│   安装状态检查 · /api 前缀处理 · 静态资源托管        │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 FastAPI 应用层                       │
│     路由注册 · 权限校验 · 中间件 · 依赖注入          │
├─────────────────────────────────────────────────────┤
│                  插件管理器 (PluginManager)          │
│  动态加载 · 启停控制 · 生命周期钩子 · 菜单/权限注册  │
├─────────────────────────────────────────────────────┤
│                  业务插件层                          │
│  Agent · LLM · CRM · Finance · MES · Audit · ...    │
├─────────────────────────────────────────────────────┤
│                  核心服务层                          │
│  用户 · 权限 · 部门 · 安装 · 扩展                    │
├─────────────────────────────────────────────────────┤
│                  公共基础设施                        │
│  配置 · 数据库 · 缓存 · 安全 · 日志 · 响应           │
├─────────────────────────────────────────────────────┤
│                  数据持久层                          │
│  Tortoise ORM · asyncpg · PostgreSQL/openGauss       │
└─────────────────────────────────────────────────────┘
```

### 关键设计

- **未安装状态**: 系统未安装时，后端跳过数据库初始化、插件加载和后台任务，仅提供最小化 HTTP 服务
- **安装拦截**: ASGI 中间件拦截非安装/public API 请求，返回 503 并重定向到 `/install`
- **前端双验证**: 路由守卫同时检查 localStorage 缓存和后端 `/v1/install/status` API
- **双验证重启**: 安装完成后，验证数据库写入完整性和安装文件完整性，再触发系统重启
- **审计安全**: ORM 事件监听和审计中间件检查 `Tortoise._inited` 标志，数据库未初始化时自动禁用

---

## 🐳 Docker 部署

### openGauss 数据库

```bash
cd deploy/openguass
docker-compose up -d
```

### RabbitMQ（可选）

```bash
cd rabbitmq
docker-compose up -d
```

### 完整部署建议

```bash
# 1. 克隆并安装后端依赖
git clone <repo> && cd jingxipanel
pip install -r requirements.txt

# 2. 构建前端
cd web && npm install && npm run build && cd ..

# 3. 启动 openGauss
cd deploy/openguass && docker-compose up -d && cd ../..

# 4. 启动应用
python run.py
```

---

## 📊 监控

系统集成 Prometheus 监控和 OpenTelemetry 链路追踪：

- **指标暴露**: `http://127.0.0.1:9998/metrics`
- **健康检查**: `http://127.0.0.1:9998/health`
- **Prometheus 配置**: 参见 `monitoring/prometheus.yml`
- **告警规则**: 参见 `monitoring/alert_rules.yml`

---

## ❓ 常见问题

### Q1: 安装时提示数据库连接失败

**可能原因：**
- 数据库服务未启动
- 端口不正确（openGauss 通常为 15432，PostgreSQL 默认 5432）
- 用户名密码错误
- 数据库不存在

**解决方法：**
```bash
# 使用 psql 或 gsql 测试连接
# PostgreSQL:
psql -h 127.0.0.1 -p 5432 -U admin -d jingxipanel
# openGauss:
gsql -h 127.0.0.1 -p 15432 -U admin -d jingxipanel
```

### Q2: openGauss 与 PostgreSQL 的兼容性

本系统同时支持 PostgreSQL 和 openGauss：
- openGauss 使用端口 `15432`
- openGauss 默认用户 `omm` 的权限无法通过 `ALTER ROLE` 修改
- 建议创建独立 `admin` 用户进行应用连接
- openGauss 使用 `gs_dumpall` 而非 `pg_dumpall` 进行备份

### Q3: 安装完成后无法登录

**可能原因：**
- 管理员账户创建失败
- 密码输入错误

**解决方法：**
1. 检查数据库中是否存在用户记录
2. 如需重置管理员密码，执行：
```sql
UPDATE "user" SET password = '<new_password_hash>' WHERE username = 'admin';
```

### Q4: 前端页面访问空白

**可能原因：**
- 前端未构建
- 开发服务器未启动

**解决方法：**
```bash
# 构建前端
cd web && npm install && npm run build

# 或启动开发服务器
npm run dev
```

### Q5: 如何修改服务端口

编辑 `run.py` 或设置环境变量：
```bash
# Windows PowerShell
$env:UVICORN_PORT = "8080"
python run.py

# Linux/Mac
export UVICORN_PORT=8080
python run.py
```

### Q6: Windows 下开发模式热重载

Windows 平台 uvicorn 多 worker 模式存在 socket 继承问题，默认使用单 worker。开发模式下设置：
```bash
$env:UVICORN_RELOAD = "true"
python run.py
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。