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

# funcli.log = log


class Value(enum.Enum):
	value1 = 1
	value2 = 2


def simple():
	"""
	simple function with no args
	"""
	print("ok")


def default_value(a_bool:bool=True, a_int: int=1, a_str:str="string", a_list:list[str]=["a", "b", "c"]):
	"""
	function with default values for every args
	:param a_bool:
	:param a_int:
	:param a_str:
	:param a_list:
	:return:
	"""
	print(f"{a_bool=}, {a_int=}, {a_str=}, {a_list=}")


def an_unspecified_list(a_list:list):
	"""
	function with a list of unknown types
	:param a_list:
	:return:
	"""
	print(f"{a_list=}")


def an_int_list(a_list:list[int]):
	"""
	function with a list of int
	:param a_list:
	:return:
	"""
	print(f"{a_list=}")


def an_str_list(a_list:list[str]):
	"""
	function with a list of str
	:param a_list:
	:return:
	"""
	print(f"{a_list=}")


def a_bool(a_bool: bool):
	"""
	function with a bool
	"""
	print(a_bool)

def an_int(value:int):
	"""
	function with an int
	:param value:
	:return:
	"""
	print(value)


def raise_error():
	"""
	function that raise a funcli error
	:return:
	"""
	raise funcli.ArgError(arg_name="test", message="This arg value doesn't look right")


if __name__ == "__main__":
	funcli.fun_to_cli([simple, default_value, an_unspecified_list, an_int_list, an_str_list, a_bool, raise_error, an_int], "simple")

