
import typer
import auth
import files
import admin

# Create a Typer app instance
app = typer.Typer()

# Define the commands for the app
app.command()(auth.register)
app.command()(auth.login)
app.command()(auth.logout)

app.command()(files.upload)
app.command()(files.download)
app.command()(files.delete)
app.command()(files.list)

app.command()(admin.list_users)
app.command()(admin.delete_user)

def main():
    app()

if __name__ == "__main__":
    main()    