from fastapi import APIRouter
from database import get_all_cameras

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("/")
def list_cameras():
    return {"cameras": get_all_cameras()}
