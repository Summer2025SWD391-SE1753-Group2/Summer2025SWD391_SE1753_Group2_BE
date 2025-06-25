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
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
def search_posts(db: Session, title: str, skip: int = 0, limit: int = 100):
    """Search posts by title using case-insensitive partial match"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.title.ilike(f"%{title}%"))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [PostOut.model_validate(post) for post in posts]
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

        post = Post(
            title=post_data.title,
            content=post_data.content,
            status=post_data.status,
            created_by=post_data.created_by,
            updated_by=post_data.created_by,
        )

        # If status is approved, set approved_by
        if post_data.status == PostStatusEnum.approved:
            post.approved_by = post_data.created_by

        db.add(post)
        db.commit()
        db.refresh(post)

        # Handle materials with quantities
        if post_data.materials:
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

                # Create PostMaterial entry using material's fixed unit
                post_material = PostMaterial(
                    post_id=post.post_id,
                    material_id=material_data.material_id,
                    quantity=material_data.quantity
                )
                db.add(post_material)

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

        db.commit()
        db.refresh(post)
        return get_post_by_id(db, post.post_id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
def get_approved_posts(db: Session, skip: int = 0, limit: int = 100) -> List[PostOut]:
    """Get all approved posts with eager loading of relationships"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.status == PostStatusEnum.approved)\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        return [PostOut.model_validate(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_approved_posts: {str(e)}", exc_info=True)
        raise
def search_posts_by_topic_name(db: Session, topic_name: str, skip: int = 0, limit: int = 100):
    """Search posts by topic name with eager loading"""
    posts = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.steps),
            joinedload(Post.post_materials).joinedload(PostMaterial.material)
        )\
        .join(Post.topics)\
        .filter(Topic.name.ilike(f"%{topic_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    return [PostOut.model_validate(post) for post in posts]
def search_posts_by_tag_name(db: Session, tag_name: str, skip: int = 0, limit: int = 100):
    """Search posts by tag name with eager loading"""
    posts = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.steps),
            joinedload(Post.post_materials).joinedload(PostMaterial.material)
        )\
        .join(Post.tags)\
        .filter(Tag.name.ilike(f"%{tag_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    return [PostOut.model_validate(post) for post in posts]
def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    """Get all posts with eager loading of relationships"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # Convert to Pydantic models explicitly
        return [PostOut.model_validate(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_all_posts: {str(e)}", exc_info=True)
        raise

def get_post_by_id(db: Session, post_id: UUID) -> PostOut:
    """Get a post by ID with all relationships loaded"""
    try:
        post = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.post_id == post_id)\
            .first()
            
        if not post:
            raise HTTPException(
                status_code=404, 
                detail="Post not found"
            )

        return PostOut.model_validate(post)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_post_by_id: {str(e)}", exc_info=True)
        raise
def get_my_posts(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> list[PostOut]:
    """Get all posts created by a specific user with eager loading of relationships"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.steps),
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.created_by == user_id)\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # Convert to Pydantic models explicitly
        return [PostOut.model_validate(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_my_posts: {str(e)}", exc_info=True)
        raise
def update_post(db: Session, post_id: UUID, post_data: PostUpdate) ->  PostOut:
    # Get the actual DB model, not the Pydantic model
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        # Check if post is rejected
        if post.status == "rejected":
            raise HTTPException(
                status_code=400,
                detail="Cannot edit a rejected post"
            )

        # Set status based on user role
        current_user = db.query(Account).filter(Account.account_id == post_data.updated_by).first()
        if current_user and current_user.role.role_name in ["moderator", "admin"]:
            post_data.status = "approved"
        elif post.status in ["waiting", "approved"]:
            post_data.status = "waiting"

        # Validate required fields if provided
        if post_data.topic_ids is not None and not post_data.topic_ids:
            raise HTTPException(
                status_code=400,
                detail="At least one topic is required"
            )
        if post_data.materials is not None and not post_data.materials:
            raise HTTPException(
                status_code=400,
                detail="At least one material is required"
            )

        # Validate step order numbers if provided
        if post_data.steps is not None:
            order_numbers = [step.order_number for step in post_data.steps]
            if len(order_numbers) != len(set(order_numbers)):
                raise HTTPException(
                    status_code=400,
                    detail="Duplicate step order numbers are not allowed"
                )
        # IMPORTANT: When post is updated, it needs to go through moderation again
        # Set status to waiting and clear previous moderation data
        post.status = PostStatusEnum.waiting
        post.approved_by = None
        post.rejection_reason = None
        
        # Delete all comments related to this post (as per requirement)
        db.query(Comment).filter(Comment.post_id == post_id).delete()
        
        # Update basic fields - Only update what's provided in PostUpdate
        if post_data.title is not None:
            post.title = post_data.title
        if post_data.content is not None:
            post.content = post_data.content
        if post_data.updated_by is not None:
            post.updated_by = post_data.updated_by
        
        # Update tags
        if post_data.tag_ids is not None:
            tags = db.query(Tag).filter(Tag.tag_id.in_(post_data.tag_ids)).all()
            if len(tags) != len(post_data.tag_ids):
                raise HTTPException(status_code=400, detail="One or more tag IDs not found")
            post.tags = tags

        # Update topics
        if post_data.topic_ids is not None:
            topics = db.query(Topic).filter(Topic.topic_id.in_(post_data.topic_ids)).all()
            if len(topics) != len(post_data.topic_ids):
                raise HTTPException(status_code=400, detail="One or more topic IDs not found")
            post.topics = topics
         # Update steps
        if post_data.steps is not None:
            # Remove existing steps
            db.query(Step).filter(Step.post_id == post_id).delete()
            
            # Add new steps
            for step_data in post_data.steps:
                step = Step(
                    post_id=post.post_id,
                    order_number=step_data.order_number,
                    content=step_data.content
                )
                db.add(step)
        # Update materials
        if post_data.materials is not None:
            # Remove existing materials
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
                    post_id=post.post_id,
                    material_id=material_data.material_id,
                    quantity=material_data.quantity
                )
                db.add(post_material)
        # Update images
        if post_data.images is not None:
            # Remove existing images
            db.query(PostImage).filter(PostImage.post_id == post_id).delete()
            
            # Add new images
            for image_url in post_data.images:
                db_image = PostImage(image_url=image_url, post_id=post.post_id)
                db.add(db_image)

        db.commit()
        # Refresh post with all relationships loaded
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
    """Moderate a post by updating its status and rejection reason"""
    try:
        # Get post and moderator
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=404,
                detail="Post not found"
            )

        moderator = db.query(Account).filter(Account.account_id == moderation_data.approved_by).first()
        if not moderator:
            raise HTTPException(
                status_code=404,
                detail="Moderator not found"
            )

        # Check if moderator has correct role
        if moderator.role.role_name not in [RoleNameEnum.moderator, RoleNameEnum.admin]:
            raise HTTPException(
                status_code=403,
                detail="Only moderators and admins can moderate posts"
            )

        # Prevent self-moderation
        if post.created_by == moderation_data.approved_by:
            raise HTTPException(
                status_code=403,
                detail="Users cannot moderate their own posts"
            )

        # Update post status and rejection reason
        post.status = moderation_data.status
        post.approved_by = moderation_data.approved_by
        
        # Set rejection reason only if status is rejected
        if moderation_data.status == PostStatusEnum.rejected:
            if not moderation_data.rejection_reason:
                raise HTTPException(
                    status_code=400,
                    detail="Rejection reason is required when rejecting a post"
                )
            post.rejection_reason = moderation_data.rejection_reason
        else:
            post.rejection_reason = None

        db.commit()
        db.refresh(post)
        return get_post_by_id(db, post_id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))