#######################################################################################
# Yourname: Jasmine Alysha Theseira
# Your student ID: 66070246
# Your GitHub Repo: https://github.com/jazzpu/IPA2024-Final.git

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import os
import time
import json
import requests
import restconf_final, netconf_final, netmiko_final, ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
print(os.getenv('WEBEX_ACCESS_TOKEN'))
ACCESS_TOKEN = os.getenv('WEBEX_ACCESS_TOKEN')

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.getenv('ROOM_ID')
MY_STUDENT_ID = os.getenv('STUDENT_ID')

current_method = None
VALID_IPS = ["10.0.15.61", "10.0.15.62", "10.0.15.63", "10.0.15.64", "10.0.15.65"]
PART1_COMMANDS = ["create", "delete", "enable", "disable", "status"]

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
        parts = message.split(" ")
        command_parts = parts[1:] #takes out the /<ID>

        responseMessage = ""
        ip_address_used = None
        command_used = None

    # Complete the logic for each command Restconf, netconf or create
        if len(command_parts) == 1:
            command = command_parts[0]
            command_used = command
            
            if command == "restconf":
                current_method = "restconf"
                responseMessage = "Ok: Restconf"
            elif command == "netconf":
                current_method = "netconf"
                responseMessage = "Ok: Netconf"
            elif command in PART1_COMMANDS:
                if current_method is None:
                    responseMessage = "Error: No Method specified"
                else:
                    responseMessage = "Error: No IP specified"
            # สมมติว่า gigabit_status และ showrun ก็ต้องการ IP เหมือนกัน
            # This handles /ID gigabit_status or /ID showrun (no IP)
            elif command == "gigabit_status" or command == "showrun":
                 responseMessage = "Error: No IP specified"
            # This handles /ID 10.0.15.61 (no command)
            elif command in VALID_IPS:
                responseMessage = "Error: No command found."
            else:
                responseMessage = "Error: No command or unknown command"

    # ตรวจสอบคำสั่งแบบ 2 ส่วนเช่น 10.0.15.61 create
        elif len(command_parts) == 2:
            ip_address = command_parts[0]
            command = command_parts[1]
            ip_address_used = ip_address # เก็บ IP ไว้ใช้
            command_used = command # เก็บ command ไว้ใช้

            if ip_address not in VALID_IPS:
                responseMessage = f"Error: Invalid IP address {ip_address}"
            
            # คำสั่งกลุ่ม 1 (Restconf/Netconf)
            elif command in PART1_COMMANDS:
                if current_method is None:
                    responseMessage = "Error: No method specified"
                elif current_method == "restconf":
                    # เราต้องไปแก้ function ใน restconf_final ให้รับ ip_address
                    func = getattr(restconf_final, command)
                    responseMessage = func(ip_address)
                elif current_method == "netconf":
                    # เราต้องไปแก้ function ใน netconf_final ให้รับ ip_address
                    func = getattr(netconf_final, command)
                    responseMessage = func(ip_address)

            # คำสั่งกลุ่ม 2 (Netmiko)
            elif command == "gigabit_status":
                # เราต้องไปแก้ function ใน netmiko_final ให้รับ ip_address
                responseMessage = netmiko_final.gigabit_status(ip_address)
            
            # คำสั่งกลุ่ม 3 (Ansible)
            elif command == "showrun":
                # เราต้องไปแก้ function ใน ansible_final ให้รับ ip_address
                responseMessage = ansible_final.showrun(ip_address)
                # filename = f"show_run_66070246_{ip_address_used}.txt"
            
            else:
                responseMessage = "Error: No command or unknown command"

    # กรณีอื่นๆ
        else:
            responseMessage = "Error: Invalid command format"

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
            filename = f"show_run_66070246_{ip_address_used}.txt"
            try:
                # Open the file in binary read mode
                fileobject = open(filename, "rb")

                # Use MultipartEncoder to package the file and text together
                postData = MultipartEncoder({
                    "roomId": roomIdToGetMessages,
                    "text": f"Show running config from {ip_address_used}",
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