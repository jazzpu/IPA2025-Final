#######################################################################################
# Yourname: Jasmine Alysha Theseira
# Your student ID: 66070246
# Your GitHub Repo: https://github.com/jazzpu/IPA2024-Final.git

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import os
# from dotenv import load_dotenv <---- Import this if you want to use .env file!
import time
import json
import requests
import restconf_final, netmiko_final, ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder

# load_dotenv() for using dotenv

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
print(os.getenv('WEBEX_ACCESS_TOKEN'))
ACCESS_TOKEN = os.getenv('WEBEX_ACCESS_TOKEN')

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.getenv('ROOM_ID')
MY_STUDENT_ID = os.getenv('STUDENT_ID')

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith(f"/{MY_STUDENT_ID}"):

        # extract the command
        command = message.split(" ")[1]
        print(f"Executing command: {command}")
        responseMessage=""

# 5. Complete the logic for each command

        if command == "create":
            responseMessage = restconf_final.create()
        elif command == "delete":
            responseMessage = restconf_final.delete()
        elif command == "enable":
            responseMessage = restconf_final.enable()
        elif command == "disable":
            responseMessage = restconf_final.disable()
        elif command == "status":
            responseMessage = restconf_final.status()
        elif command == "gigabit_status":
            responseMessage = netmiko_final.gigabit_status()
        elif command == "showrun":
            responseMessage = ansible_final.showrun()
        else:
            responseMessage = "Error: No command or unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail
        # Decide what to do based on the command and the response from the module
        if command == "showrun" and responseMessage == "ok":
            # This block handles sending the backup file
            filename = "show_run_66070246_R1-Exam.txt"
            try:
                # Open the file in binary read mode
                fileobject = open(filename, "rb")

                # Use MultipartEncoder to package the file and text together
                postData = MultipartEncoder({
                    "roomId": roomIdToGetMessages,
                    "text": "Show running config from R1-Exam",
                    "files": (filename, fileobject, "text/plain"),
                })

                # The Content-Type header MUST come from the encoder
                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": postData.content_type,
                }
                
                # Send the single, correctly formatted request
                r = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=postData,
                    headers=HTTPHeaders
                )

            except FileNotFoundError:
                print(f"ERROR: Could not find the file {filename} to send.")
                # If the file is missing, send an error message instead
                postData = {"roomId": roomIdToGetMessages, "text": "Error: Playbook ran, but the backup file was not found."}
                HTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
                r = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=json.dumps(postData),
                    headers=HTTPHeaders
                )

        else:
            # For all other commands, just send a simple text message
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=json.dumps(postData),
                headers=HTTPHeaders,
            )

        # Check the status of the one request that was sent
        if not r.status_code == 200:
            raise Exception(
                f"Incorrect reply from Webex Teams API. Status code: {r.status_code}"
            )