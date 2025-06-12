from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models.account import Account
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles
from app.core.deps import get_db
from app.schemas.favourite import FavouriteCreate, FavouriteUpdate, FavouriteResponse, FavouriteListResponse, FavouriteCreateResponse
from app.schemas.post import PostOut
from app.services import favourite_service

router = APIRouter()

@router.post("/", response_model=FavouriteCreateResponse, status_code=status.HTTP_201_CREATED)
def create_favourite(
    favourite_data: FavouriteCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Create a new favourite list"""
    return favourite_service.create_favourite(
        db=db,
        favourite_data=favourite_data,
        account_id=current_user.account_id
    )

@router.get("/", response_model=List[FavouriteListResponse])
def get_favourites(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="Sort by field (created_at, favourite_name)"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get all favourite lists with search and sort options"""
    return favourite_service.get_favourites(
        db=db,
        account_id=current_user.account_id,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/{favourite_id}", response_model=FavouriteResponse)
def get_favourite(
    favourite_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get favourite list by ID"""
    favourite = favourite_service.get_favourite(db=db, favourite_id=favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    if favourite.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return favourite

@router.get("/{favourite_id}/posts", response_model=List[PostOut])
def get_posts_by_favourite_id(
    favourite_id: UUID,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = Query(None, description="Sort by field (created_at, title)"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get posts in a favourite list by ID"""
    favourite = favourite_service.get_favourite(db=db, favourite_id=favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    if favourite.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return favourite_service.get_posts_by_favourite_id(
        db=db,
        favourite_id=favourite_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/name/{favourite_name}/posts", response_model=List[PostOut])
def get_posts_by_favourite_name(
    favourite_name: str,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = Query(None, description="Sort by field (created_at, title)"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc, desc)"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get posts in a favourite list by name"""
    return favourite_service.get_posts_by_favourite_name(
        db=db,
        favourite_name=favourite_name,
        account_id=current_user.account_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.put("/{favourite_id}", response_model=FavouriteResponse)
def update_favourite(
    favourite_id: UUID,
    favourite_data: FavouriteUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Update favourite list"""
    favourite = favourite_service.get_favourite(db=db, favourite_id=favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    if favourite.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return favourite_service.update_favourite(
        db=db,
        favourite=favourite,
        favourite_data=favourite_data
    )

@router.delete("/{favourite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favourite(
    favourite_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Delete favourite list"""
    favourite = favourite_service.get_favourite(db=db, favourite_id=favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    if favourite.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    favourite_service.delete_favourite(db=db, favourite_id=favourite_id)

@router.post("/{favourite_id}/posts/{post_id}", status_code=status.HTTP_201_CREATED)
def add_post_to_favourite(
    favourite_id: UUID,
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Add post to favourite list by ID"""
    favourite = favourite_service.get_favourite(db=db, favourite_id=favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    if favourite.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    favourite_service.add_post_to_favourite(db=db, favourite_id=favourite_id, post_id=post_id)
    return {"message": "Post added to favourite list successfully"}

@router.post("/name/{favourite_name}/posts/{post_id}", status_code=status.HTTP_201_CREATED)
def add_post_to_favourite_by_name(
    favourite_name: str,
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Add post to favourite list by name"""
    favourite_service.add_post_to_favourite_by_name(
        db=db,
        favourite_name=favourite_name,
        post_id=post_id,
        account_id=current_user.account_id
    )
    return {"message": "Post added to favourite list successfully"}

@router.delete("/{favourite_id}/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_post_from_favourite(
    favourite_id: UUID,
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Remove post from favourite list"""
    favourite = favourite_service.get_favourite(db=db, favourite_id=favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    if favourite.account_id != current_user.account_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    favourite_service.remove_post_from_favourite(db=db, favourite_id=favourite_id, post_id=post_id) 