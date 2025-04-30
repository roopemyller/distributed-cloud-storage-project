
import typer
import auth
import file
import admin

app = typer.Typer()

app.command()(auth.register)
app.command()(auth.login)
app.command()(auth.logout)

app.command()(file.upload)
app.command()(file.download)
app.command()(file.delete)
app.command()(file.list)

app.command()(admin.list_users)
app.command()(admin.delete_user)

def main():
    app()

if __name__ == "__main__":
    main()    