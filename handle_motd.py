import subprocess
from netmiko import ConnectHandler

# --- ดึงค่า username/password มาจากไฟล์อื่น (หรือจะ Hardcode ที่นี่ก็ได้) ---
# นี่เป็นวิธีที่ไม่ดีนัก แต่เพื่อให้ง่ายตามโจทย์
username = "admin"
password = "cisco"
# -----------------------------------------------------------------

def set_motd(ip_address, message):
    """
    ใช้ Ansible (playbook_motd.yaml) เพื่อตั้งค่า MOTD
    """
    command = [
        'ansible-playbook', 
        'playbook_motd.yaml',
        '--limit', ip_address,
        '-e', f'motd_message="{message}"' # ใส่ "" คร่อม message เสมอ
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        output = result.stdout
        
        if 'failed=0' in output and 'unreachable=0' in output:
            return 'Ok: success'
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
        "username": username,
        "password": password,
    }
    
    command_to_run = "show running-config | include banner motd"
    
    try:
        with ConnectHandler(**device_params) as ssh:
            result = ssh.send_command(command_to_run)
        
        # ผลลัพธ์ที่คาดหวัง: "banner motd CAuthorized users only!C"
        # หรือ "" (ว่าง) ถ้าไม่มี
        
        if result:
            # 'banner motd' ยาว 11 ตัวอักษร
            # ตัวที่ 12 (index 11) คือตัวคั่น (Delimiter)
            delimiter = result[11]
            
            # หาตัวคั่นตัวสุดท้าย
            last_delim_index = result.rfind(delimiter)
            
            if last_delim_index > 11:
                # ดึงข้อความระหว่างตัวคั่นตัวแรกและตัวสุดท้าย
                motd_message = result[12:last_delim_index]
                return motd_message
            else:
                # เจอ "banner motd" แต่หาตัวคั่นปิดไม่เจอ
                return "Error: Could not parse MOTD"
        else:
            # ถ้า 'result' ว่างเปล่า = ไม่มีการตั้งค่า MOTD
            return "Error: No MOTD Configured"
    
    except Exception as e:
        print(f"Netmiko MOTD error: {e}")
        return f"Error: Could not connect to {ip_address}"