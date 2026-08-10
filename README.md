# AIPanelAdmin - AI应用管理后台

基于 FastAPI 开发的 AI 应用管理后台系统，提供用户管理、权限管理、智能体管理、LLM 模型管理、财务/库存管理等功能。

## 目录结构

```
jingxipanel/
├── base/                    # 核心代码目录
│   ├── cli/                # 命令行工具
│   ├── common/             # 公共模块（配置、数据库、安全等）
│   ├── core/               # 核心业务模块
│   │   ├── dept/          # 部门管理
│   │   ├── install/       # 系统安装向导
│   │   └── users/         # 用户与权限
│   └── plugins/            # 插件模块
│       ├── agent/         # 智能体管理
│       ├── llm/           # LLM大模型
│       ├── mail/          # 邮件服务
│       ├── mes/           # 制造执行系统
│       └── ...            # 其他插件
├── web/                    # 前端代码（Vue3 + Element Plus）
├── migrations/            # 数据库迁移脚本
├── config.conf            # 配置文件
├── requirements.txt       # Python 依赖
└── run.py                 # 启动入口
```

## 环境要求

| 软件 | 最低版本 | 推荐版本 | 说明 |
|------|---------|---------|------|
| Python | 3.8 | 3.10+ | 后端运行环境 |
| PostgreSQL | 12 | 14+ | 数据库（也支持 openGauss） |
| Node.js | 16 | 18+ | 前端构建环境 |
| npm | 8 | 9+ | 前端包管理 |

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd jingxipanel
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 启动后端服务

```bash
python run.py
```

服务默认启动在 `http://127.0.0.1:9998`

### 4. 启动前端开发服务（可选）

```bash
cd web
npm install
npm run dev
```

前端开发服务默认启动在 `http://127.0.0.1:3000`

---

## 🌱 系统安装向导

本系统提供了友好的 Web 安装向导，可通过浏览器访问完成系统初始化配置。

### 安装前准备

在开始安装之前，请确保以下条件已满足：

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

安装向导会自动检测运行环境，包括：
- 操作系统兼容性
- Python 版本
- 数据库连接性（提示）
- 文件写入权限

如果检测项显示为红色 ❌，请根据提示解决问题后再继续。

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

**配置完成后，点击"测试连接"按钮验证数据库连接是否正常。**

#### 第三步：管理员设置

配置系统管理员账户：

- **用户名**：登录用户名（3-20 字符）
- **密码**：登录密码（至少 8 位）
- **确认密码**：再次输入密码
- **昵称**：管理员显示名称
- **邮箱**：管理员邮箱地址

#### 第四步：完成安装

点击"开始安装"按钮，系统将自动执行：
1. 写入配置文件 `config.conf`
2. 初始化数据库连接
3. 创建系统数据表
4. 创建管理员账户
5. 标记系统为已安装

安装过程大约需要 30 秒，请耐心等待。

#### 第五步：安装完成

看到成功页面即表示安装完成，点击"前往登录"按钮进入登录页面。

### 安装后配置

安装完成后，建议进行以下操作：

1. **修改默认密码**
   - 登录后进入"个人信息"页面修改密码

2. **配置邮件服务**（可选）
   - 编辑 `config.conf` 中的 `[email]` 部分
   ```ini
   [email]
   enabled = true
   smtp_host = smtp.qq.com
   smtp_port = 465
   sender_email = your-email@example.com
   sender_password = your-email-password
   ```

3. **配置 Redis**（可选）
   - 编辑 `config.conf` 中的 `[redis]` 部分
   ```ini
   [redis]
   enabled = true
   host = 127.0.0.1
   port = 6379
   password = your-redis-password
   db = 0
   ```

4. **配置文件存储路径**
   - 编辑 `config.conf` 中的 `[storage]` 部分
   ```ini
   [storage]
   path = /path/to/storage
   ```

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

## 配置文件说明

`config.conf` 包含系统所有配置项：

### 数据库配置 `[db]`

```ini
[db]
db_host = 127.0.0.1        # 数据库主机
db_port = 15432             # 数据库端口
db_name = jingxipanel       # 数据库名
db_user = admin             # 用户名
db_password = Admin@123     # 密码
minsize = 5                 # 最小连接数
maxsize = 20                # 最大连接数
timeout = 30                # 连接超时
command_timeout = 30        # 命令超时
```

### 应用配置 `[app]`

```ini
[app]
name = AIPanelAdmin
version = v0.1.0
debug = false               # 调试模式，生产环境建议关闭
```

### 其他配置模块

| 模块 | 说明 | 是否必填 |
|------|------|---------|
| `[storage]` | 文件存储路径 | 是 |
| `[log]` | 日志路径 | 是 |
| `[redis]` | Redis 缓存 | 否 |
| `[email]` | 邮件服务 | 否 |
| `[qdrant]` | 向量数据库 | 否 |
| `[audit]` | 审计日志 | 是 |
| `[monitoring]` | Prometheus 监控 | 否 |
| `[rabbitmq]` | 消息队列 | 否 |

---

## 常见问题

### Q1: 安装时提示数据库连接失败

**可能原因：**
- 数据库服务未启动
- 端口不正确（openGauss 通常为 15432，PostgreSQL 默认 5432）
- 用户名密码错误
- 数据库不存在

**解决方法：**
```bash
# 使用 psql 或 gsql 测试连接
psql -h 127.0.0.1 -p 15432 -U admin -d jingxipanel
```

### Q2: 安装完成后无法登录

**可能原因：**
- 管理员账户创建失败
- 密码输入错误

**解决方法：**
1. 检查数据库中是否存在用户记录
2. 如需重置管理员密码，执行：
```sql
UPDATE "user" SET password = '<new_password_hash>' WHERE username = 'admin';
```

### Q3: 前端页面访问空白

**可能原因：**
- 前端未构建
- 开发服务器未启动

**解决方法：**
```bash
# 构建前端
cd web
npm run build

# 或启动开发服务器
npm run dev
```

### Q4: 如何修改服务端口

编辑 `run.py` 或设置环境变量：
```bash
# Windows PowerShell
$env:UVICORN_PORT = "8080"
python run.py

# Linux/Mac
export UVICORN_PORT=8080
python run.py
```

### Q5: openGauss 与 PostgreSQL 的兼容性

本系统同时支持 PostgreSQL 和 openGauss 数据库：
- openGauss 使用端口 `15432`
- openGauss 默认用户为 `omm`，初始化账户不可修改权限
- 建议使用 `admin` 用户进行应用连接

---

## API 文档

启动服务后访问：
- Swagger UI: `http://127.0.0.1:9998/docs`
- ReDoc: `http://127.0.0.1:9998/redoc`
- OpenAPI JSON: `http://127.0.0.1:9998/openapi.json`

## 技术栈

**后端：**
- Python 3.8+
- FastAPI（Web 框架）
- Tortoise ORM（异步 ORM）
- asyncpg（PostgreSQL 驱动）
- Pydantic（数据验证）
- Loguru（日志）

**前端：**
- Vue 3
- Element Plus（UI 组件库）
- Pinia（状态管理）
- Vue Router（路由）
- Axios（HTTP 客户端）

## License

MIT License
