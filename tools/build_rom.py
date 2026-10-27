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
    "script_op08": ("CONTROL_SCRIPT_OP08", "jsr $F057", "jsr $F058"),
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
    "script_op1f": ("CONTROL_SCRIPT_OP1F", "jsr $D002", "jsr $D003"),
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
    "script_op2d": ("CONTROL_SCRIPT_OP2D", "jsr $F05C", "jsr $F05D"),
    "script_op2e": ("CONTROL_SCRIPT_OP2E", "lda #$FF", "lda #$FE"),
    "script_op2f": ("CONTROL_SCRIPT_OP2F", "ora $61", "ora $62"),
    "script_op30": ("CONTROL_SCRIPT_OP30", "eor $61", "eor $62"),
    "script_op31": ("CONTROL_SCRIPT_OP31", "lda #$00", "lda #$01"),
    "script_op32": ("CONTROL_SCRIPT_OP32", "lda $61", "lda $62"),
    "script_op33": ("CONTROL_SCRIPT_OP33", "jsr $EBAC", "jsr $EBAD"),
    "script_op34": ("CONTROL_SCRIPT_OP34", "jsr $EBAC", "jsr $EBAD"),
    "script_op35": ("CONTROL_SCRIPT_OP35", "lda $63", "lda $62"),
    "script_op36": ("CONTROL_SCRIPT_OP36", "cmp #$FF", "cmp #$FE"),
    "script_op37": ("CONTROL_SCRIPT_OP37", "jsr $EB8B", "jsr $EB8C"),
    "script_op3b": ("CONTROL_SCRIPT_OP3B", "jsr $EB8B", "jsr $EB8C"),
    "script_op3c": ("CONTROL_SCRIPT_OP3C", "jsr $EB8B", "jsr $EB8C"),
    "script_op3d": ("CONTROL_SCRIPT_OP3D", "lda $07", "lda $08"),
    "script_op3e": ("CONTROL_SCRIPT_OP3E", "lda $61", "lda $62"),
    "script_op3f": ("CONTROL_SCRIPT_OP3F", "jsr ScriptClearSlotHigh", "jsr ScriptClearSlotHigh + 1"),
    "script_store_pair": ("CONTROL_SCRIPT_STORE_PAIR", "sta $70,x", "sta $71,x"),
    "script_copy_pair": ("CONTROL_SCRIPT_COPY_PAIR", "lda $0670,x", "lda $0671,x"),
    "script_compare_coords": ("CONTROL_SCRIPT_COMPARE_COORDS", "sty $03", "sty $04"),
    "script_read_indirect": ("CONTROL_SCRIPT_READ_INDIRECT", "jsr $F29B", "jsr $F29C"),
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
    "script_op61": ("CONTROL_SCRIPT_OP61", "jsr $D002", "jsr $D003"),
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
    "script_op73": ("CONTROL_SCRIPT_OP73", "jsr $EB8B", "jsr $EB8C"),
    "script_op74": ("CONTROL_SCRIPT_OP74", "jmp ScriptWaitForState", "jmp ScriptWaitForState + 1"),
    "script_op75": ("CONTROL_SCRIPT_OP75", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op77": ("CONTROL_SCRIPT_OP77", "ldx $63", "ldx $64"),
    "script_op78": ("CONTROL_SCRIPT_OP78", "jsr ScriptFetchIndexedEight", "jsr ScriptFetchIndexedEight + 1"),
    "script_op79": ("CONTROL_SCRIPT_OP79", "stx $03", "stx $04"),
    "script_op7a": ("CONTROL_SCRIPT_OP7A", "jsr ScriptOperand61OrSlot", "jsr ScriptOperand62OrSlot"),
    "script_op7b": ("CONTROL_SCRIPT_OP7B", "ldx $63", "ldx $64"),
    "script_op7c": ("CONTROL_SCRIPT_OP7C", "jsr ScriptResolveOperand61", "jsr ScriptResolveOperand62"),
    "script_op7e": ("CONTROL_SCRIPT_OP7E", "jsr $EF68", "jsr $EF69"),
    "script_op7f": ("CONTROL_SCRIPT_OP7F", "lda $E7", "lda $E8"),
    "script_op80": ("CONTROL_SCRIPT_OP80", "lda $61", "lda $62"),
    "script_op81": ("CONTROL_SCRIPT_OP81", "jsr ScriptResolveOperand61", "jsr ScriptResolveOperand62"),
    "script_op82": ("CONTROL_SCRIPT_OP82", "cmp $70,x", "cmp $71,x"),
    "script_op83": ("CONTROL_SCRIPT_OP83", "lda $E7", "lda $E8"),
    "script_op84": ("CONTROL_SCRIPT_OP84", "jsr $EBAC", "jsr $EBAD"),
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
    "script_op92": ("CONTROL_SCRIPT_OP92", "jsr $EBAC", "jsr $EBAD"),
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
    "script_opb4": ("CONTROL_SCRIPT_OPB4", "jsr $D0B3", "jsr $D0B4"),
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
    "script_opc3": ("CONTROL_SCRIPT_OPC3", "jsr $CD93", "jsr $CD94"),
    "script_opc4": ("CONTROL_SCRIPT_OPC4", "lda $10", "lda $11"),
    "script_mark_other": ("CONTROL_SCRIPT_MARK_OTHER", "lda $10", "lda $11"),
    "script_prepare_loop": ("CONTROL_SCRIPT_PREPARE_LOOP", "jsr ScriptLoadSlotPointer", "jsr ScriptLoadSlotPointer + 1"),
    "script_pending": ("CONTROL_SCRIPT_PENDING", "lda $04F0,x", "lda $04F1,x"),
    "script_loop_wait": ("CONTROL_SCRIPT_LOOP_WAIT", "lda $0530,x", "lda $0531,x"),
    "script_advance_twice": ("CONTROL_SCRIPT_ADVANCE_TWICE", "jsr AdvanceScriptPointerOnce", "jsr AdvanceScriptPointerOnce + 1"),
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
