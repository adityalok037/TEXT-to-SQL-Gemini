import sqlite3

# Function to create and initialize the database with the STUDENT table
def initialize_database(db_name):
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()

            # Create the STUDENT table if it does not exist
            table_info = """
            CREATE TABLE IF NOT EXISTS STUDENT (
                STUDENT_ID VARCHAR(10) PRIMARY KEY,
                NAME VARCHAR(25),
                CLASS VARCHAR(25),
                SECTION VARCHAR(25),
                MARKS INTEGER
            )
            """
            cursor.execute(table_info)
            conn.commit()
        
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Initialize the database
initialize_database("student.db")
