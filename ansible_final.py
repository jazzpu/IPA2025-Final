import subprocess

def showrun(ip_address):
    # เราจะใช้ ip_address ในการ --limit และส่งเป็นตัวแปร target_ip
    # หมายเหตุ: 'target_host' ใน playbook.yaml จะถูกกำหนดโดย --limit
    # เราต้องแน่ใจว่า IP นี้มีอยู่ในไฟล์ hosts
    
    # เราจะใช้ ip_address (เช่น 10.0.15.61) เป็นตัว limit
    # และส่งตัวแปร 'target_ip' เข้าไปใน playbook เพื่อใช้ตั้งชื่อไฟล์
    
    command = [
        'ansible-playbook', 
        'playbook.yaml',
        '--limit', ip_address,  # จำกัดการรันเฉพาะ IP นี้ (ต้องมีใน inventory)
        '-e', f'target_ip={ip_address}' # ส่งตัวแปรเข้าไปใน playbook
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    
    if 'failed=0' in output and 'unreachable=0' in output:
        return 'ok'
    else:
        print("Ansible failed. Output:")
        print(output)
        print(result.stderr)
        return 'Error: Ansible'