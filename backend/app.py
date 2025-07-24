from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import os

from models import db
from ocr import extract_text_and_schedule
from db import save_user
from scheduler import schedule_emails
from config import VALID_ACCESS_CODE, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    code = data.get('code')
    if code == VALID_ACCESS_CODE:
        return jsonify({"valid": True})
    return jsonify({"valid": False}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    schedule = data.get('schedule')

    if not email or not schedule:
        return jsonify({"error": "Missing email or schedule"}), 400
    
    try:
        save_user(email, schedule)
        schedule_emails(email, schedule)
        return jsonify({"status": "registered"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload(): 
    image = request.files.get('image')
    if not image:
        return jsonify({"error": "No image uploaded"}), 400
    text, schedule = extract_text_and_schedule(image)
    return jsonify({"text": text, "schedule": schedule})

if __name__ == '__main__':
    app.run(debug=True)