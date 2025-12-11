"""
Test multiple Python Cloud Functions with Firebase emulators.
This replicates the StA2BLE-Cloud scenario where getAccountInfo function fails.
"""
import os
import time
import pytest
import requests
from firebase_admin import credentials, initialize_app, auth, firestore

# Set emulator environment variables
os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:18080'
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = 'localhost:19099'

# Initialize Firebase Admin with mock credentials for emulator
@pytest.fixture(scope='module', autouse=True)
def setup_firebase():
    """Initialize Firebase Admin SDK."""
    from firebase_admin import _apps
    if not len(_apps):
        # Use mock credentials for emulator
        mock_cred = {
            "type": "service_account",
            "project_id": "demo-test",
            "private_key_id": "mock-key-id",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1vQnD2SCZakqPIdIq4NLdNy9a/OoUpPjwIFA+KRtypHA/Tnd\nSS+cqqbciKh6s0JnmokZt06K9pGk+yQ4nLjRqOUQ7a2OFuzgN7LYw4n3C8rIvACU\nv5/wHd8h82Qt1K7jPelgO+Mwf4aZ6GLUMTXuqYlDvfSRokz6xmYm8t6YYL8/8OzH\nMcJFRHPmHXbLhvVb/bvwX7fvI2UN9kzGL+CgDqNjopVxK97gJVH5x3KUzokr3OmE\n6VzyJ05fOHjPF5vxTJsb/nYG4RqnJ8y+FGZjeauwqInwAg7BJ113KdKEPtMX69KB\n2z7kwHfPUYsjQFQDyBOf5uX1zEbVxrg8qYHBSQIDAQABAoIBAFxouTQaWx62U4ST\nClBF0RYr4bk7lmTt1E9JofNiyRp5f7S9gB76+4i31H5ho+JVzXF3uFkASKiI45re\nLwJdSDEqTRVI9Blx+1CmsB6cPNtSceq0+z3IVfOZniBjNHrHNsVCg88rNAnXBWqM\ntjlzvKcg7kEHF+bk3jiV6O+nd227cLmeBqXvuW+Uz2ybw0jeOwgecD4XFSeiS8w4\n8hHsGxIFvxbeQ8UoYAjnFn/m+7Ia3tRESoLIiW8Glz9M4zoX4F5FJ9YEtKDX6kFO\nErE+zBx9PwdZ8i0jNRYVrUogW4dkSaHXBPzM/k53BtZHIJBhzuj9GJhEB3jjRhNR\nWYBZaXsCgYEA8+fhOVFRVnh9RZcGcykUqaAumbjz2WODtPsIj5Z4b6iErttjrwFk\n/W2OfaEf4gT+cvJdPG+l0KiBP7kmBZnx1kvC6sWflKWIpxa/VLmXAxn2xrELaI5Z\ngOZQVYRnrI+poZ3qREqC7MI+rwQVlL4puRv34b3tMYRc4NCGjtJlQbMCgYEA4ZzB\n+LQxPniapH31rppZ2nuF910mocoB31NnvN9Jn3/nXrir3fdIcO7X3cNenl6ldYuL\nufBnX93/WpFj35yJ3i3B7O2nPe6Rk6zKvJ9iSdnc/2ekKyc+b/oUteKgGsZR5B6N\njD/MgAl6W6fV8eFDSjAiwtvfu2QK6bigXoGwGxMCgYEAzWyF772CcP7IG31ojEOU\nSI1F0mjI0FYVTq+DdVP5GanoHlFe8r2M7jmAomS7MqScHfns9wLduBDD0wTAdkVD\nPwbOIufRUOPeZUQuX1B0VMNgadYhUq1Zysuv62a53secyibzcRMElB3Bp6wb9Qv4\nnhRlQTayeFsP0rUuL0oayCsCgYEAlGnykBC5dEcSM7NIsxuGkFtBvX/hsfyZTrgn\nPfAFFo+lPIJvTQ0m8mOsTY3/6F6KqdCqkh67Yi0/leyerrLjXuzq7VlI80zFJ0g7\n9elDVyGiZ8FeFaUzRaZViXETsYlUxaPzqZcuh+u0Oicmbn+pLFyOAXFytGsTYry5\ngnH9z1ECgYB86WIzOvUx+DwnZ1qRaYR7ZrVBcxMvwMfEiLoaTnQd37O8ZZmum8ha\ngYbcxwSnLV+VU82sbOL/+lV2b1uNPXG3z53x58ErMEfYCwRD9kFVhZQS6M/oTL1p\nHHDdX0b+TdUN0tJGRl/HZeJ+/vOuCUUtsy5PPdnOL3JKos26Ll51LA==\n-----END RSA PRIVATE KEY-----\n",
            "client_email": "mock@mock-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mock%40mock-project.iam.gserviceaccount.com"
        }
        cred = credentials.Certificate(mock_cred)
        initialize_app(cred, options={'projectId': 'demo-test'})


def test_create_user_and_firestore_document():
    """Test creating a Firebase Auth user and Firestore document."""
    # Create Auth user
    try:
        user = auth.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        uid = user.uid
        print(f"Created user with UID: {uid}")
        
        # Create Firestore document
        db = firestore.client()
        doc_ref = db.collection('accounts').document(uid)
        doc_ref.set({
            'tickets': 100,
            'email': 'test@example.com',
            'accountId': 'test-account-001'
        })
        print(f"Created Firestore document for account: {uid}")
        
        # Verify document exists
        doc = doc_ref.get()
        assert doc.exists
        assert doc.to_dict()['tickets'] == 100
        
    finally:
        # Cleanup
        try:
            auth.delete_user(uid)
        except:
            pass


def test_call_get_account_info_function():
    """Test calling the getAccountInfo Cloud Function."""
    # First, create a test user and document
    user = auth.create_user(
        email='functest@example.com',
        password='testpassword123'
    )
    uid = user.uid
    account_id = 'test-account-002'
    
    try:
        # Create Firestore document
        db = firestore.client()
        doc_ref = db.collection('accounts').document(account_id)
        doc_ref.set({
            'tickets': 50,
            'email': 'functest@example.com',
            'uid': uid
        })
        
        # Get custom token and exchange for ID token
        custom_token = auth.create_custom_token(uid)
        
        # Exchange custom token for ID token using Auth emulator REST API
        exchange_url = 'http://localhost:19099/identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=fake-api-key'
        exchange_payload = {
            'token': custom_token.decode(),
            'returnSecureToken': True
        }
        exchange_response = requests.post(exchange_url, json=exchange_payload)
        id_token = exchange_response.json()['idToken']
        
        # Call the Cloud Function
        # URL format: http://localhost:{port}/{project-id}/{region}/{function-name}
        function_url = 'http://localhost:15001/demo-test/us-central1/getAccountInfo'
        
        headers = {
            'Authorization': f'Bearer {id_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'data': {
                'accountId': account_id
            }
        }
        
        response = requests.post(function_url, json=payload, headers=headers)
        
        print(f"Function response status: {response.status_code}")
        print(f"Function response body: {response.text}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'result' in data
        assert 'account' in data['result']
        assert data['result']['account']['tickets'] == 50
        
    finally:
        # Cleanup
        try:
            auth.delete_user(uid)
            doc_ref.delete()
        except:
            pass
