
from flask import Flask, render_template, redirect, url_for, session,request
from data.switch_device_data import DeviceData
import time
import threading
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'your_secret_key'  
data_thread = None
device_data = DeviceData(socketio)
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
    if data_thread is None or not data_thread.is_alive():
        data_thread = threading.Thread(target=update_data)
        data_thread.daemon = True
        data_thread.start()
    return redirect(url_for('connecting'))


@app.route('/connecting/')
def connecting():
    return render_template('connecting.html')

#i think this is bad having this many redirects for the websocket to work but i want to get this working before i sleep

@app.route('/connected')
def connected():
    session['connected'] = True

    return redirect(url_for('home'))

@app.route('/home')
def home():
    print(session)
    if 'connected' in session:
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/ports')
def ports():
    if 'connected' in session:
        print("in ports")
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

@app.route('/terminal')
def terminal():
    if 'connected' in session:
        return render_template('terminal.html')
    return redirect(url_for('index'))


@socketio.on('connect', namespace='/ports')
def test_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/ports')
def test_disconnect():
    print('Client disconnected')




if __name__ == '__main__':
   
    socketio.run(app, debug=True)