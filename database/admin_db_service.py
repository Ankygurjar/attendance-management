import pymysql
from pymysql.cursors import DictCursor 

from .universal_connection import connect

def get_admin(username: str, password: str):
    con = connect()
    cursor = con.cursor()

    try: 
        cursor.execute("Select * from admin where email = %s and password = %s", (username, password))
        admin_data = cursor.fetchall()
        if(admin_data.count == 0):
             return False
        return admin_data
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

def add_teacher(name, password, email, phone, subject, photo_path):
    con = None
    cursor = None
    try:
        con = connect()
        cursor = con.cursor()
        
        cursor.execute(
            "INSERT INTO teacher(name, password, email, phone_number, subject, image_path) "
            "VALUES(%s, %s, %s, %s, %s, %s)", 
            (name, password, email, phone, subject, photo_path)
        )
        con.commit()
        return True
    except Exception as e:  # For other unexpected errors
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()
