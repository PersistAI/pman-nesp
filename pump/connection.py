import serial
# Start transmission
STX = '\x02'
# End transmission
ETX = '\x03'
CR = '\r'

baudrate=9600
class Connection:
    """
    Manages the serial connection between server and instruments
    multiple Pumps can depend on a single connection
    """
    def __init__(self, port):
        try:
            self.connection = serial.Serial(port, baudrate)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Failed to connect on {port}: {e}")

    def open(self, port):
        if self.connection.is_open:
            return
        try:
            self.connection = serial.Serial(port, baudrate)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Failed to connect on {port}: {e}")

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Connection closed")

    def send(self, data):
        # Send data to the serial port
        if self.connection and self.connection.is_open:
            self.connection.write(data.encode())

    def receive(self):
        # Receive data from the serial port
        if self.connection and self.connection.is_open:
            return self.connection.read_until(ETX.encode()).decode().strip()

    def terminal(self, timeout=5):
        """
        For communicating directly with a pump
        Great for troubleshooting
        """
        if self.connection:
            print("setting timeout to:",timeout)
            self.connection.timeout = timeout
        while True:
            data = input("$: ") + '\r'
            if data =='exit\r':
                return
            if self.connection and self.connection.is_open:
                self.connection.write(data.encode())
                response = self.connection.read_until(ETX.encode())
                print(response)
            else:
                print("no connection")

# Example usage
if __name__ == "__main__":
    conn = Connection('COM24')
    conn.terminal()
