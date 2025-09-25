from typing import Dict, List, Optional, Tuple
from google.cloud import firestore

db = firestore.Client()
COLL = "distributori"

# Optional map (extend as needed)
PROV_FULL = {
    "MI": "Milano",
    "TO": "Torino",
    "RM": "Roma",
    "NA": "Napoli",
    "BO": "Bologna"
}
def _full_name(code_or_name: str) -> str:
    code = (code_or_name or "").strip().upper()
    if code in PROV_FULL:
        return PROV_FULL[code]
    for k, v in PROV_FULL.items():
        if v.strip().upper() == code:
            return v
    return code_or_name

def _same_prov(a: str, b: str) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()

def _normalize(doc: firestore.DocumentSnapshot) -> Dict:
    d = doc.to_dict() or {}
    # enforce types for safety
    d["id"] = int(d["id"])
    d["lat"] = float(d["lat"])
    d["lon"] = float(d["lon"])
    d["prezzo_benzina"] = float(d.get("prezzo_benzina", 1.899))
    d["prezzo_diesel"] = float(d.get("prezzo_diesel", 1.799))
    lc = d.get("livello_carburante", {})
    d["livello_carburante"] = {
        "benzina": float(lc.get("benzina", 0.0)),
        "diesel": float(lc.get("diesel", 0.0)),
    }
    return d

def list_all_ordered() -> List[Dict]:
    qs = db.collection(COLL).order_by("id").stream()
    return [_normalize(doc) for doc in qs]

def get_by_id(did: int) -> Optional[Dict]:
    doc = db.collection(COLL).document(str(did)).get()
    return _normalize(doc) if doc.exists else None

def get_by_provincia(provincia: str) -> List[Dict]:
    """
    Matches both province code (e.g., 'MI') and full name ('Milano').
    We do two equality queries and merge (cheap for small datasets).
    """
    code = provincia.strip().upper()
    name = _full_name(provincia)

    docs = []
    for value in {code, name}:
        if not value:
            continue
        docs.extend(db.collection(COLL).where("provincia", "==", value).stream())

    # de-duplicate by document id
    seen, out = set(), []
    for doc in docs:
        if doc.id in seen: 
            continue
        seen.add(doc.id)
        out.append(_normalize(doc))
    return out

def geo_all() -> List[Dict]:
    return list_all_ordered()

def update_prices_by_province(provincia: str, benzina=None, diesel=None) -> Tuple[int, List[Dict]]:
    if benzina is None and diesel is None:
        raise ValueError("Specificare almeno uno tra 'benzina' o 'diesel'")
    if benzina is not None and float(benzina) <= 0:
        raise ValueError("Il prezzo benzina deve essere > 0")
    if diesel is not None and float(diesel) <= 0:
        raise ValueError("Il prezzo diesel deve essere > 0")

    items = get_by_provincia(provincia)
    if not items:
        return 0, []

    batch = db.batch()
    updated = []
    for d in items:
        data = {}
        if benzina is not None:
            data["prezzo_benzina"] = float(benzina)
        if diesel is not None:
            data["prezzo_diesel"] = float(diesel)
        ref = db.collection(COLL).document(str(d["id"]))
        batch.update(ref, data)
        updated.append({"id": d["id"], **data})
    batch.commit()
    return len(updated), updated