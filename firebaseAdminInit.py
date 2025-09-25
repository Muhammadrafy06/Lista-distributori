# firebase_admin_init.py
import os, json, firebase_admin
from firebase_admin import credentials, firestore as admin_firestore

def _init_app_from_env():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not sa_json:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT is missing. "
            "Set it to the FULL JSON of your Firebase service account."
        )

    sa_info = json.loads(sa_json)
    # projectId is optional here; Admin SDK infers it from the SA JSON.
    cred = credentials.Certificate(sa_info)
    return firebase_admin.initialize_app(cred)

# Initialize once at import
firebase_app = _init_app_from_env()

# Firestore client using Admin app (this uses Admin credentials; no ADC)
db = admin_firestore.client(app=firebase_app)
# firebase_admin_init.py
import os, json, firebase_admin
from firebase_admin import credentials, firestore as admin_firestore

def _init_app_from_env():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    sa_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not sa_json:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT is missing. "
            "Set it to the FULL JSON of your Firebase service account."
        )

    sa_info = json.loads(sa_json)
    # projectId is optional here; Admin SDK infers it from the SA JSON.
    cred = credentials.Certificate(sa_info)
    return firebase_admin.initialize_app(cred)

# Initialize once at import
firebase_app = _init_app_from_env()

# Firestore client using Admin app (this uses Admin credentials; no ADC)
db = admin_firestore.client(app=firebase_app)
