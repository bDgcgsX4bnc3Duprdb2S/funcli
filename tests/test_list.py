import pytest
import shlex
import subprocess
import logging
import rich
from rich.logging import RichHandler

log = logging.getLogger(name=__name__)

log.setLevel(logging.DEBUG)
console = rich.get_console()
console.width = 150
handler = RichHandler(console=console)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)


def test_an_unspecified_list_to_list_str():
	"""
	If list is used instead of list[...], it's considered to be list[str]
	"""
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_list.py an_unspecified_list --a_list 11 --a_list 22 --a_list 33"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=a_list=['11', '22', '33']")


def test_an_str_list():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_list.py an_str_list --a_list test1 --a_list test2 --a_list test3"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=a_list=['test1', 'test2', 'test3']")


def test_an_int_list():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_list.py an_int_list --a_list 11 --a_list 22 --a_list 33"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=a_list=[11, 22, 33]")


