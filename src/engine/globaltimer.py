

_TICK_COUNT = 0


def tick_count():
    """returns: How many 'ticks' the game has been running for. This number will never decrease on subsequent calls."""
    return _TICK_COUNT


def inc_tick_count():
    """
    It's pretty important that the game loop calls this once per frame (at the end, after rendering).
    src.engine.renderengine and src.engine.inputs specifically rely on this for their internal logic.
    """
    global _TICK_COUNT
    _TICK_COUNT += 1


def get_fps():
    return -1
