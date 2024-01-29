import serial
import time
import threading
from collections import deque
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
    def __init__(self, port,timeout=2):

        self.command_queue = deque() # basically a list but optomized to act as a queue
        self.response_queue = deque()
        self.queue_lock = threading.Lock()  # Lock to ensure thread-safe operations on queues
        self.queue_condition = threading.Condition(self.queue_lock)  # Helps optimize wait times in process_queue()
        self.processing_thread = threading.Thread(target=self.process_queue)
        self.processing_thread.daemon = True  # Ensures thread exits when main program does, among other things
        self.processing_thread.start()

        try:
            self.connection = serial.Serial(port, baudrate, timeout=timeout)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Failed to connect on {port}: {e}")

    def queue_command(self, command_data):
        with self.queue_lock:
            self.command_queue.append(command_data)

    def get_response(self):
        with self.queue_condition:
            while not self.response_queue:
                self.queue_condition.wait()
            
            with self.queue_lock:
                response = self.response_queue.popleft()
        return response
    
    def process_queue(self):
        while True:
            with self.queue_condition:
                while not self.command_queue:
                    self.queue_condition.wait()  # Wait for a signal that a command has been added
                command_data = self.command_queue.popleft()

            self.send(command_data)
            response = self.receive()

            with self.queue_lock:  # Just need the lock here as we're not working with the condition
                self.response_queue.append(response)

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
        Great for troubleshooting but only used for dev and debug purposes
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
