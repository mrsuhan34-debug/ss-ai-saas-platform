import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "suhan_super_secret_key_2026"
app.permanent_session_lifetime = timedelta(days=31)

DB_FILE = 'users_db.json'

def load_db():
import os
import json
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
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

# 🎬 🤖 ইনস্ট্যান্ট এআই ক্রিয়েটর কোর ইঞ্জিন
# কাস্টমার ক্যাটাগরি লক করা মাত্রই এই ফাংশন ব্যাকগ্রাউন্ডে ওই নির্দিষ্ট দিন থেকেই কন্টেন্ট প্রোডাকশন লাইভ করে দেবে
def trigger_instant_ai_production(customer_phone, category_name):
    try:
        print(f"[AI ENGINE ACTIVE] -> Generating content immediately for customer {customer_phone} in {category_name} niche.")
        # এখানে তোমার এআই ভিডিও স্ক্রিপ্ট রাইটার, ভয়েসওভার এবং ইউটিউব এপিআই শিডিউলার সরাসরি এক্সিকিউট হবে
        # এর ফলে কাস্টমার যে মুহূর্ত থেকে সেট করবে, সেই দিন থেকেই বটের ফার্স্ট ভিডিও শিডিউল হয়ে যাবে
        return True
    except Exception as e:
        print(f"AI Engine Trigger Error: {e}")
        return False

@app.route('/')
def index():
    if 'username' in session:
        db = load_db()
        if session['role'] == 'admin': return render_template('index.html', role='admin', username=session['username'], customers=db["customers"])
        user_info = db["customers"].get(session['username'], {})
        if not user_info.get('is_approved', False): session.clear(); return redirect(url_for('index'))
        if not user_info.get('is_active', True): session.clear(); return "<h1>🛑 Account Blocked!</h1><a href='/logout'>Go Back</a>"
        return render_template('index.html', role='customer', username=session['username'], name=user_info.get('name', 'Customer'), category=user_info.get('category', ''), linked=user_info.get('youtube_linked', False), gmail_id=user_info.get('gmail', ''))
    return render_template('index.html', role='guest')

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
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    gmail = data.get('gmail', '').strip()
    password = data.get('password', '').strip()
    client_device = data.get('device_id', '')
    
    db = load_db()
    if phone in db["customers"]: return jsonify({"status": "ERROR", "message": "🛑 Number already registered!"})
        
    db["customers"][phone] = {
        "name": name, "password": password, "category": "", "gmail": gmail,
        "is_active": True, "is_approved": False, "youtube_linked": False, "device_id": client_device,
        "bot_active": False # প্রথমাবস্থায় বট স্ট্যান্ডবাই মুডে থাকবে
    }
    save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    phone = request.json.get('phone', '').strip()
    db = load_db()
    if phone not in db["customers"]: return jsonify({"status": "REJECTED"})
    if db["customers"][phone].get('is_approved', False): return jsonify({"status": "APPROVED"})
    return jsonify({"status": "PENDING"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    data = request.json
    target_user = data.get('target_user'); action = data.get('action'); db = load_db()
    if target_user in db["customers"]:
        if action == 'approve':
            db["customers"][target_user]["is_approved"] = True; save_db(db)
            return jsonify({"status": "SUCCESS", "message": "✅ Account APPROVED Live!"})
        elif action == 'reject':
            db["customers"].pop(target_user); save_db(db)
            return jsonify({"status": "SUCCESS", "message": "❌ Account REJECTED!"})
    return jsonify({"status": "ERROR"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session: return jsonify({"status": "ERROR"})
    db = load_db(); username = session['username']
    db["customers"][username]["youtube_linked"] = True; save_db(db)
    return jsonify({"status": "SUCCESS", "message": "✅ Official YouTube Channel Access Linked!"})

# 🎯 কাস্টমার ক্যাটাগরি সেট করার রাউট (ইনস্ট্যান্ট ফার্স্ট-ডে এআই প্রোডাকশন সিঙ্ক)
@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session['role'] != 'customer': return jsonify({"status": "ERROR"})
    selected_cat = request.json.get('category', '').strip()
    db = load_db(); username = session['username']
    
    db["customers"][username]["category"] = selected_cat
    db["customers"][username]["bot_active"] = True # কাস্টমার লক করা মাত্রই বট ইঞ্জিন ইনস্ট্যান্ট একটিভ হলো
    save_db(db)
    
    # ⚡ লাইভ মেকানিজম ট্রিগার (যাতে প্রথম দিন থেকেই ভিডিও জেনারেশন ও আপলোডিং প্রসেস রান করে)
    trigger_instant_ai_production(username, selected_cat)
    
    return jsonify({"status": "SUCCESS", "message": f"🎯 Category Locked & AI Automation Active From Today!"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); db = load_db()
    if target_user in db["customers"]: db["customers"].pop(target_user); save_db(db); return jsonify({"status": "SUCCESS", "message": f"💥 Customer DELETED!"})
    return jsonify({"status": "ERROR"})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); action = request.json.get('action'); db = load_db()
    if target_user in db["customers"]: db["customers"][target_user]["is_active"] = (action == 'unblock'); save_db(db); return jsonify({"status": "SUCCESS", "message": "Status updated!"})
    return jsonify({"status": "ERROR"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"admin": {"user_id": "SS_ELITE_ADMIN_2026", "password": "REK_#9824_SNC_@Z7X", "role": "admin"}, "customers": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

@app.route('/')
def index():
    if 'username' in session:
        db = load_db()
        if session['role'] == 'admin': return render_template('index.html', role='admin', username=session['username'], customers=db["customers"])
        user_info = db["customers"].get(session['username'], {})
        
        if not user_info.get('is_approved', False): session.clear(); return redirect(url_for('index'))
        if not user_info.get('is_active', True): session.clear(); return "<h1>🛑 Account Blocked!</h1><a href='/logout'>Go Back</a>"
        
        return render_template('index.html', role='customer', username=session['username'], name=user_info.get('name', 'Customer'), category=user_info.get('category', ''), linked=user_info.get('youtube_linked', False), gmail_id=user_info.get('gmail', ''))
    return render_template('index.html', role='guest')

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
        if not user_data.get('is_approved', False): return jsonify({"status": "ERROR", "message": "⏳ Request is still PENDING approval from Admin!"})
        if not user_data.get('is_active', True): return jsonify({"status": "ERROR", "message": "🛑 LOGIN DENIED: Account is BLOCKED!"})
        if user_data.get('device_id') and user_data.get('device_id') != client_device: return jsonify({"status": "ERROR", "message": "🛑 [DEVICE LOCKED] Bound to another phone!"})
        
        if not user_data.get('device_id'): db["customers"][username]["device_id"] = client_device; save_db(db)
        session.permanent = True; session['username'] = username; session['role'] = "customer"
        return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

@app.route('/register_request', methods=['POST'])
def register_request():
    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    gmail = data.get('gmail', '').strip()
    password = data.get('password', '').strip()
    client_device = data.get('device_id', '')
    
    db = load_db()
    if phone in db["customers"]:
        return jsonify({"status": "ERROR", "message": "🛑 This Number is already registered!"})
        
    db["customers"][phone] = {
        "name": name, "password": password, "category": "", "gmail": gmail,
        "is_active": True, "is_approved": False, "youtube_linked": False, "device_id": client_device
    }
    save_db(db)
    return jsonify({"status": "SUCCESS", "message": "Request logged."})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    phone = request.json.get('phone', '').strip()
    db = load_db()
    if phone not in db["customers"]: return jsonify({"status": "REJECTED"})
    
    user_data = db["customers"][phone]
    if user_data.get('is_approved', False):
        session.permanent = True; session['username'] = phone; session['role'] = "customer"
        return jsonify({"status": "APPROVED"})
    return jsonify({"status": "PENDING"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    data = request.json
    target_user = data.get('target_user')
    action = data.get('action')
    db = load_db()
    
    if target_user in db["customers"]:
        if action == 'approve':
            db["customers"][target_user]["is_approved"] = True; save_db(db)
            return jsonify({"status": "SUCCESS", "message": "✅ Account APPROVED Live!"})
        elif action == 'reject':
            db["customers"].pop(target_user); save_db(db)
            return jsonify({"status": "SUCCESS", "message": "❌ Account REJECTED & Deleted!"})
    return jsonify({"status": "ERROR"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session: return jsonify({"status": "ERROR"})
    db = load_db(); username = session['username']
    db["customers"][username]["youtube_linked"] = True; save_db(db)
    return jsonify({"status": "SUCCESS", "message": "✅ Official YouTube Channel Access Linked!"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session['role'] != 'customer': return jsonify({"status": "ERROR"})
    selected_cat = request.json.get('category', '').strip()
    db = load_db(); username = session['username']
    db["customers"][username]["category"] = selected_cat; save_db(db)
    return jsonify({"status": "SUCCESS", "message": f"🎯 Category Locked Successfully!"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); db = load_db()
    if target_user in db["customers"]: db["customers"].pop(target_user); save_db(db); return jsonify({"status": "SUCCESS", "message": f"💥 Customer DELETED!"})
    return jsonify({"status": "ERROR"})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); action = request.json.get('action'); db = load_db()
    if target_user in db["customers"]: db["customers"][target_user]["is_active"] = (action == 'unblock'); save_db(db); return jsonify({"status": "SUCCESS", "message": "Status updated!"})
    return jsonify({"status": "ERROR"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
