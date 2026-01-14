# Read a configuration matrix from a serial port (Sent by control module)

import serial
import serial.tools.list_ports

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
    
    def matrix_to_state(self, matrix): # Converts configuration matrix to a state representation
        read_state = {}
        for module_idx, row in enumerate(matrix):
            for port_idx, val in enumerate(row):

                # 1 indicates the presence of the control module
                if val == 1:
                    read_state[f'M{module_idx+1}_P{port_idx+1}'] = f'M0_P0_O1'

                elif val != 0:
                    if val < 0:     #If value is negative, switch orientation
                        val = -val
                        orient = 2
                    else:
                        orient = 1

                     # Decodes actuator number and port number
                    binary_val = format(val, '08b')
                    port_num = int(binary_val[-3:], 2)
                    module_num = int(binary_val[:5], 2)

                    read_state[f'M{module_idx+1}_P{port_idx+1}'] = f'M{module_num}_P{port_num}_O{orient}'

        return frozenset(read_state.items())
    
    def read_state(self):
        matrix = self.read_matrix()
        state = self.matrix_to_state(matrix)
        return state
    

if __name__ == '__main__':
    reader = SerialHandler()
    matrix = reader.read_matrix()
    print(matrix)