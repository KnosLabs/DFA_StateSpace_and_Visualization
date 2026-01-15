from visualizer import ModularVisualizer
from fileHandler import export_transitions
import time
import csv

from itertools import product, permutations

class StateGenerator:
    def __init__(self, num_modules):
        self.num_modules = num_modules
        self.current_state = None 
        self.femalePorts = ["P1", "P2", "P3"]
        self.malePorts = ["P4", "P5", "P6"]
        self.orientations = ["O1", "O2"]
        self.bend_states = ["B0", "B90", "B180"]
        self.occupied = {}

        self.states = set()  
        self.state_maps = {}  
        self.transitions = []
       
        self.generate_topologies()
        self.expand_with_bend_angles()
        self.generate_transitions()
       
    def generate_topologies(self):
        self.topology_states = set()

        for num_connected in range(1, self.num_modules + 1):
            for modules in permutations(range(1, 1+self.num_modules), num_connected):
                modules = (0,) + modules  # Adds control module (0) to every state
                
                state_items = [[] for _ in range(len(modules)-1)]
                for i, module in enumerate(modules):
                    next_module = modules[i + 1]
                    # Generate all control module elements in states
                    if i == 0:
                        for fPort, orientation in product(self.femalePorts, self.orientations):
                            state_items[i].append(f'M{next_module}_{fPort}', f'M0_P0_{orientation}')

                    if i < len(modules) - 1 and i != 0:
                        for j in range(i):
                            for mPort, fPort, orientation in product(self.malePorts, self.femalePorts, self.orientations):
                                state_items[i].append(f'M{modules[i-j]}_{fPort}', f'M{next_module}_{mPort}_{orientation}') 
                             
                        for k in range(i):
                            for mPort, fPort, orientation in product(self.malePorts, self.femalePorts, self.orientations):  
                                state_items[i].append(f'M{next_module}_{fPort}', f'M{modules[i-k]}_{mPort}_{orientation}') 

                for combo in product(*state_items):
                    if self.valid_topology(combo):
                        self.topology_states.add(frozenset(combo))

            """
                # Linear spatial states (ring formation)
                state_items = [[] for _ in range(len(modules))]
                for i, module in enumerate(modules):
                    if i == 0:
                        for fPort in ["P2", "P3"]:
                            state_item = (f'M{modules[i+1]}_{fPort}', f'M0_P0_O1')
                            state_items[i].append(state_item)
                            
                    if i < len(modules) - 1 and i != 0:
                        state_item = (f'M{modules[i+1]}_P1', f'M{modules[i]}_P4_O1')  
                        state_items[i].append(state_item)

                    # Attaches last module to port of the first to create a ring formation
                    if i == len(modules) - 1 and i > 1:
                        state_item = (f'M{modules[1]}_P1', f'M{modules[i]}_P4_O1') 
                        state_items[i].append(state_item)

                for combo in product(*state_items):
                    self.topology_states.add(frozenset(combo))
            """
    
    def valid_topology(self, combo):
        used = set()
        for pair in combo:
            for conn in pair:
                m, p = conn.split("_")[:2]
                if (m, p) in used:
                    return False
                used.add((m, p))
        return True

    def map_topology(self, topo_state):
        state = {}

        for a, b in topo_state:
            m1, p1 = a.split("_")[:2]
            m2, p2, o = b.split("_")

            state.setdefault(m1, {"ports": {}})["ports"][p1] = (m2, p2, o)
            state.setdefault(m2, {"ports": {}})["ports"][p2] = (m1, p1, o)

        return state

    def generate_transitions_for_state(self, state):
        possible_actions = self.generate_possible_actions()
        for action in possible_actions:
            new_state = self.apply_action(state, action)
            if new_state in self.states:
                self.add_transition(state, action, new_state)


    def add_transition(self, from_state, action, to_state, reset=False):
        if from_state not in self.states or to_state not in self.states:
            raise ValueError(f"Both from_state '{from_state}' and to_state '{to_state}' are not valid states.")
        self.transitions[(from_state, action)] = to_state

    #Generates all possible actions between states
    def generate_possible_actions(self):
        actions = []
        for i in range(self.num_modules):

            #Control module connections
            for fPort, orientation in product(self.femalePorts, self.orientations):        
                        actions.append(f'connect_M{i+1}_{fPort}_M0_P0_{orientation}')

            #Module connections
            for j in range(self.num_modules):
                if i != j:
                    for mPort, fPort, orientation in product(self.malePorts, self.femalePorts, self.orientations):
                        actions.append(f'connect_M{i+1}_{fPort}_M{j+1}_{mPort}_{orientation}')
            #Module disconnections
            for fPort in self.femalePorts:
                actions.append(f'disconnect_M{i+1}_{fPort}')

            #Bending actions    
            for b in self.bend_states:
                actions.append(f'bend_M{i+1}_{b}')
        return actions
    

    #Applies possible actions to produce new states
    def apply_action(self, state, action):
        state_dict = dict(state)
        parts = action.split('_')  
        """
        if 'M0' in action:
            module, fPort, orient = parts[1], parts[2], parts[5]
            state_dict[f'{module}_{fPort}'] = f'M0_P0_{orient}'

        elif 'disconnect' in action:
            # Module-to-module disconnect
            module, fPort = parts[1], parts[2]
            state_dict.pop(f'{module}_{fPort}', None)

        elif 'connect' in action:
            module, nextModule = parts[1], parts[3] # Extract module nnumbers
            fPort, mPort, orient = parts[2], parts[4], parts[5] # Connection points
            state_dict[f'{module}_{fPort}'] = f'{nextModule}_{mPort}_{orient}'
        """
        if 'M0' in action:
            module, fPort, orient = parts[1], parts[2], parts[5]
            state_dict[f'{module}_{fPort}'] = f'M0_P0_{orient}'

        elif 'disconnect' in action:
            # Module-to-module disconnect
            module, fPort = parts[1], parts[2]
            state_dict[module].pop(fPort, None)

        elif 'connect' in action:
            module, nextModule = parts[1], parts[3] # Extract module nnumbers
            fPort, mPort, orient = parts[2], parts[4], parts[5] # Connection points
            state_dict[module][fPort] = (nextModule, mPort, orient)

        elif 'bend' in action:
            module, bend_state = parts[1], parts[2]
            state_dict[module]['bend'] = bend_state
        
        return frozenset(state_dict.items())
    
    
    def perform_action(self, action):
        if self.current_state is None:
            raise ValueError("Start state is not set.")
        
        if (self.current_state, action) in self.transitions:
            new_state = self.transitions[(self.current_state, action)]
            print(f"Transitioning from {self.current_state} to {new_state} on action '{action}'")
            self.current_state = new_state
        
            visualizer = ModularVisualizer()
            visualizer.visualize_configuration(self.current_state)
        else:
            print(f"No valid transition from state '{self.current_state}' on action '{action}'")


    def action_config_matrix(self, matrix):
        actions = []
        for module_idx, row in enumerate(matrix):
            for port_idx, val in enumerate(row):
                occupied_key = (module_idx, port_idx)

                # 1 indicates the presence of the control module
                if val == 1:
                    if occupied_key not in self.occupied:
                        self.occupied[occupied_key] = True
                        actions.append(f'connect_M{module_idx+1}_P{port_idx+1}_M0_P0_O1')

                # Non-zero indicates an actuator is connected on that port
                elif val != 0:
                    if occupied_key not in self.occupied:
                        self.occupied[occupied_key] = True

                        # Decodes actuator number and port number
                        binary_val = format(val, '08b')
                        port_num = int(binary_val[-3:], 2)
                        module_num = int(binary_val[:5], 2)

                        actions.append(f'connect_M{module_idx+1}_P{port_idx+1}_M{module_num}_P{port_num}_O1')
                        print(f'M{module_idx+1}_P{port_idx+1}_M{module_num}_P{port_num}')
                else: 
                    # If status of port changes (value to zero), disconnect actuator 
                    if occupied_key in self.occupied:
                        actions.append(f'disconnect_M{module_idx+1}_P{port_idx+1}')
                        self.occupied.pop(occupied_key)

        print(actions)

        ## Makes sure that control module is first action (for visualization)
        for action in actions:
            if "M0" in action:
                self.perform_action(action)
            time.sleep(.5)

        for action in actions:
            self.perform_action(action)
            time.sleep(.5)   

    # Will remove 
    def export_transitions(self, filename='transitions.csv'):
        # Prepare data 
        def state_to_map(state):
            # state is a frozenset of (key, val) pairs where key is like 'M1_P2'
            # and val is like 'M2_P4_O1' or 'M0_P0_O1'. We produce:
            # { 'M1_B0': { 'P2': 'M2_P4_O1', ... }, ... }
            mapping = {}
            for k, v in state:
                if not k:
                    continue
                parts = k.split('_')
                if len(parts) < 2:
                    continue
                mod = parts[0]  # e.g. 'M1'
                port = parts[1]  # e.g. 'P2'
                if mod not in mapping:
                    mapping[mod] = {}
                mapping[mod]["bend"] = 'B0'  # Default bend state
                mapping[mod][port] = v
            return mapping

        csv_data = []
        for (from_state, action), to_state in self.transitions.items():
            from_map = state_to_map(from_state)
            to_map = state_to_map(to_state)
            csv_data.append([str(from_map), action, str(to_map)])

        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['From State', 'Action', 'To State'])  # header
            writer.writerows(csv_data)

        print(f"Transitions exported to {filename}")

    def get_mapped_transitions(self):
        # Returns transitions with states mapped to actuator-port mapping form
        def state_to_map(state):
            mapping = {}
            for k, v in state:
                parts = k.split('_')
                if len(parts) < 2:
                    continue
                mod = parts[0]
                port = parts[1]
                act_key = f"{mod}_B0"
                mapping.setdefault(act_key, {})[port] = v
            return mapping

        mapped = {}
        for (from_state, action), to_state in self.transitions.items():
            mapped[(frozenset(state_to_map(from_state).items()), action)] = frozenset(state_to_map(to_state).items())
        return mapped


if __name__ == "__main__":
    num_modules = 2
    stateGen = StateGenerator(num_modules)
    #stateGen.export_transitions()
    export_transitions(stateGen.transitions)
    
    while True:
        matrix = [[20, 1, 0],
                    [0,  0, 0],  
                    [0,  0, 0]    
        ]

        #matrix = read_matrix_from_serial(port='/dev/cu.usbmodem14401', baudrate=9600)
        stateGen.action_config_matrix(matrix)
        time.sleep(10)