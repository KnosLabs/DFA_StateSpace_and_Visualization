import csv
from collections import deque
import itertools


BEND_STATES = ["B0", "B90", "B180"]
ORIENTATIONS = ["O0", "O1"]

MALE_PORTS = {"P0", "P1", "P2"}
FEMALE_PORTS = {"P3", "P4", "P5"}

LOCAL_PORTS = {
    "P0": ((0,0), (-1,0)),
    "P1": ((1,0), (1,0)),
    "P2": ((0,0), (0,1)),
    "P3": ((0,0), (0,-1)),
    "P4": ((1,0), (0,1)),
    "P5": ((1,0), (0,-1)),
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




def format_state_connections(state):  # For csv export
    acts = state.actuators
    conns = state.connections
    act_map = {a.mid: [] for a in acts}

    for (m1, p1), (m2, p2) in conns:
        a1 = next(a for a in acts if a.mid == m1)
        a2 = next(a for a in acts if a.mid == m2)
        act_map[m1].append(
            f"M{m1}_{p1}_{a1.orientation}_{a1.bend},"
            f"M{m2}_{p2}_{a2.orientation}_{a2.bend}"
        )
        act_map[m2].append(
            f"M{m2}_{p2}_{a2.orientation}_{a2.bend},"
            f"M{m1}_{p1}_{a1.orientation}_{a1.bend}"
        )

    return tuple(
        tuple(act_map[a.mid]) if act_map[a.mid]
        else (f"M{a.mid}_None_{a.orientation}_{a.bend}",)
        for a in acts
    )


def export_csv(transitions, filename):
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Transition"])
        for s0, s1 in transitions:
            w.writerow([f"{format_state_connections(s0)} :: {format_state_connections(s1)}"])



# Test and debug
if 1:
    geoms = {
        0: ActuatorGeom(0, 0, 0),
        1: ActuatorGeom(1, 1, 0),
        2: ActuatorGeom(2, 2, 0),
    }

    S0 = State(
        actuators=[
            ActuatorState(0, "O0", "B0", {"P3"}),          # right end free
            ActuatorState(1, "O0", "B0", {"P0", "P3"}),    # middle
            ActuatorState(2, "O0", "B0", {"P0"}),          # left end free
        ],
        connections={
            ((0, "P3"), (1, "P0")),
            ((1, "P3"), (2, "P0")),
        }
    )

    transitions = enumerate_reachable(S0, geoms)
    print("Transitions:", len(transitions))
    export_csv(transitions, "reachable.csv")
    print("CSV written to reachable.csv")




if 0:
    geoms = {
        0: ActuatorGeom(0, 0, 0),
        1: ActuatorGeom(1, 1, 0),
        2: ActuatorGeom(2, 2, 0),
    }

    S0 = State(
        actuators=[
            ActuatorState(0, "O0", "B0", {"P1"}),
            ActuatorState(1, "O0", "B0", {"P1", "P3"}),
            ActuatorState(2, "O0", "B0", {"P3"}),
        ],
        connections={
            ((0, "P1"), (1, "P3")),
            ((1, "P1"), (2, "P3")),
        }
    )

    transitions = enumerate_reachable(S0, geoms)
    print("Transitions:", len(transitions))
    export_csv(transitions, "reachable.csv")
    print("CSV written to reachable.csv")

