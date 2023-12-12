# emqx-kafka-mongo-messaging-app
The purpose this document is to use kafka for processing large amounts of data efficiently from IOT devices. But the challenge is, kafka was not designed for IOT devices. Hence integration of EMQX which uses mqtt lightweight protocol in conjunction with kafka can elevate wide range of opportunites to process the data in real-time.

Time sensitive application can largely benifit from this stack.

## Introduction
### EMQX
EMQX is an open-source, highly scalable, and feature-rich MQTT broker designed for IoT and real-time messaging applications. It supports up to 100 million concurrent IoT device connections per cluster while maintaining a throughput of 1 million messages per second and a millisecond latency.

EMQX supports various protocols, including MQTT (3.1, 3.1.1, and 5.0), HTTP, QUIC, and WebSocket. It also provides secure bi-directional communication with MQTT over TLS/SSL and various authentication mechanisms, ensuring reliable and efficient communication infrastructure for IoT devices and applications.

### KAFKA
Apache Kafka is a widely used open-source distributed event streaming platform that can handle the real-time transfer of data streams between applications and systems. However, Kafka is not built for edge IoT communication and Kafka clients require a stable network connection and more hardware resources. In the IoT realm, data generated from devices and applications are transmitted using the lightweight MQTT protocol. EMQX’s integration with Kafka/Confluent enables users to stream MQTT data seamlessly into or from Kafka. MQTT data streams are ingested into Kafka topics, ensuring real-time processing, storage, and analytics. Conversely, Kafka topics data can be consumed by MQTT devices, enabling timely actions.

In this article we are going to achieve the below architecture.

![emqx-kafka](images/emqx-kafka.jpg)

## Setting up EMQX
1) Docker is very handy tool when we want to setup the emqx server on the local machine. It can eliminate lot of choas and lets to run the emqx server setup with just 2 command like below,

```docker
docker pull emqx/emqx
docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 8084:8084 -p 8883:8883 -p 18083:18083 emqx/emqx
```

2) We can also use docker desktop in the windows machine to pull and run the emqx docker image.

![emqx-windows-docker](images/emqx/emqx-windows.png)

2) Once you run the docker image, you should be able to see the logs that contains the details about ports on which emqx services are running. In EMQX, listener is configured to receive requests from MQTT clients. EMQX supports the following message transfer protocols, including:
    - TCP: port 1883
    - SSL: port 8883
    - Websocket listener: 8083
    - Secure websocket listener: 8084
    - For UI Dashboard: 18083
 
![running emqx docker](images/emqx/running-emqx-docker.png)

3) In EMQX, Dashboard is a web-based graphic interface to manage and monitor EMQX and connected devices in real time.
 Access the endpoint `<ipaddress>:18083`

![webpage](images/emqx/webpage.png)

4) Login into the dashboard using default credentials.
    username: admin
    password: public

    when you login for the first time, it will prompt you to reset the password. Once we reset the password, it will redirect you to dashboard of emqx.

![dashboard](images/emqx/dashboard.png)

## Create emqx publisher/subscriber files using python programming

1) This article mainly introduces how to use the paho-mqtt client and implement connection, subscribe, messaging, and other functions between the MQTT client and MQTT broker, in the Python project.

2) Install the Paho Mqtt Client
    `pip3 install paho-mqtt`

3) Create a emqx python publisher.
```
from paho.mqtt import client as mqtt_client
import random
import logging
import time

# Create an MQTT Connection
broker      = '192.168.48.1'
port        = 1883
topic       = "python/mqtt"
client_id   = f'python-mqtt-{random.randint(0, 1000)}'
username    = "admin"
password    = "public"

# Auto reconnect for reliable connection
FIRST_RECONNECT_DELAY   = 1
RECONNECT_RATE          = 2
MAX_RECONNECT_COUNT     = 12
MAX_RECONNECT_DELAY     = 60

# on_connect callback function for connecting the broker.
# This function is called after client call has successfully connected.

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    
    def on_disconnect(client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)
        
            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

    # Set connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    client.on_disconnect = on_disconnect
    return client

# publisher code
def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 5:
            break

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_forever()

if __name__ == "__main__":
    run()
        
```

4) Create a emqx python subscriber.
```
import random
from paho.mqtt import client as mqtt_client

# Create an MQTT Connection
broker      = '192.168.48.1'
port        = 1883
topic       = "python/mqtt"
client_id   = f'subscribe-{random.randint(0, 1000)}'
username    = "admin"
password    = "public"

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == "__main__":
    run()
```

> **_NOTE:_** These both the files are very basic. The publisher will send 5 message and then will stop. The subscriber will go into infinite loop for receiving messages from publisher. Feel free to tweak publisher logic to continuosly send the messages by removing below block in it.
```
msg_count += 1
    if msg_count > 5:
        break
```

5) Execute the subscriber program in one terminal session and then run the publisher program in another session. you should be able to see something like below,

![emqx execution](images/emqx/execution-emqx.png)

## Setting up KAFKA

The below diagram shows a high level overview of what Kafka is for beginners. (there's lot more to Kafka, like Zookeeper, Consumer Groups, Partitions, etc. but we'll leave that for another time.)

![kafka setup](images/kafka/kafka-setup.png)

Kafka categorizes data into topics. A topic is a category or feed name to which records are published.


Producers publish messages to a specific topic. The messages can be in any format, with JSON and Avro being popular options. For example, a social media platform might use a producer to publish messages to a topic called posts whenever a user creates a post.


Consumers subscribe to a topic to consume the records published by producers. In the social media example, there might be a consumer set up to consume the posts topic to perform safety checks on the post before it is published to the global feed, and another consumer may asynchronously send notifications to the user's followers.