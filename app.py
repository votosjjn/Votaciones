from flask import Flask, render_template, request, jsonify, send_from_directory
import json, os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")


# =========================
#   RUTA DEL MENÚ INICIAL
# =========================
@app.route("/")
def menu():
    return render_template("menu.html")


# =========================
#   RUTAS DE PRIMARIA
# =========================
@app.route("/primaria")
def primaria_index():
    return render_template("primaria/index.html")

@app.route("/primaria/results")
def primaria_results():
    return render_template("primaria/results.html")


# =========================
#   RUTAS DE SECUNDARIA
# =========================
@app.route("/secundaria")
def secundaria_index():
    return render_template("secundaria/index.html")

@app.route("/secundaria/results")
def secundaria_results():
    return render_template("secundaria/results.html")


# ======================================
#   GUARDAR DATOS (si usas JSON local)
# ======================================
@app.route("/save_vote", methods=["POST"])
def save_vote():
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    # Crear archivo si no existe
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"votes": []}, f, indent=4)

    # Guardar voto
    with open(DATA_FILE, "r") as f:
        db = json.load(f)

    db["votes"].append(data)

    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=4)

    return jsonify({"status": "ok"})


# =========================
#   INICIO LOCAL
# =========================
if __name__ == "__main__":
    app.run(debug=True)