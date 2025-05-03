import os

TOKEN_FILE = ".token"

# saves the token to a file
def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

# loads the token from a file
def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
        return token
    if not token:
        return None
    
# removes the token file
def remove_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    return None

