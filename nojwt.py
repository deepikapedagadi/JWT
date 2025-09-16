from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
#import jwt
import datetime, base64, os, json
from cryptography.fernet import Fernet
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'user-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:welcome@localhost:5432/testdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
enc_key = os.environ.get('ENCRYPTION_KEY')
if not enc_key:
    enc_key = Fernet.generate_key().decode()
    print("WARNING: No ENCRYPTION_KEY set — generated ephemeral key (won't persist across restarts).")
app.config['ENCRYPTION_KEY'] = enc_key.encode()
app.config['ADMIN_KEY'] = os.environ.get('ADMIN_KEY', 'admin-demo-key')
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)        # hashed (for auth)
    password_encrypted = db.Column(db.Text, nullable=True)     # reversible encrypted (demo only)
with app.app_context():
    db.create_all()
def get_cipher():
    return Fernet(app.config['ENCRYPTION_KEY'])
def encrypt_password(plain_password: str) -> str:
    cipher = get_cipher()
    token = cipher.encrypt(plain_password.encode())
    return token.decode('utf-8')  # store as str
def decrypt_password(encrypted_str: str) -> str:
    cipher = get_cipher()
    plain = cipher.decrypt(encrypted_str.encode())
    return plain.decode('utf-8')
@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    if not email or not name or not password:
        return jsonify({'status': 'error', 'message': 'Email, name and password are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'User already exists'}), 409

    hashed = generate_password_hash(password)
    encrypted = encrypt_password(password)  # demo reversible storage
    user = User(email=email, name=name, password=hashed, password_encrypted=encrypted)
    db.session.add(user)
    db.session.commit()
    #token = generate_token(user)
    return jsonify({'status': 'success', 'message': 'User registered successfully'})
@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    #token = generate_token(user)
    return jsonify({'status': 'success', 'message': 'Login successful'})
@app.route('/admin/decrypt', methods=['POST'])
def admin_decrypt():
    admin_key = request.headers.get('X-ADMIN-KEY', '')
    if admin_key != app.config['ADMIN_KEY']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    data = request.json or {}
    email = data.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'email is required in body'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    if not user.password_encrypted:
        return jsonify({'status': 'error', 'message': 'No encrypted password stored for this user'}), 404
    try:
        plain = decrypt_password(user.password_encrypted)
        # WARNING: returning the plain password is unsafe — demo only
        return jsonify({'status': 'success', 'email': user.email, 'decrypted_password': plain})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Decryption failed', 'error': str(e)}), 500
@app.route('/admin/encrypt-user', methods=['POST'])
def admin_encrypt_user():
    admin_key = request.headers.get('X-ADMIN-KEY', '')
    if admin_key != app.config['ADMIN_KEY']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    user.password_encrypted = encrypt_password(password)
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Encrypted password stored for {email} and {user.password_encrypted}'})
@app.route('/decode', methods=['GET', 'POST'])
def decode_route():
    token = _extract_token_from_request(request)
    if not token:
        return jsonify({'status': 'error', 'message': 'No token provided. Use Authorization: Bearer <token>, JSON {"token":...} or ?token=...'}), 400
    try:
        header, payload, signature_b64 = decode_jwt_unverified(token)
        return jsonify({'verified': False, 'header': header, 'payload': payload, 'signature_b64url': signature_b64})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to decode token', 'error': str(e)}), 400
def _b64url_decode(data: str) -> bytes:
    if isinstance(data, str):
        data = data.encode('utf-8')
    rem = len(data) % 4
    if rem:
        data += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(data)
def decode_jwt_unverified(token: str):
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Token must have exactly 3 parts separated by dots.')
    h_b64, p_b64, s_b64 = parts
    header = json.loads(_b64url_decode(h_b64))
    payload = json.loads(_b64url_decode(p_b64))
    return header, payload, s_b64
def _extract_token_from_request(req):
    auth = req.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    if req.is_json:
        t = req.json.get('token')
        if t:
            return t.strip()
    t = req.args.get('token')
    if t:
        return t.strip()
    return None
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    # Return only safe info here
    return jsonify([{'id': u.id, 'email': u.email, 'name': u.name} for u in users])
if __name__ == '__main__':
    app.run(debug=True, port=9494)
with app.app_context():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())

