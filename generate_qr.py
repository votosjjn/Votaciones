import qrcode
import os

BASE_URL = "https://TU-PAGINA.onrender.com"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QR_DIR = os.path.join(BASE_DIR, "qrs")
os.makedirs(QR_DIR, exist_ok=True)

qr_data = {
    "primaria": f"{BASE_URL}/primaria",
    "secundaria": f"{BASE_URL}/secundaria"
}

for nombre, url in qr_data.items():
    img = qrcode.make(url)
    img.save(os.path.join(QR_DIR, f"{nombre}.png"))

print("QR generados correctamente.")
