import typer
import requests
from utils import save_token, remove_token

app = typer.Typer()
SERVER = "http://localhost:8000"

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

    If admin is set to True, the user will be registered as an admin user.
    Otherwise, the user will be registered as a regular user.
    """
    
    # Set role based on admin flag
    role = "admin" if admin else "user"

    # Make a request to the server to register the user
    payload = {"username": username, "email": email, "password": password, "role": role}
    response = requests.post(f"{SERVER}/auth/register", json=payload)

    if response.ok: # User registered successfully
        typer.echo("User registered successfully.")
    elif response.status_code == 400: # Bad request
        error_message = response.json().get("detail", "Unknown error")
        typer.echo(f"Failed to register user: {error_message}")
    else:
        typer.echo(f"Failed to register user: {response.text}")

@app.command()
def login(username: str, password: str):

    """
    Login user

    This command will authenticate the user and save the access token to a file.
    The token will be used for subsequent requests to the server.
    """

    # Make a request to the server to login the user
    payload = {"username": username, "password": password}
    response = requests.post(f"{SERVER}/auth/login", data=payload)

    if response.ok: # User logged in successfully, save token to file
        token = response.json().get("access_token")
        if not token:
            typer.echo("No token received.")
            return
        save_token(token)
        typer.echo(f"User {username} logged in successfully.")
    elif response.status_code == 401: # Invalid credentials, user not found
        typer.echo("Invalid username or password.")
    else:
        typer.echo(f"Failed to log in: {response.text}")

# Logout user and remove token
@app.command()
def logout():

    """
    Logout user

    This command will remove the access token from the file.
    """

    remove_token()
    typer.echo("User logged out successfully.")
    return