import paho.mqtt.client as mqtt
import sys

# This script responds to adjudications from the cloud

# Instantiate a Paho MQTT client ('client')
client = mqtt.Client(client_id="responder")
client.connect("mosquitto")
print("Client connect")

def on_message(client, userdata, msg):
    """Prints a `pass` message to indicate if a user passed face authentication
       or a subsequent identity challenge. 

       Returns a response with the user password if face authentication fails.

       Prints a `fail` message if the user fails face and/or identity
       authentication.
    """
    if msg.topic == "adjudication/pass":
        print("'adjudication/pass' message received!")
        print("Money dispensed!")
        sys.exit()

    elif msg.topic == "adjudication/fail_face":
        print("'adjudication/fail_face' message received!")
        verification = raw_input("Facial recognition failed. Please enter your password to authenticate your identity: ")
        client.publish("local/response", payload=verification, qos=2, retain=False)
        print("Test...response sent")

    elif msg.topic == "adjudication/terminate_face": # changed from fail info
        print("'adjudication/terminate_face' message received!")
        print("Facial recognition failed. We are unable to dispense money.")
        sys.exit()

    elif msg.topic == "adjudication/terminate_info": # changed from fail info
        print("'adjudication/terminate_info' message received!")
        print("Facial recognition was marginal and identity verification failed. We are unable to dispense money.")
        sys.exit()

    elif msg.topic == "adjudication/usernotfound":
        print("'adjudication/usernotfound' message received!")
        print("User is not in database. We are unable to dispense money.")
        sys.exit() 

    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

# Connects to local mosquitto broker and subscribes to `adjudication/#` messages
client.on_message = on_message

client.subscribe("adjudication/#")
print("Client subscribe")

# Mimics input of account information. Publishes as username to `local/ID` topic
# NOTE: Used 'raw_input', so it works in Python 2!!!
account = raw_input("Please enter your ID: ").strip(" ")
print("You entered: ", account)
client.publish("local/ID", payload=account)    

client.loop_forever()
