
from flask import Flask, render_template, redirect, url_for, session
from data.switch_device_data import device_data
import time
import threading


app = Flask(__name__)
app.secret_key = 'your_secret_key'  
data_thread = None

def update_data():
    while True:
        # Fetch the data every 10 seconds on the switch. 
        device_data.connect()
        time.sleep(1) 


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    global data_thread  
    msg = device_data.connect()
    if device_data.is_connected:
        session['connected'] = True
        if data_thread is None or not data_thread.is_alive():
            data_thread = threading.Thread(target=update_data)
            data_thread.daemon = True
            data_thread.start()
        return redirect(url_for('home'))  
    else:
        return "Connection failed", 401

@app.route('/home')
def home():
    if 'connected' in session:
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/ports')
def ports():
    if 'connected' in session:
        #convert dictionary to list of dictionaries
        port_status_list = [{port: status} for port, status in device_data.port_status.items()]

        #sorting the list to have all odd ports first, then even to match what a Cisco switch layout is
        sorted_port_status = sorted(port_status_list, key=lambda x: (int(list(x.keys())[0]) % 2 == 0, int(list(x.keys())[0])))
        return render_template('ports.html',data=sorted_port_status)
    return redirect(url_for('index'))

@app.route('/health')
def health():
    if 'connected' in session:
        return render_template('health.html',data = device_data.health_status)
    return redirect(url_for('index'))

@app.route('/device_info')
def device_info():
    if 'connected' in session:
        return render_template('device_info.html',data=device_data.general_device_info[0])
    return redirect(url_for('index'))

if __name__ == '__main__':
   
    app.run(debug=True)