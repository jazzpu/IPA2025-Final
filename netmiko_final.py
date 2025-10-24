from netmiko import ConnectHandler
from pprint import pprint

username = "admin"
password = "cisco"

def gigabit_status(ip_address):

    device_params = {
        "device_type": "cisco_ios",
        "ip": ip_address,
        "username": username,
        "password": password,
        "optional_args": {
            'kex_algs': ["diffie-hellman-group14-sha1"],
            'key_algs': ["ssh-rsa"]
        }
    }
    
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("show ip interface brief", use_textfsm=True)
        for status in result:
            if status['interface'].startswith("GigabitEthernet"):
                if status['status'] == "up" and status['proto'] == 'up':
                    up += 1
                elif status['status'] == "down" and status['proto'] == 'down':
                    down += 1
                elif status['status'] == "administratively down":
                    admin_down += 1
        ans = f"{up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans
