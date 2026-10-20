# 校园失物招领管理系统

软件体系结构课程设计。前后端分离的校园失物招领平台，支持失物/招领信息发布、
检索匹配、认领审批、内容管理与数据统计。

## 技术栈

| 层 | 选型 |
|---|---|
| 后端 | Python 3.13 + FastAPI + SQLAlchemy 2.x |
| 数据库 | MySQL 9.x（utf8mb4） |
| 迁移 | Alembic |
| 认证 | JWT（PyJWT）+ bcrypt |
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 图表 | ECharts |

## 目录结构

```
.
├── backend/                 后端
│   ├── app/
│   │   ├── core/            配置、安全、全局异常
│   │   ├── db/              连接与会话
│   │   ├── models/          ORM 表结构
│   │   ├── schemas/         接口出入参（DTO/VO）
│   │   ├── repositories/    数据访问层（只写查询）
│   │   ├── services/        业务规则层（只写规则）
│   │   └── api/v1/          路由层（只做组装）
│   ├── alembic/             数据库迁移
│   ├── init_data.py         初始化分类/管理员/演示数据
│   ├── uploads/             上传的图片（不入库）
│   └── run.py               开发启动入口（8000）
└── frontend/                前端（8090）
    └── src/
        ├── api/             每个后端模块一个请求文件
        ├── layouts/         用户端 / 管理端两套布局
        ├── router/          路由表 + 权限守卫
        ├── stores/          登录态
        ├── views/           页面
        ├── components/      可复用组件
        └── utils/           格式化与常量
```

## 启动步骤

### 1. 数据库

确保 MySQL 已启动，并创建数据库（只需一次）：

```sql
CREATE DATABASE IF NOT EXISTS campus_lostfound
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 2. 后端

```bash
cd backend
# 首次：创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt

# 配置数据库密码：复制 .env.example 为 .env，改 MYSQL_PASSWORD
# （.env 已在 .gitignore 中，不会提交）

# 建表
.venv\Scripts\alembic.exe upgrade head

# 初始化分类、管理员、演示数据（可重复执行）
.venv\Scripts\python.exe init_data.py

# 启动
.venv\Scripts\python.exe run.py
```

后端地址：http://127.0.0.1:8000 ，接口文档：http://127.0.0.1:8000/docs

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:8090

开发期 `/api` 与 `/static` 由 Vite 代理到 8000，浏览器侧是同源请求，不触发 CORS。

### 4. 默认账号

| 角色 | 账号 | 密码 |
|---|---|---|
| 管理员 | admin | admin123 |
| 普通用户 | student01 | abc123 |

## 主要功能

**用户端**

- 注册 / 登录（JWT）
- 首页：公告、最新发布、快速搜索
- 失物招领列表：按类型、分类、关键词筛选，分页
- 详情：图片、描述、联系方式（仅登录可见）
- 发布 / 编辑 / 下架 / 重新上架 / 标记已归还
- 认领申请：提交说明与联系方式，可撤销
- 收到的申请：通过 / 拒绝，通过后物品自动置为已归还

**管理端**

- 数据看板：总量、归还率、平均归还耗时、分类分布、类型占比
- 内容管理：全量信息（含已下架），可下架 / 恢复
- 分类管理：增删改、启用停用（被引用的分类禁止删除）
- 用户管理：搜索、禁用 / 启用
- 公告管理：发布、置顶、删除

## 接口约定

所有接口返回统一结构，HTTP 状态码一律 200，业务结果放在 `code`：

```json
{ "code": 20000, "message": "success", "data": {} }
```

| code | 含义 |
|---|---|
| 20000 | 成功 |
| 40000 | 业务规则不满足（如用户名已占用） |
| 40100 | 未登录 / 令牌失效 |
| 40300 | 无权限 |
| 40400 | 资源不存在 |
| 42200 | 参数校验失败（data 为字段明细数组） |
| 50000 | 服务器内部错误 |

分页结构统一为 `{ items, total, page, size }`。

## 常见问题

**alembic 报 `UnicodeDecodeError: 'gbk' codec can't decode`**
`alembic.ini` 必须保持纯 ASCII。Alembic 内部用系统 locale 编码读取 ini，
中文 Windows 下是 GBK，任何中文注释都会让它崩溃。用 `PYTHONUTF8=1` 也不能解决。

**改了 `.env` 但没生效**
配置在进程启动时加载，必须重启后端。若 8000 端口被旧进程占用，
新进程只会报 `WinError 10013`，不像典型的"端口占用"提示。

**前端端口**
`vite.config.js` 里 `strictPort: true`，8090 被占用时直接报错而不是悄悄换端口——
避免换了端口后后端 CORS 白名单对不上。

**图片存哪**
存在 `backend/uploads/年月/`，通过 `/static/uploads/...` 访问。
生产环境应换成对象存储，接口签名不用变。
