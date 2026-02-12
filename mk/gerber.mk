LAYERS := F.Cu In1.Cu In2.Cu In3.Cu In4.Cu B.Cu
LAYERS += F.Paste B.Paste
LAYERS += F.Silkscreen B.Silkscreen
LAYERS += F.Mask B.Mask
LAYERS += Edge.Cuts

GERBER_OPTIONS := --subtract-soldermask
GERBER_OPTIONS += -l $(subst $(space),$(comma),$(LAYERS))

DRILL_OPTIONS := --format excellon
DRILL_OPTIONS += --excellon-units mm
DRILL_OPTIONS += --excellon-oval-format alternate
DRILL_OPTIONS += --excellon-zeros-format decimal
DRILL_OPTIONS += --excellon-separate-th
DRILL_OPTIONS += --generate-map

PROJ_NAME := $(basename $(notdir $(INPUT_PCB)))

GERBER_DIR_NAME := $(PROJ_NAME)
GERBER_ZIP_NAME := $(PROJ_NAME).zip

GERBER_OUT_DIR := $(OUT_DIR)/$(GERBER_DIR_NAME)
GERBER_OUT_ZIP := $(OUT_DIR)/$(GERBER_ZIP_NAME)

define rules :=

gerbers: $(GERBER_OUT_ZIP)

$(GERBER_OUT_ZIP): $(INPUT_PCB)
	kicad-cli pcb export gerbers $(GERBER_OPTIONS) --output $(GERBER_OUT_DIR) $$<
	kicad-cli pcb export drill $(DRILL_OPTIONS) --output $(GERBER_OUT_DIR) $$<
	cd $(OUT_DIR) && zip $(GERBER_ZIP_NAME) -r $(GERBER_DIR_NAME)

clean: clean-$(GERBER_OUT_ZIP)
clean-$(GERBER_OUT_ZIP):
	rm -f $(GERBER_OUT_ZIP)
	rm -rf $(GERBER_OUT_DIR)

endef

$(eval $(rules))
