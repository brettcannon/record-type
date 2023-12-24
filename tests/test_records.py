from typing import TypedDict, Unpack

import pytest

import records


@records.record
def AllParameterTypes(
    pos: float,
    /,
    pos_kw: int,
    *args: int,
    kw: str,
    **kwargs: int,
):
    """An example with all the types of possible parameters."""


def test_slots():
    """All parameters are listed in __slots__."""
    expected = "pos", "pos_kw", "args", "kw", "kwargs"
    assert tuple(AllParameterTypes.__slots__) == expected


def test_no_slots():
    """No parameters, no slots."""

    @records.record
    def NoParameters():
        """An example with no parameters."""

    assert tuple(NoParameters.__slots__) == ()


def test_single_slots():
    """A single parameter, a single slot."""

    @records.record
    def SingleParameter(only_one: float):
        """An example with a single parameter."""

    assert tuple(SingleParameter.__slots__) == ("only_one",)


def test_match_args():
    """__match_args__ contains all non-keyword, non-excess parameters."""
    expected = "pos", "pos_kw"
    assert tuple(AllParameterTypes.__match_args__) == expected


def test_annotations():
    """__annotations__ contains all parameters and a return type of `None`.

    The parameter order is preserved in the dict.
    """
    expected = {
        "pos": float,
        "pos_kw": int,
        "args": tuple[int],
        "kw": str,
        "kwargs": dict[str, int],
    }
    assert AllParameterTypes.__annotations__ == expected
    assert tuple(AllParameterTypes.__annotations__.keys()) == tuple(expected.keys())


def test_text_annotations():
    @records.record
    def Example(x: "int", *args: "int", **kwargs: "int"):
        """An example."""

    assert Example.__annotations__ == {
        "x": "int",
        "args": "tuple[int]",
        "kwargs": "dict[str, int]",
    }


def test_unpack_kwags_annotations():
    @records.record
    def Example(**kwargs: Unpack[TypedDict]):
        pass

    assert Example.__annotations__ == {"kwargs": TypedDict}


def test_unpack_kwags_text_annotations():
    @records.record
    def Example(**kwargs: "Unpack[TypedDict]"):
        pass

    assert Example.__annotations__ == {"kwargs": "TypedDict"}


def test_no_annotations():
    """A record with no annotations is valid."""

    @records.record
    def NoAnnotations(x, y):
        """An example with no annotations."""

    assert NoAnnotations.__annotations__ == {}


def test_return_annotation():
    """The return annotation can only be `None` or unset."""

    @records.record
    def no_return_annotation():
        pass

    assert no_return_annotation()

    @records.record
    def redundant_return_annotation() -> None:
        pass

    assert redundant_return_annotation()

    with pytest.raises(TypeError):

        @records.record
        def bad_return_annotation() -> int:
            pass


def test_doc():
    """__doc__ is preserved."""

    @records.record
    def Documented():
        """This is the docstring."""

    assert Documented.__doc__ == "This is the docstring."


def test_name():
    """__name__ is preserved."""

    @records.record
    def Named():
        pass

    assert Named.__name__ == "Named"


def test_qualname():
    """__qualname__ is preserved."""

    @records.record
    def Inner():
        pass

    assert Inner.__qualname__ == "test_qualname.<locals>.Inner"


def test_module():
    """__module__ is preserved."""

    @records.record
    def InModule():
        pass

    assert InModule.__module__ == "test_records"


def test_eq():
    @records.record
    def Point2D(x: float, y: float):
        """A simple 2D point."""

    args = 2.0, 3.0
    ins = Point2D(*args)
    assert ins == Point2D(*args)

    @records.record
    def Point1D(x: float):
        """A simple 1D point."""

    assert Point1D(args[0]) != Point2D(*args)

    class HasSlots:
        __slots__ = "x", "y"

    assert HasSlots() != Point2D(*args)

    has_slots = HasSlots()
    has_slots.x, has_slots.y = args
    assert has_slots == Point2D(*args)


def test_hash():
    @records.record
    def Point2D(x: float, y: float):
        """A simple 2D point."""

    ins = Point2D(2.0, 3.0)
    assert hash(ins) == hash(Point2D(2.0, 3.0))


def test_default_values():
    @records.record
    def Defaults(a=1, /, b=2, *, c=3):
        pass

    ins = Defaults()

    assert ins.a == 1
    assert ins.b == 2
    assert ins.c == 3


def test_bad_repr():
    """Handle non-syntactic representations for both type hints and default values."""

    class FunkyRepr:
        def __repr__(self):
            return "!!! not valid Python !!!"

    funky_repr = FunkyRepr()

    @records.record
    def Example(x: float = 0.0, y: FunkyRepr = funky_repr):
        """A simple 2D point."""

    ins = Example()
    assert ins.x == 0.0
    assert ins.y == funky_repr


def test_immutable():
    @records.record
    def Example(x, y=None):
        """An example."""

    ins = Example(1)

    with pytest.raises(TypeError):
        ins.x = 2

    with pytest.raises(TypeError):
        ins.y = 3

    with pytest.raises(TypeError):
        del ins.x

    with pytest.raises(TypeError):
        del ins.y


def test_init():
    """__init__ accepts all parameters."""
    ins = AllParameterTypes(
        1.0,
        2,
        3,
        4,
        kw="5",
        kwarg_1=6,
    )

    assert ins.pos == 1.0
    assert ins.pos_kw == 2
    assert ins.args == (3, 4)
    assert ins.kw == "5"
    assert ins.kwargs == {"kwarg_1": 6}


def test_init_annotations():
    @records.record
    def Example(x: int, y: int):
        """An example."""

    assert Example.__init__.__annotations__ == {"x": int, "y": int, "return": None}


def test_no_parameters():
    """A record with no parameters is valid."""

    @records.record
    def NoParameters():
        """An example with no parameters."""

    assert NoParameters()


def test_repr():
    """__repr__ returns a string representation of the record."""
    ins = AllParameterTypes(
        1.0,
        2,
        3,
        4,
        kw="5",
        kwarg_1=6,
    )

    assert (
        repr(ins)
        == "AllParameterTypes(1.0, pos_kw=2, *(3, 4), kw='5', **{'kwarg_1': 6})"
    )
