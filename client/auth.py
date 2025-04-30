import typer
import requests
from utils import save_token, remove_token

app = typer.Typer()
SERVER = "http://localhost:8000" # Replace with REAL server URL

# Register user
@app.command()
def register(
    username: str,
    email: str,
    password: str,
    admin: bool = typer.Option(
        False, 
        "--admin",
        "-a",
        help="Register as admin user"
        ), 
    ):

    """
    Register a new user
    """
    
    role = "admin" if admin else "user"

    payload = {"username": username, "email": email, "password": password, "role": role}
    response = requests.post(f"{SERVER}/auth/register", json=payload)
    if response.ok:
        typer.echo("User registered successfully.")
    else:
        typer.echo(f"Failed to register user: {response.text}")

# Login user and save token
@app.command()
def login(username: str, password: str):

    """
    Login user
    """

    payload = {"username": username, "password": password}
    response = requests.post(f"{SERVER}/auth/login", data=payload)
    if response.ok:
        token = response.json().get("access_token")
        if not token:
            typer.echo("No token received.")
            return
        save_token(token)
        typer.echo(f"User {username} logged in successfully.")
    elif response.status_code == 401:
        typer.echo("Invalid username or password.")
    else:
        typer.echo(f"Failed to log in: {response.text}")

# Logout user and remove token
@app.command()
def logout():

    """
    Logout user
    """

    remove_token()
    typer.echo("User logged out successfully.")
    return