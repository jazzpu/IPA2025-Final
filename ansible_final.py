import subprocess

def showrun():
    command = ['ansible-playbook', 'playbook.yaml']
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    
    # A much more reliable way to check for success
    if 'failed=0' in output and 'unreachable=0' in output:
        return 'ok'
    else:
        # Also print the error output for easier debugging
        print("Ansible failed. Output:")
        print(output)
        print(result.stderr)
        return 'Error: Ansible'