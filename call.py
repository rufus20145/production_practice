"""
TODO module docstring
"""
from monitor import ChangeMonitor

test = ChangeMonitor()
test.get_initial_state()

stroka = input("Введите строку:")

test.get_patch()
