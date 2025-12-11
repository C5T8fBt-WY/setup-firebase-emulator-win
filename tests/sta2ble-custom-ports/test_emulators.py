"""
Test Firebase Emulators with StA2BLE-Cloud custom ports.
Tests: Auth (17641), Firestore (17644), Functions (17642)

This reproduces the StA2BLE-Cloud setup to debug connection issues.
"""
import os
import time
import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.auth import credentials as google_credentials
import requests


# Mock credentials for emulator testing
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


def initialize_firebase():
    """Initialize Firebase Admin SDK for emulator with StA2BLE custom ports."""
    # Set emulator environment variables with custom ports matching StA2BLE-Cloud
    os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:17641'
    os.environ['FIRESTORE_EMULATOR_HOST'] = '127.0.0.1:17644'
    os.environ['GCLOUD_PROJECT'] = 'demo-sta2ble-ports'

    firebase_admin.initialize_app(MockFirebaseCredential(), {'projectId': 'demo-sta2ble-ports'})

    print("[OK] Firebase Admin SDK initialized with StA2BLE custom ports")
    print("    Auth: 17641, Firestore: 17644, Functions: 17642")


def test_authentication():
    """Test Firebase Authentication emulator on custom port 17641."""
    print("\n=== Testing Authentication (Port 17641) ===")
    try:
        user = auth.create_user(email='test-sta2ble@example.com', password='testpass123')
        print(f"[OK] Created user: {user.uid}")

        fetched_user = auth.get_user_by_email('test-sta2ble@example.com')
        print(f"[OK] Retrieved user: {fetched_user.email}")

        auth.delete_user(user.uid)
        print("[OK] Deleted user")
        return True
    except Exception as e:
        print(f"[FAIL] Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_firestore():
    """Test Firestore emulator on custom port 17644."""
    print("\n=== Testing Firestore (Port 17644) ===")
    try:
        db = firestore.client()
        doc_ref = db.collection('accounts').document('test-account-001')
        doc_ref.set({'name': 'Test Account', 'port': 17644, 'balance': 100})
        print("[OK] Created document")

        doc = doc_ref.get()
        if doc.exists:
            print(f"[OK] Retrieved document: {doc.to_dict()}")

        doc_ref.delete()
        print("[OK] Deleted document")
        return True
    except Exception as e:
        print(f"[FAIL] Firestore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_functions_connection():
    """Test Functions emulator connectivity on custom port 17642."""
    print("\n=== Testing Functions (Port 17642) ===")
    try:
        # Test simple connection first
        response = requests.post(
            'http://127.0.0.1:17642/demo-sta2ble-ports/us-central1/testConnection',
            json={'data': {}},
            timeout=10
        )
        print(f"[OK] testConnection reachable, Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    Response: {response.json()}")

        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] Functions connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_functions_firestore_integration():
    """Test Functions calling Firestore on custom ports."""
    print("\n=== Testing Functions + Firestore Integration ===")
    try:
        # First create a document in Firestore
        db = firestore.client()
        doc_ref = db.collection('accounts').document('integration-test-001')
        doc_ref.set({'name': 'Integration Test', 'balance': 250})
        print("[OK] Created test document in Firestore")

        # Call function to retrieve it
        response = requests.post(
            'http://127.0.0.1:17642/demo-sta2ble-ports/us-central1/getAccountInfo',
            json={'data': {'accountId': 'integration-test-001'}},
            timeout=10
        )
        print(f"[OK] getAccountInfo called, Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"    Retrieved: {data}")
            if data.get('name') == 'Integration Test':
                print("[OK] Function successfully accessed Firestore data")
                doc_ref.delete()
                return True
            else:
                print(f"[FAIL] Unexpected data: {data}")
                doc_ref.delete()
                return False
        else:
            print(f"[FAIL] Function returned error: {response.text}")
            doc_ref.delete()
            return False

    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test runner."""
    print("=" * 60)
    print("Firebase Emulator Tests - StA2BLE Custom Ports")
    print("=" * 60)

    initialize_firebase()

    results = {
        'Authentication (17641)': test_authentication(),
        'Firestore (17644)': test_firestore(),
        'Functions Connection (17642)': test_functions_connection(),
        'Functions + Firestore Integration': test_functions_firestore_integration(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print("=" * 60)
    if all_passed:
        print("All tests passed with StA2BLE custom ports!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
