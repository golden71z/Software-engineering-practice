# 校园失物招领管理系统

基于 Spring Boot + Vue 3 前后端分离架构的校园失物招领平台。

## 项目简介

为校园场景提供一个失物发布、检索匹配、认领审核的一体化平台，解决传统失物招领靠微信群、公告栏导致的信息分散、匹配效率低的问题。

## 技术栈

### 后端
| 组件 | 版本 | 说明 |
|---|---|---|
| Spring Boot | 2.7.18 | 应用框架 |
| Java | 17 | 运行时 |
| MyBatis-Plus | 3.5.3.1 | 持久层框架 |
| Druid | 1.2.20 | 数据库连接池 |
| MySQL | 8.0+ | 数据库 |
| JWT (jjwt) | 0.11.5 | 无状态认证 |
| Knife4j | 4.x | 接口文档 |

### 前端
| 组件 | 版本 | 说明 |
|---|---|---|
| Vue | 3.x | 前端框架 |
| Vite | 5.x | 构建工具 |
| Element Plus | 2.x | UI 组件库 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由 |
| Axios | 1.x | HTTP 客户端 |
| ECharts | 5.x | 数据可视化 |

## 目录结构

```
Software-engineering-practice/
├── backend/                后端服务（Spring Boot）
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/campus/lostfound/
│       │   ├── LostFoundApplication.java
│       │   ├── common/       通用组件（统一响应、异常）
│       │   ├── config/       配置（跨域、Web、MyBatis-Plus）
│       │   └── controller/   控制层
│       └── resources/
│           └── application.yml
└── frontend/               前端应用（Vue 3 + Vite）
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/              接口封装
        ├── router/           路由
        ├── stores/           状态管理
        ├── utils/            工具（axios 封装）
        └── views/            页面
```

## 快速开始

### 环境要求
- JDK 17+
- Maven 3.8+
- Node.js 18+
- MySQL 8.0+

### 后端启动

```bash
cd backend
mvn spring-boot:run
```

服务默认运行在 `http://localhost:8080`。

健康检查接口：`GET http://localhost:8080/api/health`

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:8090`，已配置代理将 `/api` 请求转发到后端。

## 功能模块

### 用户端
- 注册 / 登录
- 发布失物信息 / 招领信息
- 分类检索、关键词搜索
- 提交认领申请
- 个人中心（我的发布、我的申请）

### 管理端
- 内容审核（通过 / 驳回 / 下架）
- 物品分类管理
- 公告发布
- 数据统计看板

### 公共支撑
- JWT 认证与权限控制
- 图片上传
- 站内消息通知
