-- ================================================================
-- 校园失物招领管理系统 - 数据库初始化脚本
-- 版本: v0.1  骨架阶段（仅建库）
-- ================================================================

CREATE DATABASE IF NOT EXISTS campus_lostfound
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE campus_lostfound;

-- ================================================================
-- 表结构将在数据库设计阶段补充，预计包含：
--   sys_user        用户表（学生 / 教职工 / 管理员）
--   item_category   物品分类表
--   item_info       物品信息表（失物 + 招领，通过 type 字段区分）
--   claim_apply     认领申请表
--   sys_notice      公告表
--   sys_message     站内消息表
--   item_image      物品图片表
-- ================================================================

-- 骨架阶段仅验证连通性，暂不建业务表
SELECT '校园失物招领管理系统 - 数据库初始化完成' AS message;
