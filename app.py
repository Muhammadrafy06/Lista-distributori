# app.py
from __future__ import annotations
from flask import Flask, jsonify, request, render_template, abort
from typing import Optional

# NEW: import Firestore data layer
from firestore_layer import (
    list_all_ordered, get_by_id, get_by_provincia, geo_all, update_prices_by_province
)

app = Flask(__name__)

# ------------------------------
# API
# ------------------------------

@app.get("/api/distributori")
def api_distributori():
    return jsonify(list_all_ordered())

@app.get("/api/distributori/provincia/<provincia>")
def api_livelli_provincia(provincia: str):
    items = get_by_provincia(provincia)
    tot_b = sum(d["livello_carburante"]["benzina"] for d in items)
    tot_d = sum(d["livello_carburante"]["diesel"] for d in items)
    return jsonify({
        "provincia": provincia,
        "distributori": [
            {
                "id": d["id"],
                "nome": d["nome"],
                "provincia": d["provincia"],
                "livello_carburante": d["livello_carburante"],
                "prezzi": {"benzina": d["prezzo_benzina"], "diesel": d["prezzo_diesel"]},
            } for d in items
        ],
        "totali_litri": {"benzina": tot_b, "diesel": tot_d},
    })

@app.get("/api/distributori/<int:did>")
def api_distributore_singolo(did: int):
    d = get_by_id(did)
    if not d:
        abort(404, description="Distributore non trovato")
    return jsonify(d)

@app.get("/api/distributori/geo")
def api_distributori_geo():
    features = []
    for d in geo_all():
        features.append({
            "type": "Feature",
            "properties": {
                "id": d["id"],
                "nome": d["nome"],
                "provincia": d["provincia"],
                "prezzi": {"benzina": d["prezzo_benzina"], "diesel": d["prezzo_diesel"]},
                "livello_carburante": d["livello_carburante"],
            },
            "geometry": {"type": "Point", "coordinates": [d["lon"], d["lat"]]},
        })
    return jsonify({"type": "FeatureCollection", "features": features})

@app.post("/api/prezzi/provincia/<provincia>")
def api_cambia_prezzi_provincia(provincia: str):
    payload = request.get_json(silent=True) or {}
    benz = payload.get("benzina", None)
    dies = payload.get("diesel", None)
    try:
        n, updated = update_prices_by_province(provincia, benzina=benz, diesel=dies)
    except ValueError as e:
        abort(400, description=str(e))
    if n == 0:
        abort(404, description="Nessun distributore trovato per la provincia indicata")
    return jsonify({"provincia": provincia, "aggiornati": n, "dettaglio": updated})

# ------------------------------
# Pagine Web (UI) — unchanged
# ------------------------------

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/distributore/<int:did>")
def dettaglio(did: int):
    d = get_by_id(did)
    if not d:
        abort(404)
    # dicts work fine with dot access in Jinja
    return render_template("dettaglio.html", d=d)

@app.get("/mappa")
def mappa():
    return render_template("mappa.html")

if __name__ == "__main__":
    app.run(debug=True)
