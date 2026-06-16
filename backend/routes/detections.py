from typing import Optional
from datetime import datetime

import cv2
import numpy as np
from fastapi import APIRouter, File, Query, UploadFile

from database import (
    create_alert,
    get_all_detections,
    is_authorized_plate,
    save_detection,
)
from processor import detectar_placa
from whatsapp_notifications import alerta_placa_no_registrada


router = APIRouter(prefix="/detections", tags=["Detections"])


@router.post("/detect")
async def detect(file: UploadFile = File(...), camera_id: Optional[str] = None):
    """
    Recibe una imagen, corre YOLO+OCR, valida contra vehicles,
    guarda en plates y crea alerta si no esta autorizada.
    """
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Imagen invalida"}

    raw_plates = detectar_placa(frame)

    if not raw_plates:
        return {"resultado": "sin_deteccion", "placas": []}

    results = []
    for plate_data in raw_plates:
        plate_text = plate_data["placa"]
        yolo_confidence = plate_data["confianza_yolo"]
        ocr_confidence = plate_data["confianza_ocr"]
        vehicle_type = plate_data.get("vehicle_type", "otro")

        authorized = is_authorized_plate(plate_text)
        status = "AUTORIZADO" if authorized else "NO AUTORIZADO"

        try:
            detection = save_detection(
                plate_text=plate_text,
                confidence=ocr_confidence,
                authorized=authorized,
                camera_id=camera_id,
                image_np=frame,
                yolo_confidence=yolo_confidence,
                ocr_confidence=ocr_confidence,
                vehicle_type=vehicle_type,
            )
        except Exception as exc:
            print(f"Error guardando deteccion: {exc}")
            continue

        if not authorized:
            try:
                create_alert(
                    plate_text,
                    camera_id=detection.get("camera_id") or camera_id,
                    plate_id=detection.get("id"),
                )
            except Exception as exc:
                print(f"Error creando alerta: {exc}")

            # ── Notificación WhatsApp ──────────────────────────────
            try:
                fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                camara_nombre = str(camera_id or "Cámara principal")
                alerta_placa_no_registrada(plate_text, camara_nombre, fecha_hora)
            except Exception as exc:
                print(f"Error enviando WhatsApp: {exc}")

        results.append(
            {
                "id": detection.get("id"),
                "plate": plate_text,
                "authorized": authorized,
                "status": status,
                "confidence": ocr_confidence,
                "confianza_yolo": yolo_confidence,
                "camera_id": detection.get("camera_id"),
                "timestamp": detection.get("timestamp"),
            }
        )

        print(f"{plate_text} - {status} ({ocr_confidence:.0%})")

    return {"resultado": "ok", "placas": results}


@router.get("/")
def list_detections(
    limit: int = 100,
    plate: Optional[str] = Query(None, description="Filtrar por número de placa (parcial)"),
    authorized: Optional[bool] = Query(None, description="Filtrar por estado: true=autorizado, false=no autorizado"),
    camera_id: Optional[str] = Query(None, description="Filtrar por ID de cámara"),
    from_date: Optional[str] = Query(None, alias="from", description="Fecha inicio YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, alias="to", description="Fecha fin YYYY-MM-DD"),
):
    detections = get_all_detections(
        limit=limit,
        plate=plate,
        authorized=authorized,
        camera_id=camera_id,
        from_date=from_date,
        to_date=to_date,
    )
    return detections
