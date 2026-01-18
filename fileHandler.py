import json
import csv
import os
from collections import defaultdict
from canonicalKeyGen import canonical_key, key_to_json, state_to_dict
    

def export_control_sequence(sequence, filepath="control_sequence.json"):
    command_list = []

    for step in sequence:
        for action in step["actions"]:
            if "inflate" in action:
                command = {
                    "time": step["time"],
                    "command": "inflate" if action["inflate"] else "deflate",
                    "target": action["actuator"]
                }
            elif action.get("action") == "disconnect":
                command = {
                    "time": step["time"],
                    "command": "disconnect",
                    "target": action["target"]
                }
            else:
                continue

            command_list.append(command)

    with open(filepath, "w") as f:
        json.dump(command_list, f, indent=2)
    print(f"Exported control sequence to {filepath}")


def freeze(obj):
    """
    Recursively convert lists to tuples so the structure becomes hashable.
    """
    if isinstance(obj, list):
        return tuple(freeze(x) for x in obj)
    elif isinstance(obj, dict):
        return tuple(sorted((k, freeze(v)) for k, v in obj.items()))
    else:
        return obj
    

def load_reachability(filename):
    cache = {}

    if not os.path.exists(filename):
        return cache

    with open(filename, "r") as f:
        for line in f:
            record = json.loads(line)

            s0_key = freeze(record["s0"])
            s1_keys = [freeze(s1) for s1 in record["s1"]]

            cache[s0_key] = s1_keys

    return cache


def save_reachability_keys(transitions, filename):
    
    transition_map = defaultdict(set)

    # Group S1s by S0
    for s0, s1 in transitions:
        k0 = canonical_key(state_to_dict(s0))
        k1 = canonical_key(state_to_dict(s1))
        transition_map[k0].add(k1)

    with open(filename, "w") as f:
        for k0, s1_keys in transition_map.items():
            record = {
                "s0": key_to_json(k0),
                "s1": [key_to_json(k1) for k1 in s1_keys]
            }
            f.write(json.dumps(record) + "\n")

    print(f"Saved {len(transition_map)} grouped S0 states to {filename}")