import os
import json
import requests
from flask import Flask, request, Response, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen:0.5b"

SYSTEM_PROMPT = (
    "You are Pandappa AI, a smart voice and text assistant. "
    "Reply in 1-2 short, direct sentences. "
    "If user speaks in Kannada, respond in Kannada. If in English, respond in English."
)

@app.route('/')
def home():
    if os.path.exists('index.html'):
        return send_file('index.html')
    return "<h1>index.html missing</h1>", 404

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    prompt = data.get('prompt', '').strip()

    if not prompt:
        return jsonify({'response': 'ದಯವಿಟ್ಟು ಏನನ್ನಾದರೂ ಕೇಳಿ.'}), 400

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {prompt}\nPandappa AI:",
        "stream": False,
        "options": {
            "num_predict": 80,
            "temperature": 0.3
        }
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=15)
        if res.status_code == 200:
            bot_response = res.json().get('response', '').strip()
            return jsonify({'response': bot_response})
        else:
            return jsonify({'response': 'Ollama ಸರ್ವರ್‌ನಿಂದ ರಿಸ್ಪಾನ್ಸ್ ಬರಲಿಲ್ಲ.'}), 500
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
