import os
import json
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
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

def send_customer_gmail(receiver_email, customer_name, category):
    try:
        sender_email = "ss.edit.bot.2026@gmail.com"
        sender_password = "xxxx xxxx xxxx xxxx"
        duration = random.randint(5, 15)
        chosen_time = random.choice(["04:30 PM", "05:45 PM", "06:45 PM", "07:30 PM"])
        chosen_topic = f"Viral Automated {category.capitalize()} Masterclass Video"

        subject = f"🎬 [SS-AI Studio] Your Video Is Ready to Publish! - {datetime.now().strftime('%d %b')}"
        body = f"Hello {customer_name},\n\nYour SS-AI Automated Studio Bot has successfully generated content!\n\n📊 VIDEO DETAILS:\n- Custom Category: {category.upper()}\n- Topic: {chosen_topic}\n- Duration: {duration} Mins\n- Upload Time: Today at {chosen_time}\n\nUpdates will be auto-published! (Platform Owner: Sk Suhan 👑)"
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = sender_email; msg['To'] = receiver_email; msg['Subject'] = subject
        
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Mail Error: {e}"); return False

@app.route('/')
def index():
    if 'username' in session:
        db = load_db()
        if session['role'] == 'admin': return render_template('index.html', role='admin', username=session['username'], customers=db["customers"])
        user_info = db["customers"].get(session['username'], {})
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
        if not user_data.get('is_active', True): return jsonify({"status": "ERROR", "message": "🛑 LOGIN DENIED: Account is BLOCKED!"})
        if user_data.get('device_id') and user_data.get('device_id') != client_device: return jsonify({"status": "ERROR", "message": "🛑 [DEVICE LOCKED] Bound to another phone!"})
        
        if not user_data.get('device_id'): db["customers"][username]["device_id"] = client_device; save_db(db)
        session.permanent = True; session['username'] = username; session['role'] = "customer"
        return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

# 📝 কাস্টমার যখন নিজে বাইরে থেকে সাইন-আপ করবে, এই রাউট কাজ করবে
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    
    if not phone or not name or not password:
        return jsonify({"status": "ERROR", "message": "All fields are required!"})
        
    db = load_db()
    if phone in db["customers"]:
        return jsonify({"status": "ERROR", "message": "🛑 This Number is already registered! Go to Login."})
        
    # অটোমেটিক কাস্টমারের ডেটা ডাটাবেসে সেভ হয়ে যাওয়া
    db["customers"][phone] = {
        "name": name,
        "password": password,
        "category": "",
        "is_active": True,
        "youtube_linked": False,
        "gmail": "",
        "device_id": ""
    }
    save_db(db)
    return jsonify({"status": "SUCCESS", "message": "🎉 Account Created Successfully! Now you can Login."})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session: return jsonify({"status": "ERROR"})
    gmail_input = request.json.get('gmail', '').strip()
    db = load_db(); username = session['username']
    db["customers"][username]["gmail"] = gmail_input; db["customers"][username]["youtube_linked"] = True; save_db(db)
    return jsonify({"status": "SUCCESS", "message": f"✅ Gmail Linked: {gmail_input}"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session['role'] != 'customer': return jsonify({"status": "ERROR"})
    selected_cat = request.json.get('category', '').strip()
    db = load_db(); username = session['username']
    db["customers"][username]["category"] = selected_cat; user_data = db["customers"][username]; save_db(db)
    if user_data.get('gmail'): send_customer_gmail(user_data['gmail'], user_data['name'], selected_cat)
    return jsonify({"status": "SUCCESS", "message": f"🎯 Category Locked & Mail Alert Sent!"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); db = load_db()
    if target_user in db["customers"]:
        db["customers"].pop(target_user); save_db(db)
        return jsonify({"status": "SUCCESS", "message": f"💥 Customer successfully DELETED!"})
    return jsonify({"status": "ERROR"})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session['role'] != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); action = request.json.get('action'); db = load_db()
    if target_user in db["customers"]:
        db["customers"][target_user]["is_active"] = (action == 'unblock'); save_db(db)
        return jsonify({"status": "SUCCESS", "message": "Status updated successfully!"})
    return jsonify({"status": "ERROR"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=True)
