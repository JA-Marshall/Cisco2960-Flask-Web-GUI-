import time 
import netmiko 
import json
from netmiko import ConnectHandler


device_info = json.load(open('data/switch_credentials.json', 'r'))

class DeviceData:
    def __init__(self):
        self.is_connected = False
        self.port_status = {}
        self.health_status = {}
        self.general_device_info = {}


    def connect(self):
        net_connect = ConnectHandler(**device_info)
        
        self.health_status = net_connect.send_command('show env all',use_textfsm=True)
        self.general_device_info = net_connect.send_command('show inventory', use_textfsm=True)
        raw_port_status = net_connect.send_command('show ip int brief',use_textfsm=True)

        self.port_status = self.build_port_up_list(raw_port_status)

        self.health_status = self.parse_show_env(self.health_status)
        print(self.health_status)
        print(self.general_device_info)
        self.is_connected = True
        net_connect.disconnect()
        print(self.port_status)
        return "Connected to device successfully!"
    
    #no ntc_template for show env all on a 2960 so need to parse it manually 

    def parse_show_env(self, health_status):
        status_dict = {}
    
        lines = health_status.split('\n')
        
        for line in lines:
            if "FAN" in line:
                status = line.split('is')[-1].strip()
              
                status_dict['fan'] = status.lower()
            elif "SYSTEM TEMPERATURE" in line:
              
                status = line.split('is')[-1].strip()
                status_dict['temp'] = status.lower()
            elif "POWER" in line:
              
                status = line.split('is')[-1].strip()
                status_dict['power'] = status.lower()
        
        return status_dict
    
    def build_port_up_list(self,raw_port_status):
        print(f'status :{raw_port_status}')
        port_status_list = []
        for index, entry in enumerate(raw_port_status):
            if 'Vlan' in entry['interface']:
                continue  
            
            port_number = str(index )  # Convert index to string and start from 1 for port numbering
            port_status = {port_number: 'up'} if entry['status'] == 'up' and entry['proto'] == 'up' else {port_number: 'down'}
            
            port_status_list.append(port_status)

        # Sorting the list to have all odd ports first, then evens to match what a cisco switch layout is 

        sorted_port_status = sorted(port_status_list, key=lambda x: (int(list(x.keys())[0]) % 2 == 0, int(list(x.keys())[0])))
        return sorted_port_status
    
device_data = DeviceData()