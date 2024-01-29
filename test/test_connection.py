import sys
import time
import pdb
import pytest
from unittest.mock import MagicMock, patch
sys.path.append('..')
from pump.connection import Connection  # Adjust the import according to your project structure

@pytest.fixture
def mock_serial():
    with patch('pump.connection.serial.Serial') as mock:
        yield mock

def test_initialization(mock_serial):
    conn = Connection('/dev/test')
    assert conn.connection is not None
    mock_serial.assert_called_with('/dev/test', 9600, timeout=2.0)

def test_queue_command(mock_serial):
    conn = Connection('/dev/test')
    conn.queue_command('TEST_COMMAND\x03')
    assert len(conn.command_queue) == 1
    assert conn.command_queue[0] == 'TEST_COMMAND\x03'

def test_process_queue(mock_serial):
    conn = Connection('/dev/test')
    conn.queue_command('TEST_COMMAND\x03')
    mock_serial.return_value.read_until.return_value = b'RESPONSE'
    # Allow some time for the thread to process the command
    time.sleep(0.5)
    assert len(conn.response_queue) == 1
    assert conn.response_queue[0] == 'RESPONSE'

def test_process_2_commands(mock_serial):
    conn = Connection('/dev/test')
    conn.queue_command('COMMAND_1\x03')
    conn.queue_command('COMMAND_2\x03')
    mock_serial.return_value.read_until.return_value = b'RESPONSE'
    # Allow some time for the thread to process the commands
    time.sleep(0.2)
    assert len(conn.response_queue) == 1
    assert conn.response_queue[0] == 'RESPONSE'
