import pymysql
import os
from werkzeug.utils import secure_filename

from database.teacher_db_services import get_teacher, get_all_teachers_db, add_student_db

UPLOAD_FOLDER = os.path.join('static', 'student_photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def login_teacher_service(username: str, password: str):
    if(username != '' and password != ''):
        return get_teacher(username, password)
    
    return tuple()

def get_all_teachers():
    return get_all_teachers_db()

def add_student_service(name, password, email, phone, roll_number, classname, photo):
    if not all([name, password, email, photo]):
        return False
    filename = f"{name}__{secure_filename(photo.filename)}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    photo.save(filepath)

    return add_student_db(name, password, email, phone, roll_number, classname, filename)