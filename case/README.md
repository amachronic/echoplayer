# Echo R1 Case

The Echo R1 case is designed with [build123d](https://github.com/gumyr/build123d),
a Python-based parametric BREP CAD package using the OpenCASCADE
geometry kernel. The case can be exported to STEP or STL files for
3D printing or to edit in other CAD applications.

## Installation

CAD models are produced by running the `echoplayer-case` script.
This needs to be installed first; the recommended way is to set
up a Python virtual environment (venv) and perform an editable
install, which allows you to modify and run the script in place.

This can be done from the shell / command line like this:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Exporting

To export STLs, run:

```
echoplayer-case --r1-rev1 --export out
```

You can also output STEP (or GLTF) files with the `--export-format` option:

```
echoplayer-case --r1-rev1 --export out --export-format stp
```

STEP is recommended if you want to make changes in another BREP
CAD package. STLs are meshes and only suitable for 3D printing.

The `--export DIR` option will write one file per unique part
to the output directory `DIR`. Some parts, like buttons, will
require multiple copies produced. At some point this will be
properly documented in BOM data for the player, but for now
you need to figure it out from looking at the render.

## Visualizing

If making edits to the code, you probably want to see what you are
doing to the model. There is built-in support for
[ocp_vscode](https://github.com/bernhard-42/vscode-ocp-cad-viewer),
which can be run either from VSCode or as a standalone server that
is accessed by a browser.

To start the standalone server:

```
python3 -m ocp_vscode
```

Navigate to `http://localhost:3939/viewer` in a browser and then
display the model with:

```
echoplayer-case --r1-rev1 --ocp-vscode
```

Passing the `--show-datums` option will include datum points and
planes in the visualization.

## Development

If you are going to be making any major changes to the Python code,
you should install development dependencies and run checks with `tox`.
Run the following command in a venv:

```
pip install -e .[dev]
```

Usage of `tox` is very simple:

```
tox r -e mypy   # type check
tox r -e ruff   # lint
tox r -e test   # test build of the case
tox p           # run all in parallel
```
