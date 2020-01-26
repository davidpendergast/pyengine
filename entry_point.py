import traceback
import datetime
import os
import pathlib

"""
The main entry point.
"""

NAME_OF_GAME = "GameName"


def _get_crash_report_file_name():
    now = datetime.datetime.now()
    date_str = now.strftime("--%Y-%m-%d--%H-%M-%S")
    return "crash_report" + date_str + ".txt"


if __name__ == "__main__":
    version_string = "?"
    try:
        import src.example.gameloop as gameloop
        gameloop.init(NAME_OF_GAME)
        gameloop.run()

    except Exception as e:
        crash_file_name = _get_crash_report_file_name()
        print("INFO: generating crash file {}".format(crash_file_name))

        directory = os.path.dirname("logs/")
        if not os.path.exists(directory):
            os.makedirs(directory)

        crash_file_path = pathlib.Path("logs/" + crash_file_name)
        with open(crash_file_path, 'w') as f:
            print("o--{}---------------o".format("-" * len(NAME_OF_GAME)), file=f)
            print("|  {} Crash Report  |".format(NAME_OF_GAME), file=f)
            print("o--{}---------------o".format("-" * len(NAME_OF_GAME)), file=f)
            print("\nVersion: {}\n".format(version_string), file=f)

            traceback.print_exc(file=f)

        raise e

