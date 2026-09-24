import streamlit as st
import requests
from gtts import gTTS
import tempfile
import os
import speech_recognition as sr

# -------------------------------
# Backend API URL
# -------------------------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Farmer Scheme Recommender",
    page_icon="🌾",
    layout="wide"
)

# ======================================================
# ECO-FRIENDLY BACKGROUND CSS
# ======================================================

# Add eco-friendly green background styling
st.markdown("""
<style>
    /* Main background - eco-friendly green gradient */
    .stApp {
        background: linear-gradient(180deg, #e8f5e9 0%, #c8e6c9 100%);
    }
    
    /* Headings color - dark green for readability */
    h1, h2, h3, h4, h5, h6 {
        color: #1b5e20 !important;
    }
    
    /* Main content text color */
    .stApp .stMarkdown {
        color: #1b5e20 !important;
    }
    
    /* Label and text colors */
    label, p, span, div {
        color: #1b5e20 !important;
    }
    
    /* Sidebar background - lighter green */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #a5d6a7 0%, #81c784 100%);
    }
    
    /* Sidebar text color */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #1b5e20 !important;
    }
    
    /* Input field backgrounds - white with dark text */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #1b5e20 !important;
        border: 1px solid #81c784 !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #1b5e20 !important;
        border: 1px solid #81c784 !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #1b5e20 !important;
        border: 1px solid #81c784 !important;
    }
    
    /* Selectbox dropdown styling - complete override */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1b5e20 !important;
    }
    
    /* Dropdown menu popup */
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    /* Dropdown option items */
    div[data-baseweb="popover"] ul li {
        color: #1b5e20 !important;
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="popover"] ul li:hover {
        background-color: #c8e6c9 !important;
        color: #1b5e20 !important;
    }
    
    /* Placeholder text */
    .stSelectbox div[data-baseweb="select"] div[data-testid="stSelectboxPlaceholder"] {
        color: #1b5e20 !important;
    }
    
    /* Option list in selectbox */
    ul[data-testid="stSelectboxPopover"] li {
        color: #1b5e20 !important;
        background-color: #ffffff !important;
    }
    
    ul[data-testid="stSelectboxPopover"] li:hover {
        background-color: #c8e6c9 !important;
    }
    
    /* Button styling - green theme */
    .stButton > button {
        background-color: #4caf50 !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #388e3c !important;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #c8e6c9 !important;
        color: #1b5e20 !important;
    }
    
    /* Info message styling */
    .stInfo {
        background-color: #b3e5fc !important;
        color: #01579b !important;
    }
    
    /* Warning message styling */
    .stWarning {
        background-color: #fff3e0 !important;
        color: #e65100 !important;
    }
    
    /* Error message styling */
    .stError {
        background-color: #ffcdd2 !important;
        color: #b71c1c !important;
    }
    
    /* Streamlit selectbox arrow color */
    .stSelectbox svg {
        fill: #1b5e20 !important;
    }
</style>
""", unsafe_allow_html=True)

# ======================================================
# HERO IMAGE
# ======================================================

# Display a farmer/agriculture related hero image at the top
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <img src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&h=400&fit=crop" 
         alt="Farmer in field" 
         style="width: 100%; max-width: 1200px; height: auto; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
</div>
""", unsafe_allow_html=True)

# ======================================================
# VOICE FUNCTIONS
# ======================================================

def text_to_speech(text, language='en'):
    """Convert text to speech"""
    try:
        lang_map = {'English': 'en', 'Hindi': 'hi', 'Telugu': 'te'}
        lang_code = lang_map.get(language, 'en')
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        import uuid
        temp_filename = os.path.join(tempfile.gettempdir(), f"tts_{uuid.uuid4().hex[:8]}.mp3")
        tts.save(temp_filename)
        
        with open(temp_filename, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        try:
            os.unlink(temp_filename)
        except (OSError, PermissionError):
            pass
            
        return audio_bytes
    except Exception as e:
        st.error(f"🔇 TTS error: {e}")
        return None


# ======================================================
# DATA
# ======================================================

ALL_LANGUAGES = ["English", "Hindi", "Telugu"]

LANG_DATA = {
    "English": {
        "title": "Smart Farmer Scheme Recommendation System",
        "subtitle": "Get personalized government schemes based on your farming profile",
        "states": {
            "Andhra Pradesh": "Andhra Pradesh", "Telangana": "Telangana", "Tamil Nadu": "Tamil Nadu",
            "Karnataka": "Karnataka", "Kerala": "Kerala", "Maharashtra": "Maharashtra",
            "Uttar Pradesh": "Uttar Pradesh", "West Bengal": "West Bengal", "Rajasthan": "Rajasthan",
            "Gujarat": "Gujarat", "Bihar": "Bihar", "Punjab": "Punjab", "Haryana": "Haryana",
            "Madhya Pradesh": "Madhya Pradesh", "Odisha": "Odisha"
        },
        "crops": {
            "All": "All", "Paddy": "Paddy", "Wheat": "Wheat", "Maize": "Maize", "Millets": "Millets",
            "Cotton": "Cotton", "Sugarcane": "Sugarcane", "Pulses": "Pulses", 
            "Vegetables": "Vegetables", "Fruits": "Fruits"
        },
        "categories": {"All": "All", "Small": "Small", "Marginal": "Marginal"}
    },
    "Telugu": {
        "title": "Smart Farmer Scheme - Voice Assistant",
        "subtitle": "Voice-based scheme recommendation",
        "states": {
            "Andhra Pradesh": "Andhra Pradesh", "Telangana": "Telangana", "Tamil Nadu": "Tamil Nadu",
            "Karnataka": "Karnataka", "Kerala": "Kerala", "Maharashtra": "Maharashtra",
            "Uttar Pradesh": "Uttar Pradesh", "West Bengal": "West Bengal", "Rajasthan": "Rajasthan",
            "Gujarat": "Gujarat", "Bihar": "Bihar", "Punjab": "Punjab", "Haryana": "Haryana",
            "Madhya Pradesh": "Madhya Pradesh", "Odisha": "Odisha"
        },
        "crops": {
            "All": "All", "Paddy": "Paddy", "Wheat": "Wheat", "Maize": "Maize", "Millets": "Millets",
            "Cotton": "Cotton", "Sugarcane": "Sugarcane", "Pulses": "Pulses", 
            "Vegetables": "Vegetables", "Fruits": "Fruits"
        },
        "categories": {"All": "All", "Small": "Small", "Marginal": "Marginal"}
    },
    "Hindi": {
        "title": "Smart Farmer Scheme - Voice Assistant",
        "subtitle": "Voice-based scheme recommendation",
        "states": {
            "Andhra Pradesh": "Andhra Pradesh", "Telangana": "Telangana", "Tamil Nadu": "Tamil Nadu",
            "Karnataka": "Karnataka", "Kerala": "Kerala", "Maharashtra": "Maharashtra",
            "Uttar Pradesh": "Uttar Pradesh", "West Bengal": "West Bengal", "Rajasthan": "Rajasthan",
            "Gujarat": "Gujarat", "Bihar": "Bihar", "Punjab": "Punjab", "Haryana": "Haryana",
            "Madhya Pradesh": "Madhya Pradesh", "Odisha": "Odisha"
        },
        "crops": {
            "All": "All", "Paddy": "Paddy", "Wheat": "Wheat", "Maize": "Maize", "Millets": "Millets",
            "Cotton": "Cotton", "Sugarcane": "Sugarcane", "Pulses": "Pulses", 
            "Vegetables": "Vegetables", "Fruits": "Fruits"
        },
        "categories": {"All": "All", "Small": "Small", "Marginal": "Marginal"}
    }
}

for lang in ALL_LANGUAGES:
    if lang not in LANG_DATA:
        LANG_DATA[lang] = LANG_DATA["English"]

CHATBOT_PROMPTS = {
    "English": {
        "welcome": "Welcome! I am your Farmer Scheme Assistant. Please choose your language: English, Hindi, or Telugu.",
        "ask_state": "Please tell me your state name. For example: Andhra Pradesh, Telangana, Tamil Nadu, etc.",
        "ask_crop": "Please tell me your crop. For example: Paddy, Wheat, Cotton, etc.",
        "ask_land": "Please tell me your land area in acres. For example: 5 acres.",
        "ask_category": "Please tell me your farmer category. Say either Small or Marginal.",
        "confirm": "Thank you! I have recorded your information. Click Get Recommendations to see your eligible schemes."
    },
    "Hindi": {
        "welcome": "स्वागत है! मैं आपका किसान योजना सहायक हूं। कृपया अपनी भाषा चुनें: अंग्रेजी, हिंदी, या तेलुगु।",
        "ask_state": "कृपया अपना राज्य बताएं।",
        "ask_crop": "कृपया अपनी फसल बताएं।",
        "ask_land": "कृपया अपनी जमीन एकड़ में बताएं।",
        "ask_category": "कृपया अपनी श्रेणी बताएं। छोटा या सीमांत।",
        "confirm": "धन्यवाद!"
    },
    "Telugu": {
        "welcome": "স্বাগতম! নেণু মী রৈতু পলক সহায়কুডু। ভাষ এণ্চুকোণ্ডু।",
        "ask_state": "রাষ্ট্রং চেপুণ্ডু।",
        "ask_crop": "পণ্ট চেপুণ্ডু।",
        "ask_land": "ভূমি ఎకరాలలो চেপুণ্ডু।",
        "ask_category": "রৈতু বর্গং চেপুণ্ডু।",
        "confirm": "ধন্যবাদলু!"
    }
}

LANG_CODE_MAP = {'English': 'en-US', 'Hindi': 'hi-IN', 'Telugu': 'te-IN'}

# ======================================================
# SESSION STATE
# ======================================================

if 'chatbot_started' not in st.session_state:
    st.session_state.chatbot_started = False
if 'chatbot_session_id' not in st.session_state:
    st.session_state.chatbot_session_id = None
if 'chatbot_language' not in st.session_state:
    st.session_state.chatbot_language = 'English'
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'idle'
if 'form_state' not in st.session_state:
    st.session_state.form_state = ''
if 'form_crop' not in st.session_state:
    st.session_state.form_crop = ''
if 'form_land' not in st.session_state:
    st.session_state.form_land = 0.0
if 'form_category' not in st.session_state:
    st.session_state.form_category = ''
if 'audio_counter' not in st.session_state:
    st.session_state.audio_counter = 0
if 'last_spoken_message' not in st.session_state:
    st.session_state.last_spoken_message = ''


# ======================================================
# MAIN UI
# ======================================================

language = st.selectbox("🌍 Select Language", ALL_LANGUAGES)
L = LANG_DATA[language]

st.markdown(f"## 🌾 {L['title']}")
st.markdown(f"**{L['subtitle']}**")

# ======================================================
# CHATBOT FUNCTIONS
# ======================================================

def start_chatbot_session():
    try:
        response = requests.post(f"{API_URL}/chatbot/start")
        if response.status_code == 200:
            data = response.json()
            st.session_state.chatbot_session_id = data['session_id']
            st.session_state.current_step = data['current_state']
            st.session_state.current_message = data['message']
            st.session_state.chatbot_started = True
            st.session_state.last_spoken_message = ""
            # Set the chatbot language based on user's language selection
            st.session_state.chatbot_language = language
            st.session_state.last_audio_key = ""
            return True
    except Exception as e:
        st.error(f"Failed to start chatbot: {e}")
    return False


def process_chatbot_input(user_input):
    try:
        payload = {
            "session_id": st.session_state.chatbot_session_id,
            "text_input": user_input
        }
        response = requests.post(f"{API_URL}/chatbot/process", json=payload)
        if response.status_code == 200:
            data = response.json()
            st.session_state.current_step = data['current_state']
            st.session_state.current_message = data['message']
            
            collected = data.get('collected_data', {})
            if collected.get('state'):
                st.session_state.form_state = collected['state']
            if collected.get('crop'):
                st.session_state.form_crop = collected['crop']
            if collected.get('land'):
                st.session_state.form_land = collected['land']
            if collected.get('category'):
                st.session_state.form_category = collected['category']
            
            return data
    except Exception as e:
        st.error(f"Failed to process input: {e}")
    return None


# ======================================================
# CHATBOT SECTION
# ======================================================

st.markdown("---")
st.markdown("### 🤖 AI Voice Assistant")

# Start button
if not st.session_state.chatbot_started:
    st.info("👋 Click the button below to start the voice assistant")
    if st.button("🎙️ START VOICE ASSISTANT", type="primary", use_container_width=True):
        if start_chatbot_session():
            st.rerun()
else:
    # Display status
    col1, col2 = st.columns([2, 1])
    with col1:
        step_names = {
            'language': 'Step 1: Choose language (English/Hindi/Telugu)',
            'state': 'Step 2: Tell your state',
            'crop': 'Step 3: Tell your crop',
            'land': 'Step 4: Tell your land area in acres',
            'category': 'Step 5: Tell your farmer category (Small/Marginal)',
            'complete': '✅ All information collected!'
        }
        st.info(step_names.get(st.session_state.current_step, "Ready"))
    
    with col2:
        if st.button("🔄 Restart", use_container_width=True):
            st.session_state.chatbot_started = False
            st.session_state.chatbot_session_id = None
            st.session_state.current_step = 'idle'
            st.session_state.current_message = ''
            st.session_state.form_state = ''
            st.session_state.form_crop = ''
            st.session_state.form_land = 0.0
            st.session_state.form_category = ''
            st.rerun()

    # Display message
    if st.session_state.current_message:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;padding:20px;border-radius:15px;margin:10px 0;">
            <h4>🤖 Assistant Says:</h4>
            <p style="font-size:18px;">{st.session_state.current_message}</p>
        </div>
        """, unsafe_allow_html=True)

        # Initialize step tracking if not exists
        if 'last_audio_step' not in st.session_state:
            st.session_state.last_audio_step = None
        
        # Play audio for each new step (more reliable tracking)
        if st.session_state.last_audio_step != st.session_state.current_step:
            audio_bytes = text_to_speech(st.session_state.current_message, st.session_state.chatbot_language)
            if audio_bytes:
                st.session_state.audio_counter += 1
                st.audio(audio_bytes, format='audio/mp3')
            st.session_state.last_audio_step = st.session_state.current_step
        
        # Also show a manual play button for convenience
        if st.button("🔊 Play Audio Again", key="play_audio_btn"):
            audio_bytes = text_to_speech(st.session_state.current_message, st.session_state.chatbot_language)
            if audio_bytes:
                st.audio(audio_bytes, format='audio/mp3')

    # Voice input section
    if st.session_state.current_step != 'complete':
        st.markdown("---")
        st.markdown("#### 🎤 Voice Input")
        
        # Use Streamlit's built-in audio_input
        st.info("📢 Click the microphone below to record your voice:")
        
        audio_data = None
        try:
            audio_data = st.audio_input(
                "🎙️ Click to speak:",
                key="voice_input"
            )
        except Exception as e:
            st.warning(f"Audio input not available: {e}")
        
        if audio_data:
            # Process the audio
            with st.spinner("Processing voice..."):
                try:
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                        f.write(audio_data.getvalue())
                        temp_path = f.name
                    
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(temp_path) as source:
                        audio = recognizer.record(source)
                        text = recognizer.recognize_google(audio)
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    
                    # Show what was recognized
                    st.success(f"✅ Recognized: '{text}'")
                    
                    # Process the text and show what's being saved
                    result = process_chatbot_input(text)
                    if result:
                        # Show what's being saved to fields with clear feedback
                        collected = result.get('collected_data', {})
                        if collected.get('state'):
                            st.session_state.form_state = collected['state']
                            st.info(f"📍 State set to: {collected['state']}")
                        if collected.get('crop'):
                            st.session_state.form_crop = collected['crop']
                            st.info(f"🌾 Crop set to: {collected['crop']}")
                        if collected.get('land'):
                            st.session_state.form_land = collected['land']
                            st.info(f"📏 Land set to: {collected['land']} acres")
                        if collected.get('category'):
                            st.session_state.form_category = collected['category']
                            st.info(f"👨‍🌾 Category set to: {collected['category']}")
                        
                        st.rerun()
                        
                except sr.UnknownValueError:
                    st.warning("Could not understand audio. Please try again or type your answer.")
                except Exception as e:
                    st.warning(f"Voice recognition error: {e}")
                    st.info("Please type your answer below instead")
        
        st.markdown("---")
        st.markdown("**Or type your answer:**")
        text_input = st.text_input("Type here:", key=f"text_{st.session_state.current_step}")
        if st.button("📤 Submit", type="primary", use_container_width=True):
            if text_input:
                result = process_chatbot_input(text_input)
                if result:
                    st.rerun()


# ======================================================
# FORM SECTION
# ======================================================

st.markdown("---")
st.markdown("### 📝 Your Information (Auto-Filled)")

col1, col2 = st.columns(2)

# Get stored values
saved_state = st.session_state.form_state
saved_crop = st.session_state.form_crop
saved_land = st.session_state.form_land
saved_category = st.session_state.form_category

with col1:
    state_options = list(L["states"].keys())
    # Find the correct index for saved state
    state_index = 0
    if saved_state:
        for i, opt in enumerate(state_options):
            if L["states"].get(opt) == saved_state:
                state_index = i
                break
    
    state_label = st.selectbox("📍 State", state_options, index=state_index, key="state_select")
    current_state = L["states"].get(state_label, state_label)
    # Update session state with what user might have changed
    st.session_state.form_state = current_state
    
    crop_options = list(L["crops"].keys())
    crop_index = 0
    if saved_crop:
        for i, opt in enumerate(crop_options):
            if L["crops"].get(opt) == saved_crop:
                crop_index = i
                break
    
    crop_label = st.selectbox("🌾 Crop", crop_options, index=crop_index, key="crop_select")
    current_crop = L["crops"].get(crop_label, crop_label)
    st.session_state.form_crop = current_crop

with col2:
    # Use saved land value or default
    land_value = float(saved_land) if saved_land and saved_land > 0 else 0.0
    current_land = st.number_input(
        "📏 Land (acres)", 
        min_value=0.0, 
        value=land_value,
        step=0.5,
        key="land_input"
    )
    st.session_state.form_land = current_land
    
    category_options = list(L["categories"].keys())
    category_index = 0
    if saved_category:
        for i, opt in enumerate(category_options):
            if L["categories"].get(opt) == saved_category:
                category_index = i
                break
    
    category_label = st.selectbox("👨‍🌾 Farmer Category", category_options, index=category_index, key="category_select")
    current_category = L["categories"].get(category_label, category_label)
    st.session_state.form_category = current_category

# ======================================================
# RECOMMENDATIONS
# ======================================================

st.markdown("---")

# Check if we should auto-show recommendations (when chatbot completed)
if st.session_state.current_step == 'complete':
    # Auto-fetch recommendations when chatbot is done
    if current_state and current_crop and current_land > 0 and current_category:
        st.success("🎉 All information collected! Showing your recommendations below:")
        
        payload = {
            "state": current_state,
            "crop": current_crop,
            "land": current_land,
            "category": current_category
        }

        try:
            with st.spinner("Fetching your personalized schemes..."):
                response = requests.post(f"{API_URL}/recommend", json=payload)

            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    st.success(f"🎉 Found {len(data)} eligible schemes!")
                    
                    for scheme in data:
                        st.markdown(f"""
                        <div style="background:#f8f9fa;padding:20px;border-radius:12px;margin-bottom:15px;border-left:5px solid #28a745;box-shadow:0 2px 8px rgba(0,0,0,0.15);">
                        <h4 style="color:#1a1a1a;margin-bottom:12px;">📌 {scheme['scheme_name']}</h4>
                        <p style="color:#333333;margin:8px 0;"><b>🎯 Focus:</b> <span style="color:#555555;">{scheme['focus_area']}</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>💰 Benefit:</b> <span style="color:#2e7d32;font-weight:600;">{scheme['benefit_type']} ({scheme['benefit_amount']})</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>📝 Description:</b> <span style="color:#555555;">{scheme['description']}</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>✅ Eligibility:</b> <span style="color:#555555;">{scheme['eligibility']}</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>📋 How to Apply:</b> <span style="color:#555555;">{scheme['application_mode']}</span></p>
                        <br>
                        <a href="{scheme['official_url']}" target="_blank" style="display:inline-block;background:#1976d2;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:500;">🔗 Visit Official Website</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No schemes found for your criteria")
            else:
                st.error(f"❌ Error: {response.text}")

        except Exception as e:
            st.error(f"❌ Connection error: {e}")

elif st.button("🔍 Get Recommendations", type="primary", use_container_width=True):
    if not current_state or not current_crop or current_land <= 0 or not current_category:
        st.error("⚠️ Please fill all fields")
    else:
        payload = {
            "state": current_state,
            "crop": current_crop,
            "land": current_land,
            "category": current_category
        }

        try:
            with st.spinner("Fetching your personalized schemes..."):
                response = requests.post(f"{API_URL}/recommend", json=payload)

            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    st.success(f"🎉 Found {len(data)} eligible schemes!")
                    
                    for scheme in data:
                        st.markdown(f"""
                        <div style="background:#f8f9fa;padding:20px;border-radius:12px;margin-bottom:15px;border-left:5px solid #28a745;box-shadow:0 2px 8px rgba(0,0,0,0.15);">
                        <h4 style="color:#1a1a1a;margin-bottom:12px;">📌 {scheme['scheme_name']}</h4>
                        <p style="color:#333333;margin:8px 0;"><b>🎯 Focus:</b> <span style="color:#555555;">{scheme['focus_area']}</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>💰 Benefit:</b> <span style="color:#2e7d32;font-weight:600;">{scheme['benefit_type']} ({scheme['benefit_amount']})</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>📝 Description:</b> <span style="color:#555555;">{scheme['description']}</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>✅ Eligibility:</b> <span style="color:#555555;">{scheme['eligibility']}</span></p>
                        <p style="color:#333333;margin:8px 0;"><b>📋 How to Apply:</b> <span style="color:#555555;">{scheme['application_mode']}</span></p>
                        <br>
                        <a href="{scheme['official_url']}" target="_blank" style="display:inline-block;background:#1976d2;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:500;">🔗 Visit Official Website</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No schemes found")
            else:
                st.error(f"❌ Error: {response.text}")

        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            st.info("Make sure backend is running: cd backend && uvicorn api:app --reload")

st.markdown("---")
st.markdown("© 2026 Smart Agri Tech")
