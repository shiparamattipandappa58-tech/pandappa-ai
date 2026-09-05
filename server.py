from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import base64
import os
import uuid

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for seamless browser interaction

# Serve the main HTML dashboard at the root URL
@app.route('/')
def home():
    if os.path.exists('index.html'):
        return send_file('index.html')
    return "<h1>404 - index.html file not found in repository!</h1>", 404

# Main Multimodal Chat & Vision Processing Endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    prompt = data.get('prompt', '').strip()
    image_data = data.get('image', None)

    if not prompt:
        return jsonify({'response': 'ದಯವಿಟ್ಟು ಏನನ್ನಾದರೂ ಕೇಳಿ (Please ask something).'}), 400

    system_prompt = (
        "You are Pandappa AI, a highly smart, local, privacy-first offline AI assistant. "
        "Answer the user query concisely and accurately in Kannada or English."
    )
    
    temp_image_path = None

    try:
        # Process image input if provided from live camera capture
        if image_data and ',' in image_data:
            try:
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
                
                # Generate a unique temp image filename to avoid race conditions
                temp_filename = f"temp_{uuid.uuid4().hex[:8]}.jpg"
                temp_image_path = os.path.join(os.getcwd(), temp_filename)
                
                with open(temp_image_path, "wb") as f:
                    f.write(image_bytes)
                
                # Command for vision model execution
                cmd = f'ollama run moondream "{system_prompt} Question: {prompt}" "{temp_image_path}"'
            except Exception as img_err:
                return jsonify({'response': f'Image Processing Error: {str(img_err)}'}), 400
        else:
            # Command for text-only execution
            cmd = f'ollama run moondream "{system_prompt} User asks: {prompt}"'

        # Execute Ollama CLI command
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Clean up temporary image file if created
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except Exception:
                pass

        if process.returncode == 0:
            response_text = process.stdout.strip()
            if not response_text:
                response_text = "ಕ್ಷಮಿಸಿ, ಯಾವುದೇ ಉತ್ತರ ದೊರೆಯಲಿಲ್ಲ."
            return jsonify({'response': response_text})
        else:
            error_msg = process.stderr.strip() or "Ollama execution failed."
            return jsonify({'response': f'Ollama Error: {error_msg}'}), 500

    except Exception as e:
        # Final safety cleanup
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
            except Exception:
                pass
        return jsonify({'response': f'Server Error: {str(e)}'}), 500

if __name__ == '__main__':
    # Run server on all interfaces at port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
