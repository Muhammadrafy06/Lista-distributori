from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from flask import Flask, jsonify, request, render_template, abort
from functools import cmp_to_key

app = Flask(__name__)

@dataclass
class Distributore:
    id: int
    nome: str
    provincia: str
    lat: float
    lon: float
    livello_carburante: Dict[str, float] = field(default_factory=lambda: {"benzina": 0.0, "diesel": 0.0})  # in litri
    prezzo_benzina: float = 1.899  # €/L
    prezzo_diesel: float = 1.799   # €/L

    def set_prezzo(self, benzina: Optional[float] = None, diesel: Optional[float] = None):
        if benzina is not None:
            if benzina <= 0:
                raise ValueError("Il prezzo benzina deve essere > 0")
            self.prezzo_benzina = round(float(benzina), 3)
        if diesel is not None:
            if diesel <= 0:
                raise ValueError("Il prezzo diesel deve essere > 0")
            self.prezzo_diesel = round(float(diesel), 3)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["livello_carburante"] = {
            "benzina": float(self.livello_carburante.get("benzina", 0.0)),
            "diesel": float(self.livello_carburante.get("diesel", 0.0)),
        }
        return d

DISTRIBUTORI: List[Distributore] = [
    Distributore(1, "Iperstaroil Milano Nord", "MI", 45.515, 9.205, {"benzina": 12000, "diesel": 15000}, 1.949, 1.829),
    Distributore(2, "Iperstaroil Milano Sud", "MI", 45.405, 9.165, {"benzina": 8000, "diesel": 7000}, 1.939, 1.819),
    Distributore(3, "Iperstaroil Torino Centro", "TO", 45.071, 7.686, {"benzina": 6000, "diesel": 5000}, 1.929, 1.809),
    Distributore(4, "Iperstaroil Roma Est", "RM", 41.909, 12.62, {"benzina": 14000, "diesel": 11000}, 1.919, 1.799),
    Distributore(5, "Iperstaroil Napoli Ovest", "NA", 40.851, 14.268, {"benzina": 3000, "diesel": 2500}, 1.959, 1.839),
    Distributore(6, "Iperstaroil Bologna Fiera", "BO", 44.512, 11.36, {"benzina": 9000, "diesel": 10500}, 1.925, 1.805),
]

def sort_by_id(dis1: Distributore, dis2: Distributore) -> int:
    return (dis1.id > dis2.id) - (dis1.id < dis2.id)

def find_by_id(did: int) -> Optional[Distributore]:
    return next((d for d in DISTRIBUTORI if d.id == did), None)

def same_prov(a: str, b: str) -> bool:
    return a.strip().lower() == b.strip().lower()

def get_by_provincia(provincia: str) -> List[Distributore]:
    return [d for d in DISTRIBUTORI if same_prov(d.provincia, provincia) or same_prov(full_province_name(d.provincia), provincia) or same_prov(d.provincia, full_province_name(provincia))]

PROV_FULL = {
    "MI": "Milano",
    "TO": "Torino",
    "RM": "Roma",
    "NA": "Napoli",
    "BO": "Bologna",
}
def full_province_name(code_or_name: str) -> str:
    code = code_or_name.strip().upper()
    if code in PROV_FULL:
        return PROV_FULL[code]
    for k, v in PROV_FULL.items():
        if v.strip().upper() == code:
            return v
    return code_or_name

@app.get("/api/distributori")
def api_distributori():
    ordered = sorted(DISTRIBUTORI, key=cmp_to_key(sort_by_id))
    return jsonify([d.to_dict() for d in ordered])

@app.get("/api/distributori/provincia/<provincia>")
def api_livelli_provincia(provincia: str):
    matches = get_by_provincia(provincia)
    if not matches:
        return jsonify({"provincia": provincia, "distributori": [], "totali_litri": {"benzina": 0.0, "diesel": 0.0}})
    tot_b = sum(d.livello_carburante["benzina"] for d in matches)
    tot_d = sum(d.livello_carburante["diesel"] for d in matches)
    return jsonify({
        "provincia": provincia,
        "distributori": [
            {
                "id": d.id,
                "nome": d.nome,
                "provincia": d.provincia,
                "livello_carburante": d.livello_carburante,
                "prezzi": {"benzina": d.prezzo_benzina, "diesel": d.prezzo_diesel},
            } for d in matches
        ],
        "totali_litri": {"benzina": tot_b, "diesel": tot_d},
    })

@app.get("/api/distributori/<int:did>")
def api_distributore_singolo(did: int):
    d = find_by_id(did)
    if not d:
        abort(404, description="Distributore non trovato")
    return jsonify(d.to_dict())

@app.get("/api/distributori/geo")
def api_distributori_geo():
    features = []
    for d in DISTRIBUTORI:
        features.append({
            "type": "Feature",
            "properties": {
                "id": d.id,
                "nome": d.nome,
                "provincia": d.provincia,
                "prezzi": {"benzina": d.prezzo_benzina, "diesel": d.prezzo_diesel},
                "livello_carburante": d.livello_carburante,
            },
            "geometry": {"type": "Point", "coordinates": [d.lon, d.lat]},
        })
    return jsonify({"type": "FeatureCollection", "features": features})

@app.post("/api/prezzi/provincia/<provincia>")
def api_cambia_prezzi_provincia(provincia: str):
    payload = request.get_json(silent=True) or {}
    benz = payload.get("benzina", None)
    dies = payload.get("diesel", None)

    if benz is None and dies is None:
        abort(400, description="Specificare almeno uno tra 'benzina' o 'diesel'")

    matches = get_by_provincia(provincia)
    if not matches:
        abort(404, description="Nessun distributore trovato per la provincia indicata")

    updated = []
    try:
        for d in matches:
            d.set_prezzo(benzina=benz, diesel=dies)
            updated.append({"id": d.id, "prezzo_benzina": d.prezzo_benzina, "prezzo_diesel": d.prezzo_diesel})
    except ValueError as e:
        abort(400, description=str(e))

    return jsonify({"provincia": provincia, "aggiornati": len(updated), "dettaglio": updated})

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/distributore/<int:did>")
def dettaglio(did: int):
    d = find_by_id(did)
    if not d:
        abort(404)
    return render_template("dettaglio.html", d=d)

@app.get("/mappa")
def mappa():
    return render_template("mappa.html")

if __name__ == "__main__":
    app.run(debug=True)
