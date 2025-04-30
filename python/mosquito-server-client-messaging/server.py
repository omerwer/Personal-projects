#!/usr/bin/env python3

import paho.mqtt.client as mqtt

BROKER = 'localhost'
PORT = 1883 # Default MQTT port

connected_clients = {}

def on_connect(client, _userdata, _flags, _rc):
    print("Server connected to broker.")
    client.subscribe("chat/+/register")
    client.subscribe("chat/+/get_address")
    client.subscribe("chat/+/get_address_only")
    client.subscribe("chat/+/send_message")
    client.subscribe("chat/+/disconnect")

def on_message(client, _userdata, msg):
    print(f"📨 Server received: {msg.topic}, Payload = {msg.payload.decode()}")
    topic_parts = msg.topic.split("/")
    username = topic_parts[1]
    action = topic_parts[2]

    if action == "register":
        client_id = msg.payload.decode()
        result_topic = f"chat/{username}/register_result/{client_id}"

        if username in connected_clients:
            print(f"Username {username} is already connected. Rejecting client {client_id}")
            client.publish(result_topic, f"ERROR: Username {username} already connected.")
        else:
            connected_clients[username] = f"chat/{username}/inbox"
            client.publish(result_topic, f"SUCCESS: Registered as {username} with ID {client_id}")

    elif action == "get_address":
        target_username = msg.payload.decode()
        reply_topic = f"chat/{username}/address_reply"
        if target_username in connected_clients:
            address = connected_clients[target_username]
            client.publish(reply_topic, f"{target_username}:{address}")
            client.publish(reply_topic, f"{username}:{address}")
        else:
            client.publish(reply_topic, f"{target_username}:NOT_FOUND")

    elif action == "get_address_only":
        target_username = msg.payload.decode()
        reply_topic = f"chat/{username}/address_reply_only"
        if target_username in connected_clients:
            address = connected_clients[target_username]
            client.publish(reply_topic, f"{target_username} address is: {address}")
        else:
            client.publish(reply_topic, f"{target_username}:NOT_FOUND")

    elif action == "send_message":
        target_username, message = msg.payload.decode().split(":")
        reply_topic = f"chat/{username}/get_message"
        if target_username in connected_clients:
            address = connected_clients[target_username]
            reply_target_topic = f"chat/{target_username}/get_message"
            client.publish(reply_target_topic, f"[Via server] {username}:{message}")
            client.publish(reply_topic, f"Message was sent to {target_username} via the server successfully.")
        else:
            client.publish(reply_topic, f"{target_username}:NOT_FOUND")

    elif action == "disconnect":
        if username in connected_clients:
            print(f"❌ {username} disconnected.")
            del connected_clients[username]
        else:
            print(f"⚠️ Received disconnect from unknown user: {username}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)
client.loop_forever()