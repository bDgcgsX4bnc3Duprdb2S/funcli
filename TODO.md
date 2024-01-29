dans le help:
    pour les list, le type est incorecte. peut-etre plutot mettre une colone single/multiple
    pour les list d'enum ou les enums, l'affichage valeur par défaut est dégueu


TODO
    add support for param: str|float
    Error : ValueError: str | float is not callable
TODO
    add support for dynamic __doc__
    add support for inline comments.
        def say_hello(
            name: str = "world",  # The name of the guy to say hello to
            # Eg: "john"
            age: int # the aged of the guy
        ):
            ...
TODO
    bug: les param de la fct et de la doc peuvent avoir un ordre différent.
    Ca casse l'interprétation du :return: si celui-ci fait plusieurs lignes.
TODO
    When a fun2 call another fun1, allow to ref parameters of fun1 in fun2 help
        def fun1(
            param1: str = "" # This is param1
        ):
            ...
        def fun2(
            param1: str = "world",  # ref=fun1.param1
            # And keep on adding details to param1 help!
        ):
        ""
        ref=fun1.__doc__
        And keep on adding details to fun2 help!
        ""
            return fun1(param1)
