"""
Simple connection test for custom ports
"""
import os
import time
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

print("\nTesting Auth emulator (17641)...")
try:
    user = auth.create_user(email='quick-test@example.com', password='test123')
    print(f"[OK] Created user: {user.uid}")
    auth.delete_user(user.uid)
    print("[OK] Deleted user")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()

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

print("\n[SUCCESS] All tests passed!")
