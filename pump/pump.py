import enum
import serial
import time
import threading

serial_lock = threading.Lock()

# windows does not let us share com ports, so we use these flags
# to tell the polling functions to stop hogging the serial lines 
# when it is time to stop

emergency_stop_flag = threading.Event()

ETX = '\x03'
STX = '\x02'
CR = '\r'

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
    def __init__(self, ser, address:int=0, logger=None):
        self.ser = ser
        self.address = address
        self.logger = logger
        pass

    def send_command(self, data):
        self.ser.write( data.encode())
        return self.ser.read_until(ETX.encode()).decode()

    def _log(self, msg):
        if self.logger:
            self.logger.debug(msg)

    def _formatArg(self,arg):
        """ take in a float and return a string rounded to 2 decimal places """
        return str(round(float(arg),2))

    def _formatCommand(self, command_data):
        """
        input: command data 
        output: command string ready to send
        """
        return str(self.address) + command_data + CR

    def run(self):
        with serial_lock:
            command = CommandName.RUN
            command = self._formatCommand(command)
            r = self.send_command(command)
        return r

    def stop(self):
        with serial_lock:
            command = self._formatCommand(CommandName.STOP)
            r = self.send_command(command)
        return r

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
        with serial_lock:
            response = self.send_command(command)
            status = self.parse_response(response)
            self._log(f"response: {response} pump status: {status}")
            # if it's not in standby, you keep waiting
            while status in ['busy', 'paused', 'error', 'unknown','timeout'] and not emergency_stop_flag.is_set():
                time.sleep(0.25)
                response = self.send_command(command)
                status = self.parse_response(response)
        return True

    def set_direction(self, direction):
        """
        direction: either INF or WDR
        """
        with serial_lock:
            command = CommandName.PUMPING_DIRECTION + direction.upper()
            command = self._formatCommand(command)
            r = self.send_command(command)
        return r

    def set_volume(self, volume):
        """
        volume: units of ML, a float, string, or int
        """
        with serial_lock:
            volume = self._formatArg(volume) # rounds and returns str
            command = CommandName.PUMPING_VOLUME + volume
            command = self._formatCommand(command)
            r = self.send_command(command)
        return r

    def set_rate(self, rate):
        """
        rate: units of mL/Min, a float, string, or int
        """
        with serial_lock:
            rate = self._formatArg(rate) # rounds and returns str
            command = CommandName.PUMPING_RATE + rate
            command = self._formatCommand(command)
            ret = self.send_command(command)
        return ret

if __name__ == "__main__":
    import doctest
    doctest.testmod()
