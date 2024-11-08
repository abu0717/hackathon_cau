from fastapi import APIRouter

router = APIRouter(prefix='/diet', tags=['diet'])


@router.get('/')
async def diet():
    return 'diet'
