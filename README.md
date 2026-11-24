# 校园失物招领管理系统

软件体系结构课程设计项目。采用 Vue 3 + FastAPI 前后端分离架构，支持失物/招领发布、搜索、相似招领推荐、认领审批、归还及后台管理。

本文以 **Windows PowerShell 本地运行**为主，附 macOS / Linux 的后端命令。仓库不包含本地数据库、`.env`、上传图片和依赖目录，首次下载需要配置数据库并执行迁移。

## 环境准备

| 工具 | 本项目运行环境 / 建议 | 用途 |
|---|---|---|
| Git | 可执行 `git --version` | 克隆和更新仓库 |
| Python | 项目使用 Python 3.13 | 后端 |
| Node.js / npm | 建议 Node.js 22，包含 npm | 前端 |
| MySQL | 项目使用 MySQL 9.x、utf8mb4 | 数据库 |

确认 `python --version`、`node --version`、`npm --version` 可运行，并启动 MySQL 服务。其他 Python / MySQL 版本未在本文中声明为已验证兼容。

## 首次安装与启动

### 1. 克隆仓库

```powershell
git clone https://github.com/golden71z/Software-engineering-practice.git
cd Software-engineering-practice
```

下文“项目根目录”指同时包含 `README.md`、`backend/`、`frontend/` 的目录。通过 ZIP 下载时，解压后进入同一目录即可。

### 2. 创建数据库

```powershell
mysql -u root -p
```

输入本机数据库密码，在 MySQL 中执行：

```sql
CREATE DATABASE IF NOT EXISTS campus_lostfound
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
EXIT;
```

也可使用数据库客户端执行 SQL。如果 `mysql` 命令不存在，请将 MySQL 的 `bin` 目录加入 PATH 或使用客户端。应用不会自动创建数据库；配置的数据库账号需有目标库的建表、修改表结构和数据读写权限。

### 3. 安装后端依赖

在项目根目录打开第一个终端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `backend/.env`，至少核对以下配置：

```dotenv
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=替换为你的MySQL密码
MYSQL_DB=campus_lostfound
SECRET_KEY=替换为自行生成的随机长字符串
```

在 `backend/` 执行以下命令，将输出复制到 `SECRET_KEY`：

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

`.env` 使用 UTF-8 编码，已被 Git 忽略，不要提交密码或密钥。后端自动读取 `backend/.env`，无需手动加载，也不需要激活虚拟环境。

### 4. 迁移数据库并初始化

继续在 `backend/` 目录执行：

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe init_data.py
.\.venv\Scripts\python.exe -m alembic current
```

- `upgrade head` 创建或升级用户、分类、物品、申请、公告、收藏等表。
- 初始化脚本创建默认分类、管理员、演示用户及演示物品；已有账号不会被覆盖，已有物品时跳过演示物品创建。
- `current` 应显示迁移版本并带有 `(head)`。

普通初始化可重复执行。脚本的 `--reset` 参数会清空物品和认领记录后重建演示数据，**不要在需要保留数据的数据库上使用**。

### 5. 启动后端

仍在第一个终端的 `backend/` 目录执行：

```powershell
.\.venv\Scripts\python.exe run.py
```

默认监听 `127.0.0.1:8000`，开发模式开启代码热重载。保持终端运行。

| 地址 | 用途 |
|---|---|
| http://127.0.0.1:8000 | 服务信息 |
| http://127.0.0.1:8000/docs | Swagger 交互式接口文档 |
| http://127.0.0.1:8000/api/v1/health | 服务与数据库连接检查 |

健康检查中 `data.status` 和 `data.database` 都应为 `UP`。仅能打开 `/docs` 不代表数据库连接正常；健康检查也只探测连接，不能替代迁移检查。

### 6. 启动前端

在项目根目录另开第二个终端：

```powershell
cd frontend
npm ci
npm run dev
```

浏览器访问 **http://localhost:8090**。前端、后端和 MySQL 都需要保持运行。终端按 `Ctrl+C` 停止对应服务。

开发服务器将 `/api` 和 `/static` 代理到 `http://127.0.0.1:8000`，本地开发无需额外设置前端环境变量。

### macOS / Linux 后端命令

数据库配置和前端命令同上，后端使用以下路径：

```bash
cd backend
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填写数据库配置和 SECRET_KEY 后再继续
.venv/bin/python -m alembic upgrade head
.venv/bin/python init_data.py
.venv/bin/python run.py
```

后文 Windows 的 `.venv\Scripts\python.exe` 对应这些系统的 `.venv/bin/python`。这些是平台对应命令，不表示已完成所有平台的部署验证。

## 账号与使用方法

### 初始账号

| 角色 | 用户名 | 初始密码 |
|---|---|---|
| 管理员 | `admin` | `admin123` |
| 普通演示用户 | `student01` | `abc123` |

账号由初始化脚本创建。初始密码仅对新建账号有效，重复初始化不会覆盖已经修改的密码。当前登录按**用户名**查找账号，邮箱用于个人资料，不能代替用户名登录。

### 普通用户流程

1. 注册账号或使用演示账号登录。
2. 丢失物品时，首页点击“我丢了东西 · 查招领”先查找；没有找到时，通过“发布信息”发布失物，填写分类、发生时间、地点、描述和联系方式。
3. 捡到物品时，点击“我捡到东西 · 查失物”查找失主，或发布招领信息。
4. 在招领详情中，点击“疑似是我的”加入待核实列表；确认后通过“我要认领”提交说明和联系方式。提交成功后自动移出待核实列表。
5. 在其他用户发布的失物详情中，通过“我捡到了”提交拾获线索。
6. 发布者进入“收到的申请”或自己的物品详情，查看并通过或拒绝申请；支持按发布条目及申请状态组合筛选。
7. 头像菜单可进入我的发布、疑似是我的、我的认领、收到的申请，以及修改个人信息、修改密码和退出登录。

验证认领流程时使用两个不同账号：一个发布、另一个申请。不能认领自己的发布。

### 管理员流程

以管理员账号登录，在头像菜单中进入“管理后台”：

- **数据看板**：查看用户数、物品数量、归还率、平均归还耗时、分类与类型分布。
- **内容管理**：查询全部信息，包括下架条目，并进行下架等管理操作。
- **分类管理**：新增、修改、删除、排序及启用/停用，已被引用的分类不能删除。
- **用户管理**：搜索、按角色筛选、启用/禁用普通账号及重置密码。
- **公告管理**：发布、置顶和删除公告。

重置密码需要弹窗确认，目标账号的新密码为 **`usr123`**。用户随后可在头像菜单验证当前密码并修改。数据库只保存密码哈希，管理员不能查看原密码。

## 功能及业务规则

- 信息列表支持类型、分类、关键词检索和分页；详情展示图片、描述、地点、时间等，联系方式仅登录后可见。
- 我的发布支持编辑、下架、上架和删除本人发布。删除会清理关联申请、拾获线索及收藏记录，页面无法恢复；已归还信息不可编辑。
- 待处理申请可由申请人撤销，已处理申请不能重复审批。审批通过后立即标记物品已归还，并自动拒绝同物品其他待处理申请，当前没有独立的双方交接确认步骤。
- 个人资料支持姓名、邮箱和手机号，用户名不变；邮箱须有效且不能被其他账号占用，手机号选填，填写时须为有效的 11 位号码。
- 修改密码须验证当前密码。新密码为 6–64 位、与原密码不同，UTF-8 编码不超过 72 字节；成功后当前页面退出并要求重新登录。目前不会自动撤销其他设备已签发的 JWT。

### 相似招领推荐

仅发布者本人查看展示中的失物详情时显示，位于详情下方、收到的拾获线索上方，最多 **3 条**。非发布者管理员也不能访问该失物的推荐接口。

候选为同分类、其他用户发布、展示中的招领，拾获时间需位于丢失时间**前 1 天至后 30 天**之间。按标题、描述、地点和时间排序，并展示理由；仅同分类不足以入选，还需文字相似，或地点和时间共同接近。这是文本规则推荐，不进行图片识别，也不保证物品属于同一人。

没有推荐时先检查实际发生时间、分类、发布者和展示状态。历史演示招领的发生时间可能不在新失物的推荐范围内。

## 更新已有项目

先备份数据库及 `backend/uploads/`，处理本地未提交改动，再在项目根目录执行：

```powershell
git pull --ff-only origin main
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
cd ../frontend
npm ci
```

随后重启前后端。分支分叉或本地改动冲突时先处理冲突，不要强制覆盖。

**拉取代码不会自动更新数据库。** 缺少 `favorites` 等新表会导致相关接口报错；每次更新后都应检查并执行迁移。已有项目通常不必重新初始化，更不要用 `--reset` 更新数据。

## 前端构建

在 `frontend/` 目录执行：

```powershell
npm run build
```

输出为 `frontend/dist/`。大于 500 kB 的打包体积提示不等于构建失败。

## 配置参考

模板为 [`backend/.env.example`](backend/.env.example)，实际读取 `backend/.env`。

| 配置项 | 模板值 | 说明 |
|---|---|---|
| `MYSQL_HOST` / `MYSQL_PORT` | `127.0.0.1` / `3306` | 数据库地址 |
| `MYSQL_USER` / `MYSQL_PASSWORD` | `root` / 占位文本 | 需填写本机可用账号密码 |
| `MYSQL_DB` | `campus_lostfound` | 需提前创建 |
| `SECRET_KEY` | 开发示例字符串 | JWT 签名密钥，替换为随机长字符串 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 令牌有效期，单位分钟 |
| `CORS_ORIGINS` | 本地 8090、5173 来源 | 逗号分隔 |
| `API_V1_PREFIX` | `/api/v1` | 前端当前按此路径请求 |
| `APP_NAME` / `APP_VERSION` | 应用名 / `0.1.0` | 展示信息 |
| `DEBUG` / `SQL_ECHO` | `true` / `false` | 配置标志 / SQL 输出 |

修改 `.env` 后重启后端。`run.py` 的监听地址、端口和热重载在脚本中指定，不能仅靠 `DEBUG` 改变；修改后端地址或端口时，还需调整 `frontend/vite.config.js` 的代理目标。

## 项目结构与接口

技术栈：Vue 3、Vite、Element Plus、Pinia、ECharts；FastAPI、SQLAlchemy、MySQL、Alembic；JWT 与 bcrypt。

```text
backend/
  app/api/v1/       接口
  app/core/         配置、安全、异常处理
  app/db/           数据库会话
  app/models/       ORM 表结构
  app/schemas/      参数校验与响应结构
  app/repositories/ 数据访问
  app/services/     业务规则与推荐
  alembic/          迁移文件
  init_data.py      初始化脚本
  run.py            开发启动入口
frontend/
  src/api/          请求封装
  src/components/   卡片、推荐及弹窗
  src/layouts/      用户端与管理端布局
  src/router/       路由与前端守卫
  src/stores/       登录状态
  src/views/        业务页面
  vite.config.js    端口与代理
```

接口以运行后的 `/docs` 为准。先通过 `POST /api/v1/auth/login` 获取 `data.access_token`，在 Swagger 的 **Authorize** 中输入令牌，或携带请求头：

```http
Authorization: Bearer <access_token>
```

统一响应示例：

```json
{ "code": 20000, "message": "success", "data": {} }
```

| code | 含义 |
|---|---|
| `20000` | 成功 |
| `40000` | 业务规则不满足 |
| `40100` | 未登录、令牌无效或账号禁用 |
| `40300` | 无权限 |
| `40400` | 业务资源不存在 |
| `42200` | 参数校验失败，data 可含字段明细 |
| `50000` | 未预期的服务器错误 |

业务异常及参数校验通常返回 HTTP 200，需要检查 `code`；未预期错误返回 HTTP 500，框架 HTTP 错误保留对应状态。分页数据结构为 `{ items, total, page, size }`。

## 常见问题

### 数据库连接失败、缺表或接口 500

检查 MySQL 服务、`.env` 的账号密码/地址/库名和数据库权限。访问健康检查，并在 `backend/` 用虚拟环境 Python 执行 `-m alembic current`、`-m alembic upgrade head`。连接成功不代表表已迁移，具体异常查看后端终端日志。

### 缺少模块或虚拟环境无法运行

确认用的是 `.venv` 的 Python 且安装了依赖。不要复制他人的 `.venv`；移动项目或更换 Python 后重新创建虚拟环境。本文命令无需运行激活脚本，可避免 PowerShell 激活策略限制。若 `npm.ps1` 被阻止，可改用 `npm.cmd ci` 和 `npm.cmd run dev`。

### Alembic 报 GBK / UnicodeDecodeError

保持 `backend/alembic.ini` 为纯 ASCII，勿添加中文注释；`.env` 则使用 UTF-8。它们由不同组件读取，不能混淆编码。

### 前端请求失败或端口占用

检查后端 8000、前端 8090 是否运行。前端启用 `strictPort`，端口占用时直接退出，不会自动换端口。更换端口时同步调整代理与跨域设置。后端绑定失败也可能是端口占用或系统保留端口，结合具体错误检查。

### 图片缺失或上传失败

图片存放于 `backend/uploads/YYYYMM/`，经 `/static/uploads/` 访问。支持 jpg、jpeg、png、gif、webp，单张不超过 5 MiB，上传须登录。Git 不保存上传目录，换环境需另行复制；删除发布目前不自动清理磁盘图片。

### 初始密码无效

需先初始化账号。重复初始化不覆盖已修改的密码；管理员重置后的密码为 `usr123`。当前没有邮箱自助找回或密保功能。

### GitHub 连接超时

检查网络和代理状态，可执行 `git ls-remote origin refs/heads/main` 只读检查连接。Git 与浏览器可能使用不同代理；切换代理状态后重试，避免反复叠加全局配置。网络超时与账号认证失败应分开排查，不要关闭 SSL 验证。

## 对外部署说明

以上是本地开发流程。正式部署还需配置：

- 独立数据库账号、随机密钥、修改演示密码。固定重置密码 `usr123` 不适合作为公开服务的长期恢复方案。
- 受进程管理的 ASGI 后端，不使用 `run.py` 的开发热重载。
- 托管前端 `dist/`，为 history 路由回退到 `index.html`，反向代理 `/api` 和 `/static` 到后端。构建产物不继承开发代理，`npm run preview` 也不应作为生产服务。
- HTTPS、访问范围、图片持久化、数据库及图片备份、升级时数据库迁移。

仓库当前未提供一键生产部署配置。生产发布前还应评估登录限流、旧令牌失效、上传内容校验和管理操作审计。
