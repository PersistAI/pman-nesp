import serial

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

    def close(self):
        # Close the serial connection
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
            return self.connection.readline().decode().strip()

# Example usage
if __name__ == "__main__":
    conn = Connection("COM3")  # Replace COM3 with your port
    conn.send("Hello")
    print(conn.receive())
    conn.close()

