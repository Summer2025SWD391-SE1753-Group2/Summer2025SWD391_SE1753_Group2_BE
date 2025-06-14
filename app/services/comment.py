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

        # If parent_comment_id exists, validate and get parent comment
        if comment.parent_comment_id:
            parent_comment = db.query(Comment).filter(Comment.comment_id == comment.parent_comment_id).first()
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found")
            if parent_comment.post_id != comment.post_id:
                raise HTTPException(status_code=400, detail="Parent comment must be from the same post")
            # Level của comment con = level của comment cha + 1
            level = parent_comment.level + 1

        # Tạo comment mới với level đã tính
        comment_data = {
            "post_id": comment.post_id,
            "account_id": user_id,
            "content": comment.content,
            "parent_comment_id": comment.parent_comment_id if comment.parent_comment_id else None,
            "level": level
        }

        db_comment = Comment(**comment_data)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    @staticmethod
    def get_comment(db: Session, comment_id: UUID) -> Comment:
        return db.query(Comment).filter(Comment.comment_id == comment_id).first()

    @staticmethod
    def get_comments_by_post(
        db: Session,
        post_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Comment]:
        from sqlalchemy.orm import joinedload
        from app.db.models.comment import CommentStatusEnum
        
        # Validate post exists
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get all comments (including deleted ones to show them with special message)
        all_comments = db.query(Comment)\
            .options(joinedload(Comment.account))\
            .filter(Comment.post_id == post_id)\
            .filter(Comment.status.in_([CommentStatusEnum.active, CommentStatusEnum.deleted]))\
            .order_by(Comment.created_at.asc())\
            .all()

        # Create a dictionary to store comments by their ID
        comment_dict = {comment.comment_id: comment for comment in all_comments}
        
        # Initialize replies list for all comments (including deleted ones)
        for comment in all_comments:
            comment.replies = []
        
        # Build nested structure
        root_comments = []
        for comment in all_comments:
            if comment.parent_comment_id is None:
                root_comments.append(comment)
            else:
                parent = comment_dict.get(comment.parent_comment_id)
                if parent:
                    parent.replies.append(comment)

        # Recursive function to sort replies by created_at
        def sort_replies(comment_list):
            for comment in comment_list:
                if hasattr(comment, 'replies') and comment.replies:
                    comment.replies.sort(key=lambda x: x.created_at)
                    sort_replies(comment.replies)

        # Sort all replies recursively
        sort_replies(root_comments)

        # Sort root comments by created_at desc and apply pagination
        root_comments.sort(key=lambda x: x.created_at, reverse=True)
        return root_comments[skip:skip + limit]

    @staticmethod
    def get_nested_comments(db: Session, post_id: str) -> list[Comment]:
        """
        Get all comments for a post with their nested replies.
        This method returns all comments including deleted ones to show with special UI.
        """
        from sqlalchemy.orm import joinedload
        from app.db.models.comment import CommentStatusEnum
        
        # Validate post exists
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Get all comments (including deleted ones to show them with special message)
        all_comments = db.query(Comment)\
            .options(joinedload(Comment.account))\
            .filter(Comment.post_id == post_id)\
            .filter(Comment.status.in_([CommentStatusEnum.active, CommentStatusEnum.deleted]))\
            .order_by(Comment.created_at.asc())\
            .all()

        # Create a dictionary to store comments by their ID
        comment_dict = {comment.comment_id: comment for comment in all_comments}
        
        # Initialize replies list for all comments (including deleted ones)
        for comment in all_comments:
            comment.replies = []
        
        # Build nested structure
        root_comments = []
        for comment in all_comments:
            if comment.parent_comment_id is None:
                root_comments.append(comment)
            else:
                parent = comment_dict.get(comment.parent_comment_id)
                if parent:
                    parent.replies.append(comment)

        # Recursive function to sort replies by created_at
        def sort_replies(comment_list):
            for comment in comment_list:
                if hasattr(comment, 'replies') and comment.replies:
                    comment.replies.sort(key=lambda x: x.created_at)
                    sort_replies(comment.replies)

        # Sort all replies recursively
        sort_replies(root_comments)

        # Sort root comments by created_at desc
        root_comments.sort(key=lambda x: x.created_at, reverse=True)
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
        from app.db.models.comment import CommentStatusEnum
        
        db_comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        # Soft delete by changing status
        db_comment.status = CommentStatusEnum.deleted
        db.commit()
        db.refresh(db_comment)
        return db_comment
