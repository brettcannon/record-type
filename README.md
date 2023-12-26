# record-type

A proof-of-concept `record` type for Python.

## Goals

- Create a simple data type that's easy to explain to beginners
- Creating the data type itself should be fast
- Type annotations are supported, but not required
- Instances are immutable to make them (potentially) hashable
- Support Python's entire parameter definition syntax for instance
  instantiation, and do so idiomatically
- Support structural typing as much as possible (e.g., equality based on object
  "shape" instead of inheritance)

## Example

Let's say you're tracking items in your store. You may want to know an item's
name, price, and quantity on hand (this is an example from the
[`dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html)).
That can be represented as a simple data class to store all that information
together.

The `record` type is meant to help facilitate creating such simple data classes:

```python
from records import record

@record
def InventoryItem(name: str, price: float, *, quantity: int = 0):
    """Class for keeping track of an item in inventory."""
```

This creates an `InventoryItem` class whose call signature for intantiation
matches that of the function. Every parameter becomes the corresponding name of
an attribute that the argument gets assigned to. It also has:

- `__slots__` for performance
- `__match_args__` for pattern matching
- `__annotations__` for runtime type annotations
- `__eq__()` for equality
- `__hash__()` for hashing
- `__repr__()` which is suitable for `eval()`
- Immutability

### Compared to other approaches

#### `dataclasses.dataclass`

You can create a
[`dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass)
for this without much issue:

```python
from dataclasses import dataclass, KW_ONLY

@dataclass(frozen=True, slots=True)
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    name: str
    price: float
    _: KW_ONLY
    quantity: int = 0
```

The drawbacks compared to `record` are:

- The use of `KW_ONLY` is awkward
- It requires using type annotations
- To make it immutable -- which implies being hashable -- and use `__slots__`
  requires remembering to opting in with the appropriate parameters
- No support for `*args` or `**kwargs`

#### Named tuples

##### `collections.namedtuple`

Using
[`namedtuple`](https://docs.python.org/3/library/collections.html#collections.namedtuple)
allows for a quick way to  create the class:

```python
from collections import namedtuple

InventoryItem = namedtuple("InventoryItem", ["name", "price", "quantity"])
```

The drawbacks compared to `record` are:

- Unable to support keyword-only, positional-only, `*args`, and `**kwargs`
  parameters
- No support for type annotations
- No support for `__match_args__`
- Requires supporting both the attribute- and index-based APIs for any code
  going forward that returns an instance of the class
- No docstring

##### `typing.NamedTuple`

You can use
[`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
to create a class that supports type annotations for a named tuple:

```python
from typing import NamedTuple

class InventoryItem(NamedTuple):
    """Class for keeping track of an item in inventory."""
    name: str
    price: float
    quantity: int = 0
```

The drawbacks compared to `record` are:

- Unable to support keyword-only, positional-only, `*args`, and `**kwargs`
  parameters
- Requires type annotations
- No support for `__match_args__`
- Requires supporting both the attribute- and index-based APIs for any code
  going forward that returns an instance of the class

#### `types.SimpleNamespace`

You can create a simple function that wraps
[`SimpleNamespace`](https://docs.python.org/3/library/types.html#types.SimpleNamespace)

```python
from types import SimpleNamespace

def InventoryItem(name: str, price: float, *, quantity: int = 0):
    return SimpleNamespace(name=name, price=price, quantity=quantity)
```

The drawbacks compared to `record` are:

- No support for `__slots__`
- No support for `__match_args__`
- No docstring
- No runtime type annotations
- Mutable (and so no hashing)

#### Manual

You can implement the equivalent of `record` manually:

```python
from typing import Any, NoReturn


class InventoryItem:
    """Class for keeping track of an item in inventory."""

    __slots__ = ("name", "price", "quantity")
    __match_args__ = ("name", "price")

    name: str
    price: float
    quantity: int

    def __init__(self, name: str, price: float, *, quantity: int = 0) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "price", price)
        object.__setattr__(self, "quantity", quantity)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}, {self.price!r}, quantity={self.quantity!r})"

    def __setattr__(self, _attr: Any, _val: Any) -> NoReturn:
        raise TypeError(f"{self.__class__.__name__} is immutable")

    def __eq__(self, other: Any) -> bool:
        if self.__slots__ != getattr(other, "__slots__", None):
            return NotImplemented
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__slots__
        )

    def __hash__(self) -> int:
        return hash(tuple(self.name, self.price, self.quantity))
```

The drawbacks compared to `record` are:

- It's much more verbose to implement
