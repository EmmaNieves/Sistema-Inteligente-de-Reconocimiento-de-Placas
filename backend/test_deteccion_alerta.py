# ============================================================
# test_deteccion_alerta.py
# Simula una detección de placa NO autorizada y verifica
# que llegue la notificación WhatsApp, igual que en producción
# Correr con: python test_deteccion_alerta.py
# ============================================================
import os
import sys
from datetime import datetime

# Cargar .env igual que lo hace el backend real
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())
    print("✅ .env cargado")
else:
    print("❌ No se encontró backend/.env")
    sys.exit(1)

# Importar el módulo real de WhatsApp
from whatsapp_notifications import alerta_placa_no_registrada

# Datos falsos de una detección
PLACA_PRUEBA    = "XYZ999"   # placa inventada, no registrada
CAMARA_PRUEBA   = "Cámara Principal - Entrada"
FECHA_HORA      = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

print("\n" + "=" * 50)
print("SIMULANDO detección de placa NO autorizada")
print(f"  Placa    : {PLACA_PRUEBA}")
print(f"  Cámara   : {CAMARA_PRUEBA}")
print(f"  Fecha/Hora: {FECHA_HORA}")
print("=" * 50)

# Llamar exactamente la misma función que llama detections.py
alerta_placa_no_registrada(PLACA_PRUEBA, CAMARA_PRUEBA, FECHA_HORA)

print("\nSi ves ✅ arriba, el WhatsApp llegará igual cuando haya un escaneo real.")
