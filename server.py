from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import requests
from datetime import timedelta

from admin.admin_services import login_admin_service, add_teacher_service
from teacher.teacher_services import login_teacher_service, add_student_service, analyze_teacher_command
from student.student_services import login_student_service, get_all_students
from face_recognition_users.face_recognition_service import match_faces

app:str = Flask(__name__)
app.secret_key = 'e2B345CV23'
app.permanent_session_lifetime = timedelta(hours=1)  # Session lasts 1 hour


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout_user():
    if(session.get('admin_email') or session.get('teacher_email') or session.get('student_email')):
        session.clear()

        return redirect(url_for('home'))

#------- ADMIN ROUTES ------
@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == "POST":
        admin_data = login_admin_service(request.form["email"], request.form["password"])
        print(admin_data)
        if(admin_data.count != 0):
            session['admin_email'] = admin_data[0]['email']
            return render_template('admin/dashboard.html')
    
    return render_template('admin/login.html')

#-------- TEACHER ROUTES -----------
@app.route('/login_teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == "POST" and (request.form["email"] != '' and request.form["password"] != ''):
        teacher_data = login_teacher_service(request.form["email"], request.form["password"])
        if(teacher_data.count != 0):
            result = match_faces(teacher_data[0]['image_path'], 'teacher')
            if(result):
                session['teacher_email'] = teacher_data[0]['email']
                session['id'] = teacher_data[0]['id']
                session['image_path'] = teacher_data[0]['image_path']
                session['phone_number'] = teacher_data[0]['phone_number']
                session['subject'] = teacher_data[0]['subject']
                session['name'] = teacher_data[0]['name']
                return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/login.html')

@app.route('/teacher_dashboard', methods=['GET'])
def teacher_dashboard():
    if(session.get('teacher_email')):
        teacher_data = dict()
        teacher_data['teacher_email'] = session.get('teacher_email')
        teacher_data['id'] = session.get('id')
        teacher_data['image_path'] = session.get('image_path')
        teacher_data['phone_number'] = session.get('phone_number')
        teacher_data['subject'] = session.get('subject')
        teacher_data['name'] = session.get('name')

        return render_template('teacher/dashboard.html', teacher_data=teacher_data)

@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == "POST":
        add_teacher_service(request.form['name'], request.form['passowrd'], request.form['email'], request.form['phone'], request.form['subject'], request.files['photo'])
    
    return render_template('admin/add_teacher.html')

@app.route('/add_student_sentiment', methods=['GET', "POST"])
def student_sentiment():
    if request.method == 'POST':
        feedback = request.form['feedback']
        marks =request.form['marks']
        attendance = request.form['attendance']

        
        return render_template("teacher/student_sentiment.html")
    return render_template("teacher/student_sentiment.html")
    
@app.route('/chatbot', methods=['GET'])
def chatbot():
    if(session.get('teacher_email') or session.get('admin_email')):
        return render_template('chatbot.html')
    
    return redirect(url_for('logout'))

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    if not session.get('teacher_email'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    ai_response = analyze_teacher_command(
        message=data['message'],
        teacher_id=session.get('id')
    )
    
    student_data = session.get('chat_context', {}).get('student_data', {})
    
    if ai_response.get('action') == 'add_student':
        if all(k in student_data for k in ['name', 'email', 'roll_number']):
            return jsonify({
                'response': f"Ready to add {student_data['name']}. Confirm?",
                'needs_confirmation': True,
                'student_data': student_data
            })
    
    return jsonify(ai_response)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == "POST":
        print(request.form)
        add_student_service(request.form['name'], request.form['password'], request.form['email'], request.form['phone'], request.form['roll_number'], request.form['classname'], request.files['photo'])

        return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher/add_student.html')

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == "POST" and (request.form["email"] != '' and request.form["password"] != ''):
        student_data = login_student_service(request.form["email"], request.form["password"])
        if(student_data.count != 0):
            result = match_faces(student_data[0]['image_path'], 'student')
            if(result):
                session['student_email'] = student_data[0]['email']
                session['id'] = student_data[0]['id']
                session['image_path'] = student_data[0]['image_path']
                session['phone_number'] = student_data[0]['phone_number']
                session['classname'] = student_data[0]['classname']
                session['name'] = student_data[0]['name']
                session['roll_number'] = student_data[0]['roll_number']
                return redirect(url_for('student_dashboard'))
    
    return render_template('student/login.html')

@app.route('/student_dashboard', methods=['GET'])
def student_dashboard():
    if(session.get('student_email')):
        student_data = dict()
        student_data['student_email'] = session.get('student_email')
        student_data['id'] = session.get('id')
        student_data['image_path'] = session.get('image_path')
        student_data['phone_number'] = session.get('phone_number')
        student_data['subject'] = session.get('subject')
        student_data['name'] = session.get('name')
        student_data['classname'] = session.get('classname')
        student_data['roll_number'] = session.get('roll_number')

        return render_template('student/dashboard.html', student_data=student_data)

@app.route('/api/students', methods=['GET'])
def get_students():
    if(session.get('teacher_email')):
        students = get_all_students()
        print(students)
        return jsonify([{
        'name': student['name'],
        'email': student['email'],
        'classname': student['classname'],
        'roll_number': student['roll_number']
        } for student in students])

def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434")
        print(response.status_code)
        return True
    except:
        return False

if __name__ == '__main__':
    app.run(debug=True)