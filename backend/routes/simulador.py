from fastapi import APIRouter
from pydantic import BaseModel
from database import save_simulation, is_authorized_plate

router = APIRouter(prefix="/simulate", tags=["simulator"])

class SimulationRequest(BaseModel):
    plate_text: str
    city: str
    vehicle_type: str = None
    camera_code: str = None

@router.post("/")
def simulate(data: SimulationRequest):
    authorized = is_authorized_plate(data.plate_text)
    save_simulation(
        plate_text=data.plate_text,
        city=data.city,
        vehicle_type=data.vehicle_type,
        camera_code=data.camera_code,
        authorized=authorized
    )
    return {"plate_text": data.plate_text, "authorized": authorized}