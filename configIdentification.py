### This is not yet implimented or complete. This wil be used for identifying what configuration the system is in a provide
# a set of commands for control. 

## Configurations to include: Crawler, Pipe Climbing Robot, Rolling Cylinder, ManusBot, TendrilBot

import json

class ModularRobotController:
    def __init__(self):
        self.CONFIG_TEMPLATES = {
            "walker_5": {
                "structure": {
                    "meta": {"connections": 4},
                    "center": "body",
                    "P3": "frontL_leg",
                    "P5": "frontR_leg",
                    "P2": "backL_leg",
                    "P6": "backR_leg"
                },
                "control": {
                    "forward": {
                        "params": {"period": 5.0, "duty": 0.4},
                        "tracks": {
                            "body": [
                                {"at": "@period*.25", "set" : {"inflate": 1}},
                                {"dt": "@period*0.5", "set": {"inflate": 0}}
                            ],
                            "frontL_leg": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set" : {"inflate": 0}}
                            ],
                            "frontR_leg": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set" : {"inflate": 0}}
                            ],
                            "backL_leg": [
                                {"at": "@0.5*period", "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set" : {"inflate": 0}}
                            ],
                            "backR_leg": [
                                {"at": "@0.5*period", "set" : {"inflate": 1}},    
                                {"dt": "@duty*period", "set" : {"inflate": 0}}
                            ]
                            
                        }
                    }
                
                }
            },
            "climbing_6": {
                "structure": {
                    "meta": {"connections": 2},
                    "center": "body",
                    "P1": "backL_leg",
                    "P4": "frontR_leg",
                    "P1>P1": "backR_leg",
                    "P4>P4": "frontL_leg"
                },
                "control": {
                    "front_climb": {
                        "params" : {"period": 8.0, "duty": 0.2},
                        "tracks": {
                            "body": [
                                {"at": "@0.2*period", "set" : {"inflate": 1}},
                                {"dt": "@3*duty*period", "set": {"inflate": 0}}
                            ],
                            "frontL_leg": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                                {"dt": "@3*duty*period", "set" : {"inflate": 0}}
                            ],
                            "frontR_leg": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                                {"dt": "@3*duty*period", "set" : {"inflate": 0}}
                            ],
                            "backL_leg": [
                                {"at": "@0.6*period", "set" : {"inflate": 1}},
                                {"dt": "@2*duty*period", "set" : {"inflate": 0}}
                            ],
                            "backR_leg": [
                                {"at": "@0.6*period", "set" : {"inflate": 1}},    
                                {"dt": "@2*duty*period", "set" : {"inflate": 0}}
                            ]
                        }
                    }
                }
            },
            "roller_6": {
                "structure": {
                    "meta": {"connections": 6},
                    "center": "roll1",
                    "P4": "roll2",
                    "P3": "roll3",
                    "P2": "roll4",
                    "P1": "roll2",
                    "P5": "roll5",
                    "P6": "roll6"
                },
                "control": {
                    "forward": {
                        "params": {"period": 8.0, "duty": 0.3},
                        "tracks": {
                            "roll1": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set": {"inflate": 0}}
                            ],
                            "roll2": [
                                {"at": "@0.5*period", "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set": {"inflate": 0}}
                            ],
                            "roll3": [
                                {"at": "@0.25*period", "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set": {"inflate": 0}}
                            ],
                            "roll4": [
                                {"at": "@0.75*period", "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set": {"inflate": 0}}
                            ],
                            "roll5": [
                                {"at": "@0.25*period", "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set": {"inflate": 0}}
                            ],
                            "roll6": [
                                {"at": "@0.75*period", "set" : {"inflate": 1}},
                                {"dt": "@duty*period", "set": {"inflate": 0}}
                            ]
                        }   
                    }
                } 
            },
            "manus_4": {
                "structure": {
                    "meta": {"connections": 2},
                    "center": "wrist1",
                    "P3": "finger1",
                    "P1": "wrist2",
                    "P1>P2": "finger2"
                },
                "control": {
                    "grasp": {
                        "params": {"period": 6.0},
                        "tracks": {
                            "wrist1": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                            ],
                            "wrist2": [
                                {"at": 0.0, "set" : {"inflate": 1}},
                            ],
                            "finger1": [
                                {"at": "@0.5*period", "set" : {"inflate": 1}},
                            ],
                          
                            "finger2": [
                                {"at": "@0.5*period", "set" : {"inflate": 1}}
                            ]
                        }
                    }
                }
            },
            "sinusoidal_4": {
                "structure": {
                    "meta": {"connections": 2},
                    "center": "body2",
                    "P1": "body1",
                    "P4": "body3",
                    "P4>P1": "body4"
                },
                "control": {
                    "sidwind": [ # 
                    ]
                }
            }
        }

        self.transition_state = {}
        self.connections = {}
        self.center_module = None
        self.current_config_name = None

    def parse_transition_system(self, transitions):
        self.transition_state = transitions
        self.connections = {}

        for key, value in transitions.items():
            module_a, port_a = key[:2], key[2:]
            module_b, port_b = value[:2], value[2:4]
            #orientation_b = value[4:] 

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
    def _is_path(spec: str) -> bool:
        return ">" in spec

    @staticmethod
    def _split_path(spec: str):
        # 'P3>P1>P6' -> ['P3', 'P1', 'P6']
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

    def generate_timed_sequence(self):
        role_map = self.assign_roles()
        template = self.CONFIG_TEMPLATES[self.current_config_name]
        sequence = template.get("control_sequence", [])
        result = []

        for step in sequence:
            time = step["time"]
            actions = []

            for role, command in step["actions"].items():
                if role == "disconnect":
                    target_id = next((k for k, v in role_map.items() if v == command), None)
                    if target_id:
                        actions.append({"action": "disconnect", "target": target_id})
                elif role in role_map:
                    actuator_id = next((k for k, v in role_map.items() if v == role), None)
                    if actuator_id:
                        actions.append({"actuator": actuator_id, **command})

            result.append({"time": time, "actions": actions})

        return result

    def export_control_sequence_as_json(self, filepath="control_sequence.json"):
        sequence = self.generate_timed_sequence()
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

if __name__ == "__main__":
    state = {
        "M1P4": "M6P3",  
        "M1P1": "M3P6",  
        "M6P4": "M4P1",
        "M3P1": "M5P4",    
    }

    robot = ModularRobotController()
    robot.parse_transition_system(state)

    config_name = robot.identify_configuration()
    print(f"Identified configuration: {config_name}")

    center = robot.center_module
    print(f"Center module: {center}")

    role_map = robot.assign_roles()
    print("Role mapping:", role_map)