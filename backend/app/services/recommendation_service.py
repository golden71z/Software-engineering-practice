"""按物品描述、地点和发生时间推荐招领，不将分数解释为认领概率。"""
import re
import unicodedata
from datetime import timedelta
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError, ForbiddenError, NotFoundError
from app.models.user import User
from app.repositories import item_repo


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    for word in ("失物招领", "丢失", "遗失", "失物", "招领", "捡到", "拾到", "拾获", "寻找", "一个", "一只", "一张", "一副"):
        value = value.replace(word, "")
    return "".join(re.findall(r"[\w]", value))


def _similarity(left: str, right: str) -> float:
    left, right = _normalize(left), _normalize(right)
    if not left or not right:
        return 0.0
    def grams(value):
        return {value[i:i + 2] for i in range(len(value) - 1)} if len(value) > 1 else {value}
    a, b = grams(left), grams(right)
    return len(a & b) / min(len(a), len(b))


def recommend_found(db: Session, item_id: int, current: User) -> list[dict]:
    lost = item_repo.get_by_id(db, item_id)
    if lost is None:
        raise NotFoundError("该信息不存在")
    # 管理员也不能查看其他发布者的私人推荐。
    if lost.publisher_id != current.id:
        raise ForbiddenError("只有发布者本人能查看相似招领")
    if lost.type != "lost":
        raise BusinessError("仅失物信息支持相似招领推荐")
    if lost.status != "published":
        return []

    candidates = item_repo.recommendation_candidates(
        db, lost, lost.event_time - timedelta(days=1), lost.event_time + timedelta(days=30)
    )
    ranked = []
    for found in candidates:
        title = _similarity(lost.title, found.title)
        description = _similarity(lost.description, found.description)
        left, right = _normalize(lost.location), _normalize(found.location)
        location = SequenceMatcher(None, left, right).ratio() if left and right else 0
        days = abs((found.event_time - lost.event_time).total_seconds()) / 86400
        # 同分类本身不足以推荐，至少有文字相似或地点与时间共同吻合。
        if title < 0.25 and description < 0.25 and not (location >= 0.6 and days <= 7):
            continue
        score = 15 + 45 * title + 15 * description + 20 * location + 5 * max(0, 1 - days / 30)
        reasons = ["同分类"]
        if title >= 0.25 or description >= 0.25:
            reasons.append("描述相似")
        if location >= 0.6:
            reasons.append("地点相近")
        if days <= 7:
            reasons.append("时间接近")
        ranked.append((score, found.event_time, found.id, {
            "id": found.id, "title": found.title, "location": found.location,
            "event_time": found.event_time,
            "thumbnail": found.image_list[0] if found.image_list else None,
            "reasons": reasons,
        }))
    ranked.sort(key=lambda row: row[:3], reverse=True)
    return [row[3] for row in ranked[:3]]
