# 🗨️ MQTT Chat App in Python

This is a MQTT chat app in Python. It allows users to connect to the server, and send messages either via the server or in a direct message (DM) and also allows to send files from one user to the other

```bash
python3 -m venv chatapp_env
source chatapp_env/bin/activate
pip install -r requirements.txt
```

### 📁 File Structure

mqtt-chat/
├── server.py       # Central server managing registration and message routing
├── client.py       # Client application with CLI and messaging
└── README.md       # This file


### 🛠️ Setup & Usage
0. Install MQTT on Linux:
```bash
sudo apt-get update
sudo apt install net-tools
sudo apt install mosquitto mosquitto-clients
```

1. Start MQTT Broker
If using Mosquitto locally - in one terminal:
```bash
sudo mosquitto
```

2. Start the Server In another terminal:
```bash
python3 server.py OR ./server.py
```

3. Start Clients
In separate terminals:
```bash
python3 client.py OR client.py
``` 

Enter a unique username when prompted. Notice that if you provide a non-unique username, you will not be able to connect.


### 💬 Client Commands
username:message          # Send message from one user to another via the server
/get username		  # Send a request to the server to check if a user is connected
/dm username:message      # Direct message from a user to a user
/file user filepath       # Send file to user directly


#### 📎 Example Session
1. Start the server
```bash
python3 server.py
```

2. Start two clients
```bash
# Terminal 1
python3 client.py
# Enter: alice
```

```bash
# Terminal 2
python3 client.py
# Enter: bob
```

2. Alice checks if Bob is connected:
```bash
/get bob
```

3. Alice sends Bob a message
```bash
bob:hi!
```

4. Bob sends Alice a direct message
```bash
/dm alice:hiiiii!
```

5. Alice sends Bob a file
```bash
/file bob ./hello.txt
```
