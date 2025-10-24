import subprocess
from netmiko import ConnectHandler

# --- ดึงค่า username/password มาจากไฟล์อื่น (หรือจะ Hardcode ที่นี่ก็ได้) ---
# นี่เป็นวิธีที่ไม่ดีนัก แต่เพื่อให้ง่ายตามโจทย์
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
        '-e', f'motd_message={message}' # ใส่ "" คร่อม message เสมอ
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        output = result.stdout
        
        # Check for success
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
    ใช้ Netmiko เพื่ออ่านค่า MOTD จาก 'show run | i banner motd'
    """
    device_params = {
        "device_type": "cisco_ios",
        "ip": ip_address,
        "username": USERNAME,
        "password": PASSWORD,
        "kex_algs": ["diffie-hellman-group14-sha1"],
        "key_algs": ["ssh-rsa"]
    }
    
    command_to_run = "show running-config | include banner motd"
    
    try:
        with ConnectHandler(**device_params) as ssh:
            result = ssh.send_command(command_to_run)
        
        motd_message_lines = []
        in_motd = False
        delimiter = None

        # Parse the config line by line
        for line in result.splitlines():
            if line.startswith("banner motd "):
                # --- Found the start line ---
                in_motd = True
                delimiter = line[11] # Get the delimiter (e.g., 'C')
                
                # Check for a single-line banner (e.g., "banner motd CMy MessageC")
                if line.endswith(delimiter) and len(line) > 12:
                    return line[12:-1] # Extract and return immediately
                
                # It's a multi-line banner, save the first part (if any)
                # e.g., "banner motd CThis is the first line"
                first_line_part = line[12:]
                if first_line_part:
                    motd_message_lines.append(first_line_part)
                continue # Move to the next line

            if in_motd:
                # We are inside the banner, waiting for the end
                if line == delimiter:
                    # --- Found the end line ---
                    in_motd = False
                    break # Stop processing
                else:
                    # This is a line of the message
                    motd_message_lines.append(line)
        
        # After the loop, check what we found
        if not motd_message_lines:
            # We never found a banner or the banner was empty
            return "Error: No MOTD Configured"
        else:
            # Join all the collected lines back together
            return "\n".join(motd_message_lines)

    except Exception as e:
        print(f"Netmiko MOTD error: {e}")
        return f"Error connecting with Netmiko: {e}"