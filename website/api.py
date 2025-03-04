from flask import Blueprint, request, current_app, render_template
import asyncio
import time
import json

api = Blueprint('api', __name__)

@api.route('/stop', methods=['GET','POST'])
@api.route('/pman/hardstop', methods=['GET','POST'])
def stop():
    if request.method != 'POST':
        addr = None
    elif not request.json:
        addr = None
    elif 'args' in request.json:
        addr = request.json['args'][0]
    else:
        addr = None

    pump = current_app.config['pump']
    address_array = current_app.config['addresses']

    if addr == None:
        response = pump.stop_all(address_array)
    else:
        response = pump.stop(addr)

    return {'status':'ok','message':f'Stopped with response: {response.decode()}'}

@api.route('/pman/resume', methods=['GET','POST'])
def resume():
    if request.method == 'POST':
        d = json.loads(request.data)
        args = d['args']
    else:
        args = [0]
    addr = int(args[0])
    pump = current_app.config['pump']
    pump.run(addr)
    asyncio.run(pump.wait_for_motor(addr))
    return {'status':'ok','message':'Resuming'}

@api.route('/pman/push', methods=['POST'])
def pmanPush():
    d = json.loads(request.data)
    args = d['args']
    addr = int(args[0])
    pump = current_app.config['pump']
    pump.set_direction(addr, 'INF')
    pump.set_volume(addr, args[1])
    pump.set_rate(addr, args[2])
    ret = pump.run(addr)
    asyncio.run(pump.wait_for_motor(addr))
    return {
            'status': 'ok',
            'message': ret
            }
    
@api.route('/pman/pull', methods=['POST'])
def pmanPull():
    d = json.loads(request.data)
    args = d['args']
    addr = int(args[0])
    pump = current_app.config['pump']
    pump.set_direction(addr, 'WDR')
    pump.set_volume(addr, args[1])
    pump.set_rate(addr, args[2])
    ret = pump.run(addr)
    asyncio.run(pump.wait_for_motor(addr))
    return {
            'status': 'ok',
            'message': ret
            }
