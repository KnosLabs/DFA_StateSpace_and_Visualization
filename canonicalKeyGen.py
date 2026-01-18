def canonical_key(state):
    return tuple(
        (
            m,
            state[m]["bend"],
            state[m]["orient"],
            tuple(
                (p, state[m][p])
                for p in ("P1","P2","P3")
                if state[m][p] is not None
            )
        )
        for m in sorted(state)
    )

def key_to_json(key):
    return [
        [
            m,
            bend,
            orient,
            [[p, list(conn)] for p, conn in ports]
        ]
        for m, bend, orient, ports in key
    ]


def key_to_dict(key):
    """
    Convert canonical JSON key back into dictionary state.
    """

    state = {}

    for m, bend, orient, ports in key:
        state[m] = {
            "bend": bend,
            "orient": orient,
            "P1": None,
            "P2": None,
            "P3": None,
        }

        for p, (m2, p2) in ports:
            state[m][p] = (m2, p2)

    return state


def state_to_dict(state):
    """
    Convert a State object from into a module-centric dictionary.
    """
    acts = state.actuators
    conns = state.connections

    state_dict = {
        f"M{a.mid}": {
            "bend": a.bend,
            "orient": a.orientation,
            "P1": None,
            "P2": None,
            "P3": None,
        }
        for a in acts
    }

    for (m1, p1), (m2, p2) in conns:
        state_dict[m1][p1] = (m2, p2)

    return state_dict