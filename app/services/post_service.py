from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.db.models.post import Post
from app.db.models.post_image import PostImage
from app.db.models.tag import Tag
from app.db.models.material import Material
from app.db.models.topic import Topic
from app.schemas.post import PostCreate, PostUpdate
from sqlalchemy import or_
from typing import List
from app.schemas.post import PostOut
from app.db.models.step import Step
from app.db.models.unit import Unit
from app.db.models.post_material import PostMaterial
from sqlalchemy.orm import Session, joinedload
import logging
from app.db.models.account import Account
from app.schemas.role import RoleNameEnum
from app.schemas.post import PostModeration
from app.db.models.post import PostStatusEnum
from app.db.models.comment import Comment
from datetime import datetime, timezone
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
def search_posts(db: Session, title: str, skip: int = 0, limit: int = 100):
    """Search posts by title using case-insensitive partial match with creator info"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material),
                joinedload(Post.creator),
                joinedload(Post.updater),
                joinedload(Post.approver)
            )\
            .filter(Post.title.ilike(f"%{title}%"))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [PostOut.from_db_model(post) for post in posts]
    except Exception as e:
        logger.error(f"Error in search_posts: {str(e)}", exc_info=True)
        raise



def create_post(db: Session, post_data: PostCreate) -> PostOut:
    try:
        # Set status based on user role if not provided by frontend
        if post_data.status is None:
            current_user = db.query(Account).filter(Account.account_id == post_data.created_by).first()
            if current_user and current_user.role.role_name in ["moderator", "admin"]:
                post_data.status = PostStatusEnum.approved
            else:
                post_data.status = PostStatusEnum.waiting

        # Validate required fields
        if not post_data.topic_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one topic is required"
            )
        if not post_data.materials:
            raise HTTPException(
                status_code=400,
                detail="At least one material is required"
            )
        
        # Validate steps if provided
        if post_data.steps:
            order_numbers = [step.order_number for step in post_data.steps]
            if len(order_numbers) != len(set(order_numbers)):
                raise HTTPException(
                    status_code=400,
                    detail="Duplicate step order numbers are not allowed"
                )

        # Get creator's role
        creator = db.query(Account).filter(Account.account_id == post_data.created_by).first()
        if not creator:
            raise HTTPException(
                status_code=404,
                detail="Creator not found"
            )

        # Tạo post và flush để lấy post_id
        post = Post(
            title=post_data.title,
            content=post_data.content,
            status=post_data.status,
            created_by=post_data.created_by,
            updated_by=post_data.created_by,
        )
        db.add(post)
        db.flush()  # Lấy post_id

        # Handle materials with quantities
        if post_data.materials:
            post_materials = []
            inserted_material_ids = []
            for material_data in post_data.materials:
                # Verify material exists
                material = db.query(Material).filter(
                    Material.material_id == material_data.material_id
                ).first()
                if not material:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Material {material_data.material_id} not found"
                    )
                post_material = PostMaterial(
                    post_id=post.post_id,
                    material_id=material_data.material_id,
                    quantity=material_data.quantity,
                    unit=material.unit.name if hasattr(material.unit, 'name') else (material.unit if isinstance(material.unit, str) else None)
                )
                post_materials.append(post_material)
                inserted_material_ids.append(str(material_data.material_id))
                db.add(post_material)  # <-- Add từng PostMaterial vào session
            post.post_materials = post_materials  # Gán vào quan hệ ORM
            # Log số lượng và id các material đã insert
            from app.db.models.post_material import PostMaterial as PM
            logger.info(f"Prepared {len(post_materials)} PostMaterial for post_id={post.post_id}, material_ids={inserted_material_ids}")

        # Handle other relationships (tags, topics, images)
        if post_data.tag_ids:
            tags = db.query(Tag).filter(Tag.tag_id.in_(post_data.tag_ids)).all()
            post.tags = tags

        if post_data.topic_ids:
            topics = db.query(Topic).filter(Topic.topic_id.in_(post_data.topic_ids)).all()
            post.topics = topics

        if post_data.images:
            for image_url in post_data.images:
                db_image = PostImage(image_url=image_url, post_id=post.post_id)
                db.add(db_image)

        if post_data.steps:
            for step_data in post_data.steps:
                step = Step(
                    post_id=post.post_id,
                    order_number=step_data.order_number,
                    content=step_data.content
                )
                db.add(step)

        # Nếu status là approved, set approved_by
        if post_data.status == PostStatusEnum.approved:
            post.approved_by = post_data.created_by

        db.commit()
        # Debug: Query lại post_materials trực tiếp
        pm_list = db.query(PostMaterial).filter(PostMaterial.post_id == post.post_id).all()
        logger.info(f"PostMaterial in DB after commit: {[(pm.material_id, pm.quantity, pm.unit) for pm in pm_list]}")
        
        # Return with creator info using get_post_by_id
        return get_post_by_id(db, post.post_id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
def get_approved_posts(db: Session, skip: int = 0, limit: int = 100) -> List[PostOut]:
    """Get all approved posts with eager loading of relationships including creator"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material),
                joinedload(Post.creator),
                joinedload(Post.updater),
                joinedload(Post.approver)
            )\
            .filter(Post.status == PostStatusEnum.approved)\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return [PostOut.from_db_model(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_approved_posts: {str(e)}", exc_info=True)
        raise
def search_posts_by_topic_name(db: Session, topic_name: str, skip: int = 0, limit: int = 100):
    """Search posts by topic name with eager loading including creator"""
    posts = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.steps),
            joinedload(Post.post_materials).joinedload(PostMaterial.material),
            joinedload(Post.creator),
            joinedload(Post.updater),
            joinedload(Post.approver)
        )\
        .join(Post.topics)\
        .filter(Topic.name.ilike(f"%{topic_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [PostOut.from_db_model(post) for post in posts]
def search_posts_by_tag_name(db: Session, tag_name: str, skip: int = 0, limit: int = 100):
    """Search posts by tag name with eager loading including creator"""
    posts = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.steps),
            joinedload(Post.post_materials).joinedload(PostMaterial.material),
            joinedload(Post.creator),
            joinedload(Post.updater),
            joinedload(Post.approver)
        )\
        .join(Post.tags)\
        .filter(Tag.name.ilike(f"%{tag_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [PostOut.from_db_model(post) for post in posts]
def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    """Get all posts for admin/moderator with creator info"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material),
                joinedload(Post.creator),
                joinedload(Post.updater),
                joinedload(Post.approver)
            )\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return [PostOut.from_db_model(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_all_posts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def get_post_by_id(db: Session, post_id: UUID) -> PostOut:
    """Get a single post by ID with all relationships including creator"""
    try:
        post = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material),
                joinedload(Post.creator),
                joinedload(Post.updater),
                joinedload(Post.approver)
            )\
            .filter(Post.post_id == post_id)\
            .first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return PostOut.from_db_model(post)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_post_by_id: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def get_my_posts(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> list[PostOut]:
    """Get user's posts with creator info"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material),
                joinedload(Post.creator),
                joinedload(Post.updater),
                joinedload(Post.approver)
            )\
            .filter(Post.created_by == user_id)\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # Convert to Pydantic models explicitly
        return [PostOut.from_db_model(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_my_posts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
def update_post(db: Session, post_id: UUID, post_data: PostUpdate) -> PostOut:
    # Get the actual DB model, not the Pydantic model
    existing_post = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.steps),
            joinedload(Post.post_materials).joinedload(PostMaterial.material),
            joinedload(Post.creator)  # Add creator join
        )\
        .filter(Post.post_id == post_id)\
        .first()

    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Store old comments count to decide whether to delete them
    old_comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()

    try:
        # Update basic fields if provided
        if post_data.title is not None:
            existing_post.title = post_data.title
        if post_data.content is not None:
            existing_post.content = post_data.content
        if post_data.rejection_reason is not None:
            existing_post.rejection_reason = post_data.rejection_reason
        if post_data.updated_by is not None:
            existing_post.updated_by = post_data.updated_by

        # Clear existing relationships and recreate them
        if post_data.tag_ids is not None:
            existing_post.tags.clear()
            if post_data.tag_ids:
                tags = db.query(Tag).filter(Tag.tag_id.in_(post_data.tag_ids)).all()
                existing_post.tags = tags

        if post_data.topic_ids is not None:
            existing_post.topics.clear()
            if post_data.topic_ids:
                topics = db.query(Topic).filter(Topic.topic_id.in_(post_data.topic_ids)).all()
                existing_post.topics = topics

        # Handle materials update
        if post_data.materials is not None:
            # Remove existing post_materials
            db.query(PostMaterial).filter(PostMaterial.post_id == post_id).delete()
            
            # Add new materials
            for material_data in post_data.materials:
                material = db.query(Material).filter(
                    Material.material_id == material_data.material_id
                ).first()
                if not material:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Material {material_data.material_id} not found"
                    )
                post_material = PostMaterial(
                    post_id=post_id,
                    material_id=material_data.material_id,
                    quantity=material_data.quantity,
                    unit=material.unit.name if hasattr(material.unit, 'name') else (material.unit if isinstance(material.unit, str) else None)
                )
                db.add(post_material)

        # Handle images update
        if post_data.images is not None:
            # Remove existing images
            db.query(PostImage).filter(PostImage.post_id == post_id).delete()
            
            # Add new images
            for image_url in post_data.images:
                db_image = PostImage(image_url=image_url, post_id=post_id)
                db.add(db_image)

        # Handle steps update
        if post_data.steps is not None:
            # Remove existing steps
            db.query(Step).filter(Step.post_id == post_id).delete()
            
            # Validate step order numbers
            if post_data.steps:
                order_numbers = [step.order_number for step in post_data.steps]
                if len(order_numbers) != len(set(order_numbers)):
                    raise HTTPException(
                        status_code=400,
                        detail="Duplicate step order numbers are not allowed"
                    )
            
            # Add new steps
            for step_data in post_data.steps:
                step = Step(
                    post_id=post_id,
                    order_number=step_data.order_number,
                    content=step_data.content
                )
                db.add(step)

        # Check if content changed
        content_changed = (post_data.title is not None and post_data.title != existing_post.title) or \
                         (post_data.content is not None and post_data.content != existing_post.content) or \
                         post_data.materials is not None or post_data.images is not None or post_data.steps is not None

        # Handle status changes based on content changes and current status
        if content_changed:
            # If post was rejected and user makes changes, resubmit for review
            if existing_post.status == PostStatusEnum.rejected:
                existing_post.status = PostStatusEnum.waiting
                existing_post.rejection_reason = None
                existing_post.approved_by = None
            # If post had comments and content changed, reset status and delete comments
            elif old_comments_count > 0:
                existing_post.status = PostStatusEnum.waiting
                existing_post.rejection_reason = None
                existing_post.approved_by = None
            
            # Delete all comments if there were any (for both rejected posts and posts with comments)
            if old_comments_count > 0:
                db.query(Comment).filter(Comment.post_id == post_id).delete()

        # Update the updated_at timestamp
        existing_post.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        # Return the updated post using get_post_by_id to ensure all relationships are loaded
        return get_post_by_id(db, post_id)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_post(db: Session, post_id: UUID):
    post = get_post_by_id(db, post_id)
    try:
        db.delete(post)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def moderate_post(db: Session, post_id: UUID, moderation_data: PostModeration) -> PostOut:
    """Moderate a post (approve/reject) with creator info"""
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = moderation_data.status
    post.rejection_reason = moderation_data.rejection_reason
    post.approved_by = moderation_data.approved_by
    post.updated_at = datetime.now(timezone.utc)

    db.commit()
    
    # Return with creator info
    return get_post_by_id(db, post_id)