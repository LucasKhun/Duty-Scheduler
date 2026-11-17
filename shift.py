"""
This module defines the Shift class, which represents a work shift
with a specific date and staffing requirements.
"""
import datetime
import sqlite3

class ShiftManager:
    """
    Manages work shifts within a specified date range.
    """

    def __init__(self, conn: sqlite3.Connection, start_date: datetime.date, end_date: datetime.date):
        """
        Initializes the ShiftManager with a start and end date for the shifts.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.conn = conn
        
        for date in self._generate_dates():
            shift_type = self.determine_shift_type(date)
            self.insert_shift(date, shift_type)

    def _generate_dates(self):
        """
        Generates a list of dates between the start and end date.
        """
        current_date = self.start_date
        while current_date <= self.end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)

    @staticmethod
    def determine_shift_type(date: datetime.date) -> str:
        """
        Determines the type of shift based on the day of the week.
        Weekdays (Sunday to Thursday) are considered 'Normal',
        while weekends (Friday and Saturday) are considered '24-hour'.
        """
        if date.weekday() < 4 or date.weekday() == 6:  # Sunday to Thursday
            return "Normal"
        # Friday and Saturday
        return "24-hour"

    def insert_shift(self, date: datetime.date, shift_type: str):
        """
        Inserts a shift into the database with the given date and shift type.
        This method should be implemented to interact with the database.
        """
        self.conn.execute("INSERT INTO Shift (date, shift_type) VALUES (?, ?)", (date, shift_type))

    def get_shift(self, date: datetime.date):
        """
        Retrieves a shift from the database based on the given date.
        This method should be implemented to interact with the database.
        """
        cursor = self.conn.execute("SELECT id FROM Shift WHERE date = ?", (date,))
        return cursor.fetchone()

    def assign_shift(self, date: datetime.date, staff_id: int):
        """
        Assigns a staff member to a shift with a specific role.
        This method should be implemented to interact with the database.
        """
        shift = self.get_shift(date)
        if not shift:
            raise ValueError(f"No shift found for date {date}")

        self.conn.execute(
            "INSERT INTO StaffShiftAuto (shift_id, staff_id) VALUES (?, ?)",
            (shift[0], staff_id)  # Assuming the first column is the shift_id
        )