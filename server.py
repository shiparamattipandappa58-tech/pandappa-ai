import os
import base64
import uuid
import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TEXT_MODEL = "qwen:0.5b"
VISION_MODEL = "moondream"

# System instruction for high-quality Kannada & English responses
SYSTEM_PROMPT = (
    "You are Pandappa AI, a smart assistant. "
    "If the user asks in Kannada, reply in simple, clear, and accurate Kannada. "
    "If the user asks in English, reply in English. "
    "Keep answers short, concise, and helpful."
)

@app.route('/')
def home():
    if os.path.exists('index.html'):
        return send_file('index.html')
    return "<h1>index.html missing</h1>", 404

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    prompt = data.get('prompt', '').strip().replace('"', "'").replace('\n', ' ')
    image_data = data.get('image', None)

    if not prompt and not image_data:
        return jsonify({'response': 'ದಯವಿಟ್ಟು ಪ್ರಶ್ನೆ ಕೇಳಿ ಅಥವಾ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.'}), 400

    temp_image_path = None

    try:
        # Vision Request (Image + Question)
        if image_data and ',' in image_data:
            header, encoded = image_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            temp_filename = f"temp_{uuid.uuid4().hex[:8]}.jpg"
            temp_image_path = os.path.join(os.getcwd(), temp_filename)
            
            with open(temp_image_path, "wb") as f:
                f.write(image_bytes)
            
            vision_prompt = f"{prompt if prompt else 'Describe this image in Kannada or English'}"
            cmd = ['ollama', 'run', VISION_MODEL, vision_prompt, temp_image_path]

        # Fast Text Request (Kannada & English Optimization)
        else:
            full_prompt = f"{SYSTEM_PROMPT}\nUser: {prompt}\nPandappa AI:"
            cmd = ['ollama', 'run', TEXT_MODEL, full_prompt]

        process = subprocess.run(cmd, capture_output=True, text=True, timeout=45)

        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        if process.returncode == 0:
            reply = process.stdout.strip()
            return jsonify({'response': reply})
        else:
            return jsonify({'response': 'ಕ್ಷಮಿಸಿ, ಉತ್ತರ ನೀಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ.'}), 500

    except subprocess.TimeoutExpired:
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return jsonify({'response': 'ಸಮಯ ಮುಗಿಯಿತು (Timeout). ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.'}), 504
    except Exception as e:
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
