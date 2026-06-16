# ============================================================
# whatsapp_notifications.py — Notificaciones WhatsApp
# Integrante 4: Base de Datos, Seguridad y Notificaciones
# ============================================================

import requests
import os

# ── Credenciales (poner en .env) ─────────────────────────────
WHATSAPP_TOKEN   = os.getenv("WHATSAPP_TOKEN")       # Token generado en Meta
PHONE_NUMBER_ID  = os.getenv("PHONE_NUMBER_ID")      # ej: 1094617207078932
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# Números que recibirán las alertas (formato internacional sin +)
ADMIN_PHONES = [
    n.strip().lstrip("+")
    for n in [
        os.getenv("WHATSAPP_NUMBER_1", "573243333381"),
        os.getenv("WHATSAPP_NUMBER_2", "573332487255"),
    ]
    if n.strip()
]


# ────────────────────────────────────────────────────────────
# FUNCIÓN BASE — enviar mensaje a TODOS los admins
# ────────────────────────────────────────────────────────────

def enviar_whatsapp(mensaje: str) -> bool:
    """Envía un mensaje de texto a todos los números configurados."""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️  WhatsApp no configurado (WHATSAPP_TOKEN / PHONE_NUMBER_ID faltantes)")
        return False

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    exito = True
    for numero in ADMIN_PHONES:
        body = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensaje},
        }
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=body)
        if response.status_code == 200:
            print(f"✅ Mensaje enviado a {numero}")
        else:
            print(f"❌ Error al enviar a {numero}: {response.text}")
            exito = False
    return exito


# ────────────────────────────────────────────────────────────
# ALERTA 1 — Placa no registrada detectada
# ────────────────────────────────────────────────────────────

def alerta_placa_no_registrada(placa: str, camara: str, fecha_hora: str):
    mensaje = (
        f"🚨 *ALERTA - Placa No Registrada*\n\n"
        f"📋 Placa: *{placa}*\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}\n\n"
        f"⚠️ Esta placa no está en el sistema. Verifique manualmente."
    )
    enviar_whatsapp(mensaje)


# ────────────────────────────────────────────────────────────
# ALERTA 2 — Placa en lista negra detectada
# ────────────────────────────────────────────────────────────

def alerta_placa_lista_negra(placa: str, camara: str, fecha_hora: str, motivo: str = ""):
    mensaje = (
        f"🔴 *ALERTA CRÍTICA - Placa Lista Negra*\n\n"
        f"📋 Placa: *{placa}*\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}\n"
        f"📌 Motivo: {motivo or 'No especificado'}\n\n"
        f"🚫 Acceso DENEGADO automáticamente. Tome acción inmediata."
    )
    enviar_whatsapp(mensaje)


# ────────────────────────────────────────────────────────────
# ALERTA 3 — Placa autorizada (confirmación de ingreso)
# ────────────────────────────────────────────────────────────

def notificar_ingreso_autorizado(placa: str, camara: str, fecha_hora: str, propietario: str = ""):
    mensaje = (
        f"✅ *Ingreso Autorizado*\n\n"
        f"📋 Placa: *{placa}*\n"
        f"👤 Propietario: {propietario or 'Registrado'}\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}"
    )
    enviar_whatsapp(mensaje)
