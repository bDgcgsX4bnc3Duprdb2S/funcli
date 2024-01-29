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


def an_unspecified_list(a_list:list):
	"""
	function with a list of unknown types
	:param a_list:
	:return:
	"""
	print(f"result={a_list=}")


def an_int_list(a_list:list[int]):
	"""
	function with a list of int
	:param a_list:
	:return:
	"""
	print(f"result={a_list=}")


def an_str_list(a_list:list[str]):
	"""
	function with a list of str
	:param a_list:
	:return:
	"""
	print(f"result={a_list=}")


if __name__ == "__main__":
	funcli.fun_to_cli([an_unspecified_list, an_int_list, an_str_list])

