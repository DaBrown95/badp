PYTHON ?= python3
TARGET ?=
ROM ?=
export BADP_TARGET = $(TARGET)
export BADP_ROM = $(ROM)
.DEFAULT_GOAL := help

.PHONY: help setup setup-mesen targets identify audit audit-all build progress verify-gameplay position-records script-entries script-flow slot-record-flow direct-record-flow packed-text trace-audio audio-inventory trace-sprites sprite-inventory test
help:
	@echo 'make targets   Show the primary target and sequential target order'
	@echo 'make identify  Inspect a ROM (default: primary target; override TARGET=id or ROM=path)'
	@echo 'make audit     Verify a local input against its pinned identity (override TARGET=id)'
	@echo 'make audit-all Verify every configured input ROM identity'
	@echo 'make setup     Download and build the pinned local cc65 tools'
	@echo 'make setup-mesen  Install the pinned local macOS ARM64 emulator'
	@echo 'make build     Assemble and verify v1.5, including source-change controls'
	@echo 'make progress  Rebuild and refresh the verified per-version README tracker'
	@echo 'make verify-gameplay  Compare v1.5 opening gameplay in MesenCE'
	@echo 'make position-records  Decode v1.5 position records to local analysis'
	@echo 'make script-entries  Inventory v1.5 script entry candidates locally'
	@echo 'make script-flow     Trace reviewed v1.5 script control flow locally'
	@echo 'make slot-record-flow  Trace candidate v1.5 slot-record accesses locally'
	@echo 'make direct-record-flow  Check direct record targets and script overlaps'
	@echo 'make packed-text     Decode v1.5 packed text to local analysis'
	@echo 'make trace-audio     Capture v1.5 audio reads locally in MesenCE'
	@echo 'make audio-inventory Validate and decode the local audio trace'
	@echo 'make trace-sprites   Capture v1.5 sprite entries locally in MesenCE'
	@echo 'make sprite-inventory Validate and decode the local sprite trace'
	@echo 'make test      Test the tools without a game ROM'

setup:
	$(PYTHON) -m tools.setup

setup-mesen:
	$(PYTHON) -m tools.setup_mesen

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

verify-gameplay:
	$(PYTHON) -m tools.mesen_runtime

position-records:
	$(PYTHON) -m tools.position_records

script-entries:
	$(PYTHON) -m tools.script_entries

script-flow:
	$(PYTHON) -m tools.script_flow

slot-record-flow:
	$(PYTHON) -m tools.slot_record_flow

direct-record-flow:
	$(PYTHON) -m tools.direct_record_flow

packed-text:
	$(PYTHON) -m tools.packed_text

trace-audio:
	$(PYTHON) -m tools.trace_audio

audio-inventory:
	$(PYTHON) -m tools.audio_commands

trace-sprites:
	$(PYTHON) -m tools.trace_sprites

sprite-inventory:
	$(PYTHON) -m tools.sprite_metadata

test:
	$(PYTHON) -m unittest discover -s tests -v
