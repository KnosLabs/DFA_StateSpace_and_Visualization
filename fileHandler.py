import json
import csv

@staticmethod
def import_transitions(filename='transitions.csv'):
    transitions = {}

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader) 

        for row in reader:
            from_state_str = row[0] 
            action = row[1]          
            to_state_str = row[2]   

            from_state = eval(from_state_str)
            to_state = eval(to_state_str)  

            transitions[(from_state, action)] = to_state

    print(f"Transitions imported from {filename}") 
    return transitions   
    

@staticmethod
def export_transitions(transitions, filename='transitions.csv'):
    # Prepare data 
    csv_data = []
    for (from_state, action), to_state in transitions.items():
        from_state_str = str(from_state)  # Convert frozenset to string
        to_state_str = str(to_state) 
        csv_data.append([from_state_str, action, to_state_str]) 

    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['From State', 'Action', 'To State'])  # header
        writer.writerows(csv_data) 

    print(f"Transitions exported to {filename}")
    

@staticmethod
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

