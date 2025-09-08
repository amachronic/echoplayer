from build123d import Axis, Compound, Location, Plane, Vector
from typing import Any, Optional, TypeAlias, Union, overload
from dataclasses import dataclass, field as dataclass_field
from copy import copy

PlaneLike: TypeAlias = Plane
VectorLike: TypeAlias = Vector | tuple[float, float, float]

def plane_at(plane: Plane,
             *,
             origin: Optional[VectorLike] = None,
             projected_origin: Optional[VectorLike] = None,
             x: Optional[float] = None,
             y: Optional[float] = None,
             z: Optional[float] = None,
             dx: float = 0,
             dy: float = 0,
             dz: float = 0) -> Plane:
    """
    Return a plane parallel to the input plane, centered at the given origin
    """

    if isinstance(plane, str):
        gplane = getattr(Plane, plane)
        assert isinstance(gplane, Plane)
    elif isinstance(plane, Plane):
        gplane = plane
    else:
        raise TypeError(f"bad plane {type(plane)}")

    if projected_origin:
        origin = Vector(projected_origin).project_to_plane(gplane)
    else:
        origin = Vector(origin or gplane.origin)

    origin.X = x or origin.X
    origin.Y = y or origin.Y
    origin.Z = z or origin.Z
    origin.X += dx
    origin.Y += dy
    origin.Z += dz

    return Plane(origin=origin, x_dir=gplane.x_dir, z_dir=gplane.z_dir)


def point_at(origin: VectorLike = (0, 0, 0),
             *,
             x: Optional[float] = None,
             y: Optional[float] = None,
             z: Optional[float] = None,
             dx: float = 0,
             dy: float = 0,
             dz: float = 0) -> Vector:
    """
    Return a point
    """
    pt = Vector(origin)
    pt.X = x if x else pt.X
    pt.Y = y if y else pt.Y
    pt.Z = z if z else pt.Z
    pt.X += dx
    pt.Y += dy
    pt.Z += dz
    return pt

Datum: TypeAlias = Union[Vector, Axis, Plane]

# build123d is unbelievably inconsistent with 3D math...

def datum_pos(d: Datum) -> Vector:
    if isinstance(d, Vector):
        return d
    if isinstance(d, Axis):
        return d.position
    if isinstance(d, Plane):
        return d.origin

    raise TypeError(type(d))

def datum_setpos(d: Datum, p: Vector) -> None:
    if isinstance(d, Vector):
        d.X = p.X
        d.Y = p.Y
        d.Z = p.Z
    elif isinstance(d, Axis):
        d.position = p
    elif isinstance(d, Plane):
        d.origin = p
    else:
        raise TypeError(type(d))

def datum_loc(d: Datum) -> Location:
    if isinstance(d, Vector):
        return Location(d)
    if isinstance(d, Axis):
        return d.location
    if isinstance(d, Plane):
        return d.location

    raise TypeError(type(d))

@overload
def datum_transform(d: None, xform: Location) -> None: ...
@overload
def datum_transform(d: Vector, xform: Location) -> Vector: ...
@overload
def datum_transform(d: Axis, xform: Location) -> Axis: ...
@overload
def datum_transform(d: Plane, xform: Location) -> Plane: ...

def datum_transform(d: Optional[Datum], xform: Location) -> Optional[Datum]:
    if d is None:
        return None
    if isinstance(d, Vector):
        return d + xform.position
    if isinstance(d, Axis):
        return copy(d).located(xform)
    if isinstance(d, Plane):
        return copy(d).move(xform)

    raise TypeError(type(d))

class DatumSetRef:
    ref: "DatumSet"
    loc: Location

    def __init__(self, ref: "DatumSet", loc: Location):
        self.ref = ref
        self.loc = loc

    def get_datum(self, name: str) -> Optional[Datum]:
        return datum_transform(self.ref.get_datum(name), self.loc)

    def get_point(self, name: str) -> Vector:
        return datum_transform(self.ref.get_point(name), self.loc)

    def get_axis(self, name: str) -> Axis:
        return datum_transform(self.ref.get_axis(name), self.loc)

    def get_plane(self, name: str) -> Plane:
        return datum_transform(self.ref.get_plane(name), self.loc)

    def get_ref(self, name: str) -> "DatumSetRef":
        subref = self.ref.get_ref(name)
        return DatumSetRef(subref.ref, self.loc * subref.loc)

    def box_dimension(self, name_prefix: str, axis: str) -> float:
        return self.ref.box_dimension(name_prefix, axis)

    def box_point(self, name_prefix: str, align: VectorLike) -> Vector:
        return datum_transform(self.ref.box_point(name_prefix, align), self.loc)

    def __getattr__(self, name: str) -> Any:
        datum = self.get_datum(name)
        if datum is not None:
            return datum

        if name in self.ref.refs:
            return self.get_ref(name)

        raise AttributeError(name)

class DatumSet:
    """
    A DatumSet is a container for named reference features (datums) sharing
    a common coordinate system.

    Datums are independent of model geometry and can be used to help simplify
    the construction of complex objects. Datums are points, lines, or planes,
    corresponding to the build123d types Vector, Axis, or Plane, respectively.
    Datum objects can be computed directly or they can be derived from faces,
    edges, or vertexes.

    All datums within the same DatumSet are assumed to lie within a shared
    coordinate system -- this makes it possible to compare arbitrary datums
    within the set and apply rigid transforms to DatumSets.

    It is possible to attach one DatumSet to another using a transform, and
    then reference datums in the attached DatumSet by adding aliases in the
    parent DatumSet. The referenced datums will be transformed automatically.
    This can be done recursively, allowing DatumSets to describe assemblies
    involving multiple objects.
    """

    datums: dict[str, Datum]
    aliases: dict[str, tuple[str, str]]
    refs: dict[str, DatumSetRef]

    @staticmethod
    def __refname(ref: Optional[str]):
        if ref is None:
            return ""

        if len(ref) == 0:
            raise ValueError("DatumSet refname must not be an empty string")

        return ref

    def __init__(self):
        self.datums = {}
        self.aliases = {}
        self.refs = { DatumSet.__refname(None) : DatumSetRef(self, Location()) }

    def add_point(self,
                  name: str,
                  origin: Optional[VectorLike] = None,
                  *,
                  X: Optional[float] = None,
                  Y: Optional[float] = None,
                  Z: Optional[float] = None,
                  dX: float = 0,
                  dY: float = 0,
                  dZ: float = 0) -> None:
        if origin is None:
            origin = Vector()
        else:
            origin = Vector(origin)

        return self.add_datum(name, origin, X=X, Y=Y, Z=Z, dX=dX, dY=dY, dZ=dZ)

    def add_axis(self,
                 name: str,
                 axis: Axis,
                 *,
                 origin: Optional[VectorLike] = None,
                 X: Optional[float] = None,
                 Y: Optional[float] = None,
                 Z: Optional[float] = None,
                 dX: float = 0,
                 dY: float = 0,
                 dZ: float = 0) -> None:
        return self.add_datum(name, axis, origin=origin, X=X, Y=Y, Z=Z, dX=dX, dY=dY, dZ=dZ)

    def add_plane(self,
                  name: str,
                  plane: Plane,
                  *,
                  projected_origin: Optional[VectorLike] = None,
                  origin: Optional[VectorLike] = None,
                  X: Optional[float] = None,
                  Y: Optional[float] = None,
                  Z: Optional[float] = None,
                  dX: float = 0,
                  dY: float = 0,
                  dZ: float = 0) -> None:
        if projected_origin is not None:
            if origin is not None:
                raise ValueError("use only one of origin and projected_origin")

            origin = Vector(projected_origin).project_to_plane(plane)

        return self.add_datum(name, plane, origin=origin, X=X, Y=Y, Z=Z, dX=dX, dY=dY, dZ=dZ)

    def add_datum(self,
                  name: str,
                  datum: Datum,
                  *,
                  origin: Optional[VectorLike] = None,
                  X: Optional[float] = None,
                  Y: Optional[float] = None,
                  Z: Optional[float] = None,
                  dX: float = 0,
                  dY: float = 0,
                  dZ: float = 0) -> None:
        if name in self.datums:
            raise ValueError(f"Datum \"{name}\" already exists")
        if name in self.aliases:
            raise ValueError(f"Datum \"{name}\" shadows existing alias")
        if name in self.refs:
            raise ValueError(f"Datum \"{name}\" shadows datum set reference")

        if origin is not None:
            origin = Vector(origin)
        else:
            origin = datum_pos(datum)

        origin.X = (X or origin.X) + dX
        origin.Y = (Y or origin.Y) + dY
        origin.Z = (Z or origin.Z) + dZ

        ldatum = copy(datum)
        datum_setpos(ldatum, origin)

        self.datums[name] = ldatum

    def add_reference(self,
                      ref: str,
                      datums: "DatumSet",
                      transform: Location = Location()) -> None:
        refname = DatumSet.__refname(ref)
        if refname in self.datums:
            raise ValueError(f"DatumSet reference \"{refname}\" shadows existing datum")
        if refname in self.aliases:
            raise ValueError(f"DatumSet reference \"{refname}\" shadows existing alias")
        if refname in self.refs:
            raise ValueError(f"DatumSet reference \"{refname}\" already exists")

        self.refs[refname] = DatumSetRef(datums, copy(transform))

    def add_alias(self,
                  newname: str,
                  name: str,
                  ref: Optional[str] = None) -> None:
        if newname in self.datums:
            raise ValueError(f"Alias \"{newname}\" shadows existing datum")
        if newname in self.refs:
            raise ValueError(f"Alias \"{newname}\" shadows datum set reference")
        if newname in self.aliases:
            raise ValueError(f"Alias \"{newname}\" already exists")

        refname = DatumSet.__refname(ref)
        if refname not in self.refs:
            raise ValueError(f"Reference \"{refname}\" does not exist")
        if self.refs[refname].get_datum(name) is None:
            raise ValueError(f"Datum \"{name}\" not found in reference \"{refname}\"")

        self.aliases[newname] = (refname, name)

    def get_datum(self, name: str) -> Optional[Datum]:
        datum = self.datums.get(name)
        if datum is not None:
            return copy(datum)

        alias = self.aliases.get(name)
        if alias is not None:
            refname, othername = alias
            return self.get_ref(refname).get_datum(othername)

        return None

    def get_point(self, name: str) -> Vector:
        datum = self.get_datum(name)
        if datum is None:
            raise KeyError(name)
        if type(datum) is not Vector:
            raise TypeError(f"{name} is not a point")

        return datum

    def get_axis(self, name: str) -> Axis:
        datum = self.get_datum(name)
        if datum is None:
            raise KeyError(name)
        if type(datum) is not Axis:
            raise TypeError(f"{name} is not an axis")

        return datum

    def get_plane(self, name: str) -> Plane:
        datum = self.get_datum(name)
        if datum is None:
            raise KeyError(name)
        if type(datum) is not Plane:
            raise TypeError(f"{name} is not a plane")

        return datum

    def get_ref(self, name: str) -> DatumSetRef:
        return self.refs[name]

    def point(self, name: str) -> Vector:
        return self.get_point(name)

    def plane(self, name: str) -> Plane:
        return self.get_plane(name)

    def __getattr__(self, name: str) -> Any:
        datum = self.get_datum(name)
        if datum is not None:
            return datum

        ref = self.refs.get(name)
        if ref is not None:
            return ref

        raise AttributeError(name)

    def add_box(
        self,
        name_prefix: str,
        dimensions: VectorLike,
        origin: VectorLike = (0, 0, 0),
        alignment: VectorLike = (0, 0, 0),
    ):
        origin_t = tuple(origin)
        alignment_t = tuple(alignment)
        dimensions_t = tuple(dimensions)
        axis_mapping = {
            "front":  (2, "z", 1),
            "back":   (2, "z", -1),
            "top":    (1, "y", 1),
            "bottom": (1, "y", -1),
            "right":  (0, "x", 1),
            "left":   (0, "x", -1),
        }

        base_planes = {
            "xy": Plane.XY,
            "xz": Plane.XZ,
            "yz": Plane.YZ,
        }

        for name_suffix in axis_mapping:
            name = f"{name_prefix}_{name_suffix}"
            index, coord, sign = axis_mapping[name_suffix]
            plane = base_planes["xyz".replace(coord, "")]

            if alignment_t[index] == 0:
                offset = sign * dimensions_t[index] / 2
            elif sign * alignment_t[index] < 0:
                offset = sign * dimensions_t[index]
            else:
                offset = 0

            args = [origin_t[0], origin_t[1], origin_t[2]]
            args[index] += offset
            self.add_plane(name, plane=plane, origin=Vector(*args))

    def box_dimension(self, name_prefix: str, axis: str) -> float:
        axis_mapping = {
            "x": ("left", "right"),
            "y": ("bottom", "top"),
            "z": ("back", "front"),
        }

        side0, side1 = axis_mapping[axis]
        plane0 = self.get_plane(f"{name_prefix}_{side0}")
        plane1 = self.get_plane(f"{name_prefix}_{side1}")

        return (getattr(plane1.origin, axis.upper()) -
                getattr(plane0.origin, axis.upper()))

    def box_point(self, name_prefix: str, align: VectorLike) -> Vector:
        align_t = tuple(align)
        out_t = [0, 0, 0]
        axis_mapping = (
            ("x", "left", "right"),
            ("y", "bottom", "top"),
            ("z", "back", "front"),
        )

        for index in range(3):
            axis, side0, side1 = axis_mapping[index]
            plane0 = self.get_plane(f"{name_prefix}_{side0}")
            plane1 = self.get_plane(f"{name_prefix}_{side1}")

            if align_t[index] == 0:
                coord = (getattr(plane0.origin, axis.upper()) +
                         getattr(plane1.origin, axis.upper())) / 2
            elif align_t[index] < 0:
                coord = getattr(plane0.origin, axis.upper())
            else:
                coord = getattr(plane1.origin, axis.upper())

            out_t[index] = coord

        return Vector(*out_t)


@dataclass
class Object:
    # Name of the object for rendering and exporting
    name: str

    # Compound and datum points
    compound: Optional[Compound] = None
    datums: Optional[DatumSet] = None
    datums_xform: Location = dataclass_field(default_factory=Location)

    # Control whether the object is used for rendering, exporting, or both.
    # This is used for instanced objects like buttons which have only one
    # model to export but need to appear multiple times for rendering.
    renderable: bool = True
    exportable: bool = True

    # Flag for manufacturable objects; false for render-only mockups.
    # Mockup objects are still exportable because they may be useful
    # to import to another CAD package.
    manufacturable: bool = True
