# Multi-Function Python Cloud Functions Test

This test case replicates the issue from StA2BLE-Cloud where calling `getAccountInfo` Cloud Function fails with 400 BAD REQUEST.

## Issue Description

In StA2BLE-Cloud CI workflow:
- Firebase emulators (Auth, Firestore) start successfully
- Python Functions Framework is started with `--target=analyze` 
- Tests try to call `getAccountInfo` function
- Result: 400 BAD REQUEST

## Problem

`functions-framework --target=<function>` only serves ONE function. When multiple callable functions exist in `main.py`, only the targeted function is accessible.

## Setup

1. Firebase emulators: Auth (9099), Firestore (8080), Functions (5001)
2. Multiple Python Cloud Functions in `functions/main.py`:
   - `getAccountInfo`: Get account info from Firestore
   - `uploadMeasurement`: Upload measurement data

## Running the Test

```powershell
# Install dependencies
cd functions
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..

# Start emulators
firebase emulators:start

# In another terminal, run tests
pytest test_multi_functions.py -v
```

## Investigation Goals

1. Understand how to properly serve multiple Python Cloud Functions locally
2. Test different approaches:
   - Using Firebase CLI `firebase emulators:start` with Functions emulator
   - Using multiple `functions-framework` instances
   - Other solutions

## Expected Outcome

Find a way to serve multiple Python Cloud Functions in CI that works on Windows runners.
