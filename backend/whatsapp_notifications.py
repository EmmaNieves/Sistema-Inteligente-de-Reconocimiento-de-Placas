# ============================================================
# whatsapp_notifications.py — Notificaciones WhatsApp
# Integrante 4: Base de Datos, Seguridad y Notificaciones
# ============================================================

import requests
import os

# ── Credenciales (poner en .env) ─────────────────────────────
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")        # Token generado en Meta
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")      # 1094617207078932
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# Número del administrador que recibirá las alertas
ADMIN_PHONE = os.getenv("ADMIN_PHONE")   # ej: 573156337544

# ────────────────────────────────────────────────────────────
# FUNCIÓN BASE — enviar mensaje de texto
# ────────────────────────────────────────────────────────────

def enviar_whatsapp(numero_destino: str, mensaje: str) -> bool:
    """
    Envía un mensaje de texto por WhatsApp.
    numero_destino: formato internacional sin + (ej: 573156337544)
    """
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": mensaje}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=body)

    if response.status_code == 200:
        print(f"✅ Mensaje enviado a {numero_destino}")
        return True
    else:
        print(f"❌ Error al enviar: {response.text}")
        return False


# ────────────────────────────────────────────────────────────
# ALERTA 1 — Placa no registrada detectada
# ────────────────────────────────────────────────────────────

def alerta_placa_no_registrada(placa: str, camara: str, fecha_hora: str):
    """
    Se llama cuando el sistema detecta una placa que NO está en la BD.
    """
    mensaje = (
        f"🚨 *ALERTA - Placa No Registrada*\n\n"
        f"📋 Placa: *{placa}*\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}\n\n"
        f"⚠️ Esta placa no está en el sistema. Verifique manualmente."
    )
    enviar_whatsapp(ADMIN_PHONE, mensaje)


# ────────────────────────────────────────────────────────────
# ALERTA 2 — Placa en lista negra detectada
# ────────────────────────────────────────────────────────────

def alerta_placa_lista_negra(placa: str, camara: str, fecha_hora: str, motivo: str = ""):
    """
    Se llama cuando el sistema detecta una placa que está en lista negra.
    """
    mensaje = (
        f"🔴 *ALERTA CRÍTICA - Placa Lista Negra*\n\n"
        f"📋 Placa: *{placa}*\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}\n"
        f"📌 Motivo: {motivo or 'No especificado'}\n\n"
        f"🚫 Acceso DENEGADO automáticamente. Tome acción inmediata."
    )
    enviar_whatsapp(ADMIN_PHONE, mensaje)


# ────────────────────────────────────────────────────────────
# ALERTA 3 — Placa autorizada (confirmación de ingreso)
# ────────────────────────────────────────────────────────────

def notificar_ingreso_autorizado(placa: str, camara: str, fecha_hora: str, propietario: str = ""):
    """
    Notificación opcional cuando una placa autorizada ingresa.
    """
    mensaje = (
        f"✅ *Ingreso Autorizado*\n\n"
        f"📋 Placa: *{placa}*\n"
        f"👤 Propietario: {propietario or 'Registrado'}\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}"
    )
    enviar_whatsapp(ADMIN_PHONE, mensaje)


# ────────────────────────────────────────────────────────────
# USO DESDE EL BACKEND (el Integrante 3 llama estas funciones)
# ────────────────────────────────────────────────────────────

# Ejemplo de cómo el Integrante 3 (IA/detección) llama esto:
#
# from whatsapp_notifications import alerta_placa_no_registrada, alerta_placa_lista_negra
#
# Cuando detecta placa desconocida:
#   alerta_placa_no_registrada("ABC123", "Camara-01", "2026-06-13 15:30:00")
#
# Cuando detecta placa en lista negra:
#   alerta_placa_lista_negra("XYZ999", "Camara-02", "2026-06-13 15:31:00", "Robo reportado")
