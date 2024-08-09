import hashlib

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer

import database

router = APIRouter(prefix="/user")
