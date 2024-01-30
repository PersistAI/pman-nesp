import sys
import pdb
import time
import pytest
from unittest.mock import patch
sys.path.append('..')
from pump.pump import Pump
from pump.connection import Connection

@pytest.fixture
def mock_connection():
    with patch('pump.connection.Connection') as mock:
        mock.get_response.return_value = "<STX>OK<ETX>"
        yield mock

def test_initialization(mock_connection):
    pump = Pump(mock_connection, 0)
    assert pump.address == 0
    assert pump.connection == mock_connection

def test_run(mock_connection):
    pump = Pump(mock_connection, 0)
    response = pump.run()
    
    mock_connection.queue_command.assert_called_once_with('0RUN\r')
    assert response == "<STX>OK<ETX>"

def test_stop(mock_connection):
    pump = Pump(mock_connection, 0)
    response = pump.stop()
    mock_connection.queue_command.assert_called_once_with('0STP\r')
    assert response == "<STX>OK<ETX>"

def test_wait_for_motor(mock_connection):
    pump = Pump(mock_connection, 0)
    mock_connection.get_response.side_effect = ["<STX>I<ETX>", "<STX>W<ETX>", "<STX>S<ETX>"]
    pump.wait_for_motor()
    assert mock_connection.get_response.call_count == 3
    mock_connection.queue_command.assert_called_with('0ROM\r')

def test_set_direction(mock_connection):
    pump = Pump(mock_connection, 0)
    direction = "INF"
    response = pump.set_direction(direction)
    mock_connection.queue_command.assert_called_once_with(f'0DIR{direction}\r')
    assert response == "<STX>OK<ETX>"

def test_set_volume(mock_connection):
    pump = Pump(mock_connection, 0)
    volume = 1.5  # mL
    response = pump.set_volume(volume)
    mock_connection.queue_command.assert_called_once_with(f'0VOL{volume}\r')
    assert response == "<STX>OK<ETX>"

def test_set_rate(mock_connection):
    pump = Pump(mock_connection, 0)
    rate = 2.5  # mL/Min
    response = pump.set_rate(rate)
    mock_connection.queue_command.assert_called_once_with(f'0RAT{rate}\r')
    assert response == "<STX>OK<ETX>"

