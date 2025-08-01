from fastapi import APIRouter
from app.apis.v1.endpoints import roles, accounts, auth, tags, materials, topics, posts, units, groups, group_members, comments, favourites, friend, feedback, feedback_types, chat, group_chat,report


api_router = APIRouter()
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
api_router.include_router(topics.router, prefix="/topics", tags=["Topics"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
api_router.include_router(units.router, prefix="/units", tags=["Units"])
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(group_members.router, prefix="/group-members", tags=["Group Members"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(favourites.router, prefix="/favourites", tags=["Favorites"])
api_router.include_router(friend.router, prefix="/friends", tags=["Friends"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(feedback_types.router, prefix="/feedback-types", tags=["Feedback Types"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(group_chat.router, prefix="/group-chat", tags=["Group Chat"])
api_router.include_router(report.router, prefix="/report", tags=["Report"])
