from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.deps import get_db, get_current_active_account
from app.schemas.friend import FriendRequest, FriendResponse, PendingFriendRequest
from app.services.friend_service import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    get_friends,
    get_pending_requests,
    remove_friend_service,
    get_friendship_status
)
from typing import List
from app.schemas.account import AccountOut

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

@router.get("/pending", response_model=List[PendingFriendRequest])
def list_pending_requests(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    raw_requests = get_pending_requests(db, current_user.account_id)
    
    # Transform the data to match PendingFriendRequest schema
    result = []
    for item in raw_requests:
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
                "email": sender_account.email,
                "avatar": sender_account.avatar
            }
        )
        result.append(pending_request)
    
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
def check_friendship_status(
    friend_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_account)
):
    return get_friendship_status(db, current_user.account_id, friend_id)