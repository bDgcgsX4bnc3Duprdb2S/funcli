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


def test_error_mandatory():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py a_bool"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stderr == "usage: demo.py a_bool [-h] --a_bool | --no-a_bool\ndemo.py a_bool: error: the following arguments are required: --a_bool/--no-a_bool"


def test_error_type():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo.py an_int --value a"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stderr == "usage: demo.py an_int [-h] --value VALUE\ndemo.py an_int: error: argument --value: invalid int value: 'a'"


def test_error_missing_value():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo.py an_int --value"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stderr == "usage: demo.py an_int [-h] --value VALUE\ndemo.py an_int: error: argument --value: expected one argument"


def test_raise_custom_error():
	result = subprocess.run(
		shlex.split("../venv/bin/python3.9 demo.py raise_error"),
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "ERROR: test: This arg value doesn't look right"

def test_error_unknown_fun():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py unknown_function"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stderr == "usage: demo.py [-h] [--full-help] [--version]\n               {simple,default_value,an_unspecified_list,an_int_list,an_str_list,a_bool,raise_error,an_int}\n               ...\ndemo.py: error: unrecognized arguments: unknown_function"
	