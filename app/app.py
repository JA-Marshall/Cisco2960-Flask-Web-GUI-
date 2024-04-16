from flask import Flask, render_template
from app.data.switch_device_data import DeviceData

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/ports')
def ports():
    return render_template('ports.html')

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/device_info')
def device_info():
    return render_template('device_info.html')

if __name__ == '__main__':
    app.run(debug=True)
