from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

import logging
import time
import json

# Sub process
import subprocess
import urllib.request

# log
import csv
import datetime
from sys import platform

# MSteam
import pymsteams
myTeamsMessage = pymsteams.connectorcard("https://sansirimail.webhook.office.com/webhookb2/c0b64c0c-8a5c-4061-831a-661626c3166a@875bdd0a-688b-41d2-96b7-454d280043aa/IncomingWebhook/47afcadebbec4e499c52a9a7eadee573/13125d96-3d9c-4fc4-81f7-59eeaa397b8d")

if platform == "Windows":
    print("Windows")

if platform == "Linux":
    # Pi IO
    import RPi.GPIO as GPIO
    # Define GPIO to use on Pi
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    IO_05_AL = 13 
    IO_13_TB = 5

    GPIO.setup(IO_05_AL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(IO_13_TB, GPIO.IN, pull_up_down=GPIO.PUD_UP)

trMill = int(time.time())
tlMill = int(time.time())

# Stop Node-RED
# if platform == "Windows":
#     node_red_path = r'C:\Users\peppe\AppData\Roaming\npm\node-red.cmd'
#     subprocess.call(['taskkill', '/F', '/IM', 'node-red'])
#     subprocess.Popen([node_red_path])
# if platform == "Linux":
#     subprocess.call(['killall', 'node-red'])
#     subprocess.Popen(['node-red'])

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# host = "aquiml1rupuga-ats.iot.ap-southeast-1.amazonaws.com"
# rootCAPath = "certs/AmazonRootCA1.pem"
# certificatePath = "certs/device.pem.crt"
# privateKeyPath = "certs/private.pem.key"

# host = "a1x0dm3q26289z-ats.iot.ap-southeast-1.amazonaws.com"
# rootCAPath = "/home/DEV01/A110/certsP/AmazonRootCA1.pem"
# certificatePath = "/home/DEV01/A110/certsP/device.pem.crt"
# privateKeyPath = "/home/DEV01/A110/certsP/private.pem.key"

host = "a1x0dm3q26289z-ats.iot.ap-southeast-1.amazonaws.com"
rootCAPath = "certsP/AmazonRootCA1.pem"
certificatePath = "certsP/device.pem.crt"
privateKeyPath = "certsP/private.pem.key"

port = 8883
useWebsocket = False
clientId = "LIV24"
topic = "iot/firealarm"

if not useWebsocket and (not certificatePath or not privateKeyPath):
    print("Missing credentials for authentication.")
    exit(2)

# Port defaults
if useWebsocket and not port:  # When no port override for WebSocket, default to 443
    port = 443
if not useWebsocket and not port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(20)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(10)  # 5 sec

# Connect and subscribe to AWS IoT
mode = 'publish'
myAWSIoTMQTTClient.connect()
if mode == 'both' or mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

def get_cpu_temperature():
    try:
        result = subprocess.check_output(["vcgencmd", "measure_temp"])
        temperature_str = result.decode("utf-8")
        temperature = float(temperature_str.split("=")[1].split("'")[0])
        return temperature
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Publish to the same topic in a loop forever
# Read data from JSON file
with open('VTGM_FAL.json', 'r') as file:
    json_data1 = json.load(file)

if __name__ == '__main__':
    while True:
        try:
            Alarm = 0
            def connect(host='http://google.com'):
                try:
                    urllib.request.urlopen(host) #Python 3.x
                    return True
                except:
                    return False
            # Function to log the current timestamp
            def log_timestamp():
                current_time = datetime.datetime.now()
                return current_time.strftime("%Y-%m-%d %H:%M:%S")
            # Create a list to store log data
            log_data = []

            # Generate log data (you can do this whenever you want to log data)
            log_data.append(log_timestamp())

            # CSV filename
            csv_filename = "timestamps.csv"

            # Check if the file already exists
            file_exists = True
            try:
                with open(csv_filename, "r") as file:
                    reader = csv.reader(file)
                    if not list(reader):
                        file_exists = False
            except FileNotFoundError:
                file_exists = False

            # If the file doesn't exist, create it with a header row
            if not file_exists:
                with open(csv_filename, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    ft_raw = ["Timestamp","ping","alarm","trouble"]
                    writer.writerow(ft_raw)  # Header row

            while connect():
                time.sleep(1)
                
                json_data1['devices'][0]['tags'][0]['value']= 15
                
                json_data1['devices'][1]['tags'][2]['value']="Z1_DZ_1_FL1_TB"
                messageJson1 = json.dumps(json_data1)
                myAWSIoTMQTTClient.publish(topic, messageJson1, 0)
                print('Published topic %s: %s\n' % (topic, messageJson1))

                time.sleep(30)
                
                json_data1['devices'][1]['tags'][2]['value']="Z1_DZ_1_FL1_TB"
                messageJson1 = json.dumps(json_data1)
                myAWSIoTMQTTClient.publish(topic, messageJson1, 0)
                print('Published topic %s: %s\n' % (topic, messageJson1))

                #DATA to Msteam
                myTeamsMessage.text("ALERT "+json_data1['gateway'])
                myTeamsMessage.send()
                
                time.sleep(30)
                    # if mode == 'publish':
                    #     print('Published topic %s: %s\n' % (topic, messageJson1))
            # Reset by pressing CTRL + C
            time.sleep(30)
            # Append log data to the CSV file
            # log_data.append(connect())
            # log_data.append(json_data1['devices'][1]['tags'][2]['value'])
            # log_data.append(json_data1['devices'][1]['tags'][3]['value'])
            # with open(csv_filename, mode="a", newline="") as file:
            #     writer = csv.writer(file)
            #     writer.writerow(log_data)
        except KeyboardInterrupt:
            print("Measurement stopped by User")
            # GPIO.cleanup()
        except Exception as e:
            print(f"An exception occurred: {str(e)}")
            pass
