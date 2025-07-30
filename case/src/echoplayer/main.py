import argparse
import pathlib
import sys
from typing import Any

from .utils import Object, datum_transform


def gen_ocp_objlist(objects: list[Object],
                    show_datums: bool = False) -> dict[str, Any]:
    tree = {}

    for o in objects:
        om: dict[str, Any] = {}

        if not o.renderable:
            continue

        if o.compound:
            om["body"] = o.compound

        if o.datums and show_datums:
            datums: list[dict[str, Any]] = []

            for n, dt in o.datums.datums.items():
                datums.append({n: datum_transform(dt, o.datums_xform)})

            om["datums"] = datums

        if len(om) == 0:
            continue
        elif len(om) == 1:
            om = next(iter(om.values()))

        tree[o.name] = om

    return tree

def ocp_vscode_show(objects: list[Object],
                    show_datums: bool = False):
    from ocp_vscode import Camera, set_defaults, show # type: ignore

    objlist = gen_ocp_objlist(objects, show_datums=show_datums)

    set_defaults(reset_camera=Camera.KEEP, axes=True, axes0=True, grid=True)
    show(objlist, names=["root"])

def export_objects(objects: list[Object],
                   output_dir: pathlib.Path,
                   output_format: str,
                   output_prefix: str,
                   export_all: bool = False):
    from build123d import (
        export_gltf,
        export_step,
        export_stl,
    )

    exporters = {
        "gltf": export_gltf,
        "step": export_step,
        "stp": export_step,
        "stl": export_stl,
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    for obj in objects:
        if not obj.exportable or obj.compound is None:
            continue
        if not obj.manufacturable and not export_all:
            continue

        file_name = output_dir / f"{output_prefix}-{obj.name}.{output_format}"

        print(f"Writing {file_name}")
        exporters[output_format](obj.compound, file_name) # type: ignore

def show_warning():
    print("""
/!\\ WARNING /!\\

This case is incomplete and of DRAFT quality only!
""")

def main():
    parser = argparse.ArgumentParser()

    case_group = parser.add_argument_group(title="Case variant selection")
    case_group = case_group.add_mutually_exclusive_group(required=True)
    case_group.add_argument("--r1-rev1", action="store_true",
                            help="R1-Rev1 / R1-Rev1.1")

    viz_group = parser.add_argument_group(title="Visualization")
    viz_group.add_argument("--ocp-vscode", action="store_true",
                                  help="Visualize with ocp_vscode")
    viz_group.add_argument("--show-datums", action="store_true", default=False,
                           help="Show datum points in visualization")

    export_group = parser.add_argument_group(title="Exporting")
    export_group.add_argument("--export", metavar="DIR",
                              type=pathlib.Path,
                              help="Export model files")
    export_group.add_argument("--export-format", metavar="FMT", default="stl",
                              choices=("stl", "step", "stp", "gltf"),
                              help="Set export format (default: .stl)")
    export_group.add_argument("--export-all", action="store_true",
                              help="Also export mockup objects that are not manufacturable")

    test_group = parser.add_argument_group()
    test_group.add_argument("--test", action="store_true",
                            help=argparse.SUPPRESS)

    args = parser.parse_args()

    print("Building model...")

    if args.r1_rev1:
        from . import r1_rev1

        if args.export:
            show_warning()

        objects = r1_rev1.build()
        file_prefix = "echoplayer-r1-rev1"
    else:
        assert False, "Unknown case type"

    if args.test:
        print("Success!")
        sys.exit(0)

    if args.ocp_vscode:
        ocp_vscode_show(objects, show_datums=args.show_datums)

    if args.export:
        export_objects(objects,
                       output_dir = args.export,
                       output_format = args.export_format,
                       output_prefix = file_prefix,
                       export_all = args.export_all)

if __name__ == '__main__':
    pass
