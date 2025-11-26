from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "6818357aadmin"

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

ADMIN_PASSWORD = "94jjn15v"

# Candidatos (puedes cambiarlos)
candidatos_primaria = ["Candidato A", "Candidato B", "Candidato C"]
candidatos_secundaria = ["Candidato X", "Candidato Y", "Candidato Z"]

# Contadores de votos
votos_primaria = {c: 0 for c in candidatos_primaria}
votos_secundaria = {c: 0 for c in candidatos_secundaria}


# ─────────────────────────────────────────────
# RUTA PRINCIPAL (LOGO ANIMADO)
# ─────────────────────────────────────────────

@app.route("/")
def menu():
    return render_template("menu.html")


# ─────────────────────────────────────────────
# PRIMARIA
# ─────────────────────────────────────────────

@app.route("/primaria")
def primaria_index():
    return render_template("primaria/index.html")

@app.route("/votar_primaria", methods=["GET", "POST"])
def votar_primaria():
    if request.method == "POST":
        candidato = request.form.get("candidato")
        if candidato in votos_primaria:
            votos_primaria[candidato] += 1
            return redirect(url_for("menu"))
    return render_template("primaria/votar.html", candidatos=candidatos_primaria)

@app.route("/results_primaria")
def results_primaria():
    if "admin" not in session:
        return redirect(url_for("admin"))
    return render_template("primaria/results.html", votos=votos_primaria)


# ─────────────────────────────────────────────
# SECUNDARIA
# ─────────────────────────────────────────────

@app.route("/secundaria")
def secundaria_index():
    return render_template("secundaria/index.html")

@app.route("/votar_secundaria", methods=["GET", "POST"])
def votar_secundaria():
    if request.method == "POST":
        candidato = request.form.get("candidato")
        if candidato in votos_secundaria:
            votos_secundaria[candidato] += 1
            return redirect(url_for("menu"))
    return render_template("secundaria/votar.html", candidatos=candidatos_secundaria)

@app.route("/results_secundaria")
def results_secundaria():
    if "admin" not in session:
        return redirect(url_for("admin"))
    return render_template("secundaria/results.html", votos=votos_secundaria)


# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("menu"))
        else:
            return render_template("admin.html", error="Contraseña incorrecta")

    return render_template("admin.html")


# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
