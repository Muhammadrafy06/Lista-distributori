import os, json, firebase_admin
from firebase_admin import credentials, auth
from google.cloud import firestore
from google.oauth2 import service_account

sa_info = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])

admin_cred = credentials.Certificate(sa_info)
firebase_admin.initialize_app(admin_cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID", sa_info.get("project_id"))
})

gcreds = service_account.Credentials.from_service_account_info(sa_info)
db = firestore.Client(
    project=os.getenv("FIREBASE_PROJECT_ID", sa_info.get("project_id")),
    credentials=gcreds
)