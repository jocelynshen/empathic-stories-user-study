import sys
from flask import Flask
from flask import abort, request, jsonify
import json
# import tensorflow as tf
# gpus = tf.config.experimental.list_physical_devices('GPU')
# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)
from flask import Flask
from flask_cors import CORS
import logging

from multiprocessing import Lock

sys.path.append("../")
lock = Lock()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "data/"
app.config['MAX_CONTENT_LENGTH'] = 10000 * 1024 * 1024
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, db

c = firebase_admin.credentials.Certificate("./credentials.json")
default_app = firebase_admin.initialize_app(c, {
    'databaseURL':"https://storytelling-6c0a3-default-rtdb.firebaseio.com/"
    })

num_hits_per_worker = 15

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/getSessionNumber/', methods=["GET", "POST"])
def get_session_number():
    """Get current session number for participant"""
    # randomly select story FROM stories that haven't been seen before (store it in firebase)
    pass


@app.route('/getPrompt/', methods=["GET", "POST"])
def get_prompt():
    """Get initial writing prompt for user + save to firebase"""
    # randomly select story FROM stories that haven't been seen before (store it in firebase)
    pass

@app.route('/getStories/', methods=["GET", "POST"])
def get_stories():
    """Get 3 stories from the model + save to firebase"""
    
    return json.dumps(dict(story1, "my story is great"))

@app.route('/submit/', methods=["GET", "POST"])
def submit():
    """User submitted survey/demographic information + save their data to firebase"""
    pass



# @app.route('/getIp/', methods=["GET", "POST"])
# def get_ip():
#     lock.acquire()
#     try:
#         print(request.form)
#         ip = request.form.get("ipaddress")
#         if ip:
#             ip = ip.replace(".", "-")
#         dbsource=request.form.get("dbsource")
#         workerId = request.form.get("workerId")
#         ref = db.reference(f'/{dbsource}/') 
#         current_ids = ref.get()
#         print(f"GET REQ FROM {ip}, {workerId}")
#         if ip in current_ids:
#             ip_count = current_ids[ip]
#         else:
#             ip_count = 0
#         if workerId in current_ids:
#             worker_count = current_ids[workerId]
#         else:
#             worker_count = 0

#         if ip_count >= num_hits_per_worker or worker_count >= num_hits_per_worker:
#             donehit = True 
#         else:
#             donehit = False
#         return json.dumps(dict(donehit=donehit))
#     except:
#         return abort(404)
#     finally:
#         lock.release()

# @app.route('/uploadIp/', methods=["GET", "POST"])
# def upload_ip():
#     lock.acquire()
#     try:
#         print(request.form)
#         ip = request.form.get("ipaddress")
#         if ip:
#             ip = ip.replace(".", "-")
#         workerId = request.form.get("workerId")
#         dbsource=request.form.get("dbsource")
#         ref = db.reference(f'/{dbsource}/')
#         current_ids = ref.get()
#         if ip in current_ids:
#             ip_count = current_ids[ip] + 1
#         else:
#             ip_count = 1
#         if workerId in current_ids:
#             worker_count = current_ids[workerId] + 1
#         else:
#             worker_count = 1
#         if ip:
#             ref.update({ip:ip_count})
#         if workerId:
#             ref.update({workerId: worker_count})
#             ref.update({workerId + "_to_ip": ip})
#         return json.dumps(dict(success=True))
#     except Exception as e:
#         print(e)
#         return abort(404)
#     finally:
#         lock.release()


################################### START SERVER ###################################
if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    debug = sys.argv[3]
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host=host, port=port, debug=debug, ssl_context=("/etc/letsencrypt/live/wall-e.media.mit.edu/fullchain.pem", "/etc/letsencrypt/live/wall-e.media.mit.edu/privkey.pem"))
