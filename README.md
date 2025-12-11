# Setup Firebase Emulator (Windows Service)

[![GitHub release](https://img.shields.io/github/v/release/C5T8fBt-WY/setup-firebase-emulator-win)](https://github.com/C5T8fBt-WY/setup-firebase-emulator-win/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A GitHub Action that sets up the Firebase Emulator Suite as a **background Windows Service** using NSSM (Non-Sucking Service Manager). Specifically designed for **Windows Runners** to provide reliable, persistent emulator execution with automatic dependency management and caching support.

## Features

- **Reliable Service Management**: Uses Windows Service for stable background process execution
- **Standalone Binary**: Uses Firebase CLI standalone binary (no Node.js dependency)
- **Automatic Dependency Setup**: Handles Java installation automatically
- **Health Checks**: Comprehensive port and HTTP response verification
- **Flexible Configuration**: Customize versions, emulators, and wait times
- **Detailed Diagnostics**: Health check summary with port status table

## Quick Start

### Basic Usage

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      project-id: 'demo-project'
      emulators: 'auth,firestore,functions'

  - name: Run Tests
    run: npm test
```

### Complete Example

```yaml
name: Firebase Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Firebase Emulator
        uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
        with:
          firebase-tools-version: '13.24.1'
          java-version: '17'
          project-id: 'my-project'
          emulators: 'auth,firestore,storage,functions'
          wait-time: '60'

      - name: Run Tests
        run: npm test

      - name: Cleanup
        if: always()
        run: |
          nssm stop FirebaseEmulator
          nssm remove FirebaseEmulator confirm
        shell: pwsh
```

### Using Existing Java

If you've already set up Java in previous steps:

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Java
    uses: actions/setup-java@v4
    with:
      distribution: 'temurin'
      java-version: '17'

  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      java-version: 'none'  # Skip Java setup
      project-id: 'demo-project'
```

### Custom Working Directory

If your Firebase configuration files are in a subdirectory:

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      working-directory: './my-firebase-app'
      project-id: 'my-project'
```

This will look for `firebase.json`, `firestore.rules`, `storage.rules`, and the `functions/` directory inside `./my-firebase-app/`.

### Custom Firebase Configuration Path

For a custom `firebase.json` filename:

```yaml
steps:
  - uses: actions/checkout@v4

  # Option 1: Custom filename in working directory
  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      working-directory: './config'
      firebase-config-path: 'firebase.custom.json'  # Relative to working-directory
      project-id: 'my-project'

  # Option 2: Workspace-relative path (use ./ prefix)
  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      firebase-config-path: './config/firebase.custom.json'  # Relative to workspace root
      project-id: 'my-project'
```

### Custom Port Configuration

To use custom ports, configure them in your `firebase.json`:

```json
{
  "emulators": {
    "auth": {
      "port": 9199
    },
    "firestore": {
      "port": 8888
    },
    "storage": {
      "port": 9299
    },
    "functions": {
      "port": 5555
    }
  }
}
```

The action will automatically detect and use these ports for health checks. Update your application code to connect to the custom ports:

```python
# Python example
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:9199'
os.environ['FIRESTORE_EMULATOR_HOST'] = '127.0.0.1:8888'
os.environ['FIREBASE_STORAGE_EMULATOR_HOST'] = '127.0.0.1:9299'
```

```yaml
# Workflow example
- name: Setup Firebase Emulator with Custom Ports
  uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
  with:
    project-id: 'my-project'
    # firebase.json will define the custom ports

- name: Run Tests
  run: |
    # Tests will use the ports from firebase.json
    python test_firebase.py
```

## Inputs

| Input                    | Description                                                                                   | Required | Default           |
| ------------------------ | --------------------------------------------------------------------------------------------- | -------- | ----------------- |
| `firebase-tools-version` | Firebase Tools version to install                                                             | No       | `13.24.1`         |
| `java-version`           | Java version to setup (Temurin). Set to `none` to skip.                                       | No       | `17`              |
| `project-id`             | Firebase project ID for emulator                                                              | No       | `demo-project`    |
| `firebase-config-path`   | Path to firebase.json (absolute, workspace-relative with `./`, or working-directory-relative) | No       | `./firebase.json` |
| `working-directory`      | Working directory containing firebase.json and related files (rules, functions/, etc.)        | No       | `.`               |
| `emulators`              | Comma-separated list of emulators (e.g., `auth,firestore`). Empty = all from `firebase.json`  | No       | `""` (all)        |
| `wait-time`              | Seconds to wait after starting service before health checks                                   | No       | `60`              |
| `skip-health-check`      | Skip health check verification (not recommended)                                              | No       | `false`           |

### Available Emulators

- `auth` - Firebase Authentication
- `firestore` - Cloud Firestore
- `storage` - Cloud Storage
- `functions` - Cloud Functions
- `hosting` - Firebase Hosting
- `pubsub` - Cloud Pub/Sub
- `database` - Realtime Database

## Outputs

| Output                 | Description                             | Example                          |
| ---------------------- | --------------------------------------- | -------------------------------- |
| `service-status`       | Status of the Firebase Emulator service | `Running`, `Stopped`, `NotFound` |
| `health-check-summary` | JSON summary of health check results    | See below                        |

### Health Check Summary Format

```json
[
  {
    "Name": "Auth",
    "Port": 9099,
    "PortOpen": true,
    "HttpWorks": true,
    "StatusCode": 200
  },
  {
    "Name": "Firestore",
    "Port": 8080,
    "PortOpen": true,
    "HttpWorks": true,
    "StatusCode": 200
  }
]
```

## 🔧 How It Works

1. **Validates Windows Runner**: Ensures action runs on Windows
2. **Setup Dependencies**: 
   - Installs Java (if not set to `none`)
   - Downloads Firebase CLI standalone binary
   - Installs Firebase Functions dependencies if present
3. **Install NSSM**: Installs Non-Sucking Service Manager via Chocolatey
4. **Configure Service**:
   - Locates Firebase binary
   - Creates Windows service with proper working directory
   - Configures stdout/stderr logging
5. **Start Service**: Launches Firebase Emulator service
6. **Wait for Initialization**: Configurable wait time
7. **Health Checks** (unless skipped):
   - Tests port availability
   - Verifies HTTP responses
   - Displays summary table

## Health Check Output Example

```
======================================
Emulator Health Check
======================================

Testing Auth on port 9099...
  Port 9099 listening: True
  HTTP request: SUCCESS (Status: 200)

Testing Firestore on port 8080...
  Port 8080 listening: True
  HTTP request: SUCCESS (Status: 200)

======================================
Summary
======================================

Name      Port PortOpen HttpWorks StatusCode
----      ---- -------- --------- ----------
Auth      9099     True      True        200
Firestore 8080     True      True        200
Storage   9199     True     False        N/A
Functions 5001     True      True        200

[SUCCESS] All emulators are healthy!
```

**Note**: Some emulators (like Storage) may show `HttpWorks: False` but still function correctly. Check `PortOpen` status and run your tests.

## Troubleshooting

### Emulators not starting

1. **Check logs**: Upload `emulator-stdout.log` and `emulator-stderr.log` as artifacts:
   ```yaml
   - name: Upload Emulator Logs
     if: always()
     uses: actions/upload-artifact@v4
     with:
       name: emulator-logs
       path: |
         emulator-stdout.log
         emulator-stderr.log
       if-no-files-found: ignore
   ```

2. **Verify firebase.json**: Ensure your configuration is valid
3. **Check Functions dependencies**: 
   - For Node.js Functions: verify `functions/package.json` exists
   - For Python Functions: verify `functions/requirements.txt` exists and see Python Functions requirements below
4. **Increase wait time**: Some emulators may need more initialization time
   
   ```yaml
   wait-time: '90'
   ```

### Health checks failing but tests pass

Some emulators don't respond to plain HTTP GET requests:
- Check `PortOpen: True` indicates emulator is listening
- Run your actual tests - they may work despite HTTP check failure
- Consider using `skip-health-check: 'true'` if false positives occur

### Python Functions Requirements

**Firebase Functions for Python requires Python 3.10 or higher.** The default Python on Windows runners is 3.9, which is too old.

**You must set up Python before using this action.** There are two recommended approaches:

**Option 1 - Using uv (Recommended, Faster):**
```yaml
steps:
  - uses: actions/checkout@v4
  
  - name: Install uv
    uses: astral-sh/setup-uv@v7
    with:
      python-version: '3.12'  # Specify 3.10+ for Firebase Functions
      enable-cache: true
  
  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      project-id: 'demo-project'
```

**Option 2 - Using setup-python:**
```yaml
steps:
  - uses: actions/checkout@v4
  
  - uses: actions/setup-python@v5
    with:
      python-version: '3.12'  # 3.10+ required
  
  - name: Setup Firebase Emulator
    uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
    with:
      project-id: 'demo-project'
```

**Note:** This action will check the Python version and fail with a clear error message if it's below 3.10.

### Using firebase-admin Python SDK with Emulators

**The Firebase Admin SDK requires credentials even when using emulators.** If you're using `firebase-admin` in your Python code/tests, you need to use mock credentials:

```python
import firebase_admin
from firebase_admin import credentials
from google.auth import credentials as google_credentials

# Mock credential classes for emulator testing
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
        import time
        self.token = f'mock-token-{int(time.time())}'
    
    @property
    def service_account_email(self):
        return 'mock-email@your-project.iam.gserviceaccount.com'


class MockFirebaseCredential(credentials.Base):
    """Mock Firebase credential for emulator testing."""
    
    def __init__(self):
        self._g_credential = MockGoogleCredential()
    
    def get_credential(self):
        return self._g_credential


# Initialize Firebase Admin with mock credentials
if not firebase_admin._apps:
    firebase_admin.initialize_app(
        MockFirebaseCredential(),
        options={'projectId': 'your-project-id'}
    )
```

**Important:** Set emulator environment variables BEFORE importing firebase_admin modules:

```python
import os

# Set BEFORE importing firebase_admin.auth or firebase_admin.firestore
os.environ['FIRESTORE_EMULATOR_HOST'] = '127.0.0.1:8080'
os.environ['FIREBASE_AUTH_EMULATOR_HOST'] = '127.0.0.1:9099'

# NOW import
import firebase_admin
from firebase_admin import auth, firestore
```

**Why is this needed?** Even though emulators don't validate credentials, the Firebase Admin SDK still attempts to load them on initialization. Using `credential=None` is not sufficient - you need the mock credential classes shown above.

For a complete working example, see [tests/with-python-functions/test_emulators.py](tests/with-python-functions/test_emulators.py) in this repository.

### Java version issues

- Most emulators require Java 11+
- To use specific version:
  ```yaml
  java-version: '17'
  ```
- To skip (use pre-installed version):
  ```yaml
  java-version: 'none'
  ```

### Service already exists

If a previous run failed to clean up:

```yaml
- name: Pre-cleanup
  run: |
    $service = Get-Service -Name FirebaseEmulator -ErrorAction SilentlyContinue
    if ($service) {
      nssm stop FirebaseEmulator
      nssm remove FirebaseEmulator confirm
    }
  shell: pwsh
```

## Performance

| Scenario       | Time         |
| -------------- | ------------ |
| **First run**  | ~2-3 minutes |
| **Subsequent** | ~2-3 minutes |

Binary download is fast and consistent (~30-60 seconds for Firebase CLI).

## Comparison with Other Approaches

| Approach                          | Pros                                                                         | Cons                                     |
| --------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------- |
| **NSSM Service** (this action)    | ✅ Reliable<br>✅ Proper lifecycle<br>✅ Background logs<br>✅ No Node.js needed | ⚠️ Windows-only                           |
| PowerShell `Start-Job`            | ✅ Simple<br>✅ No dependencies                                                | ❌ Not persistent<br>❌ Cross-step issues  |
| Direct `firebase emulators:start` | ✅ Simple                                                                     | ❌ Blocks workflow<br>❌ No parallel tests |

## Examples

### Python Tests

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install Python dependencies
  run: pip install firebase-admin requests

- name: Setup Firebase Emulator
  uses: C5T8fBt-WY/setup-firebase-emulator-win@v1

- name: Run Python Tests
  run: python test_firebase.py
```

### Node.js Tests

```yaml
- name: Setup Firebase Emulator
  uses: C5T8fBt-WY/setup-firebase-emulator-win@v1

- name: Install dependencies
  run: npm install

- name: Run Tests
  run: npm test
```

### Multiple Test Suites

```yaml
- name: Setup Firebase Emulator
  uses: C5T8fBt-WY/setup-firebase-emulator-win@v1
  with:
    emulators: 'auth,firestore,storage,functions'

- name: Run Auth Tests
  run: python test_auth.py

- name: Run Firestore Tests
  run: python test_firestore.py

- name: Run Storage Tests
  run: python test_storage.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT License - see the [LICENSE](LICENSE) file for details.

##  Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Search [existing issues](https://github.com/C5T8fBt-WY/setup-firebase-emulator-win/issues)
3. Open a [new issue](https://github.com/C5T8fBt-WY/setup-firebase-emulator-win/issues/new) with:
   - Your workflow file
   - Emulator logs (if available)
   - Error messages
   - Steps to reproduce