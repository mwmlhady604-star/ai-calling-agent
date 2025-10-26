from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from config import MONGODB_URI

client = None
db = None

try:
    if MONGODB_URI:
        client = MongoClient(MONGODB_URI)
        db = client.Cluster0
        print("✅ Connected to MongoDB")
    else:
        print("⚠️ MONGODB_URI not set. Running without database.")
except ConfigurationError as e:
    print(f"⚠️ MongoDB configuration error: {e}")
    client = None
    db = None

# Collection Definitions (only if db is available)
if db:
    users_collection = db.users
    session_logs_collection = db.session_logs
    therapy_progress_collection = db.therapy_progress
    appointments_collection = db.appointments
    chat_history_collection = db.chat_history
else:
    users_collection = session_logs_collection = therapy_progress_collection = appointments_collection = chat_history_collection = None


# ==== USER OPERATIONS ====
def add_user(user_data):
    if not users_collection: return None
    return users_collection.insert_one(user_data).inserted_id

def get_user(user_id):
    if not users_collection: return None
    return users_collection.find_one({"_id": user_id})

def update_user(user_id, update_data):
    if not users_collection: return
    users_collection.update_one({"_id": user_id}, {"$set": update_data})

def get_userid_by_phone(phone):
    if not users_collection: return None
    user = users_collection.find_one({"phone": phone})
    return user['_id'] if user else None

def verify_user(phone):
    if not users_collection: return False
    return users_collection.find_one({"phone": phone}) is not None

def has_interacted_before(phone):
    if not users_collection: return False
    user = users_collection.find_one({"phone": phone})
    return user.get('has_interacted_before', False) if user else False

def set_interacted_before(phone):
    if not users_collection: return False
    users_collection.update_one({"phone": phone}, {"$set": {"has_interacted_before": True}})
    return True


# ==== SESSION LOGS ====
def add_session_log(session_data):
    if not session_logs_collection: return None
    return session_logs_collection.insert_one(session_data).inserted_id

def get_session_logs(user_id):
    if not session_logs_collection: return []
    return list(session_logs_collection.find({"user_id": user_id}))


# ==== THERAPY PROGRESS ====
def add_therapy_progress(progress_data):
    if not therapy_progress_collection: return None
    return therapy_progress_collection.insert_one(progress_data).inserted_id

def get_therapy_progress(user_id):
    if not therapy_progress_collection: return []
    return list(therapy_progress_collection.find({"user_id": user_id}))

def update_therapy_progress(progress_id, update_data):
    if not therapy_progress_collection: return
    therapy_progress_collection.update_one({"_id": progress_id}, {"$set": update_data})


# ==== APPOINTMENTS ====
def book_appointment(userid, appointment_data):
    if not appointments_collection: return None
    return appointments_collection.insert_one({"user_id": userid, "appointment_data": appointment_data}).inserted_id

def get_appointments(user_id):
    if not appointments_collection: return []
    return list(appointments_collection.find({"user_id": user_id}))

def update_appointment(appointment_id, update_data):
    if not appointments_collection: return
    appointments_collection.update_one({"_id": appointment_id}, {"$set": update_data})

def delete_appointment(appointment_id):
    if not appointments_collection: return
    appointments_collection.delete_one({"_id": appointment_id})


# ==== CHAT HISTORY ====
def set_chat_history(user_id, message_data):
    if not chat_history_collection: return
    chat_history_collection.update_one(
        {"user_id": user_id},
        {"$push": {"messages": {"$each": message_data}}},
        upsert=True
    )

def get_chat_history(user_id):
    if not chat_history_collection: return None
    return chat_history_collection.find_one({"user_id": user_id})

def update_chat_history(user_id, update_data):
    if not chat_history_collection: return
    chat_history_collection.update_one({"user_id": user_id}, {"$set": update_data})
