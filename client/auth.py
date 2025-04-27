import typer
import requests
from utils import save_token, remove_token

app = typer.Typer()
SERVER = "http://localhost:5000" # Replace with REAL server URL

NOSERVER = True # client dev phase

# Register user
@app.command()
def register(username: str, email: str, password: str):

    if NOSERVER:
        typer.echo(f"Registering user {username}.")
        return

    payload = {"username": username, "password": password}
    response = requests.post(f"{SERVER}/auth/register", json=payload)
    if response.ok:
        typer.echo("User registered successfully.")
    else:
        typer.echo(f"Failed to register user: {response.text}")

# Login user and save token
@app.command()
def login(username: str, password: str):

    if NOSERVER:
        typer.echo(f"Login user {username}.")
        return

    payload = {"username": username, "email": email, "password": password}
    response = requests.post(f"{SERVER}/auth/login", json=payload)
    if response.ok:
        token = response.json().get("token")
        if not token:
            typer.echo("No token received.")
            return
        save_token(token)
        typer.echo(f"User {username} logged in successfully.")
    else:
        typer.echo(f"Failed to log in: {response.text}")

# Logout user and remove token
@app.command()
def logout():
    if NOSERVER:
        typer.echo("Logging out user.")
        return

    remove_token()
    typer.echo("User logged out successfully.")
    return