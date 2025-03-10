from flask import Flask
import warnings
import serial
import os
import logging
from flask_cors import CORS
import json
from website.views import views
from website.api import api
from website.pump import PumpManager

with open('./config.json') as f:
    config = json.load(f)

def create_app():

    app = Flask(__name__)
    CORS(app)
    app.config.update(config)

    app.register_blueprint(views)
    app.register_blueprint(api)
        
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

    try:
        pump = PumpManager(
                config['serial_port'],
                config['baud_rate']
                )
    except serial.SerialException as e:
        pump = None
        warnings.warn(f"Failed to connect to pump with error {e}")
    app.config['pump'] = pump
    app.config['pump-manager'] = pump
    return app
