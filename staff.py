import sqlite3

class StaffManager:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_staff(self, email: str, name: str):
        """
        Adds a new staff member to the database.
        """
        self.conn.execute("INSERT INTO Staff (email, name) VALUES (?, ?)", (email, name))

    def get_staff(self, email: str):
        """
        Retrieves a staff member's details from the database based on their email.
        """
        cursor = self.conn.execute("SELECT * FROM Staff WHERE email = ?", (email,))
        return cursor.fetchone()
