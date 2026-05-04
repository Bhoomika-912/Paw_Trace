import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, g, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pawtrace-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
CORS(app, supports_credentials=True, origins=['http://localhost:5001', 'http://127.0.0.1:5001', 'http://localhost:5500'])

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
DATABASE = 'pawtrace.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Missing pets reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_name TEXT NOT NULL,
                animal_type TEXT NOT NULL,
                breed TEXT,
                color TEXT,
                location TEXT NOT NULL,
                date_missing TEXT NOT NULL,
                owner_contact TEXT NOT NULL,
                reward INTEGER DEFAULT 0,
                description TEXT,
                image_filename TEXT,
                status TEXT DEFAULT 'missing',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Sightings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sightings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                description TEXT,
                reporter_name TEXT,
                reporter_contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Contact messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reward claims table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reward_claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER NOT NULL,
                claimant_name TEXT NOT NULL,
                proof_details TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        ''')
        
        db.commit()
        
        # Insert sample data if empty
        cursor.execute("SELECT COUNT(*) FROM reports")
        if cursor.fetchone()[0] == 0:
            sample_reports = [
                ('Luna', 'Dog', 'Golden Retriever', 'Golden', 'Central Park, NY', '2026-03-20', '+1 555 0101', 500, 'Wearing red collar. Very friendly.', None),
                ('Milo', 'Cat', 'Siamese', 'Cream', 'Brooklyn Heights, NY', '2026-03-21', '+1 555 0102', 200, 'Has a small scar on left ear.', None),
                ('Coco', 'Bird', 'Cockatiel', 'Grey/Yellow', 'Queens, NY', '2026-03-19', '+1 555 0103', 0, 'Whistles often. Responds to "Coco".', None),
                ('Max', 'Dog', 'German Shepherd', 'Black/Tan', 'Staten Island, NY', '2026-03-22', '+1 555 0104', 1000, 'Microchipped. Needs medication.', None),
                ('Bella', 'Cat', 'Persian', 'White', 'Upper West Side, NY', '2026-03-18', '+1 555 0105', 300, 'Very fluffy. Blue eyes.', None),
                ('Rocky', 'Rabbit', 'Holland Lop', 'Brown', 'Astoria, NY', '2026-03-23', '+1 555 0106', 50, 'Loves carrots. Very shy.', None),
            ]
            for report in sample_reports:
                cursor.execute('''
                    INSERT INTO reports (pet_name, animal_type, breed, color, location, date_missing, owner_contact, reward, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', report)
            
            # Sample sightings
            cursor.execute('''
                INSERT INTO sightings (report_id, location, description, reporter_name)
                VALUES (1, 'Central Park near Bethesda Fountain', 'Saw a golden dog matching description', 'Anonymous'),
                (2, 'Brooklyn Bridge Park', 'Cat spotted near the playground', 'Local resident')
            ''')
            
            db.commit()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== API ROUTES ====================

# Auth endpoints
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({'error': 'All fields required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Hash password
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    password_hash = f"{salt}${password_hash}"
    
    cursor.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                   (name, email, password_hash))
    db.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    stored_hash = user['password_hash']
    salt, hash_value = stored_hash.split('$')
    computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    if computed_hash != hash_value:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    return jsonify(dict(user))

# Reports endpoints
@app.route('/api/reports', methods=['GET'])
def get_reports():
    animal_type = request.args.get('animal_type')
    search = request.args.get('search')
    limit = request.args.get('limit', 50, type=int)
    
    db = get_db()
    cursor = db.cursor()
    
    query = 'SELECT * FROM reports WHERE status = "missing"'
    params = []
    
    if animal_type and animal_type != 'All':
        query += ' AND animal_type = ?'
        params.append(animal_type)
    
    if search:
        query += ' AND (pet_name LIKE ? OR breed LIKE ? OR location LIKE ? OR description LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param, search_param])
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    reports = cursor.fetchall()
    
    return jsonify([dict(report) for report in reports])

@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    # Get sightings for this report
    cursor.execute('SELECT * FROM sightings WHERE report_id = ? ORDER BY created_at DESC', (report_id,))
    sightings = cursor.fetchall()
    
    result = dict(report)
    result['sightings'] = [dict(s) for s in sightings]
    
    return jsonify(result)

@app.route('/api/reports', methods=['POST'])
def create_report():
    pet_name = request.form.get('pet_name')
    animal_type = request.form.get('animal_type')
    location = request.form.get('location')
    date_missing = request.form.get('date_missing')
    owner_contact = request.form.get('owner_contact')
    
    if not all([pet_name, animal_type, location, date_missing, owner_contact]):
        return jsonify({'error': 'Required fields missing'}), 400
    
    # Handle image upload
    image_filename = None
    if 'petImage' in request.files:
        file = request.files['petImage']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_filename = filename
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO reports (pet_name, animal_type, breed, color, location, date_missing, 
                            owner_contact, reward, description, image_filename, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pet_name, animal_type, request.form.get('breed'), request.form.get('color'),
        location, date_missing, owner_contact, request.form.get('reward', 0),
        request.form.get('description'), image_filename, session.get('user_id')
    ))
    db.commit()
    
    return jsonify({'message': 'Report created successfully', 'id': cursor.lastrowid}), 201

@app.route('/api/reports/<int:report_id>/sighting', methods=['POST'])
def add_sighting(report_id):
    data = request.json
    location = data.get('location')
    description = data.get('description')
    reporter_name = data.get('reporter_name')
    reporter_contact = data.get('reporter_contact')
    
    if not location:
        return jsonify({'error': 'Location required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if report exists
    cursor.execute('SELECT id FROM reports WHERE id = ?', (report_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Report not found'}), 404
    
    cursor.execute('''
        INSERT INTO sightings (report_id, location, description, reporter_name, reporter_contact)
        VALUES (?, ?, ?, ?, ?)
    ''', (report_id, location, description, reporter_name, reporter_contact))
    db.commit()
    
    return jsonify({'message': 'Sighting reported successfully'}), 201

@app.route('/api/reports/<int:report_id>/status', methods=['PUT'])
def update_report_status(report_id):
    data = request.json
    status = data.get('status')
    
    if status not in ['missing', 'found', 'resolved']:
        return jsonify({'error': 'Invalid status'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE reports SET status = ? WHERE id = ?', (status, report_id))
    db.commit()
    
    return jsonify({'message': 'Status updated successfully'})

# Feedback endpoints
@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM feedback ORDER BY created_at DESC LIMIT 20')
    feedbacks = cursor.fetchall()
    return jsonify([dict(f) for f in feedbacks])

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    rating = data.get('rating')
    message = data.get('message')
    
    if not rating or not message:
        return jsonify({'error': 'Rating and message required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO feedback (rating, message, user_id)
        VALUES (?, ?, ?)
    ''', (rating, message, session.get('user_id')))
    db.commit()
    
    return jsonify({'message': 'Feedback submitted successfully'}), 201

# Contact endpoints
@app.route('/api/contact', methods=['POST'])
def submit_contact():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    
    if not all([name, email, message]):
        return jsonify({'error': 'All fields required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO contact_messages (name, email, message)
        VALUES (?, ?, ?)
    ''', (name, email, message))
    db.commit()
    
    return jsonify({'message': 'Message sent successfully'}), 201

# Reward endpoints
@app.route('/api/rewards', methods=['GET'])
def get_rewards():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, pet_name, animal_type, location, reward 
        FROM reports 
        WHERE reward > 0 AND status = 'missing'
        ORDER BY reward DESC
    ''')
    rewards = cursor.fetchall()
    return jsonify([dict(r) for r in rewards])

@app.route('/api/rewards/claim', methods=['POST'])
def claim_reward():
    data = request.json
    report_id = data.get('report_id')
    claimant_name = data.get('claimant_name')
    proof_details = data.get('proof_details')
    
    if not all([report_id, claimant_name, proof_details]):
        return jsonify({'error': 'All fields required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if report exists and has reward
    cursor.execute('SELECT id, reward FROM reports WHERE id = ? AND reward > 0', (report_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Invalid report or no reward available'}), 404
    
    cursor.execute('''
        INSERT INTO reward_claims (report_id, claimant_name, proof_details)
        VALUES (?, ?, ?)
    ''', (report_id, claimant_name, proof_details))
    db.commit()
    
    return jsonify({'message': 'Claim submitted successfully'}), 201

# Dashboard stats
@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM reports WHERE status = "missing"')
    active_reports = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM reports')
    total_reports = cursor.fetchone()[0]
    
    cursor.execute('SELECT COALESCE(SUM(reward), 0) FROM reports WHERE status = "missing"')
    total_rewards = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sightings')
    total_sightings = cursor.fetchone()[0]
    
    return jsonify({
        'active_reports': active_reports,
        'total_reports': total_reports,
        'total_rewards': total_rewards,
        'total_sightings': total_sightings
    })

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Root endpoint for testing
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'PawTrace API is running'})

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("🐾 PawTrace Backend Server")
    print("=" * 50)
    print(f"Server running at: http://localhost:5000")
    print(f"API health check: http://localhost:5000/api/health")
    print("Press CTRL+C to stop")
    print("=" * 50)
    app.run(debug=True, port=5000)