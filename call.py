"""
TODO module docstring
"""
import argparse
import logging as log

from monitor import ChangeMonitor

DEFAULT_FILENAME = "connection_params.json"

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)

    parser = argparse.ArgumentParser()

    parser.add_argument("--dburl", help="URL for the database in SQLAlchemy format")
    parser.add_argument("--filename", help="Name of the file with database params")
    args = parser.parse_args()

    dburl = args.dburl
    filename = args.filename

    if dburl:
        api = ChangeMonitor(dburl=dburl)
    elif filename:
        api = ChangeMonitor(filename=filename)
    else:
        log.warn("No dburl or filename specified. Using default.")
        api = ChangeMonitor(filename=DEFAULT_FILENAME)

    init_state = api.get_initial_state()
    print(f"got inital data\n{init_state}")

    input("Нажмите Enter, чтобы продолжить")

    update = api.get_update()
    print(f"got update data\n{update}")
