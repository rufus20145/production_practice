"""
TODO module docstring
"""
import logging

from monitor import ChangeMonitor

logging.basicConfig(level=logging.INFO)

test = ChangeMonitor()
init = test.get_initial_state()
print(f"got inital data {init}")

stroka = input("Нажмите Enter, чтобы продолжить")

update = test.get_update()
print(f"got update {update}")
