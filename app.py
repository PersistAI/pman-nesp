from flask import Flask, render_template, request
import warnings
import threading
import os
import logging
import atexit
from flask_cors import CORS
from serial import SerialException, Serial
from pump.pump import Pump, serial_lock, emergency_stop_flag
import json
import time
import pdb

with open('./config.json') as f:
    config = json.load(f)

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.update(config)
        
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


# the app must have one global serial connection
# because windows makes it super annoying to have multiple serial connections trying to share one port
# It does not let you set exclusive=False
try:
    ser = Serial(
            baudrate=config.get('baud_rate', 19200),
            port=config.get('serial_port')
            )
except SerialException:
    serial = None
    port=config.get('serial_port')
    warnings.warn(f'Could not open port {port}, running without a connection')

@app.route('/')
def index():
    return render_template('index.html', **config)

def get_pump(addr=0):
     return Pump(ser=ser, address=addr, logger=app.logger)

@app.route('/stop', methods=['GET','POST'])
@app.route('/pman/hardstop', methods=['GET','POST'])
def stop():
    # this flag tells the poller to stop polling
    emergency_stop_flag.set()
    pump = get_pump()
    with serial_lock: # the lock makes sure that polling is done before stop command is sent
        pump.ser.write(b'STP\r') # command without addr should broadcast
        response = pump.ser.readall()
    return {'status':'ok','message':response}

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
