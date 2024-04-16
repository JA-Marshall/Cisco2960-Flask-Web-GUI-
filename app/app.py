
from flask import Flask, render_template, redirect, url_for, session
from data.switch_device_data import device_data
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    msg = device_data.connect()
    if device_data.is_connected:
        session['connected'] = True
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
        return render_template('ports.html')
    return redirect(url_for('index'))

@app.route('/health')
def health():
    if 'connected' in session:
        return render_template('health.html')
    return redirect(url_for('index'))

@app.route('/device_info')
def device_info():
    if 'connected' in session:
        return render_template('device_info.html')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)