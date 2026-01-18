from collections import deque
from canonicalKeyGen import canonical_key

class MatrixStateParser:
    def __init__(self):
        pass

    #Initializes module in state representation
    def empty_module(self):
        return {
                    "bend": 0,
                    "orient" : 0,
                    "P1": None, "P2": None, "P3": None
                }
                
    def matrix_to_state(self, matrix): # Converts configuration matrix to a state representation
        state = {}
        connections = []

        for module_idx, row in enumerate(matrix):
            m1 = f"M{module_idx+1}"
            state.setdefault(m1, self.empty_module())
            
            for port_idx, val in enumerate(row):
                p1 = f"P{port_idx+1}"

                # 1 indicates the presence of the control module
                if abs(val) == 1:
                    orient = 1 if val < 0 else 0
                    state.setdefault(m1, self.empty_module())
                    state[m1][p1] = ("M0", "P0")
                    connections.append(("M0", m1, orient))
                    
                elif val != 0 and port_idx < 3:  # For ports only (not bend angle)
                    orient = 1 if val < 0 else 0
                    val = abs(val)

                    # Decodes actuator number and port number
                    binary_val = format(val, '08b')
                    p2 = f"P{int(binary_val[-3:], 2)}"
                    m2 = f"M{int(binary_val[:5], 2)}"

                    state.setdefault(m2, self.empty_module())
                
                    #Saves port connection data
                    state[m1][p1] = (m2, p2)
                    connections.append((m1, m2, orient))

                elif port_idx == 3:  # Save bend angle only if module exists
                    state[m1]["bend"] = f"B{val}"

        # Propagate orientations based on connections
        self.propagate_orientation(state, connections)

        return state

    def propagate_orientation(self, state, connections):
        # Build adjacency list
        graph = {}

        for m1, m2, flip in connections:
            graph.setdefault(m1, []).append((m2, flip))
            graph.setdefault(m2, []).append((m1, flip))  # bidirectional

        # Control module orientation is fixed
        orientation = {"M0": 0}

        queue = deque(["M0"])

        while queue:
            current = queue.popleft()
            for neighbor, flip in graph.get(current, []):
                if neighbor not in orientation:
                    orientation[neighbor] = (orientation[current] + flip) % 2
                    queue.append(neighbor)

        # Assign orientations back to state
        for m in state:
            state[m]["orient"] = f"O{orientation.get(m, 0)}"

    def state_canonical_key(self, state):
        return canonical_key(state)

if __name__ == "__main__":
    matrix = [[28, 0, 0, 0],
              [0, 12, 0, 90],
              [-1, 0, 0, 0],
    ]
    stateParser = MatrixStateParser()
    state = stateParser.matrix_to_state(matrix)
    key = stateParser.state_canonical_key(state)
    print(key)