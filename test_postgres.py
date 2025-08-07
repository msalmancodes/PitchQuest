from pitchquest_api.database import engine
from sqlalchemy import text

# test connection

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            print("postgres is connected")
            print(f'Database version: {result.fetchone()[0]}')
    except Exception as e:
        print(f"Error connecting to postgres: {e}")

if __name__ == "__main__":
    test_connection()