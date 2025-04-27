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
def upload(file_path: str):
    if NOSERVER:
        typer.echo(f"Uploading file '{file_path}'.")
        return

    headers = get_auth_headers()

    if not os.path.exists(file_path):
        typer.echo(f"File {file_path} does not exist.")
        raise typer.Exit()

    files = {"file": open(file_path, "rb")}
    response = requests.post(f"{SERVER}/files/upload", files=files, headers=headers)
    if response.ok:
        typer.echo("File uploaded successfully.")
    else:
        typer.echo(f"Failed to upload file: {response.text}")

# Download file from the "cloud" storage
@app.command()
def download(file_name: str, save_path: str="."):
    if NOSERVER:
        typer.echo(f"Downloading file '{file_name}' to '{save_path}'.")
        return

    headers = get_auth_headers()

    params = {"file_name": file_name}
    response = requests.get(f"{SERVER}/files/download", params=params, headers=headers)
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
    response = requests.delete(f"{SERVER}/files/delete", params=params, headers=headers)
    if response.ok:
        typer.echo(f"File {file_name} deleted successfully.")
    else:
        typer.echo(f"Failed to delete file: {response.text}")

# List files in the "cloud" storage
@app.command()
def list():
    if NOSERVER:
        typer.echo("Listing files.")
        return

    headers = get_auth_headers()

    response = requests.get(f"{SERVER}/files/list", headers=headers)
    if response.ok:
        files = response.json()
        if files:
            typer.echo("Files in cloud storage:")
            for file in files:
                typer.echo(f"- {file}")
        else:
            typer.echo("No files found in cloud storage.")
    else:
        typer.echo(f"Failed to list files: {response.text}")