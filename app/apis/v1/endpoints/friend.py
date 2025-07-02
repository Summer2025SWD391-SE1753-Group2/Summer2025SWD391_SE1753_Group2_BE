from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.deps import get_db, get_current_active_account
from app.schemas.friend import FriendRequest, FriendResponse, FriendPendingWithSender
from app.services.friend_service import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    get_pending_requests,
    remove_friend_service
)
from typing import List
from app.schemas.account import AccountOut
from app.db.models.account import Account
from app.db.models.friend import Friend, FriendStatusEnum

router = APIRouter()

@router.post("/request", response_model=FriendResponse)
def create_friend_request(
    request: FriendRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return send_friend_request(db, current_user.account_id, request.receiver_id)

@router.post("/accept/{sender_id}", response_model=FriendResponse)
def accept_request(
    sender_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return accept_friend_request(db, current_user.account_id, sender_id)

@router.post("/reject/{sender_id}", response_model=FriendResponse)
def reject_request(
    sender_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return reject_friend_request(db, current_user.account_id, sender_id)

@router.get("/list", response_model=List[AccountOut])
def list_friends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return get_friends(db, current_user.account_id)

@router.get("/pending", response_model=List[FriendPendingWithSender])
def list_pending_requests(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    pending = get_pending_requests(db, current_user.account_id)
    result = []
    for req in pending:
        sender_obj = db.query(Account).filter_by(account_id=req.sender_id).first()
        sender = None
        if sender_obj:
            sender = {
                "account_id": sender_obj.account_id,
                "username": sender_obj.username,
                "full_name": sender_obj.full_name,
                "avatar": sender_obj.avatar
            }
        req_dict = req.__dict__.copy()
        req_dict["sender"] = sender
        result.append(req_dict)
    return result

@router.delete("/{friend_id}", 
              summary="Remove friend",
              description="Remove a user from friends list")
def remove_friend(
    friend_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return remove_friend_service(db, current_user.account_id, friend_id)

@router.get("/status/{friend_id}")
def get_friendship_status(
    friend_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    # Đã là bạn bè
    friendship = db.query(Friend).filter(
        ((Friend.sender_id == current_user.account_id) & (Friend.receiver_id == friend_id)) |
        ((Friend.sender_id == friend_id) & (Friend.receiver_id == current_user.account_id))
    ).first()
    if friendship:
        if friendship.status == FriendStatusEnum.accepted:
            return {"status": "friends"}
        elif friendship.status == FriendStatusEnum.pending:
            if friendship.sender_id == current_user.account_id:
                return {"status": "request_sent"}
            elif friendship.receiver_id == current_user.account_id:
                return {"status": "request_received"}
    return {"status": "none"}