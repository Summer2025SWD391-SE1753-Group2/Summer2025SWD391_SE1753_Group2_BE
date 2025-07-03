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

def get_pending_requests(db: Session, account_id: UUID):
    # Join with Account to get sender information
    pending_requests = db.query(Friend, Account).join(
        Account, Friend.sender_id == Account.account_id
    ).filter(
        Friend.receiver_id == account_id,
        Friend.status == FriendStatusEnum.pending
    ).all()
    
    # Transform to include both friend request and sender account info
    result = []
    for friend_request, sender_account in pending_requests:
        result.append({
            "friend_request": friend_request,
            "sender": sender_account
        })
    
    return result

def remove_friend_service(db: Session, account_id: UUID, friend_id: UUID):
    friendship = db.query(Friend).filter(
        ((Friend.sender_id == account_id) & (Friend.receiver_id == friend_id)) |
        ((Friend.sender_id == friend_id) & (Friend.receiver_id == account_id)),
        Friend.status == FriendStatusEnum.accepted
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")

    db.delete(friendship)
    db.commit()
    return {"message": "Friend removed successfully"}

def get_friendship_status(db: Session, account_id: UUID, friend_id: UUID):
    """Check the friendship status between two users"""
    if account_id == friend_id:
        return {"status": "self", "can_send_request": False}
    
    friendship = db.query(Friend).filter(
        ((Friend.sender_id == account_id) & (Friend.receiver_id == friend_id)) |
        ((Friend.sender_id == friend_id) & (Friend.receiver_id == account_id))
    ).first()
    
    if not friendship:
        return {"status": "none", "can_send_request": True}
    
    if friendship.status == FriendStatusEnum.accepted:
        return {"status": "friends", "can_send_request": False}
    elif friendship.status == FriendStatusEnum.pending:
        if friendship.sender_id == account_id:
            return {"status": "request_sent", "can_send_request": False}
        else:
            return {"status": "request_received", "can_send_request": False}
    else:  # rejected
        return {"status": "rejected", "can_send_request": True}

def update_nickname(db, user_id, friend_id, nickname: str):
    """Cập nhật nickname cho bạn bè. Nếu user là sender thì cập nhật sender_nickname, nếu là receiver thì cập nhật receiver_nickname."""
    from app.db.models.friend import Friend
    friend = db.query(Friend).filter(
        ((Friend.sender_id == user_id) & (Friend.receiver_id == friend_id)) |
        ((Friend.sender_id == friend_id) & (Friend.receiver_id == user_id))
    ).first()
    if not friend:
        raise Exception("Friend relationship not found")
    if friend.sender_id == user_id:
        friend.sender_nickname = nickname
    elif friend.receiver_id == user_id:
        friend.receiver_nickname = nickname
    else:
        raise Exception("User is not part of this friendship")
    db.commit()
    db.refresh(friend)
    return friend

def get_friends_with_nickname(db: Session, account_id: UUID) -> List[dict]:
    """Get friends list with nickname information"""
    # Query friends with nickname info
    friends_data = db.query(Account, Friend).join(
        Friend, 
        (
            ((Friend.sender_id == account_id) & (Friend.receiver_id == Account.account_id)) |
            ((Friend.receiver_id == account_id) & (Friend.sender_id == Account.account_id))
        )
    ).filter(Friend.status == FriendStatusEnum.accepted).all()
    
    result = []
    for account, friend in friends_data:
        # Determine which nickname to use based on user's position in friendship
        nickname = None
        if friend.sender_id == account_id:
            nickname = friend.sender_nickname
        else:
            nickname = friend.receiver_nickname
            
        friend_info = {
            "account_id": account.account_id,
            "username": account.username,
            "full_name": account.full_name,
            "email": account.email,
            "avatar": account.avatar,
            "nickname": nickname  # Add nickname field
        }
        result.append(friend_info)
    
    return result