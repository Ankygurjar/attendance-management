import pymysql
import os

from database.student_db_service import get_student, get_students

def login_student_service(username: str, password: str):
    if(username != '' and password != ''):
        return get_student(username, password)
    
    return tuple()

def get_all_students():
    return get_students()