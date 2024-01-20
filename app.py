from flask import Flask, render_template, request
from flask_cors import CORS
from pump.pump import Pump
from pump.connection import Connection
import json
import pdb

config = {}
with open('./config.json') as f:
    config = json.load(f)
connection = Connection(config['serial_port'])

connection = Connection(config['serial_port'])
app = Flask(__name__)
CORS(app)
for key in config:
    app.config[key] = config[key]
    
port = app.config['serial_port']

@app.before_request
def open_connection():
    connection.open(port)

@app.teardown_appcontext
def close_connection():
    connection.close()

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
