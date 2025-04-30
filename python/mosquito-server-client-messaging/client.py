#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import readline # necessary to be able to delete when providing a command line input
import base64
import os
import time
import uuid
import signal
import sys

address_book = {}

BROKER = 'localhost'
PORT = 1883 # Default MQTT port

registered = False
username = ""
client_id = str(uuid.uuid4()) # Unique ID per client

def handle_exit_signal(_sig, _frame):
    if registered:
        disconnect_topic = f"chat/{username}/disconnect"
        print(f"\n👋 {username} is disconnecting...")
        client.publish(disconnect_topic, "DISCONNECT", qos=1)
        client.loop()
        time.sleep(1) 
        client.disconnect()

    sys.exit(0)

def on_connect(client, _userdata, _flags, _rc):  
    client.subscribe(f"chat/{username}/register_result/{client_id}") # User registration confirmation
    client.subscribe(f"chat/{username}/inbox") # Register to own inbox

    client.subscribe(f"chat/{username}/address_reply") # Reply of check if user exists
    client.subscribe(f"chat/{username}/address_reply_only") # Reply of check if user exists
    client.subscribe(f"chat/{username}/get_message") # Reply of check if user exists
    client.subscribe(f"chat/{username}/file") # File recieve registration
    client.subscribe(f"chat/{username}/dm") # direct messages

    client.publish(f"chat/{username}/register", client_id) # register

def on_message(_client, _userdata, msg):
    global registered
    topic = msg.topic

    if topic.endswith("inbox") or topic.endswith(f"register_result/{client_id}"):
        payload = msg.payload.decode()
        if payload.startswith("SUCCESS:"):
            print(f"\n✅ {payload}")
            registered = True
        elif payload.startswith("ERROR:"):
            print(f"\n❌ {payload}")
            if topic.endswith(f"register_result/{client_id}"):
                registered = False
        else:
            if topic.endswith("inbox"):
                print(f"\n📩 {payload}")

    elif topic.endswith("address_reply"):
        payload = msg.payload.decode()
        name, addr = payload.split(":", 1)
        if addr != "NOT_FOUND":
            address_book[name] = addr

    elif topic.endswith("address_reply_only"):
        payload = msg.payload.decode()
        message, addr = msg.payload.decode().split(":")
        if addr != "NOT_FOUND":
            name = message.split(" ")[0]
            address_book[name] = addr.replace(" ", "")
            print(f"\n✅ {payload}")

    elif topic.endswith("get_message"):
        payload = msg.payload.decode()
        print(f"\n✅ {payload}")

    elif topic.endswith("file"):
        try:
            header, b64_data = msg.payload.decode().split(":", 1)
            sender, filename = header.split(",", 1)
            data = base64.b64decode(b64_data)

            with open(f"received_{filename}", "wb") as f:
                f.write(data)
            print(f"\n📁 Received file '{filename}' from {sender}. Saved as 'received_{filename}'")
        except Exception as e:
            print(f"⚠️ Failed to receive file: {e}")

def wait_for_address(target, timeout=3):
    start_time = time.time()
    while target not in address_book:
        if time.time() - start_time > timeout:
            return False
        time.sleep(0.1)
    return True

def send_loop(client):
    while True:
        user_input = input("Enter [/command] username:message - ")

        if user_input.startswith("/dm "):
            try:
                target, message = user_input.split(" ", 1)[1].split(":", 1)
                client.publish(f"chat/{username}/get_address", target)

                if not wait_for_address(target):
                    print(f"📡 {target} is not currently connected.")
                else:
                    topic = address_book[target]
                    client.publish(topic, f"[DM from {username}] {message}")
                    print(f"✅ Direct message sent to {target}")
            except ValueError:
                print("⚠️ Use format: /dm username:message")

        elif user_input.startswith("/file "):
            try:
                parts = user_input.split(" ", 2)
                target = parts[1]
                filepath = parts[2]

                if not os.path.exists(filepath):
                    print(f"❌ File '{filepath}' not found.")
                    continue

                if target not in address_book:
                    print(f"📡 {target} is not currently connected.")
                    continue

                with open(filepath, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode()

                filename = os.path.basename(filepath)
                header = f"{username},{filename}"
                file_topic = f"chat/{target}/file"
                client.publish(file_topic, f"{header}:{b64_data}")
                print(f"📤 Sent file '{filename}' to {target}")

            except Exception as e:
                print(f"⚠️ Failed to send file: {e}")

        elif user_input.startswith("/get "):
            try:
                target = user_input.split(" ", 1)[1]
                client.publish(f"chat/{username}/get_address_only", target)
                if not wait_for_address(target):
                    print(f"📡 {target} is not currently connected.")
                else:
                    continue
            except Exception as e:
                print(f"⚠️ Use format: /get username")
        
        else:
            target, message = user_input.split(":")
            client.publish(f"chat/{username}/send_message", user_input)
   
            try:
                if not wait_for_address(target):
                    print(f"📡 {target} is not currently connected.")
                else:
                    topic = address_book[target]
            except ValueError:
                print("⚠️ Use format: username:message")


def setup_client():
    global client, username, registered
    while not registered:
        username = input("Enter your username: ")
        client = mqtt.Client(client_id=client_id)
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(BROKER, PORT)
        client.loop_start()
        time.sleep(2)  # Wait to receive registration result

        if not registered:
            client.loop_stop()
            print("🔁 Try a different username.\n")

signal.signal(signal.SIGINT, handle_exit_signal)
setup_client()
send_loop(client)