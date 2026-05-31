import os
import json
import random
import ssl
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# 🔒 সেশন সিকিউরিটি লক লজিক
app.secret_key = "suhan_saas_ultra_secure_permanent_key_2026"
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)
app.config['SESSION_COOKIE_NAME'] = 'ss_ai_saas_session'

# 🌐 [রেন্ডার সিক্রেট লকার থেকে ক্লাউড ডাটাবেস লিংক টানা হচ্ছে]
MONGO_URI = os.getenv("MONGO_URI")

users_collection = None

if MONGO_URI:
    try:
        client = MongoClient(
            MONGO_URI, 
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        db = client['ss_ai_database']
        users_collection = db['users']
        print("🌐 MongoDB Cloud Database Connected Successfully!")
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
else:
    print("⚠️ WARNING: MONGO_URI is missing from Render Environment Variables!")

# ফিক্সড অ্যাডমিন আইডি লক (ডাটাবেস কানেক্টেড থাকলে চেক হবে)
try:
    if users_collection is not None and not users_collection.find_one({"_id": "admin"}):
        users_collection.insert_one({
            "_id": "admin",
            "user_id": "SS_ELITE_ADMIN_2026",
            "password": "REK_#9824_SNC_@Z7X",
            "role": "admin"
        })
except Exception as e:
    print(f"⚠️ Admin initialization skipped or deferred: {e}")

def get_all_customers():
    customers = {}
    if users_collection is not None:
        try:
            all_users = users_collection.find({"role": {"$ne": "admin"}})
            for u in all_users:
                # 📅 সাবস্ক্রিপশন ডেট ট্র্যাকিং লজিক (১০০% ক্র্যাশ প্রুফ করা হলো ভাই)
                approved_at_str = u.get("approved_at", "")
                days_left = 30
                is_expired = False
                
                if approved_at_str and approved_at_str.strip():
                    try:
                        approved_date = datetime.strptime(approved_at_str.strip(), "%Y-%m-%d")
                        elapsed_days = (datetime.now() - approved_date).days
                        days_left = max(0, 30 - elapsed_days)
                        if elapsed_days >= 30:
                            is_expired = True
                    except Exception as date_err:
                        print(f"⚠️ Date parsing error for user {u.get('_id')}: {date_err}")
                        pass

                customers[u["_id"]] = {
                    "name": u.get("name", "Unknown"),
                    "password": u.get("password", ""),
                    "category": u.get("category", ""),
                    "gmail": u.get("gmail", ""),
                    "is_approved": u.get("is_approved", False),
                    "is_blocked": u.get("is_blocked", False),
                    "youtube_linked": u.get("youtube_linked", False),
                    "approved_at": approved_at_str,
                    "days_left": days_left,
                    "is_expired": is_expired
                }
        except Exception as e:
            print(f"❌ Error fetching customers: {e}")
    return customers

@app.route('/')
def index():
    if 'username' in session:
        if session.get('role') == 'admin': 
            return render_template('index.html', role='admin', username=session['username'], customers=get_all_customers())
        
        if users_collection is not None:
            try:
                user_info = users_collection.find_one({"_id": session['username']})
                if user_info and user_info.get('is_approved', False):
                    if user_info.get('is_blocked', False):
                        session.clear()
                        return "<h1>🛑 Account Blocked By Admin!</h1><a href='/logout'>Go Back</a>"
                    
                    return render_template(
                        'index.html', 
                        role='customer', 
                        username=session['username'], 
                        name=user_info.get('name', 'Customer'), 
                        category=user_info.get('category', ''), 
                        linked=user_info.get('youtube_linked', False), 
                        gmail_id=user_info.get('gmail', ''),
                        user_password=user_info.get('password', '')
                    )
            except Exception as e:
                print(f"❌ Route index error: {e}")
        session.clear()
        return redirect(url_for('index'))
    return render_template('index.html', role='guest')

@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session: return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
    if users_collection is None: return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "DATABASE OFFLINE"})
    
    try:
        user_info = users_collection.find_one({"_id": session['username']})
        if not user_info: return jsonify({"topic": "N/A"})
        category = user_info.get('category', '').lower()
        
        current_time = datetime.now()
        random.seed(int(user_info.get('password', '123').encode().hex()) + current_time.day)
        
        hours_to_add = random.choice([3, 4, 5])
        minutes_to_add = random.choice([0, 15, 30, 45])
        traffic_time = current_time + timedelta(hours=hours_to_add)
        traffic_time = traffic_time.replace(minute=minutes_to_add)
        
        formatted_traffic_time = traffic_time.strftime("%I:%M %p")
        best_time = f"⏱️ TODAY AT {formatted_traffic_time} (Optimized Live Channel Traffic)"

        if "cartoon" in category:
            topics = ["সোনার পাখি ও জাদুকরী রূপনগর রাজ্যের কেল্লা", "ভুতুড়ে বিলের রহস্যময় ডাইনি বুড়ি", "টুনটুনি আর চালাক শেয়ালের বুদ্ধির খেলা"]
            titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon Stories 2026", "ভুতুড়ে বিলের রহস্যময়ী ডাইনি! 👺 | Bengali Animated Story", "টুনটুনি পাখি বনাম চালাক শেয়াল! নতুন রূপকথার গল্প"]
            descs = ["Description: আজ রূপনগরের জাদুকরী পাখি ও লোভী রাজার একদম নতুন পর্ব। \nThumbnail: 🟢 HD Auto-Render Complete", "Description: @ভুতুড়ে বিলের গভীর রাতের গা ছমছমে কার্টুন গল্প। \nThumbnail: 🟢 4K Thumbnail Loaded", "Description: চালাক শেয়ালকে কীভাবে উচিত শিক্ষা দিল টুনটুনি। \nThumbnail: 🟢 AI Frame Rendered"]
            lengths = ["⏳ 11 Minutes 45 Seconds", "⏳ 09 Minutes 12 Seconds", "⏳ 13 Minutes 20 Seconds"]
        elif "documentary" in category:
            topics = ["The Deep Secrets of Bermuda Triangle", "Mystery of Ancient Egyptian Pyramids", "World War II Unsolved Hidden Codes"]
            titles = ["Bermuda Triangle: The Unsolved Graveyard of Ocean 🌊", "The Secret Rooms Inside Pyramids Hidden For 4000 Years!", "The Deadliest Hidden Codes of WW2 Left Unanswered."]
            descs = ["Description: Secrets of deep oceanic anomalies.\nThumbnail: 🟢 Ultra-Detail Overlay Ready", "Description: Exploring hidden tunnels of Egypt.\nThumbnail: 🟢 3D Map Vector Loaded", "Description: Unsolved historical communication codes.\nThumbnail: 🟢 Vintage Classified Graphic"]
            lengths = ["⏳ 18 Minutes 24 Seconds", "⏳ 22 Minutes 10 Seconds", "⏳ 15 Minutes 50 Seconds"]
        else:
            topics = ["AI Automation Trends of 2026", "How To Scale Faceless YouTube Channel Fast", "Viral Editing Hacks with Topaz AI"]
            titles = ["The Future is Here: AI Systems of 2026 You Can't Ignore! 🔥", "I Started a Faceless YouTube Channel in 24 Hours (Secret AI Strategy)", "Cinematic Visuals Masterclass: Topaz AI Video Enhancement Tutorial"]
            descs = ["Description: Complete guide on 2026 AI tools.\nThumbnail: 🟢 Neon Dashboard Frame Ready", "Description: Faceless workflow for massive viral growth.\nThumbnail: 🟢 Analytics Concept Complete", "Description: Enhance old footage with AI processing.\nThumbnail: 🟢 Split Before/After Rendered"]
            lengths = ["⏳ 08 Minutes 15 Seconds", "⏳ 10 Minutes 42 Seconds", "⏳ 07 Minutes 30 Seconds"]

        idx = random.randint(0, len(topics)-1)
        
        return jsonify({
            "topic": topics[idx],
            "title": titles[idx],
            "desc_thumb": descs[idx],
            "length": lengths[idx],
            "upload_time": best_time,
            "status": "🤖 AI ENGINE STATUS: 🟢 CHANNEL TRAFFIC MATCHED & QUEUED FOR AUTO-POST"
        })
    except Exception as e:
        return jsonify({"topic": "Error loading live data"})

@app.route('/login', methods=['POST'])
def login():
    if users_collection is None: return jsonify({"status": "ERROR", "message": "Database currently offline!"})
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        admin_info = users_collection.find_one({"_id": "admin"})
        if username == admin_info["user_id"] and password == admin_info["password"]:
            session.permanent = True
            session['username'] = "Owner"
            session['role'] = "admin"
            return jsonify({"status": "SUCCESS", "message": "👑 Admin verified! Access granted."})
            
        user_data = users_collection.find_one({"_id": username})
        if user_data and user_data["password"] == password:
            if not user_data.get('is_approved', False): 
                return jsonify({"status": "ERROR", "message": "⏳ Request is still PENDING approval!"})
            if user_data.get('is_blocked', False): 
                return jsonify({"status": "ERROR", "message": "🛑 LOGIN DENIED: Account is BLOCKED!"})
            
            session.permanent = True
            session['username'] = username
            session['role'] = "customer"
            return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"Login processing error: {e}"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

@app.route('/register_request', methods=['POST'])
def register_request():
    if users_collection is None: return jsonify({"status": "ERROR", "message": "Database disconnected!"})
    try:
        data = request.json
        name = data.get('name', '').strip(); phone = data.get('phone', '').strip(); gmail = data.get('gmail', '').strip(); password = data.get('password', '').strip()
        
        if users_collection.find_one({"_id": phone}): 
            return jsonify({"status": "ERROR", "message": "🛑 Number already registered!"})
            
        users_collection.insert_one({
            "_id": phone,
            "name": name,
            "password": password,
            "category": "",
            "gmail": gmail,
            "is_approved": False,
            "is_blocked": False,
            "youtube_linked": False,
            "approved_at": "",
            "role": "customer"
        })
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    if users_collection is None: return jsonify({"status": "PENDING"})
    try:
        phone = request.json.get('phone', '').strip()
        user_data = users_collection.find_one({"_id": phone})
        if not user_data: return jsonify({"status": "REJECTED"})
        if user_data.get('is_approved', False): return jsonify({"status": "APPROVED"})
    except Exception as e:
        print(f"Error checking approval status: {e}")
    return jsonify({"status": "PENDING"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session.get('role') != 'admin' or users_collection is None: return jsonify({"status": "ERROR"})
    try:
        data = request.json; target_user = data.get('target_user'); action = data.get('action')
        if action == 'approve': 
            today_str = datetime.now().strftime("%Y-%m-%d")
            users_collection.update_one({"_id": target_user}, {"$set": {"is_approved": True, "approved_at": today_str}})
            return jsonify({"status": "SUCCESS", "message": "✅ Account APPROVED Live!"})
        elif action == 'reject': 
            users_collection.delete_one({"_id": target_user})
            return jsonify({"status": "SUCCESS", "message": "❌ Account REJECTED!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})
    return jsonify({"status": "ERROR"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session or users_collection is None: return jsonify({"status": "ERROR"})
    username = session['username']
    users_collection.update_one({"_id": username}, {"$set": {"youtube_linked": True}})
    return jsonify({"status": "SUCCESS"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session.get('role') != 'customer' or users_collection is None: return jsonify({"status": "ERROR"})
    try:
        selected_cat = request.json.get('category', '').strip(); username = session['username']
        users_collection.update_one({"_id": username}, {"$set": {"category": selected_cat}})
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session.get('role') != 'admin' or users_collection is None: return jsonify({"status": "ERROR"})
    try:
        data = request.json; target_user = data.get('target_user'); action = data.get('action')
        is_blocked = True if action == 'block' else False
        users_collection.update_one({"_id": target_user}, {"$set": {"is_blocked": is_blocked}})
        return jsonify({"status": "SUCCESS", "message": f"📊 User status updated to {action.upper()}!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session.get('role') != 'admin' or users_collection is None: return jsonify({"status": "ERROR"})
    try:
        target_user = request.json.get('target_user')
        users_collection.delete_one({"_id": target_user})
        return jsonify({"status": "SUCCESS", "message": "💥 Customer DELETED from Cloud!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)
# Suhan SaaS Ultra Force Refresh 2026
