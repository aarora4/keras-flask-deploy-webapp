import os
import sys

# Flask
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image

# Some utilites
import numpy as np

import librosa

from sklearn.preprocessing import LabelEncoder

# Declare a flask app
app = Flask(__name__)


# You can use pretrained model from Keras
# Check https://keras.io/applications/
# or https://www.tensorflow.org/api_docs/python/tf/keras/applications

# from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
# model = MobileNetV2(weights='imagenet')

# print('Model loaded. Check http://127.0.0.1:5000/')


# Model saved with Keras model.save()
MODEL_PATH = 'models/your_model.h5'

# graph = tf.get_default_graph()

# Load your own trained model
# model = load_model(MODEL_PATH)
# model._make_predict_function()          # Necessary

config = tf.ConfigProto(
                intra_op_parallelism_threads=1,
                allow_soft_placement=True
            )
session = tf.Session(config=config)

keras.backend.set_session(session)

model = load_model("best_fantano.h5", compile=False)
model._make_predict_function()
print('Model loaded. Start serving...')



le = LabelEncoder()
le.classes_ = np.load('static/classes.npy')


def model_predict(vector, model):
    # img = img.resize((224, 224))

    # Preprocessing the image
    # x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    # x = np.expand_dims(x, axis=0)

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
    # x = preprocess_input(x, mode='tf')
    print([np.array(vector)][0])

    try:
        with session.as_default():
                with session.graph.as_default():
                    preds = model.predict(np.array([vector]))

        
        # print(preds)
        # print(np.argmax(preds))
        # print(le.inverse_transform([np.argmax(preds)]))
                    return le.inverse_transform([np.argmax(preds)])
    
    except Exception as ex:
        print(ex)

    return [2.0]



@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    
    if request.method == 'POST':
        print(request.files['audio_file'])
        audio = request.files['audio_file']
        x, sr = librosa.load(audio)
        rmse = librosa.feature.rms(y=x)
        chroma_stft = librosa.feature.chroma_stft(y=x, sr=sr)
        spec_cent = librosa.feature.spectral_centroid(y=x, sr=sr)
        spec_bw = librosa.feature.spectral_bandwidth(y=x, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=x, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(x)
        mfcc = librosa.feature.mfcc(y=x, sr=sr)

        to_append = f'{np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}'    
        for e in mfcc:
            to_append += f' {np.mean(e)}'
        
        vect = to_append.split()

        for i in range(len(vect)):
            vect[i] = float(vect[i])

        # request.files.keys())
        # Get the image from post request
        # img = base64_to_pil(request.json)

        # Save the image to ./uploads
        # img.save("./uploads/image.png")

        # Make prediction
        preds = model_predict(vect, model)

        # Process your result for human
        # pred_proba = "{:.3f}".format(np.amax(preds))    # Max probability
        # pred_class = decode_predictions(preds, top=1)   # ImageNet Decode

        # result = str(pred_class[0][0][1])               # Convert to string
        # result = result.replace('_', ' ').capitalize()
        
        # Serialize the result, you can add additional fields
        # return jsonify(result=result, probability=pred_proba)
        
        return jsonify(result=preds.tolist())

    return None


if __name__ == '__main__':
    portnum = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=portnum, threaded=True)
    # app.run(threaded=True, port=process.env.PORT)

    # Serve the app with gevent
    # http_server = WSGIServer(('0.0.0.0', 5000), app)
    # http_server.serve_forever()

    
