'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''
 # PJ:XT PYT_BPU_Tank

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

import logging
import time
import json

# Sub process
import subprocess
import platform

# Pi IO
import RPi.GPIO as GPIO
# Define GPIO to use on Pi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
IO_05_AL = 13 
IO_13_TB = 5

trMill = int(time.time())
tlMill = int(time.time())

GPIO.setup(IO_05_AL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IO_13_TB, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Stop Node-RED
# if platform.system() == "Windows":
#     node_red_path = r'C:\Users\peppe\AppData\Roaming\npm\node-red.cmd'
#     subprocess.call(['taskkill', '/F', '/IM', 'node-red'])
#     subprocess.Popen([node_red_path])
# if platform.system() == "Linux":
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

host = "a1x0dm3q26289z-ats.iot.ap-southeast-1.amazonaws.com"
rootCAPath = "/home/DEV01/AWS/certsP/AmazonRootCA1.pem"
certificatePath = "/home/DEV01/AWS/certsP/device.pem.crt"
privateKeyPath = "/home/DEV01/AWS/certsP/private.pem.key"

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
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

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
with open('/home/DEV01/AWS/A110_FAL.json', 'r') as file:
    json_data1 = json.load(file)
# print(json_data)
if __name__ == '__main__':
    try:
        Alarm = 0
        while True:
            time.sleep(1)
            temperature = get_cpu_temperature()-15
            if temperature is not None:
                #print(f"CPU Temperature: {temperature}°C")
                json_data1['devices'][0]['tags'][0]['value']= round(temperature,2)
            else:
                #print("Failed to read CPU temperature.")
                json_data1['devices'][0]['tags'][0]['value']=""

            if mode == 'both' or mode == 'publish':
                # print("################")
                # print(json_data1['devices'][0]['tags'][2])
                # print("################")
                trMill = int(time.time())
                if GPIO.input(IO_05_AL) == 0 and Alarm != 2:
                    Alarm = 1
                    json_data1['devices'][1]['tags'][2]['value']="Z1_DZ_1_FL1_LOBBY"
                else:
                    json_data1['devices'][1]['tags'][2]['value']=""
                if GPIO.input(IO_13_TB) == 0:
                    json_data1['devices'][1]['tags'][3]['value']="Trouble"
                else:
                    json_data1['devices'][1]['tags'][3]['value']=""

                if Alarm == 1:
                    Alarm = 2
                    messageJson1 = json.dumps(json_data1)
                    myAWSIoTMQTTClient.publishAsync(topic, messageJson1, 1)
                    print('Published topic %s: %s\n' % (topic, messageJson1))
                    print("11111111111111111111111111")
                    time.sleep(5)
                    tlMill = int(time.time())
                elif Alarm == 2 and GPIO.input(IO_05_AL) != 0:
                    json_data1['devices'][1]['tags'][2]['value']="Z1_DZ_1_FL1_LOBBY_Restore"
                    messageJson1 = json.dumps(json_data1)
                    myAWSIoTMQTTClient.publishAsync(topic, messageJson1, 1)
                    print('Published topic %s: %s\n' % (topic, messageJson1))
                    print("22222222222222222222222")
                    time.sleep(5)
                    tlMill = int(time.time())
                    json_data1['devices'][1]['tags'][2]['value']=""
                    Alarm = 3
                if (trMill-tlMill)>30:
                    if GPIO.input(IO_05_AL) == 0:
                        json_data1['devices'][1]['tags'][2]['value']="Z1_DZ_1_FL1_LOBBY"
                    else:
                        json_data1['devices'][1]['tags'][2]['value']=""
                    messageJson1 = json.dumps(json_data1)
                    myAWSIoTMQTTClient.publishAsync(topic, messageJson1, 1)
                    print("0000000000000000000000000")
                    tlMill = int(time.time())

                # if mode == 'publish':
                #     print('Published topic %s: %s\n' % (topic, messageJson1))
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     GPIO.cleanup()
    GPIO.cleanup()
