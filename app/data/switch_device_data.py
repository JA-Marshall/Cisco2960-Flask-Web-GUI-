import time 
import netmiko 
import json
from netmiko import ConnectHandler
import pprint
from flask_socketio import SocketIO, emit
from flask_socketio import SocketIO


device_info = json.load(open('app/data/switch_credentials.json', 'r'))

class DeviceData:
    def __init__(self,socketio):
        self.is_connected = False
        self.socketio = socketio
        self.port_status = {}
        self.health_status = {}
        self.general_device_info = {}
        self.port_names = []
        self.port_up_down_log = []


    def connect(self):
        try:
            time.sleep(2)
            self.socketio.emit('status_update', {'message': f'Attempting to SSH to {device_info["ip"]} as {device_info["username"]}...'}, namespace='/')
            net_connect = ConnectHandler(**device_info)
            self.is_connected = True
            self.socketio.emit('status_update', {'message': 'Connected successfully!'}, namespace='/')
        except Exception as e:
            self.socketio.emit('status_update', {'message': f'Connection failed: {e}'}, namespace='/')
            time.sleep(15)
            self.is_connected = False
            return "Failed to connect to device."


        self.socketio.emit('status_update', {'message': 'Running show commands..'}, namespace='/')

        self.health_status = net_connect.send_command('show env all',use_textfsm=True)

        self.general_device_info = net_connect.send_command('show inventory', use_textfsm=True)
        raw_port_status = net_connect.send_command('show ip int brief',use_textfsm=True)

        self.port_status = self.build_port_up_list(raw_port_status)
        if not self.port_names:
            self.port_names = self.get_port_names(raw_port_status)
            
        self.health_status = self.parse_show_env(self.health_status)
      
       

        self.socketio.emit('status_update', {'message': 'Done :D Redirecting..'}, namespace='/')

        
        net_connect.disconnect()
        #print(self.port_status)
        #print(self.port_up_down_log)
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
    
    def build_port_up_list(self, raw_port_status):
       
        port_status_dict = {}
        for index, entry in enumerate(raw_port_status):
            if 'Vlan' in entry['interface']:
                continue

            port_number = str(index)  # Convert index to string and start from 1 for port numbering
            port_status_dict[port_number] = 'up' if entry['status'] == 'up' and entry['proto'] == 'up' else 'down'

        # Check for port updates if it's not the first time we're fetching the data
        if self.port_status:
            self.check_port_status_differences(port_status_dict)
            

        return port_status_dict
        


    def check_port_status_differences(self, new_port_status_dict):

        changes = []
  
        for port, current_status in new_port_status_dict.items():
            previous_status = self.port_status.get(port, 'unknown')  
            if previous_status != current_status:
                print(f'\n\n {self.port_names}')
                index = int(port) - 1
                port_name = self.port_names[index]
                print(f'\n\n {port_name}')
                change = f"Change detected: Port {port} ({port_name['full_port_name']}) was {previous_status.upper()}' now '{current_status.upper()}'"
                print(change)
                changes.append({'port': port, 'display_str': change})
      
        if changes:
            print(changes)
            self.socketio.emit('port_update', {'data': changes}, namespace='/ports')

    ##this isn't actually needed i realized ios lets you type in FastEthernet0/1 i thought i needed to add the space..
    ##leaving it in because its less typing for netmiko..
    def get_port_names(self, raw_port_status):

        port_names = []
        for  port in raw_port_status:
            if 'Vlan' in port['interface']:
                continue  
            port_speed = port['interface'][:1]
            ##get last 4 chars, but from ports 1-9 this will get something like 
            #t0/5 so check if first char is a digit if its not chop it off 
            port_number = port['interface'][-4:]
            if not port_number[0].isdigit():
                port_number = port_number[1:]
            #print(f'{port_speed} {port_number}')
            port_names.append({'port_name' : f'{port_speed} {port_number}','full_port_name' : port['interface']})
          
        #print(port_names)
        return port_names
        

    
