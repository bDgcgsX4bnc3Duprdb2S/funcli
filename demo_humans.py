"""
This is a short demo for Humans
"""
import enum
import logging
from enum import auto

import rich
from rich.logging import RichHandler

import funcli

__app_name__ = "Demo for Humans"
__version__ = "0.0.1"
__author__ = "gme"

log = logging.getLogger(name=__name__)

log.setLevel(logging.DEBUG)
console = rich.get_console()
console.width = 150
handler = RichHandler(console=console)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

funcli.log = log


class Status(enum.Enum):
	active = auto()
	inactive = auto()

	
def hello(
	name: str,
	age: int,
	enjoy_funcli: bool = True,
	lang: list[str] = ["Python", "c"],
	score: list[int] = [100, 10],
	status: list[Status] = [Status.active, Status.inactive]
):
	"""
	Basic function to demo the lib
	:param name:
	:param age:
	:param enjoy_funcli:
	:param lang:
	:param score:
	:param status:
	:return:
	"""
	
	if not (len(lang) == len(score) == len(status)):
		raise funcli.ArgError(arg_name="lang, score, status", message="You're expected to provide complete informations for all lists")
	
	print(f"Hello {name}")
	print(f"So you're {age}?")
	if enjoy_funcli:
		print(f"Glad you enjoy funcli")
	else:
		print(f"Oh, you don't enjoy funcli :-(")
		print(f"I'm sure there are lot other CLI libs for you out there")
	print(f"You like these programming languages?")
	
	for index, lang_name in enumerate(lang):
		lang_score = score[index]
		lang_status = status[index]
		print(f"{lang_name=}, {lang_score=}, {lang_status=}")

funcli.fun_to_cli([hello], "hello")