from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import uuid
import numpy as np
import speech_recognition as sr
from typing import Dict, Any, Optional
from voice_chatbot import VoiceChatbot


# -----------------------------
# App Initialization
# -----------------------------
app = FastAPI(
    title="Farmer Scheme Recommendation API",
    version="1.0.0",
    description="API to recommend government schemes to farmers based on eligibility"
)

# -----------------------------
# Enable CORS (Frontend support)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load CSV Data
# -----------------------------
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(script_dir, "schemes.csv")

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"schemes.csv not found at: {CSV_PATH}")

schemes_df = pd.read_csv(CSV_PATH)

# Fill missing values safely
schemes_df.fillna("NA", inplace=True)

# -----------------------------
# Request Models
# -----------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class RecommendRequest(BaseModel):
    state: str
    crop: str
    land: float
    category: str


class ChatbotInput(BaseModel):
    session_id: Optional[str] = None
    text_input: Optional[str] = None
    language: Optional[str] = None


class AudioInput(BaseModel):
    session_id: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio
    language: Optional[str] = 'en-US'


class ChatbotResponse(BaseModel):
    session_id: str
    current_state: str
    message: str
    audio_url: Optional[str] = None
    collected_data: Dict[str, Any]
    is_complete: bool


# -----------------------------
# Chatbot Session Management
# -----------------------------
chatbot_sessions: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
    """Get existing session or create new one"""
    if session_id and session_id in chatbot_sessions:
        return session_id, chatbot_sessions[session_id]
    
    # Create new session
    new_session_id = str(uuid.uuid4())
    session_data = {
        'chatbot': VoiceChatbot(),
        'state': 'language',
        'language': 'English',
        'collected_data': {
            'state': None,
            'crop': None,
            'land': None,
            'category': None
        }
    }
    chatbot_sessions[new_session_id] = session_data
    return new_session_id, session_data


def process_chatbot_input(session_id: str, text_input: str) -> Dict[str, Any]:
    """Process user input and return next state"""
    if session_id not in chatbot_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chatbot_sessions[session_id]
    chatbot = session['chatbot']
    current_state = session['state']
    
    result = {
        'success': False,
        'message': '',
        'next_state': current_state,
        'parsed_value': None,
        'is_complete': False
    }
    
    # Handle language selection
    if current_state == 'language':
        detected_lang = chatbot.detect_language(text_input)
        if detected_lang in ['English', 'Hindi', 'Telugu']:
            session['language'] = detected_lang
            chatbot.set_language(detected_lang)
            session['state'] = 'state'
            result['success'] = True
            result['parsed_value'] = detected_lang
            result['next_state'] = 'state'
            result['message'] = chatbot.get_prompt('choose_state', detected_lang)
        else:
            result['message'] = chatbot.get_prompt('welcome', 'English')
    
    # Handle state input
    elif current_state == 'state':
        state_value = chatbot.parse_state(text_input, session['language'])
        if state_value:
            session['collected_data']['state'] = state_value
            session['state'] = 'crop'
            result['success'] = True
            result['parsed_value'] = state_value
            result['next_state'] = 'crop'
            result['message'] = chatbot.get_prompt('choose_crop', session['language'])
        else:
            result['message'] = chatbot.get_prompt('choose_state', session['language']) + " " + chatbot.get_prompt('error', session['language'])
    
    # Handle crop input
    elif current_state == 'crop':
        crop_value = chatbot.parse_crop(text_input, session['language'])
        if crop_value:
            session['collected_data']['crop'] = crop_value
            session['state'] = 'land'
            result['success'] = True
            result['parsed_value'] = crop_value
            result['next_state'] = 'land'
            result['message'] = chatbot.get_prompt('choose_land', session['language'])
        else:
            result['message'] = chatbot.get_prompt('choose_crop', session['language']) + " " + chatbot.get_prompt('error', session['language'])
    
    # Handle land input
    elif current_state == 'land':
        land_value = chatbot.parse_land(text_input)
        if land_value is not None:
            session['collected_data']['land'] = land_value
            session['state'] = 'category'
            result['success'] = True
            result['parsed_value'] = land_value
            result['next_state'] = 'category'
            result['message'] = chatbot.get_prompt('choose_category', session['language'])
        else:
            result['message'] = chatbot.get_prompt('choose_land', session['language']) + " " + chatbot.get_prompt('error', session['language'])
    
    # Handle category input
    elif current_state == 'category':
        category_value = chatbot.parse_category(text_input, session['language'])
        if category_value:
            session['collected_data']['category'] = category_value
            session['state'] = 'complete'
            result['success'] = True
            result['parsed_value'] = category_value
            result['next_state'] = 'complete'
            result['is_complete'] = True
            result['message'] = chatbot.get_prompt('processing', session['language'])
        else:
            result['message'] = chatbot.get_prompt('choose_category', session['language']) + " " + chatbot.get_prompt('error', session['language'])
    
    return result


# -----------------------------
# Root Endpoint
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to Farmer Scheme Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This information",
            "GET /health": "Health check",
            "POST /login": "User authentication",
            "POST /recommend": "Scheme recommendations"
        }
    }


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "OK"}


# -----------------------------
# Login API (Demo Authentication)
# -----------------------------
@app.post("/login")
def login(data: LoginRequest):
    # Demo login logic (for hackathon)
    if data.username == "admin" and data.password == "admin":
        return {"success": True}
    return {"success": False, "message": "Invalid credentials"}


# -----------------------------
# Recommendation Logic
# -----------------------------
@app.post("/recommend")
def recommend(data: RecommendRequest):
    state = data.state.strip()
    crop = data.crop.strip()
    land = data.land
    category = data.category.strip()
    
    # Debug: Log the incoming request
    print(f"[DEBUG] Received request: state='{state}', crop='{crop}', land={land}, category='{category}'")
    print(f"[DEBUG] Available states in CSV: {schemes_df['state'].unique().tolist()}")

    # Filter by state - case insensitive
    df = schemes_df[schemes_df["state"].str.lower() == state.lower()]

    print(f"[DEBUG] Filtered {len(df)} schemes for state '{state}'")
    
    if df.empty:
        raise HTTPException(status_code=404, detail="No schemes found for this state")

    results = []

    for _, row in df.iterrows():
        score = 0

        # Crop match - case insensitive
        if row["crop_type"].lower() == "all" or row["crop_type"].lower() == crop.lower():
            score += 2

        # Farmer category match - case insensitive
        if row["farmer_category"].lower() == "all" or row["farmer_category"].lower() == category.lower():
            score += 2

        # Land eligibility
        try:
            min_land = float(row["min_land"])
            max_land = float(row["max_land"])
            if min_land <= land <= max_land:
                score += 2
        except:
            pass

        if score > 0:
            results.append({
                "scheme_name": row["scheme_name"],
                "focus_area": row["focus_area"],
                "benefit_type": row["benefit_type"],
                "benefit_amount": row["benefit_amount"],
                "description": row["description"],
                "eligibility": row["eligibility"],
                "application_mode": row["application_mode"],
                "official_url": row["official_url"],
                "score": score
            })

    if not results:
        return {"message": "No eligible schemes found"}

    # Sort by score (highest first)
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results


# -----------------------------
# Ignore favicon.ico warnings
# -----------------------------
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return {}


# -----------------------------
# Chatbot Endpoints
# -----------------------------
@app.post("/chatbot/start")
def chatbot_start():
    """Initialize a new chatbot session"""
    session_id, session = get_or_create_session()
    chatbot = session['chatbot']
    
    welcome_msg = chatbot.get_prompt('welcome', 'English')
    
    return {
        "session_id": session_id,
        "current_state": "language",
        "message": welcome_msg,
        "collected_data": session['collected_data'],
        "is_complete": False
    }


@app.post("/chatbot/process")
def chatbot_process(data: ChatbotInput):
    """Process user input and return next prompt"""
    if not data.session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    if not data.text_input:
        raise HTTPException(status_code=400, detail="Text input required")
    
    result = process_chatbot_input(data.session_id, data.text_input)
    session = chatbot_sessions[data.session_id]
    
    return {
        "session_id": data.session_id,
        "current_state": result['next_state'],
        "message": result['message'],
        "collected_data": session['collected_data'],
        "is_complete": result['is_complete']
    }


@app.post("/chatbot/recommend")
def chatbot_recommend(data: ChatbotInput):
    """Get recommendations based on collected data"""
    if not data.session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    if data.session_id not in chatbot_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chatbot_sessions[data.session_id]
    collected = session['collected_data']
    
    # Validate all data is collected
    if not all(collected.values()):
        missing = [k for k, v in collected.items() if v is None]
        raise HTTPException(status_code=400, detail=f"Missing data: {', '.join(missing)}")
    
    # Get recommendations using existing logic
    state = collected['state']
    crop = collected['crop']
    land = collected['land']
    category = collected['category']
    
    # Filter by state - case insensitive
    df = schemes_df[schemes_df["state"].str.lower() == state.lower()]
    
    if df.empty:
        return {
            "session_id": data.session_id,
            "message": "No schemes found for this state",
            "recommendations": [],
            "is_complete": True
        }
    
    results = []
    
    for _, row in df.iterrows():
        score = 0
        
        # Crop match - case insensitive
        if row["crop_type"].lower() == "all" or row["crop_type"].lower() == crop.lower():
            score += 2
        
        # Farmer category match - case insensitive
        if row["farmer_category"].lower() == "all" or row["farmer_category"].lower() == category.lower():
            score += 2
        
        # Land eligibility
        try:
            min_land = float(row["min_land"])
            max_land = float(row["max_land"])
            if min_land <= land <= max_land:
                score += 2
        except:
            pass
        
        if score > 0:
            results.append({
                "scheme_name": row["scheme_name"],
                "focus_area": row["focus_area"],
                "benefit_type": row["benefit_type"],
                "benefit_amount": row["benefit_amount"],
                "description": row["description"],
                "eligibility": row["eligibility"],
                "application_mode": row["application_mode"],
                "official_url": row["official_url"],
                "score": score
            })
    
    if not results:
        return {
            "session_id": data.session_id,
            "message": "No eligible schemes found",
            "recommendations": [],
            "is_complete": True
        }
    
    # Sort by score (highest first)
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Get success message in selected language
    chatbot = session['chatbot']
    success_msg = chatbot.get_prompt('success', session['language'])
    
    return {
        "session_id": data.session_id,
        "message": success_msg,
        "recommendations": results,
        "is_complete": True
    }
@app.post("/speech-to-text")
def speech_to_text(data: AudioInput):
    """Convert speech audio to text"""
    try:
        # Get audio data from request
        audio_list = data.audio_data
        if not audio_list:
            return {"text": "", "error": "No audio data provided"}
        
        # Convert list to numpy array
        audio_np = np.array(audio_list, dtype=np.int16)
        
        # Create recognizer and audio data
        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(
            audio_np.tobytes(),
            sample_rate=16000,
            sample_width=2
        )
        
        # Recognize speech
        text = recognizer.recognize_google(audio_data, language=data.language or 'en-US')
        return {"text": text}
        
    except sr.UnknownValueError:
        return {"text": "", "error": "Could not understand audio"}
    except sr.RequestError as e:
        return {"text": "", "error": f"Speech recognition service error: {str(e)}"}
    except Exception as e:
        return {"text": "", "error": str(e)}
