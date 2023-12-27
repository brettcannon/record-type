import inspect
import typing


def _make_var_positional_annotation(annotation):
    """Convert the type annotation for *args to an appropriate one for a record."""
    if isinstance(annotation, str):
        return f"tuple[{annotation}]"
    else:
        return tuple[annotation]


def _make_var_keyword_annotation(annotation):
    """Convert the type annotation for **kwargs to an appropriate one for a record."""
    if isinstance(annotation, str):
        if annotation.startswith("Unpack["):
            return annotation.removeprefix("Unpack[").removesuffix("]")
        else:
            return f"dict[str, {annotation}]"
    # typing.Unpack explicitly refuses to work with isinstance() and
    # issubclass() due to returning different things depending on what is
    # passed into the constructor.
    elif isinstance(annotation, typing.Unpack[typing.TypedDict].__class__):
        return annotation.__args__[0]
    else:
        return dict[str, annotation]


class Record:
    __slots__ = ()

    def __eq__(self, other):
        """Check for equality.

        The comparison is done per-attribute to allow for duck typing (i.e.,
        nominal typing is not used as a shortcut for comparing).
        """
        other_attrs = frozenset(getattr(type(other), "__slots__", [object()]))
        self_attrs = frozenset(type(self).__slots__)
        if self_attrs != other_attrs:
            # Avoids the question of what to do if there are extra attributes on
            # `other`.
            return NotImplemented

        for attr in self_attrs:
            if not hasattr(other, attr):
                return NotImplemented
            elif getattr(self, attr) != getattr(other, attr):
                return False
        else:
            return True

    def __hash__(self):
        return hash(tuple(getattr(self, name) for name in self.__slots__))

    def __setattr__(self, *_):
        raise TypeError(
            f"{type(self).__name__} object does not support attribute assignment"
        )

    def __delattr__(self, *_):
        raise TypeError(
            f"{type(self).__name__} object does not support attribute deletion"
        )

    def __repr__(self):
        init_signature = inspect.signature(self.__init__)
        args = []
        # Using the bound `__init__()` means `inspect` takes care of `self`.
        for parameter in init_signature.parameters.values():
            param_repr = repr(getattr(self, parameter.name))
            match parameter.kind:
                case parameter.POSITIONAL_ONLY:
                    args.append(param_repr)
                case parameter.POSITIONAL_OR_KEYWORD | parameter.KEYWORD_ONLY:
                    args.append(f"{parameter.name}={param_repr}")
                case parameter.VAR_POSITIONAL:
                    args.append(f"*{param_repr}")
                case parameter.VAR_KEYWORD:
                    args.append(f"**{param_repr}")
                case _:
                    typing.assert_never(parameter.kind)
        return f"{type(self).__name__}({', '.join(args)})"


def record(func):
    """Create a record type."""
    name = func.__name__
    func_signature = inspect.signature(func)
    if func_signature.return_annotation not in {inspect.Signature.empty, None}:
        raise TypeError("return type annotation can only be 'None' or unset")

    self_parameter = inspect.Parameter("self", inspect.Parameter.POSITIONAL_ONLY)
    init_signature = func_signature.replace(
        parameters=(
            self_parameter,
            *(
                param.replace(default=param.empty, annotation=param.empty)
                for param in func_signature.parameters.values()
            ),
        )
    )

    parameters = (
        f"object.__setattr__(self, {name!r}, {name})"
        for name in func_signature.parameters
    )
    init_body = (f"\n{' ' * 8}").join(parameters) or "pass"

    if len(func_signature.parameters) == 1:
        slots = f"{next(iter(func_signature.parameters))!r},"
    else:
        slots = ", ".join(map(repr, func_signature.parameters))

    class_syntax = f"""\
class {name}(Record):
    __slots__ = ({slots})

    def __init__{init_signature}:
        {init_body}
"""
    globals = {"Record": Record}
    exec(class_syntax, globals)
    cls = globals[name]
    cls.__qualname__ = func.__qualname__
    cls.__module__ = func.__module__
    cls.__doc__ = func.__doc__
    proposed_annotations = func.__annotations__.copy()
    try:
        del proposed_annotations["return"]
    except KeyError:
        pass

    # Buid annotations dict from scratch to keep the iteration order.
    cls_annotations = {}
    for parameter in func_signature.parameters.values():
        if parameter.name not in proposed_annotations:
            continue
        annotation = proposed_annotations[parameter.name]
        if parameter.kind == parameter.VAR_POSITIONAL:
            annotation = _make_var_positional_annotation(annotation)
        elif parameter.kind == parameter.VAR_KEYWORD:
            annotation = _make_var_keyword_annotation(annotation)

        cls_annotations[parameter.name] = annotation

    cls.__annotations__ = cls_annotations

    match_args = []
    for parameter in func_signature.parameters.values():
        if parameter.kind in {
            parameter.VAR_POSITIONAL,
            parameter.KEYWORD_ONLY,
            parameter.VAR_KEYWORD,
        }:
            break
        match_args.append(parameter.name)

    cls.__match_args__ = tuple(match_args)

    # The return annotations was guaranteed earlier.
    cls.__init__.__annotations__ = func.__annotations__ | {"return": None}
    cls.__init__.__defaults__ = func.__defaults__
    cls.__init__.__kwdefaults__ = func.__kwdefaults__

    return cls
