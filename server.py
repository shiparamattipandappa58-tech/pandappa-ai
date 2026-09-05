import os
import json
import requests
from flask import Flask, request, Response, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
TEXT_MODEL = "qwen:0.5b"
VISION_MODEL = "moondream"

SYSTEM_PROMPT = (
    "You are Pandappa AI, a highly capable mobile assistant. "
    "If the user asks in Kannada, answer in simple, grammatically accurate Kannada. "
    "If asked in English, answer in English. Keep answers short and fast."
)

@app.route('/')
def home():
    if os.path.exists('index.html'):
        return send_file('index.html')
    return "<h1>index.html missing</h1>", 404

@app.route('/stream-chat', methods=['POST'])
def stream_chat():
    data = request.json or {}
    prompt = data.get('prompt', '').strip()
    image_data = data.get('image', None)
    mode = data.get('mode', 'chat')

    if not prompt and not image_data:
        return jsonify({'error': 'No input provided'}), 400

    # Mode Handling (Web Search / Project Simulation)
    if mode == 'search':
        prompt = f"[Web Search Simulated] Provide latest factual info: {prompt}"
    elif mode == 'image_gen':
        prompt = f"Describe a detailed prompt to create an image for: {prompt}"

    model_to_use = VISION_MODEL if image_data else TEXT_MODEL

    payload = {
        "model": model_to_use,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {prompt}\nPandappa AI:",
        "stream": True,
        "options": {
            "num_predict": 120,
            "temperature": 0.3
        }
    }

    if image_data and ',' in image_data:
        payload["images"] = [image_data.split(',', 1)[1]]

    def generate():
        try:
            res = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=30)
            for line in res.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    text_chunk = chunk.get('response', '')
                    if text_chunk:
                        yield f"data: {json.dumps({'chunk': text_chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
