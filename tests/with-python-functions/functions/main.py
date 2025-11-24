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
