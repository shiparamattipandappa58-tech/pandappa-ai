from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import base64

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    image_data = data.get('image', None)

    if not prompt:
        return jsonify({'response': 'ದಯವಿಟ್ಟು ಏನನ್ನಾದರೂ ಕೇಳಿ.'})

    system_prompt = "You are Pandappa AI, a smart offline assistant. Respond in Kannada or English."
    
    if image_data:
        image_bytes = base64.b64decode(image_data.split(',')[1])
        with open("temp.jpg", "wb") as f:
            f.write(image_bytes)
        cmd = f'ollama run moondream "{system_prompt} {prompt} temp.jpg"'
    else:
        cmd = f'ollama run moondream "{system_prompt} User asks: {prompt}"'

    try:
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        response = process.stdout.strip()
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
