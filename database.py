import os
import cv2
from datetime import datetime
from supabase import create_client, Client

# ─────────────────────────────────────────────
#  Configuración — pega tus credenciales aquí
# ─────────────────────────────────────────────
SUPABASE_URL = "https://ecwomhimxcypilnuatdn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNzM0MTAsImV4cCI6MjA5MjY0OTQxMH0.uqHcrfBjNTNXaRNbD-BlO6dv6HjmNXnCd9buA9Rn-1w"

STORAGE_BUCKET = "plate-images"

_client: Client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        if "TU_PROJECT" in SUPABASE_URL:
            raise ValueError("Configura SUPABASE_URL y SUPABASE_KEY en database.py")
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

        url = client.storage.from_(STORAGE_BUCKET).get_public_url(filename)
        return url

    except Exception as e:
        print(f"Error subiendo imagen: {e}")
        return ""


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