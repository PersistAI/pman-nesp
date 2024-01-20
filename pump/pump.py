import enum
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

    def _sendCommand(self, command_string):
        self.connection.send(command_string)
        return self.connection.receive()

    def run(self):
        command = CommandName.RUN
        command = self._formatCommand(command)
        return self._sendCommand(command)

    def set_direction(self, direction):
        """
        direction: either INF or WDR
        """
        command = CommandName.PUMPING_DIRECTION + direction.upper()
        command = self._formatCommand(command)
        return self._sendCommand(command)

    def set_volume(self, volume):
        """
        volume: units of ML, a float, string, or int
        """
        volume = str(volume) + 'ML'
        command = CommandName.PUMPING_VOLUME + volume
        command = self._formatCommand(command)
        return self._sendCommand(command)

    def set_rate(self, rate):
        """
        rate: units of mL/Min, a float, string, or int
        """
        rate = str(rate) + 'MM'
        command = CommandName.PUMPING_VOLUME + rate
        command = self._formatCommand(command)
        return self._sendCommand(command)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
