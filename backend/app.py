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
    pytesseract = None

app = Flask(__name__)

# Configure CORS - More permissive configuration
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": False,
         "max_age": 3600
     }})

# Database configuration
if 'SQLALCHEMY_DATABASE_URI' in globals():
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize database
    if 'db' in globals():
        db.init_app(app)
        
        # Create tables
        with app.app_context():
            try:
                db.create_all()
                print("Database tables created successfully")
            except Exception as e:
                print(f"Error creating database tables: {e}")

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "Schedly API is running",
        "pytesseract_available": pytesseract is not None
    })

@app.route('/verify', methods=['POST', 'OPTIONS'])
def verify():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"valid": False, "error": "No data provided"}), 400
            
        code = data.get('code')
        
        if 'VALID_ACCESS_CODE' in globals() and code == VALID_ACCESS_CODE:
            return jsonify({"valid": True}), 200
        return jsonify({"valid": False}), 401
    except Exception as e:
        print(f"Error in /verify: {e}")
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        schedule = data.get('schedule')

        if not email or not schedule:
            return jsonify({"error": "Missing email or schedule"}), 400
        
        if 'save_user' in globals() and 'schedule_emails' in globals():
            save_user(email, schedule)
            schedule_emails(email, schedule)
            return jsonify({"status": "registered"}), 200
        else:
            return jsonify({"error": "Database service not available"}), 503
    except Exception as e:
        print(f"Error in /register: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    # Handle preflight request
    if request.method == 'OPTIONS':
        return '', 204
    
    print(f"Upload request received - Method: {request.method}")
    print(f"Files: {list(request.files.keys())}")
    print(f"Form: {list(request.form.keys())}")
    
    try:
        # Check if pytesseract is available
        if not pytesseract:
            return jsonify({
                "error": "OCR service not available - Tesseract not installed"
            }), 503
        
        # Check if image file exists in request
        if 'image' not in request.files:
            return jsonify({
                "error": "No image file provided. Expected 'image' field in form data."
            }), 400
        
        image_file = request.files['image']
        
        # Check if file is empty
        if image_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        print(f"Processing image: {image_file.filename}")
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
        file_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            }), 400
        
        # Extract text and schedule
        if 'extract_text_and_schedule' in globals():
            text, schedule = extract_text_and_schedule(image_file)
            
            print(f"Extracted text length: {len(text)}")
            print(f"Extracted schedule items: {len(schedule)}")
            
            return jsonify({
                "text": text, 
                "schedule": schedule,
                "status": "success"
            }), 200
        else:
            return jsonify({"error": "OCR function not available"}), 503
            
    except Exception as e:
        print(f"Error in /upload: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Error processing image: {str(e)}",
            "error_type": type(e).__name__
        }), 500

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Flask app on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Pytesseract available: {pytesseract is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)