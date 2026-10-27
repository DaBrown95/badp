PYTHON ?= python3
ROM ?= baseroms/bible-adventures.nes
export BADP_ROM = $(ROM)
.DEFAULT_GOAL := help

.PHONY: help identify test
help:
	@echo 'make identify  Inspect and hash a local NES ROM (override ROM=path)'
	@echo 'make test      Test the tools without a game ROM'
	@echo 'ROM reconstruction and make build are not implemented yet.'

identify:
	$(PYTHON) tools/identify_rom.py

test:
	$(PYTHON) -m unittest discover -s tests -v
