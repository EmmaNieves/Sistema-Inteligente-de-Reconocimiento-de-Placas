# ============================================================
# whatsapp_notifications.py — Notificaciones WhatsApp
# Usa CallMeBot (gratuito, sin cuenta de desarrollador)
# ============================================================
# SETUP (solo una vez por número):
#   1. Guarda el contacto de CallMeBot: +34 644 65 21 68
#   2. Envíale por WhatsApp: "I allow callmebot to send me messages"
#   3. Recibirás tu apikey por WhatsApp en segundos
#   4. Pon en backend/.env:
#        CALLMEBOT_APIKEY_1=tu_apikey_numero1
#        CALLMEBOT_APIKEY_2=tu_apikey_numero2
#        WHATSAPP_NUMBER_1=573243333381
#        WHATSAPP_NUMBER_2=573332487255
# ============================================================

import os
import requests
from urllib.parse import quote

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php?phone=573243333381&text=This+is+a+test&apikey=2995336"

# Pares (numero, apikey) — lee desde .env
DESTINATARIOS = [
    (
        os.getenv("WHATSAPP_NUMBER_1", "573243333381"),
        os.getenv("CALLMEBOT_APIKEY_1", "2995336"),
    ),
    (
        os.getenv("WHATSAPP_NUMBER_2", "573332487255"),
        os.getenv("CALLMEBOT_APIKEY_2", ""),
    ),
]


# ── FUNCIÓN BASE ─────────────────────────────────────────────

def enviar_whatsapp(mensaje: str) -> bool:
    """Envía el mensaje a todos los números configurados via CallMeBot."""
    exito = True
    for numero, apikey in DESTINATARIOS:
        if not numero or not apikey:
            print(f" Número o apikey no configurado ({numero}) — omitiendo")
            continue
        try:
            resp = requests.get(
                CALLMEBOT_URL,
                params={
                    "phone": numero,
                    "text": mensaje,
                    "apikey": apikey,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                print(f"WhatsApp enviado a {numero}")
            else:
                print(f"Error enviando a {numero}: {resp.status_code} {resp.text}")
                exito = False
        except Exception as exc:
            print(f"Excepción enviando a {numero}: {exc}")
            exito = False
    return exito


# ── ALERTA 1 — Placa no registrada ───────────────────────────

def alerta_placa_no_registrada(placa: str, camara: str, fecha_hora: str):
    mensaje = (
        f"🚨 ALERTA - Placa No Registrada\n\n"
        f"📋 Placa: {placa}\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}\n\n"
        f"⚠️ Esta placa no está en el sistema. Verifique manualmente."
    )
    enviar_whatsapp(mensaje)


# ── ALERTA 2 — Placa en lista negra ──────────────────────────

def alerta_placa_lista_negra(placa: str, camara: str, fecha_hora: str, motivo: str = ""):
    mensaje = (
        f"🔴 ALERTA CRÍTICA - Placa Lista Negra\n\n"
        f"📋 Placa: {placa}\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}\n"
        f"📌 Motivo: {motivo or 'No especificado'}\n\n"
        f"🚫 Acceso DENEGADO. Tome acción inmediata."
    )
    enviar_whatsapp(mensaje)


# ── ALERTA 3 — Ingreso autorizado ────────────────────────────

def notificar_ingreso_autorizado(placa: str, camara: str, fecha_hora: str, propietario: str = ""):
    mensaje = (
        f"✅ Ingreso Autorizado\n\n"
        f"📋 Placa: {placa}\n"
        f"👤 Propietario: {propietario or 'Registrado'}\n"
        f"📍 Cámara: {camara}\n"
        f"🕐 Fecha/Hora: {fecha_hora}"
    )
    enviar_whatsapp(mensaje)


# ── TEST rápido (ejecutar directamente para probar) ──────────
if __name__ == "__main__":
    print("Probando envío de WhatsApp...")
    ok = enviar_whatsapp("🧪 Prueba de conexión PlacaControl - sistema activo")
    print("Resultado:", "✅ OK" if ok else "❌ Falló")
