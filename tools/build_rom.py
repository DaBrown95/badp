"""Assemble the v1.5 scaffold, compare it, and retain source-change controls."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .identify_rom import inspect_rom
from .project import IDENTITY_PARTS, load_target
from .setup import verified_tools


ROOT = Path(__file__).resolve().parents[1]
TARGET = "us-v1.5"
PROOF_INPUTS = ("tools/build_rom.py", "tools/identify_rom.py", "tools/project.py",
                "tools/setup.py", "config/cc65-toolchain.json")

# Each mutation changes a meaningful instruction or structured data value.
# The marker must occur exactly once in the maintained source, even when its
# macro expands into two banks. Controls are built from isolated source copies.
MUTATIONS = {
    "boot": ("CONTROL_BOOT", "sei", "cli"),
    "reset_dispatch": ("CONTROL_STATE_DISPATCH", "cmp #$FF", "cmp #$FE"),
    "nmi_frame": ("CONTROL_FRAME_WORK", "ldx #$08", "ldx #$07"),
    "nmi_swap": ("CONTROL_SWAP_WORKSPACE", "$EC + slot", "$ED + slot"),
    "nmi_ppu": ("CONTROL_APPLY_PPU", "and #$E7", "and #$E6"),
    "slot_init": ("CONTROL_SLOT_INIT", "cpx #$28", "cpx #$27"),
    "enable_nmi": ("CONTROL_ENABLE_NMI", "ora #$80", "ora #$40"),
    "ppu_flush": ("CONTROL_PPU_FLUSH", "ldx #$00", "ldx #$01"),
    "oam_init": ("CONTROL_OAM_INIT", "ldy #$00", "ldy #$01"),
    "restore_bank": ("CONTROL_RESTORE_BANK", "lda $03C0", "ldx $03C0"),
    "record_fetch": ("CONTROL_RECORD_FETCH", "lda a:$54", "ldx a:$54"),
    "script_step": ("CONTROL_SCRIPT_STEP", "ldx #$00", "ldx #$01"),
    "script_dispatch": ("CONTROL_SCRIPT_DISPATCH", "ldy $60", "ldx $60"),
    "script_lengths": ("CONTROL_SCRIPT_LENGTHS", "2, $D70F", "3, $D70F"),
    "script_low": ("CONTROL_SCRIPT_LOW", "5, $D72C", "5, $D72D"),
    "script_high": ("CONTROL_SCRIPT_HIGH", "4, $D79B", "4, $D89B"),
    "script_op00": ("CONTROL_SCRIPT_OP00", "lda #$FF", "lda #$FE"),
    "script_op01": ("CONTROL_SCRIPT_OP01", "cmp #$A3", "cmp #$A2"),
    "script_op02": ("CONTROL_SCRIPT_OP02", "ldx #$00", "ldx #$01"),
    "script_op03": ("CONTROL_SCRIPT_OP03", "ldy #$02", "ldy #$03"),
    "script_jump": ("CONTROL_SCRIPT_JUMP", "lda $61", "lda $62"),
    "script_op05": ("CONTROL_SCRIPT_OP05", "cmp $1B", "cmp $1A"),
    "script_op06": ("CONTROL_SCRIPT_OP06", "cmp #$FF", "cmp #$FE"),
    "script_wait": ("CONTROL_SCRIPT_WAIT", "sta $0530,x", "sta $0520,x"),
    "script_op08": ("CONTROL_SCRIPT_OP08", "jsr UpdateSlotFieldsMode00", "jsr $F058"),
    "script_op09": ("CONTROL_SCRIPT_OP09", "lda #$10", "lda #$11"),
    "script_op0a": ("CONTROL_SCRIPT_OP0A", "cmp #$FF", "cmp #$FE"),
    "script_op0b": ("CONTROL_SCRIPT_OP0B", "sta $0640,x", "sta $0641,x"),
    "script_op0c": ("CONTROL_SCRIPT_OP0C", "sta $0670,x", "sta $0671,x"),
    "script_op0d": ("CONTROL_SCRIPT_OP0D", "lda #$FC", "lda #$FD"),
    "script_op0e": ("CONTROL_SCRIPT_OP0E", "lda #$CF", "lda #$CE"),
    "script_op0f": ("CONTROL_SCRIPT_OP0F", "sta $00", "sta $01"),
    "script_op10": ("CONTROL_SCRIPT_OP10", "and #$81", "and #$80"),
    "script_op11": ("CONTROL_SCRIPT_OP11", "lda $3E,y", "lda $40,y"),
    "script_op12": ("CONTROL_SCRIPT_OP12", "lda $40,y", "lda $41,y"),
    "script_op13": ("CONTROL_SCRIPT_OP13", "sta $3E,y", "sta $3F,y"),
    "script_op14": ("CONTROL_SCRIPT_OP14", "sta $40,y", "sta $41,y"),
    "script_op15": ("CONTROL_SCRIPT_OP15", "and $038D,y", "and $038E,y"),
    "script_op16": ("CONTROL_SCRIPT_OP16", "sta $FE", "sta $FD"),
    "script_fetch_pair": ("CONTROL_SCRIPT_FETCH_PAIR", "lda #$60", "lda #$61"),
    "script_op17": ("CONTROL_SCRIPT_OP17", "cmp #$FF", "cmp #$FE"),
    "script_op19": ("CONTROL_SCRIPT_OP19", "and #$07", "and #$06"),
    "script_slot_pointer": ("CONTROL_SCRIPT_SLOT_POINTER", "lda $05B0,x", "lda $05B1,x"),
    "script_op1a": ("CONTROL_SCRIPT_OP1A", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op1b": ("CONTROL_SCRIPT_OP1B", "cmp $0360,x", "cmp $0361,x"),
    "script_op1c": ("CONTROL_SCRIPT_OP1C", "lda $06D0,x", "lda $06D1,x"),
    "script_op1d": ("CONTROL_SCRIPT_OP1D", "cmp #$FF", "cmp #$FE"),
    "script_op1e": ("CONTROL_SCRIPT_OP1E", "jsr ScriptYield", "jsr ScriptYieldIfNonnegative"),
    "script_bitmasks": ("CONTROL_SCRIPT_BITMASKS", "1 << bit", "$80 >> bit"),
    "script_op1f": ("CONTROL_SCRIPT_OP1F", "jsr FindAvailableSlot", "jsr $D003"),
    "script_save_pointer": ("CONTROL_SCRIPT_SAVE_POINTER", "lda $53", "lda $54"),
    "script_op20": ("CONTROL_SCRIPT_OP20", "and #$10", "and #$20"),
    "script_op21": ("CONTROL_SCRIPT_OP21", "and #$07", "and #$06"),
    "script_op22": ("CONTROL_SCRIPT_OP22", "cmp $0520,x", "cmp $0521,x"),
    "script_op23": ("CONTROL_SCRIPT_OP23", "cmp $0760,x", "cmp $0761,x"),
    "script_op24": ("CONTROL_SCRIPT_OP24", "cmp $63", "cmp $62"),
    "script_op25": ("CONTROL_SCRIPT_OP25", "lda $0500,x", "lda $0501,x"),
    "script_op26": ("CONTROL_SCRIPT_OP26", "ora #$20", "ora #$10"),
    "script_op27": ("CONTROL_SCRIPT_OP27", "and #$08", "and #$04"),
    "script_op28": ("CONTROL_SCRIPT_OP28", "cpx $63", "cpx $62"),
    "script_op29": ("CONTROL_SCRIPT_OP29", "ldx $61", "ldx $62"),
    "script_op2a": ("CONTROL_SCRIPT_OP2A", "cmp $0770,x", "cmp $0771,x"),
    "script_op2b": ("CONTROL_SCRIPT_OP2B", "cmp $0780,x", "cmp $0781,x"),
    "script_op2c": ("CONTROL_SCRIPT_OP2C", "lda $61", "lda $62"),
    "script_op2d": ("CONTROL_SCRIPT_OP2D", "jsr UpdateSlotFieldsMode80", "jsr $F05D"),
    "script_op2e": ("CONTROL_SCRIPT_OP2E", "lda #$FF", "lda #$FE"),
    "script_op2f": ("CONTROL_SCRIPT_OP2F", "ora $61", "ora $62"),
    "script_op30": ("CONTROL_SCRIPT_OP30", "eor $61", "eor $62"),
    "script_op31": ("CONTROL_SCRIPT_OP31", "lda #$00", "lda #$01"),
    "script_op32": ("CONTROL_SCRIPT_OP32", "lda $61", "lda $62"),
    "script_op33": ("CONTROL_SCRIPT_OP33", "jsr SelectSlotFlagsOrAbort", "jsr $EBAD"),
    "script_op34": ("CONTROL_SCRIPT_OP34", "jsr SelectSlotFlagsOrAbort", "jsr $EBAD"),
    "script_op35": ("CONTROL_SCRIPT_OP35", "lda $63", "lda $62"),
    "script_op36": ("CONTROL_SCRIPT_OP36", "cmp #$FF", "cmp #$FE"),
    "script_op37": ("CONTROL_SCRIPT_OP37", "jsr SelectScriptField", "jsr $EB8C"),
    "script_op3b": ("CONTROL_SCRIPT_OP3B", "jsr SelectScriptField", "jsr $EB8C"),
    "script_op3c": ("CONTROL_SCRIPT_OP3C", "jsr SelectScriptField", "jsr $EB8C"),
    "script_op3d": ("CONTROL_SCRIPT_OP3D", "lda $07", "lda $08"),
    "script_op3e": ("CONTROL_SCRIPT_OP3E", "lda $61", "lda $62"),
    "script_op3f": ("CONTROL_SCRIPT_OP3F", "jsr ScriptClearSlotHigh", "jsr ScriptClearSlotHigh + 1"),
    "script_store_pair": ("CONTROL_SCRIPT_STORE_PAIR", "sta $70,x", "sta $71,x"),
    "script_copy_pair": ("CONTROL_SCRIPT_COPY_PAIR", "lda $0670,x", "lda $0671,x"),
    "script_compare_coords": ("CONTROL_SCRIPT_COMPARE_COORDS", "sty $03", "sty $04"),
    "script_read_indirect": ("CONTROL_SCRIPT_READ_INDIRECT", "jsr SlotRecordAddressFromCurrent", "jsr $F29C"),
    "script_coord_diff": ("CONTROL_SCRIPT_COORD_DIFF", "lda $FF", "lda $FE"),
    "script_marked_slots": ("CONTROL_SCRIPT_MARKED_SLOTS", "ldy #$00", "ldy #$01"),
    "script_unused_slots": ("CONTROL_SCRIPT_UNUSED_SLOTS", "ldy #$00", "ldy #$01"),
    "script_op40": ("CONTROL_SCRIPT_OP40", "and $70,x", "and $71,x"),
    "script_op41": ("CONTROL_SCRIPT_OP41", "lda $70,x", "lda $71,x"),
    "script_op42": ("CONTROL_SCRIPT_OP42", "adc $70,x", "adc $71,x"),
    "script_op43": ("CONTROL_SCRIPT_OP43", "eor #$FF", "eor #$FE"),
    "script_op44": ("CONTROL_SCRIPT_OP44", "lda $70,x", "lda $71,x"),
    "script_op45": ("CONTROL_SCRIPT_OP45", "cmp $07C0,x", "cmp $07C1,x"),
    "script_op46": ("CONTROL_SCRIPT_OP46", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op47": ("CONTROL_SCRIPT_OP47", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_value_array": ("CONTROL_SCRIPT_VALUE_ARRAY", "ldy $61", "ldy $62"),
    "script_op48": ("CONTROL_SCRIPT_OP48", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op49": ("CONTROL_SCRIPT_OP49", "cmp #$FF", "cmp #$FE"),
    "script_op50": ("CONTROL_SCRIPT_OP50", "lda $62", "lda $61"),
    "script_op4a": ("CONTROL_SCRIPT_OP4A", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op4b": ("CONTROL_SCRIPT_OP4B", "cmp $0370,x", "cmp $0371,x"),
    "script_op4c": ("CONTROL_SCRIPT_OP4C", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op4d": ("CONTROL_SCRIPT_OP4D", "ldx $61", "ldx $62"),
    "script_op4e": ("CONTROL_SCRIPT_OP4E", "ldx $61", "ldx $62"),
    "script_op4f": ("CONTROL_SCRIPT_OP4F", "lda $61", "lda $62"),
    "script_op51": ("CONTROL_SCRIPT_OP51", "cmp $0700,x", "cmp $0701,x"),
    "script_op52": ("CONTROL_SCRIPT_OP52", "cmp $B0,x", "cmp $B1,x"),
    "script_op53": ("CONTROL_SCRIPT_OP53", "cmp $70,x", "cmp $71,x"),
    "script_op54": ("CONTROL_SCRIPT_OP54", "jsr ScriptSaveSlotPointer", "jsr ScriptSaveSlotPointer + 1"),
    "script_op55": ("CONTROL_SCRIPT_OP55", "ora $61", "ora $62"),
    "script_op56": ("CONTROL_SCRIPT_OP56", "eor $61", "eor $62"),
    "script_op57": ("CONTROL_SCRIPT_OP57", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op59": ("CONTROL_SCRIPT_OP59", "jsr ScriptResolveOperand61", "jsr ScriptResolveOperand62"),
    "script_op5a": ("CONTROL_SCRIPT_OP5A", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op5b": ("CONTROL_SCRIPT_OP5B", "eor $70,x", "eor $71,x"),
    "script_op5c": ("CONTROL_SCRIPT_OP5C", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op5e": ("CONTROL_SCRIPT_OP5E", "jsr ScriptResolveOperand61", "jsr ScriptResolveOperand62"),
    "script_op5f": ("CONTROL_SCRIPT_OP5F", "and $D0,x", "and $D1,x"),
    "script_op60": ("CONTROL_SCRIPT_OP60", "and $D0,x", "and $D1,x"),
    "script_op61": ("CONTROL_SCRIPT_OP61", "jsr FindAvailableSlot", "jsr $D003"),
    "script_op62": ("CONTROL_SCRIPT_OP62", "lda $0660,x", "lda $0661,x"),
    "script_op63": ("CONTROL_SCRIPT_OP63", "lda $62", "lda $61"),
    "script_op64": ("CONTROL_SCRIPT_OP64", "eor #$FF", "eor #$FE"),
    "script_op65": ("CONTROL_SCRIPT_OP65", "lda $0750,x", "lda $0751,x"),
    "script_op66": ("CONTROL_SCRIPT_OP66", "lda $63", "lda $62"),
    "script_op67": ("CONTROL_SCRIPT_OP67", "jsr ScriptOp67FindAndSet", "jsr ScriptOp67FindAndSet + 1"),
    "script_op68": ("CONTROL_SCRIPT_OP68", "lda #$FF", "lda #$FE"),
    "script_op69": ("CONTROL_SCRIPT_OP69", "lda $62", "lda $61"),
    "script_op6a": ("CONTROL_SCRIPT_OP6A", "and #$BF", "and #$BE"),
    "script_op6b": ("CONTROL_SCRIPT_OP6B", "cmp #$FF", "cmp #$FE"),
    "script_op6c": ("CONTROL_SCRIPT_OP6C", "cmp #$FF", "cmp #$FE"),
    "script_op6d": ("CONTROL_SCRIPT_OP6D", "lda $E7", "lda $E8"),
    "script_op6f": ("CONTROL_SCRIPT_OP6F", "lda $E7", "lda $E8"),
    "script_op70": ("CONTROL_SCRIPT_OP70", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op72": ("CONTROL_SCRIPT_OP72", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op73": ("CONTROL_SCRIPT_OP73", "jsr SelectScriptField", "jsr $EB8C"),
    "script_op74": ("CONTROL_SCRIPT_OP74", "jmp ScriptWaitForState", "jmp ScriptWaitForState + 1"),
    "script_op75": ("CONTROL_SCRIPT_OP75", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op77": ("CONTROL_SCRIPT_OP77", "ldx $63", "ldx $64"),
    "script_op78": ("CONTROL_SCRIPT_OP78", "jsr ScriptFetchIndexedEight", "jsr ScriptFetchIndexedEight + 1"),
    "script_op79": ("CONTROL_SCRIPT_OP79", "stx $03", "stx $04"),
    "script_op7a": ("CONTROL_SCRIPT_OP7A", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op7b": ("CONTROL_SCRIPT_OP7B", "ldx $63", "ldx $64"),
    "script_op7c": ("CONTROL_SCRIPT_OP7C", "jsr ScriptResolveOperand61", "jsr ScriptResolveOperand62"),
    "script_op7e": ("CONTROL_SCRIPT_OP7E", "jsr ComputeSlotScaledPosition", "jsr $EF69"),
    "script_op7f": ("CONTROL_SCRIPT_OP7F", "lda $E7", "lda $E8"),
    "script_op80": ("CONTROL_SCRIPT_OP80", "lda $61", "lda $62"),
    "script_op81": ("CONTROL_SCRIPT_OP81", "jsr ScriptResolveOperand61", "jsr ScriptResolveOperand62"),
    "script_op82": ("CONTROL_SCRIPT_OP82", "cmp $70,x", "cmp $71,x"),
    "script_op83": ("CONTROL_SCRIPT_OP83", "lda $E7", "lda $E8"),
    "script_op84": ("CONTROL_SCRIPT_OP84", "jsr SelectSlotFlagsOrAbort", "jsr $EBAD"),
    "script_op85": ("CONTROL_SCRIPT_OP85", "lda $80,x", "lda $81,x"),
    "script_op86": ("CONTROL_SCRIPT_OP86", "jsr ScriptGetSelectedIndex", "jsr ScriptGetSelectedIndex + 1"),
    "script_op87": ("CONTROL_SCRIPT_OP87", "jsr ScriptGetSelectedIndex", "jsr ScriptGetSelectedIndex + 1"),
    "script_op88": ("CONTROL_SCRIPT_OP88", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op89_fetch": ("CONTROL_SCRIPT_OP89_FETCH", "jsr ScriptSaveSlotPointer", "jsr ScriptSaveSlotPointer + 1"),
    "script_op89_setup": ("CONTROL_SCRIPT_OP89_SETUP", "lda #$FF", "lda #$FE"),
    "script_op89_position": ("CONTROL_SCRIPT_OP89_POSITION", "lda $62", "lda $61"),
    "script_op89_shifts": ("CONTROL_SCRIPT_OP89_SHIFTS", "jmp ScriptOp89Setup", "jmp ScriptOp89Setup + 1"),
    "script_op89_relative": ("CONTROL_SCRIPT_OP89_RELATIVE", "lda $65", "lda $66"),
    "script_op18": ("CONTROL_SCRIPT_OP18", "lda #$04", "lda #$05"),
    "script_op8a": ("CONTROL_SCRIPT_OP8A", "lda $61", "lda $62"),
    "script_op8b": ("CONTROL_SCRIPT_OP8B", "lda $58", "lda $59"),
    "script_op8c": ("CONTROL_SCRIPT_OP8C", "lda #$00", "lda #$01"),
    "script_opb0": ("CONTROL_SCRIPT_OPB0", "jsr ScriptSetSlotFFFF", "jsr ScriptSetSlotFFFF + 1"),
    "script_op8d": ("CONTROL_SCRIPT_OP8D", "lda $70,x", "lda $71,x"),
    "script_op90": ("CONTROL_SCRIPT_OP90", "jsr ScriptSetIndirectOperand", "jsr ScriptSetIndirectOperand + 1"),
    "script_op91": ("CONTROL_SCRIPT_OP91", "jsr ScriptSetIndirectOperand", "jsr ScriptSetIndirectOperand + 1"),
    "script_indirect_operand": ("CONTROL_SCRIPT_INDIRECT_OPERAND", "lda $61", "lda $62"),
    "script_op92": ("CONTROL_SCRIPT_OP92", "jsr SelectSlotFlagsOrAbort", "jsr $EBAD"),
    "script_op93": ("CONTROL_SCRIPT_OP93", "cmp $0360,x", "cmp $0361,x"),
    "script_op94": ("CONTROL_SCRIPT_OP94", "lda $0700,x", "lda $0701,x"),
    "script_op95": ("CONTROL_SCRIPT_OP95", "ldx #$04", "ldx #$05"),
    "script_op96": ("CONTROL_SCRIPT_OP96", "lda $61", "lda $62"),
    "script_op97": ("CONTROL_SCRIPT_OP97", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_op98": ("CONTROL_SCRIPT_OP98", "lda $01", "lda $02"),
    "script_op99": ("CONTROL_SCRIPT_OP99", "lda #$FF", "lda #$FE"),
    "script_op9a": ("CONTROL_SCRIPT_OP9A", "jsr ScriptCompareState27", "jsr ScriptCompareState27 + 1"),
    "script_op9b": ("CONTROL_SCRIPT_OP9B", "jmp $FD88", "jmp $FD89"),
    "script_op9c": ("CONTROL_SCRIPT_OP9C", "eor #$FF", "eor #$FE"),
    "script_op9d": ("CONTROL_SCRIPT_OP9D", "rts", "rti"),
    "script_op9e": ("CONTROL_SCRIPT_OP9E", "lda $0700,x", "lda $0701,x"),
    "script_op9f": ("CONTROL_SCRIPT_OP9F", "jsr ScriptGetSecondOffset", "jsr ScriptGetSecondOffset + 1"),
    "script_opa0": ("CONTROL_SCRIPT_OPA0", "jsr ScriptGetSecondOffset", "jsr ScriptGetSecondOffset + 1"),
    "script_opa1": ("CONTROL_SCRIPT_OPA1", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_opa2": ("CONTROL_SCRIPT_OPA2", "ldy $06D0,x", "ldy $06D1,x"),
    "script_opa4": ("CONTROL_SCRIPT_OPA4", "and #$FB", "and #$FA"),
    "script_opa5": ("CONTROL_SCRIPT_OPA5", "lda $0580,x", "lda $0581,x"),
    "script_opa6": ("CONTROL_SCRIPT_OPA6", "lda $62", "lda $61"),
    "script_opa7": ("CONTROL_SCRIPT_OPA7", "lda $0580,x", "lda $0581,x"),
    "script_slot_ffff": ("CONTROL_SCRIPT_SLOT_FFFF", "lda #$FF", "lda #$FE"),
    "script_opa8": ("CONTROL_SCRIPT_OPA8", "lda $70,x", "lda $71,x"),
    "script_opa9": ("CONTROL_SCRIPT_OPA9", "lda $61", "lda $62"),
    "script_opaa": ("CONTROL_SCRIPT_OPAA", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_opab": ("CONTROL_SCRIPT_OPAB", "ldy $60", "ldy $61"),
    "script_opac": ("CONTROL_SCRIPT_OPAC", "ldy $80,x", "ldy $81,x"),
    "script_opad": ("CONTROL_SCRIPT_OPAD", "ldy $80,x", "ldy $81,x"),
    "script_opae": ("CONTROL_SCRIPT_OPAE", "lda $61", "lda $62"),
    "script_opaf": ("CONTROL_SCRIPT_OPAF", "jsr ScriptClearSlotHigh", "jsr ScriptClearSlotHigh + 1"),
    "script_opb1": ("CONTROL_SCRIPT_OPB1", "lda #$00", "lda #$01"),
    "script_opb2": ("CONTROL_SCRIPT_OPB2", "and #$BF", "and #$BE"),
    "script_opb3": ("CONTROL_SCRIPT_OPB3", "jsr ScriptSaveSlotPointer", "jsr ScriptSaveSlotPointer + 1"),
    "script_opb4": ("CONTROL_SCRIPT_OPB4", "jsr CalculateSlotCoordinate", "jsr $D0B4"),
    "script_opb6": ("CONTROL_SCRIPT_OPB6", "jsr ScriptOp67FindAndSet", "jsr ScriptOp67FindAndSet + 1"),
    "script_opb7": ("CONTROL_SCRIPT_OPB7", "lda $06D0,x", "lda $06D1,x"),
    "script_opb8": ("CONTROL_SCRIPT_OPB8", "lda $0710,x", "lda $0711,x"),
    "script_opb9": ("CONTROL_SCRIPT_OPB9", "lda $61", "lda $62"),
    "script_opba": ("CONTROL_SCRIPT_OPBA", "lda $61", "lda $62"),
    "script_opbb": ("CONTROL_SCRIPT_OPBB", "and #$10", "and #$20"),
    "script_opbc": ("CONTROL_SCRIPT_OPBC", "lda $62", "lda $61"),
    "script_related_depth": ("CONTROL_SCRIPT_RELATED_DEPTH", "sta $11", "sta $12"),
    "script_opbd": ("CONTROL_SCRIPT_OPBD", "lda $61", "lda $62"),
    "script_opbe": ("CONTROL_SCRIPT_OPBE", "ora #$20", "ora #$10"),
    "script_opc0": ("CONTROL_SCRIPT_OPC0", "ora $70,x", "ora $71,x"),
    "script_opc1": ("CONTROL_SCRIPT_OPC1", "jsr ScriptSelectValueArray", "jsr ScriptSelectValueArray + 1"),
    "script_opc2": ("CONTROL_SCRIPT_OPC2", "and #$02", "and #$04"),
    "script_opc3": ("CONTROL_SCRIPT_OPC3", "jsr RefreshSlotRecordPosition", "jsr $CD94"),
    "script_opc4": ("CONTROL_SCRIPT_OPC4", "lda $10", "lda $11"),
    "script_mark_other": ("CONTROL_SCRIPT_MARK_OTHER", "lda $10", "lda $11"),
    "script_prepare_loop": ("CONTROL_SCRIPT_PREPARE_LOOP", "jsr ScriptLoadSlotPointer", "jsr ScriptLoadSlotPointer + 1"),
    "script_pending": ("CONTROL_SCRIPT_PENDING", "lda $04F0,x", "lda $04F1,x"),
    "script_loop_wait": ("CONTROL_SCRIPT_LOOP_WAIT", "lda $0530,x", "lda $0531,x"),
    "script_advance_twice": ("CONTROL_SCRIPT_ADVANCE_TWICE", "jsr AdvanceScriptPointerOnce", "jsr AdvanceScriptPointerOnce + 1"),
    "mul_unsigned8": ("CONTROL_MUL_UNSIGNED8", "sty $03E2", "sty $03E3"),
    "div_unsigned16_8": ("CONTROL_DIV_UNSIGNED16_8", "sta $03E4", "sta $03E5"),
    "add_a_to_xy": ("CONTROL_ADD_A_TO_XY", "stx $03E2", "stx $03E3"),
    "negate_a": ("CONTROL_NEGATE_A", "eor #$FF", "eor #$FE"),
    "shift_left4": ("CONTROL_SHIFT_LEFT4", "asl a", "lsr a"),
    "shift_left3": ("CONTROL_SHIFT_LEFT3", "asl a", "lsr a"),
    "shift_right4": ("CONTROL_SHIFT_RIGHT4", "lsr a", "asl a"),
    "shift_right3": ("CONTROL_SHIFT_RIGHT3", "lsr a", "asl a"),
    "select_script_field": ("CONTROL_SELECT_SCRIPT_FIELD", "lda $61", "lda $62"),
    "select_flags_abort": ("CONTROL_SELECT_FLAGS_ABORT", "pha", "php"),
    "test_slot_offset": ("CONTROL_TEST_SLOT_OFFSET", "jsr ClampSlotOffsets", "jsr ClampSlotOffsets + 1"),
    "clamp_slot_offsets": ("CONTROL_CLAMP_SLOT_OFFSETS", "stx $03A6", "stx $03A7"),
    "slot_midpoint": ("CONTROL_SLOT_MIDPOINT", "lda $0570,x", "lda $0571,x"),
    "slot_bounds": ("CONTROL_SLOT_BOUNDS", "ldx $10", "ldx $11"),
    "slot_fields_00": ("CONTROL_SLOT_FIELDS_00", "lda #$00", "lda #$01"),
    "slot_fields_80": ("CONTROL_SLOT_FIELDS_80", "lda #$80", "lda #$81"),
    "slot_fields_c0": ("CONTROL_SLOT_FIELDS_C0", "lda #$C0", "lda #$C1"),
    "slot_fields_40": ("CONTROL_SLOT_FIELDS_40", "lda #$40", "lda #$41"),
    "slot_fields_common": ("CONTROL_SLOT_FIELDS_COMMON", "sta $05", "sta $06"),
    "slot_direction_flags": ("CONTROL_SLOT_DIRECTION_FLAGS", "lda #$00", "lda #$01"),
    "find_slot_coordinates": ("CONTROL_FIND_SLOT_COORDINATES", "lda $0680,x", "lda $0681,x"),
    "init_state_19": ("CONTROL_INIT_STATE_19", "lda #$FD", "lda #$FC"),
    "advance_state_19": ("CONTROL_ADVANCE_STATE_19", "lda $19", "lda $1A"),
    "apply_slot_offset": ("CONTROL_APPLY_SLOT_OFFSET", "jsr TestSlotOffset", "jsr TestSlotOffset + 1"),
    "slot_record_entry": ("CONTROL_SLOT_RECORD_ENTRY", "pha", "php"),
    "slot_record_lookup": ("CONTROL_SLOT_RECORD_LOOKUP", "ldy #$00", "ldy #$01"),
    "slot_record_fetch": ("CONTROL_SLOT_RECORD_FETCH", "lda $53", "lda $54"),
    "slot_record_fields": ("CONTROL_SLOT_RECORD_FIELDS", "ldy #$04", "ldy #$05"),
    "slot_record_size": ("CONTROL_SLOT_RECORD_SIZE", "ldy #$00", "ldy #$01"),
    "slot_record_allocate": ("CONTROL_SLOT_RECORD_ALLOCATE", "lda $04E0,x", "lda $04E1,x"),
    "slot_record_place": ("CONTROL_SLOT_RECORD_PLACE", "ldx $10", "ldx $11"),
    "slot_record_flags": ("CONTROL_SLOT_RECORD_FLAGS", "lda $11", "lda $12"),
    "slot_record_current": ("CONTROL_SLOT_RECORD_CURRENT", "ldx $10", "ldx $11"),
    "slot_record_address": ("CONTROL_SLOT_RECORD_ADDRESS", "sta $FE", "sta $FD"),
    "double_fe_pointer": ("CONTROL_DOUBLE_FE_POINTER", "asl $FE", "lsr $FE"),
    "slot_update_entry": ("CONTROL_SLOT_UPDATE_ENTRY", "lda $00", "lda $01"),
    "slot_update_first": ("CONTROL_SLOT_UPDATE_FIRST", "lda #$FF", "lda #$FE"),
    "slot_update_second": ("CONTROL_SLOT_UPDATE_SECOND", "lda $0750,x", "lda $0751,x"),
    "slot_update_limits": ("CONTROL_SLOT_UPDATE_LIMITS", "lda $C0,x", "lda $C1,x"),
    "slot_scaled_position": ("CONTROL_SLOT_SCALED_POSITION", "jsr CalculateSlotCoordinate", "jsr $D0B4"),
    "slot_position_shift": ("CONTROL_SLOT_POSITION_SHIFT", "lsr $12", "asl $12"),
    "slot_flag02": ("CONTROL_SLOT_FLAG02", "lda $0620,x", "lda $0621,x"),
    "slot_flag01": ("CONTROL_SLOT_FLAG01", "lda $0620,x", "lda $0621,x"),
    "linked_slot_position": ("CONTROL_LINKED_SLOT_POSITION", "ldx $10", "ldx $11"),
    "transform_slot_signed": ("CONTROL_TRANSFORM_SLOT_SIGNED", "sta $12", "sta $11"),
    "track_slot_position": ("CONTROL_TRACK_SLOT_POSITION", "ldx $10", "ldx $11"),
    "slot_direction_bits": ("CONTROL_SLOT_DIRECTION_BITS", "ldx $10", "ldx $11"),
    "sync_slot_direction": ("CONTROL_SYNC_SLOT_DIRECTION", "ldx $10", "ldx $11"),
    "unlinked_vertical": ("CONTROL_UNLINKED_VERTICAL", "lda $0510,x", "lda $0511,x"),
    "unlinked_split_vertical": ("CONTROL_UNLINKED_SPLIT_VERTICAL", "lda $04", "lda $05"),
    "unlinked_move_setup": ("CONTROL_UNLINKED_MOVE_SETUP", "ldx $10", "ldx $11"),
    "unlinked_horizontal": ("CONTROL_UNLINKED_HORIZONTAL", "ldx $05", "ldx $06"),
    "unlinked_vertical_attempt": ("CONTROL_UNLINKED_VERTICAL_ATTEMPT", "ldy $06", "ldy $05"),
    "store_record_field_0a": ("CONTROL_STORE_RECORD_FIELD_0A", "jsr SlotRecordOffset", "jsr SlotRecordOffset + 1"),
    "get_record_field_06": ("CONTROL_GET_RECORD_FIELD_06", "jsr RequireSlotRecord", "jsr RequireSlotRecord + 1"),
    "require_slot_record": ("CONTROL_REQUIRE_SLOT_RECORD", "jsr SlotRecordOffset", "jsr SlotRecordOffset + 1"),
    "slot_record_offset": ("CONTROL_SLOT_RECORD_OFFSET", "cmp #$10", "cmp #$0F"),
    "slot_query_entry": ("CONTROL_SLOT_QUERY_ENTRY", "stx $03A6", "stx $03A7"),
    "slot_query_prepare": ("CONTROL_SLOT_QUERY_PREPARE", "lda $03A6", "lda $03A7"),
    "slot_query_coordinates": ("CONTROL_SLOT_QUERY_COORDINATES", "lda ($FE),y", "lda ($FD),y"),
    "slot_query_span": ("CONTROL_SLOT_QUERY_SPAN", "lda $039E", "lda $039F"),
    "slot_query_stack": ("CONTROL_SLOT_QUERY_STACK", "tsx", "txa"),
    "slot_query_address": ("CONTROL_SLOT_QUERY_ADDRESS", "lda $039C", "lda $039D"),
    "slot_query_compare": ("CONTROL_SLOT_QUERY_COMPARE", "lda $0100,x", "lda $0101,x"),
    "read_map_byte": ("CONTROL_READ_MAP_BYTE", "lda $03A6", "lda $03A7"),
    "clear_slot_records": ("CONTROL_CLEAR_SLOT_RECORDS", "lda #$00", "lda #$01"),
    "read_banked_pointer": ("CONTROL_READ_BANKED_POINTER", "lda $03E0", "lda $03E1"),
    "resolve_map_chunk": ("CONTROL_RESOLVE_MAP_CHUNK", "lda $039A", "lda $039B"),
    "load_map_chunk_pointer": ("CONTROL_LOAD_MAP_CHUNK_POINTER", "lda $FE", "lda $FF"),
    "slot_descriptor": ("CONTROL_SLOT_DESCRIPTOR", "$716D, $00, $00, $00, $00", "$716D, $01, $00, $00, $00"),
    "initialize_slot_entry": ("CONTROL_INITIALIZE_SLOT_ENTRY", "ldx $10", "ldx $11"),
    "initialize_slot_defaults": ("CONTROL_INITIALIZE_SLOT_DEFAULTS", "lda #$00", "lda #$01"),
    "initialize_slot_descriptor": ("CONTROL_INITIALIZE_SLOT_DESCRIPTOR", "lda $2A", "lda $2B"),
    "initialize_slot_unavailable": ("CONTROL_INITIALIZE_SLOT_UNAVAILABLE", "ldx $10", "ldx $11"),
    "require_matching_slot_flag": ("CONTROL_REQUIRE_MATCHING_SLOT_FLAG", "jsr FindMatchingSlot", "jsr FindMatchingSlot + 1"),
    "find_matching_slot": ("CONTROL_FIND_MATCHING_SLOT", "ldy #$0F", "ldy #$0E"),
    "slot_related_address": ("CONTROL_SLOT_RELATED_ADDRESS", "$A302", "$A303"),
    "find_available_slot": ("CONTROL_FIND_AVAILABLE_SLOT", "ldy #$FF", "ldy #$FE"),
    "slot_distance_reference": ("CONTROL_SLOT_DISTANCE_REFERENCE", "lda $07D0,x", "lda $07D1,x"),
    "slot_position_event": ("CONTROL_SLOT_POSITION_EVENT", "lda $07D0,x", "lda $07D1,x"),
    "calculate_slot_coordinate": ("CONTROL_CALCULATE_SLOT_COORDINATE", "lda $B0,x", "lda $B1,x"),
    "rotate_slot_coordinate": ("CONTROL_ROTATE_SLOT_COORDINATE", "ror a", "asl a"),
    "release_current_slot": ("CONTROL_RELEASE_CURRENT_SLOT", "ldx $10", "ldx $11"),
    "release_slot_by_index": ("CONTROL_RELEASE_SLOT_BY_INDEX", "lda #$FF", "lda #$FE"),
    "release_selected_slots": ("CONTROL_RELEASE_SELECTED_SLOTS", "ldy #$00", "ldy #$01"),
    "find_slot_flag04": ("CONTROL_FIND_SLOT_FLAG04", "ldy #$00", "ldy #$01"),
    "update_current_slot": ("CONTROL_UPDATE_CURRENT_SLOT", "ldx $10", "ldx $11"),
    "slot_update_position": ("CONTROL_SLOT_UPDATE_POSITION", "lda $0620,x", "lda $0621,x"),
    "slot_update_contact": ("CONTROL_SLOT_UPDATE_CONTACT", "lda $0690,x", "lda $0691,x"),
    "slot_contact_bounds": ("CONTROL_SLOT_CONTACT_BOUNDS", "lda $06A0,x", "lda $06A1,x"),
    "slot_contact_scan": ("CONTROL_SLOT_CONTACT_SCAN", "jsr ScriptCheckOtherSlot", "jsr ScriptCheckOtherSlot + 1"),
    "position_record_search": ("CONTROL_POSITION_RECORD_SEARCH", "ldy #$03", "ldy #$04"),
    "convert_slot_position": ("CONTROL_CONVERT_SLOT_POSITION", "jsr ScalePositionByEight", "jsr ScalePositionByEight + 1"),
    "scale_position_by_eight": ("CONTROL_SCALE_POSITION_BY_EIGHT", "jsr ShiftPositionLeft", "jsr ShiftPositionLeft + 1"),
    "update_position_reference": ("CONTROL_UPDATE_POSITION_REFERENCE", "lda $03EE", "lda $03EF"),
    "shift_a4f_right": ("CONTROL_SHIFT_A4F_RIGHT", "lsr a", "asl a"),
    "shift_reference_right": ("CONTROL_SHIFT_REFERENCE_RIGHT", "lsr $0F", "asl $0F"),
    "banks_from_state": ("CONTROL_BANKS_FROM_STATE", "ldx $01", "ldx $02"),
    "banks_from_value": ("CONTROL_BANKS_FROM_VALUE", "pha", "php"),
    "select_both_pointers": ("CONTROL_SELECT_BOTH_POINTERS", "jsr SelectFirstRelatedPointer", "jsr SelectFirstRelatedPointer + 1"),
    "select_second_pointer": ("CONTROL_SELECT_SECOND_POINTER", "ldx $02", "ldx $03"),
    "apply_second_pointer": ("CONTROL_APPLY_SECOND_POINTER", "jsr ScriptCompareState27", "jsr ScriptCompareState27 + 1"),
    "select_first_pointer": ("CONTROL_SELECT_FIRST_POINTER", "ldx $02", "ldx $03"),
    "apply_first_pointer": ("CONTROL_APPLY_FIRST_POINTER", "jsr ScriptCompareState27", "jsr ScriptCompareState27 + 1"),
    "clear_two_ppu_ranges": ("CONTROL_CLEAR_TWO_PPU_RANGES", "jsr $85C0", "jsr $85C1"),
    "fill_ppu_range": ("CONTROL_FILL_PPU_RANGE", "ldx #$00", "ldx #$01"),
    "update_game_frame": ("CONTROL_UPDATE_GAME_FRAME", "lda $28", "lda $29"),
    "refresh_all_slot_records": ("CONTROL_REFRESH_ALL_SLOT_RECORDS", "ldx #$00", "ldx #$01"),
    "refresh_slot_record_position": ("CONTROL_REFRESH_SLOT_RECORD_POSITION", "lda $04E0,x", "lda $04E1,x"),
    "update_slot_draw_positions": ("CONTROL_UPDATE_SLOT_DRAW_POSITIONS", "ldx #$00", "ldx #$01"),
    "compute_bank_selection": ("CONTROL_COMPUTE_BANK_SELECTION", "tay", "tax"),
    "update_frame_position_bases": ("CONTROL_UPDATE_FRAME_POSITION_BASES", "lda $36", "lda $37"),
    "update_frame_second_base": ("CONTROL_UPDATE_FRAME_SECOND_BASE", "lda #$00", "lda #$01"),
    "scan_position_window": ("CONTROL_SCAN_POSITION_WINDOW", "lda #$00", "lda #$01"),
    "process_position_record": ("CONTROL_PROCESS_POSITION_RECORD", "jsr LookupPositionRecordsA", "jsr LookupPositionRecordsA + 1"),
    "create_position_slot": ("CONTROL_CREATE_POSITION_SLOT", "jsr RequireMatchingSlotFlag", "jsr RequireMatchingSlotFlag + 1"),
    "position_pointers_a": ("CONTROL_POSITION_POINTERS_A", "$A444", "$A445"),
    "position_pointers_b": ("CONTROL_POSITION_POINTERS_B", "$A444", "$A445"),
    "initialize_position_streams": ("CONTROL_INITIALIZE_POSITION_STREAMS", "ldx $02", "ldx $03"),
    "translate_slot_position": ("CONTROL_TRANSLATE_SLOT_POSITION", "cpx #$FF", "cpx #$FE"),
    "scale_world_coordinate": ("CONTROL_SCALE_WORLD_COORDINATE", "clc", "sec"),
    "scale_world_shift": ("CONTROL_SCALE_WORLD_SHIFT", "lsr a", "asl a"),
    "place_slot_sprites": ("CONTROL_PLACE_SLOT_SPRITES", "stx $03E0", "stx $03E1"),
    "place_slot_size": ("CONTROL_PLACE_SLOT_SIZE", "lda $03E1", "lda $03E0"),
    "place_slot_rows": ("CONTROL_PLACE_SLOT_ROWS", "lda $FE", "lda $FF"),
    "place_slot_evaluate": ("CONTROL_PLACE_SLOT_EVALUATE", "lda $0400,x", "lda $0401,x"),
    "place_slot_divide": ("CONTROL_PLACE_SLOT_DIVIDE", "stx $03E1", "stx $03E0"),
    "release_sprite_record": ("CONTROL_RELEASE_SPRITE_RECORD", "cmp #$FF", "cmp #$FE"),
    "update_sprite_attribute20": ("CONTROL_UPDATE_SPRITE_ATTRIBUTE20", "stx $FE", "stx $FD"),
    "set_sprite_record_mode": ("CONTROL_SET_SPRITE_RECORD_MODE", "stx $03E0", "stx $03E1"),
    "set_sprite_query_value": ("CONTROL_SET_SPRITE_QUERY_VALUE", "stx $03E0", "stx $03E1"),
    "set_sprite_bit40": ("CONTROL_SET_SPRITE_BIT40", "stx $03E0", "stx $03E1"),
    "set_sprite_bit80": ("CONTROL_SET_SPRITE_BIT80", "stx $03E0", "stx $03E1"),
    "set_sprite_record_bit10": ("CONTROL_SET_SPRITE_RECORD_BIT10", "jsr RequireSlotRecord", "jsr RequireSlotRecord + 1"),
    "update_audio_voices": ("CONTROL_UPDATE_AUDIO_VOICES", "tsx", "txa"),
    "audio_read_command": ("CONTROL_AUDIO_READ_COMMAND", "lda $04B4,x", "lda $04B5,x"),
    "audio_finish_note": ("CONTROL_AUDIO_FINISH_NOTE", "jsr AdvanceAudioCommandOne", "jsr AdvanceAudioCommandOne + 1"),
    "audio_high_command": ("CONTROL_AUDIO_HIGH_COMMAND", "cmp #$A0", "cmp #$A1"),
    "horizontal_scroll": ("CONTROL_HORIZONTAL_SCROLL", "lda $03EB", "lda $03EC"),
    "horizontal_scroll_below": ("CONTROL_HORIZONTAL_SCROLL_BELOW", "cmp #$FF", "cmp #$FE"),
    "horizontal_scroll_snap": ("CONTROL_HORIZONTAL_SCROLL_SNAP", "lda $03EE", "lda $03EF"),
    "horizontal_scroll_negative": ("CONTROL_HORIZONTAL_SCROLL_NEGATIVE", "jsr PpuQueueRemaining", "jsr PpuQueueRemaining + 1"),
    "horizontal_scroll_positive": ("CONTROL_HORIZONTAL_SCROLL_POSITIVE", "jsr PpuQueueRemaining", "jsr PpuQueueRemaining + 1"),
    "vertical_scroll": ("CONTROL_VERTICAL_SCROLL", "lda $03EB", "lda $03EC"),
    "vertical_scroll_below": ("CONTROL_VERTICAL_SCROLL_BELOW", "cmp #$FF", "cmp #$FE"),
    "vertical_scroll_snap": ("CONTROL_VERTICAL_SCROLL_SNAP", "lda $03F0", "lda $03F1"),
    "vertical_scroll_negative": ("CONTROL_VERTICAL_SCROLL_NEGATIVE", "jsr PpuQueueRemaining", "jsr PpuQueueRemaining + 1"),
    "vertical_scroll_positive": ("CONTROL_VERTICAL_SCROLL_POSITIVE", "jsr PpuQueueRemaining", "jsr PpuQueueRemaining + 1"),
    "queue_scroll_row": ("CONTROL_QUEUE_SCROLL_ROW", "jsr ScrollXTileCoordinate", "jsr ScrollXTileCoordinate + 1"),
    "update_ppu_scroll_mirror": ("CONTROL_UPDATE_PPU_SCROLL_MIRROR", "lda $03A4", "lda $03A5"),
    "queue_map_tile_row": ("CONTROL_QUEUE_MAP_TILE_ROW", "lda $EC", "lda $ED"),
    "map_tile_row_nametable": ("CONTROL_MAP_TILE_ROW_NAMETABLE", "stx $03D7", "stx $03D6"),
    "map_tile_row_width": ("CONTROL_MAP_TILE_ROW_WIDTH", "lda $03DD", "lda $03DC"),
    "map_tile_row_first_length": ("CONTROL_MAP_TILE_ROW_FIRST_LENGTH", "sta $03DC", "sta $03DD"),
    "map_tile_row_queue": ("CONTROL_MAP_TILE_ROW_QUEUE", "lda #$00", "lda #$01"),
    "map_tile_row_consume_span": ("CONTROL_MAP_TILE_ROW_CONSUME_SPAN", "sta $03D0", "sta $03D1"),
    "map_tile_row_second": ("CONTROL_MAP_TILE_ROW_SECOND", "lda $03DD", "lda $03DC"),
    "map_queue_second_nametable": ("CONTROL_MAP_QUEUE_SECOND_NAMETABLE", "sta $03DC", "sta $03DD"),
    "map_queue_store_end": ("CONTROL_MAP_QUEUE_STORE_END", "stx $0380", "stx $0381"),
    "map_chunk_row_pointer": ("CONTROL_MAP_CHUNK_ROW_POINTER", "lda $039C", "lda $039D"),
    "map_chunk_attribute_row_pointer": ("CONTROL_MAP_CHUNK_ATTRIBUTE_ROW_POINTER", "lda $039C", "lda $039D"),
    "map_chunk_column_pointer": ("CONTROL_MAP_CHUNK_COLUMN_POINTER", "lda $039A", "lda $039B"),
    "map_chunk_offset_pointer": ("CONTROL_MAP_CHUNK_OFFSET_POINTER", "pha", "php"),
    "map_chunk_attribute_pointer": ("CONTROL_MAP_CHUNK_ATTRIBUTE_POINTER", "lda $039A", "lda $039B"),
    "advance_map_chunk": ("CONTROL_ADVANCE_MAP_CHUNK", "lda $EC", "lda $ED"),
    "retreat_map_chunk": ("CONTROL_RETREAT_MAP_CHUNK", "lda $EC", "lda $ED"),
    "ppu_queue_remaining": ("CONTROL_PPU_QUEUE_REMAINING", "lda #$60", "lda #$61"),
    "clamp_scroll_targets": ("CONTROL_CLAMP_SCROLL_TARGETS", "lda $03A2", "lda $03A3"),
    "scroll_x_tile_coordinate": ("CONTROL_SCROLL_X_TILE_COORDINATE", "ldx $03F3", "ldx $03F4"),
    "scroll_y_tile_coordinate": ("CONTROL_SCROLL_Y_TILE_COORDINATE", "ldx $03F5", "ldx $03F6"),
    "shift_xy_left3": ("CONTROL_SHIFT_XY_LEFT3", "jsr ShiftXYLeft1", "jsr ShiftXYLeft1 + 1"),
    "update_scroll_work": ("CONTROL_UPDATE_SCROLL_WORK", "lda $03EB", "lda $03EC"),
    "update_palette_streams": ("CONTROL_UPDATE_PALETTE_STREAMS", "lda $0387", "lda $0388"),
    "palette_sprite_setup": ("CONTROL_PALETTE_SPRITE_SETUP", "lda $0387", "lda $0388"),
    "palette_advance_background": ("CONTROL_PALETTE_ADVANCE_BACKGROUND", "lda $0382", "lda $0383"),
    "palette_advance_sprite": ("CONTROL_PALETTE_ADVANCE_SPRITE", "lda $0388", "lda $0389"),
    "start_audio_voice": ("CONTROL_START_AUDIO_VOICE", "stx $FE", "stx $FD"),
    "start_audio_voice_check": ("CONTROL_START_AUDIO_VOICE_CHECK", "lda $04B0,x", "lda $04B1,x"),
    "start_audio_voice_initialize": ("CONTROL_START_AUDIO_VOICE_INITIALIZE", "lda #$01", "lda #$02"),
    "stop_audio_voice": ("CONTROL_STOP_AUDIO_VOICE", "cmp #$FF", "cmp #$FE"),
    "stop_audio_voice_by_index": ("CONTROL_STOP_AUDIO_VOICE_BY_INDEX", "jsr AudioVoiceOffset", "jsr AudioVoiceOffset + 1"),
    "stop_audio_voice_offset": ("CONTROL_STOP_AUDIO_VOICE_OFFSET", "lda $04B0,x", "lda $04B1,x"),
    "stop_audio_owned_voice": ("CONTROL_STOP_AUDIO_OWNED_VOICE", "jsr RestartAudioVoiceChannel", "jsr RestartAudioVoiceChannel + 1"),
    "stop_audio_find_shadow": ("CONTROL_STOP_AUDIO_FIND_SHADOW", "txa", "tya"),
    "is_audio_voice_active": ("CONTROL_IS_AUDIO_VOICE_ACTIVE", "jsr AudioVoiceOffset", "jsr AudioVoiceOffset + 1"),
    "audio_loop_command": ("CONTROL_AUDIO_LOOP_COMMAND", "lda $0100,y", "lda $0101,y"),
    "audio_command_mask_set": ("CONTROL_AUDIO_COMMAND_MASK_SET", "cmp #$C2", "cmp #$C1"),
    "audio_command_mask_clear": ("CONTROL_AUDIO_COMMAND_MASK_CLEAR", "cmp #$C3", "cmp #$C1"),
    "audio_command_dispatch": ("CONTROL_AUDIO_COMMAND_DISPATCH", "lda $0100,y", "lda $0101,y"),
    "audio_command_restore_pointer": ("CONTROL_AUDIO_COMMAND_RESTORE_POINTER", "cmp #$08", "cmp #$07"),
    "audio_command_stop_voice": ("CONTROL_AUDIO_COMMAND_STOP_VOICE", "cmp #$0C", "cmp #$0B"),
    "audio_command_write_register": ("CONTROL_AUDIO_COMMAND_WRITE_REGISTER", "cmp #$10", "cmp #$0F"),
    "audio_command_restart_channel": ("CONTROL_AUDIO_COMMAND_RESTART_CHANNEL", "cmp #$14", "cmp #$13"),
    "audio_command_enable_channel": ("CONTROL_AUDIO_COMMAND_ENABLE_CHANNEL", "cmp #$18", "cmp #$17"),
    "audio_command_select_all": ("CONTROL_AUDIO_COMMAND_SELECT_ALL", "cmp #$18", "cmp #$17"),
    "audio_command_write_five": ("CONTROL_AUDIO_COMMAND_WRITE_FIVE", "cmp #$19", "cmp #$1A"),
    "audio_command_delay": ("CONTROL_AUDIO_COMMAND_DELAY", "cmp #$1B", "cmp #$1A"),
    "enable_audio_voice_channel": ("CONTROL_ENABLE_AUDIO_VOICE_CHANNEL", "jsr AudioVoiceChannelMask", "jsr AudioVoiceChannelMask + 1"),
    "restart_audio_voice_channel": ("CONTROL_RESTART_AUDIO_VOICE_CHANNEL", "jsr AudioVoiceChannelMask", "jsr AudioVoiceChannelMask + 1"),
    "audio_voice_channel_mask": ("CONTROL_AUDIO_VOICE_CHANNEL_MASK", "lda $04B0,x", "lda $04B1,x"),
    "audio_offset_channel_mask": ("CONTROL_AUDIO_OFFSET_CHANNEL_MASK", "lsr a", "asl a"),
    "audio_channel_bits": ("CONTROL_AUDIO_CHANNEL_BITS", "$01, $02", "$03, $02"),
    "audio_all_tone_channels": ("CONTROL_AUDIO_ALL_TONE_CHANNELS", "lda #$0F", "lda #$0E"),
    "audio_note_timing": ("CONTROL_AUDIO_NOTE_TIMING", "$08, $01", "$09, $01"),
    "prepare_audio_note": ("CONTROL_PREPARE_AUDIO_NOTE", "jsr ShiftARight4", "jsr ShiftARight4 + 1"),
    "audio_voice_register_address": ("CONTROL_AUDIO_VOICE_REGISTER_ADDRESS", "lda $04B0,x", "lda $04B1,x"),
    "write_audio_voice_period": ("CONTROL_WRITE_AUDIO_VOICE_PERIOD", "jsr AudioVoiceFlags", "jsr AudioVoiceFlags + 1"),
    "advance_audio_command_two": ("CONTROL_ADVANCE_AUDIO_COMMAND_TWO", "jsr AdvanceAudioCommandOne", "jsr AdvanceAudioCommandOne + 1"),
    "advance_audio_command_one": ("CONTROL_ADVANCE_AUDIO_COMMAND_ONE", "inc $04B4,x", "inc $04B5,x"),
    "audio_voice_flags": ("CONTROL_AUDIO_VOICE_FLAGS", "lda $04B0,x", "lda $04B1,x"),
    "write_audio_voice_instrument": ("CONTROL_WRITE_AUDIO_VOICE_INSTRUMENT", "lda $04B6,x", "lda $04B7,x"),
    "audio_voice_offset": ("CONTROL_AUDIO_VOICE_OFFSET", "cmp #$05", "cmp #$04"),
    "advance_sprite_animations": ("CONTROL_ADVANCE_SPRITE_ANIMATIONS", "ldx #$00", "ldx #$01"),
    "advance_sprite_animation_active": ("CONTROL_ADVANCE_SPRITE_ANIMATION_ACTIVE", "tya", "txa"),
    "advance_sprite_animation_frame": ("CONTROL_ADVANCE_SPRITE_ANIMATION_FRAME", "lda $0408,x", "lda $0409,x"),
    "load_sprite_frame": ("CONTROL_LOAD_SPRITE_FRAME", "txa", "tya"),
    "sprite_frame_forward": ("CONTROL_SPRITE_FRAME_FORWARD", "lda #$04", "lda #$08"),
    "sprite_frame_horizontal": ("CONTROL_SPRITE_FRAME_HORIZONTAL", "lda #$FC", "lda #$F8"),
    "sprite_frame_vertical": ("CONTROL_SPRITE_FRAME_VERTICAL", "and #$40", "and #$20"),
    "sprite_frame_both": ("CONTROL_SPRITE_FRAME_BOTH", "lda #$FC", "lda #$F8"),
    "sprite_frame_row": ("CONTROL_SPRITE_FRAME_ROW", "lda $03E2", "lda $03E3"),
    "stack_copy": ("CONTROL_STACK_COPY", "tsx", "txa"),
    "stride_copy": ("CONTROL_STRIDE_COPY", "adc $03D1", "sbc $03D1"),
    "pair_copy": ("CONTROL_PAIR_COPY", "ldy #$02", "ldy #$03"),
    "linear_copy": ("CONTROL_LINEAR_COPY", "adc #$01", "adc #$02"),
    "bit_copy": ("CONTROL_BIT_COPY", "ror a", "asl a"),
    "wait": ("CONTROL_WAIT", "lda PPUSTATUS", "ldx PPUSTATUS"),
    "switch": ("CONTROL_SWITCH", "sta BankValues,y", "sta BankValues,x"),
    "table": ("CONTROL_TABLE", "$0C |", "$08 |"),
    "nmi": ("CONTROL_NMI", "ldy NmiSavedIndex", "ldx NmiSavedIndex"),
    "reset": ("CONTROL_RESET", "#$FF", "#$FE"),
    "vectors": ("CONTROL_VECTORS", "NmiHandler, ResetEntry, IrqHandler",
                "ResetEntry, ResetEntry, IrqHandler"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_regions(config: dict, prg_offset: int) -> list[dict]:
    """Validate each physical ownership span and calculate its file offset."""
    bank_size, cpu_base, count = config["bank_size"], config["cpu_base"], config["bank_count"]
    if (bank_size, cpu_base, count) != (0x8000, 0x8000, 2):
        raise ValueError("unexpected v1.5 physical bank layout")
    output = []
    for entry in config["regions"]:
        bank, cpu, size = entry["bank"], int(entry["cpu"], 0), entry["size"]
        if (bank not in range(count) or size <= 0 or cpu < cpu_base
                or cpu + size > cpu_base + bank_size or entry["kind"] not in ("code", "data")
                or entry["control"] not in MUTATIONS):
            raise ValueError(f"invalid source region: {entry}")
        output.append({**entry, "file_offset": prg_offset + bank * bank_size + cpu - cpu_base})
    if len({entry["id"] for entry in output}) != len(output):
        raise ValueError("duplicate source region id")
    if {entry["control"] for entry in output} != set(MUTATIONS):
        raise ValueError("each source-change control must own at least one region")
    for bank in range(count):
        end = cpu_base
        for entry in sorted((r for r in output if r["bank"] == bank), key=lambda r: int(r["cpu"], 0)):
            start = int(entry["cpu"], 0)
            if start < end:
                raise ValueError(f"overlapping source regions in bank {bank}")
            end = start + entry["size"]
    return output


def extract_gaps(prg: bytes, chr_data: bytes, regions: list[dict], inputs: Path) -> list[dict]:
    """Extract only the complement of claimed source spans into ignored files."""
    if len(prg) != 0x10000 or len(chr_data) != 0x10000:
        raise ValueError("unexpected v1.5 PRG/CHR sizes")
    inputs.mkdir(parents=True)
    gaps = []
    for bank in range(2):
        start = 0x8000
        spans = sorted((r for r in regions if r["bank"] == bank), key=lambda r: int(r["cpu"], 0))
        for region in [*spans, {"cpu": "0x10000", "size": 0}]:
            end = int(region["cpu"], 0)
            if end > start:
                name = f"bank{bank}_{start:04x}_{end:04x}.bin"
                offset = bank * 0x8000 + start - 0x8000
                payload = prg[offset:offset + end - start]
                (inputs / name).write_bytes(payload)
                gaps.append({"name": name, "bank": bank, "cpu_start": f"0x{start:04x}",
                             "size": len(payload), "sha256": digest(payload)})
            start = end + region["size"]
    (inputs / "chr.bin").write_bytes(chr_data)
    return gaps


def mutate_source(source: str, control: str) -> str:
    marker, old, new = MUTATIONS[control]
    lines = source.splitlines(keepends=True)
    indexes = [i for i, line in enumerate(lines) if line.partition(";")[2].strip() == marker]
    if len(indexes) != 1 or lines[indexes[0]].count(old) != 1:
        raise ValueError(f"control {control}: expected one marked, mutable source line")
    lines[indexes[0]] = lines[indexes[0]].replace(old, new, 1)
    return "".join(lines)


def verify_control(reference: bytes, candidate: bytes, regions: list[dict], control: str) -> list[int]:
    if len(candidate) != len(reference):
        raise ValueError(f"control {control}: output size changed")
    changed = {index for index, (a, b) in enumerate(zip(reference, candidate)) if a != b}
    selected = [entry for entry in regions if entry["control"] == control]
    allowed = set()
    for entry in selected:
        offsets = set(range(entry["file_offset"], entry["file_offset"] + entry["size"]))
        if not changed.intersection(offsets):
            raise ValueError(f"control {control}: no change in {entry['id']}")
        allowed.update(offsets)
    if not changed or changed - allowed:
        raise ValueError(f"control {control}: no difference or differences outside its source regions")
    return sorted(changed)


def assemble(work: Path, tools: dict[str, Path], source: Path, prefix: Path) -> Path:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        str(tools["ca65"]), "-g", "-I", "source", "--bin-include-dir", "inputs",
        "-l", str(prefix.with_suffix(".lst")), "-o", str(prefix.with_suffix(".o")), str(source),
    ], cwd=work, check=True)
    result = prefix.with_suffix(".nes")
    subprocess.run([
        str(tools["ld65"]), "-C", "source/link.cfg", "-m", str(prefix.with_suffix(".map")),
        "--dbgfile", str(prefix.with_suffix(".dbg")), "-o", str(result), str(prefix.with_suffix(".o")),
    ], cwd=work, check=True)
    return work / result


def build() -> dict:
    if os.environ.get("BADP_TARGET") not in (None, "", TARGET):
        raise ValueError("only us-v1.5 has a ROM build; select TARGET=us-v1.5")
    tool_paths = verified_tools()
    target = load_target(ROOT, TARGET)
    input_path = ROOT / (os.environ.get("BADP_ROM") or target["input_path"])
    reference = input_path.read_bytes()
    parsed = inspect_rom(reference)
    mismatch = [part for part in IDENTITY_PARTS if parsed[part] != target["reference"][part]]
    if mismatch:
        raise ValueError(f"reference input does not match {TARGET}: {', '.join(mismatch)}")
    source_map = (ROOT / "config/source-us-v1.5.json").read_bytes()
    config = json.loads(source_map)
    if config["target"] != TARGET:
        raise ValueError("source map target differs from build target")
    regions = source_regions(config, parsed["prg"]["offset"])
    source = (ROOT / config["source"]).read_text()
    include = (ROOT / "include/nes.inc").read_bytes()
    linker = (ROOT / config["linker_config"]).read_bytes()
    prg = reference[parsed["prg"]["offset"]:parsed["prg"]["offset"] + parsed["prg"]["size"]]
    chr_data = reference[parsed["chr"]["offset"]:parsed["chr"]["offset"] + parsed["chr"]["size"]]
    base = ROOT / "build"
    base.mkdir(exist_ok=True)
    final = base / TARGET
    if final.is_symlink():
        raise ValueError("refusing to replace a symlinked build directory")
    with tempfile.TemporaryDirectory(prefix=f".{TARGET}-", dir=base) as temporary:
        temp = Path(temporary)
        work = temp / "proof"
        (work / "source").mkdir(parents=True)
        (work / "source/rom.s").write_text(source)
        (work / "source/nes.inc").write_bytes(include)
        (work / "source/link.cfg").write_bytes(linker)
        gaps = extract_gaps(prg, chr_data, regions, work / "inputs")
        output_path = assemble(work, tool_paths, Path("source/rom.s"), Path("bible-adventures"))
        output = output_path.read_bytes()
        if output != reference:
            first = next((i for i, (a, b) in enumerate(zip(output, reference)) if a != b), None)
            raise ValueError(f"assembled ROM differs from reference (first byte {first}; "
                             f"sizes {len(output)} / {len(reference)})")
        output_parts = inspect_rom(output)
        component_matches = {part: output_parts[part] == parsed[part] for part in IDENTITY_PARTS}
        if not all(component_matches.values()):
            raise ValueError("assembled ROM components differ from the reference")
        controls = []
        for control in MUTATIONS:
            changed_source = mutate_source(source, control)
            control_dir = work / "controls" / control
            control_dir.mkdir(parents=True)
            (control_dir / "rom.s").write_text(changed_source)
            control_rom = assemble(work, tool_paths, Path("controls") / control / "rom.s",
                                   Path("controls") / control / "candidate")
            candidate = control_rom.read_bytes()
            changed = verify_control(reference, candidate, regions, control)
            controls.append({"control": control, "changed_offsets": changed,
                             "affected_regions": [r["id"] for r in regions if r["control"] == control],
                             "source_sha256": digest(changed_source.encode()),
                             "candidate_sha256": digest(candidate)})
        counts = {kind: sum(r["size"] for r in regions if r["kind"] == kind)
                  for kind in ("code", "data")}
        pin = json.loads((ROOT / "config/cc65-toolchain.json").read_text())
        proof = {
            "schema_version": 1, "target": TARGET, "match": True,
            "reference_sha256": parsed["file"]["sha256"], "output_sha256": digest(output),
            "component_matches": component_matches,
            "toolchain_revision": pin["revision"], "source_sha256": digest(source.encode()),
            "include_sha256": digest(include), "linker_config_sha256": digest(linker),
            "source_map_sha256": digest(source_map),
            "target_manifest_sha256": digest((ROOT / "config/targets/us-v1.5.json").read_bytes()),
            "catalogue_sha256": digest((ROOT / "config/catalogues/no-intro-nes.json").read_bytes()),
            "tool_sha256": {name: digest(path.read_bytes()) for name, path in tool_paths.items()},
            "verification_input_sha256": {name: digest((ROOT / name).read_bytes()) for name in PROOF_INPUTS},
            "source_regions": regions, "local_prg_gaps": gaps,
            "counts": {"matching_code_bytes": counts["code"], "structured_data_bytes": counts["data"],
                       "local_prg_bytes": sum(g["size"] for g in gaps),
                       "local_chr_bytes": len(chr_data), "container_header_bytes": 16},
            "controls": controls,
        }
        (work / "proof.json").write_text(json.dumps(proof, indent=2) + "\n")
        previous = temp / "previous"
        if final.exists():
            final.rename(previous)
        try:
            work.rename(final)
        except OSError:
            if previous.exists():
                previous.rename(final)
            raise
    return proof


def main() -> int:
    try:
        proof = build()
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"ROM build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"target": TARGET, "match": proof["match"],
                      "output": f"build/{TARGET}/bible-adventures.nes",
                      "proof": f"build/{TARGET}/proof.json",
                      "counts": proof["counts"], "controls_passed": len(proof["controls"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
