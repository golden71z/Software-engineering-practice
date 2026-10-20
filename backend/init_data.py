"""初始化数据脚本（幂等，可重复执行）。

做三件事：
1. 建默认分类
2. 建管理员账号 admin / admin123
3. 建几条演示数据，方便前端一进来就有内容

在 backend 目录下执行：
    .venv\\Scripts\\python.exe init_data.py
加 --reset 会先清空 items / claims 再重新生成演示数据（分类和用户不动）。
"""
import sys
from datetime import datetime, timedelta

from sqlalchemy import delete, select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Category, Claim, Item, User

DEFAULT_CATEGORIES = [
    ("证件卡片", 1),
    ("电子设备", 2),
    ("书籍资料", 3),
    ("钥匙", 4),
    ("衣物鞋帽", 5),
    ("生活用品", 6),
    ("其他", 99),
]

# (type, title, description, 分类名, 地点, 几天前, 发布者用户名)
DEMO_ITEMS = [
    (
        "lost",
        "丢失一张校园一卡通",
        "蓝色卡套，姓名张*，卡号后四位 7321。10 月 18 日中午在二食堂二楼用餐后发现不见了，"
        "可能落在餐盘回收处附近。里面有门禁和饭卡余额，补办很麻烦，麻烦捡到的同学联系我。",
        "证件卡片",
        "第二食堂二楼",
        2,
        "student01",
    ),
    (
        "found",
        "捡到一副黑色蓝牙耳机",
        "在图书馆三楼 A 区靠窗座位（编号 A312）捡到，充电盒是黑色的，品牌看着像小米。"
        "已经交给图书馆一楼服务台，失主可凭品牌和耳机上的细节来认领。",
        "电子设备",
        "图书馆三楼 A 区",
        1,
        "student01",
    ),
    (
        "lost",
        "《数据结构与算法分析》教材丢失",
        "C 语言版，封面有一点折痕，书内第 47 页有我的笔记。上周四在教三楼 302 上完课后可能忘在桌洞里了。",
        "书籍资料",
        "教三楼 302",
        5,
        "student01",
    ),
    (
        "found",
        "操场看台捡到一串钥匙",
        "三把钥匙串在一个红色编织挂绳上，还有一个小的校徽挂件。晚上在操场跑步时于东侧看台第三排捡到。",
        "钥匙",
        "东操场看台",
        3,
        "student01",
    ),
    (
        "found",
        "拾到灰色连帽卫衣一件",
        "上周五傍晚在篮球场边的长椅上，尺码 L，口袋里有半张电影票根。已带回宿舍保管。",
        "衣物鞋帽",
        "篮球场东侧长椅",
        4,
        "student01",
    ),
    (
        "lost",
        "丢失一个白色保温杯",
        "杯身有贴纸（一只柴犬），杯盖是按压式的。周二上午在实验楼 4 楼自习室可能忘在窗台上了。",
        "生活用品",
        "实验楼 4 楼自习室",
        6,
        "student01",
    ),
]


def main() -> None:
    reset = "--reset" in sys.argv
    db = SessionLocal()
    try:
        # ---- 1. 分类 ----
        created_categories = 0
        for name, order in DEFAULT_CATEGORIES:
            exists = db.scalar(select(Category).where(Category.name == name))
            if not exists:
                db.add(Category(name=name, sort_order=order, is_active=1))
                created_categories += 1
        db.commit()
        total_categories = len(db.scalars(select(Category)).all())
        print(f"[分类] 新增 {created_categories} 个，现有 {total_categories} 个")

        # ---- 2. 管理员 ----
        admin = db.scalar(select(User).where(User.username == "admin"))
        if admin is None:
            admin = User(
                username="admin",
                email="admin@campus.edu",
                password_hash=hash_password("admin123"),
                real_name="系统管理员",
                phone="13800000000",
                role="admin",
                status=1,
            )
            db.add(admin)
            db.commit()
            print("[用户] 已创建管理员 admin / admin123")
        else:
            print("[用户] 管理员已存在，跳过")

        # ---- 3. 演示用户 ----
        demo_user = db.scalar(select(User).where(User.username == "student01"))
        if demo_user is None:
            demo_user = User(
                username="student01",
                email="student01@campus.edu",
                password_hash=hash_password("abc123"),
                real_name="张三",
                phone="13800138000",
                role="user",
                status=1,
            )
            db.add(demo_user)
            db.commit()
            print("[用户] 已创建演示用户 student01 / abc123")

        # ---- 4. 演示物品 ----
        if reset:
            db.execute(delete(Claim))
            db.execute(delete(Item))
            db.commit()
            print("[演示数据] 已清空原有物品与认领记录")

        existing = db.scalar(select(Item.id).limit(1))
        if existing:
            print("[演示数据] 已存在物品数据，跳过（要重建请加 --reset）")
        else:
            category_map = {c.name: c.id for c in db.scalars(select(Category)).all()}
            publisher = db.scalar(select(User).where(User.username == "student01"))
            now = datetime.now()
            for type_, title, desc, cat, location, days_ago, username in DEMO_ITEMS:
                publisher = db.scalar(select(User).where(User.username == username)) or publisher
                db.add(
                    Item(
                        type=type_,
                        title=title,
                        description=desc,
                        category_id=category_map[cat],
                        publisher_id=publisher.id,
                        status="published",
                        event_time=now - timedelta(days=days_ago),
                        location=location,
                        contact=publisher.phone,
                        images="",
                        view_count=0,
                    )
                )
            db.commit()
            print(f"[演示数据] 已生成 {len(DEMO_ITEMS)} 条物品")

        print("\n初始化完成。管理员登录：admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
