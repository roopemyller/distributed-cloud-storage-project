import typer
import requests
from utils import load_token

app = typer.Typer()
SERVER = "http://localhost:8000" # Replace with REAL server URL

def get_auth_headers():
    token = load_token()
    if not token:
        typer.echo("No token found. Please log in first.")
        raise typer.Exit()
    return {"Authorization": f"Bearer {token}"}

# List all users
@app.command()
def list_users():
    
    """
    List all users (admin only)
    
    This command is only available to admin users.
    """

    headers = get_auth_headers()
    response = requests.get(f"{SERVER}/admin/users", headers=headers)

    if response.ok:
        users = response.json()
        if users:
            typer.echo("Users in the system:")
            typer.echo("-" * 80)
            typer.echo(f"{'ID':<5} | {'Username':<20} | {'Email':<30} | {'Role'}")
            typer.echo("-" * 80)
            for user in users:
                user_id = user.get('id', 'N/A')
                username = user.get('username', 'Unknown')
                email = user.get('email', 'Unknown')
                role = user.get('role', 'Unknown')
                
                typer.echo(f"{user_id:<5} | {username:<20} | {email:<30} | {role}")
        else:
            typer.echo("No users found.")
    elif response.status_code == 403:
        typer.echo("Access denied: You do not have permission to view this information.")
    else:
        typer.echo(f"Failed to list users: {response.text}")

# Delete a user (admin only)
@app.command()
def delete_user(user_id: int):
    
    """
    Delete a user (admin only)
    
    This command is only available to admin users.
    """

    headers = get_auth_headers()
    response = requests.delete(f"{SERVER}/admin/users/{user_id}", headers=headers)

    if response.ok:
        typer.echo(f"User with ID {user_id} deleted successfully.")
    elif response.status_code == 403:
        typer.echo("Access denied: You do not have permission to perform this action.")
    elif response.status_code == 404:
        typer.echo(f"User with ID {user_id} not found.")
    elif response.status_code == 400:
        typer.echo("Cannot delete your own account.")
    else:
        typer.echo(f"Failed to delete user: {response.text}")
