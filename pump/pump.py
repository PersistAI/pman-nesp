import enum
import time
from .connection import Connection, STX, ETX, CR

class CommandName(str, enum.Enum):
    """
    Exists to make autocomplete easier
    >>> CommandName.RUN.name
    'RUN'
    """
    STATUS             = ''
    SAFE_MODE_TIMEOUT  = 'SAF'
    FIRMWARE_VERSION   = 'VER'
    SYRINGE_DIAMETER   = 'DIA'
    PUMPING_DIRECTION  = 'DIR'
    PUMPING_VOLUME     = 'VOL'
    PUMPING_RATE       = 'RAT'
    DISPENSATION       = 'DIS'
    DISPENSATION_CLEAR = 'CLD'
    RUN                = 'RUN'
    RUN_PURGE          = 'PUR'
    STOP               = 'STP'
    PUMP_MOTOR_OPERATING='ROM' # returns 0 for no or 1 for yes

class Pump:
    """
    Basic mode command:
    [command data]<CR>
    Basic mode response:
    <STX>[response data]<ETX>
    """
    def __init__(self, connection, address=0):
        self.connection = connection
        self.address = address
        pass

    def _formatCommand(self, command_data):
        """
        input: command data 
        output: command string ready to send
        """
        return str(self.address) + command_data + CR

    def _queueCommand(self, command_string):
        self.connection.queue_command(command_string)
        return self.connection.get_response()

    def run(self):
        command = CommandName.RUN
        command = self._formatCommand(command)
        return self._queueCommand(command)

    def stop(self):
        command = self._formatCommand(CommandName.STOP)
        return self._queueCommand(command)

    def wait_for_motor(self):
        # Wait for the motor to be done running
        command = CommandName.PUMP_MOTOR_OPERATING
        command = self._formatCommand(command)
        # response[-2] is either W, I, or S
        # W: withdrawing 
        # I: infusing
        # S: standby
        response = self._queueCommand(command)
        while 'I' in response or 'W' in response:
            time.sleep(1)
            response = self._queueCommand(command)
        return

    def set_direction(self, direction):
        """
        direction: either INF or WDR
        """
        command = CommandName.PUMPING_DIRECTION + direction.upper()
        command = self._formatCommand(command)
        return self._queueCommand(command)

    def set_volume(self, volume):
        """
        volume: units of ML, a float, string, or int
        """
        volume = str(volume)
        command = CommandName.PUMPING_VOLUME + volume
        command = self._formatCommand(command)
        return self._queueCommand(command)

    def set_rate(self, rate):
        """
        rate: units of mL/Min, a float, string, or int
        """
        rate = str(rate)
        command = CommandName.PUMPING_RATE + rate
        command = self._formatCommand(command)
        return self._queueCommand(command)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
