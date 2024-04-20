# from flask import Flask, send_file, request, jsonify
# from gtts import gTTS
# from util import generate_file_name
# import os
# from langdetect import detect
# # import firebase_admin
# # from firebase_admin import credentials, firestore

# # cred = credentials.Certificate("kids-magazine-c41d5-firebase-adminsdk-b44bf-bf2e5aa3d5.json")
# # firebase_admin.initialize_app(cred)
# # db = firestore.client()
# ROOT_AUDIO_PATH = "/Users/shankarnath/Documents/explo/Android-Kid-Magazine-V3-2023/Kid-Magazine-Android_App-master/kids_magazine/assets/audio/"
# app = Flask(__name__)

# @app.route('/')
# def hlo():
#     return "Hello World!"

# @app.route('/generate_speech', methods = ['GET'])
# def generate_speech():
#     d = {}
#     text = str(request.args['text'])
#     language = str(request.args['language'])
#     if not language:
#         language = detect(text)
#     # language = "gu"
#     tts = gTTS(text=text, lang=language)

#     file_id = "temp"
#     output_file = str(ROOT_AUDIO_PATH + file_id + ".wav")
#     tts.save(output_file)

#     d['output'] = file_id
#     return d

# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, request, jsonify
# from gtts import gTTS
# import base64
# import firebase_admin
# from firebase_admin import credentials, firestore
# from langdetect import detect
# from io import BytesIO
# from util import generate_file_name
# cred = credentials.Certificate("kids-magazine-c41d5-firebase-adminsdk-b44bf-bf2e5aa3d5.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# app = Flask(__name__)
# @app.route('/', methods=['POST'])
# def hello():
#     return "hello world"

# @app.route('/generate_speech', methods=['POST'])
# def generate_speech():
#     data = request.json
#     text = data.get('original_text', '')
#     language = data.get('language', '')

#     if not language:
#         language = detect(text)

#     codeLanguage = "en"

#     if language == "Marathi":
#         codeLanguage = "mr"
#     elif language == "Bengali":
#         codeLanguage = "bn"
#     elif language == "Gujarati":
#         codeLanguage = "gu"
#     elif language == "Telugu":
#         codeLanguage = "te"

#     tts = gTTS(text=text, lang=codeLanguage)

#     audio_bytes_io = BytesIO()
#     tts.write_to_fp(audio_bytes_io)
#     audio_bytes_io.seek(0)

#     audio_bytes = audio_bytes_io.read()
#     audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
#     doc_id = str(generate_file_name())
#     # Save data to Firestore
#     db.collection('stories').document(doc_id).set(data)


#     # Save audio to Firestore
#     db.collection('stories').document(doc_id).update({'audio': audio_base64})

#     return jsonify({'message': 'Data and audio saved successfully'})

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, jsonify
from gtts import gTTS
import base64
import firebase_admin
from firebase_admin import credentials, firestore, storage
from langdetect import detect
from io import BytesIO
from util import generate_file_name
import os
# import pyrebase
# from collections.abc import MutableMapping

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

    if not language:
        language = detect(text)

    codeLanguage = "en"
    if language == "Marathi":
        codeLanguage = "mr"
    elif language == "Bengali":
        codeLanguage = "bn"
    elif language == "Gujarati":
        codeLanguage = "gu"
    elif language == "Telugu":
        codeLanguage = "te"

    tts = gTTS(text=text, lang=codeLanguage)

    # Generate a unique file name
    file_name = str(generate_file_name()) + ".mp3"
    temp_audio_path = os.path.join("./audio/", file_name)  # Store temporarily in /tmp directory
    # remote_path = "audio_files/"+file_name
    # Save the audio file temporarily
    tts.save(temp_audio_path)
    file_path = "audio/" + file_name
    # print(file_path)
    # print(temp_audio_path)
    # Read the temporarily saved audio file and encode it as base64
    # with open(temp_audio_path, "rb") as audio_file:
    #     audio_bytes = audio_file.read()
    #     audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

    # Delete the temporary audio file
    download_url = upload_audio(file_path, file_name)

    # Save data to Firestore
    doc_ref = db.collection('stories').add(data)
    doc_id = doc_ref[1].id  # Get the document ID from the returned tuple
    # Save audio to Firestore
    db.collection('stories').document(doc_id).update({'audio': download_url})
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
        # download_url = blob.generate_signed_url(expiration=None)
        download_url = f"{k}"

        print('Download URL:', download_url)
        return download_url
        # Store the download URL in Firestore
        # doc_ref = db.collection('audios').document()
        # doc_ref.set({
        #     'audioURL': download_url,
        #     # Add additional metadata fields if needed
        # })

    except Exception as e:
        print('Error uploading audio:', e)


if __name__ == '__main__':
    app.run(debug=True)
