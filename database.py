import sqlite3

def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USER (
        user_id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS EXPENSES (
        user_id TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES USER (user_id),
        CONSTRAINT expenses_category CHECK (category IN ('food', 'entertainment', 'transport', 'academics', 'other'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS INCOME (
        user_id TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES USER (user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
        sno INTEGER NOT NULL,
        password TEXT NOT NULL
        )
    ''')