import paramiko
import threading
from flask_socketio import SocketIO
import json

class TerminalEmulator:
    def __init__(self, ip, username, password, socketio):
        self.ip = ip
        self.username = username
        self.password = password
        self.socketio = socketio
        self.client = None
        self.channel = None

    def create_ssh_client(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname=self.ip, username=self.username, password=self.password, look_for_keys=False, allow_agent=False)
        except Exception as e:
            print(f"Failed to connect to {self.ip}: {e}")
            raise

    def start_terminal(self):
        self.create_ssh_client()
        self.channel = self.client.get_transport().open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()
        reader_thread = threading.Thread(target=self.read_from_channel)
        reader_thread.start()

    def read_from_channel(self):
        try:
            while True:
                if self.channel.recv_ready():
                    data = self.channel.recv(1024).decode('utf-8')
                    if not data:
                        break
                    self.socketio.emit('ssh_output', {'data': data}, namespace='/ssh')
        except Exception as e:
            print(f"Error reading from channel: {e}")
            self.channel.close()

    def send_command(self, command):
        if self.channel:
            self.channel.send(command + '\r')

    def close(self):
        if self.channel:
            self.channel.close()
        if self.client:
            self.client.close()




if __name__ == "__main__":
    device_info = json.load(open('data/switch_credentials.json', 'r'))
    ip = device_info['ip']
    username = device_info['username']
    password = device_info['password']
    while True:
        termemulator = TerminalEmulator(ip,username,password,SocketIO)
        termemulator.start_terminal()
