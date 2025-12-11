"""
Simple connection test for custom ports
Tests BOTH Admin SDK and Client REST API
"""
import os
import time
import requests
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.auth import credentials as google_credentials


# Mock credentials
class MockGoogleCredential(google_credentials.Credentials):
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
    def __init__(self):
        self._g_credential = MockGoogleCredential()

    def get_credential(self):
        return self._g_credential


# Set environment variables
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:17641'
os.environ['FIRESTORE_EMULATOR_HOST'] = '127.0.0.1:17644'
os.environ['GCLOUD_PROJECT'] = 'demo-sta2ble-ports'

print("Initializing Firebase...")
firebase_admin.initialize_app(MockFirebaseCredential(), {'projectId': 'demo-sta2ble-ports'})
print("[OK] Initialized")

print("\n=== Testing Admin SDK (server-side) ===")
print("\nTesting Auth emulator (17641) - Admin SDK...")
try:
    user = auth.create_user(email='quick-test@example.com', password='test123456')
    print(f"[OK] Created user via Admin SDK: {user.uid}")
    user_password = 'test123456'  # Save for client test
    user_email = user.email
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    raise

print("\nTesting Firestore emulator (17644)...")
try:
    db = firestore.client()
    doc_ref = db.collection('test').document('doc1')
    doc_ref.set({'test': 'data'})
    print(f"[OK] Created document")
    doc = doc_ref.get()
    print(f"[OK] Retrieved: {doc.to_dict()}")
    doc_ref.delete()
    print("[OK] Deleted document")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    raise

print("\n=== Testing Client REST API (same as .NET uses) ===")
print("\nTesting signInWithPassword endpoint...")
try:
    # This is the SAME endpoint that .NET FirebaseAuthService uses
    url = "http://127.0.0.1:17641/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=fake-api-key"
    payload = {
        "email": user_email,
        "password": user_password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload, timeout=5)
    
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Client sign-in successful!")
        print(f"     User ID: {result.get('localId')}")
        print(f"     Email: {result.get('email')}")
        print(f"     Token received: {len(result.get('idToken', ''))} chars")
    else:
        print(f"[FAIL] Status {response.status_code}: {response.text}")
        raise Exception(f"Client auth failed with {response.status_code}")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    raise

print("\n=== Cleanup ===")
try:
    auth.delete_user(user.uid)
    print("[OK] Deleted test user")
except Exception as e:
    print(f"[WARN] Cleanup failed: {e}")
