
from flask import Flask, render_template_string, request, jsonify
import re
FARMING_RESPONSES = {
    'en': {
        'tomato': "Tomato disease? Early Blight (brown spots). Spray Copper Oxychloride 2.5g/liter every 10 days.",
        'blight': "Early Blight: Remove infected leaves + Copper spray 2.5g/liter.",
        'fertilizer': "Best NPK for vegetables: 10-10-10. Apply 20g/plant monthly.",
        'weather': "Bengaluru: 28°C, 82% humidity (High fungal risk).",
        'shop': "3 agri shops within 5km.",
        'healthy': "Healthy leaf! Good farming practices.",
        'rose': "Rose: 6-12-36 NPK monthly + full sunlight.",
        'helpline': "CropCare Helpline: +919876543210 (WhatsApp/Call)",
        'default': "Upload leaf photo on /upload for AI disease detection!"
    }
}

def register_chatbot_routes(app):
    """Register chatbot routes"""
    
    @app.route("/chatbot")
    def chatbot():
        return render_template_string(CHATBOT_HTML)
    
    @app.route("/api/chatbot/query", methods=['POST'])
    def chatbot_query():
        print("CHATBOT: Request received!")  
        
        try:
            data = request.get_json()
            print(f"CHATBOT: Data received: {data}")  
            if not data:
                return jsonify({'response': 'No data received!'})
                
            query = data.get('query', '').lower()
            print(f"CHATBOT: Query: '{query}'")  
            responses = FARMING_RESPONSES['en']
            response = responses['default']
            
            for key, value in responses.items():
                if key in query:
                    response = value
                    print(f" CHATBOT: Matched '{key}' -> '{value[:50]}...'") 
                    break
            
            print(f" CHATBOT: Sending response: '{response[:50]}...'")  
            return jsonify({'response': response})
            
        except Exception as e:
            print(f"CHATBOT ERROR: {e}") 
            return jsonify({'response': f'Error: {str(e)}'})

    print("Chatbot routes registered!")
CHATBOT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PlantCare Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:'Segoe UI',sans-serif;background:#E8F5E8;height:100vh;overflow:hidden;}
        .chat-container{height:100vh;display:flex;flex-direction:column;max-width:800px;margin:0 auto;background:white;box-shadow:0 10px 50px rgba(0,0,0,0.1);}
        .chat-header{background:#4CAF50;color:white;padding:20px;text-align:center;}
        .chat-header h1{font-size:1.8em;margin:0;}
        .chat-messages{flex:1;padding:20px;overflow-y:auto;background:#f8fff8;}
        .message{margin:15px 0;padding:15px 20px;border-radius:20px;max-width:70%;}
        .user-message{background:#4CAF50;color:white;margin-left:auto;}
        .bot-message{background:white;border:1px solid #C8E6C9;margin-right:auto;}
        .chat-input{padding:20px;background:white;border-top:1px solid #E8F5E8;}
        .input-group{display:flex;gap:10px;align-items:center;}
        #messageInput{flex:1;padding:15px;border:2px solid #E8F5E8;border-radius:25px;font-size:16px;}
        #messageInput:focus{outline:none;border-color:#4CAF50;}
        .send-btn{width:50px;height:50px;border:none;background:#4CAF50;color:white;border-radius:50%;cursor:pointer;}
        .send-btn:hover{background:#45a049;}
        .suggestions{display:flex;flex-wrap:wrap;gap:10px;margin-top:15px;}
        .suggestion-btn{padding:10px 15px;background:#E8F5E8;border:1px solid #C8E6C9;border-radius:20px;cursor:pointer;font-size:14px;}
        .suggestion-btn:hover{background:#4CAF50;color:white;}
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1><i class="fas fa-robot"></i> PlantCare Assistant</h1>
            <p>Ask about crop diseases, treatments & farming!</p>
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                <strong>Hello!</strong> I help with crop diseases & farming tips.<br><br>
                <div class="suggestions">
                    <button class="suggestion-btn" onclick="sendMsg('tomato disease?')">Tomato disease</button>
                    <button class="suggestion-btn" onclick="sendMsg('blight')">Blight treatment</button>
                    <button class="suggestion-btn" onclick="sendMsg('fertilizer')">Fertilizer</button>
                    <button class="suggestion-btn" onclick="sendMsg('helpline')">Helpline</button>
                </div>
            </div>
        </div>
        
        <div class="chat-input">
            <div class="input-group">
                <input type="text" id="messageInput" placeholder="Type your question..." onkeypress="if(event.keyCode==13) sendMsg()">
                <button class="send-btn" onclick="sendMsg()" title="Send"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    </div>

    <script>
    function sendMsg() {
        const input = document.getElementById('messageInput');
        const msg = input.value.trim();
        if (!msg) return;
        
        console.log('Sending:', msg);  
        addMessage(msg, 'user');
        input.value = '';
        const typingDiv = addMessage('Typing...', 'bot');
        fetch('/api/chatbot/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: msg})
        })
        .then(response => {
            console.log('Response status:', response.status);  
            if (!response.ok) throw new Error('Network response not ok');
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data); 
            document.getElementById('messages').removeChild(typingDiv);
            addMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error('Error:', error); 
            document.getElementById('messages').removeChild(typingDiv);
            addMessage('Sorry, something went wrong! Try again.', 'bot');
        });
    }
    
    function addMessage(text, type) {
        const messages = document.getElementById('messages');
        const div = document.createElement('div');
        div.className = `message ${type}-message`;
        
        if (type === 'bot') {
            div.innerHTML = `<strong> PlantCare:</strong> ${text}`;
        } else {
            div.innerHTML = `<strong> You:</strong> ${text}`;
        }
        
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }
    </script>
</body>
</html>
'''

def init_chatbot(app):
    """Call from detector.py"""
    register_chatbot_routes(app)
    print(" Chatbot ready at /chatbot")
