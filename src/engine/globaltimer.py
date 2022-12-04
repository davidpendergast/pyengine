import time

_TICK_COUNT = 0

_DT = 0  # delta time of the current frame, in milliseconds
_DT_RATIO = 1

# used for fps tracking
_TICK_TIMES = [time.time()] * 10
_TICK_TIME_IDX = 0

_SHOW_FPS = False  # if true, current FPS will be shown in the window caption.


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

    global _TICK_TIME_IDX
    _TICK_TIMES[_TICK_TIME_IDX] = time.time()
    _TICK_TIME_IDX = (_TICK_TIME_IDX + 1) % len(_TICK_TIMES)  # circular list


def dt():
    """Returns the "delta time" of the current frame, in milliseconds.

    This describes the amount of wall-clock time that passed between
    the prior frame and the current frame.
    """
    return _DT


def set_dt(dt_millis, target_dt=None):
    """Sets the delta time for the current frame, in milliseconds."""
    global _DT, _DT_RATIO
    _DT = dt_millis
    _DT_RATIO = 1 if target_dt is None else dt_millis / target_dt


def dt_ratio():
    """Returns the ratio between dt and the target delta time.
    When the game is running slower than expected, this ratio will be greater than 1.
    """
    return _DT_RATIO


def get_fps():
    """returns: average fps of the last several frames."""
    min_time = min(_TICK_TIMES)
    max_time = max(_TICK_TIMES)
    elapsed_time = max_time - min_time
    if elapsed_time == 0:
        return 999
    else:
        return (len(_TICK_TIMES) - 1) / elapsed_time


def get_show_fps():
    return _SHOW_FPS


def set_show_fps(val):
    global _SHOW_FPS
    _SHOW_FPS = val
