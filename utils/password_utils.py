import hashlib

# Hash password using SHA256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
