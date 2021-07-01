import librosa

from sklearn.preprocessing import LabelEncoder

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
import numpy as np

import os
import random

from base64 import b64decode

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

def extract_features_and_predict(path):
    # print(path)

    random_number = random.randint(00000, 99999)

    filepath = './tmp/' + str(random_number) + '.wav'

    wav_file = open(filepath, "wb")
    decode_string = b64decode(path)
    wav_file.write(decode_string)
    
    x, sr = librosa.load(filepath)
    print('got here bor')
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

    os.remove(filepath)
    # Process your result for human
    # pred_proba = "{:.3f}".format(np.amax(preds))    # Max probability
    # pred_class = decode_predictions(preds, top=1)   # ImageNet Decode

    # result = str(pred_class[0][0][1])               # Convert to string
    # result = result.replace('_', ' ').capitalize()
    
    # Serialize the result, you can add additional fields
    # return jsonify(result=result, probability=pred_proba)

    responseObject = {
        "result": preds.tolist(),
        "errors": 'none'
    }
    
    return responseObject