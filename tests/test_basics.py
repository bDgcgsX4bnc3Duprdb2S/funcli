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
	
	assert stdout.__contains__("result=ok")

def test_default_fun_call():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=ok")



def test_default_value_call():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py default_value"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=a_bool=True, a_int=1, a_str='string', a_list=['a', 'b', 'c']")




def test_a_bool_true():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py a_bool --a_bool"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=True")

def test_a_bool_false():
	result = subprocess.run(shlex.split("../venv/bin/python3.9 demo.py a_bool --no-a_bool"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout = result.stdout.decode("utf-8").strip()
	stderr = result.stderr.decode("utf-8").strip()
	log.info(stdout)
	log.error(stderr)
	print(f"{stdout=}")
	print(f"{stderr=}")
	assert stdout.__contains__("result=False")
