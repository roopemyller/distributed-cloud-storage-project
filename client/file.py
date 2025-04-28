import typer
import requests
import os
from utils import load_token

app = typer.Typer()
SERVER = "http://localhost:8000" # Replace with REAL server URL
TOKEN_FILE = ".token"

NOSERVER = False # client dev phase

def get_auth_headers():
    token = load_token()
    if not token:
        typer.echo("No token found. Please log in first.")
        raise typer.Exit()
    return {"Authorization": f"Bearer {token}"}

# Upload file to the "cloud" storage
@app.command()
def upload(file_path: str, save_name: str=typer.Option(None, "--save-name", "-s", help="Name to save the file as in the cloud.")):
    if NOSERVER:
        typer.echo(f"Uploading file '{file_path}'.")
        return

    if not os.path.exists(file_path):
        typer.echo(f"File {file_path} does not exist.")
        raise typer.Exit()
    
    headers = get_auth_headers()

    final_name = save_name if save_name else os.path.basename(file_path)

    with open(file_path, "rb") as f:
        files = {"file": (final_name, f, "application/octet-stream")}
        response = requests.post(f"{SERVER}/file/upload", files=files, headers=headers)
    if response.ok:
        typer.echo(f"File uploaded successfully as '{final_name}'.")
    else:
        typer.echo(f"Failed to upload file: {response.text}")

# Download file from the "cloud" storage
@app.command()
def download(file_name: str, save_path: str=typer.Option(".", "--save-path", "-p", help="Path to save the downloaded file.")):
    if NOSERVER:
        typer.echo(f"Downloading file '{file_name}' to '{save_path}'.")
        return

    headers = get_auth_headers()

    params = {"file_name": file_name}
    response = requests.get(f"{SERVER}/file/download", params=params, headers=headers)
    if response.ok:
        file_save_path = os.path.join(save_path, file_name)
        with open(file_save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        typer.echo(f"File downloaded successfully to {file_save_path}.")
    else:
        typer.echo(f"Failed to download file: {response.text}")

# Delete file from the "cloud" storage
@app.command()
def delete(file_name: str):
    if NOSERVER:
        typer.echo(f"Deleting file '{file_name}'.")
        return

    headers = get_auth_headers()

    params = {"file_name": file_name}
    response = requests.delete(f"{SERVER}/file/delete", params=params, headers=headers)
    if response.ok:
        typer.echo(f"File {file_name} deleted successfully.")
    else:
        typer.echo(f"Failed to delete file: {response.text}")

# List files in the "cloud" storage
@app.command()
def list():
    """List all files in cloud storage"""
    if NOSERVER:
        typer.echo("Listing files.")
        return

    headers = get_auth_headers()

    response = requests.get(f"{SERVER}/file/list", headers=headers)
    if response.ok:
        files = response.json()
        if files:
            typer.echo("Files in cloud storage:")
            typer.echo("-" * 80)
            typer.echo(f"{'ID':<5} | {'Name':<30} | {'Size':<10} | {'Uploaded'}")
            typer.echo("-" * 80)
            for file in files:
                file_id = file.get('id', 'N/A')
                name = file.get('name', 'Unknown')
                size = file.get('size', 0)
                timestamp = file.get('timestamp', 'Unknown')
                
                # Format size
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                
                typer.echo(f"{file_id:<5} | {name:<30} | {size_str:<10} | {timestamp}")
        else:
            typer.echo("No files found in cloud storage.")
    else:
        typer.echo(f"Failed to list files: {response.text}")