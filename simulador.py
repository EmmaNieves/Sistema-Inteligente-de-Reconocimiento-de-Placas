import httpx
import random
import time
from datetime import datetime

URL = "http://localhost:8000/simulate/"

PLACAS = [
    "ABC123", "XYZ789", "DEF456", "GHI012", "JKL345",
    "MNO678", "PQR901", "STU234", "VWX567", "YZA890",
    "BCB111", "CDC222", "EDE333", "FEF444", "GFG555",
    "HIH666", "IJI777", "JKJ888", "KLK999", "LML000"
]

CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Santa Marta", "Riohacha"]

TIPOS = ["carro", "moto", "camioneta", "bus", "camión"]

CAMARAS = ["CAM-01", "CAM-02", "CAM-03", "CAM-04", "CAM-05"]

def simular():
    payload = {
        "plate_text": random.choice(PLACAS),
        "city": random.choice(CIUDADES),
        "vehicle_type": random.choice(TIPOS),
        "camera_code": random.choice(CAMARAS)
    }
    try:
        r = httpx.post(URL, json=payload, timeout=5)
        data = r.json()
        status = "AUTORIZADA" if data.get("authorized") else "NO AUTORIZADA"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {payload['plate_text']} | {payload['city']} | {status}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Simul ador iniciado. 100 vehículos/min")
    while True:
        simular()
        time.sleep(0.6)