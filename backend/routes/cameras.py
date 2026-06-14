from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from database import create_camera, get_all_cameras

router = APIRouter(prefix="/cameras", tags=["Cameras"])


class CameraCreate(BaseModel):
    name: str
    location: Optional[str] = None
    camera_code: Optional[str] = None
    status: str = "activo"
    active: bool = True


@router.get("/")
def list_cameras():
    return {"cameras": get_all_cameras()}


@router.post("/")
def register_camera(camera: CameraCreate):
    return {
        "camera": create_camera(
            name=camera.name,
            location=camera.location,
            camera_code=camera.camera_code,
            status=camera.status,
            active=camera.active,
        )
    }
