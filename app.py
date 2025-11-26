from flask import Flask, render_template, request, redirect, url_for, session
from openpyxl import Workbook, load_workbook
import os

app = Flask(__name__)
app.secret_key = "superclave123"

# Archivo Excel
EXCEL_FILE = "votos.xlsx"

# Crear Excel si no existe
if not os.path.exists(EXCEL_FILE):
    wb = Workbook()
    ws = wb.active
    ws.append(["Documento", "Nombre", "Curso", "Candidato"])
    wb.save(EXCEL_FILE)


# ------------------------------- #
# ----------- RUTAS ------------- #
# ------------------------------- #

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/votar/<nivel>", methods=["GET", "POST"])
def votar(nivel):
    candidatos = []

    if nivel == "primaria":
        candidatos = [
            {"id": 1, "nombre": "María Fernández"},
            {"id": 2, "nombre": "Juan Torres"},
            {"id": 3, "nombre": "Sara Delgado"}
        ]

    if nivel == "secundaria":
        candidatos = [
            {"id": 1, "nombre": "Camilo Vargas"},
            {"id": 2, "nombre": "Daniela Ospina"},
            {"id": 3, "nombre": "Pedro Hernández"}
        ]

    if request.method == "POST":
        documento = request.form["documento"]
        nombre = request.form["nombre"]
        curso = request.form["curso"]
        candidato = request.form["candidato"]

        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        ws.append([documento, nombre, curso, candidato])
        wb.save(EXCEL_FILE)

        return redirect(url_for("index"))

    return render_template("votar.html", candidatos=candidatos, nivel=nivel)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        return render_template("admin_login.html", error="Contraseña incorrecta")

    return render_template("admin_login.html")


@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin"))

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    votos = []
    for row in ws.iter_rows(values_only=True):
        if row[0] != "Documento":
            votos.append(row)

    return render_template("admin_panel.html", votos=votos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

