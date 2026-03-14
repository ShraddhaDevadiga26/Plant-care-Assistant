from flask import Flask, request, render_template_string, send_from_directory, session, redirect, url_for, jsonify
import cv2, os, random, threading, webbrowser
from gtts import gTTS
import playsound
from werkzeug.utils import secure_filename
import json
import requests                           
from datetime import datetime            
import smtplib                            
from email.mime.text import MIMEText 
from chatbot import init_chatbot
from helpline import init_helpline
from predict import get_weather_current, get_weather_forecast, send_laptop_sms
from flask import Flask, render_template_string, request, session, flash, redirect, url_for

WEATHER_API_KEY = "e93e3b1cfdb506dff2193df809415c1a"  
PHONE_NUMBER = "+918123893856"  

app = Flask(__name__)
init_chatbot(app)
init_helpline(app)
app.secret_key = 'plantcare-secret-key-2026'
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

plants_info = [
    {
        "id": "tulip",
        "name": {"en": "Tulip", "hi": "ट्यूलिप", "kn": "ತುಲಿಪ್"},
        "image": "tulip.jpg",
        "videos":"https://www.youtube.com/embed/BYW0u1Puups?",
        "soil": {"en": "Well-drained sandy loam", "hi": "अच्छी जल निकासी रेतीली दोमट", "kn": "ಚೆನ್ನಾಗಿ ನೀರು ಹರಿಯುವ ಹಾಲು ಮಣ್ಣು"},
        "sunlight": {"en": "Full sun (6-8 hrs)", "hi": "पूर्ण सूर्य प्रकाश (6-8 घंटे)", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ (೬-೮ ಗಂಟೆಗಳು)"},
        "water": {"en": "Moderate (once weekly)", "hi": "मध्यम (साप्ताहिक एक बार)", "kn": "ಮಧ್ಯಮ (ಸಾಪ್ತಾಹಿಕ ಒಂದು ಬಾರಿ)"},
        "temperature": {"en": "15-25°C (Cool)", "hi": "15-25°C (ठंडा)", "kn": "೧೫-೨೫° ಸೆ. (ಶೀತಲ)"},
        "ph": {"en": "6.0-7.0", "hi": "6.0-7.0", "kn": "೬.೦-೭.೦"},
        "fertilizer": {"en": "10-10-10 NPK (Spring)", "hi": "10-10-10 NPK (वसंत)", "kn": "೧೦-೧೦-೧೦ NPK (ಬಸಂತ)"},
        "spacing": {"en": "15cm apart", "hi": "15cm की दूरी", "kn": "೧೫ ಸೆ.ಮೀ. ಅಂತರ"},
        "harvest": {"en": "60-90 days", "hi": "60-90 दिन", "kn": "೬೦-೯೦ ದಿನಗಳು"},
        "pests": {"en": "Aphids, Slugs", "hi": "एफिड्स, घोंघे", "kn": "ಆಫಿಡ್ಸ್, ಕೀಟ"}
    },
    {
        "id": "rose",
        "name": {"en": "Rose", "hi": "गुलाब", "kn": "ಗುಲಾಬಿ"},
        "image": "rose.jpg",
        "videos":"https://www.youtube.com/embed/BN3G-wpWtFY?",
        "soil": {"en": "Loamy, rich organic", "hi": "दोमट, जैविक समृद्ध", "kn": "ಕೆಂಡವಾಗಿದ್ದುದು, ಸಾವಯವ ಸಮೃದ್ಧ"},
        "sunlight": {"en": "Full sun (6-8 hrs)", "hi": "पूर्ण सूर्य प्रकाश (6-8 घंटे)", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ (೬-೮ ಗಂಟೆಗಳು)"},
        "water": {"en": "Regular (daily in summer)", "hi": "नियमित (गर्मी में रोज)", "kn": "ನಿಯಮಿತ (ಗ್ರೀಷ್ಮದಲ್ಲಿ ದೈನಂದಿನ)"},
        "temperature": {"en": "18-30°C", "hi": "18-30°C", "kn": "೧೮-೩೦° ಸೆ."},
        "ph": {"en": "6.0-6.5", "hi": "6.0-6.5", "kn": "೬.೦-೬.೫"},
        "fertilizer": {"en": "6-12-36 NPK + organic", "hi": "6-12-36 NPK + जैविक", "kn": "೬-೧೨-೩೬ NPK + ಸಾವಯವ"},
        "spacing": {"en": "60cm x 60cm", "hi": "60cm x 60cm", "kn": "೬೦ ಸೆ.ಮೀ. x ೬೦ ಸೆ.ಮೀ."},
        "harvest": {"en": "Continuous flowering", "hi": "लगातार फूल", "kn": "ಲಗತಾರ ಹೂವು"},
        "pests": {"en": "Aphids, Thrips, Mealybugs", "hi": "एफिड्स, थ्रिप्स, मीलिबग", "kn": "ಆಫಿಡ್ಸ್, ಥ್ರಿಪ್ಸ್, ಮೀಲಿಬಗ್"}
    },
    {
        "id": "sunflower",
        "name": {"en": "Sunflower", "hi": "सूरजमुखी", "kn": "ಸೂರ್ಯಕಾಂತೆ"},
        "image": "sunflower.jpg",
        "videos":"https://www.youtube.com/embed/S2nBOsv4Fwg?",
        "soil": {"en": "Loamy, well-drained", "hi": "दोमट, अच्छी जल निकासी", "kn": "ಕೆಂಡವಾಗಿದ್ದುದು, ಚೆನ್ನಾಗಿ ನೀರು ಹರಿಯುವ"},
        "sunlight": {"en": "Full sun (8+ hrs)", "hi": "पूर्ण सूर्य प्रकाश (8+ घंटे)", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ (೮+ ಗಂಟೆಗಳು)"},
        "water": {"en": "Moderate till flowering", "hi": "फूल आने तक मध्यम", "kn": "ಹೂವು ಬರುವವರೆಗೆ ಮಧ್ಯಮ"},
        "temperature": {"en": "20-30°C", "hi": "20-30°C", "kn": "೨೦-೩೦° ಸೆ."},
        "ph": {"en": "6.0-7.5", "hi": "6.0-7.5", "kn": "೬.೦-೭.೫"},
        "fertilizer": {"en": "120:60:60 NPK kg/ha", "hi": "120:60:60 NPK किग्रा/हेक्टेयर", "kn": "೧೨೦:೬೦:೬೦ NPK ಕೆ.ಜಿ/ಹೆಕ್ಟೇರ್"},
        "spacing": {"en": "60cm x 30cm", "hi": "60cm x 30cm", "kn": "೬೦ ಸೆ.ಮೀ. x ೩೦ ಸೆ.ಮೀ."},
        "harvest": {"en": "80-100 days", "hi": "80-100 दिन", "kn": "೮೦-೧೦೦ ದಿನಗಳು"},
        "pests": {"en": "Head borers, Aphids", "hi": "हेड बोरर, एफिड्स", "kn": "ಹೆಡ್ ಬೋರರ್, ಆಫಿಡ್ಸ್"}
    },
    {
        "id": "mango",
        "name": {"en": "Mango", "hi": "आम", "kn": "ಮಾವಿನ"},
        "image": "mango.jpg",
        "videos":"https://www.youtube.com/embed/0iAZa5bHQj0?",
        "soil": {"en": "Deep loamy, well-drained", "hi": "गहरा दोमट, अच्छी जल निकासी", "kn": "ಗಾಢ ಕೆಂಡ, ಚೆನ್ನಾಗಿ ನೀರು ಹರಿಯುವ"},
        "sunlight": {"en": "Full sun", "hi": "पूर्ण सूर्य प्रकाश", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ"},
        "water": {"en": "Low (drought tolerant)", "hi": "कम (सूखा सहनशील)", "kn": "ಕಡಿಮೆ (ಹರಳು ಸಹಿಸುವ)"},
        "temperature": {"en": "24-30°C", "hi": "24-30°C", "kn": "೨೪-೩೦° ಸೆ."},
        "ph": {"en": "5.5-7.5", "hi": "5.5-7.5", "kn": "೫.೫-೭.೫"},
        "fertilizer": {"en": "NPK 70:40:40 g/plant", "hi": "NPK 70:40:40 ग्राम/पौधा", "kn": "NPK ೭೦:೪೦:೪೦ ಗ್ರಾಂ/ಸಸ್ಯ"},
        "spacing": {"en": "10m x 10m", "hi": "10m x 10m", "kn": "೧೦ ಮೀ. x ೧೦ ಮೀ."},
        "harvest": {"en": "3-5 years (fruiting)", "hi": "3-5 वर्ष (फलन)", "kn": "೩-೫ ವರ್ಷಗಳು (ಹಣು)"},
        "pests": {"en": "Fruit flies, Hoppers", "hi": "फल मक्खी, हॉपर", "kn": "ಹಣು ಮಕ್ಕಳು, ಹಾಪರ್"}
    },
    {
        "id": "guava",
        "name": {"en": "Guava", "hi": "अमरूद", "kn": "ಗುವಾ"},
        "image": "guava.jpg",
        "videos":"https://www.youtube.com/embed/BemCNDy2v3c?",
        "soil": {"en": "Loamy to clay loam", "hi": "दोमट से चिकनी दोमट", "kn": "ಕೆಂಡದಿಂದ ಚಿಕ್ಕ ಮಣ್ಣು"},
        "sunlight": {"en": "Full sun", "hi": "पूर्ण सूर्य प्रकाश", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ"},
        "water": {"en": "Moderate", "hi": "मध्यम", "kn": "ಮಧ್ಯಮ"},
        "temperature": {"en": "15-40°C", "hi": "15-40°C", "kn": "೧೫-೪೦° ಸೆ."},
        "ph": {"en": "5.0-8.0", "hi": "5.0-8.0", "kn": "೫.೦-೮.೦"},
        "fertilizer": {"en": "NPK 500:300:300 g/plant", "hi": "NPK 500:300:300 ग्राम/पौधा", "kn": "NPK ೫೦೦:೩೦೦:೩೦೦ ಗ್ರಾಂ/ಸಸ್ಯ"},
        "spacing": {"en": "6m x 6m", "hi": "6m x 6m", "kn": "೬ ಮೀ. x ೬ ಮೀ."},
        "harvest": {"en": "2-3 years (fruiting)", "hi": "2-3 वर्ष (फलन)", "kn": "೨-೩ ವರ್ಷಗಳು (ಹಣು)"},
        "pests": {"en": "Fruit flies, Mealybugs", "hi": "फल मक्खी, मीलिबग", "kn": "ಹಣು ಮಕ್ಕಳು, ಮೀಲಿಬಗ್"}
    },
    {
        "id": "wheat",
        "name": {"en": "Wheat", "hi": "गेहूं", "kn": "ಗೋಧಿ"},
        "image": "wheat.jpg",
        "videos":"https://www.youtube.com/embed/SJv8bHTq4mU?",
        "soil": {"en": "Loamy, clay loam", "hi": "दोमट, चिकनी दोमट", "kn": "ಕೆಂಡ, ಚಿಕ್ಕ ಮಣ್ಣು"},
        "sunlight": {"en": "Full sun (8 hrs)", "hi": "पूर्ण सूर्य प्रकाश (8 घंटे)", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ (೮ ಗಂಟೆಗಳು)"},
        "water": {"en": "4-5 irrigations", "hi": "4-5 सिंचाई", "kn": "೪-೫ ನೀರು ಹಾಕುವುದು"},
        "temperature": {"en": "10-25°C (sowing)", "hi": "10-25°C (बुआई)", "kn": "೧೦-೨೫° ಸೆ. (ನಾಟಿ)"},
        "ph": {"en": "6.0-7.5", "hi": "6.0-7.5", "kn": "೬.೦-೭.೫"},
        "fertilizer": {"en": "120:60:40 NPK kg/ha", "hi": "120:60:40 NPK किग्रा/हेक्टेयर", "kn": "೧೨೦:೬೦:೪೦ NPK ಕೆ.ಜಿ/ಹೆಕ್ಟೇರ್"},
        "spacing": {"en": "20cm row spacing", "hi": "20cm पंक्ति दूरी", "kn": "೨೦ ಸೆ.ಮೀ. ಸಾಲು ಅಂತರ"},
        "harvest": {"en": "110-140 days", "hi": "110-140 दिन", "kn": "೧೧೦-೧೪೦ ದಿನಗಳು"},
        "pests": {"en": "Stem borer, Aphids", "hi": "स्टेम बोरर, एफिड्स", "kn": "ಕಂಬ ಬೋರರ್, ಆಫಿಡ್ಸ್"}
    },
    {
        "id": "rice",
        "name": {"en": "Rice", "hi": "चावल", "kn": "ಬಿಳಿ ಅಕ್ಕಿ"},
        "image": "rice.jpg",
        "videos": "https://www.youtube.com/embed/FW_bw9jdrlQ?",
        "soil": {"en": "Clay loam, water retentive", "hi": "चिकनी दोमट, जल धारक", "kn": "ಚಿಕ್ಕ ಮಣ್ಣು, ನೀರು ಇರಿಸುವ"},
        "sunlight": {"en": "Full sun", "hi": "पूर्ण सूर्य प्रकाश", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ"},
        "water": {"en": "Standing water (5cm)", "hi": "खड़ा पानी (5cm)", "kn": "ನಿಂತ ನೀರು (೫ ಸೆ.ಮೀ.)"},
        "temperature": {"en": "20-35°C", "hi": "20-35°C", "kn": "೨೦-೩೫° ಸೆ."},
        "ph": {"en": "5.5-7.0", "hi": "5.5-7.0", "kn": "೫.೫-೭.೦"},
        "fertilizer": {"en": "120:50:50 NPK kg/ha", "hi": "120:50:50 NPK किग्रा/हेक्टेयर", "kn": "೧೨೦:೫೦:೫೦ NPK ಕೆ.ಜಿ/ಹೆಕ್ಟೇರ್"},
        "spacing": {"en": "20cm x 15cm", "hi": "20cm x 15cm", "kn": "೨೦ ಸೆ.ಮೀ. x ೧೫ ಸೆ.ಮೀ."},
        "harvest": {"en": "110-140 days", "hi": "110-140 दिन", "kn": "೧೧೦-೧೪೦ ದಿನಗಳು"},
        "pests": {"en": "Stem borer, Leaf folder", "hi": "स्टेम बोरर, लीफ फोल्डर", "kn": "ಕಂಬ ಬೋರರ್, ಇಲೆ ಫೋಲ್ಡರ್"}
    },
    {
        "id": "peanut",
        "name": {"en": "Peanut", "hi": "मूंगफली", "kn": "ಕಡಲೆಕಾಯಿ"},
        "image": "peanut.jpg",
        "videos": "https://www.youtube.com/embed/i6SxMFDf4rQ?",
        "soil": {"en": "Sandy loam", "hi": "रेतीली दोमट", "kn": "ಹಾಲು ಮಣ್ಣು"},
        "sunlight": {"en": "Full sun", "hi": "पूर्ण सूर्य प्रकाश", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ"},
        "water": {"en": "Moderate (avoid waterlogging)", "hi": "मध्यम (जलभराव न हो)", "kn": "ಮಧ್ಯಮ (ನೀರು ತುಂಬಬೇಡ)"},
        "temperature": {"en": "20-30°C", "hi": "20-30°C", "kn": "೨೦-೩೦° ಸೆ."},
        "ph": {"en": "6.0-7.0", "hi": "6.0-7.0", "kn": "೬.೦-೭.೦"},
        "fertilizer": {"en": "20:40:40 NPK kg/ha", "hi": "20:40:40 NPK किग्रा/हेक्टेयर", "kn": "೨೦:೪೦:೪೦ NPK ಕೆ.ಜಿ/ಹೆಕ್ಟೇರ್"},
        "spacing": {"en": "30cm x 10cm", "hi": "30cm x 10cm", "kn": "೩೦ ಸೆ.ಮೀ. x ೧೦ ಸೆ.ಮೀ."},
        "harvest": {"en": "90-110 days", "hi": "90-110 दिन", "kn": "೯೦-೧೧೦ ದಿನಗಳು"},
        "pests": {"en": "Leaf miner, Aphids", "hi": "लीफ माइनर, एफिड्स", "kn": "ಇಲೆ ಮೈನರ್, ಆಫಿಡ್ಸ್"}
    },
    {
        "id": "ragi",
        "name": {"en": "Ragi (Finger Millet)", "hi": "नाचनी/रागी", "kn": "ರಾಗಿ"},
        "image": "ragi.jpg",
        "videos": "https://www.youtube.com/embed/CZF1wIeuTdA?",
        "soil": {"en": "Red loam, sandy loam", "hi": "लाल दोमट, रेतीली दोमट", "kn": "ಕೆಂಪು ಮಣ್ಣು, ಹಾಲು ಮಣ್ಣು"},
        "sunlight": {"en": "Full sun", "hi": "पूर्ण सूर्य प्रकाश", "kn": "ಪೂರ್ಣ ಸೂರ್ಯನ ಆಲೋಕ"},
        "water": {"en": "Low (drought tolerant)", "hi": "कम (सूखा सहनशील)", "kn": "ಕಡಿಮೆ (ಹರಳು ಸಹಿಸುವ)"},
        "temperature": {"en": "25-30°C", "hi": "25-30°C", "kn": "೨೫-೩೦° ಸೆ."},
        "ph": {"en": "5.0-8.0", "hi": "5.0-8.0", "kn": "೫.೦-೮.೦"},
        "fertilizer": {"en": "20:40:20 NPK kg/ha", "hi": "20:40:20 NPK किग्रा/हेक्टेयर", "kn": "೨೦:೪೦:೨೦ NPK ಕೆ.ಜಿ/ಹೆಕ್ಟೇರ್"},
        "spacing": {"en": "25cm x 10cm", "hi": "25cm x 10cm", "kn": "೨೫ ಸೆ.ಮೀ. x ೧೦ ಸೆ.ಮೀ."},
        "harvest": {"en": "90-120 days", "hi": "90-120 दिन", "kn": "೯೦-೧೨೦ ದಿನಗಳು"},
        "pests": {"en": "Stem borer, Shootfly", "hi": "स्टेम बोरर, शूटफ्लाई", "kn": "ಕಂಬ ಬೋರರ್, ಷೂಟ್‌ಫ್ಲೈ"}
    }
]
lang_texts = {
    'en': {
        'welcome': "Welcome farmer! I hope you are having a good day. Choose what you want to do.",
        'upload_title': "Leaf Disease Detection",
        'upload_btn': "Go to Plant Info Page",
        'analyze_btn': "Analyze Leaf",
        'disease': "Disease",
        'confidence': "Confidence",
        'recommendation': "Recommendation",
        'healthy': "Healthy Leaf",
        'healthy_msg': "Plant looks healthy. Maintain watering and sunlight.",
        'plants_title': "Plant Info Page",
        'plants_btn': "Go to Upload Leaf Detection",
        'treatment_btn': "💊 Treatment Suggestions",
        'treatment_title': "Detailed Treatment Plan",
        'map_btn': "🗺️ Find Nearby Shops",
        'map_title': "Nearby Agro Shops"
    },
    'hi': {
        'welcome': "किसान स्वागत है! आशा है आपका दिन अच्छा जा रहा है। जो करना चाहते हैं वह चुनें।",
        'upload_title': "पत्ती रोग पहचान",
        'upload_btn': "पौधे की जानकारी पेज पर जाएं",
        'analyze_btn': "पत्ती का विश्लेषण करें",
        'disease': "रोग",
        'confidence': "विश्वास",
        'recommendation': "सिफारिश",
        'healthy': "स्वस्थ पत्ती",
        'healthy_msg': "पौधा स्वस्थ दिख रहा है। पानी और धूप का ध्यान रखें।",
        'plants_title': "पौधे की जानकारी पेज",
        'plants_btn': "पत्ती अपलोड डिटेक्शन पर जाएं",
        'treatment_btn': "💊 उपचार सुझाव",
        'treatment_title': "विस्तृत उपचार योजना",
        'map_btn': "🗺️ आसपास की दुकानें खोजें",
        'map_title': "आसपास के कृषि स्टोर"
    },
    'kn': {
        'welcome': "ಶ್ರೀಮಂತ ರೈತರಿಗೆ ಸ್ವಾಗत! ನಿಮ್ಮ ದಿನ ಚೆನ್ನಾಗಿರುವುದು ಆಶಿಸುತ್ತೇನೆ. ನೀವು ಏನು ಮಾಡಬೇಕು ಎಂದು ಆಯ್ಕೆಮಾಡಿ.",
        'upload_title': "ಇಲೆ ರೋಗ ಸತ್ಯಾನ್ವೇಷಣೆ",
        'upload_btn': "ಬೆಳೆಗಳ ಮಾಹಿತಿ ಪುಟಕ್ಕೆ ಹೋಗಿ",
        'analyze_btn': "ಇಲೆಯನ್ನು ವಿಶ್ಲೇಷಿಸಿ",
        'disease': "ರೋಗ",
        'confidence': "ನಂಬಿಕೆ",
        'recommendation': "ಸಲಹೆ",
        'healthy': "ಆರೋಗ್ಯವಾದ ಇಲೆ",
        'healthy_msg': "ಬೆಳೆ ಆರೋಗ್ಯವಾಗಿದೆ. ನೀರು ಮತ್ತು ಸೂರ್ಯನ ಲಭ್ಯತೆಯನ್ನು ನಿರ್ವಹಿಸಿ.",
        'plants_title': "ಬೆಳೆಗಳ ಮಾಹಿತಿ ಪುಟ",
        'plants_btn': "ಇಲೆ ಅಪ್‌ಲೋಡ್ ಡಿಟೆಕ್ಷನ್‌ಗೆ ಹೋಗಿ",
        'treatment_btn': "💊 ಚಿಕಿತ್ಸೆ ಸಲಹೆಗಳು",
        'treatment_title': "ವಿವರವಾದ ಚಿಕಿತ್ಸಾ ಯೋಜನೆ",
        'map_btn': "🗺️ ಹತ್ತಿರದ ದುಕಾನುಗಳು",
        'map_title': "ಹತ್ತಿರದ ಕೃಷಿ ದುಕಾನುಗಳು"
    }
}
 
disease_info = {
    'en': {
        "Healthy Leaf": "Plant looks healthy. Maintain watering and sunlight.",
        "Tomato Early Blight": "Apply copper fungicide and avoid overhead watering.",
        "Tomato Late Blight": "Apply copper fungicide and avoid overhead watering.",
        "Potato Leaf Spot": "Remove infected leaves and monitor soil moisture.",
        "Powdery Mildew": "Spray fungicide and ensure proper air circulation."
    },
    'hi': {
        "Healthy Leaf": "पौधा स्वस्थ दिख रहा है। पानी और धूप का ध्यान रखें।",
        "Tomato Early Blight": "तांबे का फफूंदनाशक लगाएं और ऊपर से पानी न दें।",
        "Tomato Late Blight": "तांबे का फफूंदनाशक लगाएं और ऊपर से पानी न दें।",
        "Potato Leaf Spot": "प्रभावित पत्तियों को हटा दें और मिट्टी की नमी पर नजर रखें।",
        "Powdery Mildew": "फफूंदनाशक का छिड़काव करें और हवा का संचार सुनिश्चित करें।"
    },
    'kn': {
        "Healthy Leaf": "ಬೆಳೆ ಆರೋಗ್ಯವಾಗಿದೆ. ನೀರು ಮತ್ತು ಸೂರ್ಯನ ಲಭ್ಯತೆಯನ್ನು ನಿರ್ವಹಿಸಿ.",
        "Tomato Early Blight": "ತಾಮ್ರ ಫಂಗಸೈಡ್ ಅನ್ವಯಿಸಿ ಮತ್ತು ಮೇಲಿನಿಂದ ನೀರು ಸುಡಲು ಬಿಡಬೇಡಿ.",
        "Tomato Late Blight": "ತಾಮ್ರ ಫಂಗಸೈಡ್ ಅನ್ವಯಿಸಿ ಮತ್ತು ಮೇಲಿನಿಂದ ನೀರು ಸುಡಲು ಬಿಡಬೇಡಿ.",
        "Potato Leaf Spot": "ಅಂಧಕಾರಗೊಂಡ ಇಲೆಗಳನ್ನು ತೆಗೆಯಿರಿ ಮತ್ತು ಮಣ್ಣಿನ 습್ಯತೆಯನ್ನು ಪರೀಕ್ಷಿಸಿ.",
        "Powdery Mildew": "ಫಂಗಸೈಡ್ ಸಿಂಪಡಿಸಿ ಮತ್ತು ಸರಿಯಾದ ಗಾಳಿ ಸಂಚಾರವನ್ನು ಖಚಿತಪಡಿಸಿ."
    }
}

treatment_suggestions = {
    'en': {
        "Tomato Early Blight": [
            "1. Apply Copper Oxychloride (50% WP) - 2.5g/liter water every 10-15 days",
            "2. Remove and burn infected leaves immediately",
            "3. Use drip irrigation, avoid overhead watering",
            "4. Apply Neem oil (2ml/liter) as preventive measure",
            "5. Maintain proper spacing between plants"
        ],
        "Tomato Late Blight": [
            "1. Apply Mancozeb (75% WP) - 2g/liter water every 7-10 days",
            "2. Spray Ridomil Gold (2.5g/liter) during rainy season",
            "3. Remove lower leaves touching soil",
            "4. Apply Trichoderma (5g/kg seed) as soil treatment",
            "5. Ensure good air circulation between plants"
        ],
        "Potato Leaf Spot": [
            "1. Apply Chlorothalonil (2g/liter) every 10 days",
            "2. Remove and destroy infected leaves",
            "3. Apply balanced NPK fertilizer (10:26:26)",
            "4. Mulch with organic matter to reduce soil splash",
            "5. Spray Potassium Phosphite (3ml/liter) for resistance"
        ],
        "Powdery Mildew": [
            "1. Apply Sulphur 80% WP (2g/liter) every 7-10 days",
            "2. Spray Milk solution (1:9 ratio with water) weekly",
            "3. Use systemic fungicide like Hexaconazole (1ml/liter)",
            "4. Prune infected parts and burn them",
            "5. Apply Bio-fungicide Trichoderma viride (5g/liter)"
        ]
    },
    'hi': {
        "टमाटर अगेती झुलसा": [
            "1. कॉपर ऑक्सीक्लोराइड (50% WP) - 2.5 ग्राम/लीटर पानी हर 10-15 दिन",
            "2. संक्रमित पत्तियों को तुरंत हटाकर जला दें",
            "3. ड्रिप सिंचाई करें, ऊपर से पानी न दें",
            "4. निवारक के रूप में नीम तेल (2ml/लीटर)",
            "5. पौधों के बीच उचित दूरी रखें"
        ],
        "टमाटर पछेती झुलसा": [
            "1. मैनकोजेब (75% WP) - 2 ग्राम/लीटर हर 7-10 दिन",
            "2. बारिश के मौसम में रिडोमिल गोल्ड (2.5g/लीटर)",
            "3. मिट्टी को छूने वाली निचली पत्तियाँ हटाएँ",
            "4. ट्राइकोडर्मा (5g/kg बीज) मिट्टी उपचार के लिए",
            "5. पौधों के बीच अच्छा हवा का संचार"
        ],
        "आलू पत्ती धब्बा": [
            "1. क्लोरोथैलोनिल (2g/लीटर) हर 10 दिन",
            "2. संक्रमित पत्तियाँ हटाकर नष्ट करें",
            "3. संतुलित NPK उर्वरक (10:26:26)",
            "4. मिट्टी के छींटों को कम करने के लिए जैविक मल्चिंग",
            "5. प्रतिरोध के लिए पोटैशियम फॉस्फाइट (3ml/लीटर)"
        ],
        "पाउडरी मिल्ड्यू": [
            "1. सल्फर 80% WP (2g/लीटर) हर 7-10 दिन",
            "2. दूध घोल (1:9 अनुपात पानी के साथ) साप्ताहिक",
            "3. हेक्साकोनाजोल (1ml/लीटर) सिस्टमिक फफूंदनाशक",
            "4. संक्रमित भागों को छाँटकर जला दें",
            "5. बायो-फफूंदनाशक ट्राइकोडर्मा विरिडे (5g/लीटर)"
        ]
    },
    'kn': {
        "ಟೊಮ್ಯಾಟೋ ಆರಂಭಿಕ ಬ್ಲೈಟ್": [
            "1. ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (50% WP) - 2.5g/ಲೀಟರ್ ನೀರು 10-15 ದಿನಗಳಿಗೊಮ್ಮೆ",
            "2. ಸೋಂಕಿತ ಇಲೆಗಳನ್ನು ತೆಗೆದು ಉಂಟಿಸಿ",
            "3. ಡ್ರಿಪ್ ತುಂಡು, ಮೇಲಿನಿಂದ ನೀರು ಸುಡಬೇಡಿ",
            "4. ತಡೆಗಟ್ಟುವಿಗೆ ನೀಮ್ ತೈಲ (2ml/ಲೀಟರ್)",
            "5. ಸಸ್ಯಗಳ ನಡುವೆ ಸರಿಯಾದ ಅಂತರ"
        ],
        "ಟೊಮ್ಯಾಟೋ ತಡ ಬ್ಲೈಟ್": [
            "1. ಮ್ಯಾಂಕೋಜೆಬ್ (75% WP) - 2g/ಲೀಟರ್ 7-10 ದಿನಗಳಿಗೊಮ್ಮೆ",
            "2. ಮಳೆ ಕಾಲದಲ್ಲಿ ರಿಡೋಮಿಲ್ ಗೋಲ್ಡ್ (2.5g/ಲೀಟರ್)",
            "3. ಮಣ್ಣು ಸ್ಪರ್ಶಿಸುವ ಕೆಳಗಿನ ಇಲೆಗಳನ್ನು ತೆಗೆಯಿರಿ",
            "4. ಟ್ರೈಕೋಡರ್ಮಾ (5g/kg ಬೀಜ) ಮಣ್ಣು ಚಿಕಿತ್ಸೆಗೆ",
            "5. ಸಸ್ಯಗಳ ನಡುವೆ ಚೆನ್ನಾಗಿ ಗಾಳಿ ಸಂಚಾರ"
        ],
        "ಆಲೂಗಡ್ಡೆ ಇಲೆ ಸ್ಪಾಟ್": [
            "1. ಕ್ಲೋರೋಥಾಲೋನಿಲ್ (2g/ಲೀಟರ್) 10 ದಿನಗಳಿಗೊಮ್ಮೆ",
            "2. ಸೋಂಕಿತ ಇಲೆಗಳನ್ನು ತೆಗೆದು ನಾಶಮಾಡಿ",
            "3. ಸಮತೋಲಿತ NPK ಗೊಬ್ಬರ (10:26:26)",
            "4. ಮಣ್ಣಿನ ಚಿಮ್ಮುಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಸಾವಯವ ಮಲ್ಚಿಂಗ್",
            "5. ಪೊಟ್ಯಾಶಿಯಂ ಫಾಸ್ಫೈಟ್ (3ml/ಲೀಟರ್) ಪ್ರತಿರೋಧಕ್ಕೆ"
        ],
        "ಪೌಡರಿ ಮಿಲ್ಡ್ಯೂ": [
            "1. ಸಲ್ಫರ್ 80% WP (2g/ಲೀಟರ್) 7-10 ದಿನಗಳಿಗೊಮ್ಮೆ",
            "2. ಹಾಲಿನ ಮಿಶ್ರಣ (1:9 ನೀರು) ಸಾಪ್ತಾಹಿಕ",
            "3. ಹೆಕ್ಸಾಕೋನಾಜೋಲ್ (1ml/ಲೀಟರ್) ಸಿಸ್ಟಮಿಕ್ ಫಂಗಸೈಡ್",
            "4. ಸೋಂಕಿತ ಭಾಗಗಳನ್ನು ಕತ್ತರಿಸಿ ಉಂಟಿಸಿ",
            "5. ಬಯೋ-ಫಂಗಸೈಡ್ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ (5g/ಲೀಟರ್)"
        ]
    }
}

nearby_shops = [
    {
        "id": 1,
        "name": {"en": "Mak Agri Care", "hi": "माक एग्री केयर", "kn": "ಮಾಕ್ ಆಗ್ರಿ ಕೇರ್"},
        "lat": 12.9905,
        "lng": 77.5521,
        "address": {"en": "19th Main Road, 1st Block Rajajinagar, Bengaluru", "hi": "19वीं मुख्य सड़क, 1st ब्लॉक राजाजीनगर", "kn": "೧೯ನೇ ಮುಖ್ಯ ರಸ್ತೆ, ೧ನೇ ಬ್ಲಾಕ್ ರಾಜಾಜಿನಗರ್"},
        "price_range": {"en": "₹200-₹1000", "hi": "₹200-₹1000", "kn": "₹200-₹1000"},
        "products": {"en": "Fungicides (Tricolor, Copper-based)", "hi": "फफूंदनाशक (ट्राइकलर, तांबा-आधारित)", "kn": "ಫಂಗಸೈಡ್ (ಟ್ರೈಕಾಲರ್, ತಾಮ್ರ ಆಧಾರಿತ)"}
    },
    {
        "id": 2,
        "name": {"en": "Agriplex Pvt Ltd", "hi": "एग्रीप्लेक्स प्राइवेट लिमिटेड", "kn": "ಆಗ್ರಿಪ್ಲೆಕ್ಸ್ ಪ್ರೈವೇಟ್ ಲಿಮಿಟೆಡ್"},
        "lat": 12.9650,
        "lng": 77.6420,
        "address": {"en": "Jayanagar 4th Block area, Bengaluru", "hi": "जयानगर 4th ब्लॉक क्षेत्र", "kn": "ಜಯನಗರ ೪ನೇ ಬ್ಲಾಕ್ ಪ್ರದೇಶ"},
        "price_range": {"en": "₹150-₹800", "hi": "₹150-₹800", "kn": "₹150-₹800"},
        "products": {"en": "Neem Oil, Bio-fungicides, Mancozeb", "hi": "नीम तेल, बायो-फफूंदनाशक, मैनकोजेब", "kn": "ನೀಮ್ ತೈಲ, ಬಯೋ-ಫಂಗಸೈಡ್, ಮ್ಯಾಂಕೋಜೆಬ್"}
    },
    {
        "id": 3,
        "name": {"en": "FarmIndia Supplies", "hi": "फार्मइंडिया सप्लाईज", "kn": "ಫಾರ್ಮಿಂಡಿಯಾ ಸಪ್ಲೈಸ್"},
        "lat": 12.9279,
        "lng": 77.6276,
        "address": {"en": "1st Cross, 3rd Block Koramangala, Bengaluru", "hi": "1st क्रॉस, 3rd ब्लॉक कोरमंगला", "kn": "೧ನೇ ಕ್ರಾಸ್, ೩ನೇ ಬ್ಲಾಕ್ ಕೋರಮಂಗಲ"},
        "price_range": {"en": "₹300-₹1200", "hi": "₹300-₹1200", "kn": "₹300-₹1200"},
        "products": {"en": "Organic Fertilizers, Pesticides, Chlorothalonil", "hi": "जैविक उर्वरक, कीटनाशक, क्लोरोथैलोनिल", "kn": "ಸಾವಯವ ಗೊಬ್ಬರ, ಕೀಟನಾಶಕ, ಕ್ಲೋರೋಥಾಲೋನಿಲ್"}
    },
    {
        "id": 4,
        "name": {"en": "Samrudhi Agro Centre", "hi": "समृद्धि एग्रो सेंटर", "kn": "ಸಮೃದ್ಧಿ ಆಗ್ರೋ ಸೆಂಟರ್"},
        "lat": 12.9595,
        "lng": 77.5942,
        "address": {"en": "New Tharagupet, Bengaluru", "hi": "न्यू थरागुपेट, बेंगलुरु", "kn": "ನ್ಯೂ ಥರಗುಪೇಟ್, ಬೆಂಗಳೂರು"},
        "price_range": {"en": "₹100-₹700", "hi": "₹100-₹700", "kn": "₹100-₹700"},
        "products": {"en": "Sulphur WP, Trichoderma, Potassium Phosphite", "hi": "सल्फर WP, ट्राइकोडर्मा, पोटैशियम फॉस्फाइट", "kn": "ಸಲ್ಫರ್ WP, ಟ್ರೈಕೋಡರ್ಮಾ, ಪೊಟ್ಯಾಶಿಯಂ ಫಾಸ್ಫೈಟ್"}
    }
]
def get_weather_current(lat=12.9716, lon=77.5946):  
    
    """Get current weather with fallback"""
    try:
        print(f" Fetching weather for {lat},{lon}...") 
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        print(f"API Status: {response.status_code}")  
        
        data = response.json()
        if response.status_code == 200:
            weather = {
                "temp": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "condition": data['weather'][0]['main'],
                "description": data['weather'][0]['description']
            }
            print(f" Weather: {weather['temp']}°C, {weather['humidity']}%")  
            return weather
        else:
            print(f" API Error: {data}")  
            return {"error": "API failed", "code": response.status_code}
    except Exception as e:
        print(f" Exception: {e}")  
        return {"error": str(e)}
def get_current_lang():
    return session.get('lang', 'en')   
@app.route("/weather")
def weather_page():
    lang_code = session.get('lang','en')
    current = get_weather_current()
    forecast = get_weather_forecast()
    texts = lang_texts.get(lang_code, lang_texts['en'])
    weather = get_weather_current()
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title> Current Weather</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
body {font-family: 'Segoe UI'; background: linear-gradient(135deg, #FFF8E1 0%, #E8F5E8 100%); padding:20px; margin:0;}
.main-container {max-width:800px; margin:0 auto; text-align:center;}
.weather-card {background:white; padding:40px; border-radius:25px; box-shadow:0 20px 40px rgba(0,0,0,0.1); margin:30px 0;}
.temp-big {font-size:6em; font-weight:bold; color:#F57C00; margin:0;}
.condition {font-size:2em; color:#2196F3; margin:10px 0;}
.stats {display:grid; grid-template-columns:repeat(3,1fr); gap:20px; margin:30px 0;}
.stat {background:#f8f9fa; padding:20px; border-radius:15px;}
button {padding:15px 30px; font-size:18px; border:none; border-radius:25px; margin:10px; cursor:pointer;}
.primary {background:linear-gradient(45deg, #F57C00, #E68900); color:white;}
.weather-btn {background:linear-gradient(45deg, #2196F3, #1976D2); color:white;}
</style>
</head>
<body>
<div class="main-container">
    <h1 style="color:#2196F3; font-size:2.5em;"> Current Bengaluru Weather</h1>
    
    <div style="margin:30px 0;">
        <button class="primary" onclick="location.href='/upload'">Upload the image</button>
        <button class="primary" onclick="location.href='/plants'">Plants</button>
        <button class="primary" onclick="location.href='/map'"> Shops</button>
        <button onclick="location.href='/chatbot'" class="btn">Assistant</button>
    </div>

    {% if weather and weather.get('temp') %}
    <div class="weather-card">
        <div class="temp-big">{{ "%.1f"|format(weather.temp) }}°C</div>
        <div class="condition">{{ weather.condition }}</div>
        <p style="font-size:1.3em; color:#666;">{{ weather.description|title }}</p>
        
        <div class="stats">
            <div class="stat">
                <i class="fas fa-tint" style="font-size:2em; color:#2196F3;"></i>
                <div style="font-size:2em; font-weight:bold;">{{ weather.humidity }}%</div>
                <div>Humidity</div>
            </div>
        </div>
        
        <p style="font-size:1.2em; color:#2E7D32;">Updated: {{ "now"|string }}</p>
    </div>
    {% else %}
    <div class="weather-card" style="background:#ffebee;">
        <h2> Weather Not Available</h2>
        <p><strong>Reasons:</strong></p>
        <ul style="text-align:left; font-size:1.1em;">
            <li> No API key set</li>
            <li> Internet down</li>
            <li> API quota exceeded</li>
        </ul>
        <p><strong>Fix:</strong> Check terminal console (F12) for error details</p>
    </div>
    {% endif %}
</div>
</body>
</html>""", texts=texts, weather=weather, forecast=forecast)

disease_names = {
    'en': ["Tomato Early Blight","Tomato Late Blight","Potato Leaf Spot","Powdery Mildew"],
    'hi': ["टमाटर अगेती झुलसा","टमाटर पछेती झुलसा","आलू पत्ती धब्बा","पाउडरी मिल्ड्यू"],
    'kn': ["ಟೊಮ್ಯಾಟೋ ಆರಂಭಿಕ ಬ್ಲೈಟ್","ಟೊಮ್ಯಾಟೋ ತಡ ಬ್ಲೈಟ್","ಆಲೂಗಡ್ಡೆ ಇಲೆ ಸ್ಪಾಟ್","ಪೌಡರಿ ಮಿಲ್ಡ್ಯೂ"]
}
def speak(text, lang='en'):
    try:
        tts = gTTS(text=text, lang=lang)
        filename = "temp.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print("TTS error:", e)

def get_text(key, lang):
    return lang_texts.get(lang, lang_texts['en']).get(key, key)

def get_plant_text(plant, key, lang):
    return plant[key].get(lang, plant[key]['en'])

def predict_disease(image_path, lang='en'):
    image = cv2.imread(image_path)
    if image is None:
        return "Could not load image", 0, "Check file path"
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_intensity = gray.mean()
    
    if mean_intensity > 120:
        return get_text('healthy', lang), round(random.uniform(0.85,0.95),2), get_text('healthy_msg', lang)
    else:
        english_diseases = ["Tomato Early Blight", "Tomato Late Blight", "Potato Leaf Spot", "Powdery Mildew"]
        disease_en = random.choice(english_diseases)
        confidence = round(random.uniform(0.80,0.92),2)
        
        disease_list = disease_names.get(lang, disease_names['en'])
        disease_display = random.choice(disease_list)
        
        recommendation = disease_info.get(lang, disease_info['en']).get(disease_en, "Consult expert.")
        
        return disease_display, confidence, recommendation, disease_en  
HOME_HTML="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌱 </title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', sans-serif;
            height: 50vh;
            overflow: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            position: relative;
        }
        .bg-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1.5" fill="rgba(255,255,255,0.05)"/><circle cx="50" cy="10" r="0.8" fill="rgba(255,255,255,0.08)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>'),
            z-index: 1;
            animation: float 20s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-10px) rotate(1deg); }
        }
        
        .container {
            position: relative;
            z-index: 10;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: white;
            padding: 20px;
        }
        .welcome-hero {
            font-size: clamp(2.5rem, 8vw, 5rem);
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #FFD700, #FFA500, #FF6347);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: welcomeGlow 3s ease-in-out infinite alternate, slideInUp 1s ease-out;
            text-shadow: 0 0 30px rgba(255,215,0,0.5);
        }
        
        @keyframes welcomeGlow {
            from { filter: drop-shadow(0 0 20px #FFD700); }
            to { filter: drop-shadow(0 0 40px #FFA500); }
        }
        
        @keyframes slideInUp {
            from { transform: translateY(100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        .welcome-subtitle {
            font-size: clamp(1.2rem, 4vw, 2rem);
            margin-bottom: 50px;
            opacity: 0;
            animation: fadeInUp 1s ease-out 0.5s forwards;
            max-width: 600px;
            line-height: 1.4;
        }
        
        @keyframes fadeInUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .lang-prompt {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            padding: 25px 40px;
            border-radius: 25px;
            margin-bottom: 40px;
            border: 1px solid rgba(255,255,255,0.2);
            opacity: 0;
            animation: fadeInUp 1s ease-out 1s forwards;
            font-size: 1.2rem;
            font-weight: 400;
        }
        .lang-buttons {
            display: flex;
            gap: 25px;
            flex-wrap: wrap;
            justify-content: center;
            opacity: 0;
            animation: fadeInUp 1s ease-out 1.5s forwards;
        }
        
        .lang-btn {
            padding: 20px 40px;
            font-size: 1.4rem;
            font-weight: 600;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            min-width: 200px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .lang-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .lang-btn:hover::before {
            left: 100%;
        }
        
        .en-btn { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; }
        .hi-btn { background: linear-gradient(45deg, #FF5722, #E64A19); color: white; }
        .kn-btn { background: linear-gradient(45deg, #2196F3, #1976D2); color: white; }
        
        .lang-btn:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }
        
        .lang-btn:active {
            transform: translateY(-5px) scale(1.02);
        }
        .farmer-icon {
            font-size: 8rem;
            margin-bottom: 20px;
            animation: bounce 2s infinite;
            opacity: 0.9;
        }
        
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            60% { transform: translateY(-10px); }
        }
        @media (max-width: 768px) {
            .lang-buttons { flex-direction: column; align-items: center; }
            .lang-btn { width: 250px; }
        }
        .loading {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(102, 126, 234, 0.95);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            transition: opacity 0.5s;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(255,255,255,0.3);
            border-top: 5px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div class="loading" id="loading">
        <div class="spinner"></div>
    </div>
    
    <div class="bg-pattern"></div>
    
    <div class="container">
        <div class="farmer-icon">
            <i class="fas fa-tractor"></i>
        </div>
        
        <h1 class="welcome-hero" id="welcomeText">
{{ ' PlantCare Assistant' if lang=='en' else ' PlantCare सहायक' if lang=='hi' else ' PlantCare ಸಹಾಯಕ' }}</h1>
        <p class="welcome-subtitle">
{{ 'Empowering farmers with AI-powered plant disease detection, weather forecasts & expert advice' if lang=='en' else 'AI-संचालित पौधे रोग पहचान, मौसम पूर्वानुमान और विशेषज्ञ सलाह से किसानों को सशक्त बनाना' if lang=='hi' else 'AI ಸಹಾಯದಿಂದ ಬೆಳೆ ರೋಗ ಗುರುತಿಸುವಿಕೆ, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಮತ್ತು ತಜ್ಞರ ಸಲಹೆಯಿಂದ ರೈತರನ್ನು ಬಲಪಡಿಸುವುದು' }}</p>
        <div class="lang-prompt">
            <i class="fas fa-globe-asia"></i>
            Select your language / अपनी भाषा चुनें / ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆರಿಸಿ
        </div>
        
        <div class="lang-buttons">
            <button class="lang-btn en-btn" onclick="chooseLanguage('en')">
                <i class="flag-icon-us"></i> English
            </button>
            <button class="lang-btn hi-btn" onclick="chooseLanguage('hi')">
                <i class="flag-icon-in"></i> हिंदी
            </button>
            <button class="lang-btn kn-btn" onclick="chooseLanguage('kn')">
                <i class="flag-icon-in"></i> ಕನ್ನಡ
            </button>
        <!-- NEW HELPLINE BUTTON -->
    <button class="lang-btn call-btn" onclick="window.location.href='/helpline'" style="background: linear-gradient(45deg, #ff6b6b, #ff5252);">
        <i class="fas fa-phone"></i> Helpline
    </button>
        </div>
    </div>
                                  <!-- Add this after lang-prompt div (~line 240) -->
    <div style="margin:30px 0;">
        <a href="/helpline" style="color:white;text-decoration:none;font-size:1.3rem;font-weight:600;padding:15px 30px;background:rgba(255,107,107,0.3);border-radius:30px;border:2px solid rgba(255,255,255,0.4);display:inline-block;transition:all 0.3s;">
<i class="fas fa-phone"></i> {{ 'Need Help Now? Contact Helpline' if lang=='en' else 'अभी मदद चाहिए? हेल्पलाइन संपर्क करें' if lang=='hi' else 'ಈಗ ಸಹಾಯ ಬೇಕೇ? ಹೆಲ್ಪ್‌ಲೈನ್ ಸಂಪರ್ಕಿಸಿ' }}
</a>

    </div>
    <script>
        // Hide loading screen
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.getElementById('loading').style.opacity = '0';
                setTimeout(() => {
                    document.getElementById('loading').style.display = 'none';
                }, 500);
            }, 1000);
        });
        
        function chooseLanguage(lang) {
            // Show loading
            document.getElementById('loading').style.display = 'flex';
            document.getElementById('loading').style.opacity = '1';
            
            // Set language and redirect
            fetch('/set_language?lang=' + lang)
                .then(() => {
                    setTimeout(() => {
                        window.location.href = '/upload';
                    }, 800);
                })
                .catch(err => {
                    console.error('Language set error:', err);
                    window.location.href = '/upload';
                });
        }
        document.addEventListener('DOMContentLoaded', () => {
            const enFlag = document.querySelector('.en-btn i');
            enFlag.className = 'fas fa-flag-usa';
            
            const hiFlag = document.querySelector('.hi-btn i');
            hiFlag.className = 'fas fa-flag';
            
            const knFlag = document.querySelector('.kn-btn i');
            knFlag.className = 'fas fa-flag';
        });
    </script>
</body>
</html>
"""
@app.route("/")
def home():
    send_laptop_sms()
    lang = get_current_lang() 
    print(f"🔍 DEBUG: Current lang = '{lang}' | Session = {session.get('lang', 'NONE')}")
    return render_template_string(HOME_HTML, lang=lang)

@app.route("/set_language")
def set_language():
    lang = request.args.get('lang','en')
    session['lang'] = lang
    welcome_text = {
        'en': "Welcome farmer! I hope you are having a good day. Choose what you want to do.",
        'hi': "किसान स्वागत है! आशा है आपका दिन अच्छा जा रहा है। जो करना चाहते हैं वह चुनें।",
        'kn': "ರೈತರಿಗೆ ಸ್ವಾಗತ!. ನೀವು ಏನು ಮಾಡಬೇಕು ಎಂದು ಆಯ್ಕೆಮಾಡಿ."
    }
    threading.Thread(target=speak, args=(welcome_text.get(lang,'en'), lang)).start()
    return "OK"

@app.route("/upload", methods=["GET","POST"])
def upload_leaf():
    lang_code = session.get('lang','en')
    texts = lang_texts.get(lang_code, lang_texts['en'])
    
    result = session.get('analysis_result')
    show_treatment = request.args.get('show_treatment') == 'true'
    
    if request.method == "POST":
        if 'leaf_image' in request.files:
            file = request.files['leaf_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                disease, confidence, recommendation, disease_english = predict_disease(path, lang_code)
                disease_english = disease 
                result = {
                    "disease": disease,
                    "confidence": confidence,
                    "recommendation": recommendation,
                    "filename": filename,
                    "disease_english": disease_english or "healthy_leaf"
                }
                session['analysis_result'] = result
                
                speak_text = f"{texts.get('disease', 'Disease')}: {disease}. {texts.get('recommendation', 'Recommendation')}: {recommendation}"
                threading.Thread(target=speak, args=(speak_text, lang_code)).start()
    treatment_list = []
    if result and show_treatment and result.get('disease_english'):
        treatments = treatment_suggestions.get(lang_code, treatment_suggestions.get('en', {}))
        treatment_list = treatments.get(result.get('disease_english'), [])

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>{{ texts['upload_title'] }}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { 
    font-family: 'Poppins', sans-serif; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh; 
    padding: 20px;
}
.main-container {max-width:1400px; margin:0 auto;}
h1 { 
    color:white; 
    font-size:3em; 
    text-align:center; 
    margin:30px 0; 
    text-shadow:0 4px 20px rgba(0,0,0,0.3);
}

.action-buttons {
    display:flex; justify-content:center; gap:20px; margin:40px 0; flex-wrap:wrap;
}
.btn {
    padding:18px 35px; font-size:18px; border:none; border-radius:25px;
    cursor:pointer; font-weight:600; text-transform:uppercase;
    letter-spacing:1px; min-width:220px; transition:all 0.3s ease;
    box-shadow:0 10px 30px rgba(0,0,0,0.3);
    color:white; text-decoration:none; display:inline-block;
    text-align:center;
}
.btn:hover { transform:translateY(-5px) scale(1.05); box-shadow:0 15px 40px rgba(0,0,0,0.4); }
.primary { background:linear-gradient(45deg, #F57C00, #E68900); }
.weather { background:linear-gradient(45deg, #2196F3, #1976D2); }
.plants { background:linear-gradient(45deg, #4CAF50, #45a049); }

.upload-section {
    background:rgba(255,255,255,0.15); backdrop-filter:blur(20px);
    border-radius:30px; padding:50px; margin:40px 0; border:1px solid rgba(255,255,255,0.2);
    box-shadow:0 25px 60px rgba(0,0,0,0.2);
}
.upload-title { color:white; font-size:2.2em; margin-bottom:30px; text-align:center; }

.file-upload-container {
    position:relative; display:inline-block; width:100%; max-width:500px; margin:0 auto;
}
.file-input { display:none; }
.file-upload-btn {
    width:100%; padding:25px 40px; background:linear-gradient(145deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
    border:2px dashed rgba(255,255,255,0.4); border-radius:25px; cursor:pointer;
    transition:all 0.4s ease; text-align:center; backdrop-filter:blur(10px);
    font-size:1.4em; color:white; font-weight:600;
}
.upload-background {
    position:absolute; top:0; left:0; width:100%; height:100%;
    border-radius:25px; overflow:hidden; opacity:0.3; z-index:1;
}
.upload-background img {
    width:100%; height:100%; object-fit:cover;
}
.upload-content {
    position:relative; z-index:2; padding:25px 40px;
    text-align:center;
}
.file-upload-btn {
    position:relative; /* ADD THIS */
    width:100%; padding:0; /* CHANGE THIS */
    background:linear-gradient(145deg, rgba(255,255,255,0.25), rgba(255,255,255,0.1));
    border:3px dashed rgba(255,255,255,0.5);
    min-height:250px; /* ADD HEIGHT */
}
.file-upload-btn:hover {
    background:linear-gradient(145deg, rgba(255,255,255,0.3), rgba(255,255,255,0.2));
    border-color:rgba(255,255,255,0.6); transform:scale(1.02);
    box-shadow:0 20px 50px rgba(0,0,0,0.3);
}
.file-upload-btn.dragover {
    background:linear-gradient(145deg, rgba(76,175,80,0.3), rgba(76,175,80,0.2));
    border-color:#4CAF50; transform:scale(1.05);
}
.upload-icon { font-size:3em; margin-bottom:15px; display:block; }
.file-name { margin-top:15px; font-size:1.1em; opacity:0.9; }

.results-grid {
    display:grid; grid-template-columns:1fr 1fr; gap:40px; margin-top:50px;
}
.result-card {
    background:rgba(255,255,255,0.15); backdrop-filter:blur(20px);
    border-radius:25px; padding:40px; border:1px solid rgba(255,255,255,0.2);
    box-shadow:0 20px 50px rgba(0,0,0,0.2);
}
.disease-card { border-left:5px solid #F57C00; }
.treatment-card { border-left:5px solid #4CAF50; }
.card-title {
    font-size:2em; margin-bottom:25px; text-align:center;
    font-weight:700;
}
.disease-title { color:#F57C00; }
.treatment-title { color:#4CAF50; }
.disease-name { 
    color:#F57C00; font-size:2.5em; margin:20px 0; font-weight:700; 
    text-shadow:0 2px 10px rgba(245,124,0,0.3);
}
.confidence-bar {
    background:rgba(255,255,255,0.2); height:25px; border-radius:15px;
    margin:25px 0; overflow:hidden;
}
.confidence-fill {
    height:100%; background:linear-gradient(90deg, #4CAF50, #8BC34A);
    border-radius:15px; transition:width 1.5s ease;
}
.confidence-text { 
    color:white; font-size:1.3em; font-weight:600; margin:15px 0;
}
.leaf-image {
    width:100%; max-height:300px; object-fit:cover; border-radius:20px;
    border:4px solid rgba(255,255,255,0.3); box-shadow:0 15px 40px rgba(0,0,0,0.3);
    margin:25px 0;
}
.treatment-list {
    max-height:450px; overflow-y:auto; padding-right:10px;
}
.treatment-list::-webkit-scrollbar { width:6px; }
.treatment-list::-webkit-scrollbar-track { background:rgba(255,255,255,0.1); border-radius:10px; }
.treatment-list::-webkit-scrollbar-thumb { 
    background:#4CAF50; border-radius:10px; 
}
.treatment-item {
    background:rgba(255,255,255,0.2); margin:15px 0; padding:20px;
    border-radius:15px; backdrop-filter:blur(10px); border-left:4px solid #4CAF50;
    transition:all 0.3s ease;
}
.treatment-item:hover { transform:translateX(10px); box-shadow:0 10px 30px rgba(0,0,0,0.2); }

.treatment-toggle {
    width:100%; padding:18px; margin-top:25px; background:linear-gradient(45deg, #4CAF50, #45a049);
    color:white; border:none; border-radius:20px; font-size:1.2em; font-weight:600;
    cursor:pointer; transition:all 0.3s ease;
}
.treatment-toggle:hover { transform:translateY(-3px); box-shadow:0 15px 40px rgba(76,175,80,0.4); }

@media (max-width:1024px) {
    .results-grid { grid-template-columns:1fr; }
}
@media (max-width:768px) {
    .action-buttons { flex-direction:column; }
    .btn { width:100%; }
    h1 { font-size:2em; }
    .upload-section { padding:30px 20px; }
}

.upload-options { align-items: start; }
.upload-column, .camera-column { background: rgba(255,255,255,0.1); 
    border-radius: 20px; padding: 30px; backdrop-filter: blur(10px); }
.camera-container { position: relative; }
.camera-preview {
    width: 100%; height: 280px; background: rgba(0,0,0,0.3);
    border-radius: 20px; display: flex; align-items: center; justify-content: center;
    border: 3px dashed rgba(255,255,255,0.3); overflow: hidden;
}
#videoElement { width: 100%; height: 100%; object-fit: cover; border-radius: 17px; }
.camera-placeholder { text-align: center; opacity: 0.5; }
.camera-controls { display: flex; flex-direction: column; gap: 12px; }
.camera-btn {
    padding: 15px 25px; border: none; border-radius: 20px; font-size: 16px;
    font-weight: 600; cursor: pointer; transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.start-camera { background: linear-gradient(45deg, #2196F3, #1976D2); color: white; }
.capture-photo { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; }
.stop-camera { background: linear-gradient(45deg, #f44336, #d32f2f); color: white; }
.camera-btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 35px rgba(0,0,0,0.3); }
.camera-btn:active { transform: translateY(-1px); }

@media (max-width: 768px) {
    .upload-options { grid-template-columns: 1fr !important; }
    .camera-preview { height: 250px; }
}
</style>
</head>
<body>
<div class="main-container">
    <h1><i class="fas fa-leaf"></i> {{ texts['upload_title'] }}</h1>
    
    <div class="action-buttons">
        <a href="/plants" class="btn plants">Plants</a>
        <a href="/weather" class="btn weather">Weather</a>
        <a href="/map" class="btn primary"> Shops</a>
        <a href="/chatbot" class="btn" style="background:linear-gradient(45deg, #9C27B0, #7B1FA2);">🤖 Assistant</a>
    </div>
<div class="upload-section">
    <h2 class="upload-title"><i class="fas fa-cloud-upload-alt"></i> Upload Leaf Image</h2>
    
    <div class="upload-options" style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; max-width: 1000px; margin: 0 auto;">
        
        <div class="upload-column">
            <h3 style="color: white; margin-bottom: 20px; opacity: 0.9;"> Choose File</h3>
            <form method="POST" enctype="multipart/form-data" id="uploadForm">
                <div class="file-upload-container">
                    <input type="file" name="leaf_image" id="fileInput" class="file-input" accept="image/*" required>
                    <label for="fileInput" class="file-upload-btn" id="fileLabel">
                        <div class="upload-background">
                            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNTAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDUwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI1MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRkZGMEJCIiBmaWxsLW9wYWNpdHk9IjAuMSIvPgo8Y2lyY2xlIGN4PSI4MCIgY3k9IjgwIiByPSI0MCIgZmlsbD0iI0ZGQjAwMCIgZmlsbC1vcGFjaXR5PSIwLjIiLz4KPGNpcmNsZSBjeD0iNDEwIiBjeT0iMTIwIiByPSIzNSIgZmlsbD0iIzRDMUY1MCIgZmlsbC1vcGFjaXR5PSIwLjE1Ii8+CjxjaXJjbGUgY3g9IjIwMCIgY3k9IjIwMCIgcj0iNTAiIGZpbGw9IiMyRTdEMzIiIGZpbGwtb3BhY2l0eT0iMC4xIi8+CjxjaXJjbGUgY3g9IjM1MCIgY3k9IjUwIiByPSIyNSIgZmlsbD0iI0ZGQTAwMCIgZmlsbC1vcGFjaXR5PSIwLjIiLz4KPHBhdGggZD0iTTAgMzAwIEw1MDAgMzAwIEw1MDAgMjUwIEw0NzAgMjAwIEw0MjAgMTUwIEwzNzAgMTAwIEwzMDAgODAgTDIwMCAxMjAgTDEyMCAxNjAgTDgwIDIwMCBMNDAgMjUwIEwwIDMwMCIgZmlsbD0iI0ZGRTgwMCIgZmlsbC1vcGFjaXR5PSIwLjA1Ii8+Cjwvc3ZnPgo=" alt="Leaf pattern">
                        </div>
                        <div class="upload-content">
                            <span class="upload-icon"></span>
                            <strong>Click or Drag Photo</strong><br>
                            <span style="opacity:0.9;">Choose leaf image</span>
                            <div class="file-name" id="fileName">No file selected</div>
                        </div>
                    </label>
                </div>
                <button type="submit" class="btn primary" style="margin-top:25px; width:100%;">
                    <i class="fas fa-search"></i> Analyze Photo
                </button>
            </form>
        </div>

        <div class="camera-column">
            <h3 style="color: white; margin-bottom: 20px; opacity: 0.9;"> Live Camera</h3>
            <div class="camera-container">
                <div class="camera-preview" id="cameraPreview">
                    <div class="camera-placeholder">
                        <i class="fas fa-video" style="font-size: 4em; color: rgba(255,255,255,0.3); margin-bottom: 20px;"></i>
                        <p style="color: rgba(255,255,255,0.6);">Click camera to start</p>
                    </div>
                    <video id="videoElement" style="display: none;" autoplay muted playsinline></video>
                    <canvas id="photoCanvas" style="display: none;"></canvas>
                </div>
                
                <div class="camera-controls" style="margin-top: 20px;">
                    <button class="camera-btn start-camera" onclick="startCamera()">
                        <i class="fas fa-camera"></i>Start camera</button>
                    <button class="camera-btn capture-photo" onclick="capturePhoto()" style="display: none;">
                        <i class="fas fa-camera-retro"></i>Capture camera</button>
                    <button class="camera-btn stop-camera" onclick="stopCamera()" style="display: none;">
                        <i class="fas fa-stop"></i>Stop camera</button>
                </div>
            </div>
        </div>
    </div>
</div>

    {% if result %}
    <div class="results-grid">
        <div class="result-card disease-card">
            <h3 class="card-title disease-title">
                <i class="fas fa-stethoscope"></i> Disease Recommender
            </h3>
            <div class="disease-name">{{ result.disease }}</div>
            
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {{ "%.0f"|format(result.confidence*100) }}%"></div>
            </div>
            <div class="confidence-text">
                Confidence: {{ "%.1f"|format(result.confidence*100) }}%
            </div>
            
            <p style="color:white; font-size:1.2em; margin:25px 0; line-height:1.6;">
                <strong>Treatment:</strong> {{ result.recommendation }}
            </p>
            
            <img src="{{ url_for('uploaded_file', filename=result.filename) }}" 
                 class="leaf-image" alt="Analyzed Leaf">
            
            {% if result.disease != 'Healthy Leaf' %}
            <button class="treatment-toggle" onclick="toggleTreatment()">
                {% if not show_treatment %} Show Treatment{% else %} Hide Treatment{% endif %}
            </button>
            {% endif %}
        </div>
        {% if treatment_list and show_treatment %}
        <div class="result-card treatment-card">
            <h3 class="card-title treatment-title">
                <i class="fas fa-prescription-bottle-alt"></i> Treatment Recommender
            </h3>
            <div class="treatment-list">
                {% for treatment in treatment_list %}
                <div class="treatment-item">
                    <i class="fas fa-check-circle" style="color:#4CAF50; margin-right:10px;"></i>
                    {{ treatment }}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
    {% endif %}
</div>

<script>
let treatmentVisible = {{ show_treatment|tojson|safe }};

function toggleTreatment() {
    if (treatmentVisible) {
        window.location.href = '/upload';
    } else {
        window.location.href = '/upload?show_treatment=true';
    }
}
const fileInput = document.getElementById('fileInput');
const fileLabel = document.getElementById('fileLabel');
const fileName = document.getElementById('fileName');

fileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        fileName.textContent = this.files[0].name;
    }
});
fileLabel.addEventListener('dragover', e => {
    e.preventDefault();
    fileLabel.classList.add('dragover');
});
fileLabel.addEventListener('dragleave', () => {
    fileLabel.classList.remove('dragover');
});
fileLabel.addEventListener('drop', e => {
    e.preventDefault();
    fileLabel.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        fileName.textContent = files[0].name;
    }
});
let stream = null;
let isCameraActive = false;

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480, facingMode: 'environment' } 
        });
        
        const video = document.getElementById('videoElement');
        video.srcObject = stream;
        video.style.display = 'block';
        
        document.querySelector('.camera-placeholder').style.display = 'none';
        document.querySelector('.start-camera').style.display = 'none';
        document.querySelector('.capture-photo').style.display = 'inline-block';
        document.querySelector('.stop-camera').style.display = 'inline-block';
        
        isCameraActive = true;
    } catch (err) {
        alert('Camera access denied or not available');
        console.error('Camera error:', err);
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    
    document.getElementById('videoElement').style.display = 'none';
    document.querySelector('.camera-placeholder').style.display = 'flex';
    document.querySelector('.start-camera').style.display = 'inline-block';
    document.querySelector('.capture-photo').style.display = 'none';
    document.querySelector('.stop-camera').style.display = 'none';
    
    isCameraActive = false;
}

function capturePhoto() {
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('photoCanvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
        const file = new File([blob], 'captured_leaf.jpg', { type: 'image/jpeg' });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        
        const fileInput = document.getElementById('fileInput');
        fileInput.files = dataTransfer.files;
        
        // Auto-submit form
        document.getElementById('uploadForm').submit();
    }, 'image/jpeg', 0.9);
}
</script>
</body>
</html>""",texts=texts, result=result, treatment_list=treatment_list, show_treatment=show_treatment)

@app.route("/map")
def map_page():
    lang_code = session.get('lang','en')
    texts = lang_texts.get(lang_code, lang_texts['en'])
    
    # Localize shop data
    localized_shops = []
    for shop in nearby_shops:
        localized_shops.append({
            'id': shop['id'],
            'name': shop['name'].get(lang_code, shop['name']['en']),
            'lat': shop['lat'],
            'lng': shop['lng'],
            'address': shop['address'].get(lang_code, shop['address']['en']),
            'price_range': shop['price_range'].get(lang_code, shop['price_range']['en']),
            'products': shop['products'].get(lang_code, shop['products']['en'])
        })
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>{{ texts['map_title'] }}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
body { 
    font-family: 'Segoe UI', sans-serif; 
    background: linear-gradient(135deg, #FFF8E1 0%, #E8F5E8 100%);
    margin: 0; 
    padding: 20px;
    min-height: 100vh;
}
.main-container {max-width:1200px; margin:0 auto;}
h1 { 
    color:#2196F3; 
    font-size:2.8em; 
    text-align:center; 
    margin-bottom:20px;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.1);
}
.action-buttons {text-align:center; margin-bottom:40px;}
button { 
    padding:18px 35px; 
    font-size:18px; 
    border:none; 
    border-radius:25px; 
    background:linear-gradient(45deg, #F57C00, #E68900); 
    color:white; 
    cursor:pointer; 
    margin:10px;
    box-shadow:0 8px 25px rgba(0,0,0,0.2);
    font-weight:600;
    transition:all 0.3s ease;
}
button:hover {transform:translateY(-3px); box-shadow:0 12px 35px rgba(0,0,0,0.3);}

.shop-list { 
    display:grid; 
    grid-template-columns:repeat(auto-fit, minmax(320px,1fr)); 
    gap:25px; 
    margin-bottom:40px;
}
.shop-card { 
    background:white; 
    padding:30px; 
    border-radius:25px; 
    box-shadow:0 15px 40px rgba(0,0,0,0.1); 
    cursor:pointer; 
    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
    border:3px solid transparent;
    position:relative;
    overflow:hidden;
}
.shop-card::before {
    content:''; 
    position:absolute; 
    top:0; 
    left:0; 
    right:0; 
    height:4px; 
    background:linear-gradient(90deg, #2196F3, #4CAF50);
}
.shop-card:hover { 
    transform:translateY(-12px) scale(1.02); 
    box-shadow:0 25px 60px rgba(33,150,243,0.3);
    border-color:#2196F3;
}
.shop-card.selected {
    border-color:#4CAF50 !important;
    box-shadow:0 20px 50px rgba(76,175,80,0.4) !important;
    transform:translateY(-8px) scale(1.01);
}
.shop-icon {font-size:4em; margin-bottom:15px; color:#2196F3;}
.shop-name {font-size:2em; color:#2E7D32; margin-bottom:15px; font-weight:700;}
.shop-details {color:#666; line-height:1.6;}
.shop-details strong {color:#333;}
.distance-badge {
    position:absolute; 
    top:15px; 
    right:15px; 
    background:#4CAF50; 
    color:white; 
    padding:8px 15px; 
    border-radius:20px; 
    font-weight:600; 
    font-size:0.9em;
}

#map-container {
    display:none; 
    background:white; 
    border-radius:25px; 
    box-shadow:0 20px 60px rgba(0,0,0,0.2); 
    padding:30px; 
    margin-top:30px;
}
#map { 
    height:550px !important; 
    width:100%; 
    border:4px solid #2196F3; 
    border-radius:20px; 
    margin-bottom:25px;
}
.directions-panel {
    background:#f8f9fa; 
    padding:25px; 
    border-radius:20px; 
    border-left:5px solid #4CAF50;
}
.directions-title {color:#2E7D32; font-size:1.5em; margin-bottom:15px;}
.distance-info {font-size:1.2em; color:#2196F3; margin:10px 0;}
.open-maps-btn {
    width:100%; 
    padding:15px; 
    background:linear-gradient(45deg, #4CAF50, #45a049) !important; 
    font-size:18px; 
    font-weight:600;
}

.close-map {
    position:absolute; 
    top:20px; 
    right:20px; 
    background:#f44336; 
    color:white; 
    border:none; 
    width:50px; 
    height:50px; 
    border-radius:50%; 
    font-size:1.2em; 
    cursor:pointer; 
    box-shadow:0 5px 15px rgba(244,67,54,0.4);
}

@media (max-width:768px) {
    .shop-list {grid-template-columns:1fr;}
    button {width:100%; margin:8px 0;}
}
</style>
</head>
<body>
<div class="main-container">
    <h1><i class="fas fa-store"></i> 🏪 {{ texts['map_title'] }}</h1>
    
    <div class="action-buttons">
        <!-- CORRECT (Multi-language) -->
    <button onclick="location.href='/upload'">upload the image</button>
    <button onclick="location.href='/plants'">Plants</button>
    <button onclick="location.href='/camera'">Camera</button>
    <button onclick="location.href='/analyze'">Analyse</button>
    </div>
    
    <!-- SHOPS LIST - ALWAYS VISIBLE -->
    <div class="shop-list" id="shopList">
        {% for shop in localized_shops %}
        <div class="shop-card" onclick="showShopMap({{ shop.lat }}, {{ shop.lng }}, '{{ shop.name.replace("'", "\\'") }}', {{ shop.id }})">
            <div class="distance-badge">~3-5km</div>
            <div class="shop-icon">🏪</div>
            <h3 class="shop-name">{{ shop.name }}</h3>
            <div class="shop-details">
                <strong>📍 {{ shop.address }}</strong><br><br>
                <strong>💰 {{ shop.price_range }}</strong><br>
                <strong>🛒 {{ shop.products }}</strong>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- MAP - HIDDEN UNTIL SHOP CLICKED -->
    <div id="map-container">
        <button class="close-map" onclick="closeMap()">
            <i class="fas fa-times"></i>
        </button>
        <div id="map"></div>
        <div class="directions-panel">
            <h3 class="directions-title" id="directionsTitle">Directions Loading...</h3>
            <div class="distance-info">
                <strong id="distanceInfo">Distance: Calculating...</strong><br>
                <strong id="timeInfo">Time: Calculating...</strong>
            </div>
            <p><strong>Instructions:</strong></p>
            <ol id="directionsSteps" style="text-align:left; color:#333;">
                <li>Click "Open Google Maps" for turn-by-turn navigation</li>
            </ol>
            <button class="open-maps-btn" id="googleMapsBtn" onclick="openGoogleMaps()">
                🚗 Open in Google Maps
            </button>
        </div>
    </div>
</div>

<script>
let map, userMarker, shopMarker, directionsControl;
const userLat = 12.9716;  // Bengaluru center
const userLng = 77.5946;
let selectedShop = null;

function showShopMap(shopLat, shopLng, shopName, shopId) {
    document.querySelectorAll('.shop-card').forEach(card => card.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
    
    document.getElementById('map-container').style.display = 'block';
    document.getElementById('shopList').style.opacity = '0.5';
    
    selectedShop = {lat: shopLat, lng: shopLng, name: shopName};
    document.getElementById('directionsTitle').textContent = `📱 Directions to ${shopName}`;
    document.getElementById('distanceInfo').textContent = 'Distance: ~3-5 km';
    document.getElementById('timeInfo').textContent = 'Time: 10-15 mins';
    
    setTimeout(() => {
        initMap(shopLat, shopLng, shopName);
        window.scrollTo({top: document.getElementById('map-container').offsetTop - 20, behavior: 'smooth'});
    }, 300);
}

function closeMap() {
    document.getElementById('map-container').style.display = 'none';
    document.getElementById('shopList').style.opacity = '1';
    document.querySelectorAll('.shop-card').forEach(card => card.classList.remove('selected'));
    
    if (map) {
        map.remove();
        map = null;
    }
}

function initMap(shopLat, shopLng, shopName) {
    map = L.map('map').setView([(userLat + shopLat)/2, (userLng + shopLng)/2], 14);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    userMarker = L.marker([userLat, userLng]).addTo(map)
        .bindPopup('🟢 You are here').openPopup();
    
    shopMarker = L.marker([shopLat, shopLng]).addTo(map)
        .bindPopup(`🏪 ${shopName}`).openPopup();
    
    const route = [[userLat, userLng], [shopLat, shopLng]];
    L.polyline(route, {
        color: '#f44336', 
        weight: 8, 
        opacity: 0.8,
        dashArray: '15 10'
    }).addTo(map);
    
    map.fitBounds([
        [userLat, userLng],
        [shopLat, shopLng]
    ]);
}

function openGoogleMaps() {
    if (selectedShop) {
        const url = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${selectedShop.lat},${selectedShop.lng}&travelmode=driving`;
        window.open(url, '_blank');
    }
}
</script>
</body>
</html>""", texts=texts, localized_shops=localized_shops)


@app.route("/plants")
def plants():
    lang_code = session.get('lang','en')
    texts = lang_texts.get(lang_code, lang_texts['en'])
    
    localized_plants = []
    for plant in plants_info:
        localized_plants.append({
            'id': plant['id'],
            'name': get_plant_text(plant, 'name', lang_code),
            'image': plant['image']
        })
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>{{ texts['plants_title'] }}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
body {font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #E8F6EF 0%, #D0F4F0 100%); margin:0; padding:20px;}
.container {max-width:1400px; margin:0 auto;}
h1 {color:#2E7D32; font-size:3em; text-align:center; margin:30px 0; text-shadow:0 2px 10px rgba(0,0,0,0.1);}
.action-buttons {text-align:center; margin:30px 0;}
button {padding:15px 30px; margin:10px; font-size:18px; border:none; border-radius:25px; cursor:pointer; box-shadow:0 8px 25px rgba(0,0,0,0.2);}
.primary {background:linear-gradient(45deg, #F57C00, #E68900); color:white;}
.plant-grid {display:grid; grid-template-columns:repeat(auto-fill, minmax(320px,1fr)); gap:30px; margin:40px 0;}
.plant-card {background:white; border-radius:25px; overflow:hidden; box-shadow:0 20px 40px rgba(0,0,0,0.1); transition:all 0.4s ease; cursor:pointer;}
.plant-card:hover {transform:translateY(-15px) scale(1.02); box-shadow:0 30px 60px rgba(0,0,0,0.2);}
.plant-image {width:100%; height:250px; object-fit:cover;}
.plant-info {padding:25px; text-align:center;}
.plant-name {font-size:1.8em; color:#2E7D32; margin-bottom:10px; font-weight:600;}
.icon {color:#F57C00; margin-right:10px;}
</style>
</head>
<body>
<div class="container">
    <h1><i class="fas fa-seedling"></i> {{ texts['plants_title'] }}</h1>
    
    <div class="action-buttons">
        <button class="primary" onclick="location.href='/upload'">{{ texts['plants_btn'] }}</button>
        <button class="primary" onclick="location.href='/map'">🗺️ {{ texts['map_btn'] }}</button>
        <button class="primary" onclick="location.href='/weather'">🌤️ Weather</button>
    </div>
    
    <div class="plant-grid">
        {% for plant in localized_plants %}
        <div class="plant-card" onclick="location.href='/plant/{{ plant.id }}'">
            <img src="{{ url_for('static', filename=plant.image) }}" alt="{{ plant.name }}" class="plant-image">
            <div class="plant-info">
                <h3 class="plant-name"><i class="fas fa-leaf icon"></i>{{ plant.name }}</h3>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
</style>
</body>
</html>""", texts=texts, localized_plants=localized_plants)

@app.route("/plant/<plant_id>")
def plant_detail(plant_id):
    lang_code = session.get('lang','en')
    texts = lang_texts.get(lang_code, lang_texts['en'])
    
    plant = next((p for p in plants_info if p['id'] == plant_id), None)
    if not plant:
        return "Plant not found", 404
    
    localized_plant = {}
    for key in plant:
        if key != 'id' and isinstance(plant[key], dict):
            localized_plant[key] = plant[key].get(lang_code, plant[key].get('en', ''))
        else:
            localized_plant[key] = plant[key]
    
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>{{ localized_plant.name }} - PlantCare</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
body {font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #FFF8E1 0%, #E8F5E8 100%); margin:0; padding:20px;}
.container {max-width:1200px; margin:0 auto;}
.header {text-align:center; margin:40px 0;}
.plant-name {font-size:3em; color:#2E7D32; margin-bottom:10px;}
.breadcrumb {color:#666; font-size:1.1em;}
.main-content {display:grid; grid-template-columns:1fr 1fr; gap:40px; margin:40px 0;}
.info-section, .video-section {background:white; padding:30px; border-radius:25px; box-shadow:0 15px 35px rgba(0,0,0,0.1);}
.info-grid {display:grid; gap:20px;}
.info-item {display:flex; align-items:center; padding:15px; background:#f8f9fa; border-radius:15px;}
.info-icon {font-size:2em; margin-right:20px; width:60px;}
.info-label {font-weight:600; color:#2E7D32; font-size:1.1em;}
.info-value {color:#333; margin-left:auto;}
.video-container {position:relative; width:100%; height:0; padding-bottom:56.25%; border-radius:15px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.2);}
.video-container iframe {position:absolute; top:0; left:0; width:100%; height:100%;}
.action-buttons {text-align:center; margin:40px 0;}
button {padding:15px 30px; margin:10px; font-size:18px; border:none; border-radius:25px; cursor:pointer; box-shadow:0 8px 25px rgba(0,0,0,0.2);}
.back-btn {background:linear-gradient(45deg, #2196F3, #1976D2); color:white;}
@media (max-width:768px) {.main-content {grid-template-columns:1fr;}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <a href="/plants" class="breadcrumb">
            <i class="fas fa-arrow-left"></i> {{ texts['plants_title'] }}
        </a>
        <h1 class="plant-name">{{ localized_plant.name }}</h1>
    </div>
    
    <div class="main-content">
        <div class="info-section">
            <h2 style="color:#2E7D32; margin-bottom:25px;"><i class="fas fa-info-circle"></i> Growing Guide</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-icon" style="color:#8B4513;">🌱</div>
                    <span class="info-label">Soil:</span>
                    <span class="info-value">{{ localized_plant.soil }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#FFA500;">☀️</div>
                    <span class="info-label">Sunlight:</span>
                    <span class="info-value">{{ localized_plant.sunlight }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#1E90FF;">💧</div>
                    <span class="info-label">Watering:</span>
                    <span class="info-value">{{ localized_plant.water }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#FF1493;">🌡️</div>
                    <span class="info-label">Temperature:</span>
                    <span class="info-value">{{ localized_plant.temperature }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#9370DB;">🧪</div>
                    <span class="info-label">Soil pH:</span>
                    <span class="info-value">{{ localized_plant.ph }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#32CD32;">🌾</div>
                    <span class="info-label">Fertilizer:</span>
                    <span class="info-value">{{ localized_plant.fertilizer }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#FF4500;">📏</div>
                    <span class="info-label">Spacing:</span>
                    <span class="info-value">{{ localized_plant.spacing }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#FFD700;">⏳</div>
                    <span class="info-label">Harvest:</span>
                    <span class="info-value">{{ localized_plant.harvest }}</span>
                </div>
                <div class="info-item">
                    <div class="info-icon" style="color:#DC143C;">🐛</div>
                    <span class="info-label">Pests:</span>
                    <span class="info-value">{{ localized_plant.pests }}</span>
                </div>
            </div>
        </div>
        
        <div class="video-section">
            <h2 style="color:#2E7D32; margin-bottom:25px;"><i class="fas fa-video"></i> 📺 Farming Video Guide</h2>
            <div class="video-container">
                <iframe src="{{ localized_plant.videos }}" 
                        frameborder="0" 
                        allowfullscreen>
                </iframe>
            </div>
            <p style="margin-top:20px; color:#666; font-style:italic;">
                👨‍🌾 Watch this video to learn perfect farming techniques for {{ localized_plant.name }}
            </p>
        </div>
    </div>
    
    <div class="action-buttons">
        <button class="back-btn" onclick="location.href='/plants'">
            <i class="fas fa-arrow-left"></i> Back to Plants
        </button>
        <button class="primary" onclick="location.href='/upload'">
            🌿 Analyze Leaf
        </button>
    </div>
</div>
</body>
</html>""", texts=texts, localized_plant=localized_plant)

def get_plant_text(plant, key, lang):
    if key in plant and isinstance(plant[key], dict):
        return plant[key].get(lang, plant[key].get('en', ''))
    return plant.get(key, '')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def get_current_lang():
    if not session.get('lang'): 
        session['lang'] = 'en'
    return session.get('lang', 'en')


if __name__ == "__main__":
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="0.0.0.0",port=5000,debug=True)
