from fastapi import APIRouter, UploadFile, File
import numpy as np
import cv2
from processor import detectar_placa
from database import (
    save_plate,
    is_authorized_plate,
    save_detection,
    create_alert,
    get_all_detections,
)

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.post("/detect")
async def detect(file: UploadFile = File(...), camera_id: int = 1):
    """
    Recibe una imagen, corre YOLO+OCR, valida contra vehicles,
    guarda en detections y crea alerta si no está autorizada.
    """
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Imagen inválida"}

    raw_plates = detectar_placa(frame)

    if not raw_plates:
        return {"resultado": "sin_deteccion", "placas": []}

    results = []
    for p in raw_plates:
        plate_text = p["placa"]
        confidence = p["confianza_ocr"]

        # ── 1. Verificar autorización ──────────────────────────────────
        authorized = is_authorized_plate(plate_text)
        status = "AUTORIZADO" if authorized else "NO AUTORIZADO"

        # ── 2. Guardar en detections ───────────────────────────────────
        try:
            save_detection(
                plate_text=plate_text,
                confidence=confidence,
                authorized=authorized,
                camera_id=camera_id,
            )
        except Exception as e:
            print(f"Error guardando detección: {e}")

        # ── 3. Crear alerta si no autorizada ───────────────────────────
        if not authorized:
            try:
                create_alert(plate_text, camera_id)
            except Exception as e:
                print(f"Error creando alerta: {e}")

        # ── 4. Guardar imagen en plates (historial) ────────────────────
        try:
            save_plate(plate_text, frame)
        except Exception as e:
            print(f"Error guardando plate: {e}")

        results.append({
            "plate": plate_text,
            "authorized": authorized,
            "status": status,
            "confidence": confidence,
            "confianza_yolo": p["confianza_yolo"],
        })

        print(f"{'✅' if authorized else '🚫'} {plate_text} — {status} ({confidence:.0%})")

    return {"resultado": "ok", "placas": results}


@router.get("/")
def list_detections(limit: int = 100):
    return {"detections": get_all_detections(limit)}
