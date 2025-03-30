import configparser
import os
import subprocess

SKBD = f"""
─▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▄   ───▄██▄─────────────▄▄
█░░░█░░░░░░░░░░▄▄░██░█  ──█████▄▄▄▄───────▄▀
█░▀▀█▀▀░▄▀░▄▀░░▀▀░▄▄░█  ────▀██▀▀████▄───▄▀
█░░░▀░░░▄▄▄▄▄░░██░▀▀░█  ───▄█▀▄██▄████▄─▄█
─▀▄▄▄▄▄▀─────▀▄▄▄▄▄▄▀    ▄▄█▀▄▄█─▀████▀██▀  
   ▄████████    ▄█   ▄█▄ ▀█████████▄  ████████▄  
  ███    ███   ███ ▄███▀   ███    ███ ███   ▀███ 
  ███    █▀    ███▐██▀     ███    ███ ███    ███  
  ███         ▄█████▀     ▄███▄▄▄██▀  ███    ███ 
▀███████████ ▀▀█████▄    ▀▀███▀▀▀██▄  ███    ███  
         ███   ███▐██▄     ███    ██▄ ███    ███  
   ▄█    ███   ███ ▀███▄   ███    ███ ███   ▄███ 
 ▄████████▀    ███   ▀█▀ ▄█████████▀  ████████▀  
Maptnh@S-H4CK13  SKBD(Scorpion-Killer)V1.0-Server-EXEC  https://github.com/MartinxMax
=============="""

class MachineControl:
    def __init__(self):
        self.machines = []
        self.current_machine = None
        self.temp_config = {} 
        self.load_machines()

    def load_machines(self):
        seen_sns = set()  
        self.machines = []  
        for root, dirs, files in os.walk('./machines'):
            if 'info.conf' in files:
                machine_info_file = os.path.join(root, 'info.conf')
                machine_data = self.parse_info_file(machine_info_file)
                if machine_data and machine_data['sn'] not in seen_sns:
                    self.machines.append(machine_data)
                    seen_sns.add(machine_data['sn'])

    def parse_info_file(self, filepath):
        config = configparser.ConfigParser(allow_no_value=True, delimiters=('=', ':'))
        try:
            config.read(filepath)
        except configparser.ParsingError as e:
            print(f"Error parsing {filepath}: {e}")
            return {}

        machine_data = {}

        for section in config.sections():
            for key, value in config.items(section):
                machine_data[key] = value.strip() if value else ''

        if 'users' not in machine_data or 'ips' not in machine_data or 'sn' not in machine_data:
            print(f"Warning: Missing required fields in {filepath}. Skipping.")
            return {}

        return machine_data
    
    def display_machines(self):
        self.load_machines()  
        if not self.machines:
            print("No valid machines found.")
            return

        print("+----------------------------------+-----------------------+-------------------+----------------------------------+")
        print("| Machine ID                       | Users                 | IPS               | SN                               |")
        print("+----------------------------------+-----------------------+-------------------+----------------------------------+")
        for index, machine in enumerate(self.machines, start=1):
            print(f"| {str(index).ljust(32)} | {machine['users'].ljust(21)} | {machine['ips'].ljust(17)} | {machine['sn'].ljust(34)} |")
            print("+----------------------------------+-----------------------+-------------------+----------------------------------+")


            
    def select_machine(self, machine_id):
        if 1 <= machine_id <= len(self.machines):
            self.current_machine = self.machines[machine_id - 1]
            self.temp_config = { 
                'user': self.current_machine['users'].split(',')[0].strip(),
                'ip': self.current_machine['ips'].split(',')[0].strip(),
                'port': '22'   
            }
            print(f"Entering submodule for machine with SN: {self.current_machine['sn']}")
            return True
        return False

    def show_config(self):
        if not self.current_machine:
            print("No machine selected.")
            return

        sn = self.current_machine['sn']
        config_path = f'./machines/{sn}/info.conf'
        config = configparser.ConfigParser(allow_no_value=True, delimiters=('=', ':'))
        try:
            config.read(config_path)
        except configparser.ParsingError as e:
            print(f"Error parsing {config_path}: {e}")
            return
        parameters = {key: value for section in config.sections() for key, value in config.items(section)}
        print("\n+-------------------------------------------+-------------------------------------------+")
        print(f"| Configuring Machine: {sn[:35].ljust(35)} |")
        print("+-------------------------------------------+-------------------------------------------+")
        print("| Parameter".ljust(20) + " | Value".ljust(35) + " |")
        print("+-------------------------------------------+-------------------------------------------+")

        for key, value in parameters.items():
            print(f"| {key.ljust(18)} | {value.ljust(33)} | (Editable) |")

        print("+-------------------------------------------+-------------------------------------------+\n")
        print("To modify values, use: set <param> <value>")
        print("Example: set user admin")

        print("\nCurrent session variables:")
        print("+-------------------+-------------------+")
        print(f"| user: {self.temp_config['user'].ljust(17)} |")
        print(f"| ip: {self.temp_config['ip'].ljust(18)} |")
        print(f"| port: {str(self.temp_config['port']).ljust(13)} |")
        print("+-------------------+-------------------+")
        
    def configure_machine(self, param, value):
        if not self.current_machine:
            print("No machine selected.")
            return

        if param.lower() in ['user', 'ip', 'port']:
            self.temp_config[param.lower()] = value
            print(f"Updated {param.capitalize()} to {value}")
        else:
            print(f"Invalid parameter {param}. Only 'user', 'ip', and 'port' are allowed.")
    def connect_to_machine(self):
        if not self.current_machine:
            print("No machine selected.")
            return
        user = self.temp_config['user']
        ip = self.temp_config['ip']
        port = self.temp_config['port']
        sn = self.current_machine['sn']
        key_path = './auth_protect/id_rsa'
        cert_path = f'./machines/{sn}/skbd.pub'
        ssh_command = f"ssh -i {key_path} -o CertificateFile={cert_path} -p {port} {user}@{ip}"
        os.system(ssh_command)

    def show_help(self):
        print("Available commands:")
        print("  info - Display all available machines.")
        print("  use <machine_id> - Enter the configuration submodule for a selected machine.")
        print("  exit - Exit the script or submodule.")
        print("  help - Show this help message.")

        if self.current_machine:
            print("Submodule Commands:")
            print("  show - Display current configuration (info.conf) and session variables.")
            print("  set <param> <value> - Set a session parameter (user, ip, port).")
            print("  run - Connect via SSH using session variables.")

def main():
    control = MachineControl()
    control.show_help()

    while True:
        command = input("SKBD # ").strip()
        if command.lower() == "exit":
            break
        elif command.lower() == "info":
            control.display_machines()
        elif command.lower().startswith("use"):
            try:
                machine_id = int(command.split()[1])
                if control.select_machine(machine_id):
                    while True:
                        sub_command = input(f"SKBD[{control.current_machine['sn']}]# ").strip()
                        if sub_command.lower() == "exit":
                            break
                        elif sub_command.lower() == "show":
                            control.show_config()
                        elif sub_command.lower().startswith("set"):
                            parts = sub_command.split()
                            if len(parts) == 3:
                                control.configure_machine(parts[1], parts[2])
                            else:
                                print("Invalid command format. Use 'set <param> <value>'")
                        elif sub_command.lower() == "run":
                            control.connect_to_machine()
                        elif sub_command.lower() == "help":
                            control.show_help()
                        else:
                            print("Invalid command. Use 'show', 'set <param> <value>', or 'run'.")
                else:
                    print("Invalid machine ID.")
            except (IndexError, ValueError):
                print("Invalid command format. Use 'use <machine_id>'.")
        elif command.lower() == "help":
            control.show_help()
        else:
            print("Invalid command. Use 'info', 'use <machine_id>', 'help', or 'exit'.")

if __name__ == "__main__":
    print(SKBD)
    main()