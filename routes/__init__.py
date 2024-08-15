from fastapi import APIRouter

from . import admin
from . import user
from . import form
from . import answer

router = APIRouter()

router.include_router(admin.router)
router.include_router(user.router)
router.include_router(form.router)
router.include_router(answer.router)
