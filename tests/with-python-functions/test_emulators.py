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
            assert response.status_code == 200
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
