from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models.favourite import Favourite
from app.db.models.favourite_post import favourite_posts
from app.db.models.post import Post
from app.schemas.favourite import FavouriteCreate, FavouriteUpdate
from sqlalchemy import desc, asc
from fastapi import HTTPException, status

def create_favourite(
    db: Session,
    favourite_data: FavouriteCreate,
    account_id: UUID
) -> Favourite:
    """Create a new favourite list"""
    # Check if favourite name already exists for this account
    existing_favourite = db.query(Favourite).filter(
        Favourite.account_id == account_id,
        Favourite.favourite_name == favourite_data.favourite_name
    ).first()
    
    if existing_favourite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Favourite list with this name already exists"
        )

    db_favourite = Favourite(
        favourite_name=favourite_data.favourite_name,
        account_id=account_id
    )
    db.add(db_favourite)
    db.commit()
    db.refresh(db_favourite)
    return db_favourite

def get_favourite(db: Session, favourite_id: UUID) -> Optional[Favourite]:
    """Get favourite list by ID"""
    return db.query(Favourite).filter(Favourite.favourite_id == favourite_id).first()

def get_favourite_by_name(db: Session, favourite_name: str, account_id: UUID) -> Optional[Favourite]:
    """Get favourite list by name and account_id"""
    return db.query(Favourite).filter(
        Favourite.favourite_name == favourite_name,
        Favourite.account_id == account_id
    ).first()

def get_favourites(
    db: Session,
    account_id: UUID,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None
) -> List[Favourite]:
    """Get all favourite lists with search and sort options"""
    query = db.query(Favourite).filter(Favourite.account_id == account_id)
    
    if search:
        query = query.filter(Favourite.favourite_name.ilike(f"%{search}%"))
    
    if sort_by:
        if sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(desc(Favourite.created_at))
            else:
                query = query.order_by(asc(Favourite.created_at))
        elif sort_by == "favourite_name":
            if sort_order == "desc":
                query = query.order_by(desc(Favourite.favourite_name))
            else:
                query = query.order_by(asc(Favourite.favourite_name))
    
    return query.offset(skip).limit(limit).all()

def get_posts_by_favourite_id(
    db: Session,
    favourite_id: UUID,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None
) -> List[Post]:
    """Get posts in a favourite list by ID"""
    favourite = get_favourite(db, favourite_id)
    if not favourite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favourite list not found"
        )

    query = db.query(Post).join(
        favourite_posts,
        Post.post_id == favourite_posts.c.post_id
    ).filter(
        favourite_posts.c.favourite_id == favourite_id
    )

    if sort_by:
        if sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(desc(Post.created_at))
            else:
                query = query.order_by(asc(Post.created_at))
        elif sort_by == "title":
            if sort_order == "desc":
                query = query.order_by(desc(Post.title))
            else:
                query = query.order_by(asc(Post.title))

    return query.offset(skip).limit(limit).all()

def get_posts_by_favourite_name(
    db: Session,
    favourite_name: str,
    account_id: UUID,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None
) -> List[Post]:
    """Get posts in a favourite list by name"""
    favourite = get_favourite_by_name(db, favourite_name, account_id)
    if not favourite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favourite list not found"
        )

    query = db.query(Post).join(
        favourite_posts,
        Post.post_id == favourite_posts.c.post_id
    ).filter(
        favourite_posts.c.favourite_id == favourite.favourite_id
    )

    if sort_by:
        if sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(desc(Post.created_at))
            else:
                query = query.order_by(asc(Post.created_at))
        elif sort_by == "title":
            if sort_order == "desc":
                query = query.order_by(desc(Post.title))
            else:
                query = query.order_by(asc(Post.title))

    return query.offset(skip).limit(limit).all()

def update_favourite(
    db: Session,
    favourite: Favourite,
    favourite_data: FavouriteUpdate
) -> Favourite:
    """Update favourite list"""
    # Check if new name already exists for this account
    if favourite_data.favourite_name != favourite.favourite_name:
        existing_favourite = db.query(Favourite).filter(
            Favourite.account_id == favourite.account_id,
            Favourite.favourite_name == favourite_data.favourite_name
        ).first()
        
        if existing_favourite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Favourite list with this name already exists"
            )

    for field, value in favourite_data.dict(exclude_unset=True).items():
        setattr(favourite, field, value)
    
    db.commit()
    db.refresh(favourite)
    return favourite

def delete_favourite(db: Session, favourite_id: UUID) -> None:
    """Delete favourite list"""
    favourite = get_favourite(db, favourite_id)
    if favourite:
        db.delete(favourite)
        db.commit()

def add_post_to_favourite(db: Session, favourite_id: UUID, post_id: UUID) -> None:
    """Add a post to a favourite list"""
    favourite = get_favourite(db, favourite_id)
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    
    # Check if post exists and is approved
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved posts can be added to favourites")
    
    # Check if post is already in the favourite list
    existing_favourite_post = db.query(favourite_posts).filter(
        favourite_posts.c.favourite_id == favourite_id,
        favourite_posts.c.post_id == post_id
    ).first()
    if existing_favourite_post:
        raise HTTPException(status_code=400, detail="Post is already in this favourite list")
    
    stmt = favourite_posts.insert().values(
        favourite_id=favourite_id,
        post_id=post_id
    )
    db.execute(stmt)
    db.commit()

def add_post_to_favourite_by_name(db: Session, favourite_name: str, post_id: UUID, account_id: UUID) -> None:
    """Add a post to a favourite list by name"""
    favourite = db.query(Favourite).filter(
        Favourite.favourite_name == favourite_name,
        Favourite.account_id == account_id
    ).first()
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite list not found")
    
    # Check if post exists and is approved
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved posts can be added to favourites")
    
    # Check if post is already in the favourite list
    existing_favourite_post = db.query(favourite_posts).filter(
        favourite_posts.c.favourite_id == favourite.favourite_id,
        favourite_posts.c.post_id == post_id
    ).first()
    if existing_favourite_post:
        raise HTTPException(status_code=400, detail="Post is already in this favourite list")
    
    stmt = favourite_posts.insert().values(
        favourite_id=favourite.favourite_id,
        post_id=post_id
    )
    db.execute(stmt)
    db.commit()

def remove_post_from_favourite(db: Session, favourite_id: UUID, post_id: UUID) -> None:
    """Remove post from favourite list"""
    stmt = favourite_posts.delete().where(
        favourite_posts.c.favourite_id == favourite_id,
        favourite_posts.c.post_id == post_id
    )
    db.execute(stmt)
    db.commit() 