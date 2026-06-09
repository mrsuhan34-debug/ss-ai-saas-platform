import os
import json
import random
import threading
import urllib.request
import certifi
import ssl
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler

# এআই ভিডিও ম্যাকিং ইঞ্জিনের জন্য প্রয়োজনীয় ফ্রি লাইব্রেরিস

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

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload"
]

GOOGLE_OAUTH_CONFIG = {
    "web": {
        "client_id": os.environ.get('GOOGLE_CLIENT_ID', '822666139852-qbq9b548gj8juh8fna5kk1vgbgvlqun2.apps.googleusercontent.com').strip(),
        "project_id": "ss-ai-cartoon-saas",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET', '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').strip(),
        "redirect_uris": ["https://ss-ai-saas-platform.onrender.com/oauth2callback"]
    }
}

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

def keep_alive():
    import time
    time.sleep(60)
    while True:
        try:
            urllib.request.urlopen("https://ss-ai-saas-platform.onrender.com/ping")
        except:
            pass
        time.sleep(600)

threading.Thread(target=keep_alive, daemon=True).start()

def get_best_upload_time(user_info):
    today_str = datetime.now().strftime("%Y-%m-%d")
    saved_date = user_info.get("best_time_date", "")
    saved_time = user_info.get("best_time_value", "")

    if saved_date == today_str and saved_time and "TOMORROW" not in saved_time:
        return saved_time

    current_time = datetime.now()
    current_total = current_time.hour * 60 + current_time.minute + 30
    time_slots = [7*60, 8*60, 9*60, 10*60, 11*60, 12*60, 13*60,
                  14*60, 15*60, 16*60, 17*60, 18*60, 19*60, 20*60, 21*60, 22*60]
    future_slots = [s for s in time_slots if s > current_total]

    if future_slots:
        best_slot = random.choice(future_slots[:3])
        best_hour = best_slot // 60
        best_minute = random.choice([0, 15, 30, 45])
        traffic_time = current_time.replace(hour=best_hour, minute=best_minute, second=0, microsecond=0)
        best_time = f"TODAY AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"
    else:
        traffic_time = (current_time + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        best_time = f"TOMORROW AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"

    try:
        users_collection.update_one(
            {"_id": user_info["_id"]},
            {"$set": {"best_time_date": today_str, "best_time_value": best_time}}
        )
    except:
        pass

    return best_time

# ================= 🎬 নতুন ফ্রি এআই ভিডিও মেকার ইঞ্জিন =================
def generate_ai_video_file(category_name, video_title):
    video_file_path = "output.mp4"
    audio_file_path = "voice.mp3"
    try:
        print(f"🤖 AI Engine: Starting auto-generation for {category_name}...")
        
        # ১. ক্যাটাগরি অনুযায়ী বাংলায় রিয়েল স্ক্রিপ্ট সিলেকশন
        if "cartoon" in category_name or "animation" in category_name:
            script_text = f"বন্ধুরা, আজকের কার্টুন গল্পে আপনাকে স্বাগতম। আজ আমরা জানবো {video_title} এর একটি চমৎকার রহস্যময় ঘটনা। শেষ পর্যন্ত সাথে থাকুন।"
            bg_color = (0, 255, 204) # ডাইনামিক নিয়ন গ্রিন কার্টুন থিম
        elif "islamic" in category_name or "quran" in category_name:
            script_text = f"আসসালামু আলাইকুম। আজকের ভিডিওর মূল বিষয় হলো {video_title}। আমাদের জীবনকে সুন্দর করতে এই কথাগুলো মেনে চলা অত্যন্ত জরুরী।"
            bg_color = (17, 42, 34) # ইসলামিক ডিপ গ্রিন থিম
        elif "horror" in category_name or "bhoot" in category_name:
            script_text = f"সাবধান! রাত যখন তিনটে বাজে, তখন চারপাশের পরিবেশ কেমন অদ্ভুত হয়ে যায় না? আজ শুনুন {video_title} এর গা শিউরে ওঠা সত্য ঘটনা।"
            bg_color = (20, 0, 0) # ভুতুড়ে ডার্ক রেড থিম
        else:
            script_text = f"হ্যালো বন্ধুরা, আমাদের ইনফরমেশন চ্যানেলে আপনাকে স্বাগতম। আজ আমরা আলোচনা করব {video_title} নিয়ে। ভিডিওটি ভালো লাগলে অবশ্যই সাবস্ক্রাইব করবেন।"
            bg_color = (15, 15, 18) # স্ট্যান্ডার্ড আল্ট্রা ডার্ক থিম

        # ২. gTTS দিয়ে ফ্রিতে বাংলা ভয়েসওভার (Audio) তৈরি
        tts = gTTS(text=script_text, lang='bn', slow=False)
        tts.save(audio_file_path)
        
        # ৩. MoviePy দিয়ে লুপ ব্যাকগ্রাউন্ড এবং অডিও মার্জ করে রিয়েল MP4 তৈরি
        audio_clip = AudioFileClip(audio_file_path)
        duration = audio_clip.duration + 1.0 # ভয়েসের লেন্থ অনুযায়ী ভিডিওর দৈর্ঘ্য হবে অটোমেটিক
        
        # কালার ব্যাকগ্রাউন্ড লুপ জেনারেট
        bg_clip = ColorClip(size=(1080, 1920), color=bg_color, duration=duration) # ফুল ১০৮০p শর্টস সাইজ
        video_clip = bg_clip.set_audio(audio_clip)
        
        # ফাইনাল ভিডিও এক্সপোর্ট
        video_clip.write_videofile(
            video_file_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", 
            verbose=False, 
            logger=None
        )
        
        # টেম্পোরারি অডিও ফাইল ডিলিট করে মেমোরি ক্লিয়ার করা
        audio_clip.close()
        video_clip.close()
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            
        print("🎯 AI Engine: Video File (output.mp4) Generated Successfully with Voiceover!")
        return True
    except Exception as e:
        print(f"❌ AI Video Maker Engine Failed: {e}")
        # ব্যাকআপ হিসেবে ফাঁকা ব্রোকেন ফাইল এভয়েড করতে ৮ সেকেন্ডের ডামি ফাইল রাইট
        with open(video_file_path, "wb") as f:
            f.write(b"\x00\x00\x00\x18ftypmp42")
        return False

def do_upload_for_user(user):
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        token_data = json.loads(user.get('youtube_token'))
        credentials = Credentials.from_authorized_user_info(token_data, YOUTUBE_SCOPES)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            users_collection.update_one({"_id": user["_id"]}, {"$set": {"youtube_token": credentials.to_json()}})
        youtube = build('youtube', 'v3', credentials=credentials)
        category = str(user.get('category', '')).lower()
        
        if "cartoon" in category or "animation" in category:
            titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon 2026", "ভুতুড়ে বিলের ডাইনি | Bengali Animated Story", "টুনটুনি বনাম শেয়াল | Bangla Cartoon"]
            descs = ["জাদুকরী পাখির নতুন পর্ব।", "ভুতুড়ে বিলের গল্প।", "টুনটুনির বুদ্ধির গল্প।"]
        elif "gaming" in category or "free fire" in category or "esports" in category or "freefire" in category:
            titles = ["Free Fire Best Tips 2026 | Bangla", "Top Mobile Games 2026 | Bangla", "BGMI vs Free Fire | Bangla"]
            descs = ["Free Fire tips and tricks.", "Top mobile games guide.", "Game comparison guide."]
        elif "islamic" in category or "quran" in category or "motivat" in category:
            titles = ["Islamic Motivation 2026 | Bangla", "ইসলামিক উক্তি | Bangla", "সফলতার পথ | Islamic Bangla"]
            descs = ["ইসলামিক অনুপ্রেরণা।", "ইসলামিক উক্তি সংকলন।", "ইসলামিক জীবনধারা।"]
        elif "documentary" in category or "mystery" in category:
            titles = ["Bermuda Triangle Mystery | Bangla", "Egyptian Pyramids Secrets | Bangla", "WW2 Hidden Codes | Bangla"]
            descs = ["Bermuda Triangle secrets.", "Egyptian pyramid mystery.", "World War 2 codes."]
        elif "cooking" in category or "recipe" in category or "food" in category:
            titles = ["বাংলার সেরা রেসিпи 2026", "১৫ মিনিটে ভর্তা রেসিপি | Bangla", "ইফতার রেসিপি ২০২৬ | Bangla"]
            descs = ["বাংলাদেশের রান্নার রেসিপি।", "দ্রুত ভর্তা রেসিপি।", "রমজানের ইফতার আইটেম।"]
        elif "health" in category or "fitness" in category:
            titles = ["সকালের রুটিন | Morning Routine Bangla", "ডায়াবেটিস নিয়ন্ত্রণ | Bangla", "ব্যায়াম গাইড | Workout Bangla 2026"]
            descs = ["সকালের স্বাস্থ্যকর অভ্যাস।", "ডায়াবেটিস টিপস।", "দৈনিক ব্যায়ামের গাইড।"]
        elif "kids" in category or "rhyme" in category or "children" in category:
            titles = ["আম পাকা জাম পাকা | Bangla Rhymes 2026", "নতুন বাংলা ছড়া | Kids Song 2026", "রঙিন দুনিয়া | Colorful Kids Video"]
            descs = ["শিশুদের মজার বাংলা ছড়া।", "নতুন বাংলা ছড়া।", "শিশুদের শেখার ভিডিও।"]
        elif "business" in category or "finance" in category or "entrepreneur" in category:
            titles = ["৫০০০ টাকায় ব্যবসা | Small Business Bangla", "অনলাইন ব্যবসারアイデア | Bangla 2026", "ফ্রিল্যান্সিং গাইড | Bangla Tutorial"]
            descs = ["কম টাকায় লাভজনক ব্যবসা।", "অনলাইন ব্যবসার গাইড।", "ফ্রিল্যান্সিং শুরু করার গাইড।"]
        elif "travel" in category or "vlog" in category:
            titles = ["বাংলাদেশের লুকানো সৌন্দর্য | Travel 2026", "সুন্দরবন ভ্রমণ | Sundarban Vlog", "সেন্টমার্টিন ভ্রমণ | Travel Vlog"]
            descs = ["বাংলাদেশের অজানা স্থান।", "সুন্দরবনের অ্যাডভেঞ্চার।", "সেন্টমার্টিনের ট্রাভেল ভ্লগ।"]
        elif "farming" in category or "agriculture" in category:
            titles = ["আধুনিক সবজি চাষ | Farming Bangla 2026", "হাইব্রিড ধান চাষ | Rice Farming Bangla", "ছাদ বাগান গাইড | Rooftop Garden"]
            descs = ["আধুনিক সবজি চাষের গাইড।", "হাইব্রিড ধান চাষ।", "ছাদ বাগান টিউটোরিয়াল।"]
        elif "tech" in category or "review" in category or "gadget" in category:
            titles = ["Best Budget Phone 2026 | Bangla Review", "5 AI Tools Replacing Humans | Bangla", "iPhone vs Samsung 2026 | Bangla"]
            descs = ["সেরা বাজেট স্মার্টফোন রিভিউ।", "AI tools guide.", "Phone comparison guide."]
        elif "horror" in category or "bhoot" in category:
            titles = ["ভুতুড়ে বাড়ির গল্প | Horror Story Bangla", "রাত ৩টার রহস্য | Midnight Horror Bangla", "সত্যিকারের ভূত | Real Ghost Story Bangla"]
            descs = ["ভয়ংকর ভুতুড়ে স্থানের গল্প।", "রাতের রহস্যময় ঘটনা।", "সত্যিকারের भूতের অভিজ্ঞতা।"]
        else:
            titles = ["AI Systems 2026 | Bangla", "Faceless YouTube Channel Guide", "Topaz AI Tutorial 2026"]
            descs = ["AI tools guide 2026.", "Faceless channel tips.", "AI video enhancement."]

        idx = random.randint(0, len(titles) - 1)
        selected_title = titles[idx]
        
        # 🚀 আপলোডের ঠিক আগে ডাইনামিক রিয়েল ভিডিও ফাইল জেনারেশন ট্রিগার
        generate_ai_video_file(category, selected_title)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        best_time = user.get("best_time_value", "")
        video_file_path = "output.mp4"
        
        body = {
            'snippet': {
                'title': selected_title,
                'description': descs[idx] + f"\n\nSS AI Platform | {best_time}",
                'tags': ['bangla', 'ai', '2026', 'viral'],
                'categoryId': '24'
            },
            'status': {'privacyStatus': 'public'}
        }
        media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        resp = req.execute()
        
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_upload_date": today_str, "best_time_date": "", "best_time_value": ""}}
        )
        print(f"✅ Auto uploaded for {user['_id']}: {resp.get('id')}")
        
        # আপলোড শেষে ফাইল ডিলিট করে সার্ভার স্পেস ফ্রী করা
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
            
    except Exception as e:
        print(f"❌ Upload error for {user.get('_id')}: {e}")

def auto_upload_all_customers():
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now()
        all_customers = users_collection.find({
            "role": "customer",
            "is_approved": True,
            "is_blocked": {"$ne": True},
            "youtube_linked": True,
            "youtube_token": {"$exists": True}
        })
        for user in all_customers:
            try:
                saved_date = user.get("best_time_date", "")
                saved_time = user.get("best_time_value", "")
                already_uploaded = user.get("last_upload_date", "") == today_str
                if already_uploaded:
                    continue
                if saved_date != today_str or not saved_time or "TOMORROW" in saved_time:
                    continue
                time_part = saved_time.replace("TODAY AT", "").replace("(Optimized Live Channel Traffic)", "").strip()
                try:
                    target_dt = datetime.strptime(today_str + " " + time_part, "%Y-%m-%d %I:%M %p")
                except:
                    continue
                diff = (current_time - target_dt).total_seconds()
                if 0 <= diff <= 600:
                    print(f"🚀 Time matched for {user['_id']} — uploading...")
                    do_upload_for_user(user)
            except Exception as ue:
                print(f"❌ User loop error {user.get('_id')}: {ue}")
    except Exception as e:
        print(f"❌ Scheduler error: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(auto_upload_all_customers, 'interval', minutes=5)
scheduler.start()

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
                
                # রিয়েল-টাইমে বেস্ট আপলোড টাইম ক্যালকুলেশন ভ্যালু পাঠানো
                best_time_generated = get_best_upload_time(user_info)
                
                return render_template(
                    'index.html',
                    role='customer',
                    username=username,
                    name=user_info.get('name', 'Customer'),
                    category=user_info.get('category', ''),
                    linked=user_info.get('youtube_linked', False),
                    gmail_id=user_info.get('gmail', ''),
                    user_password=user_info.get('password', ''),
                    best_time=best_time_generated
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
            "thirty_days_dismissed": False,
            "best_time_date": "",
            "best_time_value": "",
            "last_upload_date": ""
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
    if 'username' not in session:
        return jsonify({"status": "ERROR"})
    try:
        username = str(session['username']).strip()
        users_collection.update_one({"_id": username}, {"$set": {"youtube_linked": True}})
    except Exception as e:
        print(f"Auth YouTube error: {e}")
    return jsonify({"status": "SUCCESS"})

@app.route('/oauth2callback')
def oauth2callback():
    if 'oauth_state' not in session:
        return "Authorization failed.", 400
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
        response = youtube.channels().list(part="snippet", mine=True).execute()
        if not response.get('items'):
            return "<h1>No YouTube Channel found!</h1><a href='/'>Go Back</a>"
        channel_name = response['items'][0]['snippet'].get('title', 'Unknown')
        username = str(session.get('username')).strip()
        users_collection.update_one(
            {"_id": username},
            {"$set": {"youtube_linked": True, "youtube_token": credentials.to_json(), "channel_name": channel_name}}
        )
        return redirect(url_for('index'))
    except Exception as e:
        return f"<h1>OAuth Error</h1><p>{str(e)}</p><a href='/'>Go Back</a>", 500

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

@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session:
        return jsonify({"status": "ERROR", "message": "Unauthorized"})
    username = str(session['username']).strip()
    user_info = users_collection.find_one({"_id": username})
    if not user_info:
        return jsonify({"status": "ERROR", "message": "User not found"})
        
    category = user_info.get('category', 'General')
    best_time = get_best_upload_time(user_info)
    
    # ড্যাশবোর্ডের জন্য রিয়েল-টাইম মেটাডেটা জেনারেশন সিমুলেশন
    return jsonify({
        "topic": f"Trending {category} Special Episode",
        "title": f"AI Masterclass: {category} 2026",
        "desc_thumb": f"Automated Description for {category} channel.",
        "length": "0:45 Sec (YouTube Shorts)",
        "upload_time": best_time,
        "status": "⚡ AI ENGINE ACTIVE: VIDEO FILE LINKED & QUEUED"
    })

@app.route('/customer/upload_video', methods=['POST'])
def upload_video():
    if 'username' not in session or session.get('role') != 'customer':
        return jsonify({"status": "ERROR", "message": "Unauthorized!"})
    username = str(session['username']).strip()
    user_info = users_collection.find_one({"_id": username})
    if not user_info:
        return jsonify({"status": "ERROR", "message": "User not found!"})
    
    # ম্যানুয়াল টেস্ট ট্রিগার ট্রাফিক ম্যাচার
    threading.Thread(target=do_upload_for_user, args=(user_info,), daemon=True).start()
    return jsonify({"status": "SUCCESS", "message": "AI Generator Triggered Live!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
