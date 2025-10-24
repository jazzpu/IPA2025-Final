import subprocess
from netmiko import ConnectHandler
import re

USERNAME = "admin"
PASSWORD = "cisco"
# -----------------------------------------------------------------

def set_motd(ip_address, message):
    """
    ใช้ Ansible (playbook_motd.yaml) เพื่อตั้งค่า MOTD
    """
    command = [
        'ansible-playbook',
        'playbook_motd.yaml',
        '--limit', ip_address,
        '-e', f'motd_message={message}'
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        output = result.stdout

        # ตรวจสอบผลลัพธ์ของ ansible
        if 'failed=0' in output and 'unreachable=0' in output and 'changed=1' in output:
            return 'Ok: success'
        elif 'failed=0' in output and 'changed=0' in output:
            return 'Ok: success (message was already set)'
        else:
            print("Ansible MOTD failed. Output:")
            print(output)
            print(result.stderr)
            return 'Error: Ansible failed to set MOTD'

    except Exception as e:
        print(f"Error running set_motd: {e}")
        return f"Error: {e}"


def get_motd(ip_address):
    """
    ใช้ Netmiko เพื่ออ่านค่า MOTD จาก running-config (รองรับ multi-line)
    """
    device_params = {
        "device_type": "cisco_ios",
        "host": ip_address,
        "username": USERNAME,
        "password": PASSWORD
    }

    command_to_run = "show running-config"

    try:
        with ConnectHandler(**device_params) as ssh:
            result = ssh.send_command(command_to_run)
            print(result)

        # --- ใช้ Regex หา banner motd ---
        motd_pattern = r"banner motd (.)C(.*?)\1"
        match = re.search(motd_pattern, result, re.DOTALL)
        print("match, %s"%match)
        if match:
            motd_message = match.group(2).strip()
            return motd_message if motd_message else "Error: MOTD is empty"
        else:
            return "Error: No MOTD Configured"

    except Exception as e:
        print(f"Netmiko MOTD error: {e}")
        return f"Error connecting with Netmiko: {e}"
