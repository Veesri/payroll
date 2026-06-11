import sqlite3

def inspect():
    conn = sqlite3.connect('instance/hrms.db')
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall() if not t[0].startswith('sqlite_')]
    
    for table in tables:
        print(f"\n========================================")
        print(f" TABLE: {table}")
        print(f"========================================")
        
        # Get schema/columns
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        print(f" Columns: {', '.join(columns)}")
        
        # Get rows
        cursor.execute(f"SELECT * FROM {table};")
        rows = cursor.fetchall()
        print(f" Rows count: {len(rows)}")
        for row in rows:
            print(f"  {row}")
            
    conn.close()

if __name__ == '__main__':
    inspect()
