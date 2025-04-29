import os

TOKEN_FILE = ".token"

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
        return token
    if not token:
        return None
    
def remove_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    return None

