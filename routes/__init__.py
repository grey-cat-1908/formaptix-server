from fastapi import APIRouter

from . import admin

router = APIRouter()

router.include_router(admin.router)
