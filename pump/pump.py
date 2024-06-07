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
    def __init__(self, connection, address=0, logger=None, hardstop_flags=[False,False]):
        self.connection = connection # serial connection manager
        self.address = address
        self.logger = logger
        self.hardstop_flags = hardstop_flags # must be a list so it can be changed from outside
        pass
    def _log(self, msg):
        if self.logger:
            self.logger.debug(msg)

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

    def parse_response(self, response):
        """
        Parses the response and categorizes it based on predefined meanings.
        Args:
        response (str): The response to be parsed and categorized.
            response[-2] is one of the below:
            W: withdrawing 
            I: infusing
            T: Timed Pause Phase
            X: Purging
            P: Pumping Program Paused
            U: Operational trigger wait (user wait)
            S: standby
            A: alarm
            '': timeout (because no response)

        Returns:
        str: The categorization based on the identified meaning from the response. Possible categories include:
            'busy': Indicates that the system is busy performing a certain operation (e.g., withdrawing, infusing, etc.).
            'paused': Indicates that the system is in a paused state (e.g., pumping program paused, operational trigger wait, etc.).
            'standby': Indicates that the system is in a standby state.
            'error': Indicates that an error has occurred.
            'unknown': Indicates that the meaning of the response could not be categorized.
        """
        meanings = {
         ('W', 'I', 'T', 'X'): 'busy',
         ('P', 'U'): 'paused',
         ('S',): 'standby',
         ('A',): 'error'
        }

        if response == '':
            return 'timeout'

        # response format with A? must be parsed differently 
        # for example, if A? is present, 'S' means stall, not 'standby'
        # for now, just treat as error
        if 'A?' in response:
            return 'error'

        for key in meanings:
            if any(letter in response for letter in key):
                return meanings[key]
        return 'unknown'

    def wait_for_motor(self):
        """ Wait for the motor to enter standby """
        self._log("initiated pump.wait_for_motor()")
        command = CommandName.PUMP_MOTOR_OPERATING
        command = self._formatCommand(command)
        response = self._queueCommand(command)
        status = self.parse_response(response)
        self._log(f"response: {response} pump status: {status}")
        # if it's not in standby, you keep waiting
        while status in ['busy', 'paused', 'error', 'unknown','timeout'] and not self.hardstop_flags[int(self.address)]:
            time.sleep(1)
            response = self._queueCommand(command)
            status = self.parse_response(response)
            self._log(f"response: {response} pump status: {status}")
        if self.hardstop_flags[int(self.address)]:
            self._log(f"hardstop hit -- no longer waiting for pump")
            # now we set the hardstop flag back to False to acknowledge that we have already stopped
            # if we do not do this, the scheduler will never short poll again unless "resume" is hit
            self.hardstop_flags[int(self.address)] = False

        return True

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
