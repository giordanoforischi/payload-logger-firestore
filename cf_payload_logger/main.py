import functions_framework
from datetime import datetime

import firebase_admin
from firebase_admin import firestore

app = firebase_admin.initialize_app()

def persist(data):
    db = firestore.client()

    collection_id = f'requests-logger'
    document_id = datetime.now().isoformat()
    
    db.collection(collection_id).document(document_id).set(data)

    return f"Request persisted to Firestore in record {collection_id}/{document_id}"

@functions_framework.http
def main(req):
    try:
        # Headers, content-type e charset para decoding
        headers_json = dict(req.headers)
        content_type = req.headers.get("Content_Type", "(not set)")
        charset = next((part.split("=", 1)[1] for part in content_type.split(";") if "charset=" in part), "utf-8")

        # Dados do payload
        if content_type in ("application/json"):
            data = dict(req.json)
        elif content_type in ("application/xml", "text/html", "text/plain", "text/csv "):
            data = req.data.decode(charset)
        elif content_type == "application/x-www-form-urlencoded":
            data = dict(req.form)
        else:
            data = {}

        # Args
        request_args = dict(req.args)

        # Persists data
        request_data = dict({
            "headers": headers_json,
            "content_type": content_type,
            "payload": data,
            "query_params": request_args,
            "timestamp": datetime.now().isoformat()
        })

        return persist(request_data), 200

    except Exception as e:
        return f"{str(e)}", 501
