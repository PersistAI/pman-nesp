from flask import Flask, render_template, request
import os
import logging
import atexit
from flask_cors import CORS
from pump.pump import Pump
import json
import time
import pdb

with open('./config.json') as f:
    config = json.load(f)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.update(config)
        
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
    return render_template('index.html', **config)

def get_pump(addr=0):
     port = config['serial_port']
     return Pump(port, address=addr, logger=app.logger)

@app.route('/stop', methods=['GET','POST'])
@app.route('/pman/hardstop', methods=['GET','POST'])
def stop():
    for addr in config.get("addresses", [0]):
        pump = get_pump(addr)
        pump.stop()
    return {'status':'ok','message':'stopped'}

@app.route('/pman/resume', methods=['GET','POST'])
def resume():
    if request.method == 'POST':
        d = json.loads(request.data)
        args = d['args']
    else:
        args = [0]
    addr = int(args[0])
    pump = get_pump(addr)
    pump.run()
    pump.wait_for_motor()
    
    return {'status':'ok','message':'Resuming'}

@app.route('/pman/push', methods=['POST'])
def pmanPush():
    d = json.loads(request.data)
    args = d['args']
    addr = int(args[0])
    pump = get_pump(addr)
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
    addr = int(args[0])
    pump = get_pump(addr)
    pump.set_direction('WDR')
    pump.set_volume(args[1])
    pump.set_rate(args[2])
    ret = pump.run()
    pump.wait_for_motor()
    return {
            'status': 'ok',
            'message': ret
            }

if __name__ == '__main__':
    app.run(debug=True, port=5058)
