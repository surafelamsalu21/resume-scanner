from app import create_app
from database.db import db
import os
import sqlite3

# Create app with development configuration
app = create_app('development')


def add_column_if_not_exists(table, column, column_type):
    """Add a column to a table if it doesn't exist."""
    try:
        conn = sqlite3.connect('instance/resume_ai.db')
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]

        if column not in columns:
            print(f"Adding column {column} to table {table}")
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
            conn.commit()
            print(f"Column {column} added successfully")
        else:
            print(f"Column {column} already exists in table {table}")

        conn.close()
        return True
    except Exception as e:
        print(f"Error adding column {column} to table {table}: {str(e)}")
        return False


def update_database_schema():
    """Update the database schema to match the current models."""
    try:
        # Add admin_feedback column to resume table
        add_column_if_not_exists('resume', 'admin_feedback', 'TEXT')

        # Add pdf_report_path column to resume table
        add_column_if_not_exists('resume', 'pdf_report_path', 'VARCHAR(512)')

        # Add category_id column to job_posting table
        add_column_if_not_exists(
            'job_posting', 'category_id', 'INTEGER REFERENCES job_category(id)')

        # Add job_category_id column to ai_prompt table
        add_column_if_not_exists(
            'ai_prompt', 'job_category_id', 'INTEGER REFERENCES job_category(id)')

        print("Database schema updated successfully")
        return True
    except Exception as e:
        print(f"Error updating database schema: {str(e)}")
        return False


if __name__ == "__main__":
    update_database_schema()
