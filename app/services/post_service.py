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
from app.schemas.post import PostOut
from app.db.models.unit import Unit
from app.db.models.post_material import PostMaterial
from sqlalchemy.orm import Session, joinedload
import logging
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
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.title.ilike(f"%{title}%"))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [PostOut.from_orm(post) for post in posts]
    except Exception as e:
        logger.error(f"Error in search_posts: {str(e)}", exc_info=True)
        raise



def create_post(db: Session, post_data: PostCreate) -> Post:
    try:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            status=post_data.status,
            rejection_reason=post_data.rejection_reason,
            created_by=post_data.created_by,
            updated_by=post_data.created_by,
        )

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
                db_image = PostImage(image_url=image_url, post_id=post.post_id)  # Changed from url to image_url
                db.add(db_image)

        db.commit()
        db.refresh(post)
        return get_post_by_id(db, post.post_id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
def search_posts_by_topic_name(db: Session, topic_name: str, skip: int = 0, limit: int = 100):
    """Search posts by topic name with eager loading"""
    posts = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.post_materials).joinedload(PostMaterial.material)
        )\
        .join(Post.topics)\
        .filter(Topic.name.ilike(f"%{topic_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    return [PostOut.from_orm(post) for post in posts]
def search_posts_by_tag_name(db: Session, tag_name: str, skip: int = 0, limit: int = 100):
    """Search posts by tag name with eager loading"""
    posts = db.query(Post)\
        .options(
            joinedload(Post.tags),
            joinedload(Post.topics),
            joinedload(Post.images),
            joinedload(Post.post_materials).joinedload(PostMaterial.material)
        )\
        .join(Post.tags)\
        .filter(Tag.name.ilike(f"%{tag_name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
        
    return [PostOut.from_orm(post) for post in posts]
def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    """Get all posts with eager loading of relationships"""
    try:
        posts = db.query(Post)\
            .options(
                joinedload(Post.tags),
                joinedload(Post.topics),
                joinedload(Post.images),
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # Convert to Pydantic models explicitly
        return [PostOut.from_orm(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_all_posts: {str(e)}", exc_info=True)
        raise

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
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.post_id == post_id)\
            .first()
            
        if not post:
            raise HTTPException(
                status_code=404, 
                detail="Post not found"
            )

        return PostOut.from_orm(post)

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
                joinedload(Post.post_materials).joinedload(PostMaterial.material)
            )\
            .filter(Post.created_by == user_id)\
            .order_by(Post.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()

        # Convert to Pydantic models explicitly
        return [PostOut.from_orm(post) for post in posts]

    except Exception as e:
        logger.error(f"Error in get_my_posts: {str(e)}", exc_info=True)
        raise
def update_post(db: Session, post_id: UUID, post_data: PostUpdate) -> Post:
    post = get_post_by_id(db, post_id)

    try:
        # Update basic fields
        post.title = post_data.title
        post.content = post_data.content
        post.status = post_data.status
        post.rejection_reason = post_data.rejection_reason
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