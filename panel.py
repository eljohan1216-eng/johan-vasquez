from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os, json

app = Flask(__name__, template_folder="templates")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_FILE = os.path.join(BASE_DIR, "signals.json")
STATE_FILE   = os.path.join(BASE_DIR, "estado_bot.json")
MODE_FILE    = os.path.join(BASE_DIR, "modo_actual.txt")  # "OTC" o "REAL"

def read_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)
    return True

@app.route("/")
def index():
    return render_template("panel.html")

@app.route("/api/signals", methods=["GET", "POST"])
def api_signals():
    if request.method == "GET":
        return jsonify(read_json(SIGNALS_FILE, []))
    try:
        payload = request.get_json(force=True) or []
        write_json(SIGNALS_FILE, payload)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/api/toggle-bot", methods=["POST"])
def toggle_bot():
    state = read_json(STATE_FILE, {"activo": False})
    state["activo"] = not state.get("activo", False)
    write_json(STATE_FILE, state)
    return jsonify({"ok": True, "activo": state["activo"]})

@app.route("/api/estado", methods=["GET"])
def estado():
    state = read_json(STATE_FILE, {"activo": False})
    modo = "OTC"
    try:
        if os.path.exists(MODE_FILE):
            with open(MODE_FILE, "r") as f:
                modo = (f.read().strip() or "OTC")
    except:
        pass
    return jsonify({"activo": state.get("activo", False), "modo": modo})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    app.run(host="0.0.0.0", port=port)
