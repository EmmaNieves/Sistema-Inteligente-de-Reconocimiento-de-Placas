import os
import cv2
from datetime import datetime
from supabase import create_client, Client

# ─────────────────────────────────────────────
#  Configuración
# ─────────────────────────────────────────────
SUPABASE_URL = "https://ecwomhimxcypilnuatdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNzM0MTAsImV4cCI6MjA5MjY0OTQxMH0.uqHcrfBjNTNXaRNbD-BlO6dv6HjmNXnCd9buA9Rn-1w"

STORAGE_BUCKET = "plate-images"

_client: Client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def init_db():
    try:
        client = _get_client()
        client.table("plates").select("id").limit(1).execute()
        print("Conexión a Supabase OK")
    except Exception as e:
        print(f"Error conectando a Supabase: {e}")
        raise


# ─────────────────────────────────────────────
#  Imágenes
# ─────────────────────────────────────────────

def _upload_image(plate_text: str, image_np) -> str:
    try:
        client = _get_client()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plate_text}_{timestamp}.jpg"

        success, buffer = cv2.imencode(".jpg", image_np)
        if not success:
            return ""

        image_bytes = buffer.tobytes()
        client.storage.from_(STORAGE_BUCKET).upload(
            path=filename,
            file=image_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        return client.storage.from_(STORAGE_BUCKET).get_public_url(filename)

    except Exception as e:
        print(f"Error subiendo imagen: {e}")
        return ""


# ─────────────────────────────────────────────
#  Tabla: plates  (registro histórico de imágenes)
# ─────────────────────────────────────────────

def save_plate(plate_text: str, image_np) -> bool:
    client = _get_client()
    existing = (
        client.table("plates")
        .select("id")
        .eq("plate_text", plate_text)
        .execute()
    )
    if existing.data:
        print(f"Placa ya registrada: {plate_text}")
        return False

    image_url = _upload_image(plate_text, image_np)
    client.table("plates").insert({
        "plate_text": plate_text,
        "image_url": image_url,
        "timestamp": datetime.now().isoformat(),
        "status": "registrado"
    }).execute()

    print(f"Placa nueva guardada: {plate_text}")
    return True


def get_all_plates() -> list:
    client = _get_client()
    response = (
        client.table("plates")
        .select("*")
        .order("timestamp", desc=True)
        .execute()
    )
    return response.data


def plate_exists(plate_text: str) -> bool:
    client = _get_client()
    response = (
        client.table("plates")
        .select("id")
        .eq("plate_text", plate_text)
        .execute()
    )
    return len(response.data) > 0


# ─────────────────────────────────────────────
#  Tabla: vehicles  (vehículos autorizados)
# ─────────────────────────────────────────────

def is_authorized_plate(plate_text: str) -> bool:
    """Devuelve True si la placa existe en la tabla vehicles."""
    client = _get_client()
    response = (
        client.table("vehicles")
        .select("id")
        .eq("plate", plate_text)
        .execute()
    )
    return len(response.data) > 0


def get_all_vehicles() -> list:
    client = _get_client()
    response = (
        client.table("vehicles")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def add_vehicle(plate: str, owner: str = None, description: str = None) -> dict:
    client = _get_client()
    return client.table("vehicles").insert({
        "plate": plate,
        "owner": owner,
        "description": description,
        "created_at": datetime.now().isoformat()
    }).execute()


def remove_vehicle(plate: str) -> dict:
    client = _get_client()
    return client.table("vehicles").delete().eq("plate", plate).execute()


# ─────────────────────────────────────────────
#  Tabla: detections  (cada evento detectado)
# ─────────────────────────────────────────────

def save_detection(
    plate_text: str,
    confidence: float,
    authorized: bool,
    camera_id: int = 1,
    image_url: str = None
) -> dict:
    """Guarda cada detección con su estado de autorización."""
    client = _get_client()
    return client.table("detections").insert({
        "plate": plate_text,
        "camera_id": camera_id,
        "confidence": confidence,
        "authorized": authorized,
        "image_url": image_url,
        "timestamp": datetime.now().isoformat()
    }).execute()


def get_all_detections(limit: int = 100) -> list:
    client = _get_client()
    response = (
        client.table("detections")
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


# ─────────────────────────────────────────────
#  Tabla: alertas  (accesos no autorizados)
# ─────────────────────────────────────────────

def create_alert(plate_text: str, camera_id: int = 1) -> dict:
    """Crea alerta para placas no autorizadas."""
    client = _get_client()
    print(f"🚨 Alerta — placa NO autorizada: {plate_text}")
    return client.table("alertas").insert({
        "plate": plate_text,
        "camera_id": camera_id,
        "timestamp": datetime.now().isoformat(),
        "resolved": False
    }).execute()


def get_all_alerts(only_unresolved: bool = False) -> list:
    client = _get_client()
    query = client.table("alertas").select("*").order("timestamp", desc=True)
    if only_unresolved:
        query = query.eq("resolved", False)
    return query.execute().data


def resolve_alert(alert_id: int) -> dict:
    client = _get_client()
    return client.table("alertas").update({"resolved": True}).eq("id", alert_id).execute()


# ─────────────────────────────────────────────
#  Tabla: cameras
# ─────────────────────────────────────────────

def get_all_cameras() -> list:
    client = _get_client()
    response = client.table("cameras").select("*").execute()
    return response.data


# ─────────────────────────────────────────────
#  Estadísticas
# ─────────────────────────────────────────────

def get_stats() -> dict:
    client = _get_client()
    detections = client.table("detections").select("authorized").execute().data
    total = len(detections)
    authorized = sum(1 for d in detections if d.get("authorized"))
    unauthorized = total - authorized
    alerts = client.table("alertas").select("id").eq("resolved", False).execute().data
    vehicles = client.table("vehicles").select("id").execute().data

    return {
        "total_detections": total,
        "authorized": authorized,
        "unauthorized": unauthorized,
        "open_alerts": len(alerts),
        "registered_vehicles": len(vehicles)
    }
