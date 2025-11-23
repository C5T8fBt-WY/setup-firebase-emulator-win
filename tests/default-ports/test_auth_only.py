"""Quick test for Auth emulator only."""
import os

os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "127.0.0.1:9099"
import firebase_admin
from firebase_admin import credentials, auth

cred_dict = {
    "type": "service_account",
    "project_id": "demo-project",
    "private_key_id": "key123",
    "private_key":
    "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAub1uzfk0FR/f21aV9o0E3Q60xXzKAiy1UPBII/qFWL1F+rX1\nf3HG92hMXxrDpDs5T4cYQ5/aWzXcIJWSG6EruovkOLjYDlJ/wVW606JsTTwjhsrB\nRt2r7bYlyWRPRW/QCEcmi60Zago1oVBwwObRhbW0eAGmZO3pDaeUgJRH3PNUlnst\nXzp/hSJPZQv92sNV5NqZR7Kj3nuabkR8rbvsal02w2A4NW7KiLGyQgAXMYgO7Rc1\n//fZ04lmoXSnhZBLyxA+9y9MjnypW9msVVAb+h3af6Hb449XEVlyC1lsFKUHdp4a\nQqY2MnxhZxAS3OyrJSQMEvyqJT22KLuzSAvkXwIDAQABAoIBAEv6hg+Cn7/+bGuE\nVU7oK7OjluXsIJRYJoln6RKyoYaF0lD2yuhpqeq9wvPqdlpBkbWK/S14f/FsrFG1\n7XEY8lLac66SSms9ax4yi/yThfroHV4/pWVwOyq/pmBmBJlSXkZsmINteSZr67lD\ntwPpx46LIDow7ph9y6Y2xWP9hBII0pPE2XKicFUOXDHtYYCgyKiVaC6n29QJRHY5\nY8D+w+Hjqojx5VvBvV/q3Sh710cs5Z4MhE2B+6dAw5HaZMtnBadJ4LoAH07uBN2w\nxHCcOoX0zvct8zlrR7gxj5p1YVleZfGnV6gKsrbqaPxVZqKf81SI4I7N9fkBXWVw\nCT+tK9kCgYEA7pAsWx+03BwpaiLAE3nHKDiZIqaMMT1SZqkuHe0wc1VqB3xy5Dkn\nZfRUV9MMiObfzDaKDish6I/Kqk0Q9SXpNa/rTAGswa7xgOLnpOsfYTFVCAUVtM4n\nOXjDNKhUluKUw9EGZgVrKe22yBPB/SxC1PsXUWLzLFKnGiogH7WypUkCgYEAx1De\na5R31dM9Ib2tJ+PXBkO5g3aJVHqZrrExaegd1vQw35BgHvnxcuDD/zr4Y9cobCqu\nzbv+2E42N5IVHDH2IlmU4A2A9sJ7cmLXrnNk6PZoTKzfY6fPdLHT2TSyIQEd36gV\nC0WT+2dVhBmXNn8EKbmJ+JV5zA9CwjjQyaMkRGcCgYAyhmZehkCPvYcn62Qyu7/q\nTNJh/FQEubAR/hK+U9XHF3f1Te4nV9N4TF7wmso01HDhl0t15LyxvIJ3vwqwYO8b\nZ761wkUMYDjVyzi0PPfQZdpUcH9AY8j66xCsvlnr+uD29/Ya9VrU7nuftE+Jhy5A\nXU169zH5WSf66qETFjBXwQKBgH+EfJilZznVKPJSUNsJiMNIRwMVrmzu9y3tzaht\nSdIBbtdJnkWTMWeG575+MvZlbEYv1KBpm3U2LLfG7VyZlliJqZbi7NRyvtoC5OyG\nhVQKedY8b7tpXG/Taa84aJJ3DW7PMY+Bl1ir1ulqGfVStA4h12TD9SWZyeNKyEGI\n76YXAoGBAOjs37VNQeRPJbGLiZz4jjR/bIdKE/XN6pIan7mYHpHq0HU3HHkZF5E/\nNQySCZ/5pVRDJVgYJTD4hPWCMwY60iz1RopGBQAP5/Cbl3DVBb9PKT6NVlXn/Cfb\n+XsHJwfGHMwxqU2WqHvaL4ROmEN5g1NwacSWGn7b3zyG5V4fU6Zf\n-----END RSA PRIVATE KEY-----\n",
    "client_email": "test@demo-project.iam.gserviceaccount.com",
    "client_id": "123",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}

firebase_admin.initialize_app(credentials.Certificate(cred_dict))
user = auth.create_user(email="auth-only@example.com", password="test123")
print(f"[OK] Created user: {user.uid}")
auth.delete_user(user.uid)
print("[OK] Deleted user")
print("[OK] Auth-only test PASSED")
