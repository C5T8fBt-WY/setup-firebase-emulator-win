"""
Test Python functions for Firebase Emulator with StA2BLE-Cloud custom ports.
Tests Auth (17641), Firestore (17644), and Functions (17642) integration.
"""
import time
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_functions import https_fn
from google.auth import credentials as google_credentials


# Initialize Firebase Admin (must be done before defining functions)
class MockGoogleCredential(google_credentials.Credentials):
    """Mock Google authentication credential for emulator testing."""

    def __init__(self):
        super().__init__()
        self._token = 'mock-token'
        self.expiry = None

    @property
    def valid(self):
        return True

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    def refresh(self, request):
        self.token = f'mock-token-{int(time.time())}'

    @property
    def service_account_email(self):
        return 'mock-email@demo-sta2ble-ports.iam.gserviceaccount.com'


class MockFirebaseCredential(credentials.Base):
    """Mock Firebase credential for emulator testing."""

    def __init__(self):
        self._g_credential = MockGoogleCredential()

    def get_credential(self):
        return self._g_credential


# Initialize Firebase Admin SDK
firebase_admin.initialize_app(MockFirebaseCredential(), options={'projectId': 'demo-sta2ble-ports'})


@https_fn.on_request()
def getAccountInfo(req: https_fn.Request) -> https_fn.Response:
    """Get account information from Firestore - tests Firestore integration."""
    try:
        data = req.get_json()
        account_id = data.get('accountId') if data else None

        if not account_id:
            return https_fn.Response({'error': 'Missing accountId'}, status=400)

        # Access Firestore
        db = firestore.client()
        doc_ref = db.collection('accounts').document(account_id)
        doc = doc_ref.get()

        if doc.exists:
            return https_fn.Response(doc.to_dict(), status=200)
        else:
            return https_fn.Response({'error': 'Account not found'}, status=404)
    except Exception as e:
        return https_fn.Response({'error': str(e)}, status=500)


@https_fn.on_request()
def testConnection(req: https_fn.Request) -> https_fn.Response:
    """Simple connection test function."""
    return https_fn.Response({
        'message': 'Connection successful',
        'port': 17642,
        'emulator': 'functions'
    }, status=200)
