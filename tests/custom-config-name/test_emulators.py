#!/usr/bin/env python3
"""Test Firebase emulators with custom config filename."""

import os
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests

# Initialize Firebase Admin
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "demo-project",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC5OyG\nhVQKedY8b7fJWnYL9Wr7F0MCW0IQxaQVJEI2M3YpKqYwHI5N9g8cSC\n-----END PRIVATE KEY-----\n",
    "client_email": "test@demo-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
})
firebase_admin.initialize_app(cred)

print("Testing Auth emulator...")
user = auth.create_user(email="test@example.com", password="password123")
print(f"✓ Created user: {user.uid}")
auth.delete_user(user.uid)
print(f"✓ Deleted user: {user.uid}")

print("\nTesting Firestore emulator...")
db = firestore.client()
doc_ref = db.collection('test').document('doc1')
doc_ref.set({'message': 'Hello from custom config test!'})
print(f"✓ Created document")
doc = doc_ref.get()
print(f"✓ Retrieved document: {doc.to_dict()}")
doc_ref.delete()
print(f"✓ Deleted document")

print("\n✅ All tests passed!")
