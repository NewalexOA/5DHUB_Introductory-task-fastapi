# URL Shortening Service Tests Documentation

This document outlines the tests implemented for the URL shortening service using FastAPI and pytest. Each test is designed to ensure the functionality of the application, covering the main features of the URL shortening process.

## Test Setup

The tests use a separate SQLite database (`test.db`) for isolation between test cases. The database is created and dropped for each test function using a fixture to maintain a clean state.

### Fixtures

- `client`: This fixture initializes the `AsyncClient` with the `app` instance, providing a testing client for making HTTP requests to the API.
- `setup_and_teardown`: This fixture creates the database tables before each test and drops them afterward. It also verifies that the tables exist in the database before running the tests.

## Test Cases

### 1. `test_create_short_url`

- **Description**: Tests the creation of a short URL.
- **Input**: A valid URL (`"https://example.com"`).
- **Expected Output**:
  - HTTP status code 201.
  - Response contains a `short_url` key.
  - The `short_url` should match the expected format, starting with the base URL and having a length of 8 characters for the short ID.

### 2. `test_redirect_to_original_url`

- **Description**: Tests redirection from a short URL to the original URL.
- **Input**: A valid URL (`"https://example.com"`), which is first shortened.
- **Expected Output**:
  - HTTP status code 307 for the redirection.
  - The `Location` header in the response should point to the original URL.

### 3. `test_database_entry_created`

- **Description**: Tests the direct creation of a database entry.
- **Input**: Directly adds a new URL entry with a known `short_id`.
- **Expected Output**:
  - The entry should be retrievable from the database, confirming that it was created correctly.

### 4. `test_database_entry_not_found`

- **Description**: Tests the scenario where a database entry is not found.
- **Input**: Queries the database for a non-existent `short_id`.
- **Expected Output**:
  - The query should return `None`, confirming that the entry does not exist.

### 5. `test_short_id_collision`

- **Description**: Tests the handling of short ID collisions by mocking the ID generation function.
- **Input**: Simulates two requests that could generate the same short ID using a fixed ID list.
- **Expected Output**:
  - Both requests should result in different short IDs being generated, ensuring unique entries.

### 6. `test_integrity_error_on_collision`

- **Description**: Tests handling of `IntegrityError` when a duplicate short ID is attempted to be added.
- **Input**: Attempts to add two URLs with the same generated short ID using a mocked function.
- **Expected Output**:
  - The application should handle the `IntegrityError` and generate a unique short ID for the subsequent request.

## New Test Cases

### 7. `test_redirect_nonexistent_url`

- **Description**: Tests redirection for a non-existent short URL.
- **Input**: A short URL that does not exist (`"/nonexistent"`).
- **Expected Output**:
  - HTTP status code 404.
  - Response contains a message indicating that the URL was not found.

### 8. `test_invalid_url_format`

- **Description**: Tests the handling of an invalid URL format.
- **Input**: An invalid URL (`"not_a_valid_url"`).
- **Expected Output**:
  - HTTP status code 422 indicating a validation error.

## Conclusion

These tests ensure that the URL shortening service operates as expected, handling both normal and edge cases. They cover the critical functionality of URL shortening and redirection, as well as error handling related to database integrity and URL validation. The fixtures ensure that each test runs in isolation with a clean state.
