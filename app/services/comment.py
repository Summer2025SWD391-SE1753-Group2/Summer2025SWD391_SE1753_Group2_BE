from sqlalchemy.orm import Session
from app.db.models.comment import Comment
from app.db.models.post import Post, PostStatusEnum
from app.db.models.account import Account
from app.schemas.comment import CommentCreate, CommentUpdate
from fastapi import HTTPException
from uuid import UUID

class CommentService:
    @staticmethod
    def create_comment(db: Session, comment: CommentCreate, user_id: str) -> Comment:
        # Validate post exists and is approved
        post = db.query(Post).filter(Post.post_id == comment.post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.status != PostStatusEnum.approved:
            raise HTTPException(status_code=400, detail="Cannot comment on unapproved post")

        # Validate account exists
        account = db.query(Account).filter(Account.account_id == user_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Set default level and parent comment
        level = 1
        parent_comment = None
        print(f"Initial level: {level}") # In ra level khởi tạo
        print(f"Initial parent_comment: {parent_comment}") # In ra parent_comment khởi tạo

        # If parent_comment_id exists, validate and get parent comment
        if comment.parent_comment_id:
            parent_comment = db.query(Comment).filter(Comment.comment_id == comment.parent_comment_id).first()
            print(f"Parent comment found (after query): {parent_comment.comment_id if parent_comment else 'None'}") # In ra parent_comment_id nếu tìm thấy
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found")
            if parent_comment.post_id != comment.post_id:
                raise HTTPException(status_code=400, detail="Parent comment must be from the same post")
            # Level của comment con = level của comment cha + 1
            level = parent_comment.level + 1
            print(f"Updated level (based on parent): {level}") # In ra level sau khi cập nhật
            print(f"Parent comment object (after update): {parent_comment}") # In ra đối tượng parent_comment

        # Tạo comment mới với level đã tính
        comment_data = {
            "post_id": comment.post_id,
            "account_id": user_id,
            "content": comment.content,
            "parent_comment_id": comment.parent_comment_id if comment.parent_comment_id else None,
            "level": level  # Gán level đã tính
        }
        print(f"Comment data before creation: {comment_data}") # In ra dữ liệu trước khi tạo

        db_comment = Comment(**comment_data)
        print(f"db_comment created with level: {db_comment.level}") # In ra level của db_comment khi khởi tạo
        print(f"db_comment parent_comment_id: {db_comment.parent_comment_id}") # In ra parent_comment_id của db_comment

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        print(f"db_comment after commit and refresh - comment_id: {db_comment.comment_id}, level: {db_comment.level}") # In ra thông tin sau commit

        # Add parent comment to response if exists
        if comment.parent_comment_id:
            # Gán lại parent_comment sau khi commit để có đầy đủ thông tin
            db_comment.parent_comment = db.query(Comment).filter(Comment.comment_id == comment.parent_comment_id).first()
            print(f"db_comment.parent_comment (after re-query): {db_comment.parent_comment}") # In ra parent_comment sau khi truy vấn lại
            db_comment.parent_level = db_comment.parent_comment.level
            print(f"db_comment.parent_level: {db_comment.parent_level}") # In ra parent_level

        return db_comment

    @staticmethod
    def get_comment(db: Session, comment_id: UUID) -> Comment:
        return db.query(Comment).filter(Comment.comment_id == comment_id).first()

    @staticmethod
    def get_comments_by_post(
        db: Session,
        post_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> list[Comment]:
        # Validate post exists
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get root comments (no parent)
        root_comments = db.query(Comment)\
            .filter(Comment.post_id == post_id)\
            .filter(Comment.parent_comment_id.is_(None))\
            .offset(skip)\
            .limit(limit)\
            .all()

        # For each root comment, get its replies
        for comment in root_comments:
            replies = db.query(Comment)\
                .filter(Comment.parent_comment_id == comment.comment_id)\
                .all()
            comment.replies = replies

        return root_comments

    @staticmethod
    def update_comment(
        db: Session,
        comment_id: UUID,
        comment: CommentUpdate
    ) -> Comment:
        db_comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        for key, value in comment.dict(exclude_unset=True).items():
            setattr(db_comment, key, value)

        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def delete_comment(db: Session, comment_id: UUID) -> Comment:
        db_comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        db.delete(db_comment)
        db.commit()
        return db_comment
