import time 
class DeviceData:
    def __init__(self):
        self.is_connected = False

    def connect(self):
        time.sleep(2)  #temp delay will actually connect to the switch 
        self.is_connected = True
        return "Connected to device successfully!"

device_data = DeviceData()