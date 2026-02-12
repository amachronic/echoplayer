##
## Global make targets
##

all: gerbers
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

INPUT_PCB := r1-rev1/echo-r1-rev1.kicad_pcb
OUT_DIR   := r1-rev1/out

include mk/gerber.mk

INPUT_PCB := r1-rev1.1/echo-r1-rev1.1.kicad_pcb
OUT_DIR   := r1-rev1.1/out

include mk/gerber.mk
