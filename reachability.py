import csv
from fileHandler import save_reachability_keys
from collections import deque
import itertools


BEND_STATES = ["B0", "B90", "B180"]
ORIENTATIONS = ["O0", "O1"]

FEMALE_PORTS = {"P1", "P2", "P3"}
MALE_PORTS = {"P4", "P5", "P6"}

LOCAL_PORTS = {
    "P1": ((0,0), (-1,0)),
    "P2": ((1,0), (1,0)),
    "P3": ((0,0), (0,1)),
    "P4": ((0,0), (0,-1)),
    "P5": ((1,0), (0,1)),
    "P6": ((1,0), (0,-1)),
}

def rotate(cell, orientation):
    x, y = cell
    return (x, y) if orientation == "O0" else (x, -y)


class ActuatorGeom:
    def __init__(self, mid, x, y):
        self.mid = mid
        self.x = x
        self.y = y

    def ports(self, orientation, bend):
        res = {}
        for p, (cell, normal) in LOCAL_PORTS.items():
            cx, cy = rotate(cell, orientation)
            nx, ny = rotate(normal, orientation)
            res[p] = ((self.x + cx, self.y + cy), (nx, ny))
        return res


class ActuatorState:
    def __init__(self, mid, orientation, bend, ports=None):
        self.mid = mid
        self.orientation = orientation
        self.bend = bend
        self.ports = set(ports) if ports else set()

    def canonical(self):
        return (self.mid, self.orientation, self.bend, tuple(sorted(self.ports)))


class State: # System State
    def __init__(self, actuators, connections=None):
        self.actuators = actuators
        self.connections = connections if connections else set()
        self._assert_consistent()

    def _assert_consistent(self):
        """Enforce one bending orientation per module per state"""
        seen = {}
        for a in self.actuators:
            key = (a.orientation, a.bend)
            if a.mid in seen and seen[a.mid] != key:
                raise ValueError(
                    f"Inconsistent state for M{a.mid}: {seen[a.mid]} vs {key}"
                )
            seen[a.mid] = key

    def canonical(self):
        acts = tuple(sorted(a.canonical() for a in self.actuators))
        conns = tuple(sorted(tuple(sorted(c)) for c in self.connections))
        return (acts, conns)


def port_in_use(connections, mid, port):
    for (m1, p1), (m2, p2) in connections:
        if (m1 == mid and p1 == port) or (m2 == mid and p2 == port):
            return True
    return False


def ports_compatible(a_geom, a_state, b_geom, b_state, p1, p2):
    if not ((p1 in MALE_PORTS and p2 in FEMALE_PORTS) or
            (p2 in MALE_PORTS and p1 in FEMALE_PORTS)):
        return False

    (c1, n1) = a_geom.ports(a_state.orientation, a_state.bend)[p1]
    (c2, n2) = b_geom.ports(b_state.orientation, b_state.bend)[p2]

    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]

    if abs(dx) + abs(dy) != 1:
        return False
    if n1 != (dx, dy):
        return False
    if n2 != (-dx, -dy):
        return False

    return True


def expand_state(state, geoms):
    next_states = []

    # 1. No-op
    next_states.append(state)

    # 2. Bend transitions (module-unique)
    for i, a in enumerate(state.actuators):
        for b in BEND_STATES:
            if b == a.bend:
                continue

            new_acts = []
            for j, aj in enumerate(state.actuators):
                if j == i:
                    new_acts.append(
                        ActuatorState(aj.mid, aj.orientation, b, aj.ports)
                    )
                else:
                    new_acts.append(aj)

            next_states.append(State(new_acts, set(state.connections)))

    # 3. Connection transitions
    for a1, a2 in itertools.permutations(state.actuators, 2):
        geom1 = geoms[a1.mid]
        geom2 = geoms[a2.mid]
        for p1 in a1.ports:
            for p2 in a2.ports:
                if port_in_use(state.connections, a1.mid, p1):
                    continue
                if port_in_use(state.connections, a2.mid, p2):
                    continue
                if ports_compatible(geom1, a1, geom2, a2, p1, p2):
                    new_conns = set(state.connections)
                    new_conns.add(((a1.mid, p1), (a2.mid, p2)))
                    next_states.append(State(state.actuators, new_conns))

    return next_states


def enumerate_reachable(initial, geoms, max_states=1000): # Reachability
    Q = deque([initial])
    visited = set()
    transitions = set()

    while Q and len(visited) < max_states:
        s = Q.popleft()
        try:
            key = s.canonical()
        except ValueError:
            continue

        if key in visited:
            continue
        visited.add(key)

        for sn in expand_state(s, geoms):
            try:
                sn_key = sn.canonical()
            except ValueError:
                continue

            if sn_key != key:
                transitions.add((s, sn))
            Q.append(sn)

    return transitions

# Test and debug
if 1:
    geoms = {
        1: ActuatorGeom(1, 0, 0),
        2: ActuatorGeom(2, 1, 0),
        3: ActuatorGeom(3, 2, 0),
    }

    S0 = State(
        actuators=[
            ActuatorState(1, "O0", "B0", {"P1, P4"}),          # right end free
            ActuatorState(2, "O0", "B90", {"P2"}),    # middle
            ActuatorState(3, "O0", "B0", {"P4"}),          # left end free
        ],
        connections={
            (("M1", "P1"), ("M2", "P5")),
            (("M2", "P1"), ("M3", "P5")),
        }
    )

    transitions = enumerate_reachable(S0, geoms)
    print("Transitions:", len(transitions))
    save_reachability_keys(transitions, "reachable.ndjson")
    #export_csv(transitions, "reachable.csv")
    print("CSV written to reachable.csv")


