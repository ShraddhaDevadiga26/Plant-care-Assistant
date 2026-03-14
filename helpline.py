from flask import render_template_string, request

HELPLINE_CONFIG = {
    'phone': '+918123893856',
    'whatsapp': '+918123893856', 
    'email': 'shraddhadevadiga26@gmail.com',
    'name': 'CropCare Helpline'
}

def register_helpline_routes(app):
    """Register helpline routes - call from main.py"""
    
    @app.route("/helpline")
    def helpline_page():
        return render_template_string(HELPLINE_HTML, helpline=HELPLINE_CONFIG)
    
    @app.route("/api/helpline/call", methods=['POST'])
    def helpline_call():
        data = request.json
        print(f"HELPLINE CALL REQUEST: {data}")
        return {"success": True, "message": "Call initiated!"}
    
    print("Helpline ready at /helpline")
    
HELPLINE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>CropCare Helpline</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:'Poppins',sans-serif;background:linear-gradient(135deg,#ff6b6b,#ff8e8e);min-height:100vh;}
        .container{max-width:600px;margin:0 auto;padding:40px;text-align:center;color:white;}
        .hero-icon{font-size:8rem;margin-bottom:20px;animation:pulse 2s infinite;}
        @keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.1);}}
        h1{font-size:2.5rem;margin-bottom:20px;font-weight:700;}
        .phone-display{font-size:2rem;background:rgba(255,255,255,0.2);padding:20px;border-radius:20px;margin:30px 0;font-weight:600;}
        .helpline-buttons{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;}
        .helpline-btn{padding:20px 30px;border-radius:50px;text-decoration:none;font-weight:700;font-size:1.2rem;transition:all 0.3s;min-width:180px;display:flex;align-items:center;gap:15px;justify-content:center;}
        .call-btn{background:rgba(255,255,255,0.95);color:#ff6b6b;}
        .whatsapp-btn{background:#25D366;color:white;}
        .email-btn{background:#1e90ff;color:white;}
        .helpline-btn:hover{transform:translateY(-5px) scale(1.05);box-shadow:0 15px 35px rgba(0,0,0,0.3);}
        .back-btn{background:rgba(255,255,255,0.2);color:white;border:2px solid rgba(255,255,255,0.5);padding:15px 30px;border-radius:30px;text-decoration:none;font-weight:600;margin-top:30px;display:inline-block;}
        @media(max-width:768px){.helpline-buttons{flex-direction:column;}.helpline-btn{width:100%;max-width:350px;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero-icon">
            <i class="fas fa-headset"></i>
        </div>
        <h1>{{ helpline.name }}</h1>
        <div class="phone-display">{{ helpline.phone }}</div>
        <p><strong>24/7 Expert Support</strong><br>Disease diagnosis • Treatment plans • Fertilizer advice</p>
        
        <div class="helpline-buttons">
            <a href="tel:{{ helpline.phone }}" class="helpline-btn call-btn">
                <i class="fas fa-phone"></i> Call Now
            </a>
            <a href="https://wa.me/{{ helpline.whatsapp | replace('+', '') }}?text=Hi%2C%20need%20crop%20help!" class="helpline-btn whatsapp-btn" target="_blank">
                <i class="fab fa-whatsapp"></i> WhatsApp
            </a>
            <a href="mailto:{{ helpline.email }}?subject=Crop%20Help" class="helpline-btn email-btn">
                <i class="fas fa-envelope"></i> Email
            </a>
        </div>
        
        <a href="/" class="back-btn">← Back to Home</a>
    </div>
</body>
</html>
"""

def init_helpline(app):
    """Initialize from main.py"""
    register_helpline_routes(app)
