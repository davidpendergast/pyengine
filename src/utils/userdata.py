import os.path
import traceback
import typing
import string

import platform
import json


_ACTUALLY_RUNNING_IN_WEB_MODE = False
_HAS_APPDIRS = False

if platform.system().lower() == "emscripten":
    # Note that this stuff only resolves when running in a web context
    if __WASM__ and __EMSCRIPTEN__ and __EMSCRIPTEN__.is_browser:
        from __EMSCRIPTEN__ import window, document
    _ACTUALLY_RUNNING_IN_WEB_MODE = True
else:
    try:
        import appdirs  # 3rd party module: https://pypi.org/project/appdirs/
        _HAS_APPDIRS = True
    except ImportError:
        print("WARN: appdirs module couldn't be imported. userdata.USER_DATA_DIR mode will not be available.")


# Storage Modes
USER_DATA_DIR = "USER_DATA_DIR"
CURRENT_WORKING_DIR = "CURRENT_WORKING_DIR"
LOCAL_WEB_STORAGE = "LOCAL_WEB_STORAGE"
SAVE_AND_LOAD_DISABLED = "SAVE_AND_LOAD_DISABLED"
BEST = "BEST"


# Metadata
_KEY: typing.Optional[str] = None
_MODE: str = SAVE_AND_LOAD_DISABLED
_APPNAME: typing.Optional[str] = None
_APPAUTHOR: typing.Optional[str] = None

_VERSION_KEY = "_vers"
_VERSION: typing.Optional[str] = None

# Actual Data
_IN_MEMORY = {}
_DIRTY = False


def initialize(keyname: str, mode: str = BEST, appname=None, appauthor=None, version=None):
    """Initializes the module.

    Args:
        keyname (str): An identifier for this blob of data. In web mode, this is used as the key in the browser's
            storage area. In desktop mode, it's used for the name of the json file. This key should be consistent
            across different runs of the program.
        mode (str): Where to save/load the data. Must be one of the following:
            userdata.CURRENT_WORKING_DIR: Store the data at ./keyname.json
            userdata.USER_DATA_DIR: Store data in a json file at an appropriate location for this OS.
            userdata.LOCAL_WEB_STORAGE: Store data in the browser (will only work in web mode).
            userdata.SAVE_AND_LOAD_DISABLED: Do not save or load any data.
            userdata.BEST (default): Choose the best option automatically.
        appname (str): Only used in USER_DATA_DIR mode. May affect where the data gets saved on disk.
        appauthor (str): Only used in USER_DATA_DIR mode. May affect where the data gets saved on disk.
        version (str): An optional version string that will be included in the save file if given.
    """
    if keyname is None and mode != SAVE_AND_LOAD_DISABLED:
        raise ValueError("keyname cannot be None")

    global _KEY, _APPNAME, _APPAUTHOR, _VERSION
    _KEY = keyname
    _set_mode(mode)

    _APPNAME = appname
    _APPAUTHOR = appauthor
    _VERSION = version


def load_data_from_disk() -> bool:
    """Loads the data from disk into program memory."""
    _check_initialized()

    global _IN_MEMORY, _DIRTY
    _IN_MEMORY = {}
    _DIRTY = False

    try:
        if _MODE == SAVE_AND_LOAD_DISABLED:
            pass
        elif _MODE == LOCAL_WEB_STORAGE:
            blob_str = window.localStorage.getItem(_KEY)
            if blob_str is not None:
                print(f"INFO: loaded \"{_KEY}\" from window.localStorage: {blob_str}")
                _IN_MEMORY = json.loads(blob_str)
            else:
                print(f"INFO: no save data found in window.localStorage at \"{_KEY}\", fresh launch?")
        else:
            local_filepath = _get_local_filepath()
            if os.path.exists(local_filepath):
                with open(local_filepath) as fp:
                    _IN_MEMORY = json.load(fp)
                    print(f"INFO: loaded data from {local_filepath}: {_IN_MEMORY}")
            else:
                print(f"INFO: no save data found at {local_filepath}, fresh launch?")

    except Exception:
        print("ERROR: failed to load user's save data, treating it as a fresh launch instead")
        traceback.print_exc()
        return False

    return True


def save_data_to_disk(force=False) -> bool:
    """Saves the data from program memory to disk, if new changes are present.

        Args:
            force (bool): If True, will update the data on disk even if no new changes are present.
    """
    _check_initialized()

    global _DIRTY
    if _DIRTY or force:
        if _VERSION is not None:
            _IN_MEMORY[_VERSION_KEY] = _VERSION
        _DIRTY = False

        try:
            if _MODE == SAVE_AND_LOAD_DISABLED:
                pass
            elif _MODE == LOCAL_WEB_STORAGE:
                blob_str = json.dumps(_IN_MEMORY)
                window.localStorage.setItem(_KEY, blob_str)
                print(f"INFO: wrote \"{_KEY}\" to window.localStorage: {blob_str}")
            else:
                local_filepath = _get_local_filepath()
                action_str = "overwrote" if os.path.exists(local_filepath) else "created"
                with open(local_filepath, 'w') as fp:
                    json.dump(_IN_MEMORY, fp)
                    print(f"INFO: {action_str} {local_filepath} with data: {_IN_MEMORY}")

        except Exception:
            print("ERROR: failed to save user data")
            traceback.print_exc()
            return False

    return True


def set_data(key: str, val, and_save_to_disk=True):
    """Creates or updates a key-value pair of data in program memory.

        Args:
            key (str): the key for the data.
            val: the data to store. Must be json-compatible.
            and_save_to_disk (bool): Whether to save this change to disk immediately.
    """
    _check_initialized()

    global _IN_MEMORY, _DIRTY
    val = _copy_via_json_serialization(val)
    if key not in _IN_MEMORY or _IN_MEMORY[key] != val:
        _DIRTY = True
    _IN_MEMORY[key] = val

    if and_save_to_disk:
        save_data_to_disk()


def get_data(key: str, coercer=lambda x: x, or_else=None):
    """Fetches a piece of data from program memory using its key.

        Args:
            key (str): the key for the data.
            coercer: an optional function that converts or cleans the data before it's returned. For example,
                if you're expecting the data to be an integer, you may want to pass `coercer=int` to guarantee the
                return value is an int. This way callers can prevent themselves from receiving corrupted data to
                some degree.
            or_else: a value to return if the data isn't present or caused `coercer` to throw an error.
    """
    _check_initialized()

    if key in _IN_MEMORY:
        val = _IN_MEMORY[key]
        val = _copy_via_json_serialization(val)
        if coercer is not None:
            try:
                return coercer(val)
            except Exception:
                print(f"ERROR: failed to coerce user data: {key}={val} (using {or_else} instead)")
                traceback.print_exc()
                return or_else
        else:
            return val

    return or_else


def reset_data(hard=False):
    """Erases the user's data in program memory.

        Args:
            hard (bool): If True, will immediately delete the user's data on-disk or in the browser as well.

                If False, this function will leave the data on-disk intact (wiping the data in program memory only).
                Note that saving anything new to disk after a soft reset will overwrite the data that was
                there previously though, effectively wiping it. So proceed with caution if calling this.
    """
    _check_initialized()

    global _DIRTY
    _IN_MEMORY.clear()
    _DIRTY = False

    if hard:
        try:
            if _MODE == SAVE_AND_LOAD_DISABLED:
                print("INFO: not resetting on-disk data because user data is disabled.")
                pass
            elif _MODE == LOCAL_WEB_STORAGE:
                window.localStorage.removeItem(_KEY)
                print(f"INFO: removed \"{_KEY}\" from window.localStorage")
            else:
                local_filepath = _get_local_filepath()
                if os.path.exists(local_filepath):
                    os.remove(local_filepath)
                    print(f"INFO: removed user data file: {local_filepath}")
                else:
                    print(f"INFO: no save data to reset, file doesn't exist: {local_filepath}")

        except Exception:
            print("ERROR: failed to reset user's save data")
            traceback.print_exc()
            return False

    return True


def _set_mode(mode):
    if mode == BEST:
        if _ACTUALLY_RUNNING_IN_WEB_MODE:
            mode = LOCAL_WEB_STORAGE
        else:
            mode = USER_DATA_DIR if _HAS_APPDIRS else CURRENT_WORKING_DIR

    if mode == LOCAL_WEB_STORAGE and not _ACTUALLY_RUNNING_IN_WEB_MODE:
        raise ValueError(f"Cannot use saving mode \"{mode}\" if not running in web mode.")
    elif mode == USER_DATA_DIR and not _HAS_APPDIRS:
        raise ValueError(f"Cannot use saving mode \"{mode}\" without appdirs module.")
    elif mode in (LOCAL_WEB_STORAGE, CURRENT_WORKING_DIR, USER_DATA_DIR, SAVE_AND_LOAD_DISABLED):
        global _MODE
        _MODE = mode
    else:
        raise ValueError(f"Unrecognized saving mode: \"{mode}\"")


def _check_initialized():
    if _KEY is None:
        raise ValueError("module has not been initialized.")


_VALID_CHARS_FOR_FP = set(s for s in string.ascii_letters + "0123456789_()")


def _clean_for_fp(text, replacewith=""):
    if text is None:
        return None
    else:
        return "".join((t if t in _VALID_CHARS_FOR_FP else replacewith) for t in text)


def _copy_via_json_serialization(val):
    try:
        val_as_json_str = json.dumps(val)
        return json.loads(val_as_json_str)
    except Exception as e:
        print(f"ERROR: val isn't json-compatible: {val} (type is {type(val).__name__})")
        raise e


def _get_local_filepath(mkdirs_if_necessary=True) -> str:
    filename = f"{_KEY}.json"
    if _MODE == USER_DATA_DIR:
        directory = appdirs.user_data_dir(
            appname=_clean_for_fp(_APPNAME),
            appauthor=_clean_for_fp(_APPAUTHOR))

        if mkdirs_if_necessary and not os.path.exists(directory):
            print(f"INFO: creating {directory}")
            os.makedirs(directory, exist_ok=True)

        return os.path.join(directory, filename)
    else:
        return filename
