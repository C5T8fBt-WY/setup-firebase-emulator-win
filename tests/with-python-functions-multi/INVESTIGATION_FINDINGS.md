# Multiple Python Cloud Functions Investigation - FINDINGS

## Date
December 9, 2025

## Context
Investigating why `getAccountInfo` Cloud Function returns 400 BAD REQUEST in StA2BLE-Cloud CI workflow while other tests pass.

## Test Setup
- Firebase emulators with Auth (19099), Firestore (18080), Functions (15001)
- Two Python Cloud Functions: `getAccountInfo` and `uploadMeasurement`
- Both defined in `functions/main.py` using `@https_fn.on_call()` decorator

## Key Findings

### ✅ Firebase CLI CAN Serve Multiple Python Cloud Functions
When using `firebase emulators:start`, the Firebase CLI correctly:
1. Discovers both functions from `main.py`
2. Initializes both functions with separate HTTP endpoints
3. Serves both functions simultaneously on the Functions emulator port

**Evidence from emulator logs:**
```
+  functions: Loaded functions definitions from source: getAccountInfo, uploadMeasurement.
+  functions[us-central1-getAccountInfo]: http function initialized (http://127.0.0.1:15001/demo-test/us-central1/getAccountInfo).
+  functions[us-central1-uploadMeasurement]: http function initialized (http://127.0.0.1:15001/demo-test/us-central1/uploadMeasurement).
```

### ✅ Authentication Requires ID Tokens, Not Custom Tokens
The Cloud Functions authentication validator specifically checks for ID tokens:
```
ERROR:root:Error validating token: verify_id_token() expects an ID token, but was given a custom token.
WARNING:root:Callable request verification failed
```

**Solution:**
1. Create custom token with `auth.create_custom_token(uid)`
2. Exchange for ID token via Auth emulator REST API:
   ```python
   exchange_url = 'http://localhost:19099/identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=fake-api-key'
   exchange_payload = {
       'token': custom_token.decode(),
       'returnSecureToken': True
   }
   response = requests.post(exchange_url, json=exchange_payload)
   id_token = response.json()['idToken']
   ```
3. Use ID token in Authorization header: `Authorization: Bearer {id_token}`

### ✅ Test Results
Both tests pass successfully:
- `test_create_user_and_firestore_document` ✅ 
- `test_call_get_account_info_function` ✅

## Root Cause Analysis for StA2BLE-Cloud

The issue in StA2BLE-Cloud is **NOT** that multiple functions can't be served. The Firebase CLI handles this correctly.

### ✅ ACTUAL ROOT CAUSE IDENTIFIED

**Document ID Mismatch Between Python Script and Cloud Function**

1. **The Cloud Function expects** `accountId` to be the Firestore document ID:
   ```python
   # In getAccountInfo function
   account_ref = db.collection('accounts').document(account_id)
   ```

2. **The Python script was using** UID as the document ID:
   ```python
   # BUG in admin-create-account.py
   account_ref = db.collection('accounts').document(uid)  # Should be account_id!
   ```

3. **The C# test was looking for** accountId="test-account-001":
   ```csharp
   string accountId = "test-account-001";
   var accountInfo = await _storageService.GetAccountInfoAsync(accountId, ...);
   ```

4. **The CI workflow was creating** accountId="test-account" (wrong value):
   ```yaml
   python admin-create-account.py create $env:TEST_EMAIL test-account 100 --password-env
   ```

### Result
When `getAccountInfo` function tried to look up document ID "test-account-001", it didn't exist because:
- The actual document was created with UID as the ID (not accountId)
- Even if we fixed that, the CI was using "test-account" not "test-account-001"

This explains the 400 BAD REQUEST - the function was likely returning NOT_FOUND which manifested as a client error

## Fix Applied to StA2BLE-Cloud

### 1. Fixed admin-create-account.py
Changed document ID from UID to accountId:
```python
# OLD (WRONG):
account_ref = db.collection('accounts').document(uid)

# NEW (CORRECT):
account_ref = db.collection('accounts').document(account_id)
account_data = {
    'userId': uid,  # Store UID as a field
    'tickets': tickets,
    'offlineQuota': tickets,
    ...
}
```

### 2. Fixed CI workflow accountId
Changed from "test-account" to "test-account-001" to match test expectations:
```yaml
# OLD (WRONG):
python admin-create-account.py create $env:TEST_EMAIL test-account 100 --password-env

# NEW (CORRECT):
python admin-create-account.py create $env:TEST_EMAIL test-account-001 100 --password-env
```

## Impact

This fix should resolve the 400 BAD REQUEST error because:
1. The Firestore document will be created with the correct document ID
2. When `getAccountInfo` function queries `accounts/test-account-001`, it will find the document
3. The function will return 200 OK with the account data

## Testing

To verify the fix:
1. Push changes to StA2BLE-Cloud
2. Run CI workflow
3. Check that all 9 tests pass (including the `GetAccountInfo` test)
4. Verify Functions emulator logs show successful function execution
