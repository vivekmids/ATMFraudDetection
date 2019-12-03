import paho.mqtt.client as mqtt


# This script mimics adjudication traffic

# Instantiate a Paho MQTT client ('client') that connects to the local mosquiito
# broker on the TX2
client = mqtt.Client(client_id="adjudicator")
client.connect("mosquitto")

def on_message(client, userdata, msg):
    """After receiving a message, the local client will publish it to the remote
    client under the same topic
    """
    if msg.topic == "response":
        print("'response' message received!")
        
        if msg.payload == "money":
            client.publish("adjudication/pass", payload="Dispense money", qos=2, retain=False)

        elif msg.payload == "poor":
            client.publish("adjudication/fail_info", payload="Contact your bank", qos=2, retain=False)

        else:
            client.publish("adjudication/fail_info", payload="Something else went wrong", qos=2, retain=False)

        #break # Change in production so loop exits


    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

# Test publications
client.publish("adjudication/pass", payload="Test pass", qos=2, retain=False)
client.publish("adjudication/fail_info", payload="Test fail info", qos=2, retain=False)
client.publish("adjudication/fail_face", payload="Test fail face", qos=2, retain=False)

while True:

    client.connect("mosquitto")
    print("Client connect")
    client.on_message = on_message

    client.subscribe("adjudication")
    print("Client subscribe")
    

client.loop_forever() # Change in production so loop exits
