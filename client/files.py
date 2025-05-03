import typer
import requests
import os
import threading
import sys
from datetime import datetime
from utils import load_token
from tqdm import tqdm

app = typer.Typer()
SERVER = "http://localhost:8000"
TOKEN_FILE = ".token"

def get_auth_headers():
    """
    Function to get the authentication headers for API requests.

    This function retrieves the token from a local file and constructs the headers
    for the requests.
    """

    token = load_token()
    if not token:
        typer.echo("No token found. Please log in first.")
        raise typer.Exit()
    return {"Authorization": f"Bearer {token}"}

def upload_file(file_path: str, save_name: str):
    """ 
    Function to upload a file to the server    

    This function reads the file in chunks and uploads it to the server.
    It uses the tqdm library to show a progress bar during the upload process.
    The file is uploaded as a multipart/form-data request.
    """
    
    # Check if the file exists
    if not os.path.exists(file_path):
        typer.echo(f"File {file_path} does not exist.")
        raise typer.Exit()
    
    # Construct the headers for the request, and get the file size
    # and the final name to save the file as
    headers = get_auth_headers()
    final_name = save_name if save_name else os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Read the file in chunks and upload it to the server
    # Use tqdm to show a progress bar during the upload process
    with open(file_path, "rb") as f, tqdm(
        total=file_size, unit="B", unit_scale=True, desc=f"Uploading {final_name}",
    ) as progress:
        chunks = []
        for chunk in iter(lambda: f.read(8192), b""):
            progress.update(len(chunk))
            chunks.append(chunk)

        # Join the chunks into a single byte string
        # and send the request to the server
        file_content = b"".join(chunks)
        files = {"file": (final_name, file_content, "application/octet-stream")}
        response = requests.post(f"{SERVER}/files/upload", files=files, headers=headers)

    # Check the response from the server
    if response.ok:
        typer.echo(f"File uploaded successfully as '{final_name}'.")
    elif response.status_code == 500: # Server error
        error_message = response.json().get("detail", "Unknown error")
        if "401" in error_message:  # user not logged in
            typer.echo("Authentication failed. Please log in again.")
        else: # Other errors
            typer.echo(f"Failed to upload file: {error_message}")
    else:
        typer.echo(f"Failed to upload file: {response.text}")

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

    Threading is used to allow the user to continue using the CLI while the file is uploading.
    """

    # start a new thread to upload the file
    thread = threading.Thread(target=upload_file, args=(file_path, save_name))
    thread.start()
    
def download_file(file_name: str, save_path: str):
    """
    Function to download a file from the server

    This function retrieves the file from the server and saves it to the specified path.
    It uses the tqdm library to show a progress bar during the download process.
    """

    # Check if the save path exists
    if not os.path.exists(save_path):
        typer.echo(f"Path {save_path} does not exist.")
        raise typer.Exit()

    # Construct the headers for the request
    # and send the request to the server
    headers = get_auth_headers()
    params = {"file_name": file_name}
    response = requests.get(f"{SERVER}/files/download", params=params, headers=headers, stream=True)

    if response.ok: # File downloaded successfully
        # Save the file to the specified path
        file_save_path = os.path.join(save_path, file_name)
        total_size = int(response.headers.get("Content-Length", 0))
        # Use tqdm to show a progress bar during the download process
        with open(file_save_path, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, desc=f"Downloading {file_name}",
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(len(chunk))
        typer.echo(f"File downloaded successfully to {file_save_path}.")
    elif response.status_code == 500: # Server error
        error_message = response.json().get("detail", "Unknown error")
        if "401" in error_message: # user not logged in
            typer.echo("Authentication failed. Please log in again.")
        else: # Other errors
            typer.echo(f"Failed to upload file: {error_message}")
    else:
        typer.echo(f"Failed to download file: {response.text}")

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

    Threading is used to allow the user to continue using the CLI while the file is downloading.
    """

    # start a new thread to download the file
    thread = threading.Thread(target=download_file, args=(file_name, save_path))
    thread.start()

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

    #  Construct the headers for the request
    headers = get_auth_headers()
 
    # Check if the user is admin or not
    # If admin is True, delete the file as admin
    # Otherwise, delete the file as a regular user
    if admin:
        # Admin delete
        response = requests.delete(f"{SERVER}/admin/files/{file_id}", headers=headers)
    else:
        # User delete
        response = requests.delete(f"{SERVER}/files/{file_id}", headers=headers)

    if response.ok:
        typer.echo(f"File with file_id {file_id} deleted successfully.")
    elif response.status_code == 500: # Server error
        error_message = response.json().get("detail", "Unknown error")
        if "401" in error_message: # user not logged in
            typer.echo("Authentication failed. Please log in again.")
        else:  # Other errors
            typer.echo(f"Failed to delete file: {error_message}")
    elif response.status_code == 403: # Permission denied
        typer.echo("Permission denied. You can only delete your own files.")
    elif response.status_code == 404: # File not found
        typer.echo(f"File with file_id {file_id} not found.")
    else:
        typer.echo(f"Failed to delete file: {response.text}")

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
    # Construct the headers for the request
    headers = get_auth_headers()

    # Check if the user is admin or not
    # If admin is True, list all files as admin
    # Otherwise, list the files as a regular user
    if admin:
        # Admin view
        # Make a request to the server to list all files
        response = requests.get(f"{SERVER}/admin/files", headers=headers)
        if response.ok:
            # Parse the JSON response and display the file information
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
                    
                    # Convert timestamp to datetime object and format it
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
                    # Display file information
                    typer.echo(f"{file_id:<5} | {file_owner:<10} | {name:<30} | {size_str:<10} | {timestamp_str}")
            else:
                typer.echo("No files found in cloud storage.")
        elif response.status_code == 401: # User not logged in
            typer.echo("Authentication failed. Please log in again.")   
        else:
            typer.echo(f"Failed to list files: {response.text}")
    else:
        # User view
        # Make a request to the server to list the files
        response = requests.get(f"{SERVER}/files/list", headers=headers)
        if response.ok:
            # Parse the JSON response and display the file information
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
                    
                    # Convert timestamp to datetime object and format it
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
                    # Display file information
                    typer.echo(f"{file_id:<5} | {name:<30} | {size_str:<10} | {timestamp_str}")
            else:
                typer.echo("No files found in cloud storage.")
        elif response.status_code == 401: # User not logged in
            typer.echo("Authentication failed. Please log in again.")
        else:
            typer.echo(f"Failed to list files: {response.text}")