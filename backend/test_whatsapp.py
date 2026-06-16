# ============================================================
# test_whatsapp.py — Diagnóstico completo de WhatsApp
# Correr con: python test_whatsapp.py
# ============================================================
import os
import sys
import requests

print("=" * 50)
print("DIAGNÓSTICO WHATSAPP - PlacaControl")
print("=" * 50)

# 1. Cargar .env manualmente
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    print(f"\n✅ Archivo .env encontrado en: {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())
else:
    print(f"\n❌ NO se encontró .env en: {env_path}")
    print("   Crea el archivo backend/.env con las variables necesarias")
    sys.exit(1)

# 2. Verificar variables
print("\n--- Variables cargadas ---")
numero1  = os.getenv("WHATSAPP_NUMBER_1", "")
apikey1  = os.getenv("CALLMEBOT_APIKEY_1", "")
numero2  = os.getenv("WHATSAPP_NUMBER_2", "")
apikey2  = os.getenv("CALLMEBOT_APIKEY_2", "")

print(f"WHATSAPP_NUMBER_1  = '{numero1}'  {'✅' if numero1 else '❌ VACÍO'}")
print(f"CALLMEBOT_APIKEY_1 = '{apikey1}'  {'✅' if apikey1 else '❌ VACÍO'}")
print(f"WHATSAPP_NUMBER_2  = '{numero2}'  {'✅' if numero2 else '⚠️  vacío (opcional)'}")
print(f"CALLMEBOT_APIKEY_2 = '{apikey2}'  {'✅' if apikey2 else '⚠️  vacío (opcional)'}")

# 3. Intentar envío real
print("\n--- Enviando mensaje de prueba ---")
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"
destinatarios = [(numero1, apikey1), (numero2, apikey2)]

for numero, apikey in destinatarios:
    if not numero or not apikey:
        print(f"⚠️  Saltando {numero or 'vacío'} — apikey no configurada")
        continue
    
    mensaje = "✅ Prueba PlacaControl: el sistema de alertas funciona correctamente"
    print(f"\nEnviando a {numero}...")
    try:
        resp = requests.get(
            CALLMEBOT_URL,
            params={"phone": numero, "text": mensaje, "apikey": apikey},
            timeout=15,
        )
        print(f"  Status HTTP: {resp.status_code}")
        print(f"  Respuesta:   {resp.text[:200]}")
        if resp.status_code == 200:
            print(f"  ✅ ENVIADO correctamente a {numero}")
        else:
            print(f"  ❌ Error — revisa el número y la apikey")
    except Exception as e:
        print(f"  ❌ Excepción: {e}")

print("\n" + "=" * 50)
print("Diagnóstico completado.")
