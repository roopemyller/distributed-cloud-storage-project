import os

TOKEN_FILE = ".token"

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    print(f"Token saved to {TOKEN_FILE}")
    print(f"Token: {token}")

def load_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"Token file {TOKEN_FILE} does not exist.")
        return None
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
        print(f"Token loaded from {TOKEN_FILE}")
        print(f"Token: {token}")
        return token
    if not token:
        print(f"Token file {TOKEN_FILE} is empty.")
        return None
    
def remove_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print(f"Token file {TOKEN_FILE} removed.")
    else:
        print(f"Token file {TOKEN_FILE} does not exist.")
    print(f"Token file {TOKEN_FILE} does not exist.")
    return None

