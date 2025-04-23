# Alembic Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for managing SQLAlchemy database migrations.

## Setup

1. Install dependencies:
   ```
   pip install alembic python-dotenv
   ```

2. Create a `.env` file with your database URL:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

3. Initialize Alembic (only once):
   ```
   alembic init alembic
   ```

4. Update `alembic/env.py` to read from `.env`:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()
   config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
   ```

## Usage

- Generate a migration:
  ```
  alembic revision -m "your message" --autogenerate
  ```

- Apply migrations:
  ```
  alembic upgrade head
  ```

- Downgrade:
  ```
  alembic downgrade -1
  ```

## Notes

- Do **not** commit your `.env` file.
- The `alembic.ini` file does not contain the DB URL directly; it's set dynamically via `env.py`.
