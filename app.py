import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "suhan_super_secret_key_2026"

DB_FILE = 'users_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"admin": {"password": "suhan_admin_2026", "role": "admin"}, "customers": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

@app.route('/')
def index():
    if 'username' in session:
        db = load_db()
        if session['role'] == 'admin':
            return render_template('index.html', role='admin', username=session['username'], customers=db["customers"])
        else:
            user_info = db["customers"].get(session['username'], {})
            if not user_info.get('is_active', True):
                session.clear()
                return "🛑 আপনাকে অ্যাডমিন প্যানেল থেকে ব্লক করা হয়েছে!"
            return render_template('index.html', role='customer', username=session['username'], category=user_info.get('category', ''), linked=user_info.get('youtube_linked', False))
    return render_template('index.html', role='guest')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    db = load_db()
    
    if username == "admin" and password == db["admin"]["password"]:
        session['username'] = "admin"
        session['role'] = "admin"
        return jsonify({"status": "SUCCESS", "message": "অ্যাডমিন ভেরিফাইড! কন্ট্রোল রুম লোড হচ্ছে..."})
        
    if username in db["customers"] and db["customers"][username]["password"] == password:
        if not db["customers"][username].get('is_active', True):
            return jsonify({"status": "ERROR", "message": "🛑 আপনার অ্যাকাউন্টটি সাসপেন্ড করা হয়েছে!"})
        session['username'] = username
        session['role'] = "customer"
        return jsonify({"status": "SUCCESS", "message": "লগইন সফল! এআই স্টুডিও ওপেন হচ্ছে..."})
        
    return jsonify({"status": "ERROR", "message": "ভুল ইউজারনেম বা পাসওয়ার্ড!"})

@app.route('/admin/kick', methods=['POST'])
def kick_user():
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({"status": "ERROR", "message": "অননুমোদিত অ্যাক্সেস!"})
    target_user = request.json.get('target_user')
    db = load_db()
    if target_user in db["customers"]:
        db["customers"][target_user]["is_active"] = False
        save_db(db)
        return jsonify({"status": "SUCCESS", "message": f"ইউজার {target_user} কে সাকসেসফুলি লগ-আউট ও ব্লক করা হয়েছে।"})
    return jsonify({"status": "ERROR", "message": "ইউজার পাওয়া যায়নি।"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session['role'] != 'customer':
        return jsonify({"status": "ERROR", "message": "দয়া করে আগে লগইন করুন।"})
    selected_cat = request.json.get('category', '').lower()
    ALLOWED_CATEGORIES = ["gaming", "cooking", "tech", "cartoon", "motivation"]
    if selected_cat not in ALLOWED_CATEGORIES:
        return jsonify({"status": "ERROR", "message": "🛑 অবৈধ ক্যাটাগরি সিলেক্ট করেছেন!"})
    db = load_db()
    username = session['username']
    if db["customers"][username].get('category'):
        return jsonify({"status": "WARNING", "message": f"আপনার ক্যাটাগরি অলরেডি '{db['customers'][username]['category']}' লক করা আছে!"})
    db["customers"][username]["category"] = selected_cat
    save_db(db)
    return jsonify({"status": "SUCCESS", "message": f"🎯 ক্যাটাগরি সফলভাবে লক করা হয়েছে: {selected_cat.upper()}"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
