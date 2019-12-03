import paho.mqtt.client as mqtt


# This script takes adjudications from the cloud and mediates user inputs

# Instantiate a Paho MQTT client ('client') that connects to the local mosquiito
# broker on the TX2
client = mqtt.Client(client_id="responder")
client.connect("mosquitto")

def on_message(client, userdata, msg):
    """After receiving a message, the local client will publish it to the remote
    client under the same topic
    """
    if msg.topic == "adjudication/pass":
        print("'adjudication/pass' message received!")
        print("Money dispensed!")
        #break # Change in production so loop exits

    elif msg.topic == "adjudication/fail_face":
        print("'adjudication/fail_face' message received!")
        #verification = input("Facial recognition failed. Please answer the question below to authenticate your identity.\n\n", msg.payload)
        verification = "money"
        client.publish("local/response", payload=verification, qos=2, retain=False)
        print("Test...response sent")

    elif msg.topic == "adjudication/fail_info":
        print("'adjudication/fail_info' message received!")
        print("Facial recognition and identity check failed. We are unable to dispense money.")
        #break # Change in production so loop exits

    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")




client.connect("mosquitto")
print("Client connect")
client.on_message = on_message

client.subscribe("adjudication/#")
print("Client subscribe")
    

client.loop_forever() # Change in production so loop exits
