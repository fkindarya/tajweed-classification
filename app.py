import os
import requests
import base64
import imghdr
import re
from timeit import default_timer as timer
from io import BytesIO
from ArabicOcr import arabicocr
from datetime import datetime
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def ArabicOCR(image):
    results = arabicocr.arabic_ocr(image, image)
    return results

def QuranVerseSound(arabic_text):
    try:
        url = "https://www.alfanous.org/api/search?query=" + arabic_text
        response = requests.get(url)

        data = response.json()
        response.close()
        if data:
            if data['search']['ayas']:
                quran_sound = data['search']['ayas']['1']['aya']['recitation']
            else:
                quran_sound = "Not Found"
        else:
            quran_sound = "Not Found"
        
        return quran_sound
    except requests.exceptions.ConnectionError:
        quran_sound = "Max retires exceeded"
        return quran_sound

def CheckWordAfterNoonSaakin(arrayLength, words):
    for i in range(arrayLength):
        if 'ن' in words[i]:
            for j in range(len(words[i])):
                if words[i][j] == 'ن':
                    index = i, j
                    if index[1] < len(words[i])-1:
                        if words[index[0]][index[1]+1] == ' ':
                            next_word = words[index[0]][index[1]+2]
                        elif words[index[0]][index[1]+1] != ' ':
                            next_word = words[index[0]][index[1]+1]
                            if next_word == 'ا':
                                if words[index[0]][index[1]+2] == ' ':
                                    next_word = words[index[0]][index[1]+3]
                                elif words[index[0]][index[1]+2] != ' ':
                                    next_word = words[index[0]][index[1]+2]
                    else:
                        next_word = 'Word Not Detected'
                    break
        else:
            next_word = 'There Are No Noon Saakin'
    return next_word

def CheckTajweedLaws(next_word):
    if next_word == 'أ' or next_word == 'ء':
        law = "Idhar Halqi"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idhar/alif.mp3")
    elif next_word == 'ح':
        law = "Idhar Halqi"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idhar/kha.mp3")
    elif next_word == 'خ':
        law = "Idhar Halqi"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idhar/kho.mp3")
    elif next_word == 'ع':
        law = "Idhar Halqi"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idhar/ain.mp3")
    elif next_word == 'غ':
        law = "Idhar Halqi"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idhar/ghoin.mp3")
    elif next_word == 'ه':
        law = "Idhar Halqi"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idhar/ha.mp3")
    elif next_word == 'ي':
        law = "Idgham Bigunnah"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idgham/ya.mp3")
    elif next_word == 'و':
        law = "idgham Bigunnah"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idgham/waw.mp3")
    elif next_word == 'م':
        law = "Idgham Bigunnah"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idgham/mim.mp3")
    elif next_word == 'ن':
        law = "Idgham Bigunnah"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idgham/nun.mp3")
    elif next_word == 'ل':
        law = "Idgham Bilagunnah"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idgham/lam.mp3")
    elif next_word == 'ر':
        law = "Idgham Bilagunnah"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "idgham/ra.mp3")
    elif next_word == 'ت':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/ta.mp3")
    elif next_word == 'ث':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/tsa.mp3")
    elif next_word == 'د':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/dal.mp3")
    elif next_word == 'ذ':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/dzal.mp3")
    elif next_word == 'ج':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/jim.mp3")
    elif next_word == 'ز':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/za.mp3")
    elif next_word == 'س':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/sin.mp3")
    elif next_word == 'ش':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/syin.mp3")
    elif next_word == 'ص':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/shad.mp3")
    elif next_word == 'ض':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/dhad.mp3")
    elif next_word == 'ط':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/tha.mp3")
    elif next_word == 'ظ':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/zha.mp3")
    elif next_word == 'ف':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/fa.mp3")
    elif next_word == 'ق':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/qaf.mp3")
    elif next_word == 'ك':
        law = "Ikhfa Hakiki"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "ikhfa/kaf.mp3")
    elif next_word == 'ب':
        law = "Iqlab"
        sound = os.path.join(app.config['UPLOAD_FOLDER'], "iqlab/ba.mp3")
    else:
        law = "No Laws Detected"
        sound = "No sound"
    return law, sound

@app.route('/')
def hello_world():
    return jsonify("Hello World"),200

@app.route('/upload-image-base64', methods=['POST'])
def upload_image():
    start = timer()
    data = request.get_json()
    if 'path' in request.form:
        base64_image = request.form['path']
    elif 'path' in data:
        base64_image = data['path']
    else:
        return jsonify({"message": "No File Selected"}), 422
    
    image_decoded = base64.b64decode(base64_image)
    image_extension = imghdr.what(None, h=image_decoded)
    if image_extension not in ALLOWED_EXTENSIONS:
        return jsonify({"message": "File not supported"}), 415
    if base64_image and (image_extension in ALLOWED_EXTENSIONS):
        image_data = Image.open(BytesIO(image_decoded))
        filename = datetime.now().strftime("%d%m%Y%H%M%S") + "." + image_extension
        image_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename), optimize=True)

        # Open File
        image = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # ArabicOCR
        results = ArabicOCR(image)

        # Get The Text After OCR
        words = []
        for j in range(len(results)):
            word = results[j][1]
            words.append(word)

        # Check if ArabicOCR detected the image
        arrayLength = len(words)

        if arrayLength > 0:
            # Turn Text Into String
            arabic_text = ' '.join(words)
            arabic_text = re.sub(' +', ' ', arabic_text)
            words = []
            words.append(arabic_text)
            arrayLength = len(words)

            # Get Verse From Quran Using Arabic Word Search
            quran_sound = QuranVerseSound(arabic_text)
        
            # Check Word After Nun Sukun
            next_word = CheckWordAfterNoonSaakin(arrayLength, words)

            # Check Tajweed Laws
            law, sound = CheckTajweedLaws(next_word)

            if quran_sound == "Not Found" or quran_sound == "Max retires exceeded":
                sound_how_to_read = sound
            else:
                sound_how_to_read = quran_sound
            
            if sound_how_to_read == "No sound":
                display_sound = sound_how_to_read
            elif sound_how_to_read != "Not found" and sound_how_to_read == sound:
                display_sound = request.host_url + sound_how_to_read
            else:
                display_sound = sound_how_to_read

            objectData = {
                "image": request.host_url + app.config['UPLOAD_FOLDER'] + filename,
                "arabic_text": arabic_text,
                "word_after_noon_sakin": next_word,
                "tajweed_law": law,
                "sound_how_to_read": display_sound
            }

            print(timer()-start)
            return jsonify(objectData)
        else:
            return jsonify({"message": "Image Not Detected"}), 422

if __name__ == '__main__':
    app.run()