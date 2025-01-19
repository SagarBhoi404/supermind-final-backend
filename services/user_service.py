import hashlib
import jwt
import datetime
import config

# Utility function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generate JWT token for login
def generate_jwt_token(user_id, email, role):
    payload = {
        'user_id': str(user_id),
        'email': email,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }
    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm='HS256')
    return token

# Decode JWT token (for profile verification)
def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
