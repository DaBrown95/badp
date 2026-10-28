PYTHON ?= python3
TARGET ?=
ROM ?=
export BADP_TARGET = $(TARGET)
export BADP_ROM = $(ROM)
.DEFAULT_GOAL := help

.PHONY: help setup setup-mesen targets identify audit audit-all build progress verify-gameplay verify-controller verify-audio-bank verify-record-boundary verify-script-overlap indexed-jump-inventory native-control-flow native-script-calls position-records script-entries script-flow slot-record-flow contact-record-flow native-event-flow direct-record-flow packed-text ppu-streams trace-audio trace-audio-route audio-inventory audio-flow trace-sprites sprite-inventory map-data trace-map extract-map-chunks extract-map-layouts extract-packed-text prg-inventory trace-runtime-extents runtime-extents test
help:
	@echo 'make targets   Show the primary target and sequential target order'
	@echo 'make identify  Inspect a ROM (default: primary target; override TARGET=id or ROM=path)'
	@echo 'make audit     Verify a local input against its pinned identity (override TARGET=id)'
	@echo 'make audit-all Verify every configured input ROM identity'
	@echo 'make setup     Download and build the pinned local cc65 tools'
	@echo 'make setup-mesen  Install the pinned local macOS ARM64 emulator'
	@echo 'make build     Assemble and verify v1.5, including source-change controls'
	@echo 'make progress  Rebuild and refresh the verified per-version README tracker'
	@echo 'make verify-gameplay  Compare v1.5 opening gameplay and inventory in MesenCE'
	@echo 'make verify-controller Check v1.5 controller bit order and transitions'
	@echo 'make verify-audio-bank Check audio selector and mapper behavior in MesenCE'
	@echo 'make verify-record-boundary Check record fetch wrapping in MesenCE'
	@echo 'make verify-script-overlap Check a controlled ambiguous record path'
	@echo 'make indexed-jump-inventory Check the $$F434 index and local table candidates'
	@echo 'make native-control-flow  Inventory reconstructed native transfers locally'
	@echo 'make native-script-calls  Inventory candidate BOGUS native-call targets'
	@echo 'make position-records  Decode v1.5 position records to local analysis'
	@echo 'make script-entries  Inventory v1.5 script entry candidates locally'
	@echo 'make script-flow     Trace reviewed v1.5 script control flow locally'
	@echo 'make slot-record-flow  Trace candidate v1.5 slot-record accesses locally'
	@echo 'make contact-record-flow  Trace possible v1.5 contact-event records locally'
	@echo 'make native-event-flow  Trace candidate native event contexts locally'
	@echo 'make direct-record-flow  Check direct record targets and script overlaps'
	@echo 'make packed-text     Decode v1.5 packed text to local analysis'
	@echo 'make ppu-streams    Inventory candidate PPU command streams locally'
	@echo 'make trace-audio     Capture v1.5 audio reads locally in MesenCE'
	@echo 'make trace-audio-route Compare audio reads on the maintained Moses route'
	@echo 'make audio-inventory Validate and decode the local audio trace'
	@echo 'make audio-flow      Trace candidate audio-command paths locally'
	@echo 'make trace-sprites   Capture v1.5 sprite entries locally in MesenCE'
	@echo 'make sprite-inventory Validate and decode the local sprite trace'
	@echo 'make map-data        Decode v1.5 map layouts and chunks locally'
	@echo 'make extract-map-chunks  Export editable v1.5 map chunks locally'
	@echo 'make extract-map-layouts Export editable v1.5 map grids locally'
	@echo 'make extract-packed-text Export editable v1.5 messages locally'
	@echo 'make trace-map       Check mapped map fetches in MesenCE'
	@echo 'make prg-inventory   Combine source and local PRG-use evidence'
	@echo 'make trace-runtime-extents  Capture sampled Moses interpreter and record accesses'
	@echo 'make runtime-extents  Check sampled command and record bytes against source'
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

verify-controller:
	$(PYTHON) -m tools.verify_controller

verify-audio-bank:
	$(PYTHON) -m tools.verify_audio_bank

verify-record-boundary:
	$(PYTHON) -m tools.verify_record_boundary

verify-script-overlap:
	$(PYTHON) -m tools.verify_script_overlap

indexed-jump-inventory:
	$(PYTHON) -m tools.indexed_jump_inventory

native-control-flow:
	$(PYTHON) -m tools.native_control_flow

native-script-calls:
	$(PYTHON) -m tools.native_script_calls

position-records:
	$(PYTHON) -m tools.position_records

script-entries:
	$(PYTHON) -m tools.script_entries

script-flow:
	$(PYTHON) -m tools.script_flow

slot-record-flow:
	$(PYTHON) -m tools.slot_record_flow

contact-record-flow:
	$(PYTHON) -m tools.contact_record_flow

native-event-flow:
	$(PYTHON) -m tools.native_event_flow

direct-record-flow:
	$(PYTHON) -m tools.direct_record_flow

packed-text:
	$(PYTHON) -m tools.packed_text

ppu-streams:
	$(PYTHON) -m tools.ppu_streams

trace-audio:
	$(PYTHON) -m tools.trace_audio

trace-audio-route:
	$(PYTHON) -m tools.trace_audio_route

audio-inventory:
	$(PYTHON) -m tools.audio_commands

audio-flow:
	$(PYTHON) -m tools.audio_flow

trace-sprites:
	$(PYTHON) -m tools.trace_sprites

sprite-inventory:
	$(PYTHON) -m tools.sprite_metadata

map-data:
	$(PYTHON) -m tools.map_data

extract-map-chunks:
	$(PYTHON) -m tools.map_assets

extract-map-layouts:
	$(PYTHON) -m tools.map_layout_assets

extract-packed-text:
	$(PYTHON) -m tools.text_assets

trace-map:
	$(PYTHON) -m tools.trace_map

prg-inventory:
	$(PYTHON) -m tools.prg_inventory

trace-runtime-extents:
	$(PYTHON) -m tools.trace_runtime_extents

runtime-extents:
	$(PYTHON) -m tools.runtime_extents

test:
	$(PYTHON) -m unittest discover -s tests -v
