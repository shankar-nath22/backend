from flask import Flask, request, jsonify
from gtts import gTTS
import base64
import firebase_admin
from firebase_admin import credentials, firestore, storage
from langdetect import detect
from io import BytesIO
from util import generate_file_name
import os

cred = credentials.Certificate("./keys.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'kids-magazine-c41d5.appspot.com'})
db = firestore.client()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return "hello world"

@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    data = request.json
    text = data.get('original_text', '')
    language = data.get('language', '')

    # detectedLangugage = detect(text)
    if not language:
        language = detect(text)
    # if detectedLangugage != language:
    #     language = detectedLangugage
    codeLanguage = language
    if not codeLanguage:
        codeLanguage = "en"
    print(codeLanguage)
    printLang = ""
    if codeLanguage == "mr":
        printLang = "Marathi"
    elif codeLanguage == "bn":
        printLang = "Bengali"
    elif codeLanguage == "gu":
        printLang = "Gujarati"
    elif codeLanguage == "te":
        printLang = "Telugu"
    else:
        printLang = detect(text)

    tts = gTTS(text=text, lang=codeLanguage)

    # Generate a unique file name
    file_name = str(generate_file_name()) + ".mp3"
    temp_audio_path = os.path.join("./audio/", file_name)  # Store temporarily in /tmp directory
    # remote_path = "audio_files/"+file_name
    # Save the audio file temporarily
    tts.save(temp_audio_path)
    file_path = "audio/" + file_name
    
    # Delete the temporary audio file
    download_url = upload_audio(file_path, file_name)

    # Save data to Firestore
    doc_ref = db.collection('stories').add(data)
    doc_id = doc_ref[1].id  # Get the document ID from the returned tuple
    # Save audio to Firestore
    db.collection('stories').document(doc_id).update({'audio': download_url, 'language':printLang})
    os.remove(temp_audio_path)

    return jsonify({'message': 'Data and audio saved successfully'})


def upload_audio(file_path, file_name):
    try:
        
        # Create a reference to the audio file in Firebase Cloud Storage
        bucket = storage.bucket()
        k = "audio_files/" + file_name
        blob = bucket.blob(k)
        # # Upload the audio file to Firebase Cloud Storage
        blob.upload_from_filename(file_path)

        # # Get the download URL for the uploaded audio file
        download_url = f"{k}"

        print('Download URL:', download_url)
        return download_url
       
    except Exception as e:
        print('Error uploading audio:', e)


if __name__ == '__main__':
    app.run(debug=True)
