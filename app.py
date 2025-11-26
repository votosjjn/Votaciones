import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
import csv

# Excel reader
import openpyxl

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "cambiame_ya_123")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ADMIN password
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345")

# Files
CAND_PRIM = os.path.join(DATA_DIR, "candidatos_primaria.json")
CAND_SEC = os.path.join(DATA_DIR, "candidatos_secundaria.json")
VOTES_PRIM = os.path.join(DATA_DIR, "votos_primaria.json")
VOTES_SEC = os.path.join(DATA_DIR, "votos_secundaria.json")
VOTERS_PRIM = os.path.join(DATA_DIR, "votantes_primaria.json")
VOTERS_SEC = os.path.join(DATA_DIR, "votantes_secundaria.json")
ESTUD_PRIM = os.path.join(DATA_DIR, "estudiantes_primaria.json")
ESTUD_SEC = os.path.join(DATA_DIR, "estudiantes_secundaria.json")

ALLOWED_EXTENSIONS = {"xlsx", "xls", "csv"}


# ---------- helpers ----------
def _load(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return default


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensure_defaults():
    # candidatos defaults
    if not os.path.exists(CAND_PRIM):
        _save(CAND_PRIM, [
            {"id": "p1", "nombre": "Candidato A", "img": "/static/img/default.png"},
            {"id": "p2", "nombre": "Candidato B", "img": "/static/img/default.png"},
            {"id": "p3", "nombre": "Candidato C", "img": "/static/img/default.png"}
        ])
    if not os.path.exists(CAND_SEC):
        _save(CAND_SEC, [
            {"id": "s1", "nombre": "Candidato X", "img": "/static/img/default.png"},
            {"id": "s2", "nombre": "Candidato Y", "img": "/static/img/default.png"},
            {"id": "s3", "nombre": "Candidato Z", "img": "/static/img/default.png"}
        ])
    # votos, votantes y estudiantes
    if not os.path.exists(VOTES_PRIM): _save(VOTES_PRIM, {})
    if not os.path.exists(VOTES_SEC): _save(VOTES_SEC, {})
    if not os.path.exists(VOTERS_PRIM): _save(VOTERS_PRIM, {})
    if not os.path.exists(VOTERS_SEC): _save(VOTERS_SEC, {})
    if not os.path.exists(ESTUD_PRIM): _save(ESTUD_PRIM, {})  # estructura {doc: {nombre,curso,presente:bool}}
    if not os.path.exists(ESTUD_SEC): _save(ESTUD_SEC, {})


ensure_defaults()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Public views ----------
@app.route("/")
def menu():
    return render_template("menu.html")


@app.route("/primaria")
def primaria_index():
    candidatos = _load(CAND_PRIM, [])
    return render_template("primaria/index.html", candidatos=candidatos)


@app.route("/secundaria")
def secundaria_index():
    candidatos = _load(CAND_SEC, [])
    return render_template("secundaria/index.html", candidatos=candidatos)


# ---------- Vote endpoints (script.js uses these) ----------
def vote_logic(level, doc, candidato):
    doc = str(doc).strip()
    if not doc or not candidato:
        return {"ok": False, "msg": "Faltan datos"}, 400

    if level == "primaria":
        estudiantes_file = ESTUD_PRIM
        votes_file = VOTES_PRIM
        voters_file = VOTERS_PRIM
        candidates_file = CAND_PRIM
    else:
        estudiantes_file = ESTUD_SEC
        votes_file = VOTES_SEC
        voters_file = VOTERS_SEC
        candidates_file = CAND_SEC

    # verify student exists and is present
    estudiantes = _load(estudiantes_file, {})
    if doc not in estudiantes:
        return {"ok": False, "msg": "Documento no registrado o no habilitado"}, 403
    if not estudiantes[doc].get("presente", False):
        return {"ok": False, "msg": "Estudiante no marcado como presente"}, 403

    # verify candidate exists
    candidatos = _load(candidates_file, [])
    ids = [c["id"] for c in candidatos]
    if candidato not in ids:
        return {"ok": False, "msg": "Candidato inválido"}, 400

    # check double vote
    votantes = _load(voters_file, {})
    if doc in votantes:
        return {"ok": False, "msg": "Documento ya votó"}, 403

    votos = _load(votes_file, {})
    votos[candidato] = votos.get(candidato, 0) + 1
    _save(votes_file, votos)

    votantes[doc] = True
    _save(voters_file, votantes)

    return {"ok": True}, 200


@app.route("/primaria/vote", methods=["POST"])
def primaria_vote():
    data = request.get_json() or {}
    return vote_logic("primaria", data.get("doc"), data.get("candidato"))


@app.route("/secundaria/vote", methods=["POST"])
def secundaria_vote():
    data = request.get_json() or {}
    return vote_logic("secundaria", data.get("doc"), data.get("candidato"))


# ---------- Results (admin only) ----------
def load_counts(level):
    if level == "primaria":
        candidatos = _load(CAND_PRIM, [])
        conteo = _load(VOTES_PRIM, {})
    else:
        candidatos = _load(CAND_SEC, [])
        conteo = _load(VOTES_SEC, {})
    conteo = {k: int(v) for k, v in conteo.items()}
    return candidatos, conteo


def admin_required(fn):
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin"))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/primaria/results")
@admin_required
def primaria_results():
    candidatos, conteo = load_counts("primaria")
    return render_template("primaria/results.html", candidatos=candidatos, conteo=conteo)


@app.route("/secundaria/results")
@admin_required
def secundaria_results():
    candidatos, conteo = load_counts("secundaria")
    return render_template("secundaria/results.html", candidatos=candidatos, conteo=conteo)


# ---------- ADMIN: upload students Excel / CSV & manage attendance ----------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # login
    if request.method == "POST" and "password" in request.form:
        pwd = request.form.get("password", "")
        if pwd == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("admin.html", error="Contraseña incorrecta")
    # else GET: admin dashboard
    if not session.get("admin"):
        return render_template("admin.html")
    # load data for display
    estud_prim = _load(ESTUD_PRIM, {})
    estud_sec = _load(ESTUD_SEC, {})
    total_prim = len(estud_prim)
    total_sec = len(estud_sec)
    return render_template("admin.html", estudiantes_prim=estud_prim, estudiantes_sec=estud_sec,
                           total_prim=total_prim, total_sec=total_sec)


@app.route("/admin/upload_students", methods=["POST"])
@admin_required
def admin_upload_students():
    """
    Accepts file upload .xlsx, .xls or .csv
    Expected columns: Documento, Nombre, Curso, Nivel (primaria|secundaria optional)
    """
    f = request.files.get("file")
    if not f or not allowed_file(f.filename):
        return "Archivo no válido", 400
    filename = secure_filename(f.filename)
    ext = filename.rsplit(".", 1)[1].lower()

    rows = []
    try:
        if ext in ("xlsx", "xls"):
            wb = openpyxl.load_workbook(f, data_only=True)
            ws = wb.active
            # read header row to find columns
            headers = [str(cell.value).strip() if cell.value is not None else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            # normalize header names
            headers = [h.lower() for h in headers]
            col_map = {i: h for i, h in enumerate(headers)}
            for row in ws.iter_rows(min_row=2, values_only=True):
                rowd = {}
                for i, val in enumerate(row):
                    key = col_map.get(i, "")
                    rowd[key] = "" if val is None else str(val).strip()
                rows.append(rowd)
        else:
            # csv
            stream = f.stream.read().decode("utf-8")
            reader = csv.DictReader(stream.splitlines())
            for r in reader:
                rows.append({k.lower(): str(v).strip() for k, v in r.items()})
    except Exception as e:
        return f"Error leyendo archivo: {e}", 400

    # process rows into students dict
    prim = _load(ESTUD_PRIM, {})
    sec = _load(ESTUD_SEC, {})
    count = 0
    for r in rows:
        # possible header keys: documento, documento:, id, dni, nombre, curso, nivel
        doc = r.get("documento") or r.get("doc") or r.get("dni") or r.get("id")
        nombre = r.get("nombre") or r.get("name") or ""
        curso = r.get("curso") or r.get("grade") or ""
        nivel = (r.get("nivel") or "").lower()
        if not doc:
            continue
        # default level inference: if curso contains numbers/letters we can't always know; allow admin to fix later
        if nivel.startswith("p") or nivel == "primaria":
            target = prim
        elif nivel.startswith("s") or nivel == "secundaria":
            target = sec
        else:
            # heuristic: if curso contains 'B','A' but not reliable; fallback: put in primaria if course <=6 (try int)
            try:
                num = int(''.join([c for c in curso if c.isdigit()]) or 0)
                target = prim if num > 0 and num <= 6 else sec
            except:
                target = prim
        target[doc] = {"nombre": nombre or f"Estudiante {doc}", "curso": curso or "", "presente": False}
        count += 1

    _save(ESTUD_PRIM, prim)
    _save(ESTUD_SEC, sec)

    return redirect(url_for("admin"))


@app.route("/admin/toggle_present", methods=["POST"])
@admin_required
def admin_toggle_present():
    data = request.get_json() or {}
    level = data.get("level")
    doc = str(data.get("doc", "")).strip()
    if not doc:
        return jsonify({"ok": False}), 400
    if level == "primaria":
        d = _load(ESTUD_PRIM, {})
    else:
        d = _load(ESTUD_SEC, {})
    if doc not in d:
        return jsonify({"ok": False, "msg": "Documento no encontrado"}), 404
    d[doc]["presente"] = not bool(d[doc].get("presente", False))
    if level == "primaria":
        _save(ESTUD_PRIM, d)
    else:
        _save(ESTUD_SEC, d)
    return jsonify({"ok": True, "presente": d[doc]["presente"]})


@app.route("/admin/export_students/<level>")
@admin_required
def admin_export_students(level):
    if level == "primaria":
        d = _load(ESTUD_PRIM, {})
    else:
        d = _load(ESTUD_SEC, {})
    si = BytesIO()
    writer = csv.writer(si, lineterminator="\n")
    writer.writerow(["Documento", "Nombre", "Curso", "Presente"])
    for doc, info in d.items():
        writer.writerow([doc, info.get("nombre", ""), info.get("curso", ""), info.get("presente", False)])
    si.seek(0)
    return send_file(si, as_attachment=True, download_name=f"{level}_estudiantes.csv", mimetype="text/csv")


# ---------- Reset votes (admin) ----------
@app.route("/admin/reset/<level>", methods=["POST"])
@admin_required
def admin_reset(level):
    if level == "primaria":
        _save(VOTES_PRIM, {})
        _save(VOTERS_PRIM, {})
    else:
        _save(VOTES_SEC, {})
        _save(VOTERS_SEC, {})
    return redirect(url_for("admin"))


# ---------- Export results CSV ----------
@app.route("/data/export/<level>")
@admin_required
def export_csv(level):
    candidatos, conteo = ( _load(CAND_PRIM, []), _load(VOTES_PRIM, {}) ) if level=="primaria" else ( _load(CAND_SEC, []), _load(VOTES_SEC, {}) )
    si = BytesIO()
    writer = csv.writer(si, lineterminator="\n")
    writer.writerow(["id", "nombre", "votos"])
    for c in candidatos:
        writer.writerow([c["id"], c["nombre"], conteo.get(c["id"], 0)])
    si.seek(0)
    return send_file(si, as_attachment=True, download_name=f"{level}_resultados.csv", mimetype="text/csv")


# ---------- static proxy (optional) ----------
@app.route("/static/<path:filename>")
def static_proxy(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
