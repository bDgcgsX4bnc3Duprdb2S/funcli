import enum
import sys
import types

class Value(enum.Enum):
	value1 = 1
	value2 = 2

type_list=[
	"int",
	"str",
	"bool",
	"list",
	"list[str]",
	"list[int]",
	"Value",
	"__main__.Value"
]



def get_type_from_str(type_name: str) -> type:
	try:
		# Builtin types
		return eval(type_name)
	except NameError:
		# Custom types
		module_nbr = type_name.count(".")
		if module_nbr == 0:
			# If no module specified
			return getattr(sys.modules[__name__], type_name)
		else:
			# If a module is specified
			module_name, type_name = type_name.split(sep=".")
			return getattr(sys.modules[module_name], type_name)
		
for a_type in type_list:
	
	a_type = get_type_from_str(a_type)
	
	
	if type(a_type) == type:  # If it's a basic type like int, str, bool...
		# Get the type name this way
		a_type_name = a_type.__name__
	else:  # If it's a more specific type like list[int]...
		# Get the type name that way
		a_type_name = str(a_type)
	print(f"    {a_type_name}: {a_type}")
	print("---")
