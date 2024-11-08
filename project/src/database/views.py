from fastapi import APIRouter

router = APIRouter(prefix='/database', tags=['database'])


@router.get('/')
async def database():
    return 'database'
