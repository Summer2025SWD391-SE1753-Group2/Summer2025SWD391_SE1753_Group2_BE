from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.friend import Friend, FriendStatusEnum
from app.db.models.account import Account
from uuid import UUID
from typing import List
from datetime import datetime, timezone

def send_friend_request(db: Session, sender_id: UUID, receiver_id: UUID):
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if receiver exists
    receiver = db.query(Account).filter(Account.account_id == receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Check if friend request already exists
    existing_request = db.query(Friend).filter(
        ((Friend.sender_id == sender_id) & (Friend.receiver_id == receiver_id)) |
        ((Friend.sender_id == receiver_id) & (Friend.receiver_id == sender_id))
    ).first()

    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already exists")

    friend_request = Friend(
        sender_id=sender_id,
        receiver_id=receiver_id,
        status=FriendStatusEnum.pending
    )

    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    return friend_request

def accept_friend_request(db: Session, receiver_id: UUID, sender_id: UUID):
    friend_request = db.query(Friend).filter(
        Friend.sender_id == sender_id,
        Friend.receiver_id == receiver_id,
        Friend.status == FriendStatusEnum.pending
    ).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    friend_request.status = FriendStatusEnum.accepted
    friend_request.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(friend_request)
    return friend_request

def reject_friend_request(db: Session, receiver_id: UUID, sender_id: UUID):
    friend_request = db.query(Friend).filter(
        Friend.sender_id == sender_id,
        Friend.receiver_id == receiver_id,
        Friend.status == FriendStatusEnum.pending
    ).first()

    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    friend_request.status = FriendStatusEnum.rejected
    friend_request.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(friend_request)
    return friend_request

def get_friends(db: Session, account_id: UUID) -> List[Account]:
    friends = db.query(Account).join(
        Friend, 
        (
            ((Friend.sender_id == account_id) & (Friend.receiver_id == Account.account_id)) |
            ((Friend.receiver_id == account_id) & (Friend.sender_id == Account.account_id))
        )
    ).filter(Friend.status == FriendStatusEnum.accepted).all()
    
    return friends

def get_pending_requests(db: Session, account_id: UUID) -> List[Friend]:
    return db.query(Friend).filter(
        Friend.receiver_id == account_id,
        Friend.status == FriendStatusEnum.pending
    ).all()