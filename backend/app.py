from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pytesseract
    from PIL import Image
    from models import db
    from ocr import extract_text_and_schedule
    from db import save_user
    from scheduler import schedule_emails
    from config import VALID_ACCESS_CODE, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
except ImportError as e:
    print(f"Import error: {e}")
    # Continue without OCR functionality for now
    pytesseract = None

app = Flask(__name__)

# Configure CORS - Allow all origins for testing, restrict in production
CORS(app, 
     resources={r"/*": {
         "origins": [
             "http://localhost:3000",
             "http://127.0.0.1:5500",
             "http://localhost:5500",
             "https://schedly-lemon.vercel.app"
         ],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type"],
         "supports_credentials": True
     }})

# Database configuration
if 'SQLALCHEMY_DATABASE_URI' in globals():
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize database
    if 'db' in globals():
        db.init_app(app)
        
        # Create tables
        with app.app_context():
            db.create_all()

@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "message": "Schedly API is running"})

@app.route('/verify', methods=['POST', 'OPTIONS'])
def verify():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json()
    code = data.get('code')
    
    if 'VALID_ACCESS_CODE' in globals() and code == VALID_ACCESS_CODE:
        return jsonify({"valid": True})
    return jsonify({"valid": False}), 401

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        email = data.get('email')
        schedule = data.get('schedule')

        if not email or not schedule:
            return jsonify({"error": "Missing email or schedule"}), 400
        
        if 'save_user' in globals() and 'schedule_emails' in globals():
            save_user(email, schedule)
            schedule_emails(email, schedule)
            return jsonify({"status": "registered"})
        else:
            return jsonify({"error": "Service not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        image = request.files.get('image')
        if not image:
            return jsonify({"error": "No image uploaded"}), 400
        
        if pytesseract and 'extract_text_and_schedule' in globals():
            text, schedule = extract_text_and_schedule(image)
            return jsonify({"text": text, "schedule": schedule})
        else:
            return jsonify({"error": "OCR service not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)