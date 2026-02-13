OUT_KICAD_BOM := $(OUT_DIR)/work/kicad_bom.csv
OUT_KICAD_POS := $(OUT_DIR)/work/kicad_pos.csv
OUT_JLC_STAMP := $(OUT_DIR)/work/.jlc_stamp
OUT_JLC_BOM   := $(OUT_DIR)/jlc_pcba/jlc_bom.csv
OUT_JLC_CPL   := $(OUT_DIR)/jlc_pcba/jlc_cpl.csv

# All this escaping needed to get through both make and shell...
BOM_FIELDS := Reference Value Footprint
BOM_FIELDS += LCSC\#
BOM_FIELDS += \$$$${QUANTITY}
BOM_FIELDS += \$$$${DNP}

BOM_EXPORT_OPTIONS := --format-preset CSV
BOM_EXPORT_OPTIONS += --fields $(subst $(space),$(comma),$(BOM_FIELDS))

POS_EXPORT_OPTIONS := --format csv --units mm --side both

define rules :=

pcba: $(OUT_JLC_BOM) $(OUT_JLC_CPL)

$(OUT_KICAD_BOM): $(INPUT_SCH)
	kicad-cli sch export bom $(BOM_EXPORT_OPTIONS) --output $$@ $$<

$(OUT_KICAD_POS): $(INPUT_PCB)
	kicad-cli pcb export pos $(POS_EXPORT_OPTIONS) --output $$@ $$<

$(OUT_JLC_BOM) $(OUT_JLC_CPL): $(OUT_JLC_STAMP)
$(OUT_JLC_STAMP): $(OUT_KICAD_BOM) $(OUT_KICAD_POS) $(BOMTOOL_DEPS)
	mkdir -p $(dir $(OUT_JLC_BOM))
	$(BOMTOOL) --kicad-bom=$(OUT_KICAD_BOM) --kicad-pos=$(OUT_KICAD_POS) \
			   --output-jlc-bom=$(OUT_JLC_BOM) --output-jlc-cpl=$(OUT_JLC_CPL)
	touch $$@

clean: clean-$(OUT_KICAD_BOM)
clean-$(OUT_KICAD_BOM):
	rm -f $(OUT_KICAD_BOM) $(OUT_KICAD_POS)
	rm -f $(OUT_JLC_BOM) $(OUT_JLC_CPL)

endef

$(eval $(rules))
