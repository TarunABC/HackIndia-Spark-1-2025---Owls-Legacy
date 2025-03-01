from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
import os
import time
import random
from PIL import Image, ImageDraw, ImageFont
import uuid
import gtts
import pyttsx3  # Import pyttsx3 for text-to-speech
from ollama import chat_with_ollama  # Import the chat_with_ollama function

app = Flask(__name__)

# Create necessary directories
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

# Simple in-memory database for chat history
chat_history = []

# Initialize pyttsx3 engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Set speech rate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    is_image_mode = data.get('isImageMode', False)
    is_audio_mode = data.get('isAudioMode', False)
    use_pyttsx3 = data.get('usePyttsx3', False)  # New flag for pyttsx3 TTS

    # Generate response using Ollama
    response_text = generate_response(message)

    # Generate image if requested
    image_url = None
    if is_image_mode:
        image_url = generate_image(message)

    # Generate audio if requested
    audio_url = None
    if is_audio_mode:
        if use_pyttsx3:
            # Use pyttsx3 for TTS
            speak_with_pyttsx3(response_text)
        else:
            # Use gTTS for TTS
            audio_url = text_to_speech(response_text)

    # Store in chat history
    chat_history.append({
        'user_message': message,
        'bot_response': response_text,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'image_url': image_url,
        'audio_url': audio_url,
    })

    return jsonify({
        'text': response_text,
        'image_url': image_url,
        'audio_url': audio_url,
    })

@app.route('/api/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    use_pyttsx3 = data.get('usePyttsx3', False)  # New flag for pyttsx3 TTS

    if use_pyttsx3:
        # Use pyttsx3 for TTS
        speak_with_pyttsx3(text)
        return jsonify({'status': 'success', 'message': 'Speech generated using pyttsx3'})
    else:
        # Use gTTS for TTS
        audio_url = text_to_speech(text)
        return jsonify({'audio_url': audio_url})

def generate_response(message):
    """Generate response using Ollama"""
    history = [f"You: {message}"]
    response = chat_with_ollama(history)
    return response

def generate_image(prompt):
    """Generate an image based on the prompt"""
    width, height = 512, 512
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    draw.text((10, 10), prompt, fill=(255, 255, 255), font=font)
    filename = f"image_{uuid.uuid4()}.png"
    filepath = os.path.join('static', 'images', filename)
    image.save(filepath)
    return url_for('serve_static', filename=f'images/{filename}')

def text_to_speech(text):
    """Convert text to speech using gTTS"""
    filename = f"speech_{uuid.uuid4()}.mp3"
    filepath = os.path.join('static', 'audio', filename)
    tts = gtts.gTTS(text=text, lang='en', slow=False)
    tts.save(filepath)
    return url_for('serve_static', filename=f'audio/{filename}')

def speak_with_pyttsx3(text):
    """Convert text to speech using pyttsx3"""
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)