import pymysql
from pymysql.cursors import DictCursor 

from .universal_connection import connect

def get_student(username, password):
    con = connect()
    cursor = con.cursor()

    try: 
        cursor.execute("Select * from students where email = %s and password = %s", (username, password))
        student_data = cursor.fetchall()
        if(student_data.count == 0):
            return False
        return student_data
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

def get_students():
    con = connect()
    cursor = con.cursor()

    try: 
        cursor.execute("Select * from students")
        student_data = cursor.fetchall()
        if(student_data.count == 0):
            return False
        return student_data
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()