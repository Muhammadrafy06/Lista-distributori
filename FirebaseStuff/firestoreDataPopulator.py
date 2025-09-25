# seed.py
import os
import json
from google.cloud import firestore
from google.oauth2 import service_account

sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
if not sa_json:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT env var is missing")

sa_info = json.loads(sa_json)
project_id = os.getenv("FIREBASE_PROJECT_ID", sa_info.get("project_id"))

creds = service_account.Credentials.from_service_account_info(sa_info)
db = firestore.Client(project=project_id, credentials=creds)

data = [
    {
      "id": 1, "nome": "Iperstaroil Milano Nord", "provincia": "MI",
      "lat": 45.515, "lon": 9.205,
      "livello_carburante": {"benzina": 12000, "diesel": 15000},
      "prezzo_benzina": 1.949, "prezzo_diesel": 1.829,
    },
    {
      "id": 2, "nome": "Iperstaroil Milano Sud", "provincia": "MI",
      "lat": 45.405, "lon": 9.165,
      "livello_carburante": {"benzina": 8000, "diesel": 7000},
      "prezzo_benzina": 1.939, "prezzo_diesel": 1.819,
    },
    {
      "id": 3, "nome": "Iperstaroil Torino Centro", "provincia": "TO",
      "lat": 45.071, "lon": 7.686,
      "livello_carburante": {"benzina": 6000, "diesel": 5000},
      "prezzo_benzina": 1.929, "prezzo_diesel": 1.809,
    },
    {
      "id": 4, "nome": "Iperstaroil Roma Est", "provincia": "RM",
      "lat": 41.909, "lon": 12.62,
      "livello_carburante": {"benzina": 14000, "diesel": 11000},
      "prezzo_benzina": 1.919, "prezzo_diesel": 1.799,
    },
    {
      "id": 5, "nome": "Iperstaroil Napoli Ovest", "provincia": "NA",
      "lat": 40.851, "lon": 14.268,
      "livello_carburante": {"benzina": 3000, "diesel": 2500},
      "prezzo_benzina": 1.959, "prezzo_diesel": 1.839,
    },
    {
      "id": 6, "nome": "Iperstaroil Bologna Fiera", "provincia": "BO",
      "lat": 44.512, "lon": 11.36,
      "livello_carburante": {"benzina": 9000, "diesel": 10500},
      "prezzo_benzina": 1.925, "prezzo_diesel": 1.805,
    },
]

def main():
    coll = db.collection("distributori")
    for d in data:
        coll.document(str(d["id"])).set(d)
    print(f"thrown {len(data)} documents into 'distributori' in project '{project_id}'.")

if __name__ == "__main__":
    main()