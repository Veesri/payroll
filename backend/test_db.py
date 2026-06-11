import pymysql

try:
    connection = pymysql.connect(host='127.0.0.1', user='root', password='')
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS hrms_db")
    print("Database created or already exists.")
except Exception as e:
    print(f"Error: {e}")
