from firebase_functions import https_fn
from firebase_admin import initialize_app

initialize_app()


@https_fn.on_request()
def hello_world(req: https_fn.Request) -> https_fn.Response:
    """Simple HTTP function for testing Python Functions in emulator."""
    return https_fn.Response("Hello from Python Firebase Functions!")


@https_fn.on_request()
def echo(req: https_fn.Request) -> https_fn.Response:
    """Echo the request body back."""
    return https_fn.Response(f"Echo: {req.get_data(as_text=True)}")


@https_fn.on_request()
def check_firestore(req: https_fn.Request) -> https_fn.Response:
    """Check if Firestore is accessible."""
    import os
    print(f"FIRESTORE_EMULATOR_HOST: {os.environ.get('FIRESTORE_EMULATOR_HOST')}")
    try:
        from firebase_admin import firestore
        db = firestore.client()
        doc_ref = db.collection("test").document("test_doc")
        doc_ref.set({"status": "ok"})
        return https_fn.Response("Firestore OK")
    except Exception as e:
        return https_fn.Response(f"Firestore Error: {str(e)}", status=500)
