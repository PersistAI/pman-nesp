from flask import Flask, render_template, request
import os
import logging
import atexit
from flask_cors import CORS
from pump.pump import Pump
import json
import time
import pdb

config = {}
with open('./config.json') as f:
    config = json.load(f)

def create_app():
    app = Flask(__name__)
    CORS(app)
    for key in config:
        app.config[key] = config[key]
        
    port = app.config['serial_port']

    logdir = config['logdir']
    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    file_handler = logging.FileHandler('logs/debug.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    app.logger.setLevel(logging.DEBUG) 
    app.logger.addHandler(file_handler) 

    app.logger.debug('app created')
    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transfer')
def transfer():
    return render_template('transfer.html', **config)

@app.route('/stop', methods=['GET','POST'])
@app.route('/pman/hardstop', methods=['GET','POST'])
def stop():
    # set for all addrs, not just the one in current step.
    app.connection.send('STP\r')
    # MUST receive response in order to not back up serial port cache
    response = app.connection.receive() 
    return {'status':'ok','message':'stopped'}

@app.route('/pman/resume', methods=['GET','POST'])
def resume():
    if request.method == 'POST':
        d = json.loads(request.data)
        args = d['args']
    else:
        args = [0]
    addr = int(args[0])
    # set for all addrs, not just the one in current step.
    pump = Pump(app.connection, address=addr, logger=app.logger)
    app.connection.send('RUN\r')
    # MUST receive response in order to not back up serial port cach
    response = app.connection.receive()
    pump.wait_for_motor()
    
    return {'status':'ok','message':'Resuming'}

@app.route('/pman/push', methods=['POST'])
def pmanPush():
    d = json.loads(request.data)
    args = d['args']
    pump = Pump(app.connection, address=int(args[0]), logger=app.logger)
    pump.set_direction('INF')
    pump.set_volume(args[1])
    pump.set_rate(args[2])
    ret = pump.run()
    pump.wait_for_motor()
    return {
            'status': 'ok',
            'message': ret
            }
    
@app.route('/pman/pull', methods=['POST'])
def pmanPull():
    d = json.loads(request.data)
    args = d['args']
    pump = Pump(app.connection, address=int(args[0]),logger=app.logger)
    print(pump.set_direction('WDR'))
    print(args[1])
    print(pump.set_volume(args[1]))
    print(args[2])
    print(pump.set_rate(args[2]))
    time.sleep(1)
    ret = pump.run()
    pump.wait_for_motor()
    return {
            'status': 'ok',
            'message': ret
            }

if __name__ == '__main__':
    # Debug mode must be off to avoid annoying restarts that re-declare connection
    app.run(debug=False, port=5058)
