import os
import sys

print("--- PYTHON PROCESS STARTUP ---")
print(f"Python version: {sys.version}")
print("Environment variables:")
for k, v in sorted(os.environ.items()):
    if "FIREBASE" in k or "FIRESTORE" in k or "GOOGLE" in k or "PUBSUB" in k:
        print(f"  {k}={v}")
print("------------------------------")

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
    import traceback
    import json

    # Collect ALL environment variables for diagnosis
    env_vars = {
        k: v
        for k, v in os.environ.items() if "FIRE" in k or "GOOGLE" in k or "PUBSUB" in k
    }
    print(f"[check_firestore] Environment variables: {env_vars}")

    try:
        from firebase_admin import firestore
        print("[check_firestore] Attempting to create Firestore client...")
        db = firestore.client()
        print("[check_firestore] Firestore client created successfully")

        doc_ref = db.collection("test").document("test_doc")
        print(f"[check_firestore] Writing to document: {doc_ref.path}")
        doc_ref.set({"status": "ok", "timestamp": firestore.SERVER_TIMESTAMP})
        print("[check_firestore] Document written successfully")

        return https_fn.Response(
            json.dumps({
                "status": "success",
                "message": "Firestore OK",
                "env": env_vars
            }), mimetype="application/json")
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[check_firestore] ERROR: {error_trace}")
        return https_fn.Response(
            json.dumps({
                "status": "error",
                "message": str(e),
                "type": type(e).__name__,
                "traceback": error_trace,
                "env": env_vars
            }), status=500, mimetype="application/json")


@https_fn.on_request()
def debug_env(req: https_fn.Request) -> https_fn.Response:
    """Dump environment variables."""
    import os
    import json
    return https_fn.Response(json.dumps(dict(os.environ)), mimetype="application/json")


@https_fn.on_call()
def get_account_info(req: https_fn.CallableRequest):
    """
    Test function that mimics StA2BLE-Cloud's getAccountInfo.
    Requires auth and reads from Firestore.
    """
    import traceback
    import json

    try:
        # Verify authentication (like StA2BLE-Cloud does)
        if not req.auth:
            raise https_fn.HttpsError(code=https_fn.FunctionsErrorCode.UNAUTHENTICATED,
                                      message="Authentication required")

        uid = req.auth.uid
        data = req.data
        account_id = data.get('accountId')

        if not account_id:
            raise https_fn.HttpsError(code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
                                      message="accountId is required")

        # Read from Firestore (like StA2BLE-Cloud does)
        from firebase_admin import firestore
        db = firestore.client()
        account_ref = db.collection('accounts').document(account_id)
        account_doc = account_ref.get()

        if not account_doc.exists:
            raise https_fn.HttpsError(code=https_fn.FunctionsErrorCode.NOT_FOUND,
                                      message=f"Account {account_id} not found")

        account_data = account_doc.to_dict()

        return {
            "accountId": account_id,
            "tickets": account_data.get('tickets', 0),
            "offlineQuota": account_data.get('offlineQuota', 0),
            "authUid": uid
        }

    except https_fn.HttpsError:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[get_account_info] ERROR: {error_trace}")
        raise https_fn.HttpsError(code=https_fn.FunctionsErrorCode.INTERNAL,
                                  message=f"Internal error: {str(e)}")
