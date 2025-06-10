from fastapi import APIRouter
from app.apis.v1.endpoints import roles, accounts, auth,tags,materials,topics,posts,units


api_router = APIRouter()
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
api_router.include_router(topics.router, prefix="/topics", tags=["Topics"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
api_router.include_router(units.router, prefix="/units", tags=["Units"])