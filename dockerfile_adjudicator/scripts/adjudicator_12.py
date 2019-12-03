import paho.mqtt.client as mqtt
import requests
from io import BytesIO
import face_recognition
import numpy as np
import time
from sklearn.metrics import classification_report
from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img

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
USER_NOT_FOUND = 'adjudication/usernotfound'


# Global variables
user = None
known_images = {
    'Vivek': 'https://s3.us-east.cloud-object-storage.appdomain.cloud/vivek/Vivek.png',
    'Mouli': 'https://s3.us-east.cloud-object-storage.appdomain.cloud/vivek/Mouli.png',
    'Errett': 'https://s3.us-east.cloud-object-storage.appdomain.cloud/w251-hw3-hobbs-bucket-01/20190522-225405399.png',
    'Chi': 'https://s3.us-south.cloud-object-storage.appdomain.cloud/hw3-images/face1.png'
}
session = False

#Parameters
batch_size = 5 #Number of images to batch up
give_money = 0.7 #Threshold above which to dispense money
secondary_authentication = 0.2 # Threshold above which to ask for secondary authentication


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
        mqttclient.publish(STOP, qos=2, retain=False)
    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

def start(msg):
    global image_queue
    global user
    global session
    user = msg.payload
    if type(user) == bytes:
        user = user.decode('ASCII')
    if user not in known_images.keys():
        mqttclient.publish(USER_NOT_FOUND, payload=user,  qos=2, retain=False) 
        print('User', user, 'not found!')
    else:
        session = True
        mqttclient.publish(GO, qos=2, retain=False)
        image_queue = {}
        print ('Recevied ID message with user = ',user)

def queue (user, msg):
    global image_queue
    global session
    payload = msg.payload
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
            mqttclient.publish(STOP, qos=2, retain=False)
            print('Sending', user, 'for adjudication.')
            response = adjudicate(user, image_queue.pop(user))
            print('Received', response)
            mqttclient.publish(response, qos=2, retain=False)
        else:
            image_queue = {**image_queue, user:images}
            print('Image appended for', user)

def secondary_auth(user, msg):
    # Code to verify additional information. For now, just assume secondary authentication is successful
    if msg.payload == "money":
        mqttclient.publish(GIVE_MONEY, qos=2, retain=False)
    else:
        mqttclient.publish(SECONDARY_AUTH_DECLINE, payload="You entered an incorrect password", qos=2, retain=False)

def test_model():
    # if precision of class 'closed' or class 'open' is 0 from classification report, no blink is detected

    test_data_dir = 'data/test'
    img_width, img_height = 32, 32    
    nb_test_samples = 800 
    batch_size = 16

    # Rescale pixel values to be between 0 and 1
    datagen = ImageDataGenerator(rescale=1. / 255)

    # Generate test data from a directory
    generator = datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_width, img_height),
        color_mode='rgb',
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)

    # Instantiate the VGG16 model without its top layer. Run the test images
    # through this model and collect its outputs
    model = applications.VGG16(include_top=False, weights='imagenet', input_shape=(img_width,img_height,3))

    predTest = model.predict_generator(
        generator, nb_test_samples // batch_size)

    # Instantiate the output layers we added on top of the VGG16 bottlenecks
    model = Sequential()
    model.add(Flatten(input_shape=(1,1,512)))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    # Load the model weights we calculated for our network above
    model.load_weights(top_model_weights_path)

    # Predict classes for our test images
    predicted = model.predict_classes(predTest)

    # Sets class labels
    predClasses = np.array(
        [0] * int(nb_test_samples/2) + [1] * int(nb_test_samples/2))
    #print(classification_report(predClasses, predicted))

    # compare precision from both classes, if precision is 0 on either class, return False
    # else
    return True 

def adjudicate(user, images):
    print('Received',len(images), 'images')
    url = known_images.get(user)
    response = requests.get(url)
    known_image = face_recognition.load_image_file(BytesIO(response.content))
    known_image_encoding = face_recognition.face_encodings(known_image)[0]

    print('Starting blink detection')
    blink = test_model()

    matches = 0
    print('Starting loop for face recognition')
    for unknown_image in images:
        unknown_image_encoding = face_recognition.face_encodings(unknown_image)[0]
        result = face_recognition.compare_faces([known_image_encoding], unknown_image_encoding)
        print('Result is', result)
        matches += result[0]

    match_ratio = matches/batch_size
    print('Match Ratio is', match_ratio)
    if blink and match_ratio > give_money:
        return (GIVE_MONEY)
    elif match_ratio > secondary_authentication:
        return (SECONDARY_AUTH_REQUIRED)
    else:
        return (DECLINE)

# Connect to local mosquitto broker and subscribe to `local/#`
mqttclient = mqtt.Client('Adjudicator')
mqttclient.connect("mosquitto")
print("Client connect")
mqttclient.on_message = on_message
mqttclient.on_connect = on_connect

mqttclient.loop_forever()
