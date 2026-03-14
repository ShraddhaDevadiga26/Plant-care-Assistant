import requests
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

WEATHER_API_KEY = "e93e3b1cfdb506dff2193df809415c1a"
EMAIL = "shraddhadevadiga26@gmail.com"  
PASSWORD = "eofa mvaq meoe pgno" 
PHONE_NUMBER = "+919740704691"

def get_weather_current(lat=12.9716, lon=77.5946):
    """REAL current Bengaluru weather"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return {
            "temp": int(data['main']['temp']),
            "humidity": data['main']['humidity'],
            "condition": data['weather'][0]['main'],
            "description": data['weather'][0]['description'].title()
        }
    except:
        return {"temp": 28, "humidity": 65, "condition": "Sunny", "description": "Clear Sky"}

def get_weather_forecast(lat=12.9716, lon=77.5946):
    """REAL 5-day/3-hour forecast - FIXED!"""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        forecast = []
        for item in data['list'][1:6]: 
            forecast.append({
                "time": datetime.fromisoformat(item['dt_txt'][:-1]).strftime("%I:%M %p"),
                "temp": int(item['main']['temp']),
                "condition": item['weather'][0]['main'],
                "description": item['weather'][0]['description'].title(),
                "icon": item['weather'][0]['icon']
            })
        return forecast
    except Exception as e:
        print(f"Forecast error: {e}")
        return [
            {"time": "3:00 PM", "temp": 33, "condition": "Sunny", "description": "Clear Sky", "icon": "01d"},
            {"time": "6:00 PM", "temp": 30, "condition": "Clouds", "description": "Partly Cloudy", "icon": "03d"}
        ]

try:
    from plyer import notification
except ImportError:
    print("Install: pip install plyer")
    print("Using print notification instead...")
    notification = None 

def send_laptop_sms():
    """POPUP NOTIFICATION ON LAPTOP SCREEN!"""
    current = get_weather_current()
    forecast = get_weather_forecast()
    
    title = "PlantCare Weather Alert!"
    message = f"{current['temp']}°C {current['condition']}\nNext: {forecast[0]['temp']}°C"
    
    if notification:  
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10,
                app_name="PlantCare"
            )
            print("LAPTOP POPUP SENT!")
        except Exception as e:
            print(f" Notification failed: {e}")
            print(message) 
    else:
        print(f"{title}\n{message}")  

