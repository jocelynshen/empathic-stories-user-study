from firebase_admin import credentials, firestore, initialize_app, db
import firebase_admin
import sys
import random
from flask import Flask, make_response
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


c = firebase_admin.credentials.Certificate("./credentials.json")
default_app = firebase_admin.initialize_app(c, {
    'databaseURL': "https://empathic-stories-default-rtdb.firebaseio.com/"
})

id = 0
num_hits_per_worker = 15

model1 = ["model1story1", "model1story2", "model1story3", "model1story4",
          "model1story5", "model1story6", "model1story7", "model1story8", "model1story9"]
model2 = ["model2story1", "model2story2", "model2story3", "model2story4",
          "model2story5", "model2story6", "model2story7", "model2story8", "model2story9"]
model3 = ["model3story1", "model3story2", "model3story3", "model3story4",
          "model3story5", "model3story6", "model3story7", "model3story8", "model3story9"]
model4 = ["model4story1", "model4story2", "model4story3", "model4story4",
          "model4story5", "model4story6", "model4story7", "model4story8", "model4story9"]

prompt1 = '''
<div class="col-11 section" id="storywriting-section">
<h4><label for="summary">Part 2: Write your story "prompt 1"</label></h4>
<h5 class="text-justify" style="margin-top:.5rem">
    1. Look back over your life, and tell us an emotional moment or experience you have had in the past.
    Whether it's a childhood memory, a turning point in your life, or a vivid adult experience, please
    describe the scene in detail.
    <br>You might have encountered challenges or memorable events that could be realted to:</h5>
<ul>
    <li>Family</li>
    <li>Relationship/Friendship</li>
    <li>Mental Health</li>
    <li>Physical Health</li>
    <li>College/School</li>
    <li>Work</li>
    <li>Trauma</li>
    <li>Life Milestones/Changes</li>
    <li>Happiness and Fulfillment</li>
    <li>Passion & Youth</li>
</ul>
<h5 class="text-justify">Reflect on your emotions during the experience, describe how you felt across
    different events in the story, and explain its impact. What happened, when and where, who
    was involved, and what were you thinking and feeling?</h5>
<label for="sel1" class="form-label">Choose the most relevant topic that desribes your story:</label>
<select class="form-select" id="topics" name="topics" style="width:900px;">
    <option disabled selected value="">-- please select --</option>
    <option value="family">Family</option>
    <option value="relationship/friendship">Relationship/Friendship</option>
    <option value="mental-health">Mental Health</option>
    <option value="physical-health">Physical Health</option>
    <option value="college/school">College/School</option>
    <option value="work">Work</option>
    <option value="trauma">Trauma</option>
    <option value="lifeChange">Life Milestones/Changes</option>
    <option value="happiness/fulfillment">Happiness and Fulfillment</option>
    <option value="passion/youth">Passion & Youth</option>

</select>
<br>
<small>Please share as vulnerably as you feel comfortably sharing, but do not include any personal
    identifiers (i.e. SSN, addresses,...etc).<br>
    Your stories will be received <em>anonymously.</em></small>


<div class="row">
    <div class="col-8">

    <div class="form-group">
        <textarea class="form-control" name="userstory" id="userstory" style="width: 900px;
        height: 200px;" oninput="updateCounter(this,1,100,50,1000);" required></textarea>
        <span id="userstory-sentence-counter">0 sentences (0 characters) detected</span>

    </div>
    <div id="userstory-length-warning" class="col-6 alert alert-danger" style="display: none;">
        Response must be at least 1 sentence, between 50 and 1000 characters (including spaces).
    </div>
    </div>

</div>
<!-- <p style="color:red; font-weight: bold;">Copying/pasting or using automatic tools (e.g. ChatGPT, GPT-3) to
answer this question will result in
rejection
of the HIT by our checkers. Please answer honestly and to the best of your ability.</p> -->
<p class="mt-3">
    <small>Response must be <em>at least 10 sentences</em> and <em>1000 - 10,000 characters</em> including
    spaces.</small>
    <br>

</p>
</div>
'''

prompt2 = '''
<div class="col-11 section" id="storywriting-section">
<h4><label for="summary">Part 2: Write your story "prompt 2"</label></h4>
<h5 class="text-justify" style="margin-top:.5rem">
    1. Immerse in your emotions and describe a past experience that you may describe as either a high point or a low point in your life.
    <br><br>A high point scene could be one that was an especially joyous, exciting, or wonderful moment in you life.
    The latter, however, is an unpleasant or painful experince you had to go through.
    <br>You might have encountered challenges or memorable events that could be realted to:</h5>
    <ul>
        <li>Happiness and Satisfaction</li>
        <li>Motivation</li>
        <li>Gratitude</li>
        <li>Grief</li>
        <li>Loneliness</li>
        <li>Depression</li>
        <li>Anxiety</li>
    </ul></h5>
    
    <h5 class="text-justify">Thinking back over your entire life, choose a scene, that could be positive or negative, which has had its impact in residing in your memory.
    What happened in the event, where and when, who was involved, and what were you thinking and feeling?</h5>
    <label for="sel1" class="form-label">Choose the topic that best desribes your emotions in the story:</label>
    <select class="form-select" id="topics" name="topics" style="width:900px;">
    <option disabled selected value="">-- please select --</option>
    <option value="happiness">Happiness and Satisfaction</option>
    <option value="motivation">Motivation</option>
    <option value="gratitude">Gratitude</option>
    <option value="grief">Grief</option>
    <option value="Loneliness">Loneliness</option>
    <option value="depression">Depression</option>
    <option value="anxiety">Anxiety</option>
    
    </select> 
    
    <br>
    <small>Please share as vulnerably as you feel comfortably sharing, but do not include any personal identifiers (i.e. SSN, addresses,...etc).<br>
    Your stories will be received <em>anonymously.</em></small>


<div class="row">
    <div class="col-8">

    <div class="form-group">
        <textarea class="form-control" name="userstory" id="userstory" style="width: 900px;
        height: 200px;"
        oninput="updateCounter(this,1,100,50,1000);" required></textarea>
        <span id="id="userstory-sentence-counter">0 sentences (0 characters) detected</span>

    </div>
    <div id="userstory-length-warning" class="col-6 alert alert-danger" style="display: none;">
        Response must be at least 1 sentence, between 50 and 1000 characters (including spaces).
    </div>
    </div>

</div>
<p class="mt-3">
    <small>Response must be <em>at least 10 sentences</em> and <em>1000 - 10,000 characters</em> including
    spaces.</small>
    <br>

</p>
</div>
'''

prompt3 = '''
<div class="col-11 section" id="storywriting-section">
<h4><label for="summary">Part 2: Write your story "prompt 3"</label></h4>
<h5 class="text-justify" style="margin-top:.5rem">
    1. In reviving your memories, you must have identified key moments or milestones in your life that have changed you from within. 
    These life changes may have taught you lessons that you still stand by even if you had to learn them the hard way.
    <br>You might have encountered challenges or memorable events that could be realted to:</h5>
    <ul>
        <li>Motivation & Encouragement</li>
        <li>Overcoming and Resilience</li>
        <li>Happiness and Fulfillment</li>
        <li>Social Support & Gratitude</li>
        <li>Hard Work & Success</li>
        
        
    </ul></h5>
    <h5 class="text-justify">Describe a story that may identify a turning point in your life, which may have changed your mindset and thoughts. What is the moral of your story? How has this life lesson impacted your judgement and self awareness?</h5>
    <label for="sel1" class="form-label">Choose the topic that best desribes the moral of your story:</label>
    <select class="form-select" id="topics" name="topics" style="width:900px;">
    <option disabled selected value="">-- please select --</option>
    <option value="motivation">Motivation & Encouragement</option>
    <option value="overcoming">Overcoming and Resilience</option>
    <option value="happiness">Happiness and Fulfillment</option>
    <option value="support">Social Support & Gratitude</option>
    <option value="success">Hard Work & Success</option>
    
    </select> 
    <br>
    <small>Please share as vulnerably as you feel comfortably sharing, but do not include any personal identifiers (i.e. SSN, addresses,...etc).<br>
    Your stories will be received <em>anonymously.</em></small>


<div class="row">
    <div class="col-8">

    <div class="form-group">
        <textarea class="form-control" name="userstory" id="userstory" style="width: 900px;
        height: 200px;"
        oninput="updateCounter(this,1,100,50,1000);" required></textarea>
        <span id="userstory-sentence-counter">0 sentences (0 characters) detected</span>

    </div>
    <div id="userstory-length-warning" class="col-6 alert alert-danger" style="display: none;">
        Response must be at least 1 sentence, between 50 and 1000 characters (including spaces).
    </div>
    </div>

</div>

<p class="mt-3">
    <small>Response must be <em>at least 10 sentences</em> and <em>1000 - 10,000 characters</em> including
    spaces.</small>
    <br>

</p>
</div>
'''


@app.route('/')
def hello_world():
    return "Hello World"


@app.route('/participantIDInput/', methods=["POST"])
def get_participant_id():
    # """Get current session number for participant"""
    # # randomly select story FROM stories that haven't been seen before (store it in firebase)
    # print('test')
    participantIDInput = request.json['participantIDInput']
    global id
    id = participantIDInput
    print(f'The value of my id is {id}')

    ref = db.reference(participantIDInput)
    currentSession = db.reference(participantIDInput + "/currentSession").get()

    if currentSession is None:
        db.reference(participantIDInput + "/currentSession").set(1)
    elif currentSession == 1:
        db.reference(participantIDInput + "/currentSession").set(2)
    elif currentSession == 2:
        db.reference(participantIDInput + "/currentSession").set(3)

    return "success"

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

    # """Get initial writing prompt for user + retrieve 3 stories from 3 models + save to firebase"""
    # randomly select story FROM stories that haven't been seen before (store it in firebase)
    prompt = ''
    story1 = ''
    story2 = ''
    story3 = ''
    story4 = ''
    # prepare session 1
    story1session1random = random.choice(model1)
    story2session1random = random.choice(model2)
    story3session1random = random.choice(model3)
    story4session1random = random.choice(model4)
    # prepare session 2
    exclude_model1_index = model1.index(story1session1random)
    exclude_model2_index = model2.index(story2session1random)
    exclude_model3_index = model3.index(story3session1random)
    exclude_model4_index = model4.index(story4session1random)
    model1Session2 = model1[:exclude_model1_index] + \
        model1[exclude_model1_index + 1:]
    model2Session2 = model2[:exclude_model2_index] + \
        model2[exclude_model2_index + 1:]
    model3Session2 = model3[:exclude_model3_index] + \
        model3[exclude_model3_index + 1:]
    model4Session2 = model4[:exclude_model4_index] + \
        model3[exclude_model4_index + 1:]
    story1session2random = random.choice(model1Session2)
    story2session2random = random.choice(model2Session2)
    story3session2random = random.choice(model3Session2)
    story4session2random = random.choice(model4Session2)
    # prepare session 3
    exclude_model1Session2_index = model1Session2.index(story1session2random)
    exclude_model2Session2_index = model2Session2.index(story2session2random)
    exclude_model3Session2_index = model3Session2.index(story3session2random)
    exclude_model4Session2_index = model4Session2.index(story4session2random)
    model1Session3 = model1Session2[:exclude_model1Session2_index] + \
        model1Session2[exclude_model1Session2_index + 1:]
    model2Session3 = model2Session2[:exclude_model2Session2_index] + \
        model2Session2[exclude_model2Session2_index + 1:]
    model3Session3 = model3Session2[:exclude_model3Session2_index] + \
        model3Session2[exclude_model3Session2_index + 1:]
    model4Session3 = model4Session2[:exclude_model4Session2_index] + \
        model4Session2[exclude_model4Session2_index + 1:]
    story1session3random = random.choice(model1Session3)
    story2session3random = random.choice(model2Session3)
    story3session3random = random.choice(model3Session3)
    story4session3random = random.choice(model4Session3)
    ##########################################################################
    ref = db.reference(id)
    currentSession = db.reference(id + "/currentSession").get()
    if currentSession == 1:
        prompt = prompt1
        story1 = story1session1random
        story2 = story2session1random
        story3 = story3session1random
        story4 = story4session1random
    elif currentSession == 2:
        prompt = prompt2
        story1 = story1session2random
        story2 = story2session2random
        story3 = story3session2random
        story4 = story4session2random
    elif currentSession == 3:
        prompt = prompt3
        story1 = story1session3random
        story2 = story2session3random
        story3 = story3session3random
        story4 = story4session3random

    dict = {'prompt': prompt, 'story1': story1,
            'story2': story2, 'story3': story3, 'story4': story4}
    return json.dumps(dict)


@app.route('/submit/', methods=["GET", "POST"])
def submit():

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

    demographic = {"gender": gender, "age": age,
                   "race": race, "empathyLevel": empathyLevel}
    mystoryQuestions = {"mainEvent": mainEvent,
                        "narratorEmotions": narratorEmotions, "moral": moral, "storyDate": storyDate}
    reflection = {"valence": valence, "arousal": arousal}
    story1 = {"condition": "condition1", "story": "this is story1",
              "survey1questions": survey1_answers}
    story2 = {"condition": "condition2", "story": "this is story2",
              "survey2questions": survey2_answers}
    story3 = {"condition": "condition3", "story": "this is story3",
              "survey3questions": survey3_answers}
    story4 = {"condition": "condition4", "story": "this is story4",
              "survey4questions": survey4_answers}

    ref = db.reference(id)
    currentSession = db.reference(id + "/currentSession").get()
    if currentSession == 1:
        session1 = db.reference(id + '/s001')
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
        # db.reference(participantID + "/currentSession").set(2)

    elif currentSession == 2:
        session2 = db.reference(id + '/s002')
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
        # db.reference(participantID + "/currentSession").set(3)

    elif currentSession == 3:
        session3 = db.reference(id + '/s003')
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
    # app.run(host=host, port=port, debug=debug, ssl_context=("/etc/letsencrypt/live/wall-e.media.mit.edu/fullchain.pem", "/etc/letsencrypt/live/wall-e.media.mit.edu/privkey.pem"))
