from firebase_admin import credentials, firestore, initialize_app, db
import firebase_admin
import sys
import random
from flask import Flask, make_response, redirect, url_for, session
from flask import abort, request, jsonify
import json
# import tensorflow as tf
# gpus = tf.config.experimental.list_physical_devices('GPU')
# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)
from flask import Flask
from flask_cors import CORS
import logging
import threading

from multiprocessing import Lock

sys.path.append("../")
lock = Lock()
app = Flask(__name__)
# app.secret_key = 'my_secret_key'
local_storage = threading.local()
app.config['UPLOAD_FOLDER'] = "data/"
app.config['MAX_CONTENT_LENGTH'] = 10000 * 1024 * 1024
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

sem = threading.Semaphore()

c = firebase_admin.credentials.Certificate("./credentials.json")
default_app = firebase_admin.initialize_app(c, {
    'databaseURL': "https://empathic-stories-default-rtdb.firebaseio.com/"
})

id = 0
num_hits_per_worker = 15

demographic = '''
<div class="form-group col-11 section">
    <h4><label for="summary">Part 4: Tell us about yourself and this writing task</label></h4>


    <h5 class="mt-4">1. How do you identify?<br><small>Select "prefer not to answer" if needed.</small></h5>
    <div class="form-group row mt-3">
        <label for="gender" class="col-sm-2 col-form-label">Gender identity*</label>
        <div class="col-sm-4">
        <select id="annotatorGender" name="annotatorGender" class="form-control" style="font-size: .85rem;"
            required>
            <option disabled selected value="">-- please select --</option>
            <option value="man">Man/Male</option>
            <option value="woman">Woman/Female</option>
            <option value="transman">Trans man</option>
            <option value="transwoman">Trans woman</option>
            <option value="nonBinary">Non-binary</option>
            <option value="other">Other</option>
            <option value="na">- prefer not to disclose -</option>
        </select>
        </div>
        <div class="col-sm-4"><small>Please select the gender identity you most identify with
            currently.</small>
        </div>
    </div>
    <div class="form-group row">
        <label for="annotatorAge" class="col-sm-2 col-form-label">Age (years)*</label>
        <div class="col-sm-4">
        <input type="number" id="age" name="age" placeholder="-" class="form-control" min="18" max="100" required>

        </div>
        <div class="col-sm-4"><small>Leave blank if you do not wish to disclose</small></div>

    </div>
    <div class="form-group row">
        <label for="race" class="col-sm-2 col-form-label">Race/ethnicity*</label>
        <div class="col-sm-4">
        <select id="annotatorRace" name="annotatorRace" class="form-control" style="font-size: .85rem;"
            required>
            <option disabled selected value="">-- please select --</option>
            <option value="asian">Asian/Asian American</option>
            <option value="indian">South Asian/Indian American</option>
            <option value="black">Black/African American</option>
            <option value="hisp">Hispanic/Latinx</option>
            <option value="white">White/Caucasian</option>
            <option value="middleEastern">Middle Eastern</option>
            <option value="islander">Native Hawaiian/Pacific Islander</option>
            <option value="native">Native American/First Nations</option>
            <option value="other">Mixed/other</option>
            <option value="na">- prefer not to disclose -</option>
        </select>
        </div>
        <div class="col-sm-4"><small>Please select the racial/ethnic identity you most identify with
            currently.</small></div>
    </div>
    <div class="mb-3">
        <h5 class="mt-4">2. To what extent does the following statement describe you:*</h5>
        <label for="empathy" class="form-label">
        <h5>“I am an empathetic person.” </h5>
        </label>
        <div class="form-check lickert">
        <input class="form-check-input right" type="radio" name="empathylevel" id="notTrueAtAll" value="1"
            required> <label class="form-check-label" for="notVeryTrue">&nbsp; Not very true of me </label>
        </div>
        <div class="form-check lickert">
        <input class="form-check-input right" type="radio" name="empathylevel" id="notTrue" value="2" required>
        <label class="form-check-label" for="notTrue">&nbsp; Not true</label>

        </div>
        <div class="form-check lickert">
        <input class="form-check-input right" type="radio" name="empathylevel" id="iamneutral" value="3" required>
        <label class="form-check-label" for="iamneutral">&nbsp; Neutral</label>

        </div>
        <div class="form-check lickert">
        <input class="form-check-input right" type="radio" name="empathylevel" id="true" value="4" required>
        <label class="form-check-label" for="true">&nbsp; True</label>

        </div>
        <div class="form-check lickert">
        <input class="form-check-input" type="radio" name="empathylevel" id="veryTrue" value="5" required>
        <label class="form-check-label" for="veryTrue">&nbsp; Very true of me</label>
        </div>

    </div>

    <div class="form-group">
        <div class="form-check">
        <input class="form-check-input" type="checkbox" id="certify-no-pii-story" name="certify-no-pii-story"
            required>
        <label class="form-check-label" for="certify-no-pii-story">
            I certify that my responses contain no personally identifiable information (name, address, SSN,
            etc)
            about
            myself or anyone else. *
        </label>
        </div>
    </div>
    </div>
'''

prompt1 = '''
<div class="col-11 section" id="storywriting-section">
    <h4><label for="summary">Part 2: Write your story</label></h4>
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
    <label for="sel1" class="form-label">Choose the most relevant topic that desribes your story:*</label>
    <select class="form-select" id="topics" name="topics" style="width:900px;" required>
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
        Your stories will be received <em>anonymously.</em>*</small>


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

dbprompt1 = '''
Look back over your life, and tell us an emotional moment or experience you have had in the past.
Whether it's a childhood memory, a turning point in your life, or a vivid adult experience, please
describe the scene in detail.
You might have encountered challenges or memorable events that could be realted to:
[Family, Relationship/Friendship, Mental Health, Physical Health, College/School, Work, Trauma, Life Milestones/Changes, Happiness and Fulfillment, or Passion & Youth].
Reflect on your emotions during the experience, describe how you felt across different events in the story, and explain its impact.
What happened, when and where, who was involved, and what were you thinking and feeling?
'''
prompt2 = '''
<div class="col-11 section" id="storywriting-section">
    <h4><label for="summary">Part 2: Write your story</label></h4>
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
        <label for="sel1" class="form-label">Choose the topic that best desribes your emotions in the story:*</label>
        <select class="form-select" id="topics" name="topics" style="width:900px;" required>
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
        Your stories will be received <em>anonymously.</em>*</small>


    <div class="row">
        <div class="col-8">

        <div class="form-group">
            <textarea class="form-control" name="userstory" id="userstory" style="width: 900px; height: 200px;" oninput="updateCounter(this,1,100,50,1000);" required></textarea>
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

dbprompt2 = '''
Immerse in your emotions and describe a past experience that you may describe as either a high point or a low point in your life.
A high point scene could be one that was an especially joyous, exciting, or wonderful moment in you life.
The latter, however, is an unpleasant or painful experince you had to go through.
You might have encountered challenges or memorable events that could be realted to:
[Happiness and Satisfaction, Motivation, Gratitude, Grief, Loneliness, Depression, or Anxiety].
Thinking back over your entire life, choose a scene, that could be positive or negative, which has had its impact in residing in your memory.
What happened in the event, where and when, who was involved, and what were you thinking and feeling?
'''

prompt3 = '''
<div class="col-11 section" id="storywriting-section">
    <h4><label for="summary">Part 2: Write your story</label></h4>
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
        <label for="sel1" class="form-label">Choose the topic that best desribes the moral of your story:*</label>
        <select class="form-select" id="topics" name="topics" style="width:900px;" required>
        <option disabled selected value="">-- please select --</option>
        <option value="motivation">Motivation & Encouragement</option>
        <option value="overcoming">Overcoming and Resilience</option>
        <option value="happiness">Happiness and Fulfillment</option>
        <option value="support">Social Support & Gratitude</option>
        <option value="success">Hard Work & Success</option>
        
        </select> 
        <br>
        <small>Please share as vulnerably as you feel comfortably sharing, but do not include any personal identifiers (i.e. SSN, addresses,...etc).<br>
        Your stories will be received <em>anonymously.</em>*</small>


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

dbprompt3 = '''
In reviving your memories, you must have identified key moments or milestones in your life that have changed you from within. 
These life changes may have taught you lessons that you still stand by even if you had to learn them the hard way.
You might have encountered challenges or memorable events that could be realted to:
[Motivation & Encouragement, Overcoming and Resilience, Happiness and Fulfillment, Social Support & Gratitude, or Hard Work & Success].
Describe a story that may identify a turning point in your life, which may have changed your mindset and thoughts. What is the moral of your story?
How has this life lesson impacted your judgement and self awareness?
'''


@app.route('/')
def hello_world():
    return "Hello World"


@app.route('/participantIDInput/', methods=["POST"])
def get_participant_id():
    sem.acquire()
    # """Get current session number for participant"""
    # # randomly select story FROM stories that haven't been seen before (store it in firebase)
    # print('test')
    participantIDInput = request.json['participantIDInput']
    print(f'The value of my id is {participantIDInput}')
    ref = db.reference(participantIDInput)
    currentSession = db.reference(participantIDInput + "/currentSession").get()

    if currentSession is None:
        db.reference(participantIDInput + "/currentSession").set(1)
    elif currentSession == 1:
        db.reference(participantIDInput + "/currentSession").set(2)
    elif currentSession == 2:
        db.reference(participantIDInput + "/currentSession").set(3)
    elif currentSession == 3:
        db.reference(participantIDInput + "/currentSession").set(4)

    sem.release()
    return "success"

def get_stories_from_model(mystory):
    return {"condition1": "story about apples", "condition2": "story about bananas", "condition3": "story about dogs", "condition4": "story about bananas"}

@app.route('/sessionDone/', methods=["GET", "POST"])
def sessionDone():
    sem.acquire()
    id = request.json['participantIDInput']
    ref = db.reference(id)
    currentSession = db.reference(id + "/currentSession").get()
    dict = {'showParticipantID': id, 'showSessionNum': currentSession}
    sem.release()
    return json.dumps(dict)
            

@app.route('/getPrompt/', methods=["GET", "POST"])
def getPrompt():
    # """Get initial writing prompt for user + retrieve 3 stories from 3 models + save to firebase"""
    # randomly select story FROM stories that haven't been seen before (store it in firebase)
    sem.acquire()
    id = request.json['participantIDInput']
    ##########################################################################
    currentSession = db.reference(id + "/currentSession").get()
    if currentSession == 1:
        prompt = prompt1
        dict = {'demographic': demographic, 'showParticipantID': id, 'showSessionNum': currentSession, 'prompt': prompt}
    elif currentSession == 2:
        prompt = prompt2
        dict = {'showParticipantID': id, 'showSessionNum': currentSession, 'prompt': prompt}
    elif currentSession == 3:
        prompt = prompt3
        dict = {'showParticipantID': id, 'showSessionNum': currentSession, 'prompt': prompt}
    elif currentSession == 4:
        dict = {'showParticipantID': id, 'showSessionNum': currentSession}
    sem.release()
    return json.dumps(dict)


@app.route('/submitMyStory/', methods=["GET", "POST"])
def submitMyStory():
    """Save their story in firebase"""
    sem.acquire()
    id = request.json['participantIDInput']

    valence = request.json['valence']
    arousal = request.json['arousal']
    reflection = {"valence": valence, "arousal": arousal}

    mystory = request.json['mystory']
    fullDate = request.json['fullDate']
    mystoryTopic = request.json['mystoryTopic']
    mainEvent = request.json['mainEvent']
    narratorEmotions = request.json['narratorEmotions']
    moral = request.json['moral']

    mystoryQuestions = {"mainEvent": mainEvent,
                    "narratorEmotions": narratorEmotions, "moral": moral, "fullDate": fullDate}

    ref = db.reference(id)
    currentSession = db.reference(id + "/currentSession").get()
    session = db.reference(id + '/s00' + str(currentSession))

    session.child("mystory").set(mystory)
    session.child("mystoryTopic").set(mystoryTopic)
    session.child("mystoryQuestions").set(mystoryQuestions)
    session.child("reflection").set(reflection)

    ## make call to model and send back
    stories = get_stories_from_model(mystory)
    # TODO: remove duplicates and randomize, save to firebase with what model it came from, send the 1-4 stories back to frontend to display

    sem.release()
    pass

@app.route('/submitSurveyQuestions/', methods=["GET", "POST"])
def submitSurveyQuestions():
    sem.acquire()
    id = request.json['participantIDInput']

    survey1_answers = request.json['survey1_answers']
    survey2_answers = request.json['survey2_answers']
    survey3_answers = request.json['survey3_answers']
    survey4_answers = request.json['survey4_answers']
    mostEmpathizedOrder = request.json['mostEmpathizedOrder']
    
    feedback = request.json['feedback']

    ref = db.reference(id)
    currentSession = db.reference(id + "/currentSession").get()
    if currentSession == 1:
        gender = request.json['gender']
        age = request.json['age']
        race = request.json['race']
        empathyLevel = request.json['empathyLevel']
        demographic = {"gender": gender, "age": age,
                       "race": race, "empathyLevel": empathyLevel}
        session1 = db.reference(id + '/s001')
        session1.child("demographic").set(demographic)
        session1.child("feedback").set(feedback)
        session1.child("prompt").set(dbprompt1)
        session1.child("mostEmpathizedOrder").set(mostEmpathizedOrder)

    elif currentSession == 2:
        session2 = db.reference(id + '/s002')
        session2.child("prompt").set(dbprompt2)
        session2.child("feedback").set(feedback)
        session2.child("mostEmpathizedOrder").set(mostEmpathizedOrder)

    elif currentSession == 3:
        session3 = db.reference(id + '/s003')
        session3.child("prompt").set(prompt3)
        session3.child("feedback").set(feedback)
        session3.child("mostEmpathizedOrder").set(mostEmpathizedOrder)
    sem.release()
    return 'Data submitted successfully!'

################################### START SERVER ###################################
# to run the server run the following command:
# python server.py '0.0.0.0' 5192 1
if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    debug = sys.argv[3]
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host=host, port=port, debug=debug, ssl_context=("/etc/letsencrypt/live/wall-e.media.mit.edu/fullchain.pem", "/etc/letsencrypt/live/wall-e.media.mit.edu/privkey.pem"))
