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
    env_vars = {k: v for k, v in os.environ.items() if "FIRE" in k or "GOOGLE" in k}
    print(f"Environment: {env_vars}")
    
    try:
        from firebase_admin import firestore
        db = firestore.client()
        doc_ref = db.collection("test").document("test_doc")
        doc_ref.set({"status": "ok"})
        return https_fn.Response(f"Firestore OK. Env: {env_vars}")
    except Exception as e:
        return https_fn.Response(f"Firestore Error: {str(e)}. Env: {env_vars}", status=500)

@https_fn.on_request()
def debug_env(req: https_fn.Request) -> https_fn.Response:
    """Dump environment variables."""
    import os
    import json
    return https_fn.Response(json.dumps(dict(os.environ)), mimetype="application/json")
