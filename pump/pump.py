import enum
from connection import Connection, STX, ETX, CR

class CommandName(str, enum.Enum):
    """
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

    def formatCommand(self, command_data):
        """
        input: command data 
        output: command string ready to send
        """
        return command_data + CR

    def sendCommand(self, command_string):
        self.connection.send(command_string)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
