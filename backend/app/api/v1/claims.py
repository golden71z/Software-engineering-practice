"""认领申请接口。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.claim import ClaimCreate, ClaimHandle, ClaimOut
from app.schemas.common import ApiResponse
from app.services import claim_service

router = APIRouter(tags=["认领"])


@router.post("", response_model=ApiResponse[ClaimOut], summary="提交认领申请")
def apply_claim(
    payload: ClaimCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ClaimOut]:
    claim = claim_service.apply(db, current, payload)
    return ApiResponse[ClaimOut](message="申请已提交，等待发布者处理", data=ClaimOut.from_model(claim))


@router.get("/mine", response_model=ApiResponse[list[ClaimOut]], summary="我提交的认领申请")
def list_my_claims(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[list[ClaimOut]]:
    claims = claim_service.list_mine(db, current)
    return ApiResponse[list[ClaimOut]](data=[ClaimOut.from_model(c) for c in claims])


@router.get(
    "/received", response_model=ApiResponse[list[ClaimOut]], summary="我收到的认领申请"
)
def list_received(
    status: str | None = Query(None, description="pending / approved / rejected / cancelled"),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[list[ClaimOut]]:
    claims = claim_service.list_received(db, current, status)
    return ApiResponse[list[ClaimOut]](data=[ClaimOut.from_model(c) for c in claims])


@router.get("/pending-count", response_model=ApiResponse[int], summary="待处理申请数量")
def pending_count(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[int]:
    return ApiResponse[int](data=claim_service.count_pending(db, current))


@router.post("/{claim_id}/approve", response_model=ApiResponse[ClaimOut], summary="通过认领")
def approve(
    claim_id: int,
    payload: ClaimHandle,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ClaimOut]:
    claim = claim_service.approve(db, current, claim_id, payload.comment)
    return ApiResponse[ClaimOut](message="已通过，该物品标记为已归还", data=ClaimOut.from_model(claim))


@router.post("/{claim_id}/reject", response_model=ApiResponse[ClaimOut], summary="拒绝认领")
def reject(
    claim_id: int,
    payload: ClaimHandle,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ClaimOut]:
    claim = claim_service.reject(db, current, claim_id, payload.comment)
    return ApiResponse[ClaimOut](message="已拒绝该申请", data=ClaimOut.from_model(claim))


@router.post("/{claim_id}/cancel", response_model=ApiResponse[ClaimOut], summary="撤销申请")
def cancel(
    claim_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ApiResponse[ClaimOut]:
    claim = claim_service.cancel(db, current, claim_id)
    return ApiResponse[ClaimOut](message="已撤销", data=ClaimOut.from_model(claim))
