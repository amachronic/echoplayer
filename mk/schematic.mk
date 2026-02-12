SCHEMATIC_OUT_PDF := $(OUT_DIR)/schematic.pdf

define rules :=

schematics: $(SCHEMATIC_OUT_PDF)

$(SCHEMATIC_OUT_PDF): $(INPUT_SCH)
	kicad-cli sch export pdf --output $$@ $$<

clean: clean-$(SCHEMATIC_OUT_PDF)
clean-$(SCHEMATIC_OUT_PDF):
	rm -f $(SCHEMATIC_OUT_PDF)

endef

$(eval $(rules))
