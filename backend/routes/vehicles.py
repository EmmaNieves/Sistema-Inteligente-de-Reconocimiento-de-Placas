from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from database import get_all_vehicles, add_vehicle, remove_vehicle, is_authorized_plate

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


class VehicleIn(BaseModel):
    plate: str
    owner: Optional[str] = None
    description: Optional[str] = None


@router.get("/")
def list_vehicles():
    return {"vehicles": get_all_vehicles()}


@router.post("/")
def create_vehicle(body: VehicleIn):
    add_vehicle(body.plate.upper(), body.owner, body.description)
    return {"ok": True, "plate": body.plate.upper()}


@router.delete("/{plate}")
def delete_vehicle(plate: str):
    remove_vehicle(plate.upper())
    return {"ok": True, "plate": plate.upper()}


@router.get("/check/{plate}")
def check_vehicle(plate: str):
    authorized = is_authorized_plate(plate.upper())
    return {
        "plate": plate.upper(),
        "authorized": authorized,
        "status": "AUTORIZADO" if authorized else "NO AUTORIZADO"
    }
