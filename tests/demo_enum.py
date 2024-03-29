"""
This is a demo script to be used only for tests.
Not a good implementation as an example for humans.
"""

import enum
import logging
import sys
import funcli

__app_name__ = "Demo"
__version__ = "0.0.1"
__author__ = "gme"

log = logging.getLogger(name=__name__)

log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

funcli.log = log


class Value(enum.Enum):
	value1 = 1
	value2 = 2


def an_enum(value: Value):
	"""
	function with a Value
	:param value:
	:return:
	"""
	print(f"result={value.name}")

def an_enum_list(value: list[Value]):
	"""
	function with a Value
	:param value:
	:return:
	"""
	print(f"result={value}")



if __name__ == "__main__":
	funcli.fun_to_cli([an_enum, an_enum_list])

