# Firebase Emulator Troubleshooting Guide

## Common Issues and Solutions

### 1. Hub Not Responding / Timeout Errors

**Symptoms:**
```
[ERROR] Failed to connect to Emulator Hub on port 4400
Error: timeout of 2000ms exceeded
This may indicate emulators failed to start.
```

**Diagnostic Steps:**

1. **Check if Hub port is actually open:**
   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 4400 -InformationLevel Quiet
   ```
   - Returns `True` if port is open
   - Returns `False` if nothing is listening

2. **Check emulator process status:**
   ```powershell
   Get-Service -Name FirebaseEmulator -ErrorAction SilentlyContinue
   ```
   - Should show `Running` status
   - If `Stopped` or doesn't exist, service didn't start

3. **Check NSSM service logs:**
   ```powershell
   # View stdout log
   Get-Content "emulator-stdout.log" -Tail 50
   
   # View stderr log  
   Get-Content "emulator-stderr.log" -Tail 50
   ```

**Common Causes & Fixes:**

- **Java version too old**: Firebase Emulators require Java 21+
  ```powershell
  java -version  # Should show 21 or higher
  ```
  Fix: Install Java 21+ or use `actions/setup-java@v4` with `java-version: '21'`

- **Port already in use**: Another process is using the Hub port
  ```powershell
  netstat -ano | findstr :4400
  ```
  Fix: Change `emulators.ui.port` in firebase.json or kill the conflicting process

- **Emulator startup race condition**: Hub may not be ready yet
  Fix: Increase `wait-time` parameter (default 60s, try 120s for CI)
  ```yaml
  - uses: C5T8fBt-WY/setup-firebase-emulator-win@main
    with:
      wait-time: 120  # Increase if startup is slow
  ```

- **Service failed to start**: Check stderr logs for Java errors
  Fix: Ensure JAVA_HOME points to Java 21+ installation

### 2. Python Functions Not Loading

**Symptoms:**
```
!!  functions: Failed to load function definition from source: 
    Error: spawn "...\venv\Scripts\activate.bat" ENOENT

Function us-central1-myFunction does not exist, valid functions are:
```

**Diagnostic Steps:**

1. **Check if venv exists:**
   ```powershell
   Test-Path "functions/venv/Scripts/activate.bat"
   ```

2. **Check if requirements.txt exists:**
   ```powershell
   Test-Path "functions/requirements.txt"
   ```

3. **Check if uv is installed:**
   ```powershell
   Get-Command uv -ErrorAction SilentlyContinue
   ```

**Common Causes & Fixes:**

- **uv not installed**: Action requires `uv` for Python dependency management
  ```yaml
  - uses: astral-sh/setup-uv@v5  # Add before setup-firebase-emulator-win
  ```

- **Python version too old**: firebase-functions requires Python 3.10+
  ```yaml
  - uses: actions/setup-python@v5
    with:
      python-version: "3.11"  # Or higher
  ```

- **Functions directory mismatch**: Action looks in `functions/` by default
  - For monorepos, use `functions[].source` in firebase.json:
    ```json
    {
      "functions": [
        {
          "source": "apps/functions",  // Custom path
          "codebase": "default"
        }
      ]
    }
    ```

- **Manual venv preparation conflict**: Remove manual venv creation if using the action
  - Action handles venv creation automatically
  - Duplicate preparation can cause timing issues

### 3. Function Returns 404

**Symptoms:**
```
Response status code does not indicate success: 404 (Not Found)
Function us-central1-myFunction does not exist
```

**Diagnostic Steps:**

1. **Check emulator logs for loaded functions:**
   ```powershell
   Get-Content "emulator-stdout.log" | Select-String "Loaded functions"
   ```
   Should show:
   ```
   +  functions: Loaded functions definitions from source: myFunction, otherFunction.
   +  functions[us-central1-myFunction]: http function initialized
   ```

2. **Verify function name matches:**
   - Python: `@https_fn.on_call()` decorator name must match URL
   - Example: `def myFunction(req)` → URL ends with `/myFunction`

3. **Check project ID in URL:**
   ```
   Correct:   http://127.0.0.1:5001/demo-project/us-central1/myFunction
   Incorrect: http://127.0.0.1:5001/wrong-project/us-central1/myFunction
   ```

**Common Causes & Fixes:**

- **Function name mismatch**: Use exact camelCase/snake_case as defined
  ```python
  # Function definition
  @https_fn.on_call()
  def getAccountInfo(req):  # NOT get_account_info
  ```

- **Wrong project ID**: Environment variable not set
  ```yaml
  env:
    FIREBASE_PROJECT_ID: "demo-my-project"
  ```

- **Venv not loaded**: See "Python Functions Not Loading" section above

- **Function crashed during load**: Check stderr logs for Python import errors
  ```powershell
  Get-Content "emulator-stderr.log" | Select-String "Error|Traceback"
  ```

### 4. Authentication Errors

**Symptoms:**
```
{"error":{"message":"Authentication required","status":"UNAUTHENTICATED"}}
```

**Diagnostic Steps:**

1. **Check if auth emulator is running:**
   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 9099 -InformationLevel Quiet
   ```

2. **Verify auth header in request:**
   ```csharp
   // Should include Bearer token
   httpRequest.Headers.Authorization = 
       new AuthenticationHeaderValue("Bearer", idToken);
   ```

3. **Test token generation:**
   ```python
   from firebase_admin import auth
   custom_token = auth.create_custom_token(uid)
   # Exchange for ID token via REST API
   ```

**Common Causes & Fixes:**

- **Auth emulator not configured**: Add to firebase.json
  ```json
  {
    "emulators": {
      "auth": {"port": 9099}
    }
  }
  ```

- **Missing environment variables**:
  ```yaml
  env:
    FIREBASE_AUTH_EMULATOR_HOST: "127.0.0.1:9099"
  ```

- **Token not included in request**: Callable functions require auth
  ```python
  @https_fn.on_call()
  def myFunction(req: https_fn.CallableRequest):
      if not req.auth:
          raise https_fn.HttpsError(
              code=https_fn.FunctionsErrorCode.UNAUTHENTICATED,
              message="Authentication required"
          )
  ```

### 5. Firestore Connection Issues

**Symptoms:**
```
Failed to connect to Firestore emulator
Error: connect ECONNREFUSED 127.0.0.1:8080
```

**Diagnostic Steps:**

1. **Check Firestore port:**
   ```powershell
   Test-NetConnection -ComputerName 127.0.0.1 -Port 8080 -InformationLevel Quiet
   ```

2. **Verify environment variable:**
   ```powershell
   echo $env:FIRESTORE_EMULATOR_HOST
   # Should output: 127.0.0.1:8080
   ```

3. **Check firebase.json configuration:**
   ```json
   {
     "emulators": {
       "firestore": {"port": 8080}
     }
   }
   ```

**Common Causes & Fixes:**

- **Port mismatch**: Environment variable doesn't match firebase.json
  ```yaml
  env:
    FIRESTORE_EMULATOR_HOST: "127.0.0.1:8080"  # Must match config
  ```

- **Using `0.0.0.0` as host**: Breaks Hub on Windows
  ```json
  // DON'T DO THIS on Windows:
  {
    "emulators": {
      "firestore": {
        "host": "0.0.0.0",  // ❌ Remove this line
        "port": 8080
      }
    }
  }
  ```

- **Emulator not started**: Check if firestore is in emulators list
  ```yaml
  with:
    emulators: "auth,firestore,functions"  # Include firestore
  ```

### 6. localhost vs 127.0.0.1 Issues

**Symptoms:**
```
Request to http://localhost:5001/... failed
Connection refused or timeout
```

**Diagnostic Steps:**

1. **Test both addresses:**
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 5001 -InformationLevel Quiet
   Test-NetConnection -ComputerName 127.0.0.1 -Port 5001 -InformationLevel Quiet
   ```

2. **Check DNS resolution:**
   ```powershell
   Resolve-DnsName localhost
   # Should resolve to 127.0.0.1
   ```

**Common Causes & Fixes:**

- **Windows DNS issues**: localhost may not resolve correctly in CI
  Fix: Use 127.0.0.1 explicitly
  ```csharp
  // Instead of:
  var url = $"http://localhost:{port}/...";
  
  // Use:
  var host = config.EmulatorHost == "localhost" ? "127.0.0.1" : config.EmulatorHost;
  var url = $"http://{host}:{port}/...";
  ```

- **IPv6 vs IPv4 conflict**: localhost may resolve to ::1 (IPv6)
  Fix: Force IPv4 with 127.0.0.1

### 7. Performance Issues / Slow Startup

**Symptoms:**
- Action takes >2 minutes to complete
- Tests timeout waiting for emulators

**Diagnostic Steps:**

1. **Check timing logs:**
   ```powershell
   Get-Content "emulator-stdout.log" | Select-String "TIMING"
   ```

2. **Identify slow steps:**
   - npm install: >30s (Node.js functions)
   - uv pip install: >10s (Python functions)
   - Java download: >20s (first run)

**Optimization Tips:**

- **Use caching** for Firebase emulators:
  ```yaml
  - uses: actions/cache@v4
    with:
      path: ~/.cache/firebase/emulators
      key: ${{ runner.os }}-firebase-emulators-${{ hashFiles('firebase.json') }}
  ```

- **Use uv instead of pip** for Python:
  ```yaml
  - uses: astral-sh/setup-uv@v5
    with:
      enable-cache: true
  ```

- **Reduce wait-time** if emulators start quickly:
  ```yaml
  with:
    wait-time: 30  # Default is 60s
  ```

### 8. Service Cleanup Issues

**Symptoms:**
```
Service 'FirebaseEmulator' already exists
Cannot install NSSM service
```

**Diagnostic Steps:**

1. **Check existing service:**
   ```powershell
   Get-Service -Name FirebaseEmulator -ErrorAction SilentlyContinue
   ```

2. **Check NSSM processes:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*firebase*"}
   ```

**Fix:**

Manual cleanup if needed:
```powershell
# Stop service
nssm stop FirebaseEmulator

# Remove service
nssm remove FirebaseEmulator confirm

# Kill any remaining processes
Get-Process | Where-Object {$_.ProcessName -like "*firebase*"} | Stop-Process -Force
```

The action should handle cleanup automatically in the `post` step.

## Debug Checklist

When troubleshooting, check these in order:

- [ ] Java 21+ installed and in PATH
- [ ] Python 3.10+ installed (for Python Functions)
- [ ] uv installed (for Python Functions)
- [ ] firebase.json exists and is valid JSON
- [ ] All required emulator ports are free
- [ ] Environment variables set correctly:
  - `FIREBASE_PROJECT_ID`
  - `FIREBASE_USE_EMULATOR=true`
  - `FIREBASE_AUTH_EMULATOR_HOST`
  - `FIRESTORE_EMULATOR_HOST`
- [ ] Functions directory contains package.json or requirements.txt
- [ ] Venv created (for Python Functions)
- [ ] Emulator service is running
- [ ] All emulator ports responding (use Test-NetConnection)
- [ ] Check emulator-stdout.log and emulator-stderr.log

## Getting Additional Help

1. **Enable verbose logging:**
   ```yaml
   - uses: C5T8fBt-WY/setup-firebase-emulator-win@main
     with:
       # ... other options
   
   - name: Debug - Show all logs
     if: failure()
     shell: pwsh
     run: |
       Write-Host "=== STDOUT ==="
       Get-Content emulator-stdout.log
       Write-Host "`n=== STDERR ==="
       Get-Content emulator-stderr.log
   ```

2. **Check service status:**
   ```yaml
   - name: Debug - Service status
     if: failure()
     shell: pwsh
     run: |
       Get-Service -Name FirebaseEmulator | Format-List *
       nssm status FirebaseEmulator
   ```

3. **Test port connectivity:**
   ```yaml
   - name: Debug - Port connectivity
     if: failure()
     shell: pwsh
     run: |
       $ports = @(4400, 9099, 8080, 5001)
       foreach ($port in $ports) {
         $result = Test-NetConnection -ComputerName 127.0.0.1 -Port $port -InformationLevel Quiet
         Write-Host "Port $port`: $result"
       }
   ```

## Related Documentation

- [Firebase Emulator Suite Documentation](https://firebase.google.com/docs/emulator-suite)
- [Firebase Functions Python Guide](https://firebase.google.com/docs/functions/callable-reference)
- [NSSM - Non-Sucking Service Manager](https://nssm.cc/)
- [GitHub Actions Troubleshooting](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
