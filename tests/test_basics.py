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





def test_simple_call():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py simple"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "ok"

def test_default_fun_call():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "ok"



def test_default_value_call():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py default_value"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "a_bool=True, a_int=1, a_str='string', a_list=['a', 'b', 'c']"





def test_a_bool_true():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py a_bool --a_bool"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "True"

def test_a_bool_false():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py a_bool --no-a_bool"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "False"

def test_an_unspecified_list_to_list_str():
	"""
	If list is used instead of list[...], it's considered to be list[str]
	"""
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py an_unspecified_list --a_list 11 --a_list 22 --a_list 33"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "a_list=['11', '22', '33']"
	

def test_an_str_list():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py an_str_list --a_list test1 --a_list test2 --a_list test3"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "a_list=['test1', 'test2', 'test3']"

def test_an_int_list():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py an_int_list --a_list 11 --a_list 22 --a_list 33"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout == "a_list=[11, 22, 33]"

