# Server with FastAPI and PostgreSQL

Start a new terminal from server directory and run the following commands in it

### Create .venv under the client

`python -m venv .venv`

### Activate venv

`source .venv/bin/activate`(Linux/MacOS)

or

`.venv\Scripts\activate`(Win)

### Install requirements

`pip install -r requirements.txt`

### .env

Create a `.env` file in the server directory, and then create fields for `SECRET_KEY`, `DATABASE_URL` and `ACCESS_TOKEN_EXPIRE_MINUTES`.

Example:
```
SECRET_KEY="1234"
DATABASE_URL="postgresql://myuser:mypassword@localhost/database"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
Replace fields "myuser", "mypassword" and "database" with the info from your local PostgreSQL.

### Run server with fastapi

After this is done, you can run `fastapi dev server.py`