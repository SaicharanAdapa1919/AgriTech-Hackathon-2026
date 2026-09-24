"""
Voice Chatbot Module for Multilingual Farmer Assistance
Supports English, Hindi, and Telugu voice input/output
"""

import speech_recognition as sr
import pyttsx3
import logging
import re
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class VoiceChatbot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.engine = None
        self.current_language = 'en-US'
        self.language_map = {
            'English': 'en-US',
            'Hindi': 'hi-IN',
            'Telugu': 'te-IN'
        }
        
        # Initialize microphone (optional - may fail if pyaudio not installed)
        try:
            self.microphone = sr.Microphone()
            logger.info("Microphone initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize microphone (pyaudio may not be installed): {e}")
            self.microphone = None
        
        # Initialize text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speaking rate
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            logger.info("Text-to-speech engine initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize TTS engine: {e}")

        
        # Keywords for parsing voice input
        self.state_keywords = {
            'andhra': 'Andhra Pradesh',
            'telangana': 'Telangana',
            'tamil': 'Tamil Nadu',
            'karnataka': 'Karnataka',
            'kerala': 'Kerala',
            'maharashtra': 'Maharashtra',
            'uttar': 'Uttar Pradesh',
            'west bengal': 'West Bengal',
            'rajasthan': 'Rajasthan',
            'gujarat': 'Gujarat',
            'bihar': 'Bihar',
            'punjab': 'Punjab',
            'haryana': 'Haryana',
            'madhya pradesh': 'Madhya Pradesh',
            'odisha': 'Odisha',
            'jharkhand': 'Jharkhand',
            'chhattisgarh': 'Chhattisgarh',
            'goa': 'Goa',
            'himachal': 'Himachal Pradesh',
            'uttarakhand': 'Uttarakhand',
            'sikkim': 'Sikkim',
            'arunachal': 'Arunachal Pradesh',
            'nagaland': 'Nagaland',
            'manipur': 'Manipur',
            'mizoram': 'Mizoram',
            'tripura': 'Tripura',
            'meghalaya': 'Meghalaya',
            'assam': 'Assam',
            'delhi': 'Delhi',
            'jammu': 'Jammu and Kashmir',
            'ladakh': 'Ladakh',
            'puducherry': 'Puducherry',
            'chandigarh': 'Chandigarh',
            'andaman': 'Andaman and Nicobar Islands',
            'dadra': 'Dadra and Nagar Haveli and Daman and Diu',
            'lakshadweep': 'Lakshadweep'
        }
        
        self.crop_keywords = {
            'paddy': 'Paddy',
            'rice': 'Paddy',
            'wheat': 'Wheat',
            'maize': 'Maize',
            'corn': 'Maize',
            'millets': 'Millets',
            'bajra': 'Millets',
            'cotton': 'Cotton',
            'sugarcane': 'Sugarcane',
            'pulses': 'Pulses',
            'dal': 'Pulses',
            'vegetables': 'Vegetables',
            'sabzi': 'Vegetables',
            'fruits': 'Fruits',
            'phal': 'Fruits'
        }
        
        self.category_keywords = {
            'small': 'Small',
            'marginal': 'Marginal',
            'chota': 'Small',
            'simant': 'Marginal',
            'chinn': 'Small',
            'sannakaru': 'Marginal'
        }
        
        # Hindi keywords
        self.hindi_state_keywords = {
            'आंध्र प्रदेश': 'Andhra Pradesh',
            'तेलंगाना': 'Telangana',
            'तमिलनाडु': 'Tamil Nadu',
            'कर्नाटक': 'Karnataka',
            'केरल': 'Kerala',
            'महाराष्ट्र': 'Maharashtra',
            'उत्तर प्रदेश': 'Uttar Pradesh',
            'पश्चिम बंगाल': 'West Bengal',
            'राजस्थान': 'Rajasthan',
            'गुजरात': 'Gujarat',
            'बिहार': 'Bihar',
            'पंजाब': 'Punjab',
            'हरियाणा': 'Haryana',
            'मध्य प्रदेश': 'Madhya Pradesh',
            'ओडिशा': 'Odisha',
            'झारखंड': 'Jharkhand',
            'छत्तीसगढ़': 'Chhattisgarh',
            'गोवा': 'Goa',
            'हिमाचल प्रदेश': 'Himachal Pradesh',
            'उत्तराखंड': 'Uttarakhand',
            'सिक्किम': 'Sikkim',
            'अरुणाचल प्रदेश': 'Arunachal Pradesh',
            'नागालैंड': 'Nagaland',
            'मणिपुर': 'Manipur',
            'मिजोरम': 'Mizoram',
            'त्रिपुरा': 'Tripura',
            'मेघालय': 'Meghalaya',
            'असम': 'Assam',
            'दिल्ली': 'Delhi',
            'जम्मू और कश्मीर': 'Jammu and Kashmir',
            'लद्दाख': 'Ladakh',
            'पुदुचेरी': 'Puducherry',
            'चंडीगढ़': 'Chandigarh'
        }
        
        self.hindi_crop_keywords = {
            'धान': 'Paddy',
            'गेहूं': 'Wheat',
            'मक्का': 'Maize',
            'बाजरा': 'Millets',
            'कपास': 'Cotton',
            'गन्ना': 'Sugarcane',
            'दलहन': 'Pulses',
            'सब्जियां': 'Vegetables',
            'फल': 'Fruits'
        }
        
        self.hindi_category_keywords = {
            'छोटा': 'Small',
            'सीमांत': 'Marginal'
        }
        
        # Telugu keywords
        self.telugu_state_keywords = {
            'ఆంధ్రప్రదేశ్': 'Andhra Pradesh',
            'తెలంగాణ': 'Telangana',
            'తమిళనాడు': 'Tamil Nadu',
            'కర్ణాటక': 'Karnataka',
            'కేరళ': 'Kerala',
            'మహారాష్ట్ర': 'Maharashtra',
            'ఉత్తర ప్రదేశ్': 'Uttar Pradesh',
            'పశ్చిమ బెంగాల్': 'West Bengal',
            'రాజస్థాన్': 'Rajasthan',
            'గుజరాత్': 'Gujarat',
            'బీహార్': 'Bihar',
            'పంజాబ్': 'Punjab',
            'హర్యానా': 'Haryana',
            'మధ్య ప్రదేశ్': 'Madhya Pradesh',
            'ఒడిషా': 'Odisha',
            'ఝార్ఖండ్': 'Jharkhand',
            'ఛత్తీస్‌గఢ్': 'Chhattisgarh',
            'గోవా': 'Goa',
            'హిమాచల్ ప్రదేశ్': 'Himachal Pradesh',
            'ఉత్తరాఖండ్': 'Uttarakhand',
            'సిక్కిం': 'Sikkim',
            'అరుణాచల్ ప్రదేశ్': 'Arunachal Pradesh',
            'నాగాల్యాండ్': 'Nagaland',
            'మణిపూర్': 'Manipur',
            'మిజోరాం': 'Mizoram',
            'త్రిపుర': 'Tripura',
            'మేఘాలయ': 'Meghalaya',
            'అస్సాం': 'Assam',
            'దిల్లీ': 'Delhi',
            'జమ్మూ కాశ్మీర్': 'Jammu and Kashmir',
            'లద్దాఖ్': 'Ladakh',
            'పుదుచ్చేరి': 'Puducherry',
            'చండీగఢ్': 'Chandigarh'
        }
        
        self.telugu_crop_keywords = {
            'వరి': 'Paddy',
            'గోధుమ': 'Wheat',
            'మొక్కజొన్న': 'Maize',
            'జొన్న': 'Millets',
            'పత్తి': 'Cotton',
            'చెరకు': 'Sugarcane',
            'పప్పు దినుసులు': 'Pulses',
            'కూరగాయలు': 'Vegetables',
            'పండ్లు': 'Fruits'
        }
        
        self.telugu_category_keywords = {
            'చిన్న': 'Small',
            'సన్నకారు': 'Marginal'
        }
        
        # Chat prompts in different languages
        self.prompts = {
            'English': {
                'welcome': "Welcome to Farmer Scheme Chatbot. Please choose your language: English, Hindi, or Telugu",
                'choose_state': "Please say your state name",
                'choose_crop': "Please say your crop name",
                'choose_land': "Please say your land area in acres",
                'choose_category': "Please say your farmer category: Small or Marginal",
                'processing': "Thank you. Processing your request for recommendations.",
                'error': "Sorry, I didn't understand. Please try again.",
                'success': "Here are your recommended schemes"
            },
            'Hindi': {
                'welcome': "किसान योजना चैटबॉट में आपका स्वागत है। कृपया अपनी भाषा चुनें: अंग्रेजी, हिंदी, या तेलुगु",
                'choose_state': "कृपया अपना राज्य बताएं",
                'choose_crop': "कृपया अपनी फसल बताएं",
                'choose_land': "कृपया अपनी जमीन एकड़ में बताएं",
                'choose_category': "कृपया अपना किसान श्रेणी बताएं: छोटा या सीमांत",
                'processing': "धन्यवाद। आपकी सिफारिशें तैयार की जा रही हैं।",
                'error': "क्षमा करें, मैं समझ नहीं पाया। कृपया फिर से प्रयास करें।",
                'success': "यहां आपकी अनुशंसित योजनाएं हैं"
            },
            'Telugu': {
                'welcome': "రైతు పథకాల చాట్‌బాట్‌కు స్వాగతం. దయచేసి మీ భాషను ఎంచుకోండి: ఇంగ్లీష్, హిందీ, లేదా తెలుగు",
                'choose_state': "దయచేసి మీ రాష్ట్రాన్ని చెప్పండి",
                'choose_crop': "దయచేసి మీ పంటను చెప్పండి",
                'choose_land': "దయచేసి మీ భూమిని ఎకరాలలో చెప్పండి",
                'choose_category': "దయచేసి మీ రైతు వర్గాన్ని చెప్పండి: చిన్న లేదా సన్నకారు",
                'processing': "ధన్యవాదాలు. మీ సిఫార్సులను సిద్ధం చేస్తున్నాం.",
                'error': "క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్ళీ ప్రయత్నించండి.",
                'success': "ఇక్కడ మీ సిఫార్సు చేసిన పథకాలు ఉన్నాయి"
            }
        }
    
    def set_language(self, language: str):
        """Set the current language for voice recognition"""
        if language in self.language_map:
            self.current_language = self.language_map[language]
            logger.info(f"Language set to {language} ({self.current_language})")
            return True
        return False
    
    def speak(self, text: str, language: str = 'English') -> bool:
        """Convert text to speech"""
        try:
            if self.engine:
                self.engine.say(text)
                self.engine.runAndWait()
                logger.info(f"Spoke: {text[:50]}...")
                return True
            else:
                logger.warning("TTS engine not available")
                return False
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return False
    
    def listen(self, duration: int = 5) -> Optional[str]:
        """Listen to audio and convert to text"""
        if self.microphone is None:
            logger.error("Microphone not available - pyaudio not installed")
            return None
            
        try:
            with self.microphone as source:
                logger.info("Listening for voice input...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.current_language)
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None

    
    def detect_language(self, text: str) -> str:
        """Detect language from text input"""
        text_lower = text.lower()
        
        # Telugu keywords
        telugu_words = ['telugu', 'తెలుగు', 'రైతు', 'రాష్ట్ర', 'పంట', 'భూమి', 'చిన్న', 'సన్నకారు']
        # Hindi keywords
        hindi_words = ['hindi', 'हिंदी', 'हिन्दी', 'किसान', 'राज्य', 'फसल', 'जमीन', 'छोटा', 'सीमांत']
        
        for word in telugu_words:
            if word in text_lower:
                return 'Telugu'
        for word in hindi_words:
            if word in text_lower:
                return 'Hindi'
        return 'English'
    
    def parse_state(self, text: str, language: str = 'English') -> Optional[str]:
        """Parse state from voice/text input"""
        text_lower = text.lower()
        
        # Try English keywords
        for key, value in self.state_keywords.items():
            if key in text_lower:
                return value
        
        # Try language-specific keywords
        if language == 'Hindi':
            for key, value in self.hindi_state_keywords.items():
                if key.lower() in text_lower:
                    return value
        elif language == 'Telugu':
            for key, value in self.telugu_state_keywords.items():
                if key.lower() in text_lower:
                    return value
        
        return None
    
    def parse_crop(self, text: str, language: str = 'English') -> Optional[str]:
        """Parse crop from voice/text input"""
        text_lower = text.lower()
        
        # Try English keywords
        for key, value in self.crop_keywords.items():
            if key in text_lower:
                return value
        
        # Try language-specific keywords
        if language == 'Hindi':
            for key, value in self.hindi_crop_keywords.items():
                if key.lower() in text_lower:
                    return value
        elif language == 'Telugu':
            for key, value in self.telugu_crop_keywords.items():
                if key.lower() in text_lower:
                    return value
        
        return None
    
    def parse_category(self, text: str, language: str = 'English') -> Optional[str]:
        """Parse farmer category from voice/text input"""
        text_lower = text.lower()
        
        # Try English keywords
        for key, value in self.category_keywords.items():
            if key in text_lower:
                return value
        
        # Try language-specific keywords
        if language == 'Hindi':
            for key, value in self.hindi_category_keywords.items():
                if key.lower() in text_lower:
                    return value
        elif language == 'Telugu':
            for key, value in self.telugu_category_keywords.items():
                if key.lower() in text_lower:
                    return value
        
        return None
    
    def parse_land(self, text: str) -> Optional[float]:
        """Parse land area from voice/text input"""
        # Try to find numbers in text
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            return float(numbers[0])
        return None
    
    def get_prompt(self, key: str, language: str = 'English') -> str:
        """Get prompt text in specified language"""
        lang_prompts = self.prompts.get(language, self.prompts['English'])
        return lang_prompts.get(key, "Please provide your input")
    
    def process_voice_input(self, state: str = 'language') -> Dict[str, Any]:
        """
        Process voice input based on current chatbot state
        Returns: dict with success, text, parsed_value, and next_state
        """
        result = {
            'success': False,
            'text': None,
            'parsed_value': None,
            'next_state': state,
            'error': None
        }
        
        # Listen for voice input
        text = self.listen()
        if not text:
            result['error'] = 'Could not understand audio'
            return result
        
        result['text'] = text
        result['success'] = True
        
        # Process based on current state
        if state == 'language':
            detected_lang = self.detect_language(text)
            result['parsed_value'] = detected_lang
            result['next_state'] = 'state'
            self.set_language(detected_lang)
            
        elif state == 'state':
            state_value = self.parse_state(text, self.current_language)
            if state_value:
                result['parsed_value'] = state_value
                result['next_state'] = 'crop'
            else:
                result['success'] = False
                result['error'] = 'Could not parse state'
                
        elif state == 'crop':
            crop_value = self.parse_crop(text, self.current_language)
            if crop_value:
                result['parsed_value'] = crop_value
                result['next_state'] = 'land'
            else:
                result['success'] = False
                result['error'] = 'Could not parse crop'
                
        elif state == 'land':
            land_value = self.parse_land(text)
            if land_value is not None:
                result['parsed_value'] = land_value
                result['next_state'] = 'category'
            else:
                result['success'] = False
                result['error'] = 'Could not parse land area'
                
        elif state == 'category':
            category_value = self.parse_category(text, self.current_language)
            if category_value:
                result['parsed_value'] = category_value
                result['next_state'] = 'result'
            else:
                result['success'] = False
                result['error'] = 'Could not parse category'
        
        return result

# Create a singleton instance
voice_chatbot = VoiceChatbot()

def get_voice_chatbot() -> VoiceChatbot:
    """Get the voice chatbot instance"""
    return voice_chatbot
