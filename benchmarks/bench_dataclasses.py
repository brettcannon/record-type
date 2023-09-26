import dataclasses

import records


@dataclasses.dataclass(frozen=True, slots=True)
class Point3DDataclass:
    """A point in 3D space."""

    x: float
    y: float
    z: float


@records.record
def Point3DRecord(x: float, y: float, z: float):
    """A point in 3D space."""


point_3D_dataclass = Point3DDataclass(1.0, 2.0, 3.0)


def create_dataclass():
    @dataclasses.dataclass(frozen=True, slots=True)
    class Point3D:
        """A point in 3D space."""

        x: float
        y: float
        z: float


point_3D_record = Point3DRecord(1.0, 2.0, 3.0)


def create_record():
    @records.record
    def Point3D(x: float, y: float, z: float):
        """A point in 3D space."""


def instantiate_dataclass():
    Point3DDataclass(1.0, 2.0, 3.0)


def instantiate_record():
    Point3DRecord(1.0, 2.0, 3.0)


def access_dataclass():
    point_3D_dataclass.x
    point_3D_dataclass.y
    point_3D_dataclass.z


def access_record():
    point_3D_record.x
    point_3D_record.y
    point_3D_record.z


def equal_dataclass():
    point_3D_dataclass == point_3D_dataclass


def equal_record():
    point_3D_record == point_3D_record


def hash_dataclass():
    hash(point_3D_dataclass)


def hash_record():
    hash(point_3D_record)


__benchmarks__ = [
    (create_dataclass, create_record, "class creation"),
    (instantiate_dataclass, instantiate_record, "instantiation"),
    (access_dataclass, access_record, "attribute access"),
    (equal_dataclass, equal_record, "equality"),
    (hash_dataclass, hash_record, "hashing"),
]
