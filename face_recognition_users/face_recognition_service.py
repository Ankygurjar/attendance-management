import os
import cv2
import numpy as np
import face_recognition

STORED_IMAGE_PATH_TEACHER = "static/teacher_photos/"
STORED_IMAGE_PATH_STUDENT = "static/student_photos/"
CAPTURED_IMAGE_PATH = "static/captured_image.jpg"


def encode_face(image_path):
    """Encodes a face from the given image path."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return encodings[0] if encodings else None

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    
    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(CAPTURED_IMAGE_PATH, frame)
        return CAPTURED_IMAGE_PATH
    return None

def compare_user_face(image_path, user_type):
    
    captured_img = capture_image()
    if not captured_img:
        return "Error capturing image"
    captured_encoding = encode_face(captured_img)
    if captured_encoding is None:
        return "No face detected in captured image"

    stored_img_path = os.path.join(STORED_IMAGE_PATH_TEACHER if user_type == 'teacher' else STORED_IMAGE_PATH_STUDENT, image_path)
    stored_encoding = encode_face(stored_img_path)

    if stored_encoding is not None:
        matches = face_recognition.compare_faces([stored_encoding], captured_encoding)
        if matches and matches[0] == True:
            return "Match found"
    return "No match found"

def match_faces(image_path, user_type):
    
    if(user_type == 'teacher' or user_type == 'student'):
        result = compare_user_face(image_path, user_type)
        if "Match found" in result:
            return True
        return False
    
    return False