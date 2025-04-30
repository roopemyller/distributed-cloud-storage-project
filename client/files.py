import typer
import requests
import os
from datetime import datetime
from utils import load_token
from tqdm import tqdm

app = typer.Typer()
SERVER = "http://localhost:8000" # Replace with REAL server URL
TOKEN_FILE = ".token"

def get_auth_headers():
    token = load_token()
    if not token:
        typer.echo("No token found. Please log in first.")
        raise typer.Exit()
    return {"Authorization": f"Bearer {token}"}

# Upload file to the "cloud" storage
@app.command()
def upload(
    file_path: str, 
    save_name: str=typer.Option(
        None, 
        "--save-name", 
        "-s", 
        help="Name to save the file as in the cloud. Default is the original file name."
        )
    ):
    
    """
    Upload a file to cloud storage
    """
     
    if not os.path.exists(file_path):
        typer.echo(f"File {file_path} does not exist.")
        raise typer.Exit()
    
    headers = get_auth_headers()
    final_name = save_name if save_name else os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as f, tqdm(
        total=file_size, unit="B", unit_scale=True, desc=f"Uploading {final_name}",
    ) as progress:
        
        chunks = []
        for chunk in iter(lambda: f.read(8192), b""):
            progress.update(len(chunk))
            chunks.append(chunk)

        file_content = b"".join(chunks)
        
        files = {"file": (final_name, file_content, "application/octet-stream")}
        response = requests.post(f"{SERVER}/files/upload", files=files, headers=headers)

    if response.ok:
        typer.echo(f"File uploaded successfully as '{final_name}'.")
    else:
        typer.echo(f"Failed to upload file: {response.text}")

# Download file from the "cloud" storage
@app.command()
def download(
    file_name: str, 
    save_path: str=typer.Option(
        ".", 
        "--save-path", 
        "-p", 
        help="Path to save the downloaded file."
        )
    ):
    
    """
    Download a file from cloud storage
    """
    
    if not os.path.exists(save_path):
        typer.echo(f"Path {save_path} does not exist.")
        raise typer.Exit()

    headers = get_auth_headers()
    params = {"file_name": file_name}
    response = requests.get(f"{SERVER}/files/download", params=params, headers=headers, stream=True)

    if response.ok:
        file_save_path = os.path.join(save_path, file_name)
        total_size = int(response.headers.get("Content-Length", 0))

        with open(file_save_path, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, desc=f"Downloading {file_name}",
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(len(chunk))

        typer.echo(f"File downloaded successfully to {file_save_path}.")
    else:
        typer.echo(f"Failed to download file: {response.text}")

# Delete file from the "cloud" storage
@app.command()
def delete(
    file_id: int,
    admin: bool=typer.Option(
        False,
        "--admin",
        "-a",
        help="Delete file as admin (admin only)."
        )
    ):
    
    """
    Delete a file from cloud storage

    Admin can delete any file with tag --admin or -a
    User can delete only their own files
    """

    headers = get_auth_headers()
    params = {"file_id": file_id}  
 
    if admin:
        # Admin delete
        response = requests.delete(f"{SERVER}/admin/files/{file_id}", headers=headers)
    else:
        response = requests.delete(f"{SERVER}/files/{file_id}", headers=headers)

    if response.ok:
        typer.echo(f"File with file_id {file_id} deleted successfully.")
    elif response.status_code == 403:
        typer.echo("Permission denied. You can only delete your own files.")
    elif response.status_code == 404:
        typer.echo(f"File with file_id {file_id} not found.")
    else:
        typer.echo(f"Failed to delete file: {response.text}")

# List files in the "cloud" storage
@app.command()
def list(
    admin: bool=typer.Option(
        False, 
        "--admin", 
        "-a", 
        help="List all files (admin only)."
        )
    ):
    
    """
    List all files in cloud storage

    Admin can view all files with tag --admin or -a
    User can view only their own files
    """

    headers = get_auth_headers()

    if admin:
        # Admin view
        response = requests.get(f"{SERVER}/admin/files", headers=headers)
        if response.ok:
            files = response.json()
            if files:
                typer.echo("Files in cloud storage:")
                typer.echo("-" * 80)
                typer.echo(f"{'ID':<5} | {'Owner':<10} | {'Name':<30} | {'Size':<10} | {'Uploaded'}")
                typer.echo("-" * 80)
                for file in files:
                    file_id = file.get('id', 'N/A')
                    file_owner = file.get('owner_username', 'Unknown')
                    name = file.get('name', 'Unknown')
                    size = file.get('size', 0)
                    timestamp = file.get('timestamp', 'Unknown')
                    
                    try:
                        timestamp_dt = datetime.fromisoformat(timestamp)
                        timestamp_str = timestamp_dt.strftime("%d.%m.%Y %H:%M:%S")
                    except ValueError:
                        timestamp_str = "Invalid timestamp"

                    # Format size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    
                    typer.echo(f"{file_id:<5} | {file_owner:<10} | {name:<30} | {size_str:<10} | {timestamp_str}")
            else:
                typer.echo("No files found in cloud storage.")
        else:
            typer.echo(f"Failed to list files: {response.text}")
    else:
        # User view
        response = requests.get(f"{SERVER}/files/list", headers=headers)
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
                    
                    try:
                        timestamp_dt = datetime.fromisoformat(timestamp)
                        timestamp_str = timestamp_dt.strftime("%d.%m.%Y %H:%M:%S")
                    except ValueError:
                        timestamp_str = "Invalid timestamp"

                    # Format size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    
                    typer.echo(f"{file_id:<5} | {name:<30} | {size_str:<10} | {timestamp_str}")
            else:
                typer.echo("No files found in cloud storage.")
        else:
            typer.echo(f"Failed to list files: {response.text}")