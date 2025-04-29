# Server with FastAPI and PostgreSQL

To start, create a virtual environment while inside the server folder, activate it, and then run `pip install -r requirements.txt`

Create a `.env` file in the server directory, and then create fields for `SECRET_KEY` and `DATABASE_URL`
Example: `SECRET_KEY="1234"` and `DATABASE_URL=postgresql://myuser:mypassword@localhost/database`, and replace fields
"myuser", "mypassword" and "database" with the info from your local PostgreSQL.

After this is done, you can run `fastapi dev server.py`