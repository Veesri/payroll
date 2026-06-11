import sqlite3

def migrate():
    print("Starting users migration...")
    conn = sqlite3.connect('instance/hrms.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0")
        print("Migration successful: Added is_approved column to users table.")
    except sqlite3.OperationalError as e:
        print(f"Migration error (column might already exist): {e}")
        
    # Update existing users to be approved
    cursor.execute("UPDATE users SET is_approved = 1")
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
