
import typer
import auth
import file

app = typer.Typer()

app.command()(auth.register)
app.command()(auth.login)

app.command()(file.upload)
app.command()(file.download)
app.command()(file.delete)
app.command()(file.list)

def main():
    app()

if __name__ == "__main__":
    main()    