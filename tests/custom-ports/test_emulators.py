"""
Test Firebase Emulators with custom ports.
Tests: Authentication (9199) and Firestore (8888)
"""
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore


def initialize_firebase():
    """Initialize Firebase Admin SDK for emulator with custom ports."""
    # Set emulator environment variables with custom ports
    os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:9199'
    os.environ['FIRESTORE_EMULATOR_HOST'] = '127.0.0.1:8888'
    os.environ['GCLOUD_PROJECT'] = 'demo-project'

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "demo-project",
        "private_key_id": "dummykeyid123",
        "private_key":
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAub1uzfk0FR/f21aV9o0E3Q60xXzKAiy1UPBII/qFWL1F+rX1\nf3HG92hMXxrDpDs5T4cYQ5/aWzXcIJWSG6EruovkOLjYDlJ/wVW606JsTTwjhsrB\nRt2r7bYlyWRPRW/QCEcmi60Zago1oVBwwObRhbW0eAGmZO3pDaeUgJRH3PNUlnst\nXzp/hSJPZQv92sNV5NqZR7Kj3nuabkR8rbvsal02w2A4NW7KiLGyQgAXMYgO7Rc1\n//fZ04lmoXSnhZBLyxA+9y9MjnypW9msVVAb+h3af6Hb449XEVlyC1lsFKUHdp4a\nQqY2MnxhZxAS3OyrJSQMEvyqJT22KLuzSAvkXwIDAQABAoIBAEv6hg+Cn7/+bGuE\nVU7oK7OjluXsIJRYJoln6RKyoYaF0lD2yuhpqeq9wvPqdlpBkbWK/S14f/FsrFG1\n7XEY8lLac66SSms9ax4yi/yThfroHV4/pWVwOyq/pmBmBJlSXkZsmINteSZr67lD\ntwPpx46LIDow7ph9y6Y2xWP9hBII0pPE2XKicFUOXDHtYYCgyKiVaC6n29QJRHY5\nY8D+w+Hjqojx5VvBvV/q3Sh710cs5Z4MhE2B+6dAw5HaZMtnBadJ4LoAH07uBN2w\nxHCcOoX0zvct8zlrR7gxj5p1YVleZfGnV6gKsrbqaPxVZqKf81SI4I7N9fkBXWVw\nCT+tK9kCgYEA7pAsWx+03BwpaiLAE3nHKDiZIqaMMT1SZqkuHe0wc1VqB3xy5Dkn\nZfRUV9MMiObfzDaKDish6I/Kqk0Q9SXpNa/rTAGswa7xgOLnpOsfYTFVCAUVtM4n\nOXjDNKhUluKUw9EGZgVrKe22yBPB/SxC1PsXUWLzLFKnGiogH7WypUkCgYEAx1De\na5R31dM9Ib2tJ+PXBkO5g3aJVHqZrrExaegd1vQw35BgHvnxcuDD/zr4Y9cobCqu\nzbv+2E42N5IVHDH2IlmU4A2A9sJ7cmLXrnNk6PZoTKzfY6fPdLHT2TSyIQEd36gV\nC0WT+2dVhBmXNn8EKbmJ+JV5zA9CwjjQyaMkRGcCgYAyhmZehkCPvYcn62Qyu7/q\nTNJh/FQEubAR/hK+U9XHF3f1Te4nV9N4TF7wmso01HDhl0t15LyxvIJ3vwqwYO8b\nZ761wkUMYDjVyzi0PPfQZdpUcH9AY8j66xCsvlnr+uD29/Ya9VrU7nuftE+Jhy5A\nXU169zH5WSf66qETFjBXwQKBgH+EfJilZznVKPJSUNsJiMNIRwMVrmzu9y3tzaht\nSdIBbtdJnkWTMWeG575+MvZlbEYv1KBpm3U2LLfG7VyZlliJqZbi7NRyvtoC5OyG\nhVQKedY8b7tpXG/Taa84aJJ3DW7PMY+Bl1ir1ulqGfVStA4h12TD9SWZyeNKyEGI\n76YXAoGBAOjs37VNQeRPJbGLiZz4jjR/bIdKE/XN6pIan7mYHpHq0HU3HHkZF5E/\nNQySCZ/5pVRDJVgYJTD4hPWCMwY60iz1RopGBQAP5/Cbl3DVBb9PKT6NVlXn/Cfb\n+XsHJwfGHMwxqU2WqHvaL4ROmEN5g1NwacSWGn7b3zyG5V4fU6Zf\n-----END RSA PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk@demo-project.iam.gserviceaccount.com",
        "client_id": "1234567890",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    })

    firebase_admin.initialize_app(cred, {'projectId': 'demo-project'})

    print("[OK] Firebase Admin SDK initialized with custom ports")
    print("    Auth: 9199, Firestore: 8888")


def test_authentication():
    """Test Firebase Authentication emulator on custom port."""
    print("\n=== Testing Authentication (Port 9199) ===")
    try:
        user = auth.create_user(email='test-custom@example.com', password='testpass123')
        print(f"[OK] Created user: {user.uid}")

        fetched_user = auth.get_user_by_email('test-custom@example.com')
        print(f"[OK] Retrieved user: {fetched_user.email}")

        auth.delete_user(user.uid)
        print("[OK] Deleted user")
        return True
    except Exception as e:
        print(f"[FAIL] Authentication test failed: {e}")
        return False


def test_firestore():
    """Test Firestore emulator on custom port."""
    print("\n=== Testing Firestore (Port 8888) ===")
    try:
        db = firestore.client()
        doc_ref = db.collection('custom-test').document('doc1')
        doc_ref.set({'name': 'Custom Port Test', 'port': 8888})
        print("[OK] Created document")

        doc = doc_ref.get()
        if doc.exists:
            print(f"[OK] Retrieved document: {doc.to_dict()}")

        doc_ref.delete()
        print("[OK] Deleted document")
        return True
    except Exception as e:
        print(f"[FAIL] Firestore test failed: {e}")
        return False


def main():
    """Main test runner."""
    print("=" * 50)
    print("Firebase Emulator Tests - Custom Ports")
    print("=" * 50)

    initialize_firebase()

    results = {
        'Authentication (9199)': test_authentication(),
        'Firestore (8888)': test_firestore(),
    }

    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    for test_name, passed in results.items():
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print("=" * 50)
    if all_passed:
        print("All tests passed with custom ports!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
