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

def test_an_enum():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_enum.py an_enum --value value2"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=value2")

def test_error_an_enum():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_enum.py an_enum --value valuenotexist"),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stderr.__contains__("usage: demo_enum.py an_enum [-h] --value {value1,value2}\ndemo_enum.py an_enum: error: argument --value: invalid choice: 'valuenotexist' (choose from 'value1', 'value2')")


def test_an_enum_list():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_enum.py an_enum_list --value value1 --value value2"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=[<Value.value1: 1>, <Value.value2: 2>]")


def test_error_an_enum_list():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo_enum.py an_enum_list --value value1 --value valuenotexist"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stderr.__contains__("usage: demo_enum.py an_enum_list [-h] --value {value1,value2}\ndemo_enum.py an_enum_list: error: argument --value: invalid choice: 'valuenotexist' (choose from 'value1', 'value2')")

