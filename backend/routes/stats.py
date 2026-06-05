from fastapi import APIRouter
from database import get_stats

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/")
def stats():
    return get_stats()
