#from serialHandler import SerialHandler
from stateInterpreter import MatrixStateParser
from reachableEndStates import get_reachable_end_states, actions_to_reach
from canonicalKeyGen import canonical_key, key_to_dict

# Read current state from serial port (In dict from)
# Input data from dict form to reacahability module
# Dict to canonical key
# Load reachabili.ndjson
# Compare current state to reachable state S0
# Return list of reachable end states S1 keys
# Key to dict of desired end state. 
# Return list of actions to reach each S1 from S0

if __name__ == "__main__":
    #serial_handler = SerialHandler(baudrate=9600)

    # Example current state read from serial port
    #current_state = serial_handler.read_state()
    current_state_matrix = [[28, 0, 0, 0],
                            [0, 12, 0, 90],
                            [0, 0, 0, 90],
    ]

    stateParser = MatrixStateParser()
    current_state = stateParser.matrix_to_state(current_state_matrix)
    print("Current State:", current_state)

    reachable_states = get_reachable_end_states(current_state)
    print("Reachable End States:", reachable_states)


    # For each reachable state, get actions to reach it
    for target_key in reachable_states:
        target_state = key_to_dict(target_key)
        actions = actions_to_reach(current_state, target_state)
        print(f"Actions to reach {target_key}:", actions)