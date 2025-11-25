from flask import Flask, render_template, request, jsonify, send_from_directory
import json, os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

ALLOWED_FILE = os.path.join(BASE_DIR, 'allowed.json')
VOTOS_PRIM = os.path.join(BASE_DIR, 'votos_primaria.json')
VOTOS_SEC = os.path.join(BASE_DIR, 'votos_secundaria.json')

ALLOWED = load_json(ALLOWED_FILE)

CAND = [
    {"id":"1","nombre":"Miguel Amaya","img":"/static/img/candidato1.png"},
    {"id":"2","nombre":"Sofía Castañeda","img":"/static/img/candidato2.png"},
    {"id":"3","nombre":"Johan Moreno","img":"/static/img/candidato3.png"}
]

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/primaria')
def primaria_index():
    return render_template('primaria/index.html', candidatos=CAND)

@app.route('/secundaria')
def secundaria_index():
    return render_template('secundaria/index.html', candidatos=CAND)

@app.route('/<nivel>/vote', methods=['POST'])
def votar(nivel):
    data = request.get_json() or {}
    documento = str(data.get('doc','')).strip()
    candidato = str(data.get('candidato','')).strip()
    if not documento:
        return jsonify({'ok':False,'msg':'Documento requerido.'}),400
    allowed = load_json(ALLOWED_FILE)
    if documento not in allowed:
        return jsonify({'ok':False,'msg':'Documento no autorizado.'}),403
    ruta = VOTOS_PRIM if nivel=='primaria' else VOTOS_SEC if nivel=='secundaria' else None
    if not ruta:
        return jsonify({'ok':False,'msg':'Nivel inválido.'}),400
    votos = load_json(ruta)
    # Un documento solo puede votar una vez: si ya existe, rechaza
    if documento in votos:
        return jsonify({'ok':False,'msg':'Ya votaste.'}),400
    votos[documento]=candidato
    save_json(ruta,votos)
    return jsonify({'ok':True})

@app.route('/<nivel>/results')
def resultados(nivel):
    if nivel=='primaria':
        votos=load_json(VOTOS_PRIM)
    elif nivel=='secundaria':
        votos=load_json(VOTOS_SEC)
    else:
        return 'Nivel inválido',404
    conteo={ '1':0,'2':0,'3':0 }
    for v in votos.values():
        if str(v) in conteo:
            conteo[str(v)]+=1
    return render_template(f"{nivel}/results.html", candidatos=CAND, conteo=conteo)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR,'static'), filename)

if __name__=='__main__':
    # puerto 5000 (tal como pediste)
    app.run(port=2025, debug=True)
