import sqlite3

def migrate():
    print("Starting migration...")
    conn = sqlite3.connect('instance/hrms.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE leaves ADD COLUMN requested_by_role VARCHAR(50) DEFAULT 'employee'")
        cursor.execute("ALTER TABLE leaves ADD COLUMN approval_level VARCHAR(50) DEFAULT 'hr_admin'")
        cursor.execute("ALTER TABLE leaves ADD COLUMN approved_by_role VARCHAR(50)")
        print("Migration successful: Added 3 new columns to leaves table.")
    except sqlite3.OperationalError as e:
        print(f"Migration error (columns might already exist): {e}")
        
    # Update existing records
    cursor.execute("UPDATE leaves SET requested_by_role = 'employee' WHERE requested_by_role IS NULL")
    cursor.execute("UPDATE leaves SET approval_level = 'hr_admin' WHERE approval_level IS NULL")
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
