# Read a configuration matrix from a serial port (Sent by control module)

import serial
import serial.tools.list_ports
from stateInterpreter import MatrixStateParser

class SerialHandler:
    def __init__(self, serial_port="", baudrate=9600, modules=5, ports=4):
        self.port = self.find_port(serial_port)
        self.baudrate = baudrate
        self.rows = modules
        self.cols = ports   # Number of ports + bend angle
        self.ser = serial.Serial(self.port, baudrate, timeout=1)
        if self.ser.is_open:
            print(f"Serial port {self.port} opened at {baudrate} baud.")
        else:
            print(f"Failed to open serial port {self.port}.")

    def find_port(self, default_port=""):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "COM" in port.description:
                print(f"Using port: {port.device}")
                return port.device
        print(f"Defaulting to port: {default_port}")
        return default_port
    
    def send_line(self, line: str):
        self.ser.write((line + "\n").encode("utf-8"))
        print("Sent:", line.strip())

    def close(self):
        self.ser.close()
    
    def read_matrix(self):
        config_matrix = []
        while True:
            if self.ser.in_waiting >= 0:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    row = list(map(int, line.split(',')))
                    config_matrix.append(row)
                
                    if len(config_matrix) == self.rows:
                        break
        return config_matrix

    def read_state(self):
        matrix = self.read_matrix()
        parser = MatrixStateParser()
        state = parser.matrix_to_state(matrix)
        return state

if __name__ == '__main__':
    reader = SerialHandler()
    matrix = reader.read_matrix()
    print(matrix)