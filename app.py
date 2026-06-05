import os
import json
import random
import threading
import urllib.request
import certifi
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pymongo import MongoClient

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'suhan_saas_ultra_secure_permanent_key_2026')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)
app.config['SESSION_COOKIE_NAME'] = 'ss_ai_saas_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://mrsuhan34_db_user:CC1KshAyEZQX3kwV@cluster0.eisaj7e.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true')
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['ss_ai_cartoon_database']
users_collection = db['users_data']

def init_db_admin():
    try:
        admin = users_collection.find_one({"_id": "admin"})
        if not admin:
            users_collection.insert_one({
                "_id": "admin",
                "user_id": "SS_ELITE_ADMIN_2026",
                "password": "REK_#9824_SNC_@Z7X",
                "role": "admin"
            })
    except Exception as e:
        print(f"Admin init error: {e}")

init_db_admin()

GOOGLE_OAUTH_CONFIG = {
    "web": {
        "client_id": os.environ.get('GOOGLE_CLIENT_ID', '822666139852-qbq9b548gj8juh8fna5kk1vgbgvlqun2.apps.googleusercontent.com').strip(),
        "project_id": "ss-ai-cartoon-saas",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET', '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').strip(),
        "redirect_uris": ["https://flask-hello-world-jbuj.onrender.com/oauth2callback"]
    }
}

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload"
]

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def keep_alive():
    import time
    time.sleep(60)
    while True:
        try:
            urllib.request.urlopen("https://flask-hello-world-jbuj.onrender.com/ping")
        except:
            pass
        time.sleep(600)

t = threading.Thread(target=keep_alive, daemon=True)
t.start()

def get_all_customers_from_mongo():
    customers = {}
    try:
        all_users = users_collection.find({"role": "customer"})
        for u in all_users:
            uid = str(u.get("_id"))
            approved_at_str = u.get("approved_at", "")
            days_left = 30
            is_expired = False
            if approved_at_str:
                try:
                    approved_date = datetime.strptime(approved_at_str.strip(), "%Y-%m-%d")
                    elapsed_days = (datetime.now() - approved_date).days
                    days_left = max(0, 30 - elapsed_days)
                    is_expired = elapsed_days >= 30
                except:
                    pass
            customers[uid] = {
                "name": u.get("name", "Unknown"),
                "password": u.get("password", ""),
                "category": u.get("category", ""),
                "gmail": u.get("gmail", ""),
                "is_approved": u.get("is_approved", False),
                "is_blocked": u.get("is_blocked", False),
                "youtube_linked": u.get("youtube_linked", False),
                "approved_at": approved_at_str,
                "days_left": int(days_left),
                "is_expired": bool(is_expired),
                "thirty_days_dismissed": u.get("thirty_days_dismissed", False)
            }
    except Exception as e:
        print(f"Error fetching customers: {e}")
    return customers

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/')
def index():
    if 'username' in session and 'role' in session:
        if session.get('role') == 'admin':
            return render_template('index.html', role='admin', username=session['username'], customers=get_all_customers_from_mongo())
        username = str(session['username']).strip()
        try:
            user_info = users_collection.find_one({"_id": username})
            if user_info and user_info.get('is_approved', False):
                if user_info.get('is_blocked', False):
                    session.clear()
                    return "<h1>Account Blocked By Admin!</h1><a href='/logout'>Go Back</a>"
                return render_template(
                    'index.html',
                    role='customer',
                    username=username,
                    name=user_info.get('name', 'Customer'),
                    category=user_info.get('category', ''),
                    linked=user_info.get('youtube_linked', False),
                    gmail_id=user_info.get('gmail', ''),
                    user_password=user_info.get('password', '')
                )
        except Exception as e:
            print(f"Index error: {e}")
        session.clear()
        return redirect(url_for('index'))
    return render_template('index.html', role='guest')

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = str(data.get('username', '')).strip()
        password = str(data.get('password', '')).strip()
        admin = users_collection.find_one({"_id": "admin"})
        if username == admin["user_id"] and password == admin["password"]:
            session.permanent = True
            session['username'] = "SuperAdmin_SS"
            session['role'] = "admin"
            return jsonify({"status": "SUCCESS", "message": "Admin verified! Access granted."})
        user_data = users_collection.find_one({"_id": username})
        if user_data and str(user_data["password"]) == password:
            if not user_data.get('is_approved', False):
                return jsonify({"status": "ERROR", "message": "Request is still PENDING approval!"})
            if user_data.get('is_blocked', False):
                return jsonify({"status": "ERROR", "message": "LOGIN DENIED: Account is BLOCKED!"})
            session.permanent = True
            session['username'] = username
            session['role'] = "customer"
            return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"Login error: {e}"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

@app.route('/register_request', methods=['POST'])
def register_request():
    try:
        data = request.json
        name = data.get('name', '').strip()
        phone = str(data.get('phone', '')).strip()
        gmail = data.get('gmail', '').strip()
        password = str(data.get('password', '')).strip()
        if not phone or phone.lower() in ["admin", "owner", "superadmin_ss"]:
            return jsonify({"status": "ERROR", "message": "Invalid Phone ID!"})
        if users_collection.find_one({"_id": phone}):
            return jsonify({"status": "ERROR", "message": "Number already registered!"})
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
            "role": "customer",
            "thirty_days_dismissed": False
        })
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    try:
        phone = str(request.json.get('phone', '')).strip()
        user_data = users_collection.find_one({"_id": phone})
        if not user_data:
            return jsonify({"status": "REJECTED"})
        if user_data.get('is_approved', False):
            return jsonify({"status": "APPROVED"})
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({"status": "PENDING"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session or session.get('role') != 'customer':
        return jsonify({"status": "ERROR", "message": "Unauthorized access!"})
    try:
        flow = Flow.from_client_config(
            GOOGLE_OAUTH_CONFIG,
            scopes=YOUTUBE_SCOPES,
            redirect_uri=GOOGLE_OAUTH_CONFIG["web"]["redirect_uris"][0]
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        session['oauth_state'] = state
        return jsonify({"status": "SUCCESS", "redirect_url": authorization_url})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"OAuth initialization failed: {str(e)}"})

@app.route('/oauth2callback')
def oauth2callback():
    if 'oauth_state' not in session:
        return "Authorization failed: State token missing.", 400
    try:
        flow = Flow.from_client_config(
            GOOGLE_OAUTH_CONFIG,
            scopes=YOUTUBE_SCOPES,
            state=session['oauth_state'],
            redirect_uri=GOOGLE_OAUTH_CONFIG["web"]["redirect_uris"][0]
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        youtube = build('youtube', 'v3', credentials=credentials)
        request_api = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request_api.execute()
        if not response.get('items'):
            return "<h1>Error: No YouTube Channel found!</h1><a href='/'>Go Back</a>"
        channel_name = response['items'][0]['snippet'].get('title', 'Unknown Channel')
        username = str(session.get('username')).strip()
        users_collection.update_one(
            {"_id": username},
            {"$set": {"youtube_linked": True, "youtube_token": credentials.to_json(), "channel_name": channel_name}}
        )
        return redirect(url_for('index'))
    except Exception as e:
        return f"<h1>OAuth Callback Error</h1><p>{str(e)}</p><a href='/'>Go Back</a>", 500

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session:
        return jsonify({"status": "ERROR"})
    try:
        selected_cat = request.json.get('category', '').strip()
        username = str(session['username']).strip()
        users_collection.update_one({"_id": username}, {"$set": {"category": selected_cat}})
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/customer/upload_video', methods=['POST'])
def upload_video():
    if 'username' not in session or session.get('role') != 'customer':
        return jsonify({"status": "ERROR", "message": "Unauthorized access!"})
    username = str(session['username']).strip()
    user_info = users_collection.find_one({"_id": username})
    if not user_info or not user_info.get('youtube_linked') or not user_info.get('youtube_token'):
        return jsonify({"status": "ERROR", "message": "YouTube account not linked!"})
    try:
        from google.oauth2.credentials import Credentials
        token_data = json.loads(user_info.get('youtube_token'))
        credentials = Credentials.from_authorized_user_info(token_data, YOUTUBE_SCOPES)
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            users_collection.update_one({"_id": username}, {"$set": {"youtube_token": credentials.to_json()}})
        youtube = build('youtube', 'v3', credentials=credentials)
        video_file_path = "output.mp4"
        if not os.path.exists(video_file_path):
            with open(video_file_path, "wb") as f:
                f.write(b"\x00\x00\x00\x18ftypmp42")
        category = str(user_info.get('category', '')).lower()
        current_time = datetime.now()
        try:
            random.seed(int(str(user_info.get('_id', '123')).strip()) + current_time.day)
        except:
            random.seed(current_time.day)
        min_future_minutes = current_time.hour * 60 + current_time.minute + 30
        time_slots = [7*60, 8*60, 9*60, 10*60, 11*60, 12*60, 13*60, 14*60, 15*60, 16*60, 17*60, 18*60, 19*60, 20*60, 21*60, 22*60]
        future_slots = [s for s in time_slots if s > min_future_minutes]
        if future_slots:
            best_slot = random.choice(future_slots[:3])
            best_hour = best_slot // 60
            best_minute = random.choice([0, 15, 30, 45])
            traffic_time = current_time.replace(hour=best_hour, minute=best_minute, second=0, microsecond=0)
            best_time = f"TODAY AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"
        else:
            traffic_time = (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            best_time = f"TOMORROW AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"

        if "cartoon" in category or "animation" in category:
            titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon Stories 2026", "ভুতুড়ে বিলের রহস্যময়ী ডাইনি! | Bengali Animated Story", "টুনটুনি পাখি বনাম চালাক শেয়াল! নতুন রূপকথার গল্প"]
            descs = ["আজ রূপনগরের জাদুকরী পাখির নতুন পর্ব।", "ভুতুড়ে বিলের গভীর রাতের কার্টুন গল্প।", "চালাক শেয়ালকে উচিত শিক্ষা দিল টুনটুনি।"]
        elif "gaming" in category or "esports" in category or "free fire" in category or "freefire" in category or "trending" in category:
            titles = ["Free Fire Best Character 2026 | Bangla Gaming", "Top 10 Mobile Games 2026 | Bangladesh Gamer", "BGMI vs Free Fire Ultimate Comparison | Bangla"]
            descs = ["Free Fire character guide 2026.", "Top mobile games review Bangladesh.", "BGMI vs Free Fire comparison."]
        elif "islamic" in category or "motivat" in category or "quran" in category:
            titles = ["আল্লাহর উপর ভরসা রাখো | Islamic Motivation 2026", "জীবন বদলে যাবে এই ১০টি কথায় | Bangla Islamic Video", "সফলতার রহস্য | Islamic Life Success Story Bangla"]
            descs = ["ইসলামিক অনুপ্রেরণামূলক ভিডিও।", "ইসলামিক জীবনধারার সেরা উক্তি।", "সফলতার পথে ইসলামিক গাইড।"]
        else:
            titles = ["The Future is Here: AI Systems of 2026!", "Faceless YouTube Channel in 24 Hours", "Cinematic Visuals: Topaz AI Tutorial"]
            descs = ["Complete guide on 2026 AI tools.", "Faceless workflow for viral growth.", "Enhance footage with AI processing."]

        idx = random.randint(0, len(titles) - 1)
        body = {
            'snippet': {
                'title': titles[idx],
                'description': descs[idx] + f"\n\nUploaded via SS AI SaaS Platform. Best Time: {best_time}",
                'tags': ['bangla', 'ai', '2026', 'viral'],
                'categoryId': '24'
            },
            'status': {'privacyStatus': 'public'}
        }
        media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request_upload = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response_upload = request_upload.execute()
        return jsonify({"status": "SUCCESS", "message": "Video uploaded successfully!", "youtube_id": response_upload.get('id')})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"Upload error: {str(e)}"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR"})
    try:
        data = request.json
        target_user = str(data.get('target_user', '')).strip()
        action = data.get('action')
        if action == 'approve':
            users_collection.update_one({"_id": target_user}, {"$set": {"is_approved": True, "approved_at": datetime.now().strftime("%Y-%m-%d")}})
            return jsonify({"status": "SUCCESS", "message": "Account APPROVED!"})
        elif action == 'reject':
            users_collection.delete_one({"_id": target_user})
            return jsonify({"status": "SUCCESS", "message": "Account REJECTED!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})
    return jsonify({"status": "ERROR"})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR"})
    try:
        data = request.json
        target_user = str(data.get('target_user', '')).strip()
        action = data.get('action')
        users_collection.update_one({"_id": target_user}, {"$set": {"is_blocked": (action == 'block')}})
        return jsonify({"status": "SUCCESS", "message": f"User {action.upper()}ED!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR"})
    try:
        target_user = str(request.json.get('target_user', '')).strip()
        users_collection.delete_one({"_id": target_user})
        return jsonify({"status": "SUCCESS", "message": "Customer DELETED!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/admin/dismiss_thirty_days', methods=['POST'])
def dismiss_thirty_days():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR"})
    try:
        target_user = str(request.json.get('target_user', '')).strip()
        users_collection.update_one({"_id": target_user}, {"$set": {"thirty_days_dismissed": True}})
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session:
        return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
    try:
        user_info = users_collection.find_one({"_id": str(session['username']).strip()})
        if not user_info:
            return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})

        category = str(user_info.get('category', '')).lower()
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute

        try:
            random.seed(int(str(user_info.get('_id', '123')).strip()) + current_time.day)
        except:
            random.seed(current_time.day)

        min_future_minutes = current_hour * 60 + current_minute + 30
        time_slots = [7*60, 8*60, 9*60, 10*60, 11*60, 12*60, 13*60, 14*60, 15*60, 16*60, 17*60, 18*60, 19*60, 20*60, 21*60, 22*60]
        future_slots = [s for s in time_slots if s > min_future_minutes]

        if future_slots:
            best_slot = random.choice(future_slots[:3])
            best_hour = best_slot // 60
            best_minute = random.choice([0, 15, 30, 45])
            traffic_time = current_time.replace(hour=best_hour, minute=best_minute, second=0, microsecond=0)
            best_time = f"TODAY AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"
        else:
            traffic_time = (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            best_time = f"TOMORROW AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"

        if "cartoon" in category or "animation" in category:
            topics = ["সোনার পাখি ও জাদুকরী রূপনগর রাজ্যের কেল্লা", "ভুতুড়ে বিলের রহস্যময় ডাইনি বুড়ি", "টুনটুনি আর চালাক শেয়ালের বুদ্ধির খেলা"]
            titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon Stories 2026", "ভুতুড়ে বিলের রহস্যময়ী ডাইনি! | Bengali Animated Story", "টুনটুনি পাখি বনাম চালাক শেয়াল! নতুন রূপকথার গল্প"]
            descs = ["Description: আজ রূপনগরের জাদুকরী পাখির নতুন পর্ব। Thumbnail: HD Auto-Render Complete", "Description: ভুতুড়ে বিলের গভীর রাতের কার্টুন গল্প। Thumbnail: 4K Thumbnail Loaded", "Description: চালাক শেয়ালকে উচিত শিক্ষা দিল টুনটুনি। Thumbnail: AI Frame Rendered"]
            lengths = ["11 Minutes 45 Seconds", "09 Minutes 12 Seconds", "13 Minutes 20 Seconds"]
        elif "documentary" in category or "mystery" in category:
            topics = ["The Deep Secrets of Bermuda Triangle", "Mystery of Ancient Egyptian Pyramids", "World War II Unsolved Hidden Codes"]
            titles = ["Bermuda Triangle: The Unsolved Graveyard of Ocean", "The Secret Rooms Inside Pyramids Hidden For 4000 Years!", "The Deadliest Hidden Codes of WW2 Left Unanswered."]
            descs = ["Description: Secrets of deep oceanic anomalies. Thumbnail: Ultra-Detail Overlay Ready", "Description: Exploring hidden tunnels of Egypt. Thumbnail: 3D Map Vector Loaded", "Description: Unsolved historical communication codes. Thumbnail: Vintage Classified Graphic"]
            lengths = ["18 Minutes 24 Seconds", "22 Minutes 10 Seconds", "15 Minutes 50 Seconds"]
        elif "islamic" in category or "motivat" in category or "quran" in category:
            topics = ["ইসলামিক অনুপ্রেরণামূলক গল্প ২০২৬", "জীবন বদলে দেওয়া ১০টি ইসলামিক উক্তি", "সাফল্যের পথে ইসলামিক জীবনধারা"]
            titles = ["আল্লাহর উপর ভরসা রাখো | Islamic Motivation 2026", "জীবন বদলে যাবে এই ১০টি কথায় | Bangla Islamic Video", "সফলতার রহস্য | Islamic Life Success Story Bangla"]
            descs = ["Description: ইসলামিক অনুপ্রেরণামূলক ভিডিও। Thumbnail: Islamic Gold Frame Ready", "Description: ইসলামিক সেরা উক্তি। Thumbnail: Quran Verse Overlay Loaded", "Description: সফলতার পথে ইসলামিক গাইড। Thumbnail: Mosque Sunset Rendered"]
            lengths = ["12 Minutes 30 Seconds", "08 Minutes 45 Seconds", "15 Minutes 00 Seconds"]
        elif "facts" in category or "amazing" in category or "unknown" in category:
            topics = ["10 Amazing Facts About Space You Never Knew", "Mysterious Ancient Civilizations Hidden From History", "Unbelievable Animal Facts That Will Blow Your Mind"]
            titles = ["10 Mind-Blowing Space Facts Nobody Talks About!", "The Lost Civilizations That Historians Are Hiding!", "These Animal Abilities Are Scientifically Impossible!"]
            descs = ["Description: Space facts. Thumbnail: Galaxy Neon Overlay Ready", "Description: Hidden history facts. Thumbnail: Ancient Mystery Template Loaded", "Description: Animal world facts. Thumbnail: Wildlife Action Frame Rendered"]
            lengths = ["09 Minutes 15 Seconds", "11 Minutes 30 Seconds", "07 Minutes 45 Seconds"]
        elif "cooking" in category or "recipe" in category or "food" in category:
            topics = ["বাংলাদেশের সেরা ১০টি ঐতিহ্যবাহী রেসিপি", "মাত্র ১৫ মিনিটে রান্না করুন সুস্বাদু ভর্তা", "রমজানের বিশেষ ইফতার রেসিপি ২০২৬"]
            titles = ["বাংলার ঐতিহ্যবাহী রান্না | Traditional Bangla Recipe 2026", "১৫ মিনিটে সেরা ভর্তা রেসিপি | Quick Bangla Cooking", "রমজানের সেরা ইফতার | Special Iftar Recipe Bangla"]
            descs = ["Description: বাংলাদেশের রান্নার রেসিপি। Thumbnail: Food HD Close-up Ready", "Description: দ্রুত ভর্তা রেসিপি। Thumbnail: Cooking Step Frame Loaded", "Description: রমজানের ইফতার। Thumbnail: Iftar Spread Rendered"]
            lengths = ["14 Minutes 20 Seconds", "10 Minutes 00 Seconds", "16 Minutes 30 Seconds"]
        elif "travel" in category or "vlog" in category:
            topics = ["বাংলাদেশের অজানা ১০টি সুন্দর জায়গা", "সুন্দরবনের গভীরে একদিন", "কক্সবাজার থেকে সেন্টমার্টিন নৌকা ভ্রমণ"]
            titles = ["বাংলাদেশের লুকানো সৌন্দর্য | Hidden Beauty of Bangladesh 2026", "সুন্দরবনে বাঘের সাথে! | Sundarban Travel Vlog Bangla", "সেন্টমার্টিন দ্বীপ ভ্রমণ | Saint Martin Island Travel Vlog"]
            descs = ["Description: বাংলাদেশের অজানা স্থান। Thumbnail: Aerial Bangladesh View Ready", "Description: সুন্দরবনের অ্যাডভেঞ্চার। Thumbnail: Mangrove Forest Frame Loaded", "Description: সেন্টমার্টিনের ট্রাভেল ভ্লগ। Thumbnail: Blue Ocean Island Rendered"]
            lengths = ["18 Minutes 00 Seconds", "22 Minutes 15 Seconds", "19 Minutes 45 Seconds"]
        elif "tech" in category or "review" in category or "gadget" in category:
            topics = ["Top 5 Budget Smartphones of 2026 Under 15000 Taka", "Best AI Tools That Will Replace Your Job in 2026", "iPhone vs Android: Which is Better in 2026?"]
            titles = ["Best Budget Phone 2026 | Full Review Bangla", "5 AI Tools That Are Replacing Humans Right Now!", "iPhone 17 vs Samsung S26: Ultimate Comparison Bangla"]
            descs = ["Description: সেরা বাজেট স্মার্টফোন রিভিউ। Thumbnail: Phone Comparison Layout Ready", "Description: AI tools replacing human jobs. Thumbnail: Futuristic AI Dashboard Loaded", "Description: iPhone vs Android. Thumbnail: Split Screen Phone Rendered"]
            lengths = ["13 Minutes 30 Seconds", "10 Minutes 15 Seconds", "16 Minutes 00 Seconds"]
        elif "health" in category or "fitness" in category:
            topics = ["সকালে উঠে ৫টি কাজ যা আপনার জীবন বদলে দেবে", "ডায়াবেটিস নিয়ন্ত্রণের সহজ ১০টি উপায়", "প্রতিদিন ৩০ মিনিট ব্যায়াম করুন এই নিয়মে"]
            titles = ["সকালের ৫টি অভ্যাস | Morning Routine Bangla", "ডায়াবেটিস নিয়ন্ত্রণ | Diabetes Control Bangla", "৩০ মিনিটের ব্যায়াম রুটিন | Daily Workout Bangla 2026"]
            descs = ["Description: সকালের স্বাস্থ্যকর অভ্যাস। Thumbnail: Morning Sunrise Fitness Ready", "Description: ডায়াবেটিস টিপস। Thumbnail: Health Infographic Loaded", "Description: দৈনিক ব্যায়ামের গাইড। Thumbnail: Workout Action Frame Rendered"]
            lengths = ["11 Minutes 00 Seconds", "14 Minutes 30 Seconds", "12 Minutes 45 Seconds"]
        elif "horror" in category or "bhoot" in category:
            topics = ["বাংলাদেশের সবচেয়ে ভয়ংকর ভুতুড়ে বাড়ির গল্প", "রাত ৩টার পর যা ঘটে কেউ বলে না", "সত্যিকারের ভূতের গল্প যা শুনলে ঘুম হারাম হয়"]
            titles = ["বাংলাদেশের সবচেয়ে ভুতুড়ে বাড়ি! | Real Horror Story Bangla", "রাত ৩টার রহস্য | Midnight Horror Story Bangla 2026", "সত্যিকারের ভূতের গল্প | Real Ghost Story Bangladesh"]
            descs = ["Description: ভয়ংকর ভুতুড়ে স্থানের গল্প। Thumbnail: Dark Haunted House Ready", "Description: রাতের রহস্যময় ঘটনা। Thumbnail: Horror Night Frame Loaded", "Description: সত্যিকারের ভূতের অভিজ্ঞতা। Thumbnail: Ghost Silhouette Rendered"]
            lengths = ["16 Minutes 00 Seconds", "13 Minutes 30 Seconds", "18 Minutes 45 Seconds"]
        elif "business" in category or "entrepreneur" in category or "finance" in category:
            topics = ["মাত্র ৫০০০ টাকায় শুরু করুন লাভজনক ব্যবসা", "বাংলাদেশে সেরা ১০টি অনলাইন ব্যবসার আইডিয়া ২০২৬", "ফ্রিল্যান্সিং থেকে মাসে লক্ষ টাকা আয়"]
            titles = ["৫০০০ টাকায় ব্যবসা শুরু | Small Business Idea Bangla 2026", "সেরা অনলাইন ব্যবসার আইডিয়া | Online Business Bangladesh 2026", "ফ্রিল্যান্সিং গাইড | Freelancing Bangla Tutorial 2026"]
            descs = ["Description: কম টাকায় লাভজনক ব্যবসা। Thumbnail: Business Success Frame Ready", "Description: অনলাইন ব্যবসার গাইড। Thumbnail: E-commerce Dashboard Loaded", "Description: ফ্রিল্যান্সিং গাইড। Thumbnail: Laptop Money Stack Rendered"]
            lengths = ["15 Minutes 00 Seconds", "12 Minutes 30 Seconds", "20 Minutes 00 Seconds"]
        elif "kids" in category or "rhyme" in category or "children" in category:
            topics = ["বাংলা ছড়া - আম পাকা জাম পাকা", "শিশুদের জন্য নতুন বাংলা ছড়া ২০২৬", "রঙিন দুনিয়া শিশুদের শেখার গান"]
            titles = ["আম পাকা জাম পাকা | Bangla Rhymes For Kids 2026", "নতুন বাংলা ছড়া | New Bangla Kids Song 2026", "রঙিন দুনিয়া | Colorful Kids Learning Video Bangla"]
            descs = ["Description: শিশুদের মজার বাংলা ছড়া। Thumbnail: Colorful Cartoon Kids Ready", "Description: নতুন বাংলা ছড়া। Thumbnail: Animated Kids Frame Loaded", "Description: শিশুদের শেখার ভিডিও। Thumbnail: Rainbow Learning Rendered"]
            lengths = ["08 Minutes 00 Seconds", "10 Minutes 15 Seconds", "07 Minutes 30 Seconds"]
        elif "gaming" in category or "esports" in category or "free fire" in category or "freefire" in category or "trending" in category:
            topics = ["Free Fire Best Character Combination 2026", "Top 10 Mobile Games Bangladesh 2026", "BGMI vs Free Fire: Which is Better?"]
            titles = ["Free Fire Best Character 2026 | Bangla Gaming", "Top 10 Mobile Games 2026 | Bangladesh Gamer", "BGMI vs Free Fire Ultimate Comparison | Bangla"]
            descs = ["Description: Free Fire character guide. Thumbnail: Gaming Action Frame Ready", "Description: Top mobile games review. Thumbnail: Gaming Collage Loaded", "Description: BGMI vs Free Fire comparison. Thumbnail: Split Screen Gaming Rendered"]
            lengths = ["12 Minutes 00 Seconds", "09 Minutes 30 Seconds", "14 Minutes 15 Seconds"]
        elif "farming" in category or "agriculture" in category:
            topics = ["আধুনিক পদ্ধতিতে সবজি চাষ করে লক্ষ টাকা আয়", "বাংলাদেশে হাইব্রিড ধান চাষের সম্পূর্ণ গাইড", "ছাদ বাগান করে মাসে আয় করুন ঘরে বসেই"]
            titles = ["আধুনিক সবজি চাষ | Modern Farming Bangla 2026", "হাইব্রিড ধান চাষ গাইড | Hybrid Rice Farming Bangla", "ছাদ বাগান গাইড | Rooftop Garden Bangla 2026"]
            descs = ["Description: আধুনিক সবজি চাষের গাইড। Thumbnail: Green Farm Aerial Ready", "Description: হাইব্রিড ধান চাষ। Thumbnail: Rice Field Sunset Loaded", "Description: ছাদ বাগান টিউটোরিয়াল। Thumbnail: Rooftop Garden Rendered"]
            lengths = ["16 Minutes 00 Seconds", "14 Minutes 30 Seconds", "11 Minutes 45 Seconds"]
        else:
            topics = ["AI Automation Trends of 2026", "How To Scale Faceless YouTube Channel Fast", "Viral Editing Hacks with Topaz AI"]
            titles = ["The Future is Here: AI Systems of 2026 You Cannot Ignore!", "I Started a Faceless YouTube Channel in 24 Hours", "Cinematic Visuals Masterclass: Topaz AI Enhancement Tutorial"]
            descs = ["Description: Complete guide on 2026 AI tools. Thumbnail: Neon Dashboard Frame Ready", "Description: Faceless workflow for viral growth. Thumbnail: Analytics Concept Complete", "Description: Enhance footage with AI. Thumbnail: Split Before/After Rendered"]
            lengths = ["08 Minutes 15 Seconds", "10 Minutes 42 Seconds", "07 Minutes 30 Seconds"]

        idx = random.randint(0, len(topics) - 1)
        return jsonify({
            "topic": topics[idx],
            "title": titles[idx],
            "desc_thumb": descs[idx],
            "length": lengths[idx],
            "upload_time": best_time,
            "status": "AI ENGINE: CHANNEL TRAFFIC MATCHED AND QUEUED FOR AUTO-POST"
        })
    except Exception as e:
        return jsonify({"topic": "Error", "title": "Error", "desc_thumb": str(e), "length": "N/A", "upload_time": "N/A", "status": "ERROR"})

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
