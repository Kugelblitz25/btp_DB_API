# People Tracking API

## Overview

The People Tracking API allows users to manage and track information about individuals. It provides endpoints for creating, retrieving, updating, and deleting records of people, including their name, age, and location. This API is built using Python, FastAPI, and PostgreSQL.

## Project Setup

### Dependencies

* Python 3.8+
* FastAPI
* SQLModel (for SQLAlchemy and Pydantic integration)
* Uvicorn (ASGI server)
* psycopg2-binary (for PostgreSQL connection)
* python-dotenv (for environment variable management)
* asyncpg (for FastAPI's async database access with PostgreSQL)


To install the dependencies, run:

```bash
pip install -r requirements.txt
```

### Environment Variables

* `DATABASE_URL`: URL for connecting to the PostgreSQL database. Example: `postgresql+asyncpg://user:password@host:port/database_name` (Note: `+asyncpg` for async)
* `SECRET_KEY`: Secret key for JWT tokens or other security features (if applicable, though not explicitly used in current basic setup).

(Note: `FLASK_APP` and `FLASK_ENV` are not typically used by FastAPI/Uvicorn directly. Uvicorn runs the app specified in its command.)

### Database Setup

1. Ensure you have PostgreSQL installed and running.
2. Create a new database:
   ```bash
   createdb people_tracking_db  # Or your preferred database name
   ```
3. Database tables are created automatically on application startup due to the `create_db_and_tables` function called in the `startup` event in `main.py`. If you are using a migration tool like Alembic (recommended for production), the steps would be different:
   ```bash
   # Example with Alembic (if it were set up)
   # alembic revision -m "create_initial_tables"
   # alembic upgrade head
   ```
   For the current project, manual migration commands are not needed as SQLModel handles table creation.

## Running the Application

1. Set the required environment variables. For example:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost/people_tracking_db"
   # export SECRET_KEY="your_actual_secret_key_if_needed" 
   ```
   You can also place these in a `.env` file in the project root, and they will be loaded by `python-dotenv`. Example `.env` file:
   ```
   DATABASE_URL="postgresql+asyncpg://your_user:your_password@localhost:5432/people_tracking_db"
   ```

2. Start the FastAPI development server using Uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The application will be accessible at `http://0.0.0.0:8000/` or `http://127.0.0.1:8000/`. The `/docs` endpoint provides interactive API documentation.

## API Endpoints

### Endpoint 1: Get all people

* **Description:** Retrieves a list of all people in the database.
* **Request:**
  * Method: `GET`
  * URL: `/people`
  * Headers:
    * `Content-Type: application/json`
  * Body: None
* **Response:**
  * Status Code: `200 OK`
  * Body:
    ```json
    [
      {
        "id": 1,
        "name": "John Doe",
        "age": 30,
        "location": "New York"
      },
      {
        "id": 2,
        "name": "Jane Smith",
        "age": 25,
        "location": "London"
      }
      // ... more people
    ]
    ```
  * Status Code: `204 No Content` (if no people are found)
  * Body: Empty

### Endpoint 2: Get a specific person by ID

* **Description:** Retrieves details of a specific person by their ID.
* **Request:**
  * Method: `GET`
  * URL: `/persons/{person_id}` (assuming your router uses this path based on typical FastAPI/SQLModel examples)
  * Headers:
    * `Content-Type: application/json`
  * Body: None
* **Response:**
  * Status Code: `200 OK`
  * Body:
    ```json
      {
        "id": 1,
        "name": "John Doe",
        "age": 30,
        "location": "New York"
      }
    ```
  * Status Code: `404 Not Found` (if person with the given ID does not exist)
  * Body:
    ```json
    {
      "error": "Person not found"
    }
    ```

### Endpoint 3: Create a new person

* **Description:** Adds a new person to the database.
* **Request:**
  * Method: `POST`
  * URL: `/persons`
  * Headers:
    * `Content-Type: application/json`
  * Body:
    ```json
    {
      "name": "Peter Jones",
      "age": 40,
      "location": "Paris"
    }
    ```
* **Response:**
  * Status Code: `201 Created`
  * Body:
    ```json
    {
      "id": 3, // ID assigned by the database
      "name": "Peter Jones",
      "age": 40,
      "location": "Paris"
    }
    ```
  * Status Code: `400 Bad Request` (if request body is invalid or missing fields)
  * Body:
    ```json
    {
      "error": "Invalid input",
      "details": {
        "name": ["Missing data for required field."]
      }
    }
    ```

### Endpoint 4: Update an existing person

* **Description:** Updates details of an existing person by their ID.
* **Request:**
  * Method: `PUT`
  * URL: `/persons/{person_id}`
  * URL: `/persons/{person_id}`
  * Headers:
    * `Content-Type: application/json`
  * Body:
    ```json
    {
      "name": "Peter Jones Updated",
      "age": 41,
      "location": "Paris"
    }
    ```
* **Response:**
  * Status Code: `200 OK`
  * Body:
    ```json
    {
      "id": 3,
      "name": "Peter Jones Updated",
      "age": 41,
      "location": "Paris"
    }
    ```
  * Status Code: `404 Not Found` (if person with the given ID does not exist)
  * Body:
    ```json
    {
      "error": "Person not found"
    }
    ```
  * Status Code: `400 Bad Request` (if request body is invalid)
  * Body:
    ```json
    {
      "error": "Invalid input"
    }
    ```

### Endpoint 5: Delete a person

* **Description:** Deletes a person from the database by their ID.
* **Request:**
  * Method: `DELETE`
  * URL: `/people/<int:person_id>`
  * Headers:
    * `Content-Type: application/json`
  * Body: None
* **Response:**
  * Status Code: `200 OK`
  * Body:
    ```json
    {
      "message": "Person deleted successfully"
    }
    ```
  * Status Code: `404 Not Found` (if person with the given ID does not exist)
  * Body:
    ```json
    {
      "error": "Person not found"
    }
    ```

## Running Tests

Tests are typically run using a test runner like `pytest`.

1. Ensure you have `pytest` and other development dependencies installed (see `pyproject.toml`'s `[tool.poetry.group.dev.dependencies]`):
   ```bash
   # If using poetry
   poetry install --with dev
   # Or if using pip with a requirements-dev.txt
   # pip install -r requirements-dev.txt 
   ```
2. Navigate to the project root directory.
3. Run the tests using `pytest` (preferably via Poetry if you used Poetry for setup):
   ```bash
   # If using poetry
   poetry run pytest -v
   # Or directly if pytest is in your PATH and using the correct environment
   # pytest -v
   ```

The tests are located in the `tests/` directory and include model validation tests (`test_models.py`) and API endpoint integration tests (`test_api.py`). The API tests use an in-memory SQLite database.

---

*This README provides a comprehensive guide for the People Tracking API. Ensure all paths, commands, and examples are accurate for your specific project implementation.*
