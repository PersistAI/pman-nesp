from flask import Flask, render_template, request
from flask_cors import CORS
from nesp_lib import Port, Pump, PumpingDirection
import json

config = {}
with open('./config.json') as f:
    config = json.load(f)

app = Flask(__name__)
for key in config:
    app.config[key] = config[key]
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer')
def transfer():
    return render_template('transfer.html')

@app.route('/pman/push', methods=['POST'])
def pmanPush():
    d = json.loads(request.data)
    args = d['args']
    port = Port(app.config['serial_port'])
    pump = Pump(port)
    pump.syringe_diameter = app.config['syringe_diameter_mm']
    pump.pumping_direction = PumpingDirection.INFUSE
    pump.pumping_volume = args[0]
    pump.pumping_rate = args[1]
    pump.run()
    return {
            'status': 'ok',
            'message': 'push completed'
            }
    
@app.route('/pman/pull', methods=['POST'])
def pmanPull():
    d = json.loads(request.data)
    args = d['args']
    port = Port(app.config['serial_port'])
    pump = Pump(port)
    pump.syringe_diameter = app.config['syringe_diameter_mm']
    pump.pumping_direction = PumpingDirection.WITHDRAW
    pump.pumping_volume = args[0]
    pump.pumping_rate = args[1]
    pump.run()
    return {
            'status': 'ok',
            'message': 'pull completed'
            }

if __name__ == '__main__':
    app.run(debug=True)
