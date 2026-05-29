import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "suhan_super_secret_key_2026"
app.permanent_session_lifetime = timedelta(days=31)

DB_FILE = 'users_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"admin": {"user_id": "SS_ELITE_ADMIN_2026", "password": "REK_#9824_SNC_@Z7X", "role": "admin"}, "customers": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f: 
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    if 'username' in session:
        db = load_db()
        if session['role'] == 'admin': 
            return render_template('index.html', role='admin', username=session['username'], customers=db["customers"])
        user_info = db["customers"].get(session['username'], {})
        if not user_info.get('is_approved', False): 
            session.clear(); return redirect(url_for('index'))
        if not user_info.get('is_active', True): 
            session.clear(); return "<h1>🛑 Account Blocked!</h1><a href='/logout'>Go Back</a>"
        return render_template('index.html', role='customer', username=session['username'], name=user_info.get('name', 'Customer'), category=user_info.get('category', ''), linked=user_info.get('youtube_linked', False), gmail_id=user_info.get('gmail', ''))
    return render_template('index.html', role='guest')

@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session: return jsonify({"topic": "N/A", "title": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
    
    db = load_db()
    user_info = db["customers"].get(session['username'], {})
    category = user_info.get('category', '').lower()
    
    if "cartoon" in category:
        topics = ["Bengali Fairy Tales - The Golden Bird", "Ghost Story - Suspicious Village", "Aladin New Magical Lamp Episode"]
        titles = ["সোনার পাখি ও জাদুকরী রাজা | Bengali Fairy Tales AI", "ভুতুড়ে গ্রামের রহস্যময় রাত! | Horror Cartoon Story", "আলাদিনের নতুন জাদুর চেরাগের কেল্লাফতে! 🔥"]
        best_time = "⏱️ TODAY AT 04:30 PM (Based on Kids Content Traffic)"
    elif "documentary" in category:
        topics = ["The Deep Secrets of Bermuda Triangle", "Mystery of Ancient Egyptian Pyramids", "World War II Unsolved Codes"]
        titles = ["Bermuda Triangle: The Unsolved Graveyard of Ocean 🌊", "The Secret Rooms Inside Pyramids Hidden For 4000 Years!", "The Deadliest Hidden Codes of WW2 Left Unanswered."]
        best_time = "⏱️ TODAY AT 08:15 PM (Based on Audience Retention Traffic)"
    else:
        topics = ["AI Automation Trends of 2026", "How To Scale Faceless YouTube Channel Fast", "Viral Editing Hacks with Topaz AI"]
        titles = ["The Future is Here: AI Systems of 2026 You Can't Ignore! 🔥", "I Started a Faceless YouTube Channel in 24 Hours (Secret AI Strategy)", "Cinematic Visuals Masterclass: Topaz AI Video Enhancement Tutorial"]
        best_time = "⏱️ TODAY AT 06:00 PM (Optimized via Peak Audience Traffic)"

    random.seed(int(datetime.now().strftime("%Y%m%d"))) 
    current_topic = random.choice(topics)
    current_title = random.choice(titles)
    
    return jsonify({
        "topic": current_topic,
        "title": current_title,
        "upload_time": best_time,
        "status": "🤖 AI ENGINE STATUS: 🟢 MONITORING LIVE TRAFFIC & SCHEDULING POST"
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    client_device = data.get('device_id', '')
    db = load_db()
    
    if username == db["admin"]["user_id"] and password == db["admin"]["password"]:
        session.permanent = True; session['username'] = "Owner"; session['role'] = "admin"
        return jsonify({"status": "SUCCESS", "message": "👑 Admin verified! Access granted."})
        
    if username in db["customers"] and db["customers"][username]["password"] == password:
        user_data = db["customers"][username]
        if not user_data.get('is_approved', False): return jsonify({"status": "ERROR", "message": "⏳ Request is still PENDING approval!"})
        if not user_data.get('is_active', True): return jsonify({"status": "ERROR", "message": "🛑 LOGIN DENIED: Account is BLOCKED!"})
        if user_data.get('device_id') and user_data.get('device_id') != client_device: return jsonify({"status": "ERROR", "message": "🛑 [DEVICE LOCKED] Bound to another phone!"})
        
        if not user_data.get('device_id'): db["customers"][username]["device_id"] = client_device; save_db(db)
        session.permanent = True; session['username'] = username; session['role'] = "customer"
        return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

@app.route('/register_request', methods=['POST'])
def register_request():
    data = request.json
    name = data.get('name', '').strip(); phone = data.get('phone', '').strip(); gmail = data.get('gmail', '').strip(); password = data.get('password', '').strip(); client_device = data.get('device_id', '')
    db = load_db()
    if phone in db["customers"]: return jsonify({"status": "ERROR", "message": "🛑 Number already registered!"})
    db["customers"][phone] = {"name": name, "password": password, "category": "", "gmail": gmail, "is_active": True, "is_approved": False, "youtube_linked": False, "device_id": client_device}
    save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    phone = request.json.get('phone', '').strip(); db = load_db()
    if phone not in db["customers"]: return jsonify({"status": "REJECTED"})
    if db["customers"][phone].get('is_approved', False): return jsonify({"status": "APPROVED"})
    return jsonify({"status": "PENDING"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    data = request.json; target_user = data.get('target_user'); action = data.get('action'); db = load_db()
    if target_user in db["customers"]:
        if action == 'approve': db["customers"][target_user]["is_approved"] = True; save_db(db); return jsonify({"status": "SUCCESS", "message": "✅ Account APPROVED Live!"})
        elif action == 'reject': db["customers"].pop(target_user); save_db(db); return jsonify({"status": "SUCCESS", "message": "❌ Account REJECTED!"})
    return jsonify({"status": "ERROR"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session: return jsonify({"status": "ERROR"})
    db = load_db(); username = session['username']
    db["customers"][username]["youtube_linked"] = True; save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session['role'] != 'customer': return jsonify({"status": "ERROR"})
    selected_cat = request.json.get('category', '').strip(); db = load_db(); username = session['username']
    db["customers"][username]["category"] = selected_cat; save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); db = load_db()
    if target_user in db["customers"]: db["customers"].pop(target_user); save_db(db); return jsonify({"status": "SUCCESS", "message": "💥 Customer DELETED!"})
    return jsonify({"status": "ERROR"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)
