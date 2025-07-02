from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.deps import get_db, get_current_active_account
from app.schemas.friend import FriendRequest, FriendResponse, PendingFriendRequest, FriendWithNickname
from app.services.friend_service import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    get_friends_with_nickname,
    get_pending_requests,
    remove_friend_service,
    get_friendship_status,
    update_nickname
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

@router.get("/list", response_model=List[FriendWithNickname])
def list_friends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return get_friends_with_nickname(db, current_user.account_id)

@router.get("/pending", response_model=List[PendingFriendRequest])
def list_pending_requests(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    try:
        pending = get_pending_requests(db, current_user.account_id)
        print(f"Debug: Found {len(pending)} pending requests for user {current_user.account_id}")
        
        result = []
        for item in pending:
            friend_request = item["friend_request"]
            sender_account = item["sender"]
            
            pending_request = PendingFriendRequest(
                sender_id=friend_request.sender_id,
                receiver_id=friend_request.receiver_id,
                status=friend_request.status,
                created_at=friend_request.created_at,
                updated_at=friend_request.updated_at,
                sender={
                    "account_id": sender_account.account_id,
                    "username": sender_account.username,
                    "full_name": sender_account.full_name,
                    "avatar": sender_account.avatar
                }
            )
            result.append(pending_request)
        
        print(f"Debug: Returning {len(result)} pending requests")
        return result
    except Exception as e:
        print(f"Error in list_pending_requests: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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

@router.put("/{friend_id}/nickname", response_model=FriendResponse)
def update_friend_nickname(
    friend_id: UUID,
    nickname: str = Body(..., embed=True, min_length=1, max_length=100),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account)
):
    """Cập nhật nickname cho bạn bè trong đoạn chat 1-1"""
    friend = update_nickname(db, current_user.account_id, friend_id, nickname)
    return friend

@router.get("/test-access")
def test_friend_access(
    current_user = Depends(get_current_active_account)
):
    """Test endpoint to check if user can access friend APIs"""
    return {
        "user_id": str(current_user.account_id),
        "username": current_user.username,
        "role": current_user.role.role_name if current_user.role else None,
        "status": "active",
        "message": "User can access friend APIs"
    }
