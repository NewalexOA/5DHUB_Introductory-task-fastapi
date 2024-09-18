
# URL Shortener API with FastAPI and SQLAlchemy

This project is a simple URL shortener API built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/) for handling the database. The application supports shortening URLs, redirecting to original URLs, and uses an SQLite database by default (with easy switching to PostgreSQL).

## Features

- Shorten a given URL and generate a unique short URL.
- Redirect users to the original URL when they access the shortened URL.
- Database support with SQLAlchemy (default is SQLite, easily configurable for PostgreSQL).
- Fully asynchronous with FastAPI for high performance.

## Prerequisites

- Python 3.10+
- Git
- Virtual environment (optional but recommended)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/NewalexOA/5DHUB_Introductory-task-fastapi.git
   cd 5DHUB_Introductory-task-fastapi
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   .\venv\Scripts\activate   # For Windows
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

By default, the project uses SQLite as the database. If you want to switch to PostgreSQL or any other database, you can update the `DATABASE_URL` environment variable.

1. **Environment variables**:

   You can set up the following environment variables:

   ```bash
   export DATABASE_URL="sqlite:///./urls.db"     # Default SQLite configuration
   export BASE_URL="http://127.0.0.1:8080"       # Base URL for the shortened links
   ```

   For PostgreSQL:

   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/dbname"
   ```

2. **Database migration** (optional):

   To manage migrations (if needed), consider using [Alembic](https://alembic.sqlalchemy.org/en/latest/). This is especially useful if you're planning to extend the schema in the future.

## Running the Application

1. **Run the development server**:

   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
   ```

2. **Access the API**:

   - The API will be available at: `http://127.0.0.1:8080`
   - Interactive documentation (Swagger UI): `http://127.0.0.1:8080/docs`
   - Alternative documentation (ReDoc): `http://127.0.0.1:8080/redoc`

## API Endpoints

### 1. Shorten URL (POST `/`)

- **Request**:

   ```json
   {
     "url": "https://example.com"
   }
   ```

- **Response**:

   ```json
   {
     "short_url": "http://127.0.0.1:8080/abc123"
   }
   ```

### 2. Redirect to Original URL (GET `/{short_id}`)

- Access the shortened URL:

    ```bash
    http://127.0.0.1:8080/{short_id}
    ```

- **Response**: The user is redirected to the original URL with a `307 Temporary Redirect` status.

## Customization

### Switching to PostgreSQL or another database

1. Update your `.env` file or set the `DATABASE_URL` environment variable with your database connection string.
2. Ensure that the correct database driver (e.g., `psycopg2-binary` for PostgreSQL) is installed and listed in `requirements.txt`.

### Deploying to Production

1. Replace the development server (`uvicorn --reload`) with a production-ready ASGI server, such as `uvicorn` or `gunicorn`, and remove the `--reload` flag.
2. Ensure proper database management and scaling depending on your production environment.

## Testing

To test the API endpoints, you can use tools like [Postman](https://www.postman.com/) or [httpie](https://httpie.io/).

Example of testing with `curl`:

```bash
curl -X POST "http://127.0.0.1:8080/" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions

Feel free to fork this repository, make changes, and submit pull requests. All contributions are welcome!
