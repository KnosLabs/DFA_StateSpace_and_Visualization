from fileHandler import load_reachability, save_reachability_keys  
from canonicalKeyGen import canonical_key
from reachability import (
    State,
    ActuatorState,
    ActuatorGeom, 
    enumerate_reachable, 
)

NDJSON_FILE = "reachable.ndjson"

def dict_to_State(state_dict):
    """
    Convert a decoded dictionary state into a NEW State instance for reachability.
    """
    actuators = {}
    connections = set()
    geoms = {}

    for mid, data in state_dict.items():
        actuators[mid] = ActuatorState(
                mid=int(mid[1:]),
                orientation=data["orient"],
                bend=data["bend"],
                ports=set(),
            )
  
    for m1, data in state_dict.items():
        for p1 in ("P1", "P2", "P3"):
            target = data[p1]
            if target is None:
                continue

            m2, p2 = target

            # Add ports to both actuators
            actuators[m1].ports.add(p1)
            actuators[m2].ports.add(p2)

            # Add undirected connection
            connections.add(((m1, p1), (m2, p2)))

        # Create simple geometry for each actuator present in state
        geoms[int(m1[1:])] = ActuatorGeom(mid=int(m1[1:]), x=int(m1[1:]) - 1, y=0)

    return State(actuators=list(actuators.values()), connections=connections), geoms


def get_reachable_end_states(current_state):

    # Always create a NEW State instance
    current_key = canonical_key(current_state)

    # Load cache
    cache = load_reachability(NDJSON_FILE)

    # Case 1: S0 already known
    if current_key in cache:
        print("Found matching S0 in cache")
        return cache[current_key]

    print("No matching S0 — running reachability")
    State, geoms = dict_to_State(current_state)

    transitions = enumerate_reachable(State, geoms)
    save_reachability_keys(transitions, NDJSON_FILE)

    cache = load_reachability(NDJSON_FILE)

    if current_key in cache:
        print("Found matching S0 in cache")
        return cache[current_key]
    else:
        print("No reachable end states found")
        return 


def actions_to_reach(s0_dict, s1_dict):
    """
    Generate actions required to go from S0 → S1.
    """
    """
    Generate a minimal set of actions to go from s0 to s1.
    """
    actions = []

    for m in s1_dict:
        if m not in s0_dict:
            continue

        # Bend change
        if s0_dict[m]["bend"] != s1_dict[m]["bend"]:
            actions.append(f"bend_{m}_{int(s1_dict[m]['bend'][1:])}")

        # Port changes
        for p in ("P1", "P2", "P3"):
            if s0_dict[m][p] != s1_dict[m][p]:
                if s1_dict[m][p] is None:
                    actions.append(f"disconnect_{m}_{p}")
                else:
                    m2, p2 = s1_dict[m][p]
                    actions.append(f"connect_{m}_{p}_{m2}_{p2}")

    return actions


