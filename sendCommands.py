# Class to send commands to control module via serial communication.
# Commands are based on actions defined by the model checker.

import serial

class SendCommands:
    def __init__(self, modules, serial_port='/dev/cu.usbmodem14401', baud_rate=9600):
        self.col = 4    # Number of "active" ports + bend angle (inflate command))
        self.rows = modules
        self.serial_port = serial_port
        self.baud_rate = baud_rate


    def actions_to_matrix(self, actions):
        control_matrix = [[0 for _ in range(self.col) ] for _ in range(self.rows)] # Initializes matrix with 0
        for action in actions:
            parts = action.split('_') 
            module_idx = int(parts[1][1:]) - 1
            port_idx = int(parts[2][1:]) - 1
            
            if parts[0] == "connect":
                control_matrix[module_idx][port_idx] = 1
                # Temp in progress, determine how to set bend angle based on model checker action
                control_matrix[module_idx][3] = 90  # Example: Set bend angle to 90 degrees when connecting
            if parts[0] == 'disconnect':
                control_matrix[module_idx][port_idx] = -1
        
        return control_matrix

    def write_actions_matrix(self, actions):
        matrix = self.actions_to_matrix(actions)
        with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
            for row in matrix:
                row_data = ','.join(map(str, row)) + '\n'
                ser.write(row_data.encode('utf-8'))
                ser.flush()
                print(f"Sent: {row_data.strip()}") 
        ser.write("END\n".encode('utf-8'))


if __name__ == '__main__':
    command = SendCommands(modules=3)

    actions = ["connect_M1_P1_M2_P4", "disconnect_M3_P3"]
    print(command.actions_to_matrix(actions))
    #command.write_actions_matrix(actions)


