##
## Global make targets
##

all: gerbers schematics
clean:

##
## Global variables
##

empty :=
space := $(empty) $(empty)
comma := ,

##
## Build rules for PCBs
##

INPUT_SCH := r1-rev1/echo-r1-rev1.kicad_sch
INPUT_PCB := r1-rev1/echo-r1-rev1.kicad_pcb
OUT_DIR   := r1-rev1/out

include mk/gerber.mk
include mk/schematic.mk

INPUT_SCH := r1-rev1.1/echo-r1-rev1.1.kicad_sch
INPUT_PCB := r1-rev1.1/echo-r1-rev1.1.kicad_pcb
OUT_DIR   := r1-rev1.1/out

include mk/gerber.mk
include mk/schematic.mk

INPUT_SCH := r1-rev2/echo-r1-rev2.kicad_sch
INPUT_PCB := r1-rev2/echo-r1-rev2.kicad_pcb
OUT_DIR   := r1-rev2/out

include mk/schematic.mk
