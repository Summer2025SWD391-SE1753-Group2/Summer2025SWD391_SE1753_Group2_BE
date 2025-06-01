from fastapi import APIRouter
from app.apis.v1.endpoints import roles, accounts, auth

api_router = APIRouter()
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
