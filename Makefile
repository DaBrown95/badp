PYTHON ?= python3
TARGET ?=
ROM ?=
export BADP_TARGET = $(TARGET)
export BADP_ROM = $(ROM)
.DEFAULT_GOAL := help

.PHONY: help targets identify audit audit-all test
help:
	@echo 'make targets   Show the primary target and sequential target order'
	@echo 'make identify  Inspect a ROM (default: primary target; override TARGET=id or ROM=path)'
	@echo 'make audit     Verify a local input against its pinned identity (override TARGET=id)'
	@echo 'make audit-all Verify every configured input ROM identity'
	@echo 'make test      Test the tools without a game ROM'
	@echo 'ROM reconstruction and make build are not implemented yet.'

targets:
	$(PYTHON) -m tools.project targets

identify:
	$(PYTHON) -m tools.project identify

audit:
	$(PYTHON) -m tools.project audit

audit-all:
	$(PYTHON) -m tools.project audit --all

test:
	$(PYTHON) -m unittest discover -s tests -v
