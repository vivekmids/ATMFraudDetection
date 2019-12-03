import cv2
import paho.mqtt.client as mqtt
import numpy
import sys
import time

# This script captures images from a USB camera, employs a Haar Feature-based 
# Cascade Classifier to detect faces, and then publishes any faces it detects
# to the MQTT topic "faces"

#def image_to_byte_array(image):
#   imgByteIO = io.BytesIO()
#   image.save(imgByteIO, format=image.format)
#   imgByteArr = imgByteIO.getvalue()
#   return imgByteArr

GO = False
STOP = False

def on_message(client, userdata, msg):
    """Turns camera on and off in response to instructions from the 
       `adjudicator` container
    """

    global GO
    global STOP

    if msg.topic == "adjudication/go":
        print("Start camera.")
        print(GO)
        GO = True
        print("GO set to ")
        print GO

    elif msg.topic == "adjudication/stop":
        print("Stopping camera. Adjudicator does not need any more pictures.")
        #print(GO)
        #GO = False
        #print("GO set to ")
        #print GO
        STOP = True
        #sys.exit()

    else:
        print("Message with unspecificied topic received from remote client: ", msg.topic)
        print("######  No action taken on message  ######")


# Instantiate a Paho MQTT client ('client') that connects to the local mosquiito
# broker on the TX2
client = mqtt.Client(client_id="camera")
client.connect("mosquitto")
print("Client connect")
client.on_message = on_message
client.subscribe("adjudication/#")
print("Client subscribe")


# Mimics input of account information. Publishes as username to `local/ID` topic
# NOTE: Used 'raw_input', so it works in Python 2!!!
#account = raw_input("Please enter your ID: ").strip(" ")
#print("You entered: ", account)
#client.publish("local/ID", payload=account)

#client.loop_start()
#time.sleep(0.1)
#print("First loop started")
#client.loop_stop()

while True:
    
    if GO == True:

        # Sets facial recognition model
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Capture video from my USB camera
        cap = cv2.VideoCapture(1)

        ret, frame = cap.read()

        for i in range(50):
            # Capture images frame-by-frame
            ret, frame = cap.read()

            if ret == True:
        
                # Detect faces
                faces = face_cascade.detectMultiScale(frame, 1.3, 5)

                # Encode each detected face as a .png and publish to MQTT topic "faces"
                for (x,y,w,h) in faces:
          
                    rc, jpg = cv2.imencode('.png', frame[y:y+h,x:x+w])
                    msg = jpg.tobytes() # See if we need to use the function above instead

                    client.publish("local/faces", payload=msg)
                    print("picture published!")
        # Stop taking pictures and let the adjudicator know we're finished
        GO = False
        print("GO = ", GO)
        client.publish("local/faces_finished", qos=2)
        #break
        #sys.exit()
    elif STOP == True:
        break

    client.loop_start()
    
    client.loop_stop()
    
    
#sys.exit()

#client.loop_forever()

