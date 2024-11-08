from src import *
from fastapi import APIRouter
router = APIRouter()
router.include_router(home_router)
router.include_router(auth_router)
router.include_router(database_router)
