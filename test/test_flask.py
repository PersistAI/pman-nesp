import sys
sys.path.append('..')
import pdb
import pytest
from flask import json
from app import app 
from unittest.mock import patch

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.Connection')
def test_index(MockConnection, client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.content_type

@patch('app.Connection')
def test_stop(MockConnection, client):
    app.connection = MockConnection
    response = client.post('/stop')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data == {'status': 'ok', 'message': 'stopped'}

@patch('app.Connection')
def test_stop(MockConnection, client):
    app.connection = MockConnection
    response = client.post('/stop')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data == {'status': 'ok', 'message': 'stopped'}
    MockConnection.send.assert_called_once_with('STP\r')

@patch('app.Pump')
@patch('app.Connection')
def test_pman_push(MockConnection, MockPump, client):
    app.connection = MockConnection.return_value
    mock_pump = MockPump.return_value
    mock_pump.run.return_value = "Pump running"
    response = client.post('/pman/push', data=json.dumps({'args': ['0', '1.5', '2.5']}), content_type='application/json')
    assert response.status_code == 200
    
    MockPump.assert_called_once_with(MockConnection.return_value, address=0)
    mock_pump.set_direction.assert_called_once_with('INF')
    mock_pump.set_volume.assert_called_once_with('1.5')
    mock_pump.set_rate.assert_called_once_with('2.5')
    mock_pump.run.assert_called_once()
    mock_pump.wait_for_motor.assert_called_once()
    data = json.loads(response.data.decode('utf-8'))
    assert data == {'status': 'ok', 'message': 'Pump running'}

@patch('app.Pump')
@patch('app.Connection')
def test_pman_pull(MockConnection, MockPump, client):
    app.connection = MockConnection.return_value
    mock_pump = MockPump.return_value
    mock_pump.run.return_value = "Pump running"
    response = client.post('/pman/pull', data=json.dumps({'args': ['0', '1.5', '2.5']}), content_type='application/json')
    assert response.status_code == 200
    MockPump.assert_called_once_with(MockConnection.return_value, address=0)
    mock_pump.set_direction.assert_called_once_with('WDR')
    mock_pump.set_volume.assert_called_once_with('1.5')
    mock_pump.set_rate.assert_called_once_with('2.5')
    mock_pump.run.assert_called_once()
    mock_pump.wait_for_motor.assert_called_once()
    data = json.loads(response.data.decode('utf-8'))
    assert data == {'status': 'ok', 'message': 'Pump running'}
