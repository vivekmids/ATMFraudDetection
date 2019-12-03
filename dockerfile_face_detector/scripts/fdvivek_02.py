import cv2
import paho.mqtt.client as mqtt
import numpy
import sys
import time

# This script captures images from a USB camera, employs a Haar Feature-based 
# Cascade Classifier to detect faces, and then publishes any faces it detects
# to the MQTT topic "faces"

# See if Vivek needs us to use this function later
#def image_to_byte_array(image):
#   imgByteIO = io.BytesIO()
#   image.save(imgByteIO, format=image.format)
#   imgByteArr = imgByteIO.getvalue()
#   return imgByteArr

# Used to turn the camera on and off
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
        #print GO

    elif msg.topic == "adjudication/stop":
        print("Stopping camera. Adjudicator does not need any more pictures.")
        STOP = True

    elif msg.topic == "adjudication/usernotfound":
        print("Stopping camera. User not present in database.")
        STOP = True

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


while True:
    
    if GO == True:
    
        # Sets facial recognition model
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Capture video from my USB camera
        cap = cv2.VideoCapture(1)

        ret, frame = cap.read()

        k = 0
        
        while k <= 50:
        #for i in range(50):
            # Capture images frame-by-frame
            ret, frame = cap.read()

            if ret == True:
            #Added by Vivek. Convert from BGR to RGB
                frame = frame[:,:,::-1]
            #End of added by Vivek
        
                # Detect faces
                faces = face_cascade.detectMultiScale(frame, 1.3, 5)

                # Encode each detected face as a .png and publish to MQTT topic "faces"
                for (x,y,w,h) in faces:
          
                    rc, jpg = cv2.imencode('.png', frame[y:y+h,x:x+w])

                    #Added by Vivek. Convert from BGR to RGB
                    frame = frame[:,:,::-1]
                    #End of added by Vivek
                    msg = jpg.tobytes() # See if we need to use the function above instead

                    client.publish("local/faces", payload=msg)
                    print("picture published!")
                    k += 1

        # Stop taking pictures and let the adjudicator know we're finished
        GO = False
        print("GO = ", GO)
        client.publish("local/faces_finished", qos=2)

    elif STOP == True:
        break

    client.loop_start()
    
    client.loop_stop()

