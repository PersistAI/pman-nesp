from flask import Blueprint, request, current_app, render_template
import json
from pump.pump import serial_lock, emergency_stop_flag, get_pump

api = Blueprint('api', __name__)

@api.route('/stop', methods=['GET','POST'])
@api.route('/pman/hardstop', methods=['GET','POST'])
def stop():
    # this flag tells the poller to stop polling
    emergency_stop_flag.set()
    pump = get_pump(addr=0)
    with serial_lock: # the lock makes sure that polling is done before stop command is sent
        pump.ser.write(b'STP\r') # command without addr should broadcast
        response = pump.ser.readall().decode()
    return {'status':'ok','message':response}

@api.route('/pman/resume', methods=['GET','POST'])
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

@api.route('/pman/push', methods=['POST'])
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
    
@api.route('/pman/pull', methods=['POST'])
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
