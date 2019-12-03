import cv2
import paho.mqtt.client as mqtt
import numpy

# This script captures images from a USB camera, employs a Haar Feature-based 
# Cascade Classifier to detect faces, and then publishes any faces it detects
# to the MQTT topic "faces"

# Instantiate a Paho MQTT client ('client') that connects to the local mosquiito
# broker on the TX2
client = mqtt.Client(client_id="camera")
client.connect("mosquitto")

# Sets facial recognition model
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Capture video from my USB camera
cap = cv2.VideoCapture(1)

# Use counter so we only send a limited number of photos
k = 0

print("Start publish")
client.publish("local/faces", payload="test again")
print("End publish")

#while True:
#    print("Start publish")
#    client.publish("local/faces", payload="why not work?")
#    print("End publish")

while True:
    # Capture images frame-by-frame
    ret, frame = cap.read()
    k += 1

    if ret == True:
        
        # Detect faces
        faces = face_cascade.detectMultiScale(frame, 1.3, 5)

        # Encode each detected face as a .png and publish to MQTT topic "faces"
        for (x,y,w,h) in faces:
          
            rc, jpg = cv2.imencode('.png', frame[y:y+h,x:x+w])
            msg = jpg.tobytes()

            client.publish("local/faces", payload=msg)

client.loop_forever()

