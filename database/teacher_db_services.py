import pymysql
from pymysql.cursors import DictCursor 

from .universal_connection import connect

def get_teacher(username: str, password: str):
    con = connect()
    cursor = con.cursor()

    try: 
        cursor.execute("Select * from teacher where email = %s and password = %s", (username, password))
        teacher_data = cursor.fetchall()
        if(teacher_data.count == 0):
             return False
        return teacher_data
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

def get_all_teachers_db():
    con = connect()
    cursor = con.cursor()

    try: 
        cursor.execute("Select * from teacher")
        teacher_data = cursor.fetchall()
        if(teacher_data.count == 0):
             return False
        return teacher_data
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

def add_student_db(name, password, email, phone, roll_number, classname, photo):
    con = connect()
    cursor = con.cursor()

    try:
        print(name, password, email, phone, roll_number, classname, photo)
        cursor.execute(
            "INSERT INTO students(name, password, email, phone_number, roll_number, classname, image_path) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s)", 
            (name, password, email, phone, roll_number, classname, photo)
        )
        con.commit()
        return True
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()