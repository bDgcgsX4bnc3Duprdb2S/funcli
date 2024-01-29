

import argparse
import enum
import inspect
import logging
import os
import sys
import typing
from dataclasses import dataclass

log = logging.getLogger(__name__)

class CustomAppendAction(argparse.Action):
    """Custom action to append values to a list.

    When using the `append` action, the default value is not removed
    from the list. This problem is described in
    https://github.com/python/cpython/issues/60603

    This custom action aims to fix this problem by removing the default
    value when the argument is specified for the first time.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initialize the action."""
        self.called_times = 0
        self.default_value = kwargs.get("default")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """When the argument is specified on the commandline."""
        current_values = getattr(namespace, self.dest)

        if self.called_times == 0 and current_values == self.default_value:
            current_values = []

        current_values.append(values)
        setattr(namespace, self.dest, current_values)
        self.called_times += 1

class ArgError(ValueError):
    def __init__(self, arg_name: str, message: str, *args: object) -> None:
        self.arg_name = arg_name
        self.message = message
        super().__init__(f"{arg_name}: {message}", *args)


@dataclass
class Arg:
    name: str = None
    required: bool = False
    
    original_type: type = None
    translated_type: type = str
    original_type_name: str = None
    translated_type_name: str = None
    
    help: str = None
    
    default = None
    default_repr: str = ""
    
    description: str = ""
    description_repr: str = ""

    def get_final_type(self):
        if typing.get_origin(self.original_type) == list:
            return typing.get_args(self.original_type)[0]  # Extract the type of obj in the list
        return self.original_type

    def is_enum(self):
        return issubclass(self.get_final_type(), enum.Enum)

    def is_list(self):
        if typing.get_origin(self.original_type) == list:
            return True
        return issubclass(self.original_type, list)
    
    def get_action(self, log_indent: int = 0):
        if self.translated_type == bool:
            log.debug("\t"*log_indent+f"action = store_true")
            return argparse.BooleanOptionalAction  # Use the flag/no-flag mecanism builtin argparse
        elif self.is_list():
            log.debug("\t"*log_indent+f"action = append")
            return CustomAppendAction #argparse._AppendAction
        else:
            log.debug("\t"*log_indent+f"action = store")
            return "store"
            
    def get_choices(self, log_indent: int = 0):
        choices = None
        try:
            choices = [value.name for value in list(self.get_final_type())]
        except TypeError:
            choices = None
        log.debug("\t"*log_indent+f"{choices=}")
        return choices
    
    
    def print(self, log_indent: int = 0):
        log.debug("\t" * log_indent + f"{self.name=}")
        log.debug("\t" * log_indent + f"{self.required=}")
    
        log.debug("\t" * log_indent + f"{self.is_list()=}")
        log.debug("\t" * log_indent + f"{self.is_enum()=}")
        log.debug("\t" * log_indent + f"{self.original_type=}")
        log.debug("\t" * log_indent + f"{self.translated_type=}")
        log.debug("\t" * log_indent + f"{self.original_type_name=}")
        log.debug("\t" * log_indent + f"{self.translated_type_name=}")
    
        log.debug("\t" * log_indent + f"{self.help=}")
    
        log.debug("\t" * log_indent + f"{self.default=}")
        log.debug("\t" * log_indent + f"{self.default_repr=}")
    
        log.debug("\t" * log_indent + f"{self.description=}")
        log.debug("\t" * log_indent + f"{self.description_repr=}")

@dataclass
class Function:
    name: str
    fun: callable
    descr: str = ""
    args: dict = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = {}

definitions: dict[str: Function] = {}


def get_type_name(a_type, log_indent: int = 0) -> str:
    if type(a_type) == type:  # If it's a basic type like int, str, bool...
        # Get the type name this way
        log.debug("\t"*log_indent+f"get_type_name type {a_type.__name__} is builtin")
        return a_type.__name__
    else:  # If it's a more specific type like list[int]...
        # Get the type name that way
        log.debug("\t"*log_indent+f"get_type_name type {str(a_type)} is NOT builtin")
        return str(a_type)


def get_type_from_str(type_name: str) -> type:
    try:
        # Builtin types
        a_type = eval(type_name)
        log.debug(f"get_type_from_str type is builtin")
        return a_type
    except NameError:
        # Custom types
        module_nbr = type_name.count(".")
        if module_nbr == 0:
            # If no module specified
            log.debug(f"get_type_from_str IMplicit module")
            return getattr(sys.modules[__name__], type_name)
        else:
            # If a module is specified
            log.debug(f"get_type_from_str EXplicit module")
            module_name, type_name = type_name.split(sep=".")
            return getattr(sys.modules[module_name], type_name)


"""
def print_help_and_exit(exception: Exception, parser: argparse.ArgumentParser):
    print(f"ERROR: {exception.__str__()}")
    print()
    parser.print_help()
    print()
    print(f"ERROR: {exception.__str__()}")
    print()
    sys.exit(1)
"""

def fun_to_cli(functions, default_function_name: str = "", exit_on_error=True):
    """
    Turn functions into cli utility.

    Give it a list of functions and it will:
    - Build an arg parser to parse cli commands
    - Automatically generate the cli help using docstring witch description, arg type, default value...
    - Handle raised funcli.*Error exceptions raised by the called function by displaying an error, help and exiting properly

    :param functions: A list of functions. Eg: [print, json.dumps, ]
    :param default_function_name: The name of the default function if no subcommand is called in CLI
            It can only be a function that takes no required args
    :param exit_on_error: Force parser to exit script if error happen in parsing args
    :return: (parser, parsed_args, function_result)
    """

    def get_arg_description(
        arg_name, docstring, arg_delimiter_start=":param ", arg_delimiter_end=":", return_delimiter=":return:"
    ):
        """
        Parse docstring to extract arg_name's description.
        :param arg_name: An arg name
        :param docstring: A docstring describing multiple args
        :param arg_delimiter_start: The delimiter for start of arg
        :param arg_delimiter_end: The delimiter for end of arg
        :param return_delimiter: The return delimiter
        :return: The arg description
        """
        if docstring is None or docstring == "":
            return ""
        
        tag = f"{arg_delimiter_start}{arg_name}{arg_delimiter_end}"
        arg_found = False
        description = ""
        for line in docstring.splitlines():
            if tag in line:
                arg_found = True
                line = line.replace(tag, "").strip()
                description += line + os.linesep
            elif arg_found and arg_delimiter_start not in line and return_delimiter not in line:
                line = line.strip()
                description += line + os.linesep
            elif arg_found and arg_delimiter_start in line:
                arg_found = False
                break
            else:
                pass
        return description.strip()

    def extract_description_from_docstring(docstring):
        description = ""
        for line in docstring.splitlines():
            line = line.strip()  # Strip line
            # If end of description is detected
            if line.startswith(":param ") or line.startswith(":return:"):
                break  # Break
            else:  # If still in description
                description += line + os.linesep
        return description.strip()
    
    
    # Parse args definitions
    log.debug(f"Parsing definitions...")
    log.debug(f"----------------------")
    
    # reorganise functions in a dict
    functions = {func.__name__: func for func in functions}

    # Get script details
    try:
        from __main__ import __app_name__ as module_name

        if module_name == "__main__":
            module_name = "Anonymous script"
    except ImportError as e:
        module_name = "Anonymous script"
    log.debug(f"{module_name=}")
    
    try:
        from __main__ import __version__ as module_version
    except ImportError as e:
        module_version_info = ("0", "0", "0")
        module_version = ".".join(module_version_info)
    log.debug(f"{module_version=}")
    
    try:
        from __main__ import __author__ as module_author
    except ImportError as e:
        module_author = "Anonymous author"
    log.debug(f"{module_author=}")
    
    module_version_repr = f"{module_name} version:{module_version} by {module_author}"
    log.debug(f"{module_version_repr=}")
    
    try:
        from __main__ import __doc__ as module_doc
        if module_doc is None:
            module_doc = ""
    except ImportError as e:
        module_doc = ""
    module_doc = module_version_repr + os.linesep + module_doc
    log.debug(f"{module_doc=}")

    # Init arg parser
    parser = argparse.ArgumentParser(
        description=module_doc, exit_on_error=exit_on_error, formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # For each function
    for function_name, function in functions.items():
        log.debug(f"{function_name=}")
        fun = Function(name=function_name, fun=function)
        definitions[fun.name] = fun
        
        # Create a parser for each function
        # Tag default function in help
        if fun.name == default_function_name:
            function_help = f"[default if no subcommand provided]" + os.linesep
            log.debug(f"    DEFAULT if no subcommand provided")
            
        # Use docstring as help
        if function.__doc__ is not None:
            fun.descr += extract_description_from_docstring(function.__doc__)
        
        subparser = subparsers.add_parser(
            name=fun.name,
            help=fun.descr,
            description=fun.descr,
            formatter_class=argparse.RawTextHelpFormatter,
        )

        # If there are args, add them to CLI
        for arg_name, parameter in inspect.signature(function).parameters.items():
            log.debug(f"    {arg_name=}")
            arg = Arg(name=arg_name)
            arg.default = parameter.default
            fun.args[arg.name] = arg
            
            # Detect type
            if parameter.annotation != inspect._empty:  # Annotated
                arg.original_type = parameter.annotation
                arg.translated_type = parameter.annotation
                log.debug(f"        type is explicitly defined as {arg.original_type=}")
                
            elif arg.default != inspect._empty:  # Not annotated but default value
                if arg.default is not None:
                    arg.original_type = type(arg.default)
                    arg.translated_type = type(arg.default)
                else:
                    arg.original_type = None
                    arg.translated_type = str
                log.debug(f"        type is implicitly defined as {arg.original_type=}")
                
            else:  # Not annotated and no default value
                arg.original_type = None
                arg.translated_type = str
                log.debug(f"        type is unknown")
                
                
            # Advanced type detection for list
            arg.original_type_name: str = get_type_name(arg.translated_type, log_indent=1)
            if arg.is_list():
                arg.original_type_name = arg.original_type_name.replace("list", "").replace("[", "").replace("]", "")
                
                if arg.is_list() and arg.get_final_type() == list:  # If arg is a list of unspecified type, this is a list[str]
                    arg.translated_type = str
                    arg.original_type_name = get_type_name(list[str])
                    log.debug(f"        type is list[unspecified] and will be considered as list[str]")
                else:  # If list[str], list[int]...
                    arg.translated_type = get_type_from_str(arg.original_type_name)
                    log.debug(f"        type is list[{arg.get_final_type()}] and will be considered as list[{arg.get_final_type()}]")
            
            
            # Advanced type detection for Enums
            if arg.is_enum():
                arg.original_type_name = arg.get_final_type()
                arg.translated_type = str
                log.debug(f"        type is Enum({arg.original_type_name})")
                
            # Fix default value
            if arg.default == inspect._empty:
                arg.default = None
                arg.required = True
            log.debug(f"        {arg.default=}")
            log.debug(f"        {arg.required=}")
            
            # Build help
            if arg.translated_type == str and not arg.is_list():  # Add quotes to str
                arg.default_repr = f"'{arg.default}'"
            else:
                arg.default_repr = arg.default

            arg.description = get_arg_description(arg.name, function.__doc__)
            arg.description_repr = (
                f": {arg.description}" if arg.description != "" else f""
            )  # Handle empty arg.description
            arg.help = (
                f"[{'REQUIRED' if arg.required else 'optional'}, "
                f"{arg.original_type_name}, "
                f"default:{arg.default_repr}]"
                f"{arg.description_repr}"
            )
            
            arg.print(log_indent=1)
            
            subparser.add_argument(
                f"--{arg.name}",
                action=arg.get_action(log_indent=1),
                default=arg.default,
                type=arg.translated_type,
                choices=arg.get_choices(log_indent=1),
                required=arg.required,
                help=arg.help,
            )

    # Add a full help option
    full_help = ""
    subparsers_actions = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
    for subparsers_action in subparsers_actions:
        # get all subparsers and print help
        for choice, subparser in subparsers_action.choices.items():
            full_help += os.linesep + "-" * 80 + os.linesep + os.linesep
            full_help += f"Help for subcommand '{choice}':" + os.linesep
            full_help += subparser.format_help()
    parser.add_argument(f"--full-help", action="store_true", default=False, help="show help for every subcommands")

    # Add a version option
    #parser.add_argument("--version", action="version", version=module_version_repr)
    parser.add_argument(f"--version", action="store_true", default=False, help="show version")
    
    
    
    # Parse actual args values
    log.debug(f"")
    log.debug(f"")
    log.debug(f"Parsing call...")
    log.debug(f"---------------")
    
    # Extract options as a dict
    if len(sys.argv) >= 2 and sys.argv[1] in list(functions.keys()):
        # If subcommand provided
        log.debug(f"    subcommand provided")
        parsed_args = vars(parser.parse_args(sys.argv[1:]))
    else:
        # Else, if subcommand was NOT provided
        log.debug(f"    subcommand NOT provided")

        # If a specific flag is found, revert to default
        specific_flag_found = False
        for flag in ["-h", "--help", "--full-help", "--version"]:
            if flag in sys.argv:
                log.debug(f"    specific_flag_found=True")
                parsed_args = vars(parser.parse_args(sys.argv[1:]))
                specific_flag_found = True
                break

        # If a specific flag is NOT found, inject default_function_name into argv
        if not specific_flag_found:
            parsed_args = vars(parser.parse_args([default_function_name] + sys.argv[1:]))
    log.debug(f"    {parsed_args=}")
    
    
    # If full help is called, display it
    if parsed_args["full_help"]:
        parser.print_help()
        print(f"{full_help}")
        if exit_on_error:
            sys.exit(0)
    del parsed_args["full_help"]  # Clean parsed_args for further processing by the function

    # If version is called, display it
    if parsed_args["version"]:
        print(f"{module_version_repr}")
        if exit_on_error:
            sys.exit(0)
    del parsed_args["version"]  # Clean parsed_args for further processing by the function
    
    
    # Select fun to call
    if not parsed_args["subcommand"]:
        if default_function_name == "":
            print("Subcommand required!")
            parser.print_usage()
            if exit_on_error:
                sys.exit(1)
        else:
            parsed_args["subcommand"] = default_function_name
    function_name = parsed_args["subcommand"]
    function = functions[function_name]
    # Clean parsed_args for further processing by the function
    del parsed_args["subcommand"]
    log.debug(f"    {function_name=}")

    
    # Clean args
    parsed_args_tmp: dict = {}
    # Search for list type args
    for key, value in parsed_args.items():
        fun: Function = definitions[function_name]
        arg: Arg = fun.args[key]
        log.debug(f"parsing call for arg {arg.name}({arg.original_type}) = {value}")
        
        def cast_value(arg, value):
            if arg.is_enum():
                if isinstance(value, enum.Enum):
                    return value
                return arg.get_final_type().__getitem__(value)
            return value
                
        if arg.is_list():
            list_tmp = []
            for index, item in enumerate(value):
                tmp_value = cast_value(arg, item)
                log.debug(f"\t{index=}, {item=}, {tmp_value=}")
                list_tmp.append(tmp_value)
            value = list_tmp
        else:
            value = cast_value(arg, value)
        
        parsed_args_tmp[key] = value
    parsed_args = parsed_args_tmp

    # Call function
    log.debug(f"")
    log.debug(f"")
    log.debug(f"Calling function...")
    log.debug(f"---------------")
    try:
        function_result = function(**parsed_args)
        return function_result, parsed_args, parser
    except ArgError as e:
        print(f"ERROR: {e}")
        print()
        if exit_on_error:
            sys.exit(1)
    except TypeError as e:
        if e.__str__().startswith(f"{function_name}()") and e.__str__().__contains__(f"required positional argument"):
            # Not sure this branch can be take....
            print(f"ERROR: {e}")
            print()
            if exit_on_error:
                sys.exit(1)
        else:
            raise e