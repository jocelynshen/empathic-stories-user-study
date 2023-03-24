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
    'databaseURL':"https://empathic-stories-default-rtdb.firebaseio.com/"
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



# test
# @app.route('/index/', methods=["GET", "POST"])
# def test():
#     ref = db.reference('p001/s001/demographic')
#     info = ref.get()
#     # ref.update({ip:ip_count})
#     print('----test results-----')
#     print(info)
#     # x = json.dumps(info)
#     # print(x)
#     # y = json.loads(x)
#     # print(y)
#     print('----end test results----')
#     return json.dumps(info['gender'])
# test




@app.route('/getPrompt/', methods=["GET", "POST"])
def get_prompt_and_stories():
    """Get initial writing prompt for user + retrieve 3 stories from 3 models + save to firebase"""
    # randomly select story FROM stories that haven't been seen before (store it in firebase)
    pass

@app.route('/submit/', methods=["GET", "POST"])
def submit():

    participantID = request.json['participantID']
    valence = request.json['valence']
    arousal = request.json['arousal']
    mystoryTopic = request.json['mystoryTopic']
    mystory = request.json['mystory']
    survey1_answers = request.json['survey1_answers']
    survey2_answers = request.json['survey2_answers']
    survey3_answers = request.json['survey3_answers']
    survey4_answers = request.json['survey4_answers']
    mostEmpathizedOrder = request.json['mostEmpathizedOrder']
    mainEvent = request.json['mainEvent']
    narratorEmotions = request.json['narratorEmotions']
    moral = request.json['moral']
    storyDate = request.json['storyDate']
    gender = request.json['gender']
    age = request.json['age']
    race = request.json['race']
    empathyLevel = request.json['empathyLevel']
    feedback = request.json['feedback']

    demographic = {"gender": gender, "age": age, "race": race, "empathyLevel":empathyLevel}
    mystoryQuestions = {"mainEvent": mainEvent, "narratorEmotions":narratorEmotions, "moral":moral, "storyDate":storyDate}
    reflection = {"valence": valence, "arousal": arousal}
    story1 = {"condition": "condition1", "story": "this is story1", "survey1questions": survey1_answers}
    story2 = {"condition": "condition2", "story": "this is story2", "survey2questions": survey2_answers}
    story3 = {"condition": "condition3", "story": "this is story3", "survey3questions": survey3_answers}
    story4 = {"condition": "condition4", "story": "this is story4", "survey4questions": survey4_answers}
    ref = db.reference(participantID)
    currentSession = db.reference(participantID + "/currentSession").get()
    if currentSession is None:
        session1 = db.reference(participantID +'/s001')
        session1.child("prompt").set("here store prompt1")
        session1.child("demographic").set(demographic)
        session1.child("feedback").set(feedback)
        session1.child("mostEmpathizedOrder").set(mostEmpathizedOrder)
        session1.child("mystory").set(mystory)
        session1.child("mystoryTopic").set(mystoryTopic)
        session1.child("mystoryQuestions").set(mystoryQuestions)
        session1.child("reflection").set(reflection)
        session1.child("story1").set(story1)
        session1.child("story2").set(story2)
        session1.child("story3").set(story3)
        session1.child("story4").set(story4)
        db.reference(participantID + "/currentSession").set(2)

    elif currentSession == 2:
        session2 = db.reference(participantID +'/s002')
        session2.child("prompt").set("here store prompt2")
        session2.child("demographic").set(demographic)
        session2.child("feedback").set(feedback)
        session2.child("mostEmpathizedOrder").set(mostEmpathizedOrder)
        session2.child("mystory").set(mystory)
        session2.child("mystoryTopic").set(mystoryTopic)
        session2.child("mystoryQuestions").set(mystoryQuestions)
        session2.child("reflection").set(reflection)
        session2.child("story1").set(story1)
        session2.child("story2").set(story2)
        session2.child("story3").set(story3)
        session2.child("story4").set(story4)
        db.reference(participantID + "/currentSession").set(3)

    elif currentSession == 3:
        session3 = db.reference(participantID +'/s003')
        session3.child("prompt").set("here store prompt3")
        session3.child("demographic").set(demographic)
        session3.child("feedback").set(feedback)
        session3.child("mostEmpathizedOrder").set(mostEmpathizedOrder)
        session3.child("mystory").set(mystory)
        session3.child("mystoryTopic").set(mystoryTopic)
        session3.child("mystoryQuestions").set(mystoryQuestions)
        session3.child("reflection").set(reflection)
        session3.child("story1").set(story1)
        session3.child("story2").set(story2)
        session3.child("story3").set(story3)
        session3.child("story4").set(story4)

    return 'Data submitted successfully!'
    # pass



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
# to run the server run the following command:
# python server.py '0.0.0.0' 5192 1 
if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    debug = sys.argv[3]
    app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(host=host, port=port, debug=debug, ssl_context=("/etc/letsencrypt/live/wall-e.media.mit.edu/fullchain.pem", "/etc/letsencrypt/live/wall-e.media.mit.edu/privkey.pem"))
