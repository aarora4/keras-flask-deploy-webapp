import os
import sys

# Flask
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# Some utilites
import numpy as np

from modeloperations import extract_features_and_predict

from rq import Queue
from worker import conn
import random

q = Queue(connection=conn) 

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


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/tasks/<taskID>', methods=['GET'])
def get_status(taskID):
    task = q.fetch_job(taskID)

    # If such a job exists, return its info
    if (task):
        responseObject = {
            "success": "success",
            "data": {
                "taskID": task.get_id(),
                "taskStatus": task.get_status(),
                "taskResult": task.result
            }
        }

    else:
        responseObject = {"status": "no task found!"}

    return responseObject


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    
    if request.method == 'POST':
        file = request.files['audio_file']

        random_number = random.randint(00000, 99999)

        filepath = '/tmp/' + str(random_number) + '.wav'

        file.save(filepath)

        

        task = q.enqueue(extract_features_and_predict, filepath)

        # create a dictionary with the ID of the task
        responseObject = {"status": "success", "data": {"taskID": task.get_id()}}
        # return the dictionary
        return jsonify(responseObject)

    return None


if __name__ == '__main__':
    portnum = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=portnum, threaded=True)
    # app.run(threaded=True, port=process.env.PORT)

    # Serve the app with gevent
    # http_server = WSGIServer(('0.0.0.0', 5000), app)
    # http_server.serve_forever()

    
