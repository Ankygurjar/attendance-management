import pymysql
import os
from werkzeug.utils import secure_filename

from database.admin_db_service import get_admin, add_teacher

UPLOAD_FOLDER = os.path.join('static', 'teacher_photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def login_admin_service(username: str, password: str):
    if(username != '' and password != ''):
        return get_admin(username, password)
    
    return tuple()

def add_teacher_service(name, password, email, phone, subject, photo):
    if not all([name, password, email, photo]):
        return False
    filename = f"{name}__{secure_filename(photo.filename)}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    photo.save(filepath)
    
    return add_teacher(name, password, email, phone, subject, filename)