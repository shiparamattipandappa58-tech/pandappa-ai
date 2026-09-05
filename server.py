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
    file_text = data.get('file_text', None)

    if not prompt and not image_data and not file_text:
        return jsonify({'response': 'ದಯವಿಟ್ಟು ಏನನ್ನಾದರೂ ಕೇಳಿ ಅಥವಾ ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.'}), 400

    temp_image_path = None

    try:
        # File Handling
        if file_text:
            clean_file = file_text[:1500].replace('"', "'").replace('\n', ' ')
            combined_prompt = f"Context: {clean_file} Question: {prompt}"
            cmd = ['ollama', 'run', TEXT_MODEL, combined_prompt]

        # Vision Handling
        elif image_data and ',' in image_data:
            header, encoded = image_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            temp_filename = f"temp_{uuid.uuid4().hex[:8]}.jpg"
            temp_image_path = os.path.join(os.getcwd(), temp_filename)
            
            with open(temp_image_path, "wb") as f:
                f.write(image_bytes)
            
            vision_prompt = prompt if prompt else "Describe this image"
            cmd = ['ollama', 'run', VISION_MODEL, vision_prompt, temp_image_path]

        # 1-Second Ultra Fast Text Response
        else:
            full_prompt = f"Answer briefly in Kannada or English: {prompt}"
            cmd = ['ollama', 'run', TEXT_MODEL, full_prompt]

        # Secure subprocess call without shell=True to avoid command line breakage
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        if process.returncode == 0:
            return jsonify({'response': process.stdout.strip()})
        else:
            return jsonify({'response': 'Ollama ಪ್ರಾಸೆಸ್ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.'}), 500

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
