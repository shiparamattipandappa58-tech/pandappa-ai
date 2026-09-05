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
    "You are Pandappa AI, an intelligent personal assistant. "
    "If the user asks in Kannada or Kannada script, reply in clear, accurate Kannada. "
    "If asked in English, reply in clear English. "
    "Provide fast, helpful, and concise responses."
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

    if not prompt and not image_data:
        return jsonify({'error': 'No input provided'}), 400

    full_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}\nPandappa AI:"
    model_to_use = VISION_MODEL if image_data else TEXT_MODEL

    payload = {
        "model": model_to_use,
        "prompt": full_prompt,
        "stream": True
    }

    if image_data and ',' in image_data:
        payload["images"] = [image_data.split(',', 1)[1]]

    def generate():
        try:
            res = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60)
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
