import paho.mqtt.client as mqtt
import time

# This script takes incoming messages from a local mosquitto broker on the TX2
# and forwards them to a remote broker on my VSI

# NEED TO CHANGE IP ADDRESS IF WE USE ANOTHER VSI!!!

def on_message_local(client, userdata, msg):
    """Forwards messages from the local `face_detector` and `responder` 
       containers
    """
    if msg.topic == "local/ID":
        print("'ID' message received!")
        remote_client.publish("local/ID", payload=msg.payload, qos=2, retain=False)
        print("'ID' message published to remote client", msg.payload)

    elif msg.topic == "local/faces":
        print("'faces' message received!")
        remote_client.publish("local/faces", payload=msg.payload, qos=0, retain=False)
        print("'faces' message published to remote client", msg.payload)

    elif msg.topic == "local/response":
        print("'response' message received!")
        remote_client.publish("local/response", payload=msg.payload, qos=2, retain=False)
        print("'response' message published to remote client", msg.payload)

    elif msg.topic == "local/faces_finished":
        print("'faces_finished' message received!")
        remote_client.publish("local/faces_finished", payload=msg.payload, qos=2, retain=False)
        print("'faces_finished' message published to remote client", msg.payload)
    
    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

def on_message_remote(client, userdata, msg):
    """Forwards messages from remote client that indicate if user passed facial
       recognition or identity challenge
    """

    if msg.topic == "adjudication/go":
        print("'adjudication/go' message received!")
        local_client.publish("adjudication/go", payload=msg.payload, qos=2, retain=False)
        print("'adjudication/go' message published to local client", msg.payload)

    elif msg.topic == "adjudication/stop":
        print("'adjudication/stop' message received!")
        local_client.publish("adjudication/stop", payload=msg.payload, qos=2, retain=False)
        print("'adjudication/stop' message published to local client", msg.payload)

    elif msg.topic == "adjudication/pass":
        print("'adjudication/pass' message received!")
        local_client.publish("adjudication/pass", payload=msg.payload, qos=2, retain=False)
        print("'adjudication/pass' message published to local client", msg.payload)

    elif msg.topic == "adjudication/fail_face":
        # Published if face fails authentication
        print("'adjudication/fail_face' message received!")
        local_client.publish("adjudication/fail_face", payload=msg.payload, qos=2, retain=False)
        print("'adjudication/fail_face' message published to local client", msg.payload)

    elif msg.topic == "adjudication/terminate_face":
        # Published if user completely fails face recognition
        print("'adjudication/terminate_face' message received!")
        local_client.publish("adjudication/terminate_face", payload=msg.payload, qos=2, retain=False)
        print("'adjudication/terminate_face' message published to local client", msg.payload)

    elif msg.topic == "adjudication/terminate_info":
        # Published if user fails authentication based on personal info
        print("'adjudication/terminate_info' message received!")
        local_client.publish("adjudication/terminate_info", payload=msg.payload, qos=2, retain=False)
        print("'adjudication/terminate_info' message published to local client", msg.payload)

    else:
        print("Message with unspecificied topic received from remote client: ", msg.topic)
        print("######  No action taken on message  ######")

# Instantiates a client that connects to the local mosquitto broker
local_client = mqtt.Client("camera_to_forwarder")
local_client.connect("mosquitto")
print("Local client connect")
local_client.on_message = on_message_local
local_client.subscribe("local/#")
print("Local client subscribe")

# Instantiates a client that connects to the remote mosquitto broker
# NEED TO CHANGE IP ADDRESS IF WE USE ANOTHER VSI!!!
remote_client = mqtt.Client("forwarder_to_cloud")
remote_client.connect("169.62.97.69")
print("Remote client connect")
remote_client.on_message = on_message_remote
remote_client.subscribe("adjudication/#")
print("Remote client subscribe")

# This infinite loop cycles between dealing with traffic blocked on the local 
# and remote clients. The images are potentially larger messages and could take
# more time to pass, so we use `time.sleep(2)` to keep this channel open for
# a longer amount of time in each loop
while True:

    local_client.loop_start()
    time.sleep(2)
    local_client.loop_stop()

    remote_client.loop_start()
    time.sleep(0.5)
    remote_client.loop_stop()
