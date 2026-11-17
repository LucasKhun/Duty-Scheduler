"""
This module defines the database models for the shift scheduling application.
"""


class Models:
    """
    This class contains the database schema definitions for the shift
    scheduling application. It defines the tables and triggers necessary
    for managing shifts, roles, staff, and their assignments.
    """
    # Database schema definitions
    shift = """
    CREATE TABLE IF NOT EXISTS Shift (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        shift_type TEXT NOT NULL
    );
    """

    role = """
    CREATE TABLE IF NOT EXISTS Role (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    """

    shift_role = """
    CREATE TABLE IF NOT EXISTS ShiftRole (
        shift_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        max_count INTEGER NOT NULL,
        PRIMARY KEY (shift_id, role_id),
        FOREIGN KEY (shift_id) REFERENCES Shift(id),
        FOREIGN KEY (role_id) REFERENCES Role(id)
    );
    """

    staff = """
    CREATE TABLE IF NOT EXISTS Staff (
        email TEXT PRIMARY KEY,
        name TEXT NOT NULL
    );
    """

    staff_shift = """
    CREATE TABLE IF NOT EXISTS StaffShift (
        shift_id INTEGER NOT NULL,
        staff_email TEXT NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (shift_id, staff_email),
        FOREIGN KEY (shift_id) REFERENCES Shift(id),
        FOREIGN KEY (staff_email) REFERENCES Staff(email),
        FOREIGN KEY (role_id) REFERENCES ShiftRole(role_id)
    );
    """
    staff_shift_auto_view = """
    CREATE VIEW IF NOT EXISTS StaffShiftAuto AS
    SELECT shift_id, staff_email FROM StaffShift;
    """

    staff_shift_auto_trigger = """
    CREATE TRIGGER IF NOT EXISTS trg_staffshiftauto_insert
    INSTEAD OF INSERT ON StaffShiftAuto
    BEGIN
        SELECT RAISE(ABORT, 'No open role for this shift')
        WHERE NOT EXISTS (
            SELECT 1 FROM ShiftRole sr
            WHERE sr.shift_id = NEW.shift_id
            AND (SELECT COUNT(*) FROM StaffShift ss
                WHERE ss.shift_id = sr.shift_id AND ss.role_id = sr.role_id) < sr.max_count
        );

        INSERT INTO StaffShift (shift_id, staff_email, role_id)
        SELECT sr.shift_id, NEW.staff_email, sr.role_id
        FROM ShiftRole sr
        WHERE sr.shift_id = NEW.shift_id
        AND (SELECT COUNT(*) FROM StaffShift ss
            WHERE ss.shift_id = sr.shift_id AND ss.role_id = sr.role_id) < sr.max_count
        ORDER BY sr.role_id ASC
        LIMIT 1;
    END;
    """

    # Block inserts that would exceed the role's max_count for that shift
    staff_shift_insert_trigger = """
    CREATE TRIGGER IF NOT EXISTS trg_staffshift_insert_role_capacity
    BEFORE INSERT ON StaffShift
    BEGIN
        SELECT RAISE(ABORT, 'Role is already at max_count for this shift')
        WHERE (SELECT COUNT(*) FROM StaffShift
            WHERE shift_id = NEW.shift_id AND role_id = NEW.role_id)
            >= (SELECT max_count FROM ShiftRole
                WHERE shift_id = NEW.shift_id AND role_id = NEW.role_id);
    END;
    """

    # Block moving an assignment into a (shift, role) that is already full
    staff_shift_update_trigger = """
    CREATE TRIGGER IF NOT EXISTS trg_staffshift_update_role_capacity
    BEFORE UPDATE OF shift_id, role_id ON StaffShift
    WHEN NEW.shift_id <> OLD.shift_id OR NEW.role_id <> OLD.role_id
    BEGIN
        SELECT RAISE(ABORT, 'Role is already at max_count for this shift')
        WHERE (SELECT COUNT(*) FROM StaffShift
            WHERE shift_id = NEW.shift_id AND role_id = NEW.role_id)
            >= (SELECT max_count FROM ShiftRole
                WHERE shift_id = NEW.shift_id AND role_id = NEW.role_id);
    END;
    """

    # Block lowering max_count below the number already assigned
    shift_role_update_trigger = """
    CREATE TRIGGER IF NOT EXISTS trg_shiftrole_max_count_update
    BEFORE UPDATE OF max_count ON ShiftRole
    BEGIN
        SELECT RAISE(ABORT, 'max_count is less than the number of staff already in this role')
        WHERE NEW.max_count < (SELECT COUNT(*) FROM StaffShift
                            WHERE shift_id = NEW.shift_id AND role_id = NEW.role_id);
    END;
    """
