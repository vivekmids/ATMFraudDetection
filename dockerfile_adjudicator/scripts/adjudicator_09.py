import paho.mqtt.client as mqtt
import requests
from io import BytesIO
import face_recognition
import numpy as np
import time

# This script mimics adjudication traffic

#Incoming topics
ID = 'local/ID'
FACES = 'local/faces'
START_TXN = 'local/start'
SECONDARY_AUTH_RESPONSE = 'local/response'
FACES_FINISHED = 'local/faces_finished'

#Outgoing topics
GIVE_MONEY = 'adjudication/pass'
SECONDARY_AUTH_REQUIRED = 'adjudication/fail_face'
DECLINE = 'adjudication/terminate_face'
SECONDARY_AUTH_DECLINE = 'adjudication/terminate_info'
GO = 'adjudication/go'
STOP = 'adjudication/stop'


# Global variables
user = None
known_images = {
    'Vivek': 'https://s3.us-east.cloud-object-storage.appdomain.cloud/vivek/Vivek.png',
    'Mouli': 'https://s3.us-east.cloud-object-storage.appdomain.cloud/vivek/Mouli.png',
    'Errett': 'https://s3.us-east.cloud-object-storage.appdomain.cloud/w251-hw3-hobbs-bucket-01/20190522-225405399.png'
}
session = False

#Parameters
batch_size = 20 #Number of images to batch up
give_money = 0.7 #Threshold above which to dispense money
secondary_authentication = 0.2 # Threshold above which to ask for secondary authentication


# Instantiate a Paho MQTT client ('client')
client = mqtt.Client(client_id="adjudicator")
client.connect("mosquitto")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print(client.subscribe("local/#"))

def on_message(client, userdata, msg):
    print("Message Received", msg.topic)
    msgRouter(msg)

def msgRouter(msg):
    if msg.topic == ID:
        start(msg)
    elif msg.topic == FACES and session:
        queue(user, msg)
    elif msg.topic == SECONDARY_AUTH_RESPONSE:
        secondary_auth(user, msg)
    elif msg.topic == FACES_FINISHED:
        print("'faces_finished' message received!")
        client.publish(STOP, qos=2, retain=False)
    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

def start(msg):
    global image_queue
    global user
    global session
    session = True
    user = msg.payload
    if type(user) == bytes:
        user = user.decode('ASCII')
    client.publish(GO, qos=2, retain=False)
    image_queue = {}
    print ('Recevied ID message with user = ',user)

def queue (user, msg):
    global image_queue
    global session
    image = face_recognition.load_image_file(BytesIO(msg.payload))
    if image_queue.get(user)==None:
        image_queue = {**image_queue, user:[image]}
        print('First image added for', user)
    else:
        images = image_queue.get(user)
        images.append(np.array(image))
        if len(images) >= batch_size:
            session = False
            print('Enough images received. Sending STOP to camera')
            client.publish(STOP, qos=2, retain=False)
            print('Sending', user, 'for adjudication.')
            response = adjudicate(user, image_queue.pop(user))
            print('Received', response)
            client.publish(response, qos=2, retain=False)
        else:
            image_queue = {**image_queue, user:images}
            print('Image appended for', user)

def secondary_auth(user, msg):
    # Code to verify additional information. For now, just assume secondary authentication is successful
    if msg.payload == "money":
        client.publish(GIVE_MONEY, qos=2, retain=False)
    else:
        client.publish(SECONDARY_AUTH_DECLINE, payload="You entered an incorrect password", qos=2, retain=False)

def adjudicate(user, images):
    print('In Adjudicate with user', user)
    print('Received',len(images), 'images')
    url = known_images.get(user)
    response = requests.get(url)
    known_image = face_recognition.load_image_file(BytesIO(response.content))
    known_image_encoding = face_recognition.face_encodings(known_image)[0]

    matches = 0
    print('Starting loop for face recognition')
    for unknown_image in images:
        unknown_image_encoding = face_recognition.face_encodings(unknown_image)[0]
        result = face_recognition.compare_faces([known_image_encoding], unknown_image_encoding)
        print('Comparing images for', user)
        print('Result is', result)
        matches += result[0]

    match_ratio = matches/batch_size
    print('Match Ratio is', match_ratio)
    if match_ratio > give_money:
        return (GIVE_MONEY)
    elif match_ratio > secondary_authentication:
        return (SECONDARY_AUTH_REQUIRED)
    else:
        return (DECLINE)

# Connect to local mosquitto broker and subscribe to `local/#`
client.connect("mosquitto")
print("Client connect")
client.on_message = on_message
client.on_connect = on_connect

client.loop_forever()
