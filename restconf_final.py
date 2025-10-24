import json
import requests
requests.packages.urllib3.disable_warnings()
import os

STUDENT_ID = os.getenv("STUDENT_ID")
LOOPBACK_ID = f"Loopback{STUDENT_ID}"

# api_url = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces/interface={LOOPBACK_ID}"
# operational_url = f"https://{ROUTER_IP}/restconf/data/ietf-interfaces:interfaces-state/interface={LOOPBACK_ID}"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


def create(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface={LOOPBACK_ID}"

    yangConfig ={
        "ietf-interfaces:interface": {
            "name": LOOPBACK_ID,
            "description": "Configured by RESTCONF",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": "172.3.25.1", # Calculated from student ID
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }

    resp = requests.put(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Hallelujah, You successfully created Interface {LOOPBACK_ID} !"
    else:
        print('Yikes, looks like it failed. Status Code: {}'.format(resp.status_code))
        return f"Error creating interface: {resp.text}"


def delete(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface={LOOPBACK_ID}"
   
    resp = requests.delete(
        api_url, 
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Yay! successfully deleted Interface {LOOPBACK_ID}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot delete: Interface {LOOPBACK_ID}"


def enable(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface={LOOPBACK_ID}"

    yangConfig = yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": True
        }
    }

    resp = requests.patch(
        api_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {LOOPBACK_ID} is enabled successfully :D"
    else:
        print(f'Error. Status Code: {resp.status_code}')
        return f"Cannot enable: Interface {LOOPBACK_ID}"


def disable(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface={LOOPBACK_ID}"

    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": False
        }
    }

    resp = requests.patch(
        api_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface {LOOPBACK_ID} is now down :P"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot shutdown: Interface {LOOPBACK_ID}"


def status(ip_address):
    operational_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces-state/interface={LOOPBACK_ID}"
    
    resp = requests.get(
        operational_url,
        auth=basicauth,
        headers=headers,
        verify=False
    )

    if resp.status_code == 200:
        print(f"STATUS OK: {resp.status_code}")
        response_json = resp.json()
        # Extract the status from the JSON response
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]

        if admin_status == 'up' and oper_status == 'up':
            return f"Interface {LOOPBACK_ID} is enabled"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface {LOOPBACK_ID} is disabled"
    elif resp.status_code == 404: # 404 Not Found
        print(f"STATUS NOT FOUND: {resp.status_code}")
        return f"No Interface {LOOPBACK_ID}"
    else:
        print(f'Error. Status Code: {resp.status_code}')
        return f"Error checking status: {resp.text}"
