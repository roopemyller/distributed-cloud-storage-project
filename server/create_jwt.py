from jose import jwt
import datetime

def create_test_jwt(
    secret_key: str,
    user_id: str = "test_user_123",
    email: str = "test@example.com",
    roles: list = ["user"],
    expires_delta: int = 60,  # minutes
    algorithm: str = "HS256"
):
    # Set expiration time
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    
    # Create payload with claims
    payload = {
        "sub": user_id,
        "email": email,
        "roles": roles,
        "exp": expire,
        "iat": datetime.datetime.utcnow(),
        # Add any other claims you need for testing
        "name": "Test User",
        "org_id": "test_org_456"
    }
    
    # Create the JWT token
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    
    return token

# Generate a test token
secret_key = "aaa"
test_token = create_test_jwt(
    secret_key=secret_key,
    user_id="test123",
    email="tester@example.com",
    roles=["admin", "user"]
)

print(f"Test Token: {test_token}")

# Verify it works by decoding
decoded = jwt.decode(test_token, secret_key, algorithms=["HS256"])
print(f"Decoded Token: {decoded}")