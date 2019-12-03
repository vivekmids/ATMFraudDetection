import paho.mqtt.client as mqtt

# This script mimics adjudication traffic

# Instantiate a Paho MQTT client ('client')
client = mqtt.Client(client_id="adjudicator")
client.connect("mosquitto")

def on_message(client, userdata, msg):
    """Tells TX2 to start camera upon receiving a password. Mimics adjudication 
       behavior of actual `adjudication` container
    """

    if msg.topic == "local/ID":
        print("'ID' message received!")
        print("Payload: ", msg.payload)
        client.publish("adjudication/go", qos=2, retain=False)
        print("'go' message sent!")
        
    elif msg.topic == "local/faces_finished":
        print("'faces_finished' message received!")
        client.publish("adjudication/stop", qos=2, retain=False)
        print("'stop' message sent!")
        client.publish("adjudication/fail_face", qos=2, retain=False)

    elif msg.topic == "local/response":
        print("'response' message received!")
        
        if msg.payload == "money":
            client.publish("adjudication/pass", payload="Dispense money", qos=2, retain=False)

        else:
            client.publish("adjudication/terminate_info", payload="You entered an incorrect password", qos=2, retain=False)

    else:
        print("Message with unspecificied topic received from local client: ", msg.topic)
        print("######  No action taken on message  ######")

# Connect to local mosquitto broker and subscribe to `local/#`
client.connect("mosquitto")
print("Client connect")
client.on_message = on_message

client.subscribe("local/#")
print("Client subscribe")
    
client.loop_forever()
