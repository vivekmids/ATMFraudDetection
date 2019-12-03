import paho.mqtt.client as mqtt
import time

# This script takes incoming messages from a local mosquitto broker on the TX2
# and forwards them to a remote broker on my VSI



def on_message_local(client, userdata, msg):
    """After receiving a message, the local client will publish it to the remote
    client under the same topic
    """
    if msg.topic == "local/faces":
        print("'faces' message received!")
        remote_client.publish("local/faces", payload=msg.payload, qos=0, retain=False)
        print("'faces' message published to remote client", msg.payload)

    elif msg.topic == "local/response":
        print("'response' message received!")
        # Do I need to change to retain=True for qos=2?
        remote_client.publish("local/response", payload=msg.payload, qos=2, retain=False)
        print("'response' message published to remote client", msg.payload)

    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

#def on_message_responder(client, userdata, msg):

#    if msg.topic == "response":
#        print("'response' message received!")
        # Do I need to change to retain=True for qos=2?
#        remote_client.publish("response", payload=msg.payload, qos=2, retain=False)
#        print("'response' message published to remote client", msg.payload)

#    else:
#        print("Message with unspecificied topic received from responder client: ", msg.topic)
#        print("######  No action taken on message  ######")

def on_message_remote(client, userdata, msg):
    """
    """
    if msg.topic == "adjudication/pass":
        print("'adjudication/pass' message received!")
        local_client.publish("adjudication/pass", payload=msg.payload, qos=2, retain=False)
        # Do I need to change to retain=True for qos=2?
        print("'adjudication/pass' message published to local client", msg.payload)

    elif msg.topic == "adjudication/fail_face":
        # Published if face fails authentication
        print("'adjudication/fail_face' message received!")
        local_client.publish("adjudication/fail_face", payload=msg.payload, qos=2, retain=False)
        # Do I need to change to retain=True for qos=2?
        print("'adjudication/fail_face' message published to local client", msg.payload)

    elif msg.topic == "adjudication/fail_info":
        # Published if user fails authentication based on personal info
        print("'adjudication/fail_info' message received!")
        local_client.publish("adjudication/fail_info", payload=msg.payload, qos=2, retain=False)
        # Do I need to change to retain=True for qos=2?
        print("'adjudication/fail_info' message published to local client", msg.payload)

    else:
        print("Message with unspecificied topic received from remote client: ", msg.topic)
        print("######  No action taken on message  ######")

local_client = mqtt.Client("camera_to_forwarder")
local_client.connect("mosquitto")
print("Local client connect")
local_client.on_message = on_message_local
local_client.subscribe("local/#")
#local_client.subscribe("response")
print("Local client subscribe")

#responder_client = mqtt.Client("responder_to_cloud")
#responder_client.connect("mosquitto")
#print("Responder client connect")
#responder_client.on_message = on_message_responder
#local_client.subscribe("response")
#print("Responder client subscribe")

remote_client = mqtt.Client("forwarder_to_cloud")
remote_client.connect("169.62.97.69")
print("Remote client connect")
remote_client.on_message = on_message_remote
remote_client.subscribe("adjudication/#")
print("Remote client subscribe")


while True:



    local_client.loop_start()
    time.sleep(2)
    local_client.loop_stop()

    

#    responder_client.loop_start()
#    time.sleep(0.5)
#    responder_client.loop_stop()




    remote_client.loop_start()
    time.sleep(0.5)
    remote_client.loop_stop()


#local_client.loop_forever()
#remote_client.loop_forever() # Is this syntax at the end correct?
