from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.db.models.post import Post
from app.db.models.postImage import PostImage
from app.db.models.tag import Tag
from app.db.models.material import Material
from app.db.models.topic import Topic
from app.schemas.post import PostCreate, PostUpdate
from sqlalchemy import or_

def search_posts(db: Session, title: str, skip: int = 0, limit: int = 100):
    """
    Search posts by title using case-insensitive partial match
    """
    return db.query(Post)\
        .filter(Post.title.ilike(f"%{title}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()

async def create_post(db: Session, post_data: PostCreate) -> Post:
    try:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            status=post_data.status,
            rejection_reason=post_data.rejection_reason,
            created_by=post_data.created_by,
            updated_by=post_data.created_by,
        )

        # Kiểm tra và thêm tags
        if post_data.tag_ids:
            tags = db.query(Tag).filter(Tag.tag_id.in_(post_data.tag_ids)).all()
            if len(tags) != len(post_data.tag_ids):
                raise HTTPException(
                    status_code=400,
                    detail="Một số tag_id không tồn tại"
                )
            post.tags = tags

        # Kiểm tra và thêm materials
        if post_data.material_ids:
            materials = db.query(Material).filter(
                Material.material_id.in_(post_data.material_ids)
            ).all()
            if len(materials) != len(post_data.material_ids):
                raise HTTPException(
                    status_code=400,
                    detail="Một số material_id không tồn tại"
                )
            post.materials = materials

        # Kiểm tra và thêm topics
        if post_data.topic_ids:
            topics = db.query(Topic).filter(
                Topic.topic_id.in_(post_data.topic_ids)
            ).all()
            if len(topics) != len(post_data.topic_ids):
                raise HTTPException(
                    status_code=400,
                    detail="Một số topic_id không tồn tại"
                )
            post.topics = topics

        # Thêm post và commit để lấy post_id
        db.add(post)
        db.commit()
        db.refresh(post)

        # Thêm images
        if post_data.images:
            for image_url in post_data.images:
                db_image = PostImage(
                    image_url=image_url,
                    post_id=post.post_id
                )
                db.add(db_image)
            db.commit()

        # Refresh lại để lấy tất cả relationships
        db.refresh(post)
        return post

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Lỗi khi tạo post: {str(e)}"
        )


def get_post_by_id(db: Session, post_id: UUID) -> Post:
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
def search_posts_by_tag_name(db: Session, tag_name: str, skip: int = 0, limit: int = 100):
    """
    Search posts by tag name using case-insensitive partial match
    """
    return db.query(Post)\
        .join(Post.tags)\
        .filter(Tag.name.ilike(f"%{tag_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).offset(skip).limit(limit).all()


async def update_post(db: Session, post_id: UUID, post_data: PostUpdate) -> Post:
    post = get_post_by_id(db, post_id)

    post.title = post_data.title
    post.content = post_data.content
    post.status = post_data.status
    post.rejection_reason = post_data.rejection_reason
    post.updated_by = post_data.updated_by

    if post_data.tag_ids is not None:
        post.tags = db.query(Tag).filter(Tag.tag_id.in_(post_data.tag_ids)).all()

    if post_data.material_ids is not None:
        post.materials = db.query(Material).filter(Material.material_id.in_(post_data.material_ids)).all()

    if post_data.topic_ids is not None:
        post.topics = db.query(Topic).filter(Topic.topic_id.in_(post_data.topic_ids)).all()

    if post_data.images is not None:
        # Xoá ảnh cũ
        db.query(PostImage).filter(PostImage.post_id == post_id).delete()
        # Thêm ảnh mới
        for img in post_data.images:
            db_image = PostImage(url=img.url, post_id=post.post_id)
            db.add(db_image)

    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: UUID):
    post = get_post_by_id(db, post_id)
    db.delete(post)
    db.commit()
