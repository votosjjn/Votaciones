from flask import Flask, render_template, request, jsonify, send_from_directory
import json, os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✔️ CAMBIA ESTA URL DESPUÉS DEL DEPLOY
BASE_URL = "https://TU-PAGINA.onrender.com"


# --------------------------
#  Funciones de JSON seguras
# --------------------------
def load_json(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    path = os.path.join(BASE_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# --------------------------
#  Rutas principales
# --------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/primaria")
def primaria():
    return render_template("primaria.html")


@app.route("/secundaria")
def secundaria():
    return render_template("secundaria.html")


# --------------------------
#  Guardar votos
# --------------------------
@app.route("/votar_primaria", methods=["POST"])
def votar_primaria():
    votos = load_json("votos_primaria.json")
    candidato = request.form.get("candidato")

    if candidato not in votos:
        votos[candidato] = 0

    votos[candidato] += 1
    save_json("votos_primaria.json", votos)

    return jsonify({"ok": True})


@app.route("/votar_secundaria", methods=["POST"])
def votar_secundaria():
    votos = load_json("votos_secundaria.json")
    candidato = request.form.get("candidato")

    if candidato not in votos:
        votos[candidato] = 0

    votos[candidato] += 1
    save_json("votos_secundaria.json", votos)

    return jsonify({"ok": True})


@app.route("/allowed")
def allowed():
    return send_from_directory(BASE_DIR, "allowed.json")


@app.route("/qr/<path:filename>")
def qr_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "qrs"), filename)


# --------------------------
#  Generar códigos QR desde la web
# --------------------------
@app.route("/generate_qr")
def generate_qr_route():
    import qrcode

    primaria_url = f"{BASE_URL}/primaria"
    secundaria_url = f"{BASE_URL}/secundaria"

    qr_dir = os.path.join(BASE_DIR, "qrs")
    os.makedirs(qr_dir, exist_ok=True)

    img1 = qrcode.make(primaria_url)
    img1.save(os.path.join(qr_dir, "primaria.png"))

    img2 = qrcode.make(secundaria_url)
    img2.save(os.path.join(qr_dir, "secundaria.png"))

    return jsonify({
        "primaria": "/qr/primaria.png",
        "secundaria": "/qr/secundaria.png"
    })


# --------------------------
#  Iniciar
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
