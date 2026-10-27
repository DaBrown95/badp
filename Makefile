PYTHON ?= python3
TARGET ?=
ROM ?=
export BADP_TARGET = $(TARGET)
export BADP_ROM = $(ROM)
.DEFAULT_GOAL := help

.PHONY: help setup targets identify audit audit-all build progress position-records script-entries test
help:
	@echo 'make targets   Show the primary target and sequential target order'
	@echo 'make identify  Inspect a ROM (default: primary target; override TARGET=id or ROM=path)'
	@echo 'make audit     Verify a local input against its pinned identity (override TARGET=id)'
	@echo 'make audit-all Verify every configured input ROM identity'
	@echo 'make setup     Download and build the pinned local cc65 tools'
	@echo 'make build     Assemble and verify v1.5, including source-change controls'
	@echo 'make progress  Rebuild and refresh the verified per-version README tracker'
	@echo 'make position-records  Decode v1.5 position records to local analysis'
	@echo 'make script-entries  Inventory v1.5 script entry candidates locally'
	@echo 'make test      Test the tools without a game ROM'

setup:
	$(PYTHON) -m tools.setup

targets:
	$(PYTHON) -m tools.project targets

identify:
	$(PYTHON) -m tools.project identify

audit:
	$(PYTHON) -m tools.project audit

audit-all:
	$(PYTHON) -m tools.project audit --all

build:
	$(PYTHON) -m tools.build_rom

progress: build
	$(PYTHON) -m tools.progress

position-records:
	$(PYTHON) -m tools.position_records

script-entries:
	$(PYTHON) -m tools.script_entries

test:
	$(PYTHON) -m unittest discover -s tests -v
