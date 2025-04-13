import pymysql
import os
from werkzeug.utils import secure_filename
import requests
import json
from flask import session

from database.teacher_db_services import get_teacher, get_all_teachers_db, add_student_db
# from .prediction_service import analyze_student_sentiment

UPLOAD_FOLDER = os.path.join('static', 'student_photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def login_teacher_service(username: str, password: str):
    if(username != '' and password != ''):
        return get_teacher(username, password)
    
    return tuple()

def get_all_teachers():
    return get_all_teachers_db()

def add_student_service(name, password, email, phone, roll_number, classname, photo = ''):
    if not all([name, password, email]):
        return False
    
    if(photo != ''):
        filename = f"{name}__{secure_filename(photo.filename)}"

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        photo.save(filepath)

    return add_student_db(name, password, email, phone, roll_number, classname)

# def analyze_sentiment(data):
#     if(data.feedback != None and data.marks != None and data.attendance != None):
#         print(analyze_student_sentiment(data))
#         return analyze_student_sentiment(data)
    
#     return False

def process_teacher_command(command, teacher_id):
    # Convert command to lowercase for easier processing
    lower_cmd = command.lower()
    
    # Add student logic
    if any(word in lower_cmd for word in ['add student', 'create student', 'new student']):
        return handle_add_student(command, teacher_id)
    
    # Delete student logic
    elif any(word in lower_cmd for word in ['remove student', 'delete student', 'expel student']):
        return handle_delete_student(command, teacher_id)
    
    # Default response
    return {
        'response': "I can help you manage students. Try commands like:\n"
                    "- 'Add a new student named John Doe with email john@example.com phone 1234567890 roll number 101 class 10A password abcabc'\n"
                    "- 'Delete student with roll number 101'",
        'action': None
    }

def handle_add_student(command, teacher_id):
    # Extract information using simple parsing (you can enhance this with NLP later)
    name = extract_value(command, ['named', 'name is', 'name'])
    email = extract_value(command, ['email', 'mail'])
    phone = extract_value(command, ['phone', 'number'])
    roll_number = extract_value(command, ['roll number', 'roll no', 'roll'])
    classname = extract_value(command, ['class', 'grade'])
    password = extract_value(command, ['password', 'password is'])
    
    if not all([name, email, roll_number, classname, password]):
        return {
            'response': "I need more information to add a student. Please provide:\n"
                       "- Name\n- Email\n- Roll number\n- Class\n"
                       "Example: 'Add a new student named John Doe with email john@example.com, phone 1234567890, roll number 101, class 10A'",
            'action': None
        }
    
    if(add_student_service(name, password, email, phone, roll_number, classname)):
        return {
            'response': f"Student is added :\nName: {name}\nEmail: {email}\nPhone: {phone}\nRoll: {roll_number}\nClass: {classname}\n\nType 'confirm' to proceed or 'cancel' to abort.",
            'action': {
                
            }
        }
    
    return {
        'response': f"An issue occured when saving the student",
    }

def handle_delete_student(command, teacher_id):
    roll_number = extract_value(command, ['roll number', 'roll no', 'roll'])
    email = extract_value(command, ['email', 'mail'])
    
    if not roll_number and not email:
        return {
            'response': "Please specify which student to delete by roll number or email.\n"
                       "Example: 'Delete student with roll number 101' or 'Remove student john@example.com'",
            'action': None
        }
    
    identifier = roll_number if roll_number else email
    by_roll = bool(roll_number)
    
    return {
        'response': f"Confirm deleting student with {'roll number' if by_roll else 'email'} {identifier}?\nType 'confirm' to proceed or 'cancel' to abort.",
        'action': {
            'type': 'delete_student',
            'data': {
                'roll_number': roll_number,
                'email': email,
                'teacher_id': teacher_id
            }
        }
    }

def extract_value(command, keywords):
    for keyword in keywords:
        if keyword in command.lower():
            parts = command.lower().split(keyword)
            if len(parts) > 1:
                value = parts[1].strip()
                value = value.split()[0].strip('.,;!?')
                return value
    return None

def analyze_teacher_command(message: str, teacher_id: int) -> dict:
    if 'chat_context' not in session:
        session['chat_context'] = {
            'awaiting_response': None,
            'student_data': {},
            'current_field': None,
            'required_fields': ['name', 'email', 'password', 'phone_number', 'roll_number', 'classname']
        }
    
    chat_context = session['chat_context']
    
    system_prompt = f"""You are a student management assistant. Respond in STRICT JSON format:
{{
    "response": "text",
    "next_question": "text or null",
    "action": "add_student|delete_student|null",
    "collected_data": {{}}
}}

Current Context:
- Awaiting: {chat_context['awaiting_response']}
- Collected: {chat_context['student_data']}
- Next Field Needed: {next((
    f for f in chat_context['required_fields'] 
    if f not in chat_context['student_data']
), None)}

User Input: "{message}"
"""
    
    try:
        ollama_response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_ctx": 2048
                }
            },
            timeout=15
        )
        ollama_response.raise_for_status()
        
        ai_output = parse_ollama_response(ollama_response.text)
        
        if 'collected_data' in ai_output:
            chat_context['student_data'].update(ai_output['collected_data'])
        
        if 'next_question' in ai_output:
            chat_context['awaiting_response'] = ai_output['next_question']
        
        session.modified = True
        return ai_output
        
    except requests.exceptions.RequestException as e:
        return {
            "response": f"Connection error: {str(e)}",
            "action": None
        }

def build_system_prompt(context: dict, message: str) -> str:
    """Builds a precise prompt for the current conversation stage"""
    required_fields = context.get('required_fields', ['name', 'email', 'password', 'phone_number', 'roll_number', 'classname'])
    collected_fields = context.get('student_data', {}).keys()
    missing_fields = [f for f in required_fields if f not in collected_fields]
    
    base_prompt = f"""You are a student management assistant. Follow these rules:
1. Respond ONLY in valid JSON format with: response, next_question, action, collected_data
2. Collect student data in this order: {', '.join(required_fields)}
3. Ask for one field at a time
4. Never ask for image_path
5. Verify data before confirming

Current stage: {context.get('current_field', 'start')}
Collected data: {context.get('student_data', {})}
Missing fields: {missing_fields}"""

    if not context.get('current_field'):
        return f"{base_prompt}\nUser says: '{message}'\nStart by greeting and asking if they want to add a student."
    else:
        return f"{base_prompt}\nLast asked: '{context.get('current_field')}'\nUser replied: '{message}'"

def parse_ollama_response(raw_response: str) -> dict:
    """
    Handles both streaming and non-streaming Ollama responses
    Returns: {
        "response": str,
        "next_question": str,
        "action": str,
        "collected_data": dict
    }
    """
    try:
        response_data = json.loads(raw_response)
        
        if isinstance(response_data, list):
            combined_content = ""
            for chunk in response_data:
                if 'message' in chunk and 'content' in chunk['message']:
                    combined_content += chunk['message']['content']
            try:
                return json.loads(combined_content)
            except json.JSONDecodeError:
                return {"response": combined_content.strip()}
        
        if 'message' in response_data and 'content' in response_data['message']:
            content = response_data['message']['content']
            try:
                return json.loads(content.replace('\\"', '"'))
            except json.JSONDecodeError:
                return {"response": content.strip()}
                
        return {"response": "Received unexpected response format"}
        
    except json.JSONDecodeError:
        return {"response": "Could not process AI response"}