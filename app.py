from flask import Flask, render_template, request
from flask_cors import CORS
from pump.pump import Pump
from pump.connection import Connection
import json
import time
import pdb

config = {}
with open('./config.json') as f:
    config = json.load(f)

app = Flask(__name__)
CORS(app)
for key in config:
    app.config[key] = config[key]
    
port = app.config['serial_port']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer')
def transfer():
    return render_template('transfer.html', **config)

@app.route('/stop', methods=['GET','POST'])
def stop():
    connection = Connection(config['serial_port'])
    connection.send('STP\r')
    connection.close()
    return {'status':'ok','message':'stopped'}


@app.route('/pman/push', methods=['POST'])
def pmanPush():
    d = json.loads(request.data)
    args = d['args']
    connection = Connection(config['serial_port'])
    pump = Pump(connection, address=int(args[0]))
    pump.set_direction('INF')
    pump.set_volume(args[1])
    pump.set_rate(args[2])
    ret = pump.run()
    connection.close()
    return {
            'status': 'ok',
            'message': ret
            }
    
@app.route('/pman/pull', methods=['POST'])
def pmanPull():
    d = json.loads(request.data)
    args = d['args']
    connection = Connection(config['serial_port'])
    pump = Pump(connection, address=int(args[0]))
    print(pump.set_direction('WDR'))
    print(args[1])
    print(pump.set_volume(args[1]))
    print(args[2])
    print(pump.set_rate(args[2]))
    time.sleep(1)
    ret = pump.run()
    connection.close()
    return {
            'status': 'ok',
            'message': ret
            }

if __name__ == '__main__':
    app.run(debug=True)
