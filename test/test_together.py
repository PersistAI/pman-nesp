import sys
import pdb
import time
import pytest
from unittest.mock import MagicMock, patch
sys.path.append('..')
from pump.pump import Pump
from pump.connection import Connection

@pytest.fixture
def mock_serial():
    with patch('pump.connection.serial.Serial') as mock:
        yield mock

def test_initialization(mock_serial):
    conn = Connection('/dev/test')
    pump0 = Pump(conn, 0)
    pump1 = Pump(conn, 1)
    assert pump0.connection == conn
    assert pump0.address == 0
    assert pump1.connection == conn
    assert pump1.address == 1

def test_run(mock_serial):
    num_pumps = 5
    responses = [f'RESPONSE_{addr}'.encode() for addr in range(num_pumps)]
    mock_serial.return_value.read_until.side_effect = responses
    conn = Connection('/dev/test')
    pumps = [Pump(conn, addr) for addr in range(num_pumps)]
    responses = [p.run() for p in pumps]
    for i in range(len(responses)):
        address = int(responses[i].split('_')[-1])
        assert address == pumps[i].address
