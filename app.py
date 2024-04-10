from flask import Flask, render_template, request, send_file, jsonify
import requests
import os

app = Flask(__name__)
api_key = os.environ.get("OPENAI_API_KEY")

def optimize_text(input_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Du bist ein hilfreicher Bot, der lediglich Texte umwandelt. Die Textabschnitte kommen aus einem Vorlesungsskript oder einer Präsentation bei dem sachliche Informationen in einer kompakten Form präsentiert werden. Wandle den Text so um, dass er einem fließenden und erzählenden Stil nahe kommt, der für Vorträge geeignet ist. Füge, wenn nötig, zusätzliche Informationen hinzu, um den Kontext zu verdeutlichen und die Inhalte greifbarer zu machen. Keine Einleitung. Strukturiere den Text logisch und halte dich an die Struktur, des vorgegebenen Textes, der folgt."},
            {"role": "user", "content": input_text}
        ],
        "temperature": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    response = requests.post(url, headers=headers, json=data)
    output = response.json()["choices"][0]["message"]["content"]
    return output

def generate_text_to_speech(text):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "curl"
    }
    data = {
        'model': 'tts-1',
        'input': text,
        'voice': 'alloy'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        with open("static/tts_audio.mp3", "wb") as file:
            file.write(response.content)
        return True
    else:
        print("Error:", response.status_code)
        return False

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        input_text = request.json.get('inputText1')
        
        # Optimize input text
        optimized_text = optimize_text(input_text)

        return jsonify({'optimized_text': optimized_text}), 200
    
    return render_template('index.html')

@app.route('/synthesizeAudio', methods=['POST'])
def synthesize_audio():
    data = request.json

    if 'text' in data:
        text = data['text']

        # Generate text-to-speech audio
        success = generate_text_to_speech(text)

        if success:
            return jsonify({'message': 'Audio synthesized successfully.'}), 200
        else:
            return jsonify({'error': 'Failed to synthesize audio.'}), 500
    else:
        return jsonify({'error': 'Text parameter is missing.'}), 400


@app.route('/download_audio', methods=['GET'])
def download_audio():
    file_path = 'static/tts_audio.mp3'
    return send_file(file_path, as_attachment=True)

@app.errorhandler(405)
def method_not_allowed(e):
    return "Method Not Allowed - Invalid HTTP method for this endpoint", 405


if __name__ == '__main__':
    app.run(debug=True)
