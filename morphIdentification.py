### This is not yet implimented or complete. This wil be used for identifying what configuration the system is in a provide
# a set of commands for control. 

## Configurations to include: Crawler, Pipe Climbing Robot, Rolling Cylinder, ManusBot, TendrilBot

import json
import time
import serial
from readSerial import SerialReader

class RobotController:
    def __init__(self):
        with open("config_templates.json", "r") as file:
            self.CONFIG_TEMPLATES = json.load(file)

        self.transition_state = {}
        self.connections = {}
        self.center_module = None
        self.current_config_name = None
        self.control_sequences = []

        self.ser = serial.Serial('COM13', 9600, timeout=1)

    def parse_state(self, state):
        self.current_state = state
        self.connections = {}

        for key, value in state.items():
            module_a, port_a = key[:2], key[2:]
            module_b, port_b = value[:2], value[2:4]
            orientation_b = value[4:] 

            self.connections.setdefault(module_a, {})
            self.connections.setdefault(module_b, {})

            self.connections[module_a][port_a] = (module_b, port_b)
            self.connections[module_b][port_b] = (module_a, port_a)

    def score_template_at_center(self, center_mod: str, template: dict):
        """
        Returns (resolved_count, total_specs, all_direct_requirements_present_bool).
        - Counts how many structure specs (direct ports and paths) resolve from center_mod.
        - Also checks that all direct center ports required by the template exist on center_mod.
        """
        structure = template["structure"]
        # All specs except "center"
        specs = [s for s in structure.keys() if s not in ("center", "meta")]
        total_specs = len(specs)

        # Direct center-port requirements (e.g., "P1", "P3")
        direct_reqs = [s for s in specs if not self._is_path(s)]
        has_all_direct = all(s in self.connections.get(center_mod, {}) for s in direct_reqs)

        resolved = 0
        for spec in specs:
            if self._is_path(spec):
                path_ports = self._split_path(spec)
                _, _, ok = self._follow_path(center_mod, path_ports)
                if ok:
                    resolved += 1
            else:
                if spec in self.connections.get(center_mod, {}):
                    resolved += 1

        return resolved, total_specs, has_all_direct
    

    def identify_configuration(self):
        if not self.connections:
            return None

        best = (None, None, -1, -1)  # (config_name, center_mod, resolved, total)

        for name, template in self.CONFIG_TEMPLATES.items():
            expected_deg = template["structure"]["meta"]["connections"]

            # Consider every module as a possible center for this template
            for mod, ports in self.connections.items():
                degree = len(ports)
                if degree != expected_deg:
                    continue

                resolved, total, has_all_direct = self.score_template_at_center(mod, template)
                if not has_all_direct:
                    continue  # must at least have required direct center ports

                # Pick the candidate with the most specs resolved; break ties by higher total
                if (resolved, total) > (best[2], best[3]):
                    best = (name, mod, resolved, total)

        self.current_config_name, self.center_module, _, _ = best
        return self.current_config_name
    
    @staticmethod
    def _is_path(spec: str) -> bool:    #Cecks if the spec is a path (contains '>') or a direct port connection
        return ">" in spec

    @staticmethod
    def _split_path(spec: str):
        # Ex. 'P3>P1>P6' -> ['P3', 'P1', 'P6']
        return [s.strip() for s in spec.split(">") if s.strip()]

    def _follow_path(self, start_module: str, path_ports: list[str]):
        """
        From start_module, follow a sequence of ports.
        Returns (final_module, final_port, succeeded_bool).
        """
        current_mod = start_module
        last_port = None

        for port in path_ports:
            if port not in self.connections[current_mod]:
                return (None, None, False)
            neighbor_mod, neighbor_port = self.connections[current_mod][port]
            # Step to neighbor
            last_port = neighbor_port
            current_mod = neighbor_mod

        return (current_mod, last_port, True)
    

    def assign_roles(self):
        if not self.current_config_name:
            self.identify_configuration()
        if not self.current_config_name:
            raise ValueError("No matching configuration identified.")

        template = self.CONFIG_TEMPLATES[self.current_config_name]
        structure = template["structure"]

        center_role_name = structure["center"]

        role_map = {self.center_module: center_role_name}
        reverse_role_map = {center_role_name: self.center_module}

        center_ports = self.connections[self.center_module]

        for spec, role in structure.items():
            if spec in ("center", "meta"):
                continue

            # Check if spec is a path or a direct port on center module
            if self._is_path(spec):
                # Multi-hop path
                path_ports = self._split_path(spec)
              
                target_mod, _, ok = self._follow_path(self.center_module, path_ports)
                if ok and target_mod:
                    # collision check
                    if role in reverse_role_map and reverse_role_map[role] != target_mod:
                        raise ValueError(
                            f"Conflict: Role {role} maps to multiple modules: "
                            f"{reverse_role_map[role]} and {target_mod}"
                        )
                    role_map[target_mod] = role
                    reverse_role_map[role] = target_mod
            
            else:
                # Direct neighbor: spec is a port on center
                if spec in center_ports:
                    neighbor_mod, _ = center_ports[spec]
                    if role in reverse_role_map and reverse_role_map[role] != neighbor_mod:
                        raise ValueError(
                            f"Conflict: Role {role} maps to multiple modules: "
                            f"{reverse_role_map[role]} and {neighbor_mod}"
                        )
                    role_map[neighbor_mod] = role
                    reverse_role_map[role] = neighbor_mod
                else:
                    # Required direct port not present; should not happen if identified correctly
                    raise ValueError(f"Required port {spec} not found on center module {self.center_module}.")

        return role_map  # module_id -> role
    
    @staticmethod
    def resolve_expression(expr, params):
        if isinstance(expr, (int, float)):
            return expr
        if isinstance(expr, str) and expr.startswith("@"):
            # Remove '@' and evaluate with params
            expr = expr[1:]
            return eval(expr, {}, params)
        return expr

    def generate_timed_sequence(self):
        role_map = self.assign_roles()
        commands = self.CONFIG_TEMPLATES[self.current_config_name]["control"]
        self.control_sequences = []

        for command_name, command in commands.items():
            params = command.get("params", {})  #Parameters for expressions (time, duration, etc)
            tracks = command.get("tracks", {})  #Commands for each role
            for role, steps in tracks.items():
                current_time = 0.0
                for step in steps:
                    if "at" in step:
                        time = self.resolve_expression(step["at"], params)
                        current_time = time
                    elif "dt" in step:
                        time = current_time + self.resolve_expression(step["dt"], params)
                        current_time = time
                    else:
                        print("Error: No time specified in step.")
                        continue

                    module_id = next((k for k, r in role_map.items() if r == role), None)[1]
                    
                    if "inflate" in step["set"]:
                        action = "inflate" 
                        value = step["set"]["inflate"]
                    elif "connect" in step["set"]:
                        action = "connect"
                        value = step["set"]["connect"][1] 
                    elif "disconnect" in step["set"]:
                        action = "disconnect"
                        value = step["set"]["disconnect"][1]
                    else:
                        print("Error: No valid action in step.")
                        continue
                    
                    self.control_sequences.append({"command": command_name, "time": time, "module": module_id, "action": action, "value": value})

        self.control_sequences.sort(key=lambda x: (x["command"], x["time"]))            
        return self.control_sequences
    
    def update_configuration(self, matrix):
        self.parse_state(matrix)
        self.identify_configuration()
        self.generate_timed_sequence()
    
    def get_command_sequence(self, command_name):
        all_sequences = self.control_sequences
        return [s for s in all_sequences if s["command"] == command_name]

    
    def send_command(self, sequence):
        if not self.ser or not self.ser.is_open:
            print("Error: Serial connection not open.")
            return

        for step in sequence:
            line = f"{step['command']},{step['time']},{step['module']},{step['action']},{step['value']}\n"
            self.ser.write(line.encode("utf-8"))
            print("Sent:", line.strip())
            time.sleep(0.05)

        


if __name__ == "__main__":
    state = {
        "M1P4": "M6P3O1",  
        "M1P1": "M3P6O2",  
        "M6P4": "M4P1O1",
        "M3P1": "M5P4O1",    
    }

    robot = RobotController()
    robot.parse_state(state)

    config_name = robot.identify_configuration()
    print(f"Identified configuration: {config_name}")

    role_map = robot.assign_roles()
    print("Role mapping:", role_map)


    while True:
        robot.update_configuration(state)
        print("Available commands:", list(robot.CONFIG_TEMPLATES[config_name]["control"].keys()))

        cmd = input("Enter command (or 'q'): ").strip().lower()
        if cmd == "q":
            break

        sequence = robot.get_command_sequence(cmd)
        if sequence:
            robot.send_command(sequence)
            print(f"Sending command sequence for '{cmd}'")
        else:
            print(f"Command '{cmd}' not found in configuration.")


