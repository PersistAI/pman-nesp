from flask import Flask, render_template, request
from flask_cors import CORS
from pump.pump import Pump
from pump.connection import Connection
import json

config = {}
with open('./config.json') as f:
    config = json.load(f)

app = Flask(__name__)
for key in config:
    app.config[key] = config[key]
    
port = app.config['serial_port']
connection = Connection(port)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer')
def transfer():
    return render_template('transfer.html', **config)

@app.route('/pman/push', methods=['POST'])
def pmanPush():
    d = json.loads(request.data)
    args = d['args']
    pump = Pump(connection, address=int(args[0]))
    pump.set_direction('INF')
    pump.set_volume(args[0])
    pump.set_rate(args[1])
    ret = pump.run()
    return {
            'status': 'ok',
            'message': ret
            }
    
@app.route('/pman/pull', methods=['POST'])
def pmanPull():
    d = json.loads(request.data)
    args = d['args']
    pump = Pump(connection, address=int(args[0]))
    pump.set_direction('WDR')
    pump.set_volume(args[0])
    pump.set_rate(args[1])
    ret = pump.run()
    return {
            'status': 'ok',
            'message': ret
            }

if __name__ == '__main__':
    app.run(debug=True)
