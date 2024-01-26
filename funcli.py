

import argparse
import inspect
import logging
import os
import sys

log = logging.getLogger(__name__)


class ArgError(ValueError):
    def __init__(self, arg_name: str, message: str, *args: object) -> None:
        self.arg_name = arg_name
        self.message = message
        super().__init__(f"{arg_name}: {message}", *args)


def get_type_name(a_type) -> str:
    if type(a_type) == type:  # If it's a basic type like int, str, bool...
        # Get the type name this way
        return a_type.__name__
    else:  # If it's a more specific type like list[int]...
        # Get the type name that way
        return str(a_type)


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
        
        # Create a parser for each function
        # Tag default function in help
        function_help = ""
        if function_name == default_function_name:
            function_help = f"[default if no subcommand provided]" + os.linesep
            log.debug(f"    DEFAULT if no subcommand provided")
            
        # Use docstring as help
        function_doc = ""
        if function.__doc__ is not None:
            function_doc = function.__doc__
            function_help += extract_description_from_docstring(function_doc)
        else:
            function_help += function_doc
        subparser = subparsers.add_parser(
            name=function_name,
            help=function_help,
            description=function_help,
            formatter_class=argparse.RawTextHelpFormatter,
        )

        # If there are args, add them to CLI
        for arg_name, parameter in inspect.signature(function).parameters.items():
            log.debug(f"    {arg_name=}")
            
            # Default storage mode
            arg_action = "store"
            
            # Analyze arg properties
            arg_required = False
            arg_default = parameter.default

            # Detect type
            if parameter.annotation != inspect._empty:  # Annotated
                arg_type = parameter.annotation
                true_arg_type = arg_type
                log.debug(f"        type is explicitly defined as {arg_type=}")
                
            elif arg_default != inspect._empty:  # Not annotated but default value
                if arg_default is not None:
                    arg_type = type(arg_default)
                    true_arg_type = arg_type
                else:
                    arg_type = str
                    true_arg_type = type(None)
                log.debug(f"        type is implicitly defined as {arg_type=}")
                
            else:  # Not annotated and no default value
                arg_type = str
                true_arg_type = type(None)
                log.debug(f"        type is unknown and will be considered as {arg_type=}")
                
                
            # Advanced type detection for list
            arg_type_name: str = get_type_name(arg_type)
            arg_sub_type_name: str = arg_type_name.replace("list", "").replace("[", "").replace("]", "")
            
            if arg_type_name.startswith("list"):
                # Use the list mecanism builtin argparse
                arg_action = argparse._AppendAction
                log.debug(f"        {arg_action=}")
                
                if arg_sub_type_name == "":  # If arg is a list of unspecified type, this is a list[str]
                    arg_type = str
                    arg_type_name = get_type_name(list[str])
                    log.debug(f"        type is list[unspecified] and will be considered as {arg_type_name=}")
                else:  # If list[str], list[int]...
                    arg_type = get_type_from_str(arg_sub_type_name)
                    log.debug(f"        type is {arg_type=} and will be considered as such")
            
            
            # Specifics for bool
            if arg_type == bool:  # If arg is a bool
                arg_action = argparse.BooleanOptionalAction  # Use the flag/no-flag mecanism builtin argparse
                log.debug(f"        {arg_action=}")


            # Fix default value
            if arg_default == inspect._empty:
                arg_default = None
                arg_required = True
            log.debug(f"        {arg_default=}")
            log.debug(f"        {arg_required=}")
            
            # Build help
            if true_arg_type == str:  # Add quotes to str
                arg_default_repr = f"'{arg_default}'"
            else:
                arg_default_repr = arg_default

            arg_description = get_arg_description(arg_name, function_doc)
            arg_description_repr = (
                f": {arg_description}" if arg_description != "" else f""
            )  # Handle empty arg_description
            arg_help = (
                f"[{'REQUIRED' if arg_required else 'optional'}, "
                f"{arg_type_name}, "
                f"default:{arg_default_repr}]"
                f"{arg_description_repr}"
            )
            
            subparser.add_argument(
                f"--{arg_name}",
                type=arg_type,
                required=arg_required,
                action=arg_action,
                default=arg_default,
                help=arg_help,
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

    
    """# Clean lists args
    parsed_args_tmp = parsed_args.copy()
    # Search for list type args
    for key, value in parsed_args_tmp.items():
        if type(value) == type([]):
            # Replace their value with a joined version
            parsed_args[key] = []
            new_item = ""
            for item in value:
                new_item = "".join(item)  # ['t','e','s','t'] -> 'test'
                parsed_args[key].append(new_item)"""

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