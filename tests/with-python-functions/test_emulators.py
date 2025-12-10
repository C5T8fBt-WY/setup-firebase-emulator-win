import pytest
import requests
import time


def test_python_functions_emulator():
    """Test Python Firebase Functions in emulator."""
    # Give emulator extra time to initialize Python runtime
    max_retries = 10
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            # Test hello_world function
            response = requests.get(
                "http://127.0.0.1:5001/demo-python-functions/us-central1/hello_world", timeout=5)
            assert response.status_code == 200
            assert "Hello from Python" in response.text
            print("[OK] hello_world function is responding")

            # Test echo function
            test_data = "Test message"
            response = requests.post("http://127.0.0.1:5001/demo-python-functions/us-central1/echo",
                                     data=test_data, timeout=5)
            assert response.status_code == 200
            assert test_data in response.text
            print("[OK] echo function is responding")

            # Test Firestore access from function
            response = requests.get(
                "http://127.0.0.1:5001/demo-python-functions/us-central1/check_firestore", timeout=5)
            if response.status_code != 200:
                print(f"\n[ERROR] check_firestore failed with {response.status_code}")
                print(f"Response body: {response.text}")
                try:
                    error_data = response.json()
                    print(f"Error type: {error_data.get('type')}")
                    print(f"Error message: {error_data.get('message')}")
                    print(f"Environment variables received by Python:")
                    for k, v in error_data.get('env', {}).items():
                        print(f"  {k}={v}")
                    print(f"\nFull traceback:\n{error_data.get('traceback')}")
                except:
                    pass
            assert response.status_code == 200, f"check_firestore failed: {response.text}"
            print("[OK] check_firestore function is responding")

            break
        except (requests.exceptions.ConnectionError, AssertionError) as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                pytest.fail(f"Python Functions not accessible after {max_retries} attempts: {e}")


def test_firestore_emulator():
    """Test Firestore emulator accessibility."""
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        assert response.status_code == 200
        print("[OK] Firestore Emulator is responding")
    except Exception as e:
        pytest.fail(f"Firestore Emulator not accessible: {e}")


def test_auth_and_firestore_integration():
    """
    Test Auth + Firestore integration like StA2BLE-Cloud does.
    This mimics the getAccountInfo flow: create user, get token, call function that reads Firestore.
    """
    import firebase_admin
    from firebase_admin import auth, credentials, firestore
    import os
    
    # Initialize Firebase Admin with emulator settings
    # For emulators, we need some credentials even if fake
    if not firebase_admin._apps:
        # Set environment variable for mock credentials (required by Firestore client even with emulator)
        fake_creds = {
            "type": "service_account",
            "project_id": "demo-python-functions",
            "private_key_id": "fake",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA2a2rwY/4notYPXXcjRKPQMB2R7EqnFM+IhqdJE8Kl2nNEwKD\ngEjNQgQexf3xXx0hYqZpNlxzrKzXhhzXPK6sE+P9qHSXJRPCBrARgBKwD2FUVQT4\npLIxUx7OxU7N5DjWRQz2I2GKF3UtJBPLqPqpN0oROPM9/+SLXNJPmXEgCzKkBBcg\ncvC7ySPqL+Ju7xQnXBOY1pu+0kEJiFcQBwXvGlZCgqrYD2Q2p8F2xLBp+Mc32VnZ\nDfm8vgC8cRgZMVT+OuDqFp1Y2vXTqVa5nOQOOw8XHCJW7vP93kJNBdS+7JwQjTnN\n8gY3pCJL3kqfYgPaYT+J2K7SYNZpHpv+xQIDAQABAoIBABkWl4T3+tKPlJ3Txcfz\n6wq7s+YM+qgU2hMhm/PXLjd2T6Qdx6OcTr6m8QKGzhDqB0dWvxT2F5vJNBBj4yPh\nAwLZk0mqZB6xfGqNPO6E4A3BqGKr2M4y9nKDDxl3EhJ7FMVU3E4YqVQOvJqXqX6Y\nmqpZnSGsKL1NHC9o8z0tR8KeBnNZT9LMPrGCjU9U2xvwwxA+q6JbYo3HZNRZqYUf\naQkM7oqvqQKBgQD1aYTbV9DRLqZi0pLkVHGHMqWtTprVJpXZNQDqVm7HPFZqNQEy\n4kX0YeLJDX0IQPFPvCGqGZ4HWJQk2A3EQKBQD+qxZLmnOpHxdXwPYfT3kLHGHZFU\nqwKBgQDguI2Y/R5qn2K3T7QqUQkXNqT5P1KhvVWtXPY0qrLJGQKBgQCrECvjXOWl\niXQBZQNhwTwVBKJ6tQ8CgYEAwL+HNxM=\n-----END RSA PRIVATE KEY-----\n",
            "client_email": "fake@demo-python-functions.iam.gserviceaccount.com",
            "client_id": "12345",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
        import json
        import tempfile
        # Write fake credentials to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(fake_creds, f)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
            
        firebase_admin.initialize_app(options={
            'projectId': 'demo-python-functions',
        })
    
    # Set emulator environment variables for admin SDK
    os.environ['FIRESTORE_EMULATOR_HOST'] = '127.0.0.1:8080'
    os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:9099'
    
    try:
        # Step 1: Create test user in Auth emulator
        print("\n[TEST] Creating test user in Auth emulator...")
        test_email = "test@example.com"
        test_password = "testpassword123"
        
        try:
            # Try to delete if exists
            user = auth.get_user_by_email(test_email)
            auth.delete_user(user.uid)
            print(f"  Deleted existing user: {user.uid}")
        except:
            pass
        
        # Create new user
        user = auth.create_user(
            email=test_email,
            password=test_password,
            email_verified=True
        )
        print(f"  Created user: {user.uid}")
        
        # Step 2: Create account document in Firestore
        print("\n[TEST] Creating account document in Firestore...")
        db = firestore.client()
        account_id = "test-account-001"
        account_ref = db.collection('accounts').document(account_id)
        account_ref.set({
            'accountId': account_id,
            'tickets': 100,
            'offlineQuota': 50,
            'userId': user.uid,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        print(f"  Created account: {account_id}")
        
        # Step 3: Get custom token for authentication
        print("\n[TEST] Getting custom token...")
        custom_token = auth.create_custom_token(user.uid)
        print(f"  Got custom token (length: {len(custom_token)})")
        
        # Step 4: Exchange custom token for ID token
        print("\n[TEST] Exchanging custom token for ID token...")
        api_key = "fake-api-key"  # Emulator doesn't validate this
        token_exchange_url = f"http://127.0.0.1:9099/identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
        
        token_response = requests.post(
            token_exchange_url,
            json={"token": custom_token.decode('utf-8'), "returnSecureToken": True},
            timeout=5
        )
        
        if token_response.status_code != 200:
            print(f"  Token exchange failed: {token_response.status_code}")
            print(f"  Response: {token_response.text}")
            pytest.fail(f"Failed to exchange custom token: {token_response.text}")
        
        id_token = token_response.json()['idToken']
        print(f"  Got ID token (length: {len(id_token)})")
        
        # Step 5: Call get_account_info function with auth token
        print("\n[TEST] Calling get_account_info function with auth...")
        function_url = "http://127.0.0.1:5001/demo-python-functions/us-central1/get_account_info"
        
        function_response = requests.post(
            function_url,
            json={"data": {"accountId": account_id}},
            headers={"Authorization": f"Bearer {id_token}"},
            timeout=10
        )
        
        if function_response.status_code != 200:
            print(f"  Function call failed: {function_response.status_code}")
            print(f"  Response: {function_response.text}")
            pytest.fail(f"Function call failed: {function_response.text}")
        
        result = function_response.json()
        print(f"  Function response: {result}")
        
        # Verify the response
        assert 'result' in result, "Response should contain 'result'"
        result_data = result['result']
        
        assert result_data['accountId'] == account_id, f"Expected accountId={account_id}, got {result_data.get('accountId')}"
        assert result_data['tickets'] == 100, f"Expected tickets=100, got {result_data.get('tickets')}"
        assert result_data['offlineQuota'] == 50, f"Expected offlineQuota=50, got {result_data.get('offlineQuota')}"
        assert result_data['authUid'] == user.uid, f"Expected authUid={user.uid}, got {result_data.get('authUid')}"
        
        print("[OK] Auth + Firestore integration test passed!")
        print(f"  ✓ User authentication works")
        print(f"  ✓ Python function receives auth context")
        print(f"  ✓ Function can read from Firestore")
        print(f"  ✓ Data matches expected values")
        
    except Exception as e:
        import traceback
        print(f"\n[ERROR] Test failed: {str(e)}")
        print(traceback.format_exc())
        pytest.fail(f"Auth + Firestore integration test failed: {e}")
    finally:
        # Cleanup
        try:
            if 'user' in locals():
                auth.delete_user(user.uid)
                print(f"\n[CLEANUP] Deleted test user: {user.uid}")
            if 'account_ref' in locals():
                account_ref.delete()
                print(f"[CLEANUP] Deleted test account: {account_id}")
        except Exception as e:
            print(f"[WARN] Cleanup failed: {e}")
