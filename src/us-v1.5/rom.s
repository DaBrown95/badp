.setcpu "6502"
.include "nes.inc"

; A position record stores a 15-bit sorted key and a range flag, followed by
; a selector/type and five parameters interpreted by the consuming path.
; The search routine reads four-byte $FFFF/$0000 stream terminators.
.macro PositionRecord key, rangeFlag, recordType, p0, p1, p2, p3, p4
    .word key | rangeFlag
    .byte recordType, p0, p1, p2, p3, p4
.endmacro

.macro PositionRecordEnd
    .word $FFFF, $0000
.endmacro

; Two position-record search paths share control flow while using different
; zero-page pointer pairs and linked addresses. Both scan eight-byte records against
; $5E/$5F and copy bytes 3-7 to $2A-$2E when a nonzero entry is found.
.macro PositionRecordSearch pointerLo, pointerHi, searchEntry
    .local copyReturn, searchBackward, searchForward, found, previous, notFound
    .local returnValue, stepBack, stepForward, compare, compareFlags, compareReturn
    .local compareDirect, compareDirectReturn, compareRange, compareRangeReturn
    jsr searchEntry
    beq copyReturn
    ldy #$03                     ; CONTROL_POSITION_RECORD_SEARCH
    lda (pointerLo),y
    sta $2A
    iny
    lda (pointerLo),y
    sta $2B
    iny
    lda (pointerLo),y
    sta $2C
    iny
    lda (pointerLo),y
    sta $2D
    iny
    lda (pointerLo),y
    sta $2E
    lda $29
copyReturn:
    rts
searchEntry:
    jsr compare
    beq found
    bcs searchForward
searchBackward:
    jsr stepBack
    jsr compare
    beq found
    bcc searchBackward
    jmp notFound
searchForward:
    jsr stepForward
    jsr compare
    beq found
    bcs searchForward
    jmp notFound
found:
    ldy #$02
    lda (pointerLo),y
    sta $29
    bne returnValue
    lda $5E
    ora $5F
    bne previous
    jsr stepForward
    jsr compare
    beq found
    jmp notFound
previous:
    jsr stepBack
notFound:
    lda #$00
    sta $29
    rts
returnValue:
    lda $29
    rts
stepBack:
    lda pointerLo
    sec
    sbc #$08
    sta pointerLo
    lda pointerHi
    sbc #$00
    sta pointerHi
    rts
stepForward:
    lda pointerLo
    clc
    adc #$08
    sta pointerLo
    lda pointerHi
    adc #$00
    sta pointerHi
    rts
compare:
    jsr compareDirect
    beq compareReturn
    bcc compareReturn
    php
    lda $E0
    bpl compareFlags
    pla
    jsr compareRange
    rts
compareFlags:
    plp
compareReturn:
    rts
compareDirect:
    ldy #$01
    lda (pointerLo),y
    sta $E0
    and #$7F
    sta $E1
    dey
    lda $5E
    sec
    sbc (pointerLo),y
    sta $29
    lda $5F
    sbc $E1
    bne compareDirectReturn
    lda $29
compareDirectReturn:
    rts
compareRange:
    ldy #$00
    lda (pointerLo),y
    clc
    adc #$01
    sta $E0
    lda $E1
    adc #$00
    sta $E1
    lda $5E
    sec
    sbc $E0
    sta $29
    lda $5F
    sbc $E1
    bne compareRangeReturn
    lda $29
compareRangeReturn:
    rts
.endmacro

; Record layout is established by $F0D8 and the slot initializer at $CF84.
.macro SlotDescriptor record_pointer, field_05d0, field_0610, field_05e0, field_0520
    .word record_pointer
    .byte field_05d0, field_0610, field_05e0, field_0520
.endmacro

; The loader fetches ten bytes, but reads only these first nine as record
; fields. Its tenth fetch can overlap the following record or script.
.macro SlotRuntimeRecord sprite_pointer, encoded_script, mode_flags, field_0690, field_06a0, field_06b0, field_06c0
    .word sprite_pointer, encoded_script
    .byte mode_flags, field_0690, field_06a0, field_06b0, field_06c0
.endmacro

; In a negative loader mode, the two-byte resource pointer is followed
; immediately by the flag byte; the loader does not install a script pointer.
.macro SlotCompactRecord sprite_pointer, mode_flags
    .word sprite_pointer
    .byte mode_flags
.endmacro

; BOGUS command forms below name only the behaviour established by handlers.
; Script targets in PRG bank 1 are encoded as offsets below $8000.
; Opcode $67 selects a slot, stores relative fields and yields.
.macro BogusSelectRelativeSlotAndYield first, second, selector, match, mode
    .byte $67, first, second, selector, match, mode
.endmacro
; Fields fetched by opcode $89: state selector, vertical coordinate and base,
; followed by two little-endian horizontal coordinate values. Their gameplay
; roles and valid index range remain provisional.
.macro IndexedStateRecord state, vertical, vertical_base, horizontal_base, horizontal
    .byte state, vertical, vertical_base
    .word horizontal_base, horizontal
.endmacro

; Opcode $89 reads a seven-byte state record at base plus seven times an index.
.macro BogusLoadIndexedStateRecord base
    .byte $89
    .word base
.endmacro
.macro BogusSetSlot0630Bit04UnlessFF value
    .byte $A4, value
.endmacro
; Selects a slot value from state-indexed tables; table roles remain provisional.
.macro BogusSelectStateTableValue selector
    .byte $AF, selector
.endmacro
.macro BogusCopyLinkedMotionFields
    .byte $A2
.endmacro
.macro BogusStoreSlotLowAtIndexedPage
    .byte $AD
.endmacro
.macro BogusSetSlot05E0Bit40 value
    .byte $B2, value
.endmacro
.macro BogusRelinkToLastRelatedSlot
    .byte $B8
.endmacro
.macro BogusClearSlot0640PairBits first, second
    .byte $B9, first, second
.endmacro
.macro BogusSetSlot0640PairBits first, second
    .byte $BA, first, second
.endmacro
.macro BogusConfigureSlot0750 first, second
    .byte $65, first, second
.endmacro
.macro BogusBranchOnDirectionalOffset target, value
    .byte $62
    .word target - $8000
    .byte value
.endmacro
.macro BogusBranchIfAudioVoiceActive target, voice0, voice1, voice2, voice3
    .byte $77
    .word target - $8000
    .byte voice0, voice1, voice2, voice3
.endmacro
.macro BogusMarkSlot05A0AndYield
    .byte $2E
.endmacro
.macro BogusApplyAndClearSelected3E
    .byte $11
.endmacro
.macro BogusRestoreSavedScriptAndSlotFlags
    .byte $17
.endmacro
.macro BogusSubtractSlotPriorityFromField0520
    .byte $21
.endmacro
.macro BogusBranchIfSlot0520AtMost target, value
    .byte $22
    .word target - $8000
    .byte value
.endmacro
.macro BogusBranchIfSlot06D0Present target
    .byte $6B
    .word target - $8000
.endmacro
.macro BogusMarkRelatedSlotAtDepth field, depth
    .byte $BC, field, depth
.endmacro
.macro BogusSetSlotC0 value
    .byte $09, value
.endmacro
.macro BogusSetVoicePointers voice0, voice1, voice2, voice3
    .byte $31
    .word voice0, voice1, voice2, voice3
.endmacro
.macro BogusSetUnlinkedFields first, second
    .byte $1C, first, second
.endmacro
.macro BogusSetSlotBit40 value
    .byte $6A, value
.endmacro
; Opcode $76 shares the $75 handler but has its own two-byte record length.
.macro BogusSetSlot0520 value
    .byte $76, value
.endmacro
.macro BogusSetSelectedState15 value
    .byte $84, value
.endmacro
.macro BogusReleaseOtherSlots
    .byte $79
.endmacro
.macro BogusClearSlot0790Bits mask
    .byte $30, mask
.endmacro
.macro BogusWait frames
    .byte $07, frames
.endmacro
.macro BogusSetSlotFields80 first, second
    .byte $2D, first, second
.endmacro
.macro BogusSetDispatchCounter value
    .byte $2C, value
.endmacro
.macro BogusJumpBank1 target
    .byte $04
    .word target - $8000
.endmacro
.macro BogusSetSpriteAttribute20 value
    .byte $29, value
.endmacro
.macro BogusSetSlot0620Bit20
    .byte $26
.endmacro
.macro BogusBranchAndClearSlot0620Bit08 target
    .byte $27
    .word target - $8000
.endmacro
.macro BogusSetSlot0360 value
    .byte $1A, value
.endmacro
.macro BogusSetSlot07F0 value
    .byte $4C, value
.endmacro
.macro BogusBranchIfSlot0360Above target, value
    .byte $93
    .word target - $8000
    .byte value
.endmacro
.macro BogusYieldAndSlotAction mode
    .byte $1E, mode
.endmacro
.macro BogusSetSlot0670Pair first, second
    .byte $0C, first, second
.endmacro
.macro BogusSetSlot0730 value
    .byte $32, value
.endmacro
.macro BogusRestartVoice4 pointer
    .byte $49
    .word pointer
.endmacro
.macro BogusStartVoice4 pointer
    .byte $50
    .word pointer
.endmacro
.macro BogusBranchIfSlot0700AtMost target, value
    .byte $51
    .word target - $8000
    .byte value
.endmacro
.macro BogusBranchIfAbsSlot0700Below target, value
    .byte $94
    .word target - $8000
    .byte value
.endmacro
.macro BogusBranchIfSlot0620Bit10 target
    .byte $20
    .word target - $8000
.endmacro
.macro BogusLoadSlotRecord offset, mode
    .byte $63, offset, mode
.endmacro
.macro BogusSetSlot0640Pair first, second
    .byte $0B, first, second
.endmacro
.macro BogusReadSlotValue selector
    .byte $3F, selector
.endmacro
.macro BogusBranchIfSlotValueEqual target, first, second
    .byte $53
    .word target - $8000
    .byte first, second
.endmacro
.macro BogusBranchIfSlot0760Equal target, value
    .byte $23
    .word target - $8000
    .byte value
.endmacro
.macro BogusMarkMatchingSlots value, first, second, third
    .byte $36, value, first, second, third
.endmacro
.macro BogusClearSlotD0Bits mask
    .byte $5E, mask
.endmacro
.macro BogusSetSlotD0Bits mask
    .byte $5D, mask
.endmacro
.macro BogusBranchIfSlotD0Bits target, mask
    .byte $5F
    .word target - $8000
    .byte mask
.endmacro
.macro BogusBranchIfSlot0620Bit10Clear target
    .byte $BB
    .word target - $8000
.endmacro
; $95 fetches four-byte target/value cases, but consumes only the two-byte
; zero target at the end before continuing with the next command.
.macro BogusLookupSlotValue
    .byte $95
.endmacro
.macro BogusLookupCaseBank1 target, value
    .word target - $8000, value
.endmacro
.macro BogusLookupEnd
    .word $0000
.endmacro
.macro BogusSetSlot05F0Pair first, second
    .byte $06, first, second
.endmacro
.macro BogusSetSlot0660LowBits value
    .byte $0D, value
.endmacro
.macro BogusSetSlotValue value
    .byte $3E
    .word value
.endmacro
.macro BogusStoreSlotValueArray selector
    .byte $47, selector
.endmacro
.macro BogusLoadSlotValueArray selector
    .byte $46, selector
.endmacro
.macro BogusSetSlotFields40Signed first, second
    .byte $96, first, second
.endmacro
.macro BogusSetSlotAssociation value
    .byte $10, value
.endmacro
.macro BogusBranchIfSlotValueAtLeast target, value
    .byte $41
    .word target - $8000, value
.endmacro
.macro BogusMultiplySlotValueByArray selector
    .byte $72, selector
.endmacro
.macro BogusBranchIfRemainingVerticalOffsetAtMost target, value
    .byte $A0
    .word target - $8000, value
.endmacro
.macro BogusBranchIfSlotOffset target, first, second
    .byte $7B
    .word target - $8000
    .byte first, second
.endmacro
.macro BogusBranchIfSlotFieldsWithin target, first, second
    .byte $25
    .word target - $8000
    .byte first, second
.endmacro
.macro BogusAdvanceAndBranchState1B target, value
    .byte $05
    .word target - $8000
    .byte value
.endmacro
.macro BogusSetSlotMode value
    .byte $0A, value
.endmacro
.macro BogusBranchIfSlotB0AtMost target, value
    .byte $52
    .word target - $8000
    .byte value
.endmacro
.macro BogusSetDirectionalSlotFields40 first, second
    .byte $81, first, second
.endmacro
.macro BogusLoadSlotValueIndexedBank1 target
    .byte $54
    .word target - $8000
.endmacro
.macro BogusAddSlotValue value
    .byte $42
    .word value
.endmacro
.macro BogusBranchIfSlotValueNotEqual target, value
    .byte $82
    .word target - $8000, value
.endmacro
.macro BogusQueueStateAB pointer
    .byte $AB
    .word pointer
.endmacro
.macro BogusStoreSlotLowAt address
    .byte $91
    .word address
.endmacro
.macro BogusSwapSlotValueBytes
    .byte $8F
.endmacro
.macro BogusCallNativeBank1 target
    .byte $9B
    .word target - $8000 - 1
.endmacro
.macro BogusCallNativeEncoded address
    .byte $9B
    .word address
.endmacro
.macro BogusBranchIfSelectedFlags target, mask
    .byte $15
    .word target - $8000
    .byte mask
.endmacro
.macro BogusClearSelected3E
    .byte $13
.endmacro
.macro BogusClearSelected40
    .byte $14
.endmacro
.macro BogusClampSlotValueAtMost value
    .byte $80
    .word value
.endmacro
.macro BogusBranchIfSlotValueAtLeastArray selector, target
    .byte $58, selector
    .word target - $8000
.endmacro
.macro BogusLoadPage0140BySlotHigh
    .byte $AC
.endmacro
.macro BogusMaskSlotValue value
    .byte $40
    .word value
.endmacro
.macro BogusBranchIfSlotD0BitsClear target, mask
    .byte $60
    .word target - $8000
    .byte mask
.endmacro
.macro BogusOrSlotValue value
    .byte $C0
    .word value
.endmacro
; Configure bank selectors from the operand, current slot value or state.
.macro BogusConfigureBanksFromOperand value
    .byte $AA, value
.endmacro
; Clear bit $20 on the slot found at a related-link depth.
.macro BogusClearRelatedSlotBit20 depth
    .byte $BD, depth
.endmacro
; Set bit $20 on the current slot.
.macro BogusSetCurrentSlotBit20
    .byte $BE
.endmacro
.macro BogusRemapSlotValue
    .byte $B1
.endmacro
.macro BogusRemapCase value, replacement
    .word value, replacement
.endmacro
.macro BogusRemapEnd
    .word $0000
.endmacro
.macro BogusBranchIfState27Set target
    .byte $9A
    .word target - $8000
.endmacro
.macro BogusSetMainState value
    .byte $0F, value
.endmacro
.macro BogusInitializeSplitAndMainState
    .byte $99
.endmacro
.macro BogusAddSlotFields00 first, second
    .byte $08, first, second
.endmacro
.macro BogusBranchIfSlot0630Bit02 target
    .byte $C2
    .word target - $8000
.endmacro
.macro BogusAdjustSlotBounds first, second
    .byte $A9, first, second
.endmacro
.macro BogusReadMapAtSlotOffset
    .byte $A5
.endmacro
.macro BogusXorSlotValue value
    .byte $5B
    .word value
.endmacro
.macro BogusBranchIfSlot0360AtMost target, value
    .byte $1B
    .word target - $8000
    .byte value
.endmacro
.macro BogusBranchIfState58ZeroAndClear target
    .byte $8B
    .word target - $8000
.endmacro
.macro BogusClearSlotBitset value
    .byte $8A, value
.endmacro
.macro BogusSetInvertedState18 value
    .byte $43, value
.endmacro
.macro BogusBranchIfSlotCoordinatesA3 target, first, second
    .byte $A3
    .word target - $8000
    .byte first, second
.endmacro
.macro BogusBranchIfSlotCoordinates01 target, first, second
    .byte $01
    .word target - $8000
    .byte first, second
.endmacro
.macro BogusBranchIfOffsetProbe target, count
    .byte $02
    .word target - $8000
    .byte count
.endmacro
.macro BogusBranchIfDirectionalOffsetClear target, value
    .byte $03
    .word target - $8000
    .byte value
.endmacro
.macro BogusBranchIfPositiveOffsetProbe target, count
    .byte $66
    .word target - $8000
    .byte count
.endmacro
.macro BogusStartVoice4FromIndexedPair pointer
    .byte $B3
    .word pointer
.endmacro
.macro BogusSetVoicesFromIndexedRecord pointer
    .byte $78
    .word pointer
.endmacro
.macro BogusSetLinkedSlotFieldsC0 first, second
    .byte $7D, first, second
.endmacro
.macro BogusSetSlot0660HighBits value
    .byte $0E, value
.endmacro
.macro BogusSetSlot0790Bits mask
    .byte $2F, mask
.endmacro
.macro BogusFindLinkedSlot
    .byte $8C
.endmacro
.macro BogusLoadRecordAndClearSavedState value
    .byte $00, value
.endmacro
.macro BogusSetSlotPositionFromOperands first, second
    .byte $1D, first, second
.endmacro
.macro BogusBranchIfSlot0370AtMost target, value
    .byte $4B
    .word target - $8000
    .byte value
.endmacro
.macro BogusAddSlotValueFromArray selector
    .byte $48, selector
.endmacro
.macro BogusCountSlotsByRecord value
    .byte $7A, value
.endmacro
.macro BogusBranchIfFirstWorldOffsetAtMost target, value
    .byte $9E
    .word target - $8000, value
.endmacro
.macro BogusBranchIfSecondWorldOffsetAtMost target, value
    .byte $9F
    .word target - $8000, value
.endmacro
.macro BogusLoadSlotLowFromByteArray selector
    .byte $A1, selector
.endmacro
.macro BogusCreateSlotFromValue first, second
    .byte $A6, first, second
.endmacro
.macro BogusFindSlotAtValueOffset
    .byte $A7
.endmacro
.macro BogusAlignSlotValueToScrollGrid
    .byte $A8
.endmacro
.macro BogusInitializeOtherSlotRelative first, second, third, fourth
    .byte $1F, first, second, third, fourth
.endmacro
.macro BogusInitializeOtherSlotAbsolute first, second, third, fourth
    .byte $61, first, second, third, fourth
.endmacro
.macro BogusQueueState6E pointer, first, second, mode, count
    .byte $6E
    .word pointer
    .byte first, second, mode, count
.endmacro
.macro BogusBranchIfState07ZeroAndClear target
    .byte $3D
    .word target - $8000
.endmacro
.macro BogusSetBackgroundPalettePointer pointer
    .byte $4D
    .word pointer
.endmacro
.macro BogusSetSpritePalettePointer pointer
    .byte $4E
    .word pointer
.endmacro
.macro BogusSetState03BC value
    .byte $4F, value
.endmacro
.macro BogusSetState13Bits value
    .byte $55, value
.endmacro
.macro BogusClearState13Bits value
    .byte $56, value
.endmacro
.macro BogusSaveStateAndPlaceSlots value
    .byte $98, value
.endmacro
.macro BogusReloadSlotRecordMode1 value
    .byte $C4, value
.endmacro
.macro BogusSetInvertedState3B value
    .byte $64, value
.endmacro
.macro BogusSetInvertedState03ED value
    .byte $9C, value
.endmacro
.macro BogusSetSelectedField selector, value
    .byte $3B, selector, value
.endmacro
.macro BogusReadSlotLowFrom address
    .byte $90
    .word address
.endmacro
; The slot check may yield and retry before restoring its saved pointer.
.macro BogusCheckSlotFlagsAndRestorePointer
    .byte $19
.endmacro
.macro BogusInitializeSlotMotionFields
    .byte $68
.endmacro
.macro BogusBranchIfMatchingSlotReady target, first, second, third
    .byte $35
    .word target - $8000
    .byte first, second, third
.endmacro
.macro BogusBranchIfSlotRecord06AtLeast target, value
    .byte $28
    .word target - $8000
    .byte value
.endmacro
.macro BogusClearMatchingSlotFlag20 first, second, third
    .byte $AE, first, second, third
.endmacro
.macro BogusJumpViaSlotIndexedTable
    .byte $44
.endmacro
.macro BogusIndexedTargetBank1 target
    .word target - $8000
.endmacro
.macro BogusSetSlot0370 value
    .byte $4A, value
.endmacro
.macro BogusExchangeSlotValueArray selector
    .byte $5A, selector
.endmacro
.macro BogusDivideSlotValueByByte value
    .byte $85, value
.endmacro
.macro BogusReadSelectedSlot0520 selector
    .byte $86, selector
.endmacro
.macro BogusWriteSelectedSlot0520 selector
    .byte $87, selector
.endmacro
.macro BogusBranchIfSelectedFlagsClear target, mask
    .byte $92
    .word target - $8000
    .byte mask
.endmacro
.macro BogusCreateLinkedSlot first, second, third, fourth
    .byte $69, first, second, third, fourth
.endmacro
.macro BogusLoadSlotRecordAtPointer pointer
    .byte $16
    .word pointer
.endmacro
.macro BogusBranchIfSelectedFieldEqual target, value
    .byte $24
    .word target - $8000
    .byte value
.endmacro
.macro BogusSetLinkedFieldsAndYield first, second
    .byte $6C, first, second
.endmacro
.macro BogusRefreshSlotDrawPosition
    .byte $C3
.endmacro
.macro BogusFollowLinkedSlotsAndYield first, second, third, fourth, fifth
    .byte $B6, first, second, third, fourth, fifth
.endmacro
.macro BogusRelinkSlots
    .byte $B7
.endmacro
.macro BogusBranchIfSlot0780Equal target, value
    .byte $2B
    .word target - $8000
    .byte value
.endmacro

; A command byte indexes three parallel tables: record length, and the low and
; high bytes of an RTS dispatch address. Handler addresses below are actual
; entry points; the stored pointer is entry minus one because RTS increments it.
; The command names and meanings remain to be recovered. There are 197 entries
; before the following native code; runtime bounds have not been established.
.macro ScriptOp length, handler, part
    .if part = 0
        .byte length
    .elseif part = 1
        .byte <(handler - 1)
    .elseif part = 2
        .byte >(handler - 1)
    .else
        .error "invalid script table part"
    .endif
.endmacro

.macro ScriptTable part
    ScriptOp 2, $D70F, part ; CONTROL_SCRIPT_LENGTHS
    ScriptOp 5, $D72C, part ; CONTROL_SCRIPT_LOW
    ScriptOp 4, $D79B, part ; CONTROL_SCRIPT_HIGH
    ScriptOp 4, $D7B0, part ; opcode $03
    ScriptOp 3, $D7C7, part ; opcode $04
    ScriptOp 4, $D7D0, part ; opcode $05
    ScriptOp 3, $D7DC, part ; opcode $06
    ScriptOp 2, $D7FB, part ; opcode $07
    ScriptOp 3, $D825, part ; opcode $08
    ScriptOp 2, $D82B, part ; opcode $09
    ScriptOp 2, $D836, part ; opcode $0A
    ScriptOp 3, $D8CF, part ; opcode $0B
    ScriptOp 3, $D8DA, part ; opcode $0C
    ScriptOp 2, $D8F5, part ; opcode $0D
    ScriptOp 2, $D8FA, part ; opcode $0E
    ScriptOp 2, $D90D, part ; opcode $0F
    ScriptOp 2, $D919, part ; opcode $10
    ScriptOp 1, $D94B, part ; opcode $11
    ScriptOp 1, $D960, part ; opcode $12
    ScriptOp 1, $D972, part ; opcode $13
    ScriptOp 1, $D97B, part ; opcode $14
    ScriptOp 4, $D984, part ; opcode $15
    ScriptOp 3, $D991, part ; opcode $16
    ScriptOp 1, $D9BB, part ; opcode $17
    ScriptOp 1, $FD29, part ; opcode $18
    ScriptOp 1, $D9DA, part ; opcode $19
    ScriptOp 2, $DA0A, part ; opcode $1A
    ScriptOp 4, $DA11, part ; opcode $1B
    ScriptOp 3, $DA1B, part ; opcode $1C
    ScriptOp 3, $DA33, part ; opcode $1D
    ScriptOp 2, $DA51, part ; opcode $1E
    ScriptOp 5, $DA85, part ; opcode $1F
    ScriptOp 3, $DAD9, part ; opcode $20
    ScriptOp 1, $DAE3, part ; opcode $21
    ScriptOp 4, $DAFE, part ; opcode $22
    ScriptOp 4, $DB06, part ; opcode $23
    ScriptOp 4, $DB0E, part ; opcode $24
    ScriptOp 5, $DB27, part ; opcode $25
    ScriptOp 1, $DB53, part ; opcode $26
    ScriptOp 3, $DB5C, part ; opcode $27
    ScriptOp 4, $DB6C, part ; opcode $28
    ScriptOp 2, $DB76, part ; opcode $29
    ScriptOp 4, $DB7D, part ; opcode $2A
    ScriptOp 4, $DB85, part ; opcode $2B
    ScriptOp 2, $DB8D, part ; opcode $2C
    ScriptOp 3, $DB92, part ; opcode $2D
    ScriptOp 1, $DB98, part ; opcode $2E
    ScriptOp 2, $DBA0, part ; opcode $2F
    ScriptOp 2, $DBA9, part ; opcode $30
    ScriptOp 9, $DBB4, part ; opcode $31
    ScriptOp 2, $DBEB, part ; opcode $32
    ScriptOp 1, $DBF1, part ; opcode $33
    ScriptOp 1, $DC08, part ; opcode $34
    ScriptOp 6, $DC1C, part ; opcode $35
    ScriptOp 5, $DC7E, part ; opcode $36
    ScriptOp 4, $DCD4, part ; opcode $37
    ScriptOp 4, $DCD4, part ; opcode $38
    ScriptOp 6, $DCD4, part ; opcode $39
    ScriptOp 3, $DCD4, part ; opcode $3A
    ScriptOp 3, $DCF4, part ; opcode $3B
    ScriptOp 5, $DD00, part ; opcode $3C
    ScriptOp 3, $DD18, part ; opcode $3D
    ScriptOp 3, $DD25, part ; opcode $3E
    ScriptOp 2, $DD2E, part ; opcode $3F
    ScriptOp 3, $DE83, part ; opcode $40
    ScriptOp 5, $DE90, part ; opcode $41
    ScriptOp 3, $DE9E, part ; opcode $42
    ScriptOp 2, $DEAC, part ; opcode $43
    ScriptOp 1, $DEB3, part ; opcode $44
    ScriptOp 4, $DED1, part ; opcode $45
    ScriptOp 2, $DED9, part ; opcode $46
    ScriptOp 2, $DEF3, part ; opcode $47
    ScriptOp 2, $DF16, part ; opcode $48
    ScriptOp 3, $DF38, part ; opcode $49
    ScriptOp 2, $DF55, part ; opcode $4A
    ScriptOp 4, $DF5C, part ; opcode $4B
    ScriptOp 2, $DF66, part ; opcode $4C
    ScriptOp 3, $DF6D, part ; opcode $4D
    ScriptOp 3, $DF8E, part ; opcode $4E
    ScriptOp 2, $DF9F, part ; opcode $4F
    ScriptOp 3, $DF43, part ; opcode $50
    ScriptOp 4, $DFA5, part ; opcode $51
    ScriptOp 4, $DFAF, part ; opcode $52
    ScriptOp 5, $DFB6, part ; opcode $53
    ScriptOp 3, $DFC3, part ; opcode $54
    ScriptOp 2, $DFE5, part ; opcode $55
    ScriptOp 2, $DFEC, part ; opcode $56
    ScriptOp 3, $DFF5, part ; opcode $57
    ScriptOp 4, $DFF5, part ; opcode $58
    ScriptOp 3, $E01A, part ; opcode $59
    ScriptOp 2, $E026, part ; opcode $5A
    ScriptOp 3, $E049, part ; opcode $5B
    ScriptOp 2, $E056, part ; opcode $5C
    ScriptOp 2, $E056, part ; opcode $5D
    ScriptOp 2, $E05E, part ; opcode $5E
    ScriptOp 4, $E068, part ; opcode $5F
    ScriptOp 4, $E071, part ; opcode $60
    ScriptOp 5, $E07A, part ; opcode $61
    ScriptOp 4, $E0AE, part ; opcode $62
    ScriptOp 3, $E0D6, part ; opcode $63
    ScriptOp 2, $E0DD, part ; opcode $64
    ScriptOp 3, $E0E4, part ; opcode $65
    ScriptOp 4, $E0FB, part ; opcode $66
    ScriptOp 6, $E10D, part ; opcode $67
    ScriptOp 1, $E160, part ; opcode $68
    ScriptOp 5, $E170, part ; opcode $69
    ScriptOp 2, $E1A3, part ; opcode $6A
    ScriptOp 3, $E1B4, part ; opcode $6B
    ScriptOp 3, $E1BE, part ; opcode $6C
    ScriptOp 5, $E1D9, part ; opcode $6D
    ScriptOp 7, $E1D9, part ; opcode $6E
    ScriptOp 6, $E202, part ; opcode $6F
    ScriptOp 10, $E221, part ; opcode $70
    ScriptOp 2, $E221, part ; opcode $71
    ScriptOp 2, $E267, part ; opcode $72
    ScriptOp 2, $E284, part ; opcode $73
    ScriptOp 5, $E290, part ; opcode $74
    ScriptOp 4, $E293, part ; opcode $75
    ScriptOp 2, $E293, part ; opcode $76
    ScriptOp 7, $E29A, part ; opcode $77
    ScriptOp 3, $E2C5, part ; opcode $78
    ScriptOp 1, $E30F, part ; opcode $79
    ScriptOp 2, $E327, part ; opcode $7A
    ScriptOp 5, $E341, part ; opcode $7B
    ScriptOp 2, $E34E, part ; opcode $7C
    ScriptOp 3, $E34E, part ; opcode $7D
    ScriptOp 1, $E369, part ; opcode $7E
    ScriptOp 7, $E375, part ; opcode $7F
    ScriptOp 3, $E3A2, part ; opcode $80
    ScriptOp 3, $E3B6, part ; opcode $81
    ScriptOp 5, $E3E8, part ; opcode $82
    ScriptOp 3, $E3F7, part ; opcode $83
    ScriptOp 2, $E410, part ; opcode $84
    ScriptOp 2, $E419, part ; opcode $85
    ScriptOp 2, $E42B, part ; opcode $86
    ScriptOp 2, $E442, part ; opcode $87
    ScriptOp 2, $E44B, part ; opcode $88
    ScriptOp 3, $E452, part ; opcode $89
    ScriptOp 2, $E581, part ; opcode $8A
    ScriptOp 3, $E5A4, part ; opcode $8B
    ScriptOp 1, $E5B1, part ; opcode $8C
    ScriptOp 2, $E5E0, part ; opcode $8D
    ScriptOp 2, $E5E0, part ; opcode $8E
    ScriptOp 1, $E5E0, part ; opcode $8F
    ScriptOp 3, $E5EB, part ; opcode $90
    ScriptOp 3, $E5F3, part ; opcode $91
    ScriptOp 4, $E606, part ; opcode $92
    ScriptOp 4, $E613, part ; opcode $93
    ScriptOp 4, $E61D, part ; opcode $94
    ScriptOp 1, $E62C, part ; opcode $95
    ScriptOp 3, $E656, part ; opcode $96
    ScriptOp 2, $E673, part ; opcode $97
    ScriptOp 2, $E696, part ; opcode $98
    ScriptOp 1, $E6E6, part ; opcode $99
    ScriptOp 3, $E706, part ; opcode $9A
    ScriptOp 3, $E71B, part ; opcode $9B
    ScriptOp 2, $E71E, part ; opcode $9C
    ScriptOp 2, $E726, part ; opcode $9D
    ScriptOp 5, $E727, part ; opcode $9E
    ScriptOp 5, $E745, part ; opcode $9F
    ScriptOp 5, $E75B, part ; opcode $A0
    ScriptOp 2, $E780, part ; opcode $A1
    ScriptOp 1, $E789, part ; opcode $A2
    ScriptOp 5, $D72C, part ; opcode $A3
    ScriptOp 2, $E799, part ; opcode $A4
    ScriptOp 1, $E7AA, part ; opcode $A5
    ScriptOp 3, $E7C4, part ; opcode $A6
    ScriptOp 1, $E7D3, part ; opcode $A7
    ScriptOp 1, $E83C, part ; opcode $A8
    ScriptOp 3, $E85D, part ; opcode $A9
    ScriptOp 2, $E882, part ; opcode $AA
    ScriptOp 3, $E88F, part ; opcode $AB
    ScriptOp 1, $E8B6, part ; opcode $AC
    ScriptOp 1, $E8BE, part ; opcode $AD
    ScriptOp 4, $E8C6, part ; opcode $AE
    ScriptOp 2, $E8E3, part ; opcode $AF
    ScriptOp 1, $E5B6, part ; opcode $B0
    ScriptOp 1, $E918, part ; opcode $B1
    ScriptOp 2, $E956, part ; opcode $B2
    ScriptOp 3, $E967, part ; opcode $B3
    ScriptOp 3, $E998, part ; opcode $B4
    ScriptOp 1, $E998, part ; opcode $B5
    ScriptOp 6, $E9A0, part ; opcode $B6
    ScriptOp 1, $E9C7, part ; opcode $B7
    ScriptOp 1, $E9EB, part ; opcode $B8
    ScriptOp 3, $EA1C, part ; opcode $B9
    ScriptOp 3, $EA31, part ; opcode $BA
    ScriptOp 3, $EA42, part ; opcode $BB
    ScriptOp 3, $EA4D, part ; opcode $BC
    ScriptOp 2, $EA86, part ; opcode $BD
    ScriptOp 1, $EA96, part ; opcode $BE
    ScriptOp 3, $E88F, part ; opcode $BF
    ScriptOp 3, $EA9F, part ; opcode $C0
    ScriptOp 2, $EAAC, part ; opcode $C1
    ScriptOp 3, $EAC8, part ; opcode $C2
    ScriptOp 1, $EAD3, part ; opcode $C3
    ScriptOp 2, $EAD7, part ; opcode $C4
.endmacro

; This section is byte-identical in both PRG banks. It switches between mapper
; selections while copying data via pointers at $FE/$FF or $F6/$F7. The sign
; bit of the pointer's high byte governs whether a bank change is required.
; Several RAM names and callers remain provisional; preserve absolute addressing
; for the zero-page locations where the original uses three-byte instructions.
.macro BankHelpers
; Fetch X bytes from ($53), or select the length using the first byte and the
; table at $FDA7 when X is zero. Copy the record to $60 and, if a bank switch
; occurred, restore the stored default selection. Record meanings are pending.
FetchVariableRecord:
    lda a:$54                    ; CONTROL_RECORD_FETCH
    pha
    bmi RecordBankReady
    ora #$80
    sta a:$54
    lda $03C2
    ldy $03C3
    jsr SwitchBank
RecordBankReady:
    ldy #$00
    cpx #$00
    bne RecordLengthReady
    lda ($53),y
    tax
    lda ScriptRecordLengths,x
    tax
RecordLengthReady:
    stx a:$FE
RecordCopyLoop:
    lda ($53),y
    sta $60,y
    iny
    dex
    bne RecordCopyLoop
    pla
    bmi SharedReturn
    sta a:$54
RestoreDefaultBank:
    lda $03C0                    ; CONTROL_RESTORE_BANK
    ldy $03C1
    jmp SwitchBank
SharedReturn:
    rts                           ; Also reached from an earlier unresolved routine.

CopyToStack:
    tsx                          ; CONTROL_STACK_COPY
    inx
    inx
    inx
    lda a:$FF
    pha
    bmi StackCopyReady
    ora #$80
    sta a:$FF
    lda $03C2
    ldy $03C3
    jsr SwitchBank
StackCopyReady:
    ldy #$00
StackCopyLoop:
    lda ($FE),y
    sta $0100,x
    iny
    inx
    dec $03E0
    bne StackCopyLoop
    pla
    bmi StackCopyReturn
    sta a:$FF
    jmp RestoreDefaultBank
StackCopyReturn:
    rts

; Copy bytes to the $0300 buffer using the stride in $03D1.
CopyStridedToBuffer:
    lda a:$F7
    pha
    bmi StridedCopyReady
    ora #$80
    sta a:$F7
    lda $03C2
    ldy $03C3
    jsr SwitchBank
StridedCopyReady:
    clc
    ldy #$00
StridedCopyLoop:
    lda ($F6),y
    sta $0300,x
    inx
    lda a:$F6
    adc $03D1                    ; CONTROL_STRIDE_COPY
    sta a:$F6
    bcc StridedCopyAdvanceDone
    inc a:$F7
    clc
StridedCopyAdvanceDone:
    dec $03D0
    bne StridedCopyLoop
RestoreCopyBank:
    pla
    bmi CopyReturn
    lda a:$F7
    eor #$80
    sta a:$F7
    jmp RestoreDefaultBank
CopyReturn:
    rts

; First read uses index 0; later reads use index 2. The source does not
; advance the pointer here, so retain this behaviour pending caller analysis.
CopyIndexedToState:
    ldy #$00
    lda a:$F7
    pha
    bmi IndexedCopyReady
    ora #$80
    sta a:$F7
    lda $03C2
    ldy $03C3
    jsr SwitchBank
IndexedCopyReady:
    ldy #$00
IndexedCopyLoop:
    lda ($F6),y
    sta $03D5,x
    inx
    dec $03D0
    beq RestoreCopyBank
    ldy #$02                     ; CONTROL_PAIR_COPY
    jmp IndexedCopyLoop

CopyLinearToBuffer:
    lda a:$F7
    pha
    bmi LinearCopyReady
    ora #$80
    sta a:$F7
    lda $03C2
    ldy $03C3
    jsr SwitchBank
LinearCopyReady:
    clc
    ldy #$00
LinearCopyLoop:
    lda ($F6),y
    sta $0300,x
    inx
    lda a:$F6
    adc #$01                     ; CONTROL_LINEAR_COPY
    sta a:$F6
    bcc LinearCopyAdvanceDone
    inc a:$F7
    clc
LinearCopyAdvanceDone:
    dec $03D0
    bne LinearCopyLoop
    jmp RestoreCopyBank

; Shift four source bits into each destination byte in the $0300 buffer.
CopyBitsToBuffer:
    lda a:$F7
    pha
    bmi BitCopyReady
    ora #$80
    sta a:$F7
    lda $03C2
    ldy $03C3
    jsr SwitchBank
BitCopyReady:
    ldy #$00
BitCopyLoop:
    lda ($F6),y
    ror a                        ; CONTROL_BIT_COPY
    ror $0300,x
    ror a
    ror $0300,x
    ror a
    ror $0300,x
    ror a
    ror $0300,x
    inx
    lda a:$F6
    clc
    adc #$01
    sta a:$F6
    bcc BitCopyAdvanceDone
    inc a:$F7
BitCopyAdvanceDone:
    dec $03D0
    bne BitCopyLoop
    jmp RestoreCopyBank
.endmacro

.macro BankScriptNativeCall
; $61/$62 hold the encoded RTS address of a native script helper. For an
; address below $8000 select the bank in $03C2/$03C3 before making the call.
; The helper returns to this routine, which restores the default bank.
CallScriptNativeBanked:
    lda a:$62                    ; CONTROL_SCRIPT_NATIVE_CALL
    bmi CallScriptNativeReady
    lda $03C2
    ldy $03C3
    jsr SwitchBank
CallScriptNativeReady:
    jsr CallScriptNativeOperand
    jmp RestoreDefaultBank
CallScriptNativeOperand:
    lda a:$62
    ora #$80
    pha
    lda a:$61
    pha
    rts
.endmacro

; Both 32 KiB PRG banks contain this tail at the same CPU addresses.
; NMI state addresses differ; its called routines and timing remain to be traced.
.macro BankTail nmiValue, nmiIndex, padding
SwitchBank:
    sta BankValues,y             ; CONTROL_SWITCH
    rts

; Each byte selects a CHR bank and PRG bank. The matching byte at the write
; address also prevents conflicting values from being driven on the ROM bus.
BankValues:
    .repeat 8, chrBank
        .byte ($0C | (chrBank << 4)), ($0D | (chrBank << 4)) ; CONTROL_TABLE
    .endrepeat

NmiHandler:
    pha
    tya
    pha
    lda nmiValue
    sta NmiSavedValue
    lda nmiIndex
    sta NmiSavedIndex
    jsr RestoreDefaultBank
    jsr $8211
    lda NmiSavedValue
    ldy NmiSavedIndex            ; CONTROL_NMI
    jsr SwitchBank
    pla
    tay
    pla
IrqHandler:
    rti

ResetEntry:
    ldx #$FF                     ; CONTROL_RESET
    txs
    lda #$0C
    sta BankValues
    jmp $8000

    .incbin padding              ; Unclassified six-byte local region.
    .word NmiHandler, ResetEntry, IrqHandler ; CONTROL_VECTORS
.endmacro

.segment "HEADER"
; Exact NES 2.0 container header for the pinned reference. This is metadata.
.byte $4E, $45, $53, $1A, $04, $08, $B1, $08
.byte $00, $00, $00, $00, $00, $00, $00, $01

.segment "PRG0"
.scope Bank0
BankStart:
Boot:
    sei                          ; CONTROL_BOOT
    lda #$00
    sta PPUCTRL
    jsr WaitVBlank
    jsr WaitVBlank
    lda #$06
    sta PPUMASK

; $04DE and $04DF hold a state byte and its complement used on reset. Their
; broader purpose is still provisional. An invalid pair selects state $83.
CheckResetState:
    lda $04DE
    eor $04DF
    cmp #$FF                     ; CONTROL_STATE_DISPATCH
    beq ResetStateValid
    jmp SelectReset83
ResetStateValid:
    lda $04DE
    cmp #$03
    beq SelectReset83
    cmp #$04
    beq SelectReset83
    cmp #$05
    beq SelectReset85
    cmp #$06
    beq SelectReset85
    cmp #$07
    beq SelectReset85
    cmp #$09
    beq SelectReset85
    cmp #$0B
    beq SelectReset85
    cmp #$83
    beq SelectReset84
    cmp #$84
    beq SelectReset85
    cmp #$85
    beq SelectReset86
    cmp #$86
    beq SelectReset87
    cmp #$87
    beq SelectReset89
    cmp #$89
    beq SelectReset8B
    jmp SelectReset83

SelectReset83:
    lda #$83
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence83
SelectReset84:
    lda #$84
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence84
SelectReset89:
    lda #$89
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence89
SelectReset8B:
    lda #$8B
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence8B
SelectReset85:
    lda #$85
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence85
SelectReset86:
    lda #$86
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence86
SelectReset87:
    lda #$87
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence87

; Writes target their own immediate operands in ROM. The byte on the ROM bus
; equals the value being stored, preserving the mapper write under bus conflict.
ResetSequence83:
    jsr PulseMapper00
    jsr ResetDelayShort
    jsr PulseMapper0C
    jsr ResetDelayShort
PulseMapper04Y:
    ldy #$04
    sty PulseMapper04Y+1
PulseMapper0CX:
    ldx #$0C
    stx PulseMapper0CX+1
    jmp InitializeGame

ResetSequence84:
    jsr PulseMapperTimed
    jsr PulseMapper04And0C
    jsr PulseMapper04And0C
    jmp InitializeGame
PulseMapper04And0C:
PulseMapper0CA:
    lda #$0C
    sta PulseMapper0CA+1
    jsr ResetDelayMedium
PulseMapper04A:
    lda #$04
    sta PulseMapper04A+1
    jmp ResetDelayMedium

ResetSequence85:
    jsr PulseMapper00
    ldx #$14
ResetDelayX:
    dex
    bne ResetDelayX
    jsr PulseMapper0C
    jsr ResetDelayLong
    jmp ResetSequenceCommon
ResetSequence86:
    jsr PulseMapper00
    ldx #$28
    jmp ResetDelayX
ResetSequence87:
    jsr PulseMapper00
    ldx #$46
    jmp ResetDelayX
ResetSequence89:
    jsr PulseMapperTimed
    jsr PulseMapperTimed
ResetSequenceCommon:
PulseMapper08Y:
    ldy #$08
    sty PulseMapper08Y+1
    jsr ResetDelayShort
PulseMapper0CX2:
    ldx #$0C
    stx PulseMapper0CX2+1
    jmp InitializeGame

ResetSequence8B:
    lda $04DF
    pha
    lda #$0F
    sta $04DF
ResetSequence8BLoop:
    jsr PulseMapperTimed
    jsr PulseMapperTimed
PulseMapper08X:
    ldx #$08
    stx PulseMapper08X+1
    ldx #$32
ResetDelay32:
    dex
    bne ResetDelay32
PulseMapper0CX3:
    ldx #$0C
    stx PulseMapper0CX3+1
    dec $04DF
    bne ResetSequence8BLoop
    pla
    sta $04DF
    jmp InitializeGame

ResetDelayShort:
    ldy #$02
    ldx #$46
    jmp ResetDelayLoop
ResetDelayMedium:
    ldy #$04
    ldx #$3A
ResetDelayLoop:
    dex
    bne ResetDelayLoop
    dey
    bne ResetDelayLoop
    rts
ResetDelayLong:
    ldy #$20
    ldx #$C8
    jmp ResetDelayLoop
PulseMapperTimed:
    jsr PulseMapper00
    jsr ResetDelayLong
    jsr PulseMapper0C
    jsr ResetDelayLong
    rts
PulseMapper00:
    ldx #$00
    stx PulseMapper00+1
    rts
PulseMapper0C:
    ldx #$0C
    stx PulseMapper0C+1
    rts

InitializeGame:
    lda #$7F
    sta $04DD
    lda PPUSTATUS
    lda #$3F
    sta PPUADDR
    lda #$00
    sta PPUADDR
    ldy #$1F
    lda #$0E
ClearPalette:
    sta PPUDATA
    dey
    bpl ClearPalette
    lda #$00
    sta $0387
    sta $0380
    sta $03FC
    sta $03FD
    sta $03F3
    sta $03F5
    sta $03A4
    sta $03EB
    sta $0382
    sta $0388
    sta $038D
    sta $038E
    sta $0394
    sta $0395
    sta $0392
    sta $0393
    sta $03FF
    sta $0397
    sta $03E8
    sta $03EC
    sta $03AB
    sta $03ED
    sta $03F2
    sta $03BC
    sta $03BE
    sta $03BB
    sta $03C0
    sta $03BD
    lda #$04
    sta $0391
    lda #$0A
    sta $03E6
    lda #$18
    sta $03FE
    jsr InitializeShadowOam
    jsr ClearSlotRecords
    jsr InitializeAudioVoices
    jsr InitializeMainState
    jsr EnablePpuNmi
MainLoop:
    jsr MainLoopStep
    jmp MainLoop
.assert (* - BankStart) = $0211, error, "bank 0 startup size"

; Called by the common NMI tail after restoring its default bank selection.
; The saved working state and external engine calls remain deliberately unnamed.
NmiFrameWork:
    lda #$06
    sta PPUMASK
    lda $03B9
    sec
    sbc $03BC
    sta $0200
    lda $03F2
    bne SkipOamDma
    sta OAMADDR
    lda #$02
    sta OAMDMA
SkipOamDma:
    jsr RestorePpuCtrl
    lda PPUSTATUS
    and #$20
    sta $0381
    txa
    pha
    tya
    pha
    jsr FlushPpuUpdates
    lda #$00
    sta $0380
    lda $03E2
    pha
    lda $03E3
    pha
    lda $03E4
    pha
    lda $03E5
    pha
    jsr $97C8
    jsr ApplyNmiPpuState
    lda $FE
    pha
    lda $FF
    pha
    lda $03E0
    pha
    lda $03E1
    pha
    lda $03DE
    pha
    lda $03DF
    pha
    lda $039A
    pha
    lda $039B
    pha
    lda $039C
    pha
    jsr SwapNmiWorkspace
    dec $04DD
    bne ReadController
    lda $04DE
    and #$7F
    sta $04DE
    eor #$FF
    sta $04DF

; Strobe controller 1, read eight serial bits, and update the stored current
; and changed states. The following counter and masks implement a repeat path.
ReadController:
    lda #$01
    sta JOY1
    lda #$00
    sta JOY1
    lda #$00
    sta $038F
    ldx #$08                     ; CONTROL_FRAME_WORK
ReadControllerBit:
    lda JOY1
    ror a
    rol $038F
    dex
    bne ReadControllerBit
    lda $038F
    tax
    eor $038D
    sta $038F
    stx $038D
    lda $038D
    and $0392
    sta $0392
    lda $038D
    and $0394
    sta $0394
    dec $0391
    bne DispatchControllerChanges
    lda #$04
    sta $0391
    lda $0392
    ora $038F
    sta $038F
    lda $0394
    and #$0F
    sta $0392
    lda $038D
    sta $0394

; Serial order makes $038D/$038F bits 0..7 Right, Left, Down, Up, Start,
; Select, B and A. Dispatch requires at least one changed bit still held.
; The following shifts use all changed bits, including releases, so an
; A-to-B or B-to-A transition invokes both action handlers in the same frame.
DispatchControllerChanges:
    lda $038F
    and $038D
    beq FrameEngineWork
    ror $038F
    bcc ControllerHandler1Done
    jsr ControllerPositiveXFirst
ControllerHandler1Done:
    ror $038F
    bcc ControllerHandler2Done
    jsr ControllerNegativeXFirst
ControllerHandler2Done:
    ror $038F
    bcc ControllerHandler3Done
    jsr ControllerPositiveYFirst
ControllerHandler3Done:
    ror $038F
    bcc ControllerHandler4Done
    jsr ControllerNegativeYFirst
ControllerHandler4Done:
    ror $038F
    bcc ControllerHandler5Done
    jsr ControllerTogglePause
ControllerHandler5Done:
    ror $038F
    bcc ControllerHandler6Done
    jsr ControllerConfiguredActionFirst
ControllerHandler6Done:
    ror $038F
    bcc ControllerHandler7Done
    jsr ControllerAction2DFirst
ControllerHandler7Done:
    ror $038F
    bcc FrameEngineWork
    jsr ControllerAction24First
FrameEngineWork:
    lda a:$28                    ; Original uses absolute addressing for $0028.
    bne RestoreNmiState
    jsr ProcessPendingPpuUpdate
    jsr UpdateScrollWork
    jsr UpdatePaletteStreams
    lda $03F2
    bne SkipFrameRoutine
    jsr AdvanceSpriteAnimations
SkipFrameRoutine:
    jsr UpdateAudioVoices
RestoreNmiState:
    jsr SwapNmiWorkspace
    pla
    sta $039C
    pla
    sta $039B
    pla
    sta $039A
    pla
    sta $03DF
    pla
    sta $03DE
    pla
    sta $03E1
    pla
    sta $03E0
    pla
    sta $FF
    pla
    sta $FE
    pla
    sta $03E5
    pla
    sta $03E4
    pla
    sta $03E3
    pla
    sta $03E2
    pla
    tay
    pla
    tax
    jmp EnablePpuNmi
.assert (* - BankStart) = $0389, error, "bank 0 NMI frame work size"

; NMI calls this both before and after frame work. It swaps the eight bytes
; at $EC-$F3 and four bytes at $03F7-$03FA with their corresponding saved
; slots. The zero-page and absolute instruction widths are significant.
SwapNmiWorkspace:
    .repeat 8, slot
        lda $EC + slot           ; CONTROL_SWAP_WORKSPACE
        ldx $03AC + slot
        sta $03AC + slot
        stx $EC + slot
    .endrepeat
    .repeat 4, slot
        lda $03F7 + slot
        ldx $03B4 + slot
        sta $03B4 + slot
        stx $03F7 + slot
    .endrepeat
    rts
.assert (* - BankStart) = $040A, error, "bank 0 NMI workspace swap size"

; Set shadow sprite zero from the split position and fixed tile/attributes.
InitializeSplitSprite:
    lda $03B9                    ; CONTROL_INITIALIZE_SPLIT_SPRITE
    sta $0200
    lda #$01
    sta $0203
    lda #$FE
    sta $0201
    lda #$28
    sta $0202
    rts
.assert (* - BankStart) = $0420, error, "bank 0 split sprite initialization end"

; Apply saved scroll/mask state when enabled, update PPUCTRL, then restore the
; default bank selection through the shared helper's tail call.
ApplyNmiPpuState:
    lda $03B8
    bne ApplyNmiPpuCtrl
    lda $03FC
    sta PPUSCROLL
    lda $03FD
    sta PPUSCROLL
    lda $03FE
    sta PPUMASK
    jmp ApplyNmiPpuCtrl
ApplyNmiPpuCtrl:
    lda $03FF
    and #$E7                    ; CONTROL_APPLY_PPU
    ora $03BD
    sta $03FF
    sta PPUCTRL
    jmp RestoreDefaultBank
.assert (* - BankStart) = $044B, error, "bank 0 NMI PPU state size"

; Start a voice by index A at command pointer Y:X. Invalid or already-active
; indices return early. An available record receives matching start/current
; pointers, a one-frame timer, cleared state, and initial flags $C0.
StartAudioVoice:
    stx $FE                      ; CONTROL_START_AUDIO_VOICE
    sty $FF
    jsr AudioVoiceOffset
    beq StartAudioVoiceCheck
    rts
StartAudioVoiceCheck:
    lda $04B0,x                  ; CONTROL_START_AUDIO_VOICE_CHECK
    bpl StartAudioVoiceInitialize
    lda #$01
    rts
StartAudioVoiceInitialize:
    lda #$01                     ; CONTROL_START_AUDIO_VOICE_INITIALIZE
    sta $04B1,x
    lda #$00
    sta $04B6,x
    sta $04B7,x
    lda $FE
    sta $04B2,x
    sta $04B4,x
    lda $FF
    sta $04B3,x
    sta $04B5,x
    lda #$C0
    sta $04B0,x
    rts
.assert (* - BankStart) = $0480, error, "bank 0 audio voice start end"

; Clear five eight-byte voice entries in the $04B0 state array.
InitializeAudioVoices:
    lda #$00
    sta $03FB
    tax
ClearAudioVoiceBytes:
    sta $04B0,x
    inx
    cpx #$28                     ; CONTROL_SLOT_INIT
    bne ClearAudioVoiceBytes
    rts
.assert (* - BankStart) = $048F, error, "bank 0 engine slot initializer size"

; A=$FF stops each voice until the first invalid index; other values select a
; voice index. The validated entry below also serves calls from audio commands.
StopAudioVoice:
    cmp #$FF                     ; CONTROL_STOP_AUDIO_VOICE
    bne StopAudioVoiceByIndex
StopAllAudioVoices:
    lda #$00
StopAudioVoiceAllLoop:
    pha
    jsr StopAudioVoice
    bne StopAudioVoiceAllDone
    pla
    clc
    adc #$01
    jmp StopAudioVoiceAllLoop
StopAudioVoiceAllDone:
    pla
    lda #$00
    rts
StopAudioVoiceByIndex:
    jsr AudioVoiceOffset         ; CONTROL_STOP_AUDIO_VOICE_BY_INDEX
    beq StopAudioVoiceOffset
    rts
; X is a voice record offset. Inactive records do nothing; a shadowed voice
; clears its record without changing the hardware channel.
StopAudioVoiceOffset:
    lda $04B0,x                  ; CONTROL_STOP_AUDIO_VOICE_OFFSET
    bpl StopAudioVoiceReturn
    tay
    and #$60
    beq StopAudioOwnedVoice
    lda #$00
    sta $04B0,x
    jmp StopAudioVoiceReturn
; Stop the owned channel, then find the first shadowed voice on that channel
; and restore its instrument, enable bit and ownership flag.
StopAudioOwnedVoice:
    jsr RestartAudioVoiceChannel ; CONTROL_STOP_AUDIO_OWNED_VOICE
    lda $04B0,x
    pha
    lda #$00
    sta $04B0,x
    pla
    and #$1F
    sta $FE
    cmp #$1F
    beq StopAudioVoiceReturn
    ldx #$00
StopAudioFindShadow:
    txa                          ; CONTROL_STOP_AUDIO_FIND_SHADOW
    pha
    lda $04B0,x
    bpl StopAudioNextShadow
    and #$20
    beq StopAudioNextShadow
    lda $04B0,x
    and #$1F
    eor $FE
    bne StopAudioNextShadow
    pla
    jsr WriteAudioVoiceInstrument
    jsr EnableAudioVoiceChannel
    lda $04B0,x
    and #$DF
    sta $04B0,x
    jmp StopAudioVoiceReturn
StopAudioNextShadow:
    pla
    clc
    adc #$08
    tax
    cmp #$28
    bcc StopAudioFindShadow
StopAudioVoiceReturn:
    lda #$00
    rts
; A valid active index returns 1; an inactive index returns 0. Invalid indices
; preserve the $FF error from AudioVoiceOffset.
IsAudioVoiceActive:
    jsr AudioVoiceOffset         ; CONTROL_IS_AUDIO_VOICE_ACTIVE
    bne AudioVoiceActiveReturn
    lda $04B0,x
    bmi AudioVoiceIsActive
    lda #$00
AudioVoiceActiveReturn:
    rts
AudioVoiceIsActive:
    lda #$01
    rts
.assert (* - BankStart) = $0517, error, "bank 0 audio voice stop and query end"

; Install map pointer Y:X, read its dimensions and draw the initial visible
; columns. Each column is flushed to the PPU before advancing the tile X index.
; A zero-width header starts the original 8-bit loop at zero, giving 256 passes.
InitializeMapDrawing:
    jsr PrepareDirectPpuWrites   ; CONTROL_INITIALIZE_MAP_DRAWING
    stx $F4
    sty $F5
    jsr ReadMapDimensions
    lda #$FF
    sta $03A4
    jsr FlushPpuUpdates
    jsr ClampScrollTargets
    jsr SetInitialMapTilePosition
    ldx #$21
    lda $039F
    bne InitialMapColumnLoop
    cpx $039E
    bcc InitialMapColumnLoop
    ldx $039E
InitialMapColumnLoop:
    txa                          ; CONTROL_INITIAL_MAP_COLUMN_LOOP
    pha
    jsr ResolveMapChunk
    jsr QueueMapTileColumn
    jsr FlushPpuUpdates
    lda $039A
    clc
    adc #$01
    sta $039A
    bcc InitialMapColumnAdvanceDone
    inc $039B
InitialMapColumnAdvanceDone:
    pla
    tax
    dex
    bne InitialMapColumnLoop
; Synchronize current scroll coordinates to the clamped targets and prepare
; the PPU scroll mirrors before saving the map workspace.
    lda $03EE                    ; CONTROL_INITIAL_MAP_SYNC_SCROLL
    sta $03F3
    lda $03EF
    sta $03F4
    lda $03F0
    sta $03F5
    lda $03F1
    sta $03F6
    jsr UpdatePpuScrollMirror
; Save map pointer and chunk workspace for later use. Fall through to the
; existing PPU NMI enable routine exactly as the original does.
    lda $EC                      ; CONTROL_INITIAL_MAP_SAVE_WORKSPACE
    sta $03AC
    lda $ED
    sta $03AD
    lda $EE
    sta $03AE
    lda $EF
    sta $03AF
    lda $F0
    sta $03B0
    lda $F1
    sta $03B1
    lda $F2
    sta $03B2
    lda $F3
    sta $03B3
    lda $03F7
    sta $03B4
    lda $03F8
    sta $03B5
    lda $03F9
    sta $03B6
    lda $03FA
    sta $03B7
.assert (* - BankStart) = $05B7, error, "bank 0 initial map drawing end"
; Writes the PPUCTRL mirror with the NMI bit set; the mirror itself is not
; updated here. This routine is a shared tail return from the NMI frame work.
EnablePpuNmi:
    lda $03FF
    ora #$80                     ; CONTROL_ENABLE_NMI
    sta PPUCTRL
    rts
.assert (* - BankStart) = $05C0, error, "bank 0 NMI enable routine size"

; Restore the PPU control mirror, wait for vblank and write mask $06 before
; direct PPU writes. Precise hardware timing remains to be verified.
PrepareDirectPpuWrites:
    jsr RestorePpuCtrl           ; CONTROL_PREPARE_DIRECT_PPU_WRITES
    jsr WaitVBlank
    lda #$06
    sta PPUMASK
    rts
; Convert the target pixel coordinates to tile coordinates for initial drawing.
SetInitialMapTilePosition:
    ldx $03EE                    ; CONTROL_SET_INITIAL_MAP_TILE_POSITION
    ldy $03EF
    jsr ShiftXYRight3
    sty $039B
    stx $039A
    ldx $03F0
    ldy $03F1
    jsr ShiftXYRight3
    stx $039C
    rts
; The two-byte map header gives width and height in eight-tile units. Compute
; the tile dimensions and the scroll bounds, then advance F4/F5 past it.
ReadMapDimensions:
    lda $F4                      ; CONTROL_READ_MAP_DIMENSIONS
    sta $FE
    lda $F5
    sta $FF
    jsr ReadBankedPointer
    lda $FE
    sta $03AA
    tay
    ldx #$08
    jsr MultiplyUnsigned8
    stx $039E
    sty $039F
    txa
    sec
    sbc #$20
    sta $03A0
    sta $03A2
    tya
    sbc #$00
    sta $03A1
    sta $03A3
    asl $03A2
    rol $03A3
    asl $03A2
    rol $03A3
    asl $03A2
    rol $03A3
; Height uses the low byte of height*8. A height smaller than 30 tiles
; produces a zero vertical bound, as in the original.
    lda $FF                      ; CONTROL_READ_MAP_HEIGHT
    tay
    ldx #$08
    jsr MultiplyUnsigned8
    stx $0396
    txa
    sec
    sbc #$1E
    bcs MapHeightBoundReady
    lda #$00
MapHeightBoundReady:
    sta $0399
    sta $03A8
    lda #$00
    sta $03A9
    asl $03A8
    rol $03A9
    asl $03A8
    rol $03A9
    asl $03A8
    rol $03A9
    lda $F4                      ; CONTROL_ADVANCE_MAP_HEADER
    clc
    adc #$02
    sta $F4
    lda $F5
    adc #$00
    sta $F5
    rts
; Move the current map index by two bytes, with 16-bit carry or borrow.
AdvanceMapIndexTwo:
    lda $EC                      ; CONTROL_ADVANCE_MAP_INDEX_TWO
    clc
    adc #$02
    sta $EC
    bcc AdvanceMapIndexTwoReturn
    inc $ED
AdvanceMapIndexTwoReturn:
    rts
RetreatMapIndexTwo:
    lda $EC                      ; CONTROL_RETREAT_MAP_INDEX_TWO
    sec
    sbc #$02
    sta $EC
    bcs RetreatMapIndexTwoReturn
    dec $ED
RetreatMapIndexTwoReturn:
    rts
.assert (* - BankStart) = $067F, error, "bank 0 map setup and index helpers end"
; Copy two bytes from the banked pointer in $FE/$FF onto the stack, install
; those bytes as the new pointer, and restore the previous $03E0 count.
ReadBankedPointer:
    lda $03E0                     ; CONTROL_READ_BANKED_POINTER
    pha
    pha
    pha
    lda #$02
    sta $03E0
    jsr CopyToStack
    tsx
    lda $0101,x
    sta $FE
    lda $0102,x
    sta $FF
    pla
    pla
    pla
    sta $03E0
    rts

; Compute a table index from the high portions of $039A/$039B and $039C,
; retaining the low three bits of $039A in $03DF for the map query.
ResolveMapChunk:
    lda $039A                     ; CONTROL_RESOLVE_MAP_CHUNK
    sta $EC
    lda $039B
    lsr a
    ror $EC
    lsr a
    ror $EC
    lsr a
    ror $EC
    lda $039C
    lsr a
    lsr a
    lsr a
    tax
    ldy $03AA
    jsr MultiplyUnsigned8
    lda $EC
    jsr AddAToXY
    stx $EC
    sty $ED
    lda $EC
    clc
    adc $F4
    sta $EC
    lda $F5
    adc $ED
    sta $ED
    lda $039A
    and #$07
    sta $03DF
    jmp LoadMapChunkPointer

; Preserve $FE/$FF while fetching a pointer through the table at $A1DE.
; The $F3 update uses the existing $F3 value, matching the original bytes.
LoadMapChunkPointer:
    lda $FE                       ; CONTROL_LOAD_MAP_CHUNK_POINTER
    pha
    lda $FF
    pha
    lda $EC
    sta $FE
    lda $ED
    sta $FF
    jsr ReadBankedPointer
    ldy #$00
    lda $FE
    sta $F0
    sty $F1
    asl $F0
    rol $F1
    lda #<MapChunkOffsets
    clc
    adc $F0
    sta $F0
    lda #>MapChunkOffsets
    adc $F1
    sta $F1
    lda ($F0),y
    pha
    iny
    lda ($F0),y
    sta $F1
    pla
    sta $F0
    lda #$08
    sta $03F8
    sta $03F9
    lda $F0
    clc
    adc #$40
    sta $F2
    lda $F3
    adc #$00
    sta $F3
    pla
    sta $FF
    pla
    sta $FE
    rts
.assert (* - BankStart) = $072F, error, "bank 0 map chunk helper end"

; Queue horizontal or vertical scroll work only while a map is active.
RequestHorizontalScroll:
    lda #$01                     ; CONTROL_REQUEST_HORIZONTAL_SCROLL
RequestScrollBits:
    ldx $03A4
    beq RequestScrollReturn
    ora $03EB
    sta $03EB
RequestScrollReturn:
    rts
RequestVerticalScroll:
    lda #$02                     ; CONTROL_REQUEST_VERTICAL_SCROLL
    jmp RequestScrollBits
; Install the two palette-stream pointers and set their pending setup bits.
SetBackgroundPaletteStream:
    stx $F8                      ; CONTROL_SET_BACKGROUND_PALETTE_STREAM
    sty $F9
    lda #$01
    jmp SetPaletteStreamPending
SetSpritePaletteStream:
    stx $FA                      ; CONTROL_SET_SPRITE_PALETTE_STREAM
    sty $FB
    lda #$02
SetPaletteStreamPending:
    ora $0387
    sta $0387
    rts
; Rotate up to $20 bytes of shadow OAM to the end of its $FC-byte region.
; The flags select whether rotation is needed; reserve stack space and hold
; $03F2 nonzero during the operation.
RotateShadowOam:
    lda $03AB                    ; CONTROL_ROTATE_SHADOW_OAM
    bne RotateShadowOamStart
    lda $03ED
    beq RotateShadowOamSkip
    lda $0381
    bne RotateShadowOamStart
RotateShadowOamSkip:
    jmp RotateShadowOamDone
RotateShadowOamStart:
    lda #$FF                     ; CONTROL_ROTATE_SHADOW_OAM_START
    sta $03F2
    tsx
    txa
    sec
    sbc #$20
    tax
    txs
    inx
    stx $FF
    lda $03AB
    beq RotateShadowOamMaximum
    cmp #$20
    bcc RotateShadowOamSaveCount
RotateShadowOamMaximum:
    lda #$20
RotateShadowOamSaveCount:
    sta $FE
    sta $03E0
    ldy #$00
RotateShadowOamSave:
    lda $0204,y
    sta $0100,x
    iny
    inx
    dec $FE
    bne RotateShadowOamSave
; Move the remaining bytes down and append the saved prefix from the stack.
    ldx #$00                     ; CONTROL_ROTATE_SHADOW_OAM_MOVE
    lda #$FC
    sec
    sbc $03E0
    sta $FE
RotateShadowOamMove:
    lda $0204,y
    sta $0204,x
    iny
    inx
    dec $FE
    bne RotateShadowOamMove
    lda $03E0
    sta $FE
    ldy $FF
RotateShadowOamAppend:
    lda $0100,y
    sta $0204,x
    iny
    inx
    dec $FE
    bne RotateShadowOamAppend
; Adjust all sixteen record offsets and $03AB, skipping the reserved $FC
; entry on borrow, then restore the original stack pointer and clear $03F2.
    lda #$10                     ; CONTROL_ROTATE_SHADOW_OAM_RECORDS
    sta $FE
    ldx #$00
RotateShadowOamRecordLoop:
    lda $0404,x
    sec
    sbc $03E0
    bcs RotateShadowOamRecordStore
    sec
    sbc #$04
RotateShadowOamRecordStore:
    sta $0404,x
    txa
    clc
    adc #$0B
    tax
    dec $FE
    bne RotateShadowOamRecordLoop
    lda $03AB
    sec
    sbc $03E0
    bcs RotateShadowOamStoreOffset
    sec
    sbc #$04
RotateShadowOamStoreOffset:
    sta $03AB
    tsx
    txa
    clc
    adc #$20
    tax
    txs
RotateShadowOamDone:
    lda #$00                     ; CONTROL_ROTATE_SHADOW_OAM_DONE
    sta $03F2
    rts
.assert (* - BankStart) = $07FA, error, "bank 0 scroll, palette and OAM controls end"

; Allocate sprite record A with data pointer Y:X. Reject invalid or occupied
; records; an initial $4F byte returns success without claiming the record.
AllocateSpriteRecord:
    stx $FE                      ; CONTROL_ALLOCATE_SPRITE_RECORD
    sty $FF
    jsr SlotRecordOffset
    beq AllocateSpriteRecordCheck
    rts
AllocateSpriteRecordCheck:
    lda $0400,x                  ; CONTROL_ALLOCATE_SPRITE_RECORD_CHECK
    beq AllocateSpriteRecordPointer
    lda #$01
    rts
AllocateSpriteRecordPointer:
    lda $FE                      ; CONTROL_ALLOCATE_SPRITE_RECORD_POINTER
    sta $0402,x
    lda $FF
    sta $0403,x
    lda $0401,x
    and #$C0
    sta $0401,x
    ldy #$00
    lda ($FE),y
    cmp #$4F
    bne AllocateSpriteRecordMode
    lda #$00
    rts
; Header $53 selects indexed frames and initializes their timer; other
; headers select the direct frame. $0404 temporarily holds the record flags.
AllocateSpriteRecordMode:
    cmp #$53                     ; CONTROL_ALLOCATE_SPRITE_RECORD_MODE
    beq AllocateSpriteAnimated
    lda #$C1
    sta $0404,x
    jmp AllocateSpriteFindSpace
AllocateSpriteAnimated:
    lda #$82                     ; CONTROL_ALLOCATE_SPRITE_ANIMATED
    sta $0404,x
    lda #$00
    sta $0406,x
    ldy #$02
    lda ($FE),y
    sta $0407,x
    sta $0408,x
    iny
    lda ($FE),y
    iny
    pha
    lda ($FE),y
    sta $FF
    pla
    sta $FE
; Compute the number of tiles from the packed dimensions. Search the OAM
; attribute bytes for a consecutive free range, skipping offset $FC.
AllocateSpriteFindSpace:
    lda $040A,x                  ; CONTROL_ALLOCATE_SPRITE_FIND_SPACE
    sta $04DC
    txa
    pha
    ldy #$01
    lda ($FE),y
    lsr a
    lsr a
    lsr a
    lsr a
    tax
    lda ($FE),y
    and #$0F
    tay
    jsr MultiplyUnsigned8
    stx $03E3
    ldy #$00
    lda ($FE),y
    and #$7F
    asl a
    asl a
    clc
    adc $03AB
    bcs AllocateSpriteSkipReserved
    cmp #$FC
    bne AllocateSpriteSearchStart
AllocateSpriteSkipReserved:
    clc
    adc #$04
AllocateSpriteSearchStart:
    sta $03E2
    tay
AllocateSpriteSearchCandidate:
    ldx $04DC                    ; CONTROL_ALLOCATE_SPRITE_SEARCH
    bne AllocateSpriteSearchCount
    ldx $03E3
AllocateSpriteSearchCount:
    sty $03E0
AllocateSpriteSearchSlot:
    lda $0206,y
    sta $03E1
AllocateSpriteNextSlot:
    iny
    iny
    iny
    iny
    cpy #$FC
    beq AllocateSpriteNextSlot
    tya
    eor $03E2
    beq AllocateSpriteNoSpace
    lda $03E1
    and #$08
    bne AllocateSpriteSearchCandidate
    dex
    bne AllocateSpriteSearchSlot
    jmp AllocateSpriteClaim
AllocateSpriteNoSpace:
    pla
    lda #$02
    rts
; Save the range and optionally reserve the requested number of OAM entries.
; Commit the temporary mode flags, update the PPU sprite-size mirror, and
; load tile/attribute data for the first frame.
AllocateSpriteClaim:
    ldy $03E0                    ; CONTROL_ALLOCATE_SPRITE_CLAIM
    pla
    tax
    lda $03E3
    sta $0405,x
    lda $0404,x
    sta $03E0
    tya
    sta $0404,x
    lda $04DC
    beq AllocateSpriteSize
    lda #$08
AllocateSpriteReserve:
    sta $0206,y
AllocateSpriteReserveNext:
    iny
    iny
    iny
    iny
    cpy #$FC
    beq AllocateSpriteReserveNext
    dec $04DC
    bne AllocateSpriteReserve
AllocateSpriteSize:
    lda $03FF                    ; CONTROL_ALLOCATE_SPRITE_SIZE
    and #$DF
    ldy #$00
    pha
    lda ($FE),y
    asl a
    pla
    bcc AllocateSpriteSizeStore
    ora #$20
AllocateSpriteSizeStore:
    sta $03FF
    and #$20
    sta $0397
    lda $03E0
    sta $0400,x
    jsr LoadSpriteFrame
    lda #$00
    rts
.assert (* - BankStart) = $090A, error, "bank 0 sprite record allocation end"
; Resolve the indexed slot record, save the supplied coordinates and examine
; its low mode bits. Mode zero returns 1; mode three returns 0 immediately.
PlaceSlotSprites:
    stx $03E0                     ; CONTROL_PLACE_SLOT_SPRITES
    sty $03E1
    jsr SlotRecordOffset
    beq PlaceSlotValid
    rts
PlaceSlotValid:
    lda $0402,x
    sta $FE
    lda $0403,x
    sta $FF
    lda $0400,x
    and #$7F
    sta $0400,x
    and #$03
    beq PlaceSlotModeZero
    cmp #$03
    bne PlaceSlotSelectRecord
    lda #$00
    rts
PlaceSlotSelectRecord:
    cmp #$01
    beq PlaceSlotReadSize
    ldy #$01
    lda ($FE),y
    sta $03DE
    ldy #$03
    lda ($FE),y
    pha
    iny
    lda ($FE),y
    sta $FF
    pla
    sta $FE
    jmp PlaceSlotReadSize
PlaceSlotModeZero:
    lda #$01
    rts

; Read the packed dimensions, determine an 8- or 16-unit row height, and
; seed the OAM buffer offset from the slot record's $0404 byte.
PlaceSlotReadSize:
    lda $03E1                     ; CONTROL_PLACE_SLOT_SIZE
    clc
    adc $03EC
    sta $03E1
    ldy #$00
    lda ($FE),y
    pha
    iny
    lda ($FE),y
    lsr a
    lsr a
    lsr a
    lsr a
    pha
    lda ($FE),y
    and #$0F
    sta $FF
    pla
    sta $FE
    ldy $0404,x
    lda #$08
    sta $03E2
    pla
    bpl PlaceSlotRows
    lda #$10
    sta $03E2

; Update sprite Y/X positions in the OAM buffer. The $FC skip and the
; saturation of each coordinate are original behavior, not timing evidence.
PlaceSlotRows:
    lda $FE                       ; CONTROL_PLACE_SLOT_ROWS
    sta $03E3
    lda $03E0
    pha
PlaceSlotColumn:
    lda $03E1
    sta $0204,y
    lda $03E0
    sta $0207,y
    clc
    adc #$08
    bcc PlaceSlotColumnXReady
    lda #$FF
PlaceSlotColumnXReady:
    sta $03E0
PlaceSlotNextOam:
    iny
    iny
    iny
    iny
    cpy #$FC
    beq PlaceSlotNextOam
    dec $03E3
    bne PlaceSlotColumn
    pla
    sta $03E0
    lda $03E1
    clc
    adc $03E2
    bcs PlaceSlotYMaximum
    cmp #$F9
    bcc PlaceSlotYReady
PlaceSlotYMaximum:
    lda #$F8
PlaceSlotYReady:
    sta $03E1
    dec $FF
    bne PlaceSlotRows

; For eligible modes, derive a value from a positioned sprite and the slot
; record; LoadSpriteFrame consumes the value if it changed.
PlaceSlotEvaluate:
    lda $0400,x                   ; CONTROL_PLACE_SLOT_EVALUATE
    and #$70
    beq PlaceSlotSuccess
    cmp #$40
    bcs PlaceSlotSuccess
    lda $0400,x
    and #$03
    cmp #$01
    beq PlaceSlotSuccess
    lda $0400,x
    rol a
    rol a
    rol a
    ldy $0404,x
    lda $03F0
    sta $03E0
    lda $0204,y
    bcc PlaceSlotSelectCoordinate
    lda $03EE
    sta $03E0
    lda $0207,y
PlaceSlotSelectCoordinate:
    clc
    adc $03E0
    sta $03E0
    lda $0401,x
    and #$07
    tay
    iny
PlaceSlotShiftCoordinate:
    dey
    beq PlaceSlotDivide
    lsr $03E0
    jmp PlaceSlotShiftCoordinate
PlaceSlotDivide:
    stx $03E1                     ; CONTROL_PLACE_SLOT_DIVIDE
    ldx $03E0
    ldy #$00
    lda $03DE
    jsr DivideUnsigned16By8
    ldx $03E1
    lda $0400,x
    and #$20
    beq PlaceSlotStoreResult
    lda $0401,x
    and #$40
    beq PlaceSlotStoreResult
    lda $03DE
    sty $03DE
    clc                           ; Original SBC includes an extra borrow.
    sbc $03DE
    tay
PlaceSlotStoreResult:
    tya
    ldy $0406,x
    sta $0406,x
    tya
    eor $0406,x
    beq PlaceSlotSuccess
    jsr LoadSpriteFrame
PlaceSlotSuccess:
    lda #$00
    rts
.assert (* - BankStart) = $0A4C, error, "bank 0 slot sprite placement end"


; The slot query records candidate coordinates and validates its slot record.
; A missing bit $08 returns zero without inspecting the map.
QuerySlotAtPosition:
    stx $03A6                     ; CONTROL_SLOT_QUERY_ENTRY
    sty $03A7
    jsr RequireSlotRecord
    stx $03DE
    and #$08
    bne SlotQueryPrepare
    lda #$00
    rts

; Resolve the record's graphics/data pointer, optionally following the pair
; at offsets 3-4. The record's packed byte supplies the query dimensions.
SlotQueryPrepare:
    lda $03A6                     ; CONTROL_SLOT_QUERY_PREPARE
    sta $03E2
    lda $03A7
    sta $03E5
    lda $03E2
    clc
    adc $03EE
    sta $039A
    lda $03EF
    adc #$00
    sta $039B
    lda $0402,x
    sta $FE
    lda $0403,x
    sta $FF
    lda $0400,x
    and #$03
    cmp #$01
    beq SlotQueryDimensions
    ldy #$03
    lda ($FE),y
    pha
    iny
    lda ($FE),y
    sta $FF
    pla
    sta $FE
SlotQueryDimensions:
    ldy #$01
    lda ($FE),y
    lsr a
    lsr a
    lsr a
    lsr a
    sta $03E2
    dec $03E2
    bne SlotQueryAdjustFirst
    inc $03E2
    jmp SlotQuerySecondDimension
SlotQueryAdjustFirst:
    lda $039A
    clc
    adc #$04
    sta $039A
    lda $039B
    adc #$00
    sta $039B

; Transform the second dimension and coordinates into eight-unit values.
; Keep the carry chain through the repeated shifts and rotates intact.
SlotQuerySecondDimension:
    lda ($FE),y                   ; CONTROL_SLOT_QUERY_COORDINATES
    and #$0F
    sta $03E3
    ldy #$00
    lda ($FE),y
    bpl SlotQueryScaleSecond
    asl $03E3
SlotQueryScaleSecond:
    lda $03E3
    jsr ShiftALeft3
    dec $03E5
    clc
    adc $03E5
    clc
    adc $03F0
    sta $03E5
    lda #$00
    adc $03F1
    lsr a
    ror $03E5
    lsr a
    ror $03E5
    lsr a
    ror $03E5
    lda $03E5
    sta $039C
    lsr $039B
    ror $039A
    ror $03E1
    lsr $039B
    ror $039A
    ror $03E1
    lsr $039B
    ror $039A
    ror $03E1
    cmp $0396
    bcc SlotQuerySpan
    lda #$00
    rts

; Clip the query span against the 16-bit $039E/$039F boundary. A wrapped or
; empty span selects the preceding position and one unit instead.
SlotQueryPrevious:
    lda $039E                     ; CONTROL_SLOT_QUERY_SPAN
    sec
    sbc #$01
    sta $039A
    lda $039F
    sbc #$00
    sta $039B
    lda #$01
    sta $03E1
    jmp SlotQueryReserveStack
SlotQuerySpan:
    lda $03E1
    and #$E0
    beq SlotQuerySpanSize
    inc $03E2
SlotQuerySpanSize:
    lda $03E2
    sta $03E1
    lda $039E
    sec
    sbc $039A
    tay
    lda $039F
    sbc $039B
    bcc SlotQueryPrevious
    bne SlotQueryReserveStack
    cpy $03E1
    beq SlotQueryClipSpan
    bcs SlotQueryReserveStack
SlotQueryClipSpan:
    sty $03E1
    cpy #$00
    beq SlotQueryPrevious

; Reserve 17 stack bytes, obtain map data in pieces through CopyToStack, and
; compare it with the slot record's $0409 threshold. Restore SP on both paths.
SlotQueryReserveStack:
    tsx                           ; CONTROL_SLOT_QUERY_STACK
    txa
    sec
    sbc #$11
    tax
    txs
SlotQueryChunk:
    jsr ResolveMapChunk
    lda $03F8
    sec
    sbc $03DF
    sta $03E0
    lda $03E1
    sec
    sbc $03E0
    bcs SlotQueryChunkSize
    lda #$00
SlotQueryChunkSize:
    sta $03E0
    tax
    lda $03E1
    sec
    sbc $03E0
    sta $03E0
    stx $03E1
    clc
    adc $039A
    sta $039A
    bcc SlotQueryChunkAddress
    inc $039B
SlotQueryChunkAddress:
    lda $039C                     ; CONTROL_SLOT_QUERY_ADDRESS
    and #$07
    asl a
    asl a
    asl a
    tax
    ldy #$00
    lda $03DF
    jsr AddAToXY
    txa
    clc
    adc $F0
    sta $FE
    tya
    adc $F1
    sta $FF
    lda $03E0
    sta $03DF
    jsr CopyToStack
    ldy $03DF
    ldx $03DE
    lda $0409,x
    sta $03DF
    tsx
    inx
SlotQueryCompare:
    lda $0100,x                   ; CONTROL_SLOT_QUERY_COMPARE
    inx
    cmp $03DF
    bcs SlotQueryHit
    dey
    bne SlotQueryCompare
    lda $03E1
    bne SlotQueryChunk
    lda #$00
    jmp SlotQueryReleaseStack
SlotQueryHit:
    sta $03A5
    lda #$04
SlotQueryReleaseStack:
    sta $03E0
    tsx
    txa
    clc
    adc #$11
    tax
    txs
    lda $03E0
    rts
.assert (* - BankStart) = $0C03, error, "bank 0 slot query end"

; This related map read computes a single position, copies one byte to the
; reserved stack location, and returns it in A. Its caller provides the stack.
ReadMapByteAtPosition:
    lda $03A6                     ; CONTROL_READ_MAP_BYTE
    clc
    adc $03EE
    sta $039A
    lda $03EF
    adc #$00
    lsr a
    ror $039A
    lsr a
    ror $039A
    lsr a
    ror $039A
    sta $039B
    lda $03A7
    clc
    adc $03F0
    sta $039C
    lda #$00
    adc $03F1
    lsr a
    ror $039C
    lsr a
    ror $039C
    lsr a
    ror $039C
    jsr ResolveMapChunk
    lda $039C
    and #$07
    asl a
    asl a
    asl a
    tax
    ldy #$00
    lda $03DF
    jsr AddAToXY
    txa
    clc
    adc $F0
    sta $FE
    tya
    adc $F1
    sta $FF
    lda #$01
    sta $03E0
    pha
    jsr CopyToStack
    pla
    rts

; Clear all sixteen eleven-byte $0400 records.
ClearSlotRecords:
    lda #$00                      ; CONTROL_CLEAR_SLOT_RECORDS
    tax
ClearSlotRecordsLoop:
    sta $0400,x
    inx
    cpx #$B0
    bne ClearSlotRecordsLoop
    rts
.assert (* - BankStart) = $0C72, error, "bank 0 map query helpers end"

; Release one indexed $0400 record and hide its allocated shadow sprites.
; Index $FF iterates records until SlotRecordOffset reports out of range.
ReleaseSpriteRecord:
    cmp #$FF                      ; CONTROL_RELEASE_SPRITE_RECORD
    bne ReleaseSpriteRecordOne
ReleaseAllSpriteRecords:
    lda #$00
ReleaseSpriteRecordAllLoop:
    pha
    jsr ReleaseSpriteRecord
    bne ReleaseSpriteRecordAllDone
    pla
    clc
    adc #$01
    jmp ReleaseSpriteRecordAllLoop
ReleaseSpriteRecordAllDone:
    pla
    lda #$00
    rts
ReleaseSpriteRecordOne:
    jsr SlotRecordOffset
    bne ReleaseSpriteRecordReturn
    lda $0400,x
    pha
    lda #$00
    sta $0400,x
    pla
    and #$03
    beq ReleaseSpriteRecordReturn
    cmp #$03
    beq ReleaseSpriteRecordReturn
    txa
    pha
    lda $0404,x
    tay
    lda $040A,x
    bne ReleaseSpriteCountReady
    lda $0405,x
ReleaseSpriteCountReady:
    tax
    jsr InitializeNextSprite
    pla
    tax
    lda #$00
ReleaseSpriteRecordReturn:
    rts

; For record modes 1 or 2, update the $20 attribute bit over its OAM range.
; The $FC OAM offset skip is the same as the other shadow-sprite loops.
UpdateSpriteAttribute20:
    stx $FE                       ; CONTROL_UPDATE_SPRITE_ATTRIBUTE20
    jsr SlotRecordOffset
    bne UpdateSpriteAttributeReturn
    lda $0400,x
    and #$03
    cmp #$01
    beq UpdateSpriteAttributeStart
    cmp #$02
    beq UpdateSpriteAttributeStart
    lda #$01
UpdateSpriteAttributeReturn:
    rts
UpdateSpriteAttributeStart:
    ldy $0404,x
    lda $0405,x
    tax
UpdateSpriteAttributeLoop:
    lda $0206,y
    and #$DF
    eor $FE
    sta $0206,y
UpdateSpriteAttributeNext:
    iny
    iny
    iny
    iny
    cpy #$FC
    beq UpdateSpriteAttributeNext
    dex
    bne UpdateSpriteAttributeLoop
    lda #$00
    rts

; Update mode bits in $0400 and the low three bits of $0401 after validation.
SetSpriteRecordMode:
    stx $03E0                     ; CONTROL_SET_SPRITE_RECORD_MODE
    sty $03E1
    jsr RequireSlotRecord
    and #$CF
    ora $03E0
    sta $0400,x
    lda $03E1
    and #$07
    sta $03E1
    lda $0401,x
    and #$F8
    ora $03E1
    sta $0401,x
    lda #$00
    rts
SetSpriteRecordQueryValue:
    stx $03E0                     ; CONTROL_SET_SPRITE_QUERY_VALUE
    jsr RequireSlotRecord
    lda $03E0
    sta $0409,x
    lda $0400,x
    ora #$08
    ldy $03E0
    bne SetSpriteQueryStore
    eor #$08
SetSpriteQueryStore:
    sta $0400,x
    lda #$00
    rts

; Set either high attribute bit in $0401. If the high bits changed, reload
; the sprite tile and attribute data into shadow OAM.
SetSpriteAttributeBit40:
    stx $03E0                     ; CONTROL_SET_SPRITE_BIT40
    jsr RequireSlotRecord
    lda $0401,x
    pha
    and #$BF
    ldy $03E0
    beq SetSpriteHighBits
    ora #$40
SetSpriteHighBits:
    sta $0401,x
    sta $03E0
    pla
    eor $03E0
    and #$C0
    beq SetSpriteHighBitsReturn
    jsr LoadSpriteFrame
SetSpriteHighBitsReturn:
    lda #$00
    rts
SetSpriteAttributeBit80:
    stx $03E0                     ; CONTROL_SET_SPRITE_BIT80
    jsr RequireSlotRecord
    lda $0401,x
    pha
    and #$7F
    ldy $03E0
    beq SetSpriteBit80Store
    ora #$80
SetSpriteBit80Store:
    jmp SetSpriteHighBits
SetSpriteRecordBit10:
    jsr RequireSlotRecord         ; CONTROL_SET_SPRITE_RECORD_BIT10
    lda $0401,x
    ora #$10
    sta $0401,x
    lda #$00
    rts
.assert (* - BankStart) = $0D7D, error, "bank 0 sprite record helpers end"


; Convert an index into an eleven-byte $0400 record, then store $04DC at its
; offset $0A. Out-of-range indices return without the store.
StoreSlotRecordField0A:
    jsr SlotRecordOffset         ; CONTROL_STORE_RECORD_FIELD_0A
    bne SlotRecordStoreReturn
    lda $04DC
    sta $040A,x
    lda #$00
SlotRecordStoreReturn:
    rts

; Look up a valid record's offset $06 and return it in X. The validation
; helper below may discard this routine's return address on failure.
GetSlotRecordField06:
    jsr RequireSlotRecord        ; CONTROL_GET_RECORD_FIELD_06
    lda $0406,x
    tax
    lda #$00
    rts

; Invalid indices and records with zero $0400 flags return early from the
; caller: the helper discards its caller's return address and returns the
; error in A. A nonzero record flag returns normally with its offset in X.
RequireSlotRecord:
    jsr SlotRecordOffset         ; CONTROL_REQUIRE_SLOT_RECORD
    bne SlotRecordAbortCaller
    lda $0400,x
    beq SlotRecordEmpty
    rts
SlotRecordEmpty:
    lda #$01
SlotRecordAbortCaller:
    tax
    pla
    pla
    txa
    rts

; Valid indices $00-$0F map to offsets index*11 in X; invalid values return
; $FF in A. The high multiplication byte is left in Y as in the original.
SlotRecordOffset:
    cmp #$10                     ; CONTROL_SLOT_RECORD_OFFSET
    bcs SlotRecordOffsetInvalid
    tax
    ldy #$0B
    jsr MultiplyUnsigned8
    lda #$00
    rts
SlotRecordOffsetInvalid:
    lda #$FF
    rts
.assert (* - BankStart) = $0DB7, error, "bank 0 slot record index helpers end"

; Load a record frame into shadow OAM. Mode 1 uses its pointer directly;
; other modes select a little-endian frame pointer from the indexed table.
; X is the record offset and is restored on return.
LoadSpriteFrame:
    txa ; CONTROL_LOAD_SPRITE_FRAME
    pha
    lda $0400,x
    and #$03
    cmp #$01
    bne SpriteFrameIndirect
    lda $0402,x
    sta $FE
    lda $0403,x
    sta $FF
    jmp SpriteFrameDimensions
SpriteFrameIndirect:
    lda $0406,x
    ldy #$00
    asl a
    bcc SpriteFramePointerOffset
    ldy #$01
SpriteFramePointerOffset:
    clc
    adc #$03
    bcc SpriteFramePointerBase
    iny
SpriteFramePointerBase:
    clc
    adc $0402,x
    sta $FE
    tya
    adc $0403,x
    sta $FF
    ldy #$00
    lda ($FE),y
    pha
    iny
    lda ($FE),y
    sta $FF
    pla
    sta $FE
; The frame header packs column and row counts in the high and low nibbles.
SpriteFrameDimensions:
    ldy #$01
    lda ($FE),y
    lsr a
    lsr a
    lsr a
    lsr a
    sta $03E2
    lda ($FE),y
    and #$0F
    sta $03E3
    iny
    lda $0401,x
    and #$C0
    sta $03E4
    bmi SpriteFrameFlipVertical
    and #$40
    bne SpriteFrameFlipHorizontal
; Select OAM traversal strides for the four combinations of the $40/$80
; attribute bits. Offset $FC is reserved and skipped on wrap or traversal.
    lda #$04    ; CONTROL_SPRITE_FRAME_FORWARD
    sta $03E0
    lda #$00
    sta $03E1
    sta $03DE
    lda $0404,x
SpriteFrameForwardStart:
    sec
    sbc #$04
    bcc SpriteFrameForwardStart
    tax
    jmp SpriteFrameNextRow
SpriteFrameFlipHorizontal:
    lda #$FC    ; CONTROL_SPRITE_FRAME_HORIZONTAL
    sta $03E0
    lda $03E2
    asl a
    asl a
    sta $03E5
    asl a
    sta $03E1
    lda #$00
    sta $03DE
    lda $03E5
    clc
    adc $0404,x
    bcs SpriteFrameHorizontalSkip
    cmp #$FC
    bne SpriteFrameHorizontalReady
SpriteFrameHorizontalSkip:
    clc
    adc #$04
SpriteFrameHorizontalReady:
    tax
    jmp SpriteFrameNextRow
SpriteFrameFlipVertical:
    and #$40    ; CONTROL_SPRITE_FRAME_VERTICAL
    bne SpriteFrameFlipBoth
    lda #$04
    sta $03E0
    lda $03E2
    asl a
    asl a
    sta $03E5
    asl a
    sta $03E1
    lda $0405,x
    asl a
    asl a
    sec
    sbc $03E5
    sec
    sbc #$04
    sta $03DE
    lda $0404,x
    clc
    adc $03DE
    bcs SpriteFrameVerticalSkip
    cmp #$FC
    bne SpriteFrameVerticalReady
SpriteFrameVerticalSkip:
    clc
    adc #$04
SpriteFrameVerticalReady:
    tax
    lda #$FF
    sta $03DE
    jmp SpriteFrameNextRow
SpriteFrameFlipBoth:
    lda #$FC    ; CONTROL_SPRITE_FRAME_BOTH
    sta $03E0
    lda #$00
    sta $03E1
    sta $03DE
    lda $0405,x
    asl a
    asl a
    clc
    adc $0404,x
    bcs SpriteFrameBothSkip
    cmp #$FC
    bne SpriteFrameBothReady
SpriteFrameBothSkip:
    clc
    adc #$04
SpriteFrameBothReady:
    tax
; Each entry supplies a tile and attributes. Keep the existing priority bit,
; set bit $08, and XOR the high flip bits from the record.
SpriteFrameNextRow:
    lda $03E2    ; CONTROL_SPRITE_FRAME_ROW
    sta $03E5
SpriteFrameNextTile:
    txa
    clc
    adc $03E0
    cmp #$FC
    bne SpriteFrameWriteTile
    clc
    adc $03E0
SpriteFrameWriteTile:
    tax
    lda ($FE),y
    sta $0205,x
    iny
    lda $0206,x
    and #$20
    ora #$08
    ora ($FE),y
    eor $03E4
    sta $0206,x
    iny
    dec $03E5
    bne SpriteFrameNextTile
    txa
    ldx $03DE
    bpl SpriteFrameAdvanceRow
    sec
    sbc $03E1
    bcs SpriteFrameRowReady
    sec
    sbc #$04
    jmp SpriteFrameRowReady
SpriteFrameAdvanceRow:
    clc
    adc $03E1
    bcs SpriteFrameRowSkip
    cmp #$FC
    bne SpriteFrameRowReady
SpriteFrameRowSkip:
    clc
    adc #$04
SpriteFrameRowReady:
    tax
    dec $03E3
    bne SpriteFrameNextRow
    pla
    tax
    rts
.assert (* - BankStart) = $0F10, error, "bank 0 sprite frame loading end"

; Advance animation timers in sixteen eleven-byte sprite records. Modes 0 and
; 1 do not advance. Bits $70 in the record flags also suppress advancement.
AdvanceSpriteAnimations:
    ldx #$00                     ; CONTROL_ADVANCE_SPRITE_ANIMATIONS
    ldy #$10
AdvanceSpriteAnimationLoop:
    tya
    pha
    lda $0400,x
    and #$03
    tay
    bne AdvanceSpriteAnimationActive
AdvanceSpriteAnimationNext:
    pla
    tay
    txa
    clc
    adc #$0B
    tax
    dey
    bne AdvanceSpriteAnimationLoop
    rts
AdvanceSpriteAnimationActive:
    tya                          ; CONTROL_ADVANCE_SPRITE_ANIMATION_ACTIVE
    cmp #$01
    beq AdvanceSpriteAnimationNext
    lda $0400,x
    and #$70
    beq AdvanceSpriteAnimationTick
    tya
    jmp AdvanceSpriteAnimationDone
AdvanceSpriteAnimationTick:
    dec $0407,x
    bne AdvanceSpriteAnimationDone
    tya
    cmp #$03
    bne AdvanceSpriteAnimationFrame
    lda $0405,x
    ora #$80
    sta $0405,x
; Reload the timer and advance the frame index. At the end, bit $10 chooses
; between looping to frame zero and holding the final frame with flag $40 set.
AdvanceSpriteAnimationFrame:
    lda $0408,x                  ; CONTROL_ADVANCE_SPRITE_ANIMATION_FRAME
    sta $0407,x
    lda $0402,x
    sta $F6
    lda $0403,x
    sta $F7
    inc $0406,x
    lda $0406,x
    ldy #$01
    cmp ($F6),y
    bne AdvanceSpriteAnimationLoad
    lda $0401,x
    and #$10
    beq AdvanceSpriteAnimationLoopFrame
    lda $0400,x
    ora #$40
    sta $0400,x
    dec $0406,x
    jmp AdvanceSpriteAnimationNext
AdvanceSpriteAnimationLoopFrame:
    lda #$00
    sta $0406,x
AdvanceSpriteAnimationLoad:
    lda $0400,x
    and #$03
    cmp #$02
    bne AdvanceSpriteAnimationDone
    jsr LoadSpriteFrame
AdvanceSpriteAnimationDone:
    jmp AdvanceSpriteAnimationNext
.assert (* - BankStart) = $0F90, error, "bank 0 sprite animation update end"

; Two APU register bytes per instrument for the 21-entry segment before code.
; The instrument command has five index bits; runtime bounds remain unverified.
AudioInstrumentPairs:
    .byte $C0, $00 ; CONTROL_AUDIO_INSTRUMENT_PAIRS
    .byte $C0, $00 ; index $01
    .byte $C0, $00 ; index $02
    .byte $80, $00 ; index $03
    .byte $80, $00 ; index $04
    .byte $80, $00 ; index $05
    .byte $00, $00 ; index $06
    .byte $00, $00 ; index $07
    .byte $00, $00 ; index $08
    .byte $80, $FF ; index $09
    .byte $80, $FF ; index $0A
    .byte $80, $FF ; index $0B
    .byte $00, $D6 ; index $0C
    .byte $00, $D6 ; index $0D
    .byte $00, $D6 ; index $0E
    .byte $40, $00 ; index $0F
    .byte $40, $00 ; index $10
    .byte $40, $00 ; index $11
    .byte $80, $C9 ; index $12
    .byte $80, $C9 ; index $13
    .byte $80, $C9 ; index $14
.assert (* - BankStart) = $0FBA, error, "bank 0 audio instrument pairs end"
; Reserve six stack bytes for a command buffer and visit five eight-byte voice
; records. A negative record flag marks an active voice; its timer is decremented.
UpdateAudioVoices:
    tsx                          ; CONTROL_UPDATE_AUDIO_VOICES
    txa
    sec
    sbc #$06
    tax
    txs
    inx
    stx $03DD
    ldx #$00
    stx $03E7
AudioVoiceLoop:
    lda $04B0,x
    bpl AudioNextVoice
    sta $03E7
    dec $04B1,x
    beq AudioReadCommand
AudioNextVoice:
    txa
    clc
    adc #$08
    tax
    cmp #$28
    bcc AudioVoiceLoop
    lda $03E7
    bne AudioUpdateReturn
    lda #$00
    sta $03FB
    sta $03E8
    sta $4015
AudioUpdateReturn:
    tsx
    txa
    clc
    adc #$06
    tax
    txs
    rts
; Copy five bytes from the voice command pointer into the stack buffer, then
; dispatch notes below $A0 and leave higher commands to the remaining handler.
AudioReadCommand:
    lda $04B4,x                  ; CONTROL_AUDIO_READ_COMMAND
    sta $FE
    lda $04B5,x
    sta $FF
    stx $03DC
    lda #$05
    sta $03E0
    jsr CopyToStack
    ldx $03DC
    ldy $03DD
    lda $0100,y
    and #$E0
    cmp #$A0
    bcs AudioHighCommand
    lda $0100,y
    jsr PrepareAudioNote
    bne AudioFinishNote
    lda $F6
    cmp #$1F
    beq AudioPresetNote
    lda $04B6,x
    asl a
    tay
    lda AudioPeriodPointers,y
    sta $F6
    lda AudioPeriodPointers+1,y
    sta $F7
    ldy $03DD
    lda $0100,y
    and #$1F
    cmp #$1F
    beq AudioFinishNote
    asl a
    tay
    lda ($F6),y
    sta $03E0
    iny
    lda ($F6),y
    sta $03E1
    jsr WriteAudioVoicePeriod
AudioFinishNote:
    jsr AdvanceAudioCommandOne   ; CONTROL_AUDIO_FINISH_NOTE
    jmp AudioNextVoice
; Special register-offset $1F uses five-byte presets, gated by $03FB. Keep
; both identical AND instructions: they are present in the original program.
AudioPresetNote:
    txa
    pha
    lda $0100,y
    and #$1F
    and #$1F
    cmp #$1F
    beq AudioPresetDone
    sta $03E1
    asl a
    asl a
    clc
    adc $03E1
    tax
    lda AudioSpecialPresets,x
    sta $F6
    inx
    jsr AudioOffsetChannelMask
    and $03FB
    bne AudioPresetDone
    ldy #$00
AudioPresetCopy:
    lda AudioSpecialPresets,x
    sta ($F6),y
    inx
    iny
    cpy #$04
    bne AudioPresetCopy
AudioPresetDone:
    pla
    tax
    jmp AudioFinishNote
; $A0-$BF select an instrument; other high commands continue below.
AudioHighCommand:
    cmp #$A0                     ; CONTROL_AUDIO_HIGH_COMMAND
    bne AudioOtherCommand
    lda $0100,y
    and #$1F
    sta $04B6,x
    lda $04B0,x
    and #$60
    bne AudioFinishControlCommand
    jsr WriteAudioVoiceInstrument
AudioFinishControlCommand:
    jsr AdvanceAudioCommandOne
    lda #$01
    sta $04B1,x
    jmp AudioNextVoice
.assert (* - BankStart) = $10B3, error, "bank 0 audio update dispatch end"

; $C0 repeats a command stream: initialize/decrement the loop counter, jump
; to the supplied pointer while nonzero, then skip its four-byte command.
AudioOtherCommand:
    lda $0100,y                   ; CONTROL_AUDIO_LOOP_COMMAND
    cmp #$C0
    bne AudioCommandMaskSet
    lda $04B7,x
    bne AudioLoopDecrement
    lda $0101,y
    sta $04B7,x
AudioLoopDecrement:
    dec $04B7,x
    beq AudioLoopFinished
    lda $0102,y
    sta $04B4,x
    lda $0103,y
    sta $04B5,x
    jmp AudioReadCommand
AudioLoopFinished:
    jsr AdvanceAudioCommandTwo
    jsr AdvanceAudioCommandTwo
    jmp AudioReadCommand
; $C2 and $C3 respectively set and clear the voice's channel bit in the
; $03FB mask used when copying the special five-byte note presets.
AudioCommandMaskSet:
    cmp #$C2                     ; CONTROL_AUDIO_COMMAND_MASK_SET
    bne AudioCommandMaskClear
    jsr AudioVoiceChannelMask
    ora $03FB
    sta $03FB
    jmp AudioFinishControlCommand
AudioCommandMaskClear:
    cmp #$C3                     ; CONTROL_AUDIO_COMMAND_MASK_CLEAR
    bne AudioCommandDispatch
    jsr AudioVoiceChannelMask
    pha
    ora $03FB
    sta $03FB
    pla
    eor $03FB
    sta $03FB
    jmp AudioFinishControlCommand
; All other commands dispatch on their low five bits. Values 0-3 select one
; of four APU channel offsets and mark an identical previous voice as shadowed.
AudioCommandDispatch:
    lda $0100,y                  ; CONTROL_AUDIO_COMMAND_DISPATCH
    and #$1F
    cmp #$04
    bcs AudioCommandRestorePointer
    and #$03
    asl a
    asl a
    pha
    lda $04B0,x
    and #$E0
    sta $04B0,x
    pla
    ora $04B0,x
    and #$9F
    sta $03D0
    sta $04B0,x
    stx $03D1
    ldx #$00
AudioCommandFindConflict:
    lda $04B0,x
    eor $03D0
    bne AudioCommandNextConflict
    lda $04B0,x
    ora #$20
    sta $04B0,x
AudioCommandNextConflict:
    txa
    clc
    adc #$08
    tax
    cmp #$28
    bcc AudioCommandFindConflict
    ldx $03D1
    lda $03D0
    sta $04B0,x
    jsr EnableAudioVoiceChannel
    jmp AudioFinishControlCommand
; Low values 4-7 restore the stored command pointer; 8-11 stop the current
; voice by record offset.
AudioCommandRestorePointer:
    cmp #$08                     ; CONTROL_AUDIO_COMMAND_RESTORE_POINTER
    bcs AudioCommandStopVoice
    lda $04B2,x
    sta $04B4,x
    lda $04B3,x
    sta $04B5,x
    jmp AudioFinishControlCommand
AudioCommandStopVoice:
    cmp #$0C                     ; CONTROL_AUDIO_COMMAND_STOP_VOICE
    bcs AudioCommandWriteRegister
    txa
    pha
    jsr StopAudioVoiceOffset
    pla
    tax
    jmp AudioFinishControlCommand
; Values 12-15 write the following byte to the voice register selected by the
; low two bits, unless voice flags $60 suppress writes. Consume two bytes.
AudioCommandWriteRegister:
    cmp #$10                     ; CONTROL_AUDIO_COMMAND_WRITE_REGISTER
    bcs AudioCommandRestartChannel
    lda $04B0,x
    and #$60
    bne AudioCommandWriteRegisterDone
    lda $04B0,x
    and #$1F
    sta $03E0
    ldy $03DD
    lda $0100,y
    and #$03
    clc
    adc $03E0
    sta $F6
    lda #$40
    sta $F7
    ldy $03DD
    lda $0101,y
    ldy #$00
    sta ($F6),y
AudioCommandWriteRegisterDone:
    jsr AdvanceAudioCommandOne
    jmp AudioFinishControlCommand
AudioCommandRestartChannel:
    cmp #$14                     ; CONTROL_AUDIO_COMMAND_RESTART_CHANNEL
    bcs AudioCommandEnableChannel
    jsr RestartAudioVoiceChannel
    jmp AudioFinishControlCommand
AudioCommandEnableChannel:
    cmp #$18                     ; CONTROL_AUDIO_COMMAND_ENABLE_CHANNEL
    bcs AudioCommandSelectAll
    jsr EnableAudioVoiceChannel
    jmp AudioFinishControlCommand
; $18 selects the special $1F register offset and enables the tone channels.
AudioCommandSelectAll:
    cmp #$18                     ; CONTROL_AUDIO_COMMAND_SELECT_ALL
    bne AudioCommandWriteFive
    lda $04B0,x
    and #$E0
    ora #$1F
    and #$9F
    sta $04B0,x
    jsr EnableAudioVoiceChannel
    jmp AudioFinishControlCommand
; $19 writes five consecutive APU registers unless voice flags suppress it.
; BUG: Only five total bytes were copied to the six-byte stack buffer, so the
; fifth register receives the untouched final stack byte. Five bytes advance.
AudioCommandWriteFive:
    cmp #$19                     ; CONTROL_AUDIO_COMMAND_WRITE_FIVE
    bne AudioCommandDelay
    lda $04B0,x
    and #$60
    bne AudioCommandWriteFiveDone
    lda $04B0,x
    and #$1F
    sta $F6
    lda #$40
    sta $F7
    lda $03DD
    sta $03DB
    ldy #$00
AudioCommandWriteFiveLoop:
    sty $03DC
    inc $03DB
    ldy $03DB
    lda $0100,y
    ldy $03DC
    sta ($F6),y
    iny
    cpy #$05
    bne AudioCommandWriteFiveLoop
AudioCommandWriteFiveDone:
    jsr AdvanceAudioCommandTwo
    jsr AdvanceAudioCommandTwo
    jmp AudioFinishControlCommand
; $1B loads an explicit duration and consumes two bytes. Other values use the
; ordinary one-byte completion path.
AudioCommandDelay:
    cmp #$1B                     ; CONTROL_AUDIO_COMMAND_DELAY
    bne AudioCommandDefault
    ldy $03DD
    lda $0101,y
    sta $04B1,x
    jsr AdvanceAudioCommandTwo
    jmp AudioNextVoice
AudioCommandDefault:
    jmp AudioFinishControlCommand
.assert (* - BankStart) = $122C, error, "bank 0 audio command interpreter end"
; Derive the APU channel bit from the voice record's register offset. The
; special offset $1F maps to the four non-DMC channels instead of one bit.
EnableAudioVoiceChannel:
    jsr AudioVoiceChannelMask    ; CONTROL_ENABLE_AUDIO_VOICE_CHANNEL
    ora $03E8
    sta $03E8
    sta $4015
    rts
; Temporarily clear a voice's channel enable before restoring the stored mask.
; The $0F special case is left untouched.
RestartAudioVoiceChannel:
    jsr AudioVoiceChannelMask    ; CONTROL_RESTART_AUDIO_VOICE_CHANNEL
    cmp #$0F
    beq RestartAudioVoiceReturn
    eor #$FF
    and $03E8
    sta $4015
    lda $03E8
    sta $4015
RestartAudioVoiceReturn:
    rts
AudioVoiceChannelMask:
    lda $04B0,x                  ; CONTROL_AUDIO_VOICE_CHANNEL_MASK
    and #$1F
    cmp #$1F
    beq AudioAllToneChannels
; Alternate entry accepts an APU register offset directly in A.
AudioOffsetChannelMask:
    lsr a                        ; CONTROL_AUDIO_OFFSET_CHANNEL_MASK
    lsr a
    tay
    lda AudioChannelBits,y
    rts
AudioChannelBits:
    .byte $01, $02, $04, $08, $10 ; CONTROL_AUDIO_CHANNEL_BITS
AudioAllToneChannels:
    lda #$0F                     ; CONTROL_AUDIO_ALL_TONE_CHANNELS
    rts
.assert (* - BankStart) = $1267, error, "bank 0 audio channel helpers end"

; Note duration and envelope bits, indexed in pairs from the command's upper
; bits. The values are independent of the instrument presets.
AudioNoteTiming:
    .byte $08, $01, $10, $05, $20, $08, $40, $0F, $80, $1F ; CONTROL_AUDIO_NOTE_TIMING
.assert (* - BankStart) = $1271, error, "bank 0 audio note timing end"

; Register offset followed by four APU writes for each special-note preset.
; The dispatcher admits wider indices; no runtime bound is assumed here.
AudioSpecialPresets:
    .byte $00, $80, $86, $FF, $0C ; CONTROL_AUDIO_SPECIAL_PRESETS
    .byte $04, $80, $86, $FF, $0C ; index $01
    .byte $00, $80, $84, $00, $8B ; index $02
    .byte $04, $80, $84, $00, $8B ; index $03
    .byte $00, $80, $84, $FF, $0B ; index $04
    .byte $04, $80, $84, $FF, $0B ; index $05
    .byte $0C, $00, $00, $08, $02 ; index $06
    .byte $0C, $01, $01, $03, $09 ; index $07
    .byte $0C, $0F, $00, $92, $C7 ; index $08
    .byte $0C, $05, $00, $81, $08 ; index $09
    .byte $0C, $03, $00, $04, $50 ; index $0A
    .byte $08, $04, $00, $F5, $30 ; index $0B
    .byte $00, $80, $84, $00, $89 ; index $0C
    .byte $04, $80, $84, $00, $89 ; index $0D
    .byte $00, $80, $84, $00, $8E ; index $0E
    .byte $04, $80, $84, $00, $8E ; index $0F
.assert (* - BankStart) = $12C1, error, "bank 0 special note presets end"
; Load the duration from the note command's upper bits. Unless voice flags
; $60 suppress writes, combine timing bits with the selected instrument pair
; and write the first two APU registers. Return Z set for the write path.
PrepareAudioNote:
    jsr ShiftARight4             ; CONTROL_PREPARE_AUDIO_NOTE
    and #$FE
    tay
    lda AudioNoteTiming,y
    sta $04B1,x
    jsr AudioVoiceFlags
    bne PrepareAudioNoteReturn
    iny
    lda AudioNoteTiming,y
    sta $03D0
    jsr AudioVoiceRegisterAddress
    lda $04B6,x
    asl a
    tay
    lda AudioInstrumentPairs+1,y
    pha
    lda AudioInstrumentPairs,y
    ora $03D0
    ldy #$00
    sta ($F6),y
    iny
    pla
    sta ($F6),y
    ldy #$00
PrepareAudioNoteReturn:
    rts
.assert (* - BankStart) = $12F6, error, "bank 0 audio note preparation end"

; Form the selected voice's APU-register address in $F6/$F7.
AudioVoiceRegisterAddress:
    lda $04B0,x                  ; CONTROL_AUDIO_VOICE_REGISTER_ADDRESS
    and #$1F
    sta $F6
    lda #$40
    sta $F7
    rts
.assert (* - BankStart) = $1302, error, "bank 0 audio register address end"

; Instrument indices select overlapping note-period windows in one sequence.
; Notes use indices below $1F; the extra final word remains part of the table.
AudioPeriodPointers:
    .word AudioPeriodWindow0 ; CONTROL_AUDIO_PERIOD_POINTERS
    .word AudioPeriodWindow1 ; instrument $01
    .word AudioPeriodWindow2 ; instrument $02
    .word AudioPeriodWindow0 ; instrument $03
    .word AudioPeriodWindow1 ; instrument $04
    .word AudioPeriodWindow2 ; instrument $05
    .word AudioPeriodWindow0 ; instrument $06
    .word AudioPeriodWindow1 ; instrument $07
    .word AudioPeriodWindow2 ; instrument $08
    .word AudioPeriodWindow0 ; instrument $09
    .word AudioPeriodWindow1 ; instrument $0A
    .word AudioPeriodWindow2 ; instrument $0B
    .word AudioPeriodWindow0 ; instrument $0C
    .word AudioPeriodWindow1 ; instrument $0D
    .word AudioPeriodWindow2 ; instrument $0E
    .word AudioPeriodWindow0 ; instrument $0F
    .word AudioPeriodWindow1 ; instrument $10
    .word AudioPeriodWindow2 ; instrument $11
    .word AudioPeriodWindow0 ; instrument $12
    .word AudioPeriodWindow1 ; instrument $13
    .word AudioPeriodWindow2 ; instrument $14
    .word AudioPeriodWindow0 ; instrument $15
    .word AudioPeriodWindow1 ; instrument $16
    .word AudioPeriodWindow2 ; instrument $17
    .word AudioPeriodWindow0 ; instrument $18
    .word AudioPeriodWindow1 ; instrument $19
    .word AudioPeriodWindow2 ; instrument $1A
    .word AudioPeriodWindow0 ; instrument $1B
    .word AudioPeriodWindow1 ; instrument $1C
    .word AudioPeriodWindow2 ; instrument $1D
    .word AudioPeriodWindow0 ; instrument $1E
    .word AudioPeriodWindow1 ; instrument $1F
.assert (* - BankStart) = $1342, error, "bank 0 audio period pointers end"
AudioPeriodWindow0:
    .word $0352 ; CONTROL_AUDIO_PERIOD_VALUES
    .word $0325
    .word $02FD
    .word $02CC
    .word $02A7
    .word $027C
    .word $025A
    .word $023B
    .word $0213
    .word $01FD
    .word $01DE
    .word $01C6
AudioPeriodWindow1:
    .word $01AB
    .word $0191
    .word $017A
    .word $0167
    .word $0151
    .word $013F
    .word $012C
    .word $011C
    .word $010D
    .word $00FE
    .word $00EF
    .word $00E2
AudioPeriodWindow2:
    .word $00D5
    .word $00C8
    .word $00BE
    .word $00B3
    .word $00A9
    .word $009F
    .word $0096
    .word $008E
    .word $0086
    .word $007E
    .word $0077
    .word $0070
    .word $006A
    .word $0064
    .word $005E
    .word $0059
    .word $0054
    .word $004F
    .word $004B
    .word $0046
    .word $0042
    .word $003F
    .word $003B
    .word $0038
    .word $0034
    .word $0032
    .word $002F
    .word $002C
    .word $0029
    .word $0027
    .word $0024
    .word $0023
.assert (* - BankStart) = $13B2, error, "bank 0 audio period values end"
; For an enabled voice, write the selected period's low and high bytes to its
; third and fourth APU registers. The high byte has bit $08 set.
WriteAudioVoicePeriod:
    jsr AudioVoiceFlags          ; CONTROL_WRITE_AUDIO_VOICE_PERIOD
    bne AudioVoicePeriodReturn
    jsr AudioVoiceRegisterAddress
    ldy #$02
    lda $03E0
    sta ($F6),y
    iny
    lda $03E1
    ora #$08
    sta ($F6),y
AudioVoicePeriodReturn:
    rts
; Two entry points advance the voice's little-endian command pointer by two
; or one byte respectively, carrying into the high byte.
AdvanceAudioCommandTwo:
    jsr AdvanceAudioCommandOne   ; CONTROL_ADVANCE_AUDIO_COMMAND_TWO
AdvanceAudioCommandOne:
    inc $04B4,x                  ; CONTROL_ADVANCE_AUDIO_COMMAND_ONE
    bne AdvanceAudioCommandReturn
    inc $04B5,x
AdvanceAudioCommandReturn:
    rts
AudioVoiceFlags:
    lda $04B0,x                  ; CONTROL_AUDIO_VOICE_FLAGS
    and #$60
    rts
; Use the voice's instrument index to copy a two-byte register setting from
; the instrument pair table to the voice's first two APU registers.
WriteAudioVoiceInstrument:
    lda $04B6,x                  ; CONTROL_WRITE_AUDIO_VOICE_INSTRUMENT
    asl a
    sta $03E1
    lda $04B0,x
    and #$1F
    sta $FE
    lda #$40
    sta $FF
    ldy $03E1
    lda AudioInstrumentPairs,y
    ldy #$00
    sta ($FE),y
    ldy $03E1
    iny
    lda AudioInstrumentPairs,y
    ldy #$01
    sta ($FE),y
    rts
; Valid voice indices 0-4 map to eight-byte record offsets in X.
AudioVoiceOffset:
    cmp #$05                     ; CONTROL_AUDIO_VOICE_OFFSET
    bcs AudioVoiceOffsetInvalid
    tax
    ldy #$08
    jsr MultiplyUnsigned8
    lda #$00
    rts
AudioVoiceOffsetInvalid:
    lda #$FF
    rts
.assert (* - BankStart) = $1414, error, "bank 0 audio voice helpers end"

; Process pending palette-stream setup or advance the two palette streams.
; $F8/$F9 select the background stream, $FA/$FB the sprite stream. New
; headers contain a group count, frame count and tick interval.
UpdatePaletteStreams:
    lda $0387                    ; CONTROL_UPDATE_PALETTE_STREAMS
    and #$01
    beq PaletteCheckSpriteSetup
    eor $0387
    sta $0387
    ldy #$00
    lda ($F8),y
    sta $0382
    iny
    lda ($F8),y
    sta $0383
    iny
    lda #$01
    sta $0385
    lda ($F8),y
    sta $0384
    sta $0386
    clc
    lda $F8
    adc #$03
    sta $F8
    lda $F9
    adc #$00
    sta $F9
; Enqueue the first sixteen background palette bytes at PPU address $3F00.
    ldx $0380
    lda #$00
    sta $0300,x
    inx
    lda #$3F
    sta $0300,x
    inx
    lda #$00
    sta $0300,x
    inx
    lda #$10
    sta $0300,x
    inx
    sta $03D0
    ldy #$00
PaletteSetupBackgroundCopy:
    lda ($F8),y
    iny
    sta $0300,x
    inx
    dec $03D0
    bne PaletteSetupBackgroundCopy
    stx $0380
    rts
; The other pending flag installs the sprite stream and enqueues fifteen bytes
; from offset 1 at $3F11, leaving the shared background color untouched.
PaletteCheckSpriteSetup:
    lda $0387                    ; CONTROL_PALETTE_SPRITE_SETUP
    beq PaletteAdvanceBackground
    lda #$00
    sta $0387
    ldy #$00
    lda ($FA),y
    sta $0388
    iny
    lda ($FA),y
    sta $0389
    iny
    lda #$01
    sta $038B
    lda ($FA),y
    sta $038A
    sta $038C
    clc
    lda $FA
    adc #$03
    sta $FA
    lda $FB
    adc #$00
    sta $FB
    ldx $0380
    lda #$00
    sta $0300,x
    inx
    lda #$3F
    sta $0300,x
    inx
    lda #$11
    sta $0300,x
    inx
    lda #$0F
    sta $0300,x
    inx
    sta $03D0
    ldy #$01
PaletteSetupSpriteCopy:
    lda ($FA),y
    iny
    sta $0300,x
    inx
    dec $03D0
    bne PaletteSetupSpriteCopy
    stx $0380
    rts
; Each active stream advances when its countdown reaches zero. Its group
; count selects a multiple of four bytes, placed at the end of the palette.
PaletteAdvanceBackground:
    lda $0382                    ; CONTROL_PALETTE_ADVANCE_BACKGROUND
    beq PaletteAdvanceSprite
    dec $0386
    bne PaletteAdvanceSprite
    lda $0384
    sta $0386
    lda $0382
    asl a
    asl a
    sta $03D0
    tax
    ldy $0385
    jsr MultiplyUnsigned8
    lda #$10
    sec
    sbc $03D0
    sta $03D1
    jsr AddAToXY
    stx $F6
    sty $F7
    lda $F8
    clc
    adc $F6
    sta $F6
    lda $F9
    adc $F7
    sta $F7
    ldx $0380
    lda #$00
    sta $0300,x
    inx
    lda #$3F
    sta $0300,x
    inx
    lda $03D1
    sta $0300,x
    inx
    lda $03D0
    sta $0300,x
    inx
; Y is intentionally retained from AddAToXY in the background loop.
PaletteAdvanceBackgroundCopy:
    lda ($F6),y
    sta $0300,x
    iny
    inx
    dec $03D0
    bne PaletteAdvanceBackgroundCopy
    stx $0380
    inc $0385
    lda $0385
    cmp $0383
    bne PaletteAdvanceSprite
    lda #$00
    sta $0385
PaletteAdvanceSprite:
    lda $0388                    ; CONTROL_PALETTE_ADVANCE_SPRITE
    beq PaletteStreamsReturn
    dec $038C
    bne PaletteStreamsReturn
    lda $038A
    sta $038C
    lda $0388
    asl a
    asl a
    sta $03D0
    tax
    ldy $038B
    jsr MultiplyUnsigned8
    lda #$10
    sec
    sbc $03D0
    sta $03D1
    jsr AddAToXY
    stx $F6
    sty $F7
    lda $FA
    clc
    adc $F6
    sta $F6
    lda $FB
    adc $F7
    sta $F7
    ldx $0380
    lda #$00
    sta $0300,x
    inx
    lda #$3F
    sta $0300,x
    inx
    lda $03D1
    clc
    adc #$10
    sta $0300,x
    inx
    lda $03D0
    sta $0300,x
    inx
    ldy #$00
PaletteAdvanceSpriteCopy:
    lda ($F6),y
    sta $0300,x
    iny
    inx
    dec $03D0
    bne PaletteAdvanceSpriteCopy
    stx $0380
    inc $038B
    lda $038B
    cmp $0389
    bne PaletteStreamsReturn
    lda #$00
    sta $038B
PaletteStreamsReturn:
    rts
.assert (* - BankStart) = $15D1, error, "bank 0 palette stream update end"

; If scroll work is pending, run both axis workers in alternating order.
; Each axis worker updates its scroll position and may enqueue a map redraw.
UpdateScrollWork:
    lda $03EB                    ; CONTROL_UPDATE_SCROLL_WORK
    bne ScrollWorkPending
    rts
ScrollWorkPending:
    jsr ClampScrollTargets
    lda $0398
    bne ScrollWorkVerticalFirst
    lda #$FF
    sta $0398
    jsr UpdateHorizontalScroll
    jsr UpdateVerticalScroll
    rts
ScrollWorkVerticalFirst:
    lda #$00
    sta $0398
    jsr UpdateVerticalScroll
    jsr UpdateHorizontalScroll
    rts
.assert (* - BankStart) = $15F7, error, "bank 0 scroll dispatcher end"

; Compare the current X scroll with its target. Snap and clear the pending
; bit if no tile boundary must be crossed; otherwise step at most eight pixels.
UpdateHorizontalScroll:
    lda $03EB ; CONTROL_HORIZONTAL_SCROLL
    and #$01
    beq HorizontalScrollReturn
    lda #$08
    sta $03E9
    lda $03F3
    sec
    sbc $03EE
    tay
    lda $03F4
    sbc $03EF
    bcc HorizontalScrollBelowTarget
    bne HorizontalScrollStepNegative
    tya
    beq HorizontalScrollClearPending
    cmp #$08
    bcs HorizontalScrollStepNegative
    sta $03E9
    lda $03EE
    and #$07
    sta $FE
    lda $03F3
    and #$07
    sec
    sbc $FE
    bcs HorizontalScrollSnap
    jmp HorizontalScrollStepNegative
HorizontalScrollBelowTarget:
    cmp #$FF ; CONTROL_HORIZONTAL_SCROLL_BELOW
    beq HorizontalScrollNearBelow
    jmp HorizontalScrollStepPositive
HorizontalScrollNearBelow:
    tya
    cmp #$F9
    bcc HorizontalScrollStepPositiveJump
    eor #$FF
    adc #$00
    sta $03E9
    lda $03F3
    and #$07
    sta $FE
    lda $03EE
    and #$07
    sec
    sbc $FE
    bcs HorizontalScrollSnap
HorizontalScrollStepPositiveJump:
    jmp HorizontalScrollStepPositive
HorizontalScrollSnap:
    lda $03EE ; CONTROL_HORIZONTAL_SCROLL_SNAP
    sta $03F3
    lda $03EF
    sta $03F4
HorizontalScrollClearPending:
    lda $03EB
    and #$FE
    sta $03EB
HorizontalScrollReturn:
    rts
; Moving toward lower X needs $50 bytes free in the PPU update queue.
; Calculate the newly exposed column and pass it to the local map/queue code.
HorizontalScrollStepNegative:
    jsr PpuQueueRemaining ; CONTROL_HORIZONTAL_SCROLL_NEGATIVE
    cmp #$50
    bcs HorizontalScrollNegativeQueue
    rts
HorizontalScrollNegativeQueue:
    jsr ScrollXTileCoordinate
    txa
    sec
    sbc #$01
    sta $039A
    tya
    sbc #$00
    sta $039B
    lda $03F3
    sec
    sbc $03E9
    sta $03F3
    lda $03F4
    sbc #$00
    sta $03F4
    jsr ScrollYTileCoordinate
    stx $039C
    jsr ResolveMapChunk
    jsr QueueMapTileColumn
    jmp HorizontalScrollStepReturn
; Moving toward higher X similarly queues a column when within map bounds.
HorizontalScrollStepPositive:
    jsr PpuQueueRemaining ; CONTROL_HORIZONTAL_SCROLL_POSITIVE
    cmp #$50
    bcs HorizontalScrollPositiveQueue
    rts
HorizontalScrollPositiveQueue:
    jsr ScrollYTileCoordinate
    stx $039C
    jsr ScrollXTileCoordinate
    txa
    clc
    adc #$21
    sta $039A
    tya
    adc #$00
    sta $039B
    lda $039A
    sec
    sbc $039E
    lda $039B
    sbc $039F
    bcs HorizontalScrollPositiveApply
    jsr ResolveMapChunk
    jsr QueueMapTileColumn
HorizontalScrollPositiveApply:
    lda $03F3
    clc
    adc $03E9
    sta $03F3
    lda $03F4
    adc #$00
    sta $03F4
HorizontalScrollStepReturn:
    rts
; Repeat the signed-distance and tile-boundary check for Y, using pending bit 2.
UpdateVerticalScroll:
    lda $03EB ; CONTROL_VERTICAL_SCROLL
    and #$02
    beq VerticalScrollReturn
    lda #$08
    sta $03E9
    lda $03F5
    sec
    sbc $03F0
    tay
    lda $03F6
    sbc $03F1
    bcc VerticalScrollBelowTarget
    bne VerticalScrollStepNegative
    tya
    beq VerticalScrollClearPending
    cmp #$08
    bcs VerticalScrollStepNegative
    sta $03E9
    lda $03F0
    and #$07
    sta $FE
    lda $03F5
    and #$07
    sec
    sbc $FE
    bcs VerticalScrollSnap
    jmp VerticalScrollStepNegative
VerticalScrollBelowTarget:
    cmp #$FF ; CONTROL_VERTICAL_SCROLL_BELOW
    beq VerticalScrollNearBelow
    jmp VerticalScrollStepPositive
VerticalScrollNearBelow:
    tya
    cmp #$F9
    bcc VerticalScrollStepPositiveJump
    eor #$FF
    adc #$00
    sta $03E9
    lda $03F5
    and #$07
    sta $FE
    lda $03F0
    and #$07
    sec
    sbc $FE
    bcs VerticalScrollSnap
VerticalScrollStepPositiveJump:
    jmp VerticalScrollStepPositive
VerticalScrollSnap:
    lda $03F0 ; CONTROL_VERTICAL_SCROLL_SNAP
    sta $03F5
    lda $03F1
    sta $03F6
VerticalScrollClearPending:
    lda $03EB
    and #$FD
    sta $03EB
VerticalScrollReturn:
    rts
; A vertical redraw needs $3C free queue bytes before changing position.
VerticalScrollStepNegative:
    jsr PpuQueueRemaining ; CONTROL_VERTICAL_SCROLL_NEGATIVE
    cmp #$3C
    bcs VerticalScrollNegativeQueue
    rts
VerticalScrollNegativeQueue:
    jsr ScrollYTileCoordinate
    txa
    sec
    sbc #$01
    sta $039C
    lda $03F5
    sec
    sbc $03E9
    sta $03F5
    lda $03F6
    sbc #$00
    sta $03F6
    jsr QueueScrollRow
    jmp VerticalScrollStepReturn
VerticalScrollStepPositive:
    jsr PpuQueueRemaining ; CONTROL_VERTICAL_SCROLL_POSITIVE
    cmp #$3C
    bcs VerticalScrollPositiveQueue
    rts
VerticalScrollPositiveQueue:
    jsr ScrollYTileCoordinate
    txa
    clc
    adc #$1E
    sta $039C
    jsr QueueScrollRow
    lda $03F5
    clc
    adc $03E9
    sta $03F5
    lda $03F6
    adc #$00
    sta $03F6
VerticalScrollStepReturn:
    rts
; Resolve the current X tile coordinate and queue the exposed row through
; the still-local map routines.
QueueScrollRow:
    jsr ScrollXTileCoordinate ; CONTROL_QUEUE_SCROLL_ROW
    stx $039A
    sty $039B
    jsr ResolveMapChunk
    jsr QueueMapTileRow
    rts
.assert (* - BankStart) = $17C8, error, "bank 0 scroll axis workers end"

; Update the mirrored horizontal and vertical PPU scroll values when map
; rendering is active. The vertical calculation adds $03BC, then stores the
; division routine's remainder for divisor $F0.
UpdatePpuScrollMirror:
    lda $03A4                    ; CONTROL_UPDATE_PPU_SCROLL_MIRROR
    beq PpuScrollMirrorReturn
    lda $03FF
    and #$FE
    sta $03FF
    lda $03F4
    and #$01
    ora $03FF
    sta $03FF
    lda $03F3
    sta $03FC
    lda $03F5
    clc
    adc $03BC
    tax
    lda $03F6
    adc #$00
    tay
    lda #$F0
    jsr DivideUnsigned16By8
    sty $03FD
PpuScrollMirrorReturn:
    rts
; Prepare a horizontal tile row for the PPU queue. Compute its nametable
; address and split at the 32-tile boundary, capped by the remaining map width.
QueueMapTileRow:
    lda $EC                      ; CONTROL_QUEUE_MAP_TILE_ROW
    sta $03D8
    lda $ED
    sta $03D9
    lda #$01
    sta $03D2
    lda #$00
    sta $03D3
    lda $039A
    and #$1F
    sta $03DC
    ldx #$20
    lda #$20
    and $039A
    beq MapTileRowNametable
    ldx #$24
MapTileRowNametable:
    stx $03D7                    ; CONTROL_MAP_TILE_ROW_NAMETABLE
    ldx $039C
    ldy #$00
    lda #$1E
    jsr DivideUnsigned16By8
    stx $03DA
    sty $03DF
    ldx #$20
    jsr MultiplyUnsigned8
    stx $03D6
    txa
    clc
    adc $03DC
    sta $03D4
    tya
    adc $03D7
    sta $03D5
    tya
    clc
    adc $03D7
    eor #$04
    sta $03D7
    lda $039E
    sec
    sbc $039A
    sta $03DD
    lda $039F
    sbc $039B
    beq MapTileRowWidth
    lda #$FF
    sta $03DD
MapTileRowWidth:
    lda $03DD                    ; CONTROL_MAP_TILE_ROW_WIDTH
    cmp #$21
    bcc MapTileRowWidthBounded
    lda #$21
MapTileRowWidthBounded:
    sta $03DD
    lda #$20
    sec
    sbc $03DC
    cmp $03DD
    bcc MapTileRowFirstLength
    lda $03DD
MapTileRowFirstLength:
    sta $03DC                    ; CONTROL_MAP_TILE_ROW_FIRST_LENGTH
    lda $03DD
    sec
    sbc $03DC
    sta $03DD
    jsr MapChunkRowPointer       ; Resolve source row in the current chunk.
    lda $039A
    and #$07
    sta $03DB
    clc
    adc $F6
    sta $F6
    bcc MapTileRowPointerReady
    inc $F7
MapTileRowPointerReady:
    lda #$08
    sec
    sbc $03DB
    sta $03DB
    ldx $0380
; Emit a horizontal PPU queue entry and copy spans of up to eight tiles from
; each chunk. A second entry handles crossing to the adjacent nametable.
MapTileRowQueue:
    lda #$00                     ; CONTROL_MAP_TILE_ROW_QUEUE
    sta $0300,x
    inx
    lda $03D5
    sta $0300,x
    inx
    lda $03D4
    sta $0300,x
    inx
    lda $03DC
    sta $0300,x
    inx
MapTileRowCopyNext:
    lda $03DB
    bne MapTileRowCopyCount
    jsr AdvanceMapChunk
    jsr MapChunkRowPointer
    lda #$08
    sta $03DB
MapTileRowCopyCount:
    cmp $03DC
    bcc MapTileRowCopySpan
    lda $03DC
    beq MapTileRowMaybeSecond
MapTileRowCopySpan:
    jsr MapTileRowConsumeSpan
    jmp MapTileRowCopyNext
; Deduct the span from both counts and tail-call the bank-aware linear copier.
MapTileRowConsumeSpan:
    sta $03D0                    ; CONTROL_MAP_TILE_ROW_CONSUME_SPAN
    lda $03DB
    sec
    sbc $03D0
    sta $03DB
    lda $03DC
    sec
    sbc $03D0
    sta $03DC
    jmp CopyLinearToBuffer
MapTileRowMaybeSecond:
    lda $03DD                    ; CONTROL_MAP_TILE_ROW_SECOND
    beq MapTileRowAttributes
    jsr MapQueueSecondNametable ; Switch to the next nametable address.
    jmp MapTileRowQueue
; After the tile row, decide whether this row needs attribute bytes. Some
; row positions skip the attribute update; keep the queue offset in $0380.
MapTileRowAttributes:
    stx $0380 ; CONTROL_MAP_ROW_ATTRIBUTES
    lda $03DF
    and #$02
    beq MapRowAttributesPrepare
    jmp MapQueueStoreEnd
; On alternating nametables, adjust the source row and chunk index before
; selecting the attribute address and splitting at the nametable boundary.
MapRowAttributesPrepare:
    lda #$00 ; CONTROL_MAP_ROW_ATTRIBUTES_PREPARE
    sta $EC
    sta $ED
    lda $03DA
    and #$01
    beq MapRowAttributesChunkBase
    lda $039C
    and #$07
    cmp #$02
    bcs MapRowAttributesAdjustY
    lda $03AA
    sta $EC
MapRowAttributesAdjustY:
    lda $039C
    sec
    sbc #$02
    sta $039C
MapRowAttributesChunkBase:
    lda $03D8 ; CONTROL_MAP_ROW_ATTRIBUTES_CHUNK_BASE
    sec
    sbc $EC
    sta $EC
    lda $03D9
    sbc $ED
    sta $ED
    ldx #$23
    lda #$20
    and $039A
    beq MapRowAttributeAddress
    ldx #$27
; Form the $23C0/$27C0 attribute address and count up to nine entries.
MapRowAttributeAddress:
    stx $03D7 ; CONTROL_MAP_ROW_ATTRIBUTE_ADDRESS
    lda $03DF
    and #$FC
    asl a
    clc
    adc #$C0
    sta $03D6
    lda $039A
    and #$1F
    lsr a
    lsr a
    clc
    adc $03D6
    sta $03D4
    lda $03D7
    sta $03D5
    lda $03D7
    eor #$04
    sta $03D7
    lda $039A
    and #$1F
    lsr a
    lsr a
    jsr NegateA
    clc
    adc #$08
    sta $03DC
    lda #$09
    sta $03DD
    lda $03A0
    sec
    sbc $039A
    bne MapRowAttributesFirst
    lda $03A1
    sbc $039B
    bne MapRowAttributesFirst
    dec $03DD
; Copy attribute spans in two-byte chunks, crossing the chunk and nametable
; boundaries through the same helpers as the tile-row path.
MapRowAttributesFirst:
    lda $03DD ; CONTROL_MAP_ROW_ATTRIBUTES_FIRST
    sec
    sbc $03DC
    sta $03DD
    jsr MapChunkAttributeRowPointer
    lda #$02
    sta $03DB
    lda $039A
    and #$04
    beq MapRowAttributesReady
    dec $03DB
    inc $F6
    bne MapRowAttributesReady
    inc $F7
MapRowAttributesReady:
    ldx $0380
MapRowAttributesQueue:
    lda #$00 ; CONTROL_MAP_ROW_ATTRIBUTES_QUEUE
    sta $0300,x
    inx
    lda $03D5
    sta $0300,x
    inx
    lda $03D4
    sta $0300,x
    inx
    lda $03DC
    sta $0300,x
    inx
MapRowAttributesCopyNext:
    lda $03DB
    bne MapRowAttributesCopyCount
    jsr AdvanceMapChunk
    jsr MapChunkAttributeRowPointer
    lda #$02
    sta $03DB
MapRowAttributesCopyCount:
    cmp $03DC
    bcc MapRowAttributesCopySpan
    lda $03DC
    beq MapRowAttributesMaybeSecond
MapRowAttributesCopySpan:
    jsr MapTileRowConsumeSpan
    jmp MapRowAttributesCopyNext
MapRowAttributesMaybeSecond:
    lda $03DD
    beq MapRowAttributesMerge
    jsr MapQueueSecondNametable
    jmp MapRowAttributesQueue
.assert (* - BankStart) = $1A20, error, "bank 0 map row attribute queue end"
; Move the remaining count and saved alternate nametable address into the
; active queue fields before emitting the second entry.
MapQueueSecondNametable:
    sta $03DC                    ; CONTROL_MAP_QUEUE_SECOND_NAMETABLE
    lda #$00
    sta $03DD
    lda $03D6
    sta $03D4
    lda $03D7
    sta $03D5
    rts
.assert (* - BankStart) = $1A35, error, "bank 0 map queue nametable switch end"

; For the other half of a wrapped row, merge four source bits into each
; queued attribute byte using the bank-aware bit copier.
MapRowAttributesMerge:
    lda $03DA ; CONTROL_MAP_ROW_ATTRIBUTES_MERGE
    and #$01
    bne MapRowAttributesPrepareMerge
    jmp MapQueueStoreEnd
MapRowAttributesPrepareMerge:
    stx $03D4 ; CONTROL_MAP_ROW_ATTRIBUTES_PREPARE_MERGE
    lda $039C
    clc
    adc #$02
    sta $039C
    lda #$00
    sta $EC
    sta $ED
    lda $039C
    and #$07
    cmp #$06
    bcc MapRowAttributesMergeChunk
    lda $03AA
    sta $EC
MapRowAttributesMergeChunk:
    lda $03D8 ; CONTROL_MAP_ROW_ATTRIBUTES_MERGE_CHUNK
    clc
    adc $EC
    sta $EC
    lda $03D9
    adc $ED
    sta $ED
    lda $039C
    clc
    adc #$02
    sta $039C
    lda $0380
    clc
    adc #$04
    sta $03D6
    tax
    dex
    lda $0300,x
    sta $03DC
    clc
    adc $03D6
    adc #$04
    sta $03D7
    cmp $03D4
    bcs MapRowAttributesMergeSource
    tax
    dex
    lda $0300,x
    sta $03DD
MapRowAttributesMergeSource:
    jsr MapChunkAttributeRowPointer ; CONTROL_MAP_ROW_ATTRIBUTES_MERGE_SOURCE
    lda #$02
    sta $03DB
    lda $039A
    and #$04
    beq MapRowAttributesMergeReady
    dec $03DB
    inc $F6
    bne MapRowAttributesMergeReady
    inc $F7
MapRowAttributesMergeReady:
    ldx $03D6
MapRowAttributesMergeNext:
    lda $03DB
    bne MapRowAttributesMergeCount
    jsr AdvanceMapChunk
    jsr MapChunkAttributeRowPointer
    lda #$02
    sta $03DB
MapRowAttributesMergeCount:
    cmp $03DC
    bcc MapRowAttributesMergeSpan
    lda $03DC
    beq MapRowAttributesMergeNextNametable
MapRowAttributesMergeSpan:
    jsr MapConsumeAttributeSpan
    jsr CopyBitsToBuffer
    jmp MapRowAttributesMergeNext
; Deduct a span from the current chunk and remaining nametable counts.
MapConsumeAttributeSpan:
    sta $03D0 ; CONTROL_MAP_CONSUME_ATTRIBUTE_SPAN
    lda $03DB
    sec
    sbc $03D0
    sta $03DB
    lda $03DC
    sec
    sbc $03D0
    sta $03DC
    rts
MapRowAttributesMergeNextNametable:
    lda $03DD ; CONTROL_MAP_ROW_ATTRIBUTES_MERGE_NEXT
    beq MapQueueStoreEnd
    sta $03DC
    lda #$00
    sta $03DD
    ldx $03D7
    jmp MapRowAttributesMergeNext
.assert (* - BankStart) = $1B07, error, "bank 0 map row attribute merge end"
MapQueueStoreEnd:
    stx $0380                    ; CONTROL_MAP_QUEUE_STORE_END
    rts
; Convert the row within a chunk to an eight-byte tile-row offset.
MapChunkRowPointer:
    lda $039C                    ; CONTROL_MAP_CHUNK_ROW_POINTER
    and #$07
    asl a
    asl a
    asl a
    jmp MapChunkOffsetPointer
; Select one of the two two-byte attribute rows within a chunk.
MapChunkAttributeRowPointer:
    lda $039C                    ; CONTROL_MAP_CHUNK_ATTRIBUTE_ROW_POINTER
    and #$04
    lsr a
    clc
    adc #$40
    jmp MapChunkOffsetPointer
.assert (* - BankStart) = $1B22, error, "bank 0 map queue helpers end"

; Prepare a vertical tile column, using map width as the chunk stride. Split
; the queue entry at the 30-tile nametable boundary and the map bottom.
QueueMapTileColumn:
    lda $EC ; CONTROL_QUEUE_MAP_TILE_COLUMN
    sta $03D8
    lda $ED
    sta $03D9
    lda $03AA
    sta $03D2
    lda #$00
    sta $03D3
    lda $039A
    and #$1F
    sta $03D6
    ldx #$20
    lda #$20
    and $039A
    beq MapColumnNametable
    ldx #$24
MapColumnNametable:
    stx $03D7 ; CONTROL_MAP_COLUMN_NAMETABLE
    ldx $039C
    ldy #$00
    lda #$1E
    jsr DivideUnsigned16By8
    stx $03DA
    sty $03DC
    sty $03DF
    ldx #$20
    jsr MultiplyUnsigned8
    txa
    clc
    adc $03D6
    sta $03D4
    tya
    adc $03D7
    sta $03D5
    lda $0396
    sec
    sbc $039C
    cmp #$1E
    bcc MapColumnFirstLength
    lda #$1E
MapColumnFirstLength:
    sta $03DD ; CONTROL_MAP_COLUMN_FIRST_LENGTH
    lda #$1E
    sec
    sbc $03DC
    cmp $03DD
    bcc MapColumnSource
    lda $03DD
MapColumnSource:
    sta $03DC
    lda $03DD
    sec
    sbc $03DC
    sta $03DD
    jsr MapChunkColumnPointer
    lda $039C
    and #$07
    sta $03DB
    asl a
    asl a
    asl a
    clc
    adc $F6
    sta $F6
    bcc MapColumnSourceReady
    inc $F7
MapColumnSourceReady:
    lda #$08
    sec
    sbc $03DB
    sta $03DB
    ldx $0380
; Emit vertical-increment PPU entries and copy tile spans with source stride 8.
MapColumnQueue:
    lda #$04 ; CONTROL_MAP_COLUMN_QUEUE
    sta $0300,x
    inx
    lda $03D5
    sta $0300,x
    inx
    lda $03D4
    sta $0300,x
    inx
    lda $03DC
    sta $0300,x
    inx
MapColumnCopyNext:
    lda $03DB
    bne MapColumnCopyCount
    jsr AdvanceMapChunk
    jsr MapChunkColumnPointer
    lda #$08
    sta $03DB
MapColumnCopyCount:
    cmp $03DC
    bcc MapColumnCopySpan
    lda $03DC
    beq MapColumnMaybeSecond
MapColumnCopySpan:
    jsr MapConsumeAttributeSpan
    lda #$08
    sta $03D1
    jsr CopyStridedToBuffer
    jmp MapColumnCopyNext
MapColumnMaybeSecond:
    lda $03DD ; CONTROL_MAP_COLUMN_SECOND
    beq MapColumnAttributes
    jsr MapQueueSecondNametable
    jmp MapColumnQueue
; Gather the corresponding attribute column into scratch bytes. Some edge
; cases select the previous chunk or rotate the packed attribute nibbles.
MapColumnAttributes:
    stx $0380 ; CONTROL_MAP_COLUMN_ATTRIBUTES
    lda $03D8
    sta $EC
    lda $03D9
    sta $ED
    lda $03DA
    and #$01
    sta $03D1
    lda $0396
    sec
    sbc $039C
    cmp #$24
    bcc MapColumnAttributesCount
    lda #$24
MapColumnAttributesCount:
    clc ; CONTROL_MAP_COLUMN_ATTRIBUTES_COUNT
    adc #$03
    lsr a
    lsr a
    sta $03D4
    sta $03DE
    lda #$02
    sta $03D0
    jsr MapChunkAttributePointer
    lda $03D1
    beq MapColumnAttributeAlignment
    lda $039C
    and #$02
    bne MapColumnAttributeAlignment
    lda $039C
    and #$04
    bne MapColumnAttributesGather
    jsr RetreatMapChunk
    jsr MapChunkAttributePointer
    jmp MapColumnAttributeOffset
MapColumnAttributeAlignment:
    lda $039C
    and #$04
    beq MapColumnAttributesGather
MapColumnAttributeOffset:
    lda #$01
    sta $03D0
    lda $F6
    clc
    adc #$02
    sta $F6
    bcc MapColumnAttributesGather
    inc $F7
MapColumnAttributesGather:
    ldx #$00 ; CONTROL_MAP_COLUMN_ATTRIBUTES_GATHER
MapColumnAttributesGatherNext:
    lda $03D4
    beq MapColumnAttributeRotateRight
    sec
    sbc $03D0
    sta $03D4
    jsr CopyIndexedToState
    jsr AdvanceMapChunk
    jsr MapChunkAttributePointer
    lda #$02
    sta $03D0
    cmp $03D4
    bcc MapColumnAttributesGatherNext
    lda $03D4
    sta $03D0
    jmp MapColumnAttributesGatherNext
; Rotate the scratch attribute bytes right four times when the nametable
; alignment requires it; carry propagation spans the entire scratch array.
MapColumnAttributeRotateRight:
    lda $03D1 ; CONTROL_MAP_COLUMN_ATTRIBUTE_ROTATE_RIGHT
    beq MapColumnAttributeTrim
    ldy #$04
MapColumnAttributeRotateRightLoop:
    clc
    ror $03DD
    ror $03DC
    ror $03DB
    ror $03DA
    ror $03D9
    ror $03D8
    ror $03D7
    ror $03D6
    ror $03D5
    dey
    bne MapColumnAttributeRotateRightLoop
MapColumnAttributeTrim:
    lda $03DF ; CONTROL_MAP_COLUMN_ATTRIBUTE_TRIM
    and #$03
    bne MapColumnAttributeAddress
    lda $03DE
    cmp #$08
    bcc MapColumnAttributeAddress
    lda #$08
    sta $03DE
; Emit one-byte PPU attribute entries, moving down eight bytes per entry.
MapColumnAttributeAddress:
    lda $039A ; CONTROL_MAP_COLUMN_ATTRIBUTE_ADDRESS
    and #$1F
    lsr a
    lsr a
    sta $03D2
    lda $03DF
    and #$FC
    asl a
    adc $03D2
    adc #$C0
    sta $03D2
    ldx #$23
    lda #$20
    and $039A
    beq MapColumnAttributeNametable
    ldx #$27
MapColumnAttributeNametable:
    stx $03D3
    ldx $0380
    ldy #$00
MapColumnAttributeQueue:
    lda #$00 ; CONTROL_MAP_COLUMN_ATTRIBUTE_QUEUE
    sta $0300,x
    inx
    lda $03D3
    sta $0300,x
    inx
    lda $03D2
    sta $0300,x
    inx
    lda #$01
    sta $0300,x
    inx
    lda $03D5,y
    iny
    sta $0300,x
    inx
    lda $03D2
    clc
    adc #$08
    ora #$C0
    sta $03D2
    bcc MapColumnAttributeNext
    tya
    pha
    ldy #$04
; On address wrap, rotate the scratch array left four times before continuing.
MapColumnAttributeRotateLeft:
    clc ; CONTROL_MAP_COLUMN_ATTRIBUTE_ROTATE_LEFT
    rol $03D5
    rol $03D6
    rol $03D7
    rol $03D8
    rol $03D9
    rol $03DA
    rol $03DB
    rol $03DC
    rol $03DD
    dey
    bne MapColumnAttributeRotateLeft
    pla
    tay
MapColumnAttributeNext:
    dec $03DE
    bne MapColumnAttributeQueue
    stx $0380
    rts
.assert (* - BankStart) = $1D63, error, "bank 0 map column queue end"
; Select a tile-column offset within a map chunk, then resolve its tile pointer.
MapChunkColumnPointer:
    lda $039A                    ; CONTROL_MAP_CHUNK_COLUMN_POINTER
    and #$07
; A is an offset within the chunk, EC/ED selects its banked index, and X is
; preserved. Resolve its table entry at $A1DE and return the pointer in F6/F7.
MapChunkOffsetPointer:
    pha                          ; CONTROL_MAP_CHUNK_OFFSET_POINTER
    txa
    pha
    lda $EC
    sta $FE
    lda $ED
    sta $FF
    jsr ReadBankedPointer
    pla
    tax
    pla
    ldy #$00
    pha
    lda $FE
    sta $F6
    lda #$00
    sta $F7
    asl $F6
    rol $F7
    lda #<MapChunkOffsets
    clc
    adc $F6
    sta $F6
    lda #>MapChunkOffsets
    adc $F7
    sta $F7
    pla
    clc
    adc ($F6),y
    pha
    iny
    lda ($F6),y
    adc #$00
    sta $F7
    pla
    sta $F6
    rts
; Rotate X coordinate bit 2 into carry, then select chunk offset $40 or $41.
MapChunkAttributePointer:
    lda $039A                    ; CONTROL_MAP_CHUNK_ATTRIBUTE_POINTER
    ror a
    ror a
    ror a
    lda #$40
    adc #$00
    jmp MapChunkOffsetPointer
; Advance or retreat the map chunk index by the 16-bit stride in $03D2/$03D3.
AdvanceMapChunk:
    lda $EC                      ; CONTROL_ADVANCE_MAP_CHUNK
    clc
    adc $03D2
    sta $EC
    lda $ED
    adc $03D3
    sta $ED
    rts
RetreatMapChunk:
    lda $EC                      ; CONTROL_RETREAT_MAP_CHUNK
    sec
    sbc $03D2
    sta $EC
    lda $ED
    sbc $03D3
    sta $ED
    rts
.assert (* - BankStart) = $1DD2, error, "bank 0 redraw map helpers end"

; Return the space remaining in the $60-byte PPU update queue.
PpuQueueRemaining:
    lda #$60                     ; CONTROL_PPU_QUEUE_REMAINING
    sec
    sbc $0380
    rts
; Clamp desired X/Y scroll positions to their respective upper bounds. When
; Y is clamped, run script opcode $18's sound restart exactly as the original.
ClampScrollTargets:
    lda $03A2                    ; CONTROL_CLAMP_SCROLL_TARGETS
    sec
    sbc $03EE
    lda $03A3
    sbc $03EF
    bcs ClampScrollY
    lda $03A2
    sta $03EE
    lda $03A3
    sta $03EF
ClampScrollY:
    lda $03A8
    sec
    sbc $03F0
    lda $03A9
    sbc $03F1
    bcs ClampScrollReturn
    lda $03A8
    sta $03F0
    lda $03A9
    sta $03F1
    jsr ScriptOp18
ClampScrollReturn:
    rts
; Divide the current X or Y scroll position by eight, returning Y:X.
ScrollXTileCoordinate:
    ldx $03F3                    ; CONTROL_SCROLL_X_TILE_COORDINATE
    ldy $03F4
ShiftXYRight3:
    jsr ShiftXYRight1
    jsr ShiftXYRight1
ShiftXYRight1:
    tya
    lsr a
    tay
    txa
    ror a
    tax
    rts
ScrollYTileCoordinate:
    ldx $03F5                    ; CONTROL_SCROLL_Y_TILE_COORDINATE
    ldy $03F6
    jmp ShiftXYRight3
ShiftXYLeft3:
    jsr ShiftXYLeft1             ; CONTROL_SHIFT_XY_LEFT3
    jsr ShiftXYLeft1
ShiftXYLeft1:
    txa
    asl a
    tax
    tya
    rol a
    tay
    rts
.assert (* - BankStart) = $1E3C, error, "bank 0 scroll and queue helpers end"

; Eight rounds of shift/add multiplication. The original returns the low byte
; in X and high byte in Y, using $03E2-$03E4 as scratch.
MultiplyUnsigned8:
    sty $03E2                     ; CONTROL_MUL_UNSIGNED8
    stx $03E4
    lda #$00
    sta $03E3
    ldx #$08
MultiplyUnsigned8Loop:
    asl a
    rol $03E3
    asl $03E2
    bcc MultiplyUnsigned8Next
    clc
    adc $03E4
    bcc MultiplyUnsigned8Next
    inc $03E3
MultiplyUnsigned8Next:
    dex
    bne MultiplyUnsigned8Loop
    tax
    ldy $03E3
    rts

; Eight rounds of shift/subtract division. A is the divisor, Y:X the input;
; the routine returns X and Y. The quotient must fit in one byte for the usual
; unsigned quotient/remainder interpretation; zero divisor behavior is unverified.
DivideUnsigned16By8:
    sta $03E4                     ; CONTROL_DIV_UNSIGNED16_8
    stx $03E5
    tya
    ldx #$08
DivideUnsigned16Loop:
    asl $03E5
    rol a
    bcs DivideUnsigned16Subtract
    cmp $03E4
    bcc DivideUnsigned16Next
DivideUnsigned16Subtract:
    sbc $03E4
    inc $03E5
DivideUnsigned16Next:
    dex
    bne DivideUnsigned16Loop
    tay
    ldx $03E5
    rts

; Add A and X, returning the low byte in X and incrementing Y on carry.
AddAToXY:
    stx $03E2                     ; CONTROL_ADD_A_TO_XY
    clc
    adc $03E2
    tax
    bcc AddAToXYReturn
    iny
AddAToXYReturn:
    rts
NegateA:
    eor #$FF                      ; CONTROL_NEGATE_A
    clc
    adc #$01
    rts
.assert (* - BankStart) = $1E97, error, "bank 0 arithmetic helper end"


.assert (* - BankStart) = $1E97, error, "bank 0 PPU queue offset"
; Records in $0300 contain PPUCTRL, address high/low, length, then data.
; $0380 is the queue's end offset. The entry at RestorePpuCtrl is also called
; independently by the NMI handler's bank-0 work routine.
FlushPpuUpdates:
    ldx #$00                     ; CONTROL_PPU_FLUSH
NextPpuUpdate:
    cpx $0380
    beq FinishPpuUpdates
    lda $0300,x
    sta PPUCTRL
    inx
    lda $0300,x
    sta PPUADDR
    inx
    lda $0300,x
    sta PPUADDR
    inx
    ldy $0300,x
    inx
WritePpuUpdate:
    lda $0300,x
    inx
    sta PPUDATA
    dey
    bne WritePpuUpdate
    jmp NextPpuUpdate
FinishPpuUpdates:
    lda #$00
    sta $0380
RestorePpuCtrl:
    lda $03FF
    sta PPUCTRL
    rts
.assert (* - BankStart) = $1ED0, error, "bank 0 wait routine offset"
WaitVBlank:
    lda PPUSTATUS                ; CONTROL_WAIT
    bpl WaitVBlank
    rts

; Hide the shadow sprites, with the first entry initialized separately.
InitializeShadowOam:
    lda #$F8
    sta $0200
    lda #$08
    sta $0202
InitializeRemainingShadowOam:
    ldy #$00                     ; CONTROL_OAM_INIT
    ldx #$3F
InitializeNextSprite:
    lda #$F8
    sta $0204,y
    lda #$00
    sta $0206,y
AdvanceSpriteOffset:
    iny
    iny
    iny
    iny
    cpy #$FC
    beq AdvanceSpriteOffset
    dex
    bne InitializeNextSprite
    rts
.assert (* - BankStart) = $1EFA, error, "bank 0 shadow OAM initializer size"

; Four default operands copied to $61-$64 by the main-state initializer.
DefaultSplitScreenParameters:
    .byte $00, $00, $00, $00 ; CONTROL_DEFAULT_SPLIT_PARAMETERS
.assert (* - BankStart) = $1EFE, error, "bank 0 default split parameters end"
; Signed X/Y delta pairs selected by the four controller motion paths.
ControllerDeltas:
    .byte $F4, $00, $0C, $00, $00, $F4, $00, $0C ; CONTROL_CONTROLLER_DELTAS
.assert (* - BankStart) = $1F06, error, "bank 0 controller delta table end"
; Observed six-byte slot descriptors. The pointer is an encoded ROM address;
; the other bytes initialize $05D0/$0610/$05E0/$0520. The boundary at
; $A1B2 is the start of a separately referenced table; runtime index bounds
; are not established.
SlotInitialDescriptors:
    SlotDescriptor $716D, $00, $00, $00, $00 ; CONTROL_SLOT_DESCRIPTOR
    SlotDescriptor $2CA3, $B2, $E0, $00, $0C ; index $01
    SlotDescriptor $5584, $74, $E0, $80, $01 ; index $02
    SlotDescriptor $3990, $00, $00, $40, $00 ; index $03
    SlotDescriptor $395F, $20, $00, $30, $00 ; index $04
    SlotDescriptor $5470, $00, $00, $30, $00 ; index $05
    SlotDescriptor $7419, $00, $00, $00, $00 ; index $06
    SlotDescriptor $38EE, $60, $E0, $00, $01 ; index $07
    SlotDescriptor $6E68, $20, $E0, $E0, $00 ; index $08
    SlotDescriptor $3DF6, $20, $00, $00, $00 ; index $09
    SlotDescriptor $53B7, $20, $DA, $A0, $00 ; index $0A
    SlotDescriptor $37B5, $20, $00, $20, $00 ; index $0B
    SlotDescriptor $37E5, $20, $E0, $20, $01 ; index $0C
    SlotDescriptor $33E5, $20, $00, $4F, $00 ; index $0D
    SlotDescriptor $5A1C, $30, $E0, $80, $01 ; index $0E
    SlotDescriptor $6E82, $30, $E0, $A0, $00 ; index $0F
    SlotDescriptor $6F00, $30, $E0, $A0, $00 ; index $10
    SlotDescriptor $5AD6, $30, $E0, $80, $01 ; index $11
    SlotDescriptor $5B12, $30, $E0, $80, $01 ; index $12
    SlotDescriptor $521C, $30, $E0, $00, $14 ; index $13
    SlotDescriptor $36D3, $60, $00, $80, $00 ; index $14
    SlotDescriptor $5A46, $30, $E0, $80, $01 ; index $15
    SlotDescriptor $3C6C, $00, $00, $00, $00 ; index $16
    SlotDescriptor $3CAE, $00, $00, $00, $00 ; index $17
    SlotDescriptor $5A79, $30, $E0, $80, $01 ; index $18
    SlotDescriptor $5A79, $30, $E0, $80, $01 ; index $19
    SlotDescriptor $5B4E, $30, $E0, $A0, $01 ; index $1A
    SlotDescriptor $5B4E, $30, $E0, $A0, $01 ; index $1B
    SlotDescriptor $6398, $B0, $E0, $80, $01 ; index $1C
    SlotDescriptor $63E6, $B0, $E0, $80, $01 ; index $1D
    SlotDescriptor $7C58, $20, $E9, $00, $00 ; index $1E
    SlotDescriptor $7CFC, $20, $E9, $00, $00 ; index $1F
    SlotDescriptor $54C1, $30, $E9, $80, $00 ; index $20
    SlotDescriptor $6F5A, $20, $E0, $30, $00 ; index $21
    SlotDescriptor $6F36, $30, $E0, $A0, $00 ; index $22
    SlotDescriptor $5AAC, $30, $E0, $80, $01 ; index $23
    SlotDescriptor $5AAC, $30, $E0, $80, $01 ; index $24
    SlotDescriptor $3D4F, $00, $00, $00, $00 ; index $25
    SlotDescriptor $3DB6, $00, $00, $0C, $00 ; index $26
    SlotDescriptor $3DCD, $00, $00, $00, $00 ; index $27
    SlotDescriptor $56D7, $00, $00, $00, $00 ; index $28
    SlotDescriptor $5B66, $60, $E0, $80, $01 ; index $29
    SlotDescriptor $5B66, $60, $E0, $80, $01 ; index $2A
    SlotDescriptor $5B66, $60, $E0, $80, $01 ; index $2B
    SlotDescriptor $63E6, $B0, $E0, $80, $01 ; index $2C
    SlotDescriptor $6398, $B0, $E0, $80, $01 ; index $2D
    SlotDescriptor $6BD3, $60, $E0, $80, $01 ; index $2E
    SlotDescriptor $6BD3, $60, $E0, $80, $01 ; index $2F
    SlotDescriptor $5DBC, $60, $E0, $80, $01 ; index $30
    SlotDescriptor $5DBC, $60, $E0, $80, $01 ; index $31
    SlotDescriptor $5D62, $60, $E0, $80, $01 ; index $32
    SlotDescriptor $5D8F, $60, $E0, $80, $01 ; index $33
    SlotDescriptor $5DE9, $60, $E0, $80, $01 ; index $34
    SlotDescriptor $5DE9, $60, $E0, $80, $01 ; index $35
    SlotDescriptor $6434, $B0, $E0, $80, $01 ; index $36
    SlotDescriptor $6434, $B0, $E0, $80, $01 ; index $37
    SlotDescriptor $6008, $30, $E0, $80, $01 ; index $38
    SlotDescriptor $6008, $30, $E0, $80, $01 ; index $39
    SlotDescriptor $6F48, $20, $E0, $30, $00 ; index $3A
    SlotDescriptor $393F, $30, $00, $30, $01 ; index $3B
    SlotDescriptor $6B74, $30, $E0, $80, $01 ; index $3C
    SlotDescriptor $6B74, $30, $E0, $80, $01 ; index $3D
    SlotDescriptor $62FC, $B0, $E0, $80, $01 ; index $3E
    SlotDescriptor $62FC, $B0, $E0, $80, $01 ; index $3F
    SlotDescriptor $FFFF, $30, $E0, $00, $01 ; index $40
    SlotDescriptor $FFFF, $30, $E0, $00, $01 ; index $41
    SlotDescriptor $60F4, $30, $E0, $80, $01 ; index $42
    SlotDescriptor $60F4, $30, $E0, $80, $01 ; index $43
    SlotDescriptor $60B9, $30, $E0, $80, $01 ; index $44
    SlotDescriptor $60B9, $30, $E0, $80, $01 ; index $45
    SlotDescriptor $FFFF, $30, $E0, $00, $01 ; index $46
    SlotDescriptor $FFFF, $30, $E0, $00, $01 ; index $47
    SlotDescriptor $607E, $30, $E0, $80, $01 ; index $48
    SlotDescriptor $607E, $30, $E0, $80, $01 ; index $49
    SlotDescriptor $6043, $30, $E0, $80, $01 ; index $4A
    SlotDescriptor $6043, $30, $E0, $80, $01 ; index $4B
    SlotDescriptor $FFFF, $30, $E0, $80, $01 ; index $4C
    SlotDescriptor $6EE8, $30, $E0, $A0, $00 ; index $4D
    SlotDescriptor $6D21, $30, $E0, $A0, $01 ; index $4E
    SlotDescriptor $6D21, $30, $E0, $A0, $01 ; index $4F
    SlotDescriptor $5C1A, $30, $E0, $80, $01 ; index $50
    SlotDescriptor $6B37, $30, $E0, $A0, $01 ; index $51
    SlotDescriptor $5EF4, $30, $E0, $80, $01 ; index $52
    SlotDescriptor $388A, $70, $E0, $30, $01 ; index $53
    SlotDescriptor $3B52, $20, $00, $00, $00 ; index $54
    SlotDescriptor $5584, $70, $E0, $00, $01 ; index $55
    SlotDescriptor $6D56, $30, $E0, $80, $01 ; index $56
    SlotDescriptor $6D56, $30, $E0, $80, $01 ; index $57
    SlotDescriptor $6AED, $30, $E0, $80, $01 ; index $58
    SlotDescriptor $6AED, $30, $E0, $80, $01 ; index $59
    SlotDescriptor $6F24, $30, $E0, $A0, $00 ; index $5A
    SlotDescriptor $6F5A, $20, $E0, $A0, $00 ; index $5B
    SlotDescriptor $6E82, $30, $E0, $A0, $00 ; index $5C
    SlotDescriptor $552B, $70, $E0, $80, $07 ; index $5D
    SlotDescriptor $6E94, $30, $E0, $A0, $00 ; index $5E
    SlotDescriptor $6EA6, $30, $E0, $A0, $00 ; index $5F
    SlotDescriptor $6ED0, $30, $E0, $A0, $00 ; index $60
    SlotDescriptor $6F12, $30, $E0, $A0, $00 ; index $61
    SlotDescriptor $6EB8, $30, $E0, $A0, $00 ; index $62
    SlotDescriptor $3A11, $20, $E0, $80, $01 ; index $63
    SlotDescriptor $3D09, $00, $00, $00, $00 ; index $64
    SlotDescriptor $3B60, $60, $00, $80, $00 ; index $65
    SlotDescriptor $543E, $60, $00, $00, $01 ; index $66
    SlotDescriptor $3C19, $02, $00, $20, $01 ; index $67
    SlotDescriptor $5A46, $30, $E0, $80, $01 ; index $68
    SlotDescriptor $5A1C, $30, $E0, $80, $01 ; index $69
    SlotDescriptor $6E45, $30, $E0, $A0, $01 ; index $6A
    SlotDescriptor $3A4A, $20, $00, $A0, $00 ; index $6B
    SlotDescriptor $3A63, $70, $DA, $A0, $01 ; index $6C
    SlotDescriptor $6F6C, $30, $E0, $20, $01 ; index $6D
    SlotDescriptor $634A, $B0, $E0, $80, $01 ; index $6E
    SlotDescriptor $6B9A, $20, $E0, $A0, $01 ; index $6F
    SlotDescriptor $3685, $30, $E0, $20, $00 ; index $70
    SlotDescriptor $6B13, $30, $E0, $80, $01 ; index $71
.assert (* - BankStart) = $21B2, error, "bank 0 slot descriptor boundary"

; 22 encoded addresses read as adjacent low/high bytes at $CB9A-$CB9D.
; The next table starts at $A1DE; runtime index bounds are not established.
SlotRelatedAddressTable:
    .word $A302 ; CONTROL_SLOT_RELATED_ADDRESS
    .word $744D ; index $01
    .word $744D ; index $02
    .word $744D ; index $03
    .word $744D ; index $04
    .word $7965 ; index $05
    .word $7A5C ; index $06
    .word $7B53 ; index $07
    .word $7A5C ; index $08
    .word $7965 ; index $09
    .word $7B53 ; index $0A
    .word $7625 ; index $0B
    .word $76CF ; index $0C
    .word $7735 ; index $0D
    .word $7791 ; index $0E
    .word $7873 ; index $0F
    .word $A32A ; index $10
    .word $A302 ; index $11
    .word $A318 ; index $12
    .word $A318 ; index $13
    .word $A33C ; index $14
    .word $A34E ; index $15
.assert (* - BankStart) = $21DE, error, "bank 0 related address table end"

; The map index selects an offset into the local 68-byte chunk data.
; Both references to chunk zero and the original nonsequential order remain.
MapChunkOffsets:
    .word $44 * $00 ; CONTROL_MAP_CHUNK_OFFSETS
    .word $44 * $00, $44 * $01, $44 * $02, $44 * $03, $44 * $04, $44 * $05, $44 * $06, $44 * $07
    .word $44 * $08, $44 * $09, $44 * $0A, $44 * $0B, $44 * $0C, $44 * $4D, $44 * $5F, $44 * $0D
    .word $44 * $0E, $44 * $0F, $44 * $10, $44 * $11, $44 * $12, $44 * $59, $44 * $13, $44 * $14
    .word $44 * $15, $44 * $86, $44 * $17, $44 * $18, $44 * $19, $44 * $1A, $44 * $1B, $44 * $1C
    .word $44 * $1D, $44 * $1E, $44 * $1F, $44 * $20, $44 * $21, $44 * $22, $44 * $23, $44 * $24
    .word $44 * $25, $44 * $26, $44 * $27, $44 * $28, $44 * $29, $44 * $2A, $44 * $2B, $44 * $2C
    .word $44 * $2D, $44 * $2E, $44 * $2F, $44 * $30, $44 * $31, $44 * $32, $44 * $33, $44 * $34
    .word $44 * $35, $44 * $36, $44 * $58, $44 * $38, $44 * $39, $44 * $3A, $44 * $3B, $44 * $54
    .word $44 * $3C, $44 * $3D, $44 * $3E, $44 * $3F, $44 * $78, $44 * $40, $44 * $52, $44 * $5E
    .word $44 * $37, $44 * $41, $44 * $68, $44 * $53, $44 * $7A, $44 * $4E, $44 * $79, $44 * $5A
    .word $44 * $42, $44 * $44, $44 * $45, $44 * $46, $44 * $47, $44 * $48, $44 * $49, $44 * $4A
    .word $44 * $4B, $44 * $4C, $44 * $56, $44 * $4F, $44 * $7B, $44 * $60, $44 * $61, $44 * $62
    .word $44 * $63, $44 * $64, $44 * $65, $44 * $66, $44 * $67, $44 * $69, $44 * $74, $44 * $75
    .word $44 * $76, $44 * $77, $44 * $7C, $44 * $7D, $44 * $7E, $44 * $7F, $44 * $5D, $44 * $80
    .word $44 * $81, $44 * $82, $44 * $83, $44 * $50, $44 * $5B, $44 * $5C, $44 * $6A, $44 * $6B
    .word $44 * $6C, $44 * $6D, $44 * $6E, $44 * $6F, $44 * $70, $44 * $71, $44 * $55, $44 * $51
    .word $44 * $72, $44 * $73, $44 * $57, $44 * $84, $44 * $85, $44 * $87, $44 * $88, $44 * $89
    .word $44 * $8A, $44 * $43, $44 * $8B, $44 * $8C, $44 * $8D, $44 * $8E, $44 * $8F, $44 * $90
    .word $44 * $91
.assert (* - BankStart) = $2302, error, "bank 0 map chunk offset table end"
    .incbin "bank0_a302_a368.bin"
; State-indexed vertical base seeds are multiplied by eight on the
; non-restored path. Valid state indices remain unverified.
InitialVerticalBaseSeeds:
    .byte $03, $28, $28, $28, $28, $1A, $1A, $1A ; CONTROL_INITIAL_VERTICAL_SEEDS
    .byte $1A, $1A, $1A, $10, $32, $0A, $08, $58
    .byte $00, $03, $00, $00, $00, $00
.assert (* - BankStart) = $237E, error, "bank 0 initial vertical seeds end"
; Twenty-two observed state entries select mapper and PPU-control bits. The
; code does not establish a runtime bound on the state index.
StateBankSelectors:
    .byte $0E, $00, $04, $00, $06, $08, $08, $08, $08, $08, $08, $0A, $0A, $0A, $0A, $0C, $0E, $0E, $FF, $FF, $08, $02 ; CONTROL_STATE_BANK_SELECTORS

; Encoded pointers to the locally supplied background and sprite palette
; streams, indexed by state. These addresses are metadata, not the assets.
BackgroundPalettePointers:
    .word $C83E, $C851, $C851, $C851 ; CONTROL_BACKGROUND_PALETTE_POINTERS
    .word $C83E, $C982, $C99D, $C9B8
    .word $C9D3, $C9EE, $CA09, $C923
    .word $C923, $C949, $C923, $C936
    .word $CA37, $C83E, $C851, $C851
    .word $CA09, $C877
SpritePalettePointers:
    .word $C83E, $C7F2, $C805, $C7F2 ; CONTROL_SPRITE_PALETTE_POINTERS
    .word $C82B, $C96F, $C96F, $C96F
    .word $CA24, $CA24, $CA24, $C8FD
    .word $C8FD, $C8FD, $C8FD, $C910
    .word $C83E, $C83E, $C83E, $C7F2
    .word $C95C, $C877
.assert (* - BankStart) = $23EC, error, "bank 0 state and palette pointer tables end"
; Each table has 22 two-byte starting addresses selected by $02. The target
; streams and valid runtime indices still require separate verification.
PositionRecordPointersA:
    .word PositionStreamA444 ; CONTROL_POSITION_POINTERS_A
    .word PositionStreamA5A4 ; index $01
    .word PositionStreamA7CC ; index $02
    .word PositionStreamA8C0 ; index $03
    .word PositionStreamA678 ; index $04
    .word PositionStreamAAF0 ; index $05
    .word PositionStreamABAC ; index $06
    .word PositionStreamACA0 ; index $07
    .word PositionStreamAD64 ; index $08
    .word PositionStreamAE80 ; index $09
    .word PositionStreamAF64 ; index $0A
    .word PositionStreamB14C ; index $0B
    .word PositionStreamB210 ; index $0C
    .word PositionStreamB29C ; index $0D
    .word PositionStreamB320 ; index $0E
    .word PositionStreamB3EC ; index $0F
    .word PositionStreamA458 ; index $10
    .word PositionStreamB4A0 ; index $11
    .word PositionStreamA46C ; index $12
    .word PositionStreamB4B4 ; index $13
    .word PositionStreamB4D4 ; index $14
    .word PositionStreamB4F8 ; index $15
.assert (* - BankStart) = $2418, error, "bank 0 first position pointers end"
PositionRecordPointersB:
    .word PositionStreamA444 ; CONTROL_POSITION_POINTERS_B
    .word PositionStreamA480 ; index $01
    .word PositionStreamA480 ; index $02
    .word PositionStreamA480 ; index $03
    .word PositionStreamA480 ; index $04
    .word PositionStreamAAA4 ; index $05
    .word PositionStreamAAB8 ; index $06
    .word PositionStreamAAD4 ; index $07
    .word PositionStreamAAB8 ; index $08
    .word PositionStreamAAA4 ; index $09
    .word PositionStreamAAD4 ; index $0A
    .word PositionStreamB0C0 ; index $0B
    .word PositionStreamB0FC ; index $0C
    .word PositionStreamB110 ; index $0D
    .word PositionStreamB124 ; index $0E
    .word PositionStreamB140 ; index $0F
    .word PositionStreamB4C8 ; index $10
    .word PositionStreamB4C8 ; index $11
    .word PositionStreamB4C8 ; index $12
    .word PositionStreamB4C8 ; index $13
    .word PositionStreamB4C8 ; index $14
    .word PositionStreamB4C8 ; index $15
.assert (* - BankStart) = $2444, error, "bank 0 second position pointers end"

; Sorted, sentinel-terminated position streams shared by the two pointer tables.
; Record type and parameters are interpreted by the consuming slot/event path.
; Field meanings beyond the lookup code remain provisional.
PositionStreamA444:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0000, $0000, $F0, $00, $10, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A444
    PositionRecordEnd
.assert (* - BankStart) = $2458, error, "bank 0 position stream $A444 end"

PositionStreamA458:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $001F, $0000, $F0, $09, $00, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A458
    PositionRecordEnd
.assert (* - BankStart) = $246C, error, "bank 0 position stream $A458 end"

PositionStreamA46C:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $000A, $0000, $F0, $13, $12, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A46C
    PositionRecordEnd
.assert (* - BankStart) = $2480, error, "bank 0 position stream $A46C end"

PositionStreamA480:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0003, $8000, $01, $3E, $01, $00, $00, $00 ; CONTROL_POSITION_STREAM_A480
    PositionRecord $000B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $001B, $8000, $32, $36, $80, $00, $08, $08
    PositionRecord $0023, $8000, $22, $26, $80, $02, $08, $08
    PositionRecord $003B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0043, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $004B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0053, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $005B, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $0063, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $006B, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $0073, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $007B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0083, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $008B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0093, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $009E, $8000, $31, $3C, $01, $00, $00, $00
    PositionRecord $00D3, $8000, $23, $25, $0D, $00, $08, $08
    PositionRecord $00D5, $8000, $23, $25, $0D, $00, $08, $08
    PositionRecord $0113, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $011B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0123, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $012B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0133, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $0153, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $015B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0163, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $016B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0173, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $017B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0181, $8000, $1A, $46, $01, $00, $00, $00
    PositionRecord $0189, $8000, $34, $3D, $01, $00, $00, $00
    PositionRecord $018B, $8000, $22, $26, $00, $83, $08, $08
    PositionRecord $0193, $8000, $32, $36, $00, $81, $08, $08
    PositionRecord $0199, $8000, $1E, $46, $01, $00, $00, $00
    PositionRecordEnd
.assert (* - BankStart) = $25A4, error, "bank 0 position stream $A480 end"

PositionStreamA5A4:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A5A4
    PositionRecord $0005, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0014, $0000, $F0, $0E, $3C, $00, $FF, $02
    PositionRecord $0018, $0000, $F0, $1B, $16, $00, $FF, $0E
    PositionRecord $0024, $0000, $F0, $1A, $22, $00, $FF, $0F
    PositionRecord $0040, $0000, $F0, $19, $3C, $00, $FF, $03
    PositionRecord $005C, $0000, $F0, $0A, $3C, $13, $FF, $01
    PositionRecord $0087, $0000, $F0, $11, $3A, $00, $FF, $04
    PositionRecord $00B9, $0000, $F0, $2B, $34, $00, $FF, $06
    PositionRecord $00BE, $0000, $F0, $0A, $3C, $0C, $FF, $96
    PositionRecord $00CC, $0000, $F0, $0A, $20, $0E, $FF, $D2
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00DD, $0000, $F0, $18, $30, $00, $FF, $05
    PositionRecord $00E1, $0000, $F0, $1C, $19, $00, $FF, $07
    PositionRecord $00E2, $0000, $F0, $0A, $2C, $1A, $FF, $08
    PositionRecord $00F4, $0000, $F0, $0F, $37, $00, $FF, $3E
    PositionRecord $00F6, $0000, $F0, $15, $13, $00, $FF, $09
    PositionRecord $0126, $0000, $F0, $0A, $3C, $17, $FF, $0A
    PositionRecord $0127, $0000, $F0, $22, $34, $00, $FF, $3F
    PositionRecord $013E, $0000, $F0, $2A, $3C, $00, $FF, $0B
    PositionRecord $0160, $0000, $F0, $1D, $2A, $00, $FF, $0C
    PositionRecord $016F, $0000, $F0, $12, $3A, $00, $FF, $0D
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecord $0194, $0000, $F0, $0A, $3C, $13, $FF, $E9
    PositionRecordEnd
.assert (* - BankStart) = $2678, error, "bank 0 position stream $A5A4 end"

PositionStreamA678:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A678
    PositionRecord $0003, $0000, $F0, $37, $3C, $00, $FF, $10
    PositionRecord $0004, $0000, $F0, $67, $28, $00, $FF, $FF
    PositionRecord $0008, $0000, $F0, $08, $3C, $00, $FF, $FF
    PositionRecord $000A, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0022, $0000, $F0, $07, $30, $00, $FF, $FF
    PositionRecord $0024, $0000, $F0, $0A, $33, $0C, $FF, $01
    PositionRecord $0027, $0000, $F0, $60, $16, $00, $FF, $40
    PositionRecord $0039, $0000, $F0, $38, $1E, $00, $FF, $11
    PositionRecord $0041, $0000, $F0, $2F, $3C, $00, $FF, $12
    PositionRecord $0058, $0000, $F0, $0A, $3C, $06, $FF, $8C
    PositionRecord $005E, $0000, $F0, $07, $34, $00, $FF, $FF
    PositionRecord $0078, $0000, $F0, $07, $30, $00, $FF, $FF
    PositionRecord $0081, $0000, $F0, $33, $20, $00, $FF, $13
    PositionRecord $008D, $0000, $F0, $2E, $31, $00, $FF, $14
    PositionRecord $00A2, $0000, $F0, $23, $13, $00, $FF, $15
    PositionRecord $00A8, $0000, $F0, $56, $3C, $00, $FF, $52
    PositionRecord $00B4, $0000, $F0, $30, $34, $00, $FF, $17
    PositionRecord $00B5, $0000, $F0, $07, $18, $00, $FF, $FF
    PositionRecord $00B6, $0000, $F0, $07, $30, $00, $FF, $FF
    PositionRecord $00BC, $0000, $F0, $32, $24, $00, $FF, $18
    PositionRecord $00CC, $0000, $F0, $07, $20, $00, $FF, $FF
    PositionRecord $00D3, $0000, $F0, $60, $30, $00, $FF, $42
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00DB, $0000, $F0, $07, $20, $00, $FF, $FF
    PositionRecord $00DC, $0000, $F0, $0A, $34, $19, $FF, $19
    PositionRecord $00E1, $0000, $F0, $34, $0B, $00, $FF, $1A
    PositionRecord $00E6, $0000, $F0, $31, $1C, $00, $FF, $1B
    PositionRecord $00F2, $0000, $F0, $07, $18, $00, $FF, $FF
    PositionRecord $00F5, $0000, $F0, $07, $2F, $00, $FF, $FF
    PositionRecord $0101, $0000, $F0, $39, $1C, $00, $FF, $1C
    PositionRecord $0126, $0000, $F0, $24, $3C, $00, $FF, $1D
    PositionRecord $0135, $0000, $F0, $36, $3C, $00, $FF, $1E
    PositionRecord $0136, $0000, $F0, $07, $31, $00, $FF, $FF
    PositionRecord $0151, $0000, $F0, $35, $39, $00, $FF, $1F
    PositionRecord $0167, $0000, $F0, $07, $2E, $00, $FF, $FF
    PositionRecord $0168, $0000, $F0, $57, $3C, $00, $FF, $4D
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecord $0194, $0000, $F0, $0A, $3C, $24, $FF, $A2
    PositionRecord $0195, $0000, $F0, $0A, $1C, $1F, $FF, $A3
    PositionRecordEnd
.assert (* - BankStart) = $27CC, error, "bank 0 position stream $A678 end"

PositionStreamA7CC:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A7CC
    PositionRecord $0005, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0006, $0000, $F0, $43, $2C, $00, $FF, $20
    PositionRecord $001C, $0000, $F0, $3E, $2A, $00, $FF, $22
    PositionRecord $002A, $0000, $F0, $4E, $3C, $00, $FF, $23
    PositionRecord $0049, $0000, $F0, $14, $28, $00, $FF, $FF
    PositionRecord $0056, $0000, $F0, $0F, $31, $00, $FF, $43
    PositionRecord $0057, $0000, $F0, $44, $16, $00, $FF, $9B
    PositionRecord $0061, $0000, $F0, $4B, $22, $00, $FF, $25
    PositionRecord $0071, $0000, $F0, $49, $1E, $00, $FF, $26
    PositionRecord $0079, $0000, $F0, $0A, $2E, $26, $FF, $27
    PositionRecord $0086, $0000, $F0, $62, $24, $00, $FF, $FF
    PositionRecord $008F, $0000, $F0, $14, $1A, $00, $FF, $FF
    PositionRecord $00A4, $0000, $F0, $14, $30, $00, $FF, $44
    PositionRecord $00B1, $0000, $F0, $3D, $3C, $00, $FF, $29
    PositionRecord $00BD, $0000, $F0, $14, $18, $00, $FF, $45
    PositionRecord $00C2, $0000, $F0, $3C, $24, $00, $FF, $2B
    PositionRecord $00C6, $0000, $F0, $4A, $0D, $00, $FF, $2C
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00E3, $0000, $F0, $4F, $3C, $00, $FF, $2D
    PositionRecord $0116, $0000, $F0, $48, $2E, $00, $FF, $2E
    PositionRecord $0129, $0000, $F0, $0A, $1E, $11, $FF, $2F
    PositionRecord $0136, $0000, $F0, $61, $31, $00, $FF, $46
    PositionRecord $0150, $0000, $F0, $42, $30, $00, $FF, $30
    PositionRecord $0157, $0000, $F0, $3F, $26, $00, $FF, $31
    PositionRecord $0161, $0000, $F0, $14, $30, $00, $FF, $FF
    PositionRecord $0166, $0000, $F0, $45, $24, $00, $FF, $32
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecordEnd
.assert (* - BankStart) = $28C0, error, "bank 0 position stream $A7CC end"

PositionStreamA8C0:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF ; CONTROL_POSITION_STREAM_A8C0
    PositionRecord $0005, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0007, $0000, $F0, $2C, $1F, $00, $FF, $53
    PositionRecord $0009, $0000, $F0, $0A, $3C, $0D, $FF, $54
    PositionRecord $000A, $0000, $F0, $69, $3C, $00, $FF, $55
    PositionRecord $000B, $0000, $F0, $07, $20, $00, $FF, $FF
    PositionRecord $0020, $0000, $F0, $0A, $16, $04, $FF, $56
    PositionRecord $0029, $0000, $F0, $68, $3C, $00, $FF, $57
    PositionRecord $002A, $0000, $F0, $2C, $13, $00, $FF, $58
    PositionRecord $0046, $0000, $F0, $07, $34, $00, $FF, $FF
    PositionRecord $0048, $0000, $F0, $68, $3C, $00, $FF, $5A
    PositionRecord $0049, $0000, $F0, $2D, $1F, $00, $FF, $5B
    PositionRecord $0061, $0000, $F0, $5C, $30, $00, $FF, $5D
    PositionRecord $0070, $0000, $F0, $2C, $28, $00, $FF, $5E
    PositionRecord $0071, $0000, $F0, $5F, $34, $00, $FF, $5F
    PositionRecord $0078, $0000, $F0, $0A, $3C, $33, $FF, $A1
    PositionRecord $0091, $0000, $F0, $5F, $18, $00, $FF, $62
    PositionRecord $0096, $0000, $F0, $5F, $22, $00, $FF, $63
    PositionRecord $00A2, $0000, $F0, $68, $0D, $00, $FF, $64
    PositionRecord $00A7, $0000, $F0, $69, $24, $00, $FF, $65
    PositionRecord $00A8, $0000, $F0, $68, $13, $00, $FF, $66
    PositionRecord $00AB, $0000, $F0, $69, $34, $00, $FF, $67
    PositionRecord $00BC, $0000, $F0, $07, $30, $00, $FF, $FF
    PositionRecord $00BF, $0000, $F0, $68, $24, $00, $FF, $68
    PositionRecord $00C0, $0000, $F0, $2C, $22, $00, $FF, $69
    PositionRecord $00CB, $0000, $F0, $07, $37, $00, $FF, $FF
    PositionRecord $00CD, $0000, $F0, $69, $2C, $00, $FF, $6A
    PositionRecord $00CE, $0000, $F0, $07, $11, $00, $FF, $FF
    PositionRecord $00D3, $0000, $F0, $07, $28, $00, $FF, $FF
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00DA, $0000, $F0, $0A, $28, $15, $FF, $6B
    PositionRecord $00DC, $0000, $F0, $5C, $19, $00, $FF, $6C
    PositionRecord $00DD, $0000, $F0, $5F, $30, $00, $FF, $6D
    PositionRecord $00EE, $0000, $F0, $69, $1C, $00, $FF, $6E
    PositionRecord $00F2, $0000, $F0, $5F, $37, $00, $FF, $6F
    PositionRecord $00F3, $0000, $F0, $07, $31, $00, $FF, $FF
    PositionRecord $00F5, $0000, $F0, $0A, $37, $01, $FF, $71
    PositionRecord $00F9, $0000, $F0, $69, $2C, $00, $FF, $72
    PositionRecord $00FA, $0000, $F0, $2C, $0B, $00, $FF, $73
    PositionRecord $0101, $0000, $F0, $68, $13, $00, $FF, $74
    PositionRecord $0119, $0000, $F0, $5F, $2C, $00, $FF, $75
    PositionRecord $011A, $0000, $F0, $68, $3C, $00, $FF, $76
    PositionRecord $0121, $0000, $F0, $07, $30, $00, $FF, $FF
    PositionRecord $0136, $0000, $F0, $2D, $2F, $00, $FF, $78
    PositionRecord $0144, $0000, $F0, $69, $3C, $00, $FF, $79
    PositionRecord $0151, $0000, $F0, $5C, $1E, $00, $FF, $7A
    PositionRecord $0156, $0000, $F0, $07, $16, $00, $FF, $FF
    PositionRecord $015D, $0000, $F0, $2C, $16, $00, $FF, $7B
    PositionRecord $015E, $0000, $F0, $29, $3C, $00, $FF, $7C
    PositionRecord $0168, $0000, $F0, $5F, $24, $00, $FF, $7D
    PositionRecord $016C, $0000, $F0, $5C, $3C, $00, $FF, $7F
    PositionRecord $0170, $0000, $F0, $07, $1A, $00, $FF, $FF
    PositionRecord $0177, $0000, $F0, $5C, $16, $00, $FF, $80
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecord $0185, $0000, $F0, $5C, $34, $00, $FF, $82
    PositionRecord $0190, $0000, $F0, $0A, $3C, $11, $FF, $A0
    PositionRecord $0192, $0000, $F0, $0A, $1C, $02, $FF, $83
    PositionRecord $0195, $0000, $F0, $5C, $44, $00, $FF, $84
    PositionRecordEnd
.assert (* - BankStart) = $2AA4, error, "bank 0 position stream $A8C0 end"

PositionStreamAAA4:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0112, $8000, $01, $38, $07, $00, $00, $00 ; CONTROL_POSITION_STREAM_AAA4
    PositionRecordEnd
.assert (* - BankStart) = $2AB8, error, "bank 0 position stream $AAA4 end"

PositionStreamAAB8:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $000B, $8000, $0F, $19, $01, $00, $00, $00 ; CONTROL_POSITION_STREAM_AAB8
    PositionRecord $0111, $8000, $01, $38, $07, $00, $00, $00
    PositionRecordEnd
.assert (* - BankStart) = $2AD4, error, "bank 0 position stream $AAB8 end"

PositionStreamAAD4:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $000B, $8000, $0F, $18, $01, $00, $00, $00 ; CONTROL_POSITION_STREAM_AAD4
    PositionRecord $0120, $8000, $01, $38, $07, $00, $00, $00
    PositionRecordEnd
.assert (* - BankStart) = $2AF0, error, "bank 0 position stream $AAD4 end"

PositionStreamAAF0:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF ; CONTROL_POSITION_STREAM_AAF0
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000C, $0000, $F0, $6A, $2E, $00, $FF, $01
    PositionRecord $002C, $0000, $F0, $63, $2F, $00, $FF, $02
    PositionRecord $0040, $0000, $F0, $63, $2B, $00, $FF, $03
    PositionRecord $0045, $0000, $F0, $63, $18, $00, $FF, $04
    PositionRecord $004B, $0000, $F0, $6C, $2A, $00, $FF, $05
    PositionRecord $0052, $0000, $F0, $0A, $11, $08, $FF, $6F
    PositionRecord $005A, $0000, $F0, $63, $12, $00, $FF, $06
    PositionRecord $006D, $0000, $F0, $6C, $11, $00, $FF, $07
    PositionRecord $0074, $0000, $F0, $6C, $2A, $00, $FF, $08
    PositionRecord $0087, $0000, $F0, $63, $2F, $00, $FF, $09
    PositionRecord $009D, $0000, $F0, $6C, $16, $00, $FF, $0A
    PositionRecord $00A4, $0000, $F0, $0A, $16, $14, $FF, $71
    PositionRecord $00AF, $0000, $F0, $02, $18, $00, $FF, $0B
    PositionRecord $00B0, $0000, $F0, $02, $2C, $00, $FF, $0C
    PositionRecord $00BD, $0000, $F0, $63, $2F, $00, $FF, $0D
    PositionRecord $00C7, $0000, $F0, $6C, $2A, $00, $FF, $0E
    PositionRecord $00CA, $0000, $F0, $0A, $2E, $09, $FF, $70
    PositionRecord $00EB, $0000, $F0, $6C, $2A, $00, $FF, $0F
    PositionRecord $00FC, $0000, $F0, $02, $28, $00, $FF, $10
    PositionRecord $010B, $0000, $F0, $02, $2C, $00, $FF, $11
    PositionRecordEnd
.assert (* - BankStart) = $2BAC, error, "bank 0 position stream $AAF0 end"

PositionStreamABAC:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF ; CONTROL_POSITION_STREAM_ABAC
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000A, $0000, $F0, $0A, $1E, $13, $FF, $7B
    PositionRecord $000B, $0000, $F0, $6A, $24, $00, $FF, $12
    PositionRecord $0010, $0000, $F0, $6C, $16, $00, $FF, $13
    PositionRecord $0013, $0000, $F0, $63, $0F, $00, $FF, $14
    PositionRecord $0015, $0000, $F0, $6C, $2C, $00, $FF, $15
    PositionRecord $0027, $0000, $F0, $14, $21, $00, $FF, $16
    PositionRecord $0032, $0000, $F0, $6C, $09, $00, $FF, $17
    PositionRecord $0046, $0000, $F0, $63, $27, $00, $FF, $18
    PositionRecord $004D, $0000, $F0, $0A, $2E, $1D, $FF, $79
    PositionRecord $0052, $0000, $F0, $6C, $22, $00, $FF, $19
    PositionRecord $005F, $0000, $F0, $6C, $1A, $00, $FF, $FF
    PositionRecord $0068, $0000, $F0, $63, $2F, $00, $FF, $1A
    PositionRecord $006D, $0000, $F0, $6C, $2E, $00, $FF, $1C
    PositionRecord $0075, $0000, $F0, $6C, $2A, $00, $FF, $1D
    PositionRecord $007B, $0000, $F0, $02, $0F, $00, $FF, $FF
    PositionRecord $0085, $0000, $F0, $02, $2C, $00, $FF, $1E
    PositionRecord $008A, $0000, $F0, $14, $1C, $00, $FF, $FF
    PositionRecord $0096, $0000, $F0, $6C, $16, $00, $FF, $1B
    PositionRecord $00A1, $0000, $F0, $14, $28, $00, $FF, $1F
    PositionRecord $00AF, $0000, $F0, $6C, $2E, $00, $FF, $FF
    PositionRecord $00B5, $0000, $F0, $6C, $22, $00, $FF, $FF
    PositionRecord $00B9, $0000, $F0, $14, $08, $00, $FF, $20
    PositionRecord $00C2, $0000, $F0, $6C, $0B, $00, $FF, $21
    PositionRecord $00C6, $0000, $F0, $0A, $2E, $0F, $FF, $7A
    PositionRecord $00D7, $0000, $F0, $02, $24, $00, $FF, $22
    PositionRecord $00F1, $0000, $F0, $6C, $2E, $00, $FF, $23
    PositionRecord $010A, $0000, $F0, $6C, $2E, $00, $FF, $24
    PositionRecordEnd
.assert (* - BankStart) = $2CA0, error, "bank 0 position stream $ABAC end"

PositionStreamACA0:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF ; CONTROL_POSITION_STREAM_ACA0
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $0015, $0000, $F0, $02, $16, $00, $FF, $25
    PositionRecord $001A, $0000, $F0, $6A, $1E, $00, $FF, $26
    PositionRecord $0020, $0000, $F0, $70, $0E, $00, $FF, $27
    PositionRecord $003B, $0000, $F0, $0A, $2C, $14, $FF, $83
    PositionRecord $0040, $0000, $F0, $14, $0D, $00, $FF, $FF
    PositionRecord $0048, $0000, $F0, $02, $18, $00, $FF, $28
    PositionRecord $0059, $0000, $F0, $6C, $22, $01, $FF, $FF
    PositionRecord $005A, $0000, $F0, $6C, $2E, $01, $FF, $29
    PositionRecord $006B, $0000, $F0, $14, $14, $00, $FF, $2A
    PositionRecord $007A, $0000, $F0, $02, $24, $00, $FF, $2B
    PositionRecord $0082, $0000, $F0, $6C, $2A, $02, $FF, $FF
    PositionRecord $0087, $0000, $F0, $70, $26, $00, $FF, $2C
    PositionRecord $0098, $0000, $F0, $6C, $2A, $01, $FF, $2D
    PositionRecord $00AD, $0000, $F0, $6C, $26, $01, $FF, $FF
    PositionRecord $00AF, $0000, $F0, $14, $16, $00, $FF, $FF
    PositionRecord $00C8, $0000, $F0, $02, $18, $00, $FF, $2E
    PositionRecord $00CD, $0000, $F0, $0A, $2E, $16, $FF, $84
    PositionRecord $00DC, $0000, $F0, $6C, $16, $01, $FF, $2F
    PositionRecord $00EC, $0000, $F0, $14, $0D, $00, $FF, $FF
    PositionRecord $0109, $0000, $F0, $02, $2A, $00, $FF, $30
    PositionRecord $0115, $0000, $F0, $6C, $2E, $01, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $2D64, error, "bank 0 position stream $ACA0 end"

PositionStreamAD64:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF ; CONTROL_POSITION_STREAM_AD64
    PositionRecord $0003, $0000, $F0, $6C, $2E, $01, $FF, $31
    PositionRecord $0007, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $000A, $0000, $F0, $6C, $1E, $01, $FF, $32
    PositionRecord $000D, $0000, $F0, $01, $26, $00, $FF, $FF
    PositionRecord $000F, $0000, $F0, $63, $0F, $00, $FF, $33
    PositionRecord $0016, $0000, $F0, $6A, $2E, $00, $FF, $34
    PositionRecord $0024, $0000, $F0, $0A, $2E, $1F, $FF, $8D
    PositionRecord $0025, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $0037, $0000, $F0, $6C, $2E, $01, $FF, $35
    PositionRecord $0038, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $003C, $0000, $F0, $02, $28, $00, $FF, $FF
    PositionRecord $0046, $0000, $F0, $02, $24, $00, $FF, $36
    PositionRecord $005C, $0000, $F0, $02, $2C, $00, $FF, $37
    PositionRecord $005D, $0000, $F0, $6C, $14, $01, $FF, $38
    PositionRecord $005F, $0000, $F0, $65, $1C, $00, $FF, $FF
    PositionRecord $0068, $0000, $F0, $6C, $0D, $01, $FF, $39
    PositionRecord $006C, $0000, $F0, $6C, $2E, $01, $FF, $FF
    PositionRecord $007B, $0000, $F0, $0A, $11, $22, $FF, $8E
    PositionRecord $0080, $0000, $F0, $02, $2C, $00, $FF, $3A
    PositionRecord $0082, $0000, $F0, $02, $1D, $00, $FF, $FF
    PositionRecord $008D, $0000, $F0, $65, $24, $00, $FF, $FF
    PositionRecord $0092, $0000, $F0, $6C, $1F, $01, $FF, $FF
    PositionRecord $0094, $0000, $F0, $6C, $2E, $01, $FF, $3B
    PositionRecord $00A3, $0000, $F0, $02, $1C, $00, $FF, $3C
    PositionRecord $00B5, $0000, $F0, $65, $24, $00, $FF, $FF
    PositionRecord $00B6, $0000, $F0, $02, $2C, $00, $FF, $3D
    PositionRecord $00BC, $0000, $F0, $6C, $0C, $01, $FF, $3E
    PositionRecord $00C3, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $00C6, $0000, $F0, $6C, $22, $01, $FF, $3F
    PositionRecord $00D8, $0000, $F0, $14, $1C, $00, $FF, $FF
    PositionRecord $00F5, $0000, $F0, $02, $2C, $00, $FF, $40
    PositionRecord $0108, $0000, $F0, $6C, $2E, $01, $FF, $41
    PositionRecord $010D, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $2E80, error, "bank 0 position stream $AD64 end"

PositionStreamAE80:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF ; CONTROL_POSITION_STREAM_AE80
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000C, $0000, $F0, $6A, $2E, $00, $FF, $42
    PositionRecord $001D, $0000, $F0, $02, $2C, $00, $FF, $43
    PositionRecord $002B, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $0040, $0000, $F0, $02, $28, $00, $FF, $44
    PositionRecord $0059, $0000, $F0, $6C, $2E, $02, $FF, $45
    PositionRecord $005E, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $006B, $0000, $F0, $02, $25, $00, $FF, $46
    PositionRecord $006C, $0000, $F0, $14, $1C, $00, $FF, $FF
    PositionRecord $0075, $0000, $F0, $6C, $2A, $01, $FF, $FF
    PositionRecord $007E, $0000, $F0, $02, $24, $00, $FF, $FF
    PositionRecord $0099, $0000, $F0, $63, $2F, $00, $FF, $47
    PositionRecord $00A1, $0000, $F0, $65, $18, $00, $FF, $FF
    PositionRecord $00A3, $0000, $F0, $0A, $16, $23, $FF, $97
    PositionRecord $00A5, $0000, $F0, $02, $26, $00, $FF, $FF
    PositionRecord $00AB, $0000, $F0, $0A, $24, $20, $FF, $98
    PositionRecord $00AD, $0000, $F0, $63, $2F, $00, $FF, $48
    PositionRecord $00B1, $0000, $F0, $6C, $1A, $02, $FF, $FF
    PositionRecord $00BD, $0000, $F0, $65, $20, $00, $FF, $FF
    PositionRecord $00C1, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $00CA, $0000, $F0, $14, $19, $00, $FF, $FF
    PositionRecord $00CC, $0000, $F0, $02, $2C, $00, $FF, $49
    PositionRecord $00DB, $0000, $F0, $6C, $2E, $02, $FF, $4A
    PositionRecord $00E3, $0000, $F0, $6C, $27, $02, $FF, $FF
    PositionRecord $00ED, $0000, $F0, $65, $2C, $00, $FF, $FF
    PositionRecord $00FD, $0000, $F0, $02, $28, $00, $FF, $4B
    PositionRecordEnd
.assert (* - BankStart) = $2F64, error, "bank 0 position stream $AE80 end"

PositionStreamAF64:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF ; CONTROL_POSITION_STREAM_AF64
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000C, $0000, $F0, $02, $0C, $00, $FF, $4C
    PositionRecord $0013, $0000, $F0, $6A, $1C, $00, $FF, $4D
    PositionRecord $0015, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $0017, $0000, $F0, $65, $10, $00, $FF, $FF
    PositionRecord $002A, $0000, $F0, $02, $0C, $00, $FF, $4E
    PositionRecord $0039, $0000, $F0, $65, $14, $00, $FF, $FF
    PositionRecord $0047, $0000, $F0, $02, $2C, $00, $FF, $4F
    PositionRecord $0049, $0000, $F0, $02, $18, $00, $FF, $FF
    PositionRecord $0051, $0000, $F0, $0A, $1E, $25, $FF, $A1
    PositionRecord $0058, $0000, $F0, $70, $22, $00, $FF, $50
    PositionRecord $0059, $0000, $F0, $65, $24, $00, $FF, $FF
    PositionRecord $005A, $0000, $F0, $6C, $2E, $00, $FF, $51
    PositionRecord $005E, $0000, $F0, $14, $18, $00, $FF, $FF
    PositionRecord $006F, $0000, $F0, $65, $28, $00, $FF, $FF
    PositionRecord $0078, $0000, $F0, $6C, $01, $02, $FF, $52
    PositionRecord $007A, $0000, $F0, $02, $24, $00, $FF, $FF
    PositionRecord $0081, $0000, $F0, $6C, $2C, $02, $FF, $53
    PositionRecord $0089, $0000, $F0, $02, $24, $00, $FF, $54
    PositionRecord $008D, $0000, $F0, $65, $28, $00, $FF, $FF
    PositionRecord $0094, $0000, $F0, $6C, $2A, $02, $FF, $55
    PositionRecord $0097, $0000, $F0, $6C, $2A, $00, $FF, $56
    PositionRecord $009D, $0000, $F0, $02, $24, $00, $FF, $57
    PositionRecord $00A1, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecord $00AB, $0000, $F0, $65, $28, $00, $FF, $FF
    PositionRecord $00B4, $0000, $F0, $14, $19, $00, $FF, $FF
    PositionRecord $00C5, $0000, $F0, $65, $1C, $00, $FF, $FF
    PositionRecord $00CD, $0000, $F0, $02, $26, $00, $FF, $58
    PositionRecord $00D7, $0000, $F0, $6C, $0F, $02, $FF, $59
    PositionRecord $00D9, $0000, $F0, $65, $18, $00, $FF, $FF
    PositionRecord $00DF, $0000, $F0, $6C, $2E, $00, $FF, $5A
    PositionRecord $00E0, $0000, $F0, $6C, $16, $02, $FF, $FF
    PositionRecord $00E4, $0000, $F0, $0A, $2E, $2A, $FF, $A2
    PositionRecord $00F1, $0000, $F0, $14, $1E, $00, $FF, $5B
    PositionRecord $00FB, $0000, $F0, $65, $28, $00, $FF, $FF
    PositionRecord $0108, $0000, $F0, $6C, $2A, $02, $FF, $5C
    PositionRecord $0109, $0000, $F0, $02, $28, $00, $FF, $58
    PositionRecord $010D, $0000, $F0, $14, $1C, $00, $FF, $5D
    PositionRecord $0110, $0000, $F0, $02, $26, $00, $FF, $5E
    PositionRecord $0114, $0000, $F0, $14, $22, $00, $FF, $FF
    PositionRecord $0117, $0000, $F0, $65, $30, $00, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $30C0, error, "bank 0 position stream $AF64 end"

PositionStreamB0C0:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0030, $8000, $14, $25, $01, $00, $00, $00 ; CONTROL_POSITION_STREAM_B0C0
    PositionRecord $0040, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $0078, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $0090, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $00C0, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $00D0, $8000, $01, $18, $09, $00, $00, $00
    PositionRecordEnd
.assert (* - BankStart) = $30FC, error, "bank 0 position stream $B0C0 end"

PositionStreamB0FC:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0043, $8000, $14, $28, $09, $00, $00, $00 ; CONTROL_POSITION_STREAM_B0FC
    PositionRecordEnd
.assert (* - BankStart) = $3110, error, "bank 0 position stream $B0FC end"

PositionStreamB110:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0084, $8000, $01, $10, $09, $00, $00, $00 ; CONTROL_POSITION_STREAM_B110
    PositionRecordEnd
.assert (* - BankStart) = $3124, error, "bank 0 position stream $B110 end"

PositionStreamB124:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0070, $8000, $1C, $2D, $01, $00, $00, $00 ; CONTROL_POSITION_STREAM_B124
    PositionRecord $00F4, $8000, $01, $20, $09, $00, $00, $00
    PositionRecordEnd
.assert (* - BankStart) = $3140, error, "bank 0 position stream $B124 end"

PositionStreamB140:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_POSITION_STREAM_B140
    PositionRecordEnd
.assert (* - BankStart) = $314C, error, "bank 0 position stream $B140 end"

PositionStreamB14C:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $13, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B14C
    PositionRecord $0004, $0000, $F0, $01, $22, $00, $FF, $FF
    PositionRecord $0006, $0000, $F0, $0A, $24, $0E, $FF, $BE
    PositionRecord $0009, $0000, $F0, $6E, $19, $00, $FF, $01
    PositionRecord $001C, $0000, $F0, $6E, $1C, $00, $FF, $02
    PositionRecord $0023, $0000, $F0, $6F, $24, $00, $FF, $03
    PositionRecord $002E, $0000, $F0, $6E, $1E, $00, $FF, $04
    PositionRecord $0042, $0000, $F0, $6E, $1D, $00, $FF, $05
    PositionRecord $004F, $0000, $F0, $71, $14, $00, $FF, $43
    PositionRecord $0054, $0000, $F0, $6E, $1C, $00, $FF, $06
    PositionRecord $005B, $0000, $F0, $6F, $0E, $00, $FF, $07
    PositionRecord $0064, $0000, $F0, $6F, $24, $00, $FF, $08
    PositionRecord $0067, $0000, $F0, $0A, $16, $21, $FF, $09
    PositionRecord $007A, $0000, $F0, $6E, $1D, $00, $FF, $0A
    PositionRecord $008B, $0000, $F0, $52, $22, $00, $FF, $0B
    PositionRecord $008F, $0000, $F0, $0A, $24, $13, $FF, $49
    PositionRecord $00A0, $0000, $F0, $50, $0E, $00, $FF, $44
    PositionRecord $00A1, $0000, $F0, $6E, $19, $00, $FF, $0D
    PositionRecord $00A4, $0000, $F0, $6F, $0E, $00, $FF, $0E
    PositionRecord $00A9, $0000, $F0, $0A, $19, $2C, $FF, $0F
    PositionRecord $00AB, $0000, $F0, $6E, $1C, $00, $FF, $10
    PositionRecord $00BE, $0000, $F0, $6E, $1E, $00, $FF, $11
    PositionRecord $00D0, $0000, $F0, $6B, $11, $00, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $3210, error, "bank 0 position stream $B14C end"

PositionStreamB210:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $35, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B210
    PositionRecord $0004, $0000, $F0, $01, $42, $00, $FF, $FF
    PositionRecord $0005, $0000, $F0, $50, $26, $00, $FF, $12
    PositionRecord $0006, $0000, $F0, $0A, $37, $0C, $FF, $48
    PositionRecord $000B, $0000, $F0, $50, $17, $00, $FF, $13
    PositionRecord $0019, $0000, $F0, $50, $31, $00, $FF, $14
    PositionRecord $001A, $0000, $F0, $6F, $0E, $00, $FF, $15
    PositionRecord $001B, $0000, $F0, $6F, $3A, $00, $FF, $16
    PositionRecord $0025, $0000, $F0, $50, $21, $00, $FF, $17
    PositionRecord $0027, $0000, $F0, $50, $0E, $00, $FF, $18
    PositionRecord $002D, $0000, $F0, $0A, $2F, $1C, $FF, $19
    PositionRecord $002E, $0000, $F0, $50, $39, $00, $FF, $1A
    PositionRecord $0039, $0000, $F0, $6F, $1E, $00, $FF, $1B
    PositionRecord $0042, $0000, $F0, $50, $26, $00, $FF, $1C
    PositionRecord $0043, $0000, $F0, $6B, $22, $00, $FF, $FF
    PositionRecord $004A, $0000, $F0, $6F, $39, $00, $FF, $1D
    PositionRecordEnd
.assert (* - BankStart) = $329C, error, "bank 0 position stream $B210 end"

PositionStreamB29C:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $0D, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B29C
    PositionRecord $0004, $0000, $F0, $01, $16, $00, $FF, $FF
    PositionRecord $001C, $0000, $F0, $50, $0E, $00, $FF, $1E
    PositionRecord $0020, $0000, $F0, $6F, $1C, $00, $FF, $1F
    PositionRecord $0038, $0000, $F0, $50, $0E, $00, $FF, $20
    PositionRecord $0040, $0000, $F0, $6F, $12, $00, $FF, $21
    PositionRecord $0044, $0000, $F0, $52, $19, $00, $FF, $22
    PositionRecord $004C, $0000, $F0, $50, $0A, $00, $FF, $23
    PositionRecord $0051, $0000, $F0, $51, $0E, $00, $FF, $46
    PositionRecord $0053, $0000, $F0, $6F, $16, $00, $FF, $24
    PositionRecord $0054, $0000, $F0, $6F, $0E, $00, $FF, $25
    PositionRecord $0062, $0000, $F0, $0A, $0E, $14, $FF, $26
    PositionRecord $006B, $0000, $F0, $51, $12, $00, $FF, $47
    PositionRecord $0079, $0000, $F0, $52, $0C, $00, $FF, $27
    PositionRecord $0084, $0000, $F0, $6B, $09, $00, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $3320, error, "bank 0 position stream $B29C end"

PositionStreamB320:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $0F, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B320
    PositionRecord $0004, $0000, $F0, $01, $14, $00, $FF, $FF
    PositionRecord $000B, $0000, $F0, $71, $1E, $00, $FF, $28
    PositionRecord $0021, $0000, $F0, $50, $0E, $00, $FF, $29
    PositionRecord $0028, $0000, $F0, $6F, $0E, $00, $FF, $2A
    PositionRecord $002D, $0000, $F0, $6E, $1C, $00, $FF, $2B
    PositionRecord $002F, $0000, $F0, $6F, $2C, $00, $FF, $2F
    PositionRecord $003B, $0000, $F0, $0A, $1E, $18, $FF, $2C
    PositionRecord $003F, $0000, $F0, $4D, $27, $00, $FF, $2D
    PositionRecord $004D, $0000, $F0, $6E, $24, $00, $FF, $2E
    PositionRecord $005E, $0000, $F0, $52, $2A, $00, $FF, $30
    PositionRecord $006E, $0000, $F0, $6E, $26, $00, $FF, $31
    PositionRecord $007E, $0000, $F0, $71, $16, $00, $FF, $32
    PositionRecord $0088, $0000, $F0, $0A, $24, $24, $FF, $2C
    PositionRecord $008C, $0000, $F0, $6E, $20, $00, $FF, $33
    PositionRecord $008F, $0000, $F0, $6F, $0E, $00, $FF, $34
    PositionRecord $00A0, $0000, $F0, $52, $2A, $00, $FF, $35
    PositionRecord $00A4, $0000, $F0, $6E, $23, $00, $FF, $36
    PositionRecord $00B4, $0000, $F0, $6F, $16, $00, $FF, $37
    PositionRecord $00B6, $0000, $F0, $71, $16, $00, $FF, $38
    PositionRecord $00C0, $0000, $F0, $4D, $24, $00, $FF, $39
    PositionRecord $00D1, $0000, $F0, $50, $0E, $00, $FF, $3A
    PositionRecord $00ED, $0000, $F0, $6E, $23, $00, $FF, $3B
    PositionRecord $00F4, $0000, $F0, $6B, $19, $00, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $33EC, error, "bank 0 position stream $B320 end"

PositionStreamB3EC:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0002, $0000, $F0, $0D, $5B, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B3EC
    PositionRecord $0004, $0000, $F0, $01, $6A, $00, $FF, $FF
    PositionRecord $0018, $0000, $F0, $55, $5C, $00, $FF, $96
    PositionRecord $0023, $0000, $F0, $0A, $4E, $1B, $FF, $3D
    PositionRecord $002D, $0000, $F0, $51, $16, $00, $FF, $AE
    PositionRecord $0032, $0000, $F0, $55, $4A, $00, $FF, $FF
    PositionRecord $0033, $0000, $F0, $51, $1A, $00, $FF, $9D
    PositionRecord $0034, $0000, $F0, $55, $2A, $00, $FF, $FF
    PositionRecord $003B, $0000, $F0, $51, $29, $00, $FF, $AD
    PositionRecord $0040, $0000, $F0, $55, $0C, $00, $FF, $9E
    PositionRecord $0043, $0000, $F0, $51, $5A, $00, $FF, $AC
    PositionRecord $0045, $0000, $F0, $0A, $0E, $10, $FF, $3F
    PositionRecord $004B, $0000, $F0, $0A, $3E, $1C, $FF, $9A
    PositionRecord $0054, $0000, $F0, $51, $3E, $00, $FF, $99
    PositionRecord $005D, $0000, $F0, $0A, $54, $0B, $FF, $3E
    PositionRecord $0068, $0000, $F0, $5D, $14, $00, $FF, $40
    PositionRecord $006C, $0000, $F0, $51, $52, $00, $FF, $AB
    PositionRecord $0073, $0000, $F0, $51, $22, $00, $FF, $AA
    PositionRecord $007B, $0000, $F0, $55, $31, $00, $FF, $FF
    PositionRecord $007C, $0000, $F0, $55, $42, $00, $FF, $FF
    PositionRecord $007E, $0000, $F0, $20, $08, $00, $FF, $42
    PositionRecordEnd
.assert (* - BankStart) = $34A0, error, "bank 0 position stream $B3EC end"

PositionStreamB4A0:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0000, $0000, $F0, $00, $10, $01, $FF, $FF ; CONTROL_POSITION_STREAM_B4A0
    PositionRecordEnd
.assert (* - BankStart) = $34B4, error, "bank 0 position stream $B4A0 end"

PositionStreamB4B4:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $001A, $0000, $F0, $1E, $0A, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B4B4
    PositionRecordEnd
.assert (* - BankStart) = $34C8, error, "bank 0 position stream $B4B4 end"

PositionStreamB4C8:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_POSITION_STREAM_B4C8
    PositionRecordEnd
.assert (* - BankStart) = $34D4, error, "bank 0 position stream $B4C8 end"

PositionStreamB4D4:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0001, $0000, $F0, $16, $1A, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B4D4
    PositionRecord $0002, $0000, $F0, $27, $06, $00, $FF, $FF
    PositionRecord $001D, $0000, $F0, $27, $0D, $01, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $34F8, error, "bank 0 position stream $B4D4 end"

PositionStreamB4F8:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00
    PositionRecord $0001, $0000, $F0, $25, $14, $00, $FF, $FF ; CONTROL_POSITION_STREAM_B4F8
    PositionRecord $000D, $0000, $F0, $64, $1B, $01, $FF, $FF
    PositionRecord $000E, $0000, $F0, $17, $1A, $00, $FF, $FF
    PositionRecordEnd
.assert (* - BankStart) = $351C, error, "bank 0 position stream $B4F8 end"

; Opcode $9B calls this palette fade through the native-call wrapper. Preserve
; the polling, palette order, four passes and restoration of scroll and PPU
; registers; timing and mapper behaviour still require runtime verification.
FadeOutPalettes:
    lda $03FF
    sta PPUCTRL
    ldy #$00
    sty $0380
    ldx #$0F                    ; CONTROL_FADE_PALETTE_LOAD
FadeLoadPalettes:
    lda ($F8),y
    sta $03D0,x
    lda ($FA),y
    sta $0140,x
    iny
    dex
    bpl FadeLoadPalettes
    ldx #$03
    lda $03FF
    and #$FE
    sta $03FF
    lda $03F4
    and #$01
    ora $03FF
    sta $03FF
FadePalettePass:
    jsr FadeWaitVBlank
    lda #$06
    sta PPUMASK
    lda PPUSTATUS
    lda #$3F
    sta PPUADDR
    lda #$00
    sta PPUADDR
    ldy #$0F
FadeWriteBackground:
    lda $03D0,y
    sta PPUDATA
    dey
    bpl FadeWriteBackground
    lda $03DF
    sta PPUDATA
    ldy #$0E
FadeWriteSprites:
    lda $0140,y
    sta PPUDATA
    dey
    bpl FadeWriteSprites
    lda $03FE
    sta PPUMASK
    lda $03FF
    sta PPUCTRL
    lda $03FC
    sta PPUSCROLL
    lda $03FD
    sta PPUSCROLL
    ldy #$02
FadeWaitFrames:
    lda PPUSTATUS
    bmi FadeWaitFrames
    jsr FadeWaitVBlank
    dey
    bpl FadeWaitFrames
    ldy #$0F
FadeDarkenPalettes:
    lda $03D0,y
    sec
    sbc #$10
    bpl FadeStoreBackground
    lda #$0E
FadeStoreBackground:
    sta $03D0,y
    lda $0140,y
    sec
    sbc #$10
    bpl FadeStoreSprite
    lda #$0E
FadeStoreSprite:
    sta $0140,y
    dey
    bpl FadeDarkenPalettes
    dex
    bpl FadePalettePass
    lda $03FF
    ora #$80
    sta PPUCTRL
    rts
.assert (* - BankStart) = $35CD, error, "bank 0 palette fade end"
FadeWaitVBlank:
    lda PPUSTATUS               ; CONTROL_FADE_WAIT_VBLANK
    bpl FadeWaitVBlank
    rts
.assert (* - BankStart) = $35D3, error, "bank 0 palette fade wait end"
    .incbin "bank0_b5d3_ca5d.bin"
; Initialize engine state and split-screen parameters using the locally
; supplied four-byte table. The downstream PPU and mapper behavior still
; require runtime verification.
InitializeMainState:
    lda #$00 ; CONTROL_MAIN_STATE_INIT
    sta $28
    sta $3B
    sta $18
    sta $13
    sta $08
    sta $0A
    sta $58
    sta $E7
    sta $5D
    sta $03C9
    lda #$03
    sta $0D
    sta $09
    lda #$FF
    sta $00
    sta $27
    sta $07
    sta $1E
    jsr InitializeState19To1B
    lda DefaultSplitScreenParameters
    sta $61
    lda DefaultSplitScreenParameters + 1
    sta $62
    lda DefaultSplitScreenParameters + 2
    sta $63
    lda DefaultSplitScreenParameters + 3
    sta $64
    jmp ConfigureSplitScreen

.assert (* - BankStart) = $4A9E, error, "bank 0 state preparation ca9e boundary"

; A zero main state updates a frame. Other values clear PPU ranges and
; prepare slot, bank, palette, scroll and map state before returning to frames.
MainLoopStep:
    lda $00 ; CONTROL_MAIN_STATE_DISPATCH
    bne MainStateChange
    jmp UpdateGameFrame

MainStateChange:
    jsr ClearTwoPpuRanges
    jsr ScriptCompareState27
    bne MainRestoreSlots
    lda $0A
    beq MainResetSlots
    jsr ReleaseSelectedSlots
    lda #$00
    sta $03C9
    jmp MainPrepareResources

MainRestoreSlots:
    lda #$FF
    sta $3C
    sta $3D
    lda $0A
    beq MainVisitSlots
    lda $5B
    sta $3C
    lda $5C
    sta $3D
    lda $4D
    sta $15
    lda $4E
    sta $16
.assert (* - BankStart) = $4AD6, error, "bank 0 state preparation cad6 boundary"

; Visit all sixteen slots. Retained slots may have bit $20 toggled when
; restoring prior state; other slots are released through the common helper.
MainVisitSlots:
    lda #$0F ; CONTROL_MAIN_STATE_SLOTS
    sta $10
MainVisitSlotLoop:
    ldx $10
    jsr SlotDrawCheckDisabled
    bne MainToggleSavedSlotFlag
    jsr ReleaseCurrentSlot
    jmp MainNextSlot

MainToggleSavedSlotFlag:
    lda $0A
    beq MainNextSlot
    lda $0630,x
    eor #$20
    sta $0630,x
MainNextSlot:
    dec $10
    bpl MainVisitSlotLoop
    jmp MainPrepareResources

MainResetSlots:
    jsr ReleaseAllSpriteRecords
    jsr InitializeRemainingShadowOam
    lda #$FF
    sta $3C
    sta $3D
    ldx #$00
MainClearSlotsLoop:
    sta $04E0,x
    inx
    cpx #$10
    bne MainClearSlotsLoop
.assert (* - BankStart) = $4B10, error, "bank 0 state preparation cb10 boundary"

; Select the state and either the saved or state-indexed bank and palettes.
MainPrepareResources:
    lda $08 ; CONTROL_MAIN_STATE_RESOURCES
    beq MainSelectState
    jsr StopAllAudioVoices
    lda #$00
    sta $08
MainSelectState:
    lda $00
    sta $01
    cmp #$FF
    bne MainApplyState
    lda #$00
    sta $01
MainApplyState:
    asl a
    sta $02
    jsr ScriptReadState27
    beq MainDefaultBankSelection
    lda $E6
    jsr ConfigureBanksFromValue
    jmp MainSelectPalettes

MainDefaultBankSelection:
    jsr ConfigureBanksFromState
MainSelectPalettes:
    jsr ScriptReadState27
    beq MainDefaultPalettes
    ldx $03CA
    ldy $03CB
    jsr ApplyFirstRelatedPointer
    ldx $03CC
    ldy $03CD
    jsr ApplySecondRelatedPointer
    jmp MainSetupHorizontalBase

MainDefaultPalettes:
    jsr SelectBothRelatedPointers
.assert (* - BankStart) = $4B57, error, "bank 0 state preparation cb57 boundary"

; Restore or initialize two scroll bases. The original calls each doubling
; helper three times, preserving carries in the paired bytes.
MainSetupHorizontalBase:
    lda $0C ; CONTROL_MAIN_STATE_BASES
    sta $03EF
    lda $0B
    sta $03EE
    lda $0A
    bne MainSetupVerticalBase
    sta $03EE
    sta $03EF
    jsr MainScaleHorizontalBase
    jsr MainScaleHorizontalBase
    jsr MainScaleHorizontalBase
MainSetupVerticalBase:
    lda $1C
    sta $03F0
    lda $1D
    sta $03F1
    lda $0A
    bne MainPrepareMap
    ldx $01
    lda InitialVerticalBaseSeeds,x
    sta $03F0
    lda #$00
    sta $03F1
    jsr MainScaleVerticalBase
    jsr MainScaleVerticalBase
    jsr MainScaleVerticalBase
.assert (* - BankStart) = $4B98, error, "bank 0 state preparation cb98 boundary"

; Initialize the selected map and translate selected slots when the saved
; and recalculated position references differ.
MainPrepareMap:
    ldx $02 ; CONTROL_MAIN_STATE_MAP
    ldy $A1B3,x
    lda $A1B2,x
    tax
    jsr InitializeMapDrawing
    jsr UpdatePositionReference
    lda $0A
    beq InitializePositionStreams
    jsr ScriptCompareState27
    bne InitializePositionStreams
    ldx $0B
    ldy $0C
    jsr ShiftXYRight3
    sec
    sbc $0E
    sta $FE
    tya
    sbc $0F
    ; A nonzero horizontal difference enters translation before the later
    ; vertical calculation stores $FF; the existing $FF is used unchanged.
    bne MainTranslateSlots
    lda $FE
    bne MainTranslateSlots
    ldx $1C
    ldy $1D
    jsr ShiftXYRight3
    sec
    sbc $4F
    sta $FF
    bne MainTranslateSlots
    jmp InitializePositionStreams

.assert (* - BankStart) = $4BD6, error, "bank 0 state preparation cbd6 boundary"

MainScaleHorizontalBase:
    asl $03EE ; CONTROL_MAIN_STATE_SCALE
    rol $03EF
    rts
MainScaleVerticalBase:
    asl $03F0
    rol $03F1
    rts
.assert (* - BankStart) = $4BE4, error, "bank 0 state preparation cbe4 boundary"

MainTranslateSlots:
    lda $FE ; CONTROL_MAIN_STATE_TRANSLATE
    jsr ShiftALeft3
    sta $FE
    lda $FF
    jsr ShiftALeft3
    sta $FF
    ldx $3C
    jsr TranslateSlotPosition
    ldx $3D
    jsr TranslateSlotPosition
    jsr UpdatePositionReference

.assert (* - BankStart) = $4BFF, error, "bank 0 state preparation end"

; Select the two position-record streams using the byte index in $02, reset
; shared state, and optionally scan the initial 32-position window.
InitializePositionStreams:
    ldx $02                       ; CONTROL_INITIALIZE_POSITION_STREAMS
    lda PositionRecordPointersA,x
    sta $E2
    lda PositionRecordPointersA+1,x
    sta $E3
    lda PositionRecordPointersB,x
    sta $E4
    lda PositionRecordPointersB+1,x
    sta $E5
    lda #$00
    sta $28
    sta $36
    sta $35
    sta $34
    sta $31
    sta $30
    sta $2F
    sta $E7
    sta $5D
    sta $14
    lda $0A
    beq InitializePositionScan
    lda #$00
    sta $0A
    jsr ScriptCompareState27
    beq InitializePositionScan
    lda #$FF
    sta $27
    jmp InitializePositionFinish
InitializePositionScan:
    jsr ScanPositionWindow
InitializePositionFinish:
    lda #$00
    sta $00
    jsr EnablePpuNmi
    rts

; Subtract $FE/$FF from a slot's position only when X is valid and $F981
; returns nonzero. The exact role of the callee remains to be investigated.
TranslateSlotPosition:
    cpx #$FF                      ; CONTROL_TRANSLATE_SLOT_POSITION
    beq TranslateSlotReturn
    jsr $F981
    beq TranslateSlotReturn
    lda $0580,x
    sec
    sbc $FE
    sta $0580,x
    lda $0590,x
    sec
    sbc $FF
    sta $0590,x
TranslateSlotReturn:
    rts

; Add A to $03EE/$03EF, shift the resulting 16-bit value right three times,
; and return its low/high bytes in X/Y.
ScaleWorldCoordinate:
    clc                           ; CONTROL_SCALE_WORLD_COORDINATE
    adc $03EE
    sta $11
    lda $03EF
    adc #$00
    jsr ScaleWorldShiftRight
    jsr ScaleWorldShiftRight
    jsr ScaleWorldShiftRight
    ldx $11
    tay
    rts
ScaleWorldShiftRight:
    lsr a                         ; CONTROL_SCALE_WORLD_SHIFT
    ror $11
    rts
.assert (* - BankStart) = $4C82, error, "bank 0 position stream setup end"


; Entry points share shift tails: CC82 shifts left four, CC83 shifts left
; three, CC87 shifts right four, and CC88 shifts right three.
ShiftALeft4:
    asl a                         ; CONTROL_SHIFT_LEFT4
ShiftALeft3:
    asl a                         ; CONTROL_SHIFT_LEFT3
    asl a
    asl a
    rts
ShiftARight4:
    lsr a                         ; CONTROL_SHIFT_RIGHT4
ShiftARight3:
    lsr a                         ; CONTROL_SHIFT_RIGHT3
    lsr a
    lsr a
    rts
.assert (* - BankStart) = $4C8C, error, "bank 0 shift helper end"

; The table at $A37E selects bank-control values from the current state. A
; direct entry at $CC95 accepts the table byte in A; the $FF table value skips.
ConfigureBanksFromState:
    ldx $01                       ; CONTROL_BANKS_FROM_STATE
    lda StateBankSelectors,x
    cmp #$FF
    beq ConfigureBanksReturn
ConfigureBanksFromValue:
    pha                           ; CONTROL_BANKS_FROM_VALUE
    jsr ScriptCompareState27
    bne ConfigureBanksSkipSaved
    pla
    pha
    sta $E6
ConfigureBanksSkipSaved:
    pla
    pha
    and #$01
    jsr ShiftALeft4
    ora #$08
    sta $03BD
    pla
    rol a
    rol a
    rol a
    and #$F0
    pha
    jsr ComputeBankSelection
    sta $03C0
    stx $03C1
    pla
    ora #$01
    jsr ComputeBankSelection
    sta $03C2
    stx $03C3
ConfigureBanksReturn:
    rts

; These entries select encoded pointers from $A3C0/$A394 and call separate
; consumers. The command handlers may enter after the table lookup.
SelectBothRelatedPointers:
    jsr SelectFirstRelatedPointer ; CONTROL_SELECT_BOTH_POINTERS
SelectSecondRelatedPointer:
    ldx $02                       ; CONTROL_SELECT_SECOND_POINTER
    ldy SpritePalettePointers + 1,x
    lda SpritePalettePointers,x
    tax
ApplySecondRelatedPointer:
    jsr ScriptCompareState27      ; CONTROL_APPLY_SECOND_POINTER
    bne ApplySecondPointerCall
    stx $03CC
    sty $03CD
ApplySecondPointerCall:
    jsr SetSpritePaletteStream
    rts
SelectFirstRelatedPointer:
    ldx $02                       ; CONTROL_SELECT_FIRST_POINTER
    ldy BackgroundPalettePointers + 1,x
    lda BackgroundPalettePointers,x
    tax
ApplyFirstRelatedPointer:
    jsr ScriptCompareState27      ; CONTROL_APPLY_FIRST_POINTER
    bne ApplyFirstPointerCall
    stx $03CA
    sty $03CB
ApplyFirstPointerCall:
    jsr SetBackgroundPaletteStream
    rts

; Initialize two PPU address ranges with $40. The 240 iterations write four
; bytes each. The direct-write setup is recovered; hardware timing remains unverified.
ClearTwoPpuRanges:
    jsr PrepareDirectPpuWrites    ; CONTROL_CLEAR_TWO_PPU_RANGES
    ldy #$20
    jsr FillPpuRange
    ldy #$24
FillPpuRange:
    ldx #$00                      ; CONTROL_FILL_PPU_RANGE
    lda PPUSTATUS
    sty PPUADDR
    stx PPUADDR
    ldx #$F0
    lda #$40
FillPpuRangeLoop:
    sta PPUDATA
    sta PPUDATA
    sta PPUDATA
    sta PPUDATA
    dex
    bne FillPpuRangeLoop
    rts

; The frame routine gates on $28/$14, calls shared subsystems and iterates the
; 16 slots through UpdateCurrentSlot. Several callees remain unconverted.
UpdateGameFrame:
    lda $28                       ; CONTROL_UPDATE_GAME_FRAME
    bne UpdateGameFrameReturn
    lda $14
    and #$01
    bne UpdateGameFrameStart
UpdateGameFrameReturn:
    rts
UpdateGameFrameStart:
    jsr RotateShadowOam
    dec $14
    jsr UpdateHorizontalMotion
    jsr UpdateVerticalMotion
    jsr UpdateFramePositionBases
    jsr UpdateSlotDrawPositions
    lda $36
    beq UpdateFrameSecondFlag
    jsr RequestHorizontalScroll
UpdateFrameSecondFlag:
    lda $31
    beq UpdateFrameRefreshSlots
    jsr RequestVerticalScroll
UpdateFrameRefreshSlots:
    jsr RefreshAllSlotRecords
    lda $5D
    beq UpdateFrameSlotLoopStart
    lda $25
    sta $5E
    lda $26
    sta $5F
    jsr ProcessPositionRecord
    lda #$00
    sta $5D
UpdateFrameSlotLoopStart:
    lda #$00
    sta $10
UpdateFrameSlotLoop:
    jsr UpdateCurrentSlot
    lda $00
    bne UpdateFrameDone
    lda $14
    beq UpdateFrameNextSlot
    ora #$80
    sta $14
UpdateFrameNextSlot:
    inc $10
    lda $10
    cmp #$10
    bcc UpdateFrameSlotLoop
    lda $14
    and #$7F
    bne UpdateFrameDone
    sta $14
UpdateFrameDone:
    rts
RefreshAllSlotRecords:
    ldx #$00                      ; CONTROL_REFRESH_ALL_SLOT_RECORDS
RefreshSlotRecordsLoop:
    jsr RefreshSlotRecordPosition
    inx
    cpx #$10
    bne RefreshSlotRecordsLoop
    rts
RefreshSlotRecordPosition:
    lda $04E0,x                   ; CONTROL_REFRESH_SLOT_RECORD_POSITION
    cmp #$FF
    beq RefreshSlotRecordReturn
    lda $0620,x
    bmi RefreshSlotRecordReturn
    lda $0630,x
    and #$20
    bne RefreshSlotRecordReturn
    stx $10
    lda $0590,x
    tay
    lda $0580,x
    tax
    lda $10
    jsr PlaceSlotSprites
    ldx $10
RefreshSlotRecordReturn:
    rts
UpdateSlotDrawPositions:
    ldx #$00                      ; CONTROL_UPDATE_SLOT_DRAW_POSITIONS
    stx $10
    lda $36
    ora $31
    beq UpdateSlotDrawReturn
UpdateSlotDrawLoop:
    stx $10
    jsr UpdateSlotDrawPosition
    ldx $10
    inx
    cpx #$10
    bne UpdateSlotDrawLoop
UpdateSlotDrawReturn:
    rts
.assert (* - BankStart) = $4DCF, error, "bank 0 frame dispatch end"

; Update position bases from $36/$31, recalculating references and marking
; $5D when the first reference changes. Zero values bypass their components.
UpdateFramePositionBases:
    lda $36                      ; CONTROL_UPDATE_FRAME_POSITION_BASES
    ora $31
    bne UpdateFrameFirstBase
    jmp UpdateFrameBasesReturn
UpdateFrameFirstBase:
    lda #$00
    sta $FF
    lda $36
    beq UpdateFrameSecondBase
    jsr NegateA
    sta $FE
    bpl UpdateFrameFirstAdd
    lda #$FF
    sta $FF
UpdateFrameFirstAdd:
    clc
    lda $03EE
    adc $FE
    sta $03EE
    lda $03EF
    adc $FF
    sta $03EF
    lda $0E
    sta $FE
    lda $0F
    sta $FF
    jsr UpdatePositionReference
    lda $0E
    sec
    sbc $FE
    sta $FE
    lda $0F
    sbc $FF
    bcc UpdateFrameMarkLow
    bne UpdateFrameMarkHigh
    lda $FE
    beq UpdateFrameSecondBase
UpdateFrameMarkHigh:
    lda $0E
    clc
    adc #$1F
    sta $25
    lda $0F
    adc #$00
    sta $26
    jmp UpdateFrameMarkChanged
UpdateFrameMarkLow:
    lda $0E
    sta $25
    lda $0F
    sta $26
UpdateFrameMarkChanged:
    lda #$FF
    sta $5D
UpdateFrameSecondBase:
    lda #$00                     ; CONTROL_UPDATE_FRAME_SECOND_BASE
    sta $FF
    lda $31
    beq UpdateFrameBasesReturn
    jsr NegateA
    sta $FE
    bpl UpdateFrameSecondAdd
    lda #$FF
    sta $FF
    lda $03F1
    bne UpdateFrameSecondAdd
    lda $03F0
    cmp $31
    bcs UpdateFrameSecondAdd
    lda $03F0
    sta $31
    lda #$00
    sta $03F0
    jmp UpdateFrameRecalculate
UpdateFrameSecondAdd:
    clc
    lda $03F0
    adc $FE
    sta $03F0
    lda $03F1
    adc $FF
    sta $03F1
UpdateFrameRecalculate:
    jsr UpdatePositionReference
UpdateFrameBasesReturn:
    rts

; Examine 32 consecutive position keys beginning at $0E/$0F.
ScanPositionWindow:
    lda #$00                     ; CONTROL_SCAN_POSITION_WINDOW
ScanPositionWindowLoop:
    pha
    clc
    adc $0E
    sta $5E
    lda $0F
    adc #$00
    sta $5F
    jsr ProcessPositionRecord
    pla
    tax
    inx
    txa
    cmp #$20
    bne ScanPositionWindowLoop
    rts

; Only record type $F0 invokes the slot creation path. The matching helper
; may unwind the caller on an already-present slot without the required flag.
ProcessPositionRecord:
    jsr LookupPositionRecordsA   ; CONTROL_PROCESS_POSITION_RECORD
    cmp #$F0
    bne ProcessPositionReturn
    jsr CreateSlotFromPositionRecord
ProcessPositionReturn:
    rts
CreateSlotFromPositionRecord:
    jsr RequireMatchingSlotFlag  ; CONTROL_CREATE_POSITION_SLOT
    jsr FindAvailableSlot
    bne ProcessPositionReturn
    stx $10
    lda $5E
    sta $90,x
    sta $07D0,x
    lda $5F
    sta $A0,x
    sta $07E0,x
    lda #$00
    sta $05A0,x
    lda $5E
    sta $11
    lda $5F
    sta $12
    ldy $2B
    lda #$00
    sta $50
    sta $51
    jsr ConvertSlotPosition
    bcc CreatePositionStoreCoordinates
    lda $2D
    cmp #$FF
    bne CreatePositionStoreCoordinates
    lda #$FE
    sta $2D
    ldy #$00
CreatePositionStoreCoordinates:
    txa
    ldx $10
    sta $0580,x
    tya
    sta $0590,x
    lda $2C
    sta $0780,x
    ldy #$00
    lda $2B
    sta $80,x
    lda $2D
    sta $70,x
    cmp #$FF
    beq CreatePositionStoreFlags
    ldy #$80
CreatePositionStoreFlags:
    tya
    sta $0620,x
    lda $2E
    sta $07B0,x
; Fall through into InitializeCurrentSlot at $CF02.
.assert (* - BankStart) = $4F02, error, "bank 0 frame position handlers end"


; Initialize the current slot unless its $07B0 bit is already set in the
; stack-page bitset. Defaults and repeated stores are preserved exactly.
InitializeCurrentSlot:
    ldx $10                       ; CONTROL_INITIALIZE_SLOT_ENTRY
    lda $07B0,x
    cmp #$FF
    beq InitializeSlotDefaults
    jsr ScriptSlotBitMask
    ldx $10
    and $0100,y
    beq InitializeSlotDefaults
    jmp InitializeSlotUnavailable
InitializeSlotDefaults:
    lda #$00                      ; CONTROL_INITIALIZE_SLOT_DEFAULTS
    sta $04F0,x
    sta $0750,x
    sta $0500,x
    sta $0510,x
    sta $0530,x
    sta $0700,x
    sta $0560,x
    sta $0640,x
    sta $0650,x
    sta $0660,x
    sta $0640,x
    sta $0650,x
    sta $0670,x
    sta $0680,x
    sta $0360,x
    sta $0370,x
    sta $D0,x
    lda #$FF
    sta $0790,x
    sta $0540,x
    sta $06F0,x
    sta $06D0,x
    sta $0760,x
    lda #$80
    sta $0630,x
    lda #$44
    sta $07F0,x
    lda #$10
    sta $C0,x
    lda #$24
    sta $05F0,x
    lda #$60
    sta $0600,x
    lda #$20
    sta $0710,x
    lda #$00
    sta $0720,x
    lda #$00
    sta $0730,x

; The six-byte descriptor contains a pointer followed by four values copied
; into the per-slot $05D0, $0610, $05E0 and $0520 fields.
InitializeSlotFromDescriptor:
    lda $2A                       ; CONTROL_INITIALIZE_SLOT_DESCRIPTOR
    jsr SlotRecordAddressFromIndex
    ldy #$02
    lda ($FE),y
    sta $05D0,x
    iny
    lda #$04
    ora $0620,x
    sta $0620,x
    lda ($FE),y
    sta $0610,x
    bne InitializeSlotDescriptorNext
    lda $0620,x
    eor #$04
    sta $0620,x
InitializeSlotDescriptorNext:
    iny
    lda ($FE),y
    sta $05E0,x
    iny
    lda ($FE),y
    sta $0520,x
    lda $0620,x
    bmi InitializeSlotStoreIndex
InitializeSlotCheckLoad:
    lda #$00
    sta $04DC
    lda $10
    jsr StoreSlotRecordField0A
    ldx $10
    jsr ScriptPushZeroAndCall
    beq InitializeSlotStoreIndex
InitializeSlotUnavailable:
    ldx $10                       ; CONTROL_INITIALIZE_SLOT_UNAVAILABLE
    lda #$FF
    sta $04E0,x
    rts
InitializeSlotStoreIndex:
    lda $2A
    sta $04E0,x
    rts

; The first helper discards the caller's return address for a matched slot
; whose $0630 bit $20 is clear. The search compares $90/$A0 against $5E/$5F.
RequireMatchingSlotFlag:
    jsr FindMatchingSlot          ; CONTROL_REQUIRE_MATCHING_SLOT_FLAG
    bne RequireMatchingSlotReturn
    lda $0630,y
    and #$20
    bne RequireMatchingSlotReturn
    pla
    pla
RequireMatchingSlotReturn:
    rts
FindMatchingSlot:
    ldy #$0F                      ; CONTROL_FIND_MATCHING_SLOT
FindMatchingSlotLoop:
    jsr ScriptCheckSlotPresent
    beq FindMatchingSlotNext
    lda $90,y
    cmp $5E
    bne FindMatchingSlotNext
    lda $A0,y
    cmp $5F
    beq FindMatchingSlotReturn
FindMatchingSlotNext:
    dey
    bpl FindMatchingSlotLoop
    lda #$FF
FindMatchingSlotReturn:
    rts
.assert (* - BankStart) = $5002, error, "bank 0 slot initialization end"

; Find a free slot or one eligible for reuse. If all slots are active, the
; last $05E0 bit-$10 candidate is preferred; otherwise the second scan tests
; active slots with bit $80 in $0620 and a distance of at least three.
FindAvailableSlot:
    ldy #$FF                      ; CONTROL_FIND_AVAILABLE_SLOT
    ldx #$00
FindAvailableSlotLoop:
    lda $04E0,x
    cmp #$FF
    beq FindAvailableSlotSuccess
    lda $05E0,x
    and #$10
    beq FindAvailableSlotNext
    txa
    tay
FindAvailableSlotNext:
    inx
    cpx #$10
    bne FindAvailableSlotLoop
    tya
    bmi FindAvailableSlotSecondScan
FindAvailableSlotReuse:
    pha
    tax
    jsr ReleaseSlotByIndex
    pla
    tax
FindAvailableSlotSuccess:
    lda #$00
    rts
FindAvailableSlotSecondScan:
    ldx #$00
FindAvailableSlotDistanceLoop:
    lda $0620,x
    bpl FindAvailableSlotDistanceNext
    jsr SlotDistanceFromReference
    cmp #$03
    bcs FindAvailableSlotUseDistance
FindAvailableSlotDistanceNext:
    inx
    cpx #$10
    bne FindAvailableSlotDistanceLoop
    lda #$FF
    rts
FindAvailableSlotUseDistance:
    txa
    jmp FindAvailableSlotReuse

; Calculate a bounded difference between $07D0/$07E0 and $0E/$0F. The
; subtraction and special handling of $FF in the high byte are retained.
SlotDistanceFromReference:
    lda $07D0,x                   ; CONTROL_SLOT_DISTANCE_REFERENCE
    sec
    sbc $0E
    tay
    lda $07E0,x
    sbc $0F
    bcs SlotDistanceNonnegative
    cmp #$FF
    bne SlotDistanceLarge
    tya
    jsr NegateA
    rts
SlotDistanceNonnegative:
    bne SlotDistanceLarge
    tya
    sec
    sbc #$20
    bcs SlotDistanceReturn
    lda #$00
SlotDistanceReturn:
    rts
SlotDistanceLarge:
    lda #$FF
    rts

; Consult the position-record selector and, if its checks pass, copy
; values $2B/$2C into slot fields and set pending command $1B.
UpdateSlotFromPosition:
    lda $07D0,x                   ; CONTROL_SLOT_POSITION_EVENT
    sta $5E
    lda $07E0,x
    sta $5F
    jsr LookupPositionRecordsB
    beq SlotPositionEventReturn
    cmp #$F0
    bcs SlotPositionEventReturn
    ldx $10
    jsr CalculateSlotCoordinate
    lda $11
    cmp $29
    bcc SlotPositionEventReturn
    sbc #$01
    cmp $2A
    bcs SlotPositionEventReturn
    lda #$04
    and $0790,x
    bne SlotPositionEventReturn
    lda $0630,x
    bmi SlotPositionEventApply
    and #$01
    tay
    lda $038D,y
    and $2E
    eor $2D
    bne SlotPositionEventReturn
SlotPositionEventApply:
    lda $2B
    sta $0770,x
    lda $2C
    sta $0780,x
    lda #$1B
    sta $04F0,x
SlotPositionEventReturn:
    rts

; Add $B0,x to $03F0/$03F1 and rotate the result right three times. The
; carry entering the first rotate is preserved from the original addition.
CalculateSlotCoordinate:
    lda $B0,x                     ; CONTROL_CALCULATE_SLOT_COORDINATE
    clc
    adc $03F0
    sta $11
    lda $03F1
    adc #$00
    jsr RotateSlotCoordinate
    jsr RotateSlotCoordinate
RotateSlotCoordinate:
    ror a                         ; CONTROL_ROTATE_SLOT_COORDINATE
    ror $11
    rts
.assert (* - BankStart) = $50CA, error, "bank 0 slot allocation helpers end"

; Two eight-byte search paths use different zero-page pointer pairs.
LookupPositionRecordsA:
    PositionRecordSearch $E2, $E3, SearchPositionRecordsA
.assert (* - BankStart) = $519A, error, "bank 0 first position search end"
LookupPositionRecordsB:
    PositionRecordSearch $E4, $E5, SearchPositionRecordsB
.assert (* - BankStart) = $526A, error, "bank 0 second position search end"

; Convert two position components relative to $03EE/$03EF and $03F0/$03F1.
; The caller uses carry to distinguish values that do not fit the limits.
ConvertSlotPosition:
    jsr ScalePositionByEight      ; CONTROL_CONVERT_SLOT_POSITION
    lda $51
    beq ConvertSlotFirstSubtract
    clc
    adc $11
    sta $11
    bcc ConvertSlotFirstSubtract
    inc $12
ConvertSlotFirstSubtract:
    sec
    lda $11
    sbc $03EE
    sta $11
    tax
    lda $12
    sbc $03EF
    sta $12
    bne ConvertSlotPositionOutOfRange
    bcs ConvertSlotSecond
ConvertSlotPositionOutOfRange:
    sec
    rts
ConvertSlotSecond:
    sty $11
    jsr ScalePositionByEight
    lda $50
    beq ConvertSlotSecondSubtract
    clc
    adc $11
    sta $11
    bcc ConvertSlotSecondSubtract
    inc $12
ConvertSlotSecondSubtract:
    sec
    lda $11
    sbc $03F0
    sta $11
    tay
    lda $12
    sbc $03F1
    sta $12
    bne ConvertSlotPositionOutOfRange
    bcc ConvertSlotPositionOutOfRange
    cpy #$F0
    rts
ScalePositionByEight:
    jsr ShiftPositionLeft        ; CONTROL_SCALE_POSITION_BY_EIGHT
    jsr ShiftPositionLeft
ShiftPositionLeft:
    asl $11
    rol $12
    rts

; Derive $0E/$0F and $4F from the two position bases, adding seven before
; three right shifts. Preserve carry propagation on the original entry paths.
UpdatePositionReference:
    lda $03EE                     ; CONTROL_UPDATE_POSITION_REFERENCE
    clc
    adc #$07
    sta $0E
    lda $03EF
    adc #$00
    sta $0F
    jsr ShiftReferenceRight
    jsr ShiftReferenceRight
    jsr ShiftReferenceRight
    lda $03F0
    clc
    adc #$07
    sta $4F
    lda $03F1
    adc #$00
    jsr ShiftA4FRight
    jsr ShiftA4FRight
ShiftA4FRight:
    lsr a                         ; CONTROL_SHIFT_A4F_RIGHT
    ror $4F
    rts
ShiftReferenceRight:
    lsr $0F                       ; CONTROL_SHIFT_REFERENCE_RIGHT
    ror $0E
    rts
.assert (* - BankStart) = $52F8, error, "bank 0 position conversion end"


; Mark a slot free, then pass its index to ReleaseSpriteRecord.
ReleaseCurrentSlot:
    ldx $10                       ; CONTROL_RELEASE_CURRENT_SLOT
ReleaseSlotByIndex:
    lda #$FF                      ; CONTROL_RELEASE_SLOT_BY_INDEX
    sta $04E0,x
    txa
    jmp ReleaseSpriteRecord

; Release selected active slots while retaining the original $03C9 mask test.
ReleaseSelectedSlots:
    ldy #$00                      ; CONTROL_RELEASE_SELECTED_SLOTS
ReleaseSelectedSlotsLoop:
    jsr ScriptCheckSlotPresent
    beq ReleaseSelectedSlotsNext
    lda $0630,y
    bpl ReleaseSelectedSlotsNext
    lda $05E0,y
    and $03C9
    and #$40
    bne ReleaseSelectedSlotsNext
    sty $10
    jsr ReleaseCurrentSlot
    ldy $10
ReleaseSelectedSlotsNext:
    iny
    cpy #$10
    bne ReleaseSelectedSlotsLoop
    rts

; Search active slots for $05D0 bit $04 and require $0620 to be nonnegative.
FindSlotWithFlag04:
    ldy #$00                      ; CONTROL_FIND_SLOT_FLAG04
FindSlotWithFlagLoop:
    jsr ScriptCheckSlotPresent
    beq FindSlotWithFlagNext
    lda $05D0,y
    and #$04
    bne FindSlotWithFlagCheck
FindSlotWithFlagNext:
    iny
    cpy #$10
    bne FindSlotWithFlagLoop
    rts
FindSlotWithFlagCheck:
    lda $0620,y
    bmi FindSlotWithFlagNext
    lda #$FF
    rts
.assert (* - BankStart) = $5342, error, "bank 0 slot release helpers end"

; Check whether the current slot should update this frame. Some flag and frame
; combinations update only its linked position and return without script work.
UpdateCurrentSlot:
    ldx $10                       ; CONTROL_UPDATE_CURRENT_SLOT
    lda $04E0,x
    cmp #$FF
    bne SlotUpdateCheckFrame
SlotUpdateEarlyReturn:
    rts
SlotUpdateCheckFrame:
    jsr $F987
    bne SlotUpdateEarlyReturn
    lda $0630,x
    and #$40
    beq SlotUpdateCheckAlternate
    txa
    eor $20
    and #$01
    beq SlotUpdateCheckAlternate
SlotUpdateLinkedOnly:
    lda $06D0,x
    bmi SlotUpdateEarlyReturn
    jsr UpdateLinkedSlotPosition
    jmp SlotUpdateEarlyReturn
SlotUpdateCheckAlternate:
    lda $14
    beq SlotUpdateCheckPosition
    lda $05E0,x
    and #$20
    beq SlotUpdateCheckPosition
    lda $0630,x
    and #$40
    beq SlotUpdateAlternateBit0
    txa
    eor $20
    and #$02
    bne SlotUpdateLinkedOnly
    jmp SlotUpdateCheckPosition
SlotUpdateAlternateBit0:
    txa
    eor $20
    and #$01
    bne SlotUpdateLinkedOnly

; For slots with $0620 bit $80 set, call the coordinate helper and possibly
; run the slot-load path when the returned horizontal coordinate matches.
SlotUpdateCheckPosition:
    lda $0620,x                  ; CONTROL_SLOT_UPDATE_POSITION
    bpl SlotUpdateCheckContact
    lda $07D0,x
    sta $11
    lda $07E0,x
    sta $12
    lda $05A0,x
    sta $51
    lda $80,x
    tay
    lda $0590,x
    sta $50
    jsr ConvertSlotPosition
    txa
    ldx $10
    bcs SlotUpdatePositionReturn
    sta $0580,x
    tya
    sta $0590,x
    lda $70,x
    cmp #$FE
    beq SlotUpdateReload
    lda $0580,x
    jsr ShiftARight3
    cmp $70,x
    bne SlotUpdatePositionReturn
SlotUpdateReload:
    lda $04E0,x
    sta $2A
    jsr InitializeSlotCheckLoad
    ldx $10
    lda $0620,x
    and #$7F
    sta $0620,x
SlotUpdatePositionReturn:
    rts

; Check the active contact threshold before building the contact rectangle.
SlotUpdateCheckContact:
    lda $0690,x                  ; CONTROL_SLOT_UPDATE_CONTACT
    cmp #$FF
    beq SlotUpdateStartScripts
    cmp #$FE
    beq SlotUpdateContactBounds
    lda $0620,x
    and #$20
    beq SlotUpdateStartScripts
    lda $10
    jsr GetSlotRecordField06
    txa
    ldx $10
    cmp $0690,x
    bcs SlotUpdateToggleContact
SlotUpdateStartScripts:
    jmp PrepareScriptLoop
SlotUpdateToggleContact:
    lda $0620,x
    eor #$20
    sta $0620,x

; Construct a rectangle from packed $06A0/$06C0 fields, with the original
; saturation rules, then scan up to sixteen other slot rectangles.
SlotUpdateContactBounds:
    lda $06A0,x                  ; CONTROL_SLOT_CONTACT_BOUNDS
    and #$0F
    asl a
    sta $11
    ldy $0660,x
    bpl SlotContactPositiveFirst
    lda $0700,x
    sec
    sbc $11
    bcs SlotContactFirstReady
    lda #$00
    jmp SlotContactFirstReady
SlotContactPositiveFirst:
    clc
    adc $0700,x
    bcc SlotContactFirstReady
    lda #$FF
SlotContactFirstReady:
    sta $03
    lda $06A0,x
    and #$F0
    lsr a
    lsr a
    clc
    adc $0590,x
    sta $04
    lda $06C0,x
    and #$0F
    asl a
    asl a
    sta $11
    lda $03
    clc
    adc $11
    bcc SlotContactFirstMaximum
    lda #$FF
SlotContactFirstMaximum:
    sta $05
    lda $03
    sec
    sbc $11
    bcs SlotContactFirstMinimum
    lda #$00
SlotContactFirstMinimum:
    sta $03
    lda $06C0,x
    and #$F0
    lsr a
    lsr a
    sta $11
    lda $04
    clc
    adc $11
    sta $06
    lda $04
    sec
    sbc $11
    bcs SlotContactSecondMinimum
    lda #$00
SlotContactSecondMinimum:
    sta $04
    ldy #$00
SlotContactScan:
    jsr ScriptCheckOtherSlot      ; CONTROL_SLOT_CONTACT_SCAN
    beq SlotContactNext
    lda $05D0,x
    and #$40
    beq SlotContactCheckSecond
    lda $0640,y
    and $0670,x
    bne SlotContactCheckSecond
    lda $0650,y
    and $0680,x
    beq SlotContactNext
SlotContactCheckSecond:
    lda $0590,y
    cmp $04
    bcs SlotContactSecondLower
    lda $B0,y
    cmp $04
    bcs SlotContactCheckFirst
    jmp SlotContactNext
SlotContactSecondLower:
    cmp $06
    bcc SlotContactCheckFirst
    bne SlotContactNext
SlotContactCheckFirst:
    lda $0580,y
    cmp $03
    bcs SlotContactFirstLower
    clc
    adc $0570,y
    bcc SlotContactFirstEnd
    lda #$FF
SlotContactFirstEnd:
    cmp $03
    bcs SlotContactMark
    jmp SlotContactNext
SlotContactFirstLower:
    cmp $05
    bcc SlotContactMark
    bne SlotContactNext
SlotContactMark:
    jsr ScriptMarkOtherSlot
    lda $0620,x
    ora #$08
    sta $0620,x
    lda $04E0,y
    sta $07C0,x
SlotContactNext:
    iny
    cpy #$10
    bne SlotContactScan
    jmp PrepareScriptLoop
.assert (* - BankStart) = $54DA, error, "bank 0 slot update dispatch end"


; $D4DA transfers fields from the current slot to another slot and sets a
; pending value unless bit 0 of its $0790 field is set. Several script
; commands call this helper with a temporary value in $06B0,x.
ScriptMarkOtherSlot:
    lda $10                       ; CONTROL_SCRIPT_MARK_OTHER
    sta $0540,y
    lda $04E0,x
    sta $0760,y
    lda $06B0,x
    sta $0550,y
    lda #$01
    and $0790,y
    bne ScriptMarkOtherReturn
    lda #$09
    sta $04F0,y
ScriptMarkOtherReturn:
    rts

; Restore the saved command pointer, initialize the dispatch counter, and
; decrement two slot counters if nonzero.
PrepareScriptLoop:
    jsr ScriptLoadSlotPointer     ; CONTROL_SCRIPT_PREPARE_LOOP
    lda $0D
    sta $48
    dec $48
    lda $0360,x
    beq ScriptLoopSecondCounter
    dec $0360,x
ScriptLoopSecondCounter:
    lda $0370,x
    beq ScriptLoopPending
    dec $0370,x

; A pending $04F0,x value saves the current slot state, invokes the shared
; $F0D8 path, and clears the per-slot wait count before processing commands.
ScriptLoopPending:
    lda $04F0,x                  ; CONTROL_SCRIPT_PENDING
    beq ScriptLoopContinue
    lda $53
    sta $06E0,x
    lda $54
    sta $06F0,x
    lda $0530,x
    sta $0740,x
    lda $0790,x
    sta $07A0,x
    lda #$FF
    sta $0790,x
    lda $04F0,x
    sta $61
    lda #$00
    sta $04F0,x
    jsr ScriptClear57AndCall
    lda #$00
    sta $0530,x
ScriptLoopContinue:
    lda $0530,x                  ; CONTROL_SCRIPT_LOOP_WAIT
    beq FetchAndDispatchCommand
    dec $0530,x
    jmp UpdateSlotAfterScript
.assert (* - BankStart) = $554E, error, "bank 0 script loop entry"

; Fetch the next variable-length command, advance the script pointer by the
; fetched length and dispatch its opcode. Some surrounding routines and
; handler dependencies remain unconverted, so their semantics are provisional.
FetchAndDispatchCommand:
    ldx #$00                    ; CONTROL_SCRIPT_STEP
    jsr FetchVariableRecord
    ldx $10
    lda $FE
    clc
    adc $53
    sta $53
    bcc ScriptPointerAdvanced
    inc $54
ScriptPointerAdvanced:
    jsr DispatchScriptCommand
    ldx $10
    jsr $DACE
    lda $48
    bpl ScriptCountNonnegative
    dec $48
    bmi ScriptLoopContinue
    jmp UpdateSlotAfterScript
ScriptCountNonnegative:
    dec $48
    bpl ScriptLoopContinue
    jmp UpdateSlotAfterScript
DispatchScriptCommand:
    ldy $60                     ; CONTROL_SCRIPT_DISPATCH
    lda ScriptHandlerHigh,y
    pha
    lda ScriptHandlerLow,y
    pha
    rts
.assert (* - BankStart) = $5585, error, "bank 0 script dispatch offset"
ScriptHandlerLow:
    ScriptTable 1
ScriptHandlerHigh:
    ScriptTable 2
.assert (* - BankStart) = $570F, error, "bank 0 script handler table size"

; The command numbers and their lengths/targets are known from the tables;
; names below describe observed operations rather than claiming original names.
ScriptOp00:
    lda #$FF                     ; CONTROL_SCRIPT_OP00
    sta $06F0,x
ScriptClear57AndCall:
    lda #$00
    sta $57
ScriptCallF0D8:
    lda $61
    jmp LoadSlotRecord

ScriptPushZeroAndCall:
    lda #$00
    sta $57
    lda $2A
    jsr SlotRecordAddressFromIndex
    lda #$00
    pha
    jmp LoadSlotRecordIndirect

; Opcodes $01 and $A3 share this handler. It compares values returned by
; $F357 with per-slot coordinates and command-provided limits. The $A3 variant
; also accepts the opposite orientation before setting the script pointer.
ScriptOp01OrA3:
    jsr FindSlotCoordinates
    lda $63
    sta $03E0
    lda $64
    sta $03E1
    lda $FF
    cmp #$FF
    beq ScriptConditionalReturn
    lda $03E0
    cmp #$FF
    beq ScriptCheckSecondLimit
    lda $FE
    cmp $0700,x
    bcc ScriptFirstNegative
    ldy #$00
    jmp ScriptFirstDirectionReady
ScriptFirstNegative:
    ldy #$80
ScriptFirstDirectionReady:
    tya
    eor $0500,x
    bpl ScriptCheckFirstDistance
    lda $60
    cmp #$A3                     ; CONTROL_SCRIPT_OP01
    bne ScriptConditionalReturn
ScriptCheckFirstDistance:
    lda $FE
    sec
    sbc $0700,x
    cpy #$00
    beq ScriptFirstDistanceReady
    jsr NegateA
ScriptFirstDistanceReady:
    cmp $03E0
    bcs ScriptConditionalReturn
ScriptCheckSecondLimit:
    lda $03E1
    cmp #$FF
    beq ScriptConditionalJump
    lda $FF
    cmp $B0,x
    bcc ScriptSecondNegative
    ldy #$00
    jmp ScriptSecondDirectionReady
ScriptSecondNegative:
    ldy #$80
ScriptSecondDirectionReady:
    lda $FF
    sec
    sbc $B0,x
    cpy #$00
    beq ScriptSecondDistanceReady
    jsr NegateA
ScriptSecondDistanceReady:
    cmp $03E1
    bcs ScriptConditionalReturn
ScriptConditionalJump:
    jmp ScriptSetPointerFromOperands
ScriptConditionalReturn:
    rts

; Probe a sequence of offsets using $F424 and jump on the first nonzero result.
ScriptOp02:
    lda $63
    asl a
    asl a
    asl a
    jsr NegateA
    tay
    ldx #$00                     ; CONTROL_SCRIPT_OP02
    jsr TestSlotOffset
    bne ScriptSetPointerFromOperands
    dec $63
    bne ScriptOp02
    rts

ScriptOp03:
    lda $63
    clc
    adc $0570,x
    ldy $0660,x
    bpl ScriptOp03DirectionReady
    jsr NegateA
ScriptOp03DirectionReady:
    tax
    ldy #$02                     ; CONTROL_SCRIPT_OP03
    jsr TestSlotOffset
    beq ScriptSetPointerFromOperands
    rts

; Opcode $04 and several conditions share this entry: command operand bytes
; $61/$62 become the next script pointer at $53/$54.
ScriptSetPointerFromOperands:
    lda $61                      ; CONTROL_SCRIPT_JUMP
    sta $53
    lda $62
    sta $54
ScriptPointerReturn:
    rts

ScriptOp05:
    jsr AdvanceState19To1B
    lda $63
    cmp $1B                      ; CONTROL_SCRIPT_OP05
    bcc ScriptPointerReturn
    jmp ScriptSetPointerFromOperands

; $FF leaves a field unchanged; zero selects the current slot's $70 value.
ScriptOp06:
    lda $61
    cmp #$FF                     ; CONTROL_SCRIPT_OP06
    beq ScriptOp06SecondField
    cmp #$00
    bne ScriptOp06StoreFirst
    lda $70,x
ScriptOp06StoreFirst:
    sta $05F0,x
ScriptOp06SecondField:
    lda $62
    cmp #$FF
    beq ScriptOp06Return
    cmp #$00
    bne ScriptOp06StoreSecond
    lda $70,x
ScriptOp06StoreSecond:
    sta $0600,x
ScriptOp06Return:
    rts

; Opcode $07 stores a value in the slot and yields the current command loop.
ScriptOp07:
    jsr ScriptOperand61OrSlot
    sta $0530,x                  ; CONTROL_SCRIPT_WAIT
ScriptYield:
    lda #$00
    sta $48
    rts
ScriptOperand61OrSlot:
    lda $61
ScriptOperandOrSlot:
    cmp #$00
    bne ScriptOperandReady
    lda $70,x
ScriptOperandReady:
    rts
ScriptResolveOperand61:
    jsr ScriptOperand61OrSlot
    sta $61
    rts
ScriptOperand62OrSlot:
    lda $62
    jmp ScriptOperandOrSlot
ScriptResolveOperand62:
    jsr ScriptOperand62OrSlot
    sta $62
    rts
ScriptYieldIfNonnegative:
    lda $48
    bpl ScriptYield
    rts

ScriptOp08:
    jsr UpdateSlotFieldsMode00                    ; CONTROL_SCRIPT_OP08
    jmp ScriptYieldIfNonnegative

; Opcode $09 stores its operand, substituting $10 for $FF.
ScriptOp09:
    lda $61
    cmp #$FF
    bne ScriptOp09Store
    lda #$10                     ; CONTROL_SCRIPT_OP09
ScriptOp09Store:
    sta $C0,x
    rts
.assert (* - BankStart) = $5836, error, "bank 0 initial script handlers size"

; Opcode $0A selects or updates per-slot flags and dispatches to $8D14. Several
; paths use the shared position query; retain the original tests.
ScriptOp0A:
    jsr ScriptOperand61OrSlot
    cmp #$FF                     ; CONTROL_SCRIPT_OP0A
    beq ScriptClearSlotMode
    cmp #$01
    beq ScriptSetSlotMode
    cmp #$03
    beq ScriptSetSlotFlags
    cmp #$02
    bne ScriptSetSlotValue
ScriptCheckSlotMode:
    lda $0630,x
    and #$08
    beq ScriptUpdateSlotMode
    lda $0510,x
    bmi ScriptOp0AReturn
ScriptUpdateSlotMode:
    lda $0620,x
    and #$BF
    sta $0620,x
    jsr ScriptSetSlotMode
    ldy $0590,x
    lda $0580,x
    tax
    lda $10
    jsr QuerySlotAtPosition
    ldx $10
    cmp #$00
    beq ScriptClearSlotFlag08
    jsr ScriptClearSlotMode
    lda $0620,x
    ora #$40
    sta $0620,x
ScriptOp0AReturn:
    rts
ScriptSetSlotFlags:
    lda $0630,x
    ora #$08
    sta $0630,x
    lda $0620,x
    ora #$40
    sta $0620,x
    jsr ScriptClearSlotMode
    jmp ScriptCheckSlotMode
ScriptClearSlotFlag08:
    lda $0630,x
    and #$F7
    sta $0630,x
    rts
ScriptSetSlotValue:
    sta $0610,x
    lda $0620,x
    and #$40
    bne ScriptCheckSlotMode
    lda $0620,x
    and #$04
    bne ScriptSetSlotMode
ScriptClearSlotMode:
    lda $0620,x
    and #$FB
    sta $0620,x
    ldx #$00
    jmp ScriptApplySlotMode
ScriptSetSlotMode:
    lda $0620,x
    ora #$04
    sta $0620,x
    lda $0610,x
    tax
ScriptApplySlotMode:
    lda $10
    jsr SetSpriteRecordQueryValue
    ldx $10
    rts

ScriptOp0B:
    lda $61
    sta $0640,x                  ; CONTROL_SCRIPT_OP0B
    lda $62
    sta $0650,x
    rts
; Zero operands use the current slot's $70/$80 pair.
ScriptOp0C:
    lda $61
    sta $0670,x                  ; CONTROL_SCRIPT_OP0C
    lda $62
    sta $0680,x
    bne ScriptOp0CReturn
    lda $61
    bne ScriptOp0CReturn
    lda $70,x
    sta $0670,x
    lda $80,x
    sta $0680,x
ScriptOp0CReturn:
    rts

; The next two commands update different bit fields in $0660,x.
ScriptOp0D:
    lda #$FC                     ; CONTROL_SCRIPT_OP0D
    jmp ScriptUpdateSlotBits
ScriptOp0E:
    lda #$CF                     ; CONTROL_SCRIPT_OP0E
    asl $61
    asl $61
    asl $61
    asl $61
ScriptUpdateSlotBits:
    and $0660,x
    ora $61
    sta $0660,x
    rts

ScriptOp0F:
    jsr ScriptOperand61OrSlot
ScriptSetMainState:
    sta $00                      ; CONTROL_SCRIPT_OP0F
    lda #$00
    sta $58
    jmp ScriptYield

; This updates an indexed association and marks the previous slot with $80.
ScriptOp10:
    lda $0630,x
    and #$81                     ; CONTROL_SCRIPT_OP10
    cmp $61
    beq ScriptOp10Return
    lda $61
    and #$07
    sta $61
    lda $0630,x
    and #$6E
    ora $61
    sta $0630,x
    tay
    lda #$FF
    sta $15,y
    lda $3C,y
    pha
    txa
    sta $3C,y
    pla
    tay
    lda #$80
    ora $0630,y
    sta $0630,y
ScriptOp10Return:
    rts

; $EBAC selects an index used for these state bytes; its full calling convention
; is pending. The two paths share the call at $D95A.
ScriptOp11:
    jsr SelectSlotFlagsOrAbort
    lda $3E,y                    ; CONTROL_SCRIPT_OP11
    sta $61
    lda #$00
    sta $62
    sta $3E,y
ScriptApplyOperandPair:
    jsr UpdateSlotFieldsMode40
    jmp ScriptYieldIfNonnegative
ScriptOp12:
    jsr SelectSlotFlagsOrAbort
    lda $40,y                    ; CONTROL_SCRIPT_OP12
    sta $62
    lda #$00
    sta $61
    sta $40,y
    jmp ScriptApplyOperandPair
ScriptOp13:
    jsr SelectSlotFlagsOrAbort
    lda #$00
    sta $3E,y                    ; CONTROL_SCRIPT_OP13
    rts
ScriptOp14:
    jsr SelectSlotFlagsOrAbort
    lda #$00
    sta $40,y                    ; CONTROL_SCRIPT_OP14
    rts
ScriptOp15:
    jsr SelectSlotFlagsOrAbort
    lda $63
    and $038D,y                  ; CONTROL_SCRIPT_OP15
    beq ScriptOp10Return
    jmp ScriptSetPointerFromOperands

; Use the two operand bytes as a pointer, falling back to the current slot's
; $70/$80 pair when both are zero, and tail-call the routine at $F10C.
ScriptOp16:
    lda $61
    sta $FE                      ; CONTROL_SCRIPT_OP16
    lda $62
    sta $FF
    bne ScriptOp16PointerReady
    lda $61
    bne ScriptOp16PointerReady
    lda $70,x
    sta $FE
    lda $80,x
    sta $FF
ScriptOp16PointerReady:
    jmp LoadSlotRecordAtFE

; Fetch a record using the caller's X, restore the current slot's pointer, and
; return a pointer to the copied record in $FE/$FF, set to $0060.
ScriptFetchRecordAndRestorePointer:
    jsr FetchVariableRecord
    ldx $10
    jsr ScriptLoadSlotPointer
ScriptSetRecordBufferPointer:
    lda #$60                     ; CONTROL_SCRIPT_FETCH_PAIR
    sta $FE
    lda #$00
    sta $FF
    rts

; Restore a previously saved script pointer and per-slot execution state.
ScriptOp17:
    lda $06F0,x
    cmp #$FF                     ; CONTROL_SCRIPT_OP17
    beq ScriptOp17Return
    sta $54
    lda $06E0,x
    sta $53
    lda $0740,x
    sta $0530,x
    lda $07A0,x
    sta $0790,x
    lda $0D
    sta $48
ScriptOp17Return:
    rts

; Opcode $18 dispatches elsewhere; opcode $19 falls through to the pointer
; loader after checking the low three bits and bit $40 returned by $D9FF.
ScriptOp19:
    jsr ScriptGetSlotFlags
    tay
    and #$07                     ; CONTROL_SCRIPT_OP19
    cmp #$02
    bne ScriptOp17Return
    tya
    and #$40
    bne ScriptOp17Return
    jsr ScriptYield
ScriptLoadSlotPointer:
    lda $05B0,x                  ; CONTROL_SCRIPT_SLOT_POINTER
    sta $53
    lda $05C0,x
    sta $54
    rts
ScriptGetSlotPointer:
    lda $05C0,x
    tay
    lda $05B0,x
    rts
ScriptGetSlotFlags:
    lda $10
    jsr RequireSlotRecord
    lda $0400,x
    ldx $10
    rts
.assert (* - BankStart) = $5A0A, error, "bank 0 script handlers through opcode $19"

; Opcode $1A resolves operand $61 and stores it in the current slot.
ScriptOp1A:
    jsr ScriptOperand61OrSlot       ; CONTROL_SCRIPT_OP1A
    sta $0360,x
ScriptOp1AReturn:
    rts

; Opcode $1B branches to the operand pointer when $63 is at least $0360,x.
ScriptOp1B:
    lda $63
    cmp $0360,x                    ; CONTROL_SCRIPT_OP1B
    bcc ScriptOp1AReturn
    jmp ScriptSetPointerFromOperands

; Opcode $1C conditionally updates two fields, with $FF meaning unchanged.
ScriptOp1C:
    lda $06D0,x                    ; CONTROL_SCRIPT_OP1C
    bpl ScriptOp1CReturn
    lda $61
    cmp #$FF
    beq ScriptOp1CSecond
    sta $0710,x
ScriptOp1CSecond:
    lda $62
    cmp #$FF
    beq ScriptOp1CReturn
    sta $0720,x
ScriptOp1CReturn:
    rts

; Opcode $1D resolves each operand and adjusts the second field by $0560,x.
ScriptOp1D:
    jsr ScriptOperand61OrSlot
    cmp #$FF                       ; CONTROL_SCRIPT_OP1D
    beq ScriptOp1DSecond
    sta $0580,x
ScriptOp1DSecond:
    jsr ScriptOperand62OrSlot
    cmp #$FF
    beq ScriptOp1DFinish
    sec
    sbc $0560,x
    clc
    adc #$01
    sta $0590,x
ScriptOp1DFinish:
    jmp UpdateSlotBounds

; Opcode $1E yields and may set a bit in a stack-page buffer. The helper uses
; $CC88 to select the buffer byte; its wider role remains unverified.
ScriptOp1E:
    jsr ScriptYield                ; CONTROL_SCRIPT_OP1E
    lda $61
    beq ScriptOp1ECall
    lda $07B0,x
    jsr ScriptSlotBitMask
    ldx $10
    ora $0100,y
    sta $0100,y
    lda $61
    cmp #$02
    beq ScriptOp1EReturn
ScriptOp1ECall:
    jsr ReleaseCurrentSlot
ScriptOp1EReturn:
    rts
ScriptSlotBitMask:
    pha
    jsr ShiftARight3
    tay
    pla
    and #$07
    tax
    lda ScriptBitMasks,x
    rts
ScriptBitMasks:
    .repeat 8, bit
        .byte 1 << bit             ; CONTROL_SCRIPT_BITMASKS
    .endrepeat

; Opcode $1F prepares another slot, saves the current pointer, runs $CF02 with
; that slot selected, and restores the current slot's pointer. The selection
; and reuse rules are in FindAvailableSlot.
ScriptOp1F:
    jsr FindAvailableSlot                     ; CONTROL_SCRIPT_OP1F
    bne ScriptOp1EReturn
    txa
    tay
    ldx $10
    jsr ScriptOperand61OrSlot
    sta $2A
    lda #$FF
    sta $90,y
    sta $A0,y
    lda #$00
    sta $0620,y
    lda $64
    sta $0780,y
    lda $0580,x
    clc
    adc $62
    sta $0580,y
    lda $0590,x
    clc
    adc $63
    sta $0590,y
ScriptInitializeOtherSlot:
    jsr ScriptSaveSlotPointer
    lda $10
    pha
    sty $10
    lda #$FF
    sta $07B0,y
    jsr InitializeCurrentSlot
    pla
    sta $10
    tax
    jmp ScriptLoadSlotPointer
ScriptSaveSlotPointer:
    lda $53                       ; CONTROL_SCRIPT_SAVE_POINTER
    sta $05B0,x
    lda $54
    sta $05C0,x
ScriptSavedPointerReturn:
    rts

; Opcodes $20-$2A use comparisons and bit tests to change the script pointer
; or update slot fields. Their higher-level gameplay meanings are not known.
ScriptOp20:
    lda $0620,x
    and #$10                      ; CONTROL_SCRIPT_OP20
    beq ScriptSavedPointerReturn
ScriptJumpToOperandPointer:
    jmp ScriptSetPointerFromOperands
ScriptOp21:
    lda $0550,x
    and #$07                      ; CONTROL_SCRIPT_OP21
    sta $11
    eor $0550,x
    sta $0550,x
    lda $0520,x
    sec
    sbc $11
    bcs ScriptOp21Store
    lda #$00
ScriptOp21Store:
    sta $0520,x
    rts
ScriptOp22:
    lda $63
    cmp $0520,x                   ; CONTROL_SCRIPT_OP22
    bcs ScriptJumpToOperandPointer
    rts
ScriptOp23:
    lda $63
    cmp $0760,x                   ; CONTROL_SCRIPT_OP23
    beq ScriptJumpToOperandPointer
    rts
ScriptOp24:
    jsr ScriptGetFieldValue
    cmp $63                       ; CONTROL_SCRIPT_OP24
    beq ScriptJumpToOperandPointer
    rts
ScriptGetFieldValue:
    lda $0550,x
    pha
    and #$08
    asl a
    sta $FE
    pla
    jsr ShiftARight4
    clc
    adc $FE
    rts
ScriptOp25:
    lda $0500,x                   ; CONTROL_SCRIPT_OP25
    bpl ScriptOp25FirstReady
    jsr NegateA
ScriptOp25FirstReady:
    sta $05
    lda $0510,x
    bpl ScriptOp25SecondReady
    jsr NegateA
ScriptOp25SecondReady:
    sta $06
    lda $63
    cmp #$FF
    beq ScriptOp25SecondCompare
    cmp $05
    bcs ScriptOp25SecondCompare
ScriptOp25Return:
    rts
ScriptOp25SecondCompare:
    lda $64
    cmp #$FF
    beq ScriptOp25Jump
    cmp $06
    bcc ScriptOp25Return
ScriptOp25Jump:
    jmp ScriptSetPointerFromOperands
ScriptOp26:
    lda $0620,x
    ora #$20                      ; CONTROL_SCRIPT_OP26
    sta $0620,x
    rts
ScriptOp27:
    lda $0620,x
    and #$08                      ; CONTROL_SCRIPT_OP27
    beq ScriptOp25Return
    eor $0620,x
    sta $0620,x
    jmp ScriptSetPointerFromOperands
ScriptOp28:
    lda $10
    jsr GetSlotRecordField06
    cpx $63                       ; CONTROL_SCRIPT_OP28
    bcs ScriptOp25Jump
    rts
ScriptOp29:
    ldx $61                       ; CONTROL_SCRIPT_OP29
    lda $10
    jmp UpdateSpriteAttribute20
ScriptOp2A:
    lda $63
    cmp $0770,x                   ; CONTROL_SCRIPT_OP2A
    beq ScriptOp25Jump
    rts
.assert (* - BankStart) = $5B85, error, "bank 0 script handlers through opcode $2A"

; Opcode $2B compares an operand to another per-slot field.
ScriptOp2B:
    lda $63
    cmp $0780,x                   ; CONTROL_SCRIPT_OP2B
    beq ScriptOp25Jump
    rts

; Opcodes $2C-$30 set the loop count, call pending routines, or set and clear
; bits in $0790,x. The semantics of $F05C are still unresolved.
ScriptOp2C:
    lda $61                       ; CONTROL_SCRIPT_OP2C
    sta $48
    rts
ScriptOp2D:
    jsr UpdateSlotFieldsMode80                     ; CONTROL_SCRIPT_OP2D
    jmp ScriptYieldIfNonnegative
ScriptOp2E:
    lda #$FF                      ; CONTROL_SCRIPT_OP2E
    sta $05A0,x
    jmp ScriptYield
ScriptOp2F:
    lda $0790,x
    ora $61                       ; CONTROL_SCRIPT_OP2F
    sta $0790,x
    rts
ScriptOp30:
    lda $0790,x
    ora $61
    eor $61                       ; CONTROL_SCRIPT_OP30
    sta $0790,x
    rts

; Opcode $31 processes four audio voice pointers. A $FF second byte skips the
; pair; otherwise it stops the indexed voice and starts it if the high byte is nonzero.
ScriptOp31:
    lda #$00                      ; CONTROL_SCRIPT_OP31
    sta $03
ScriptOp31Loop:
    lda $03
    asl a
    tay
    lda $61,y
    sta $11
    lda $62,y
    sta $12
    jsr ScriptOp31Pair
    lda $03
    cmp #$04
    bne ScriptOp31Loop
    rts
ScriptOp31Pair:
    lda $12
    cmp #$FF
    beq ScriptOp31Next
    lda $03
    jsr StopAudioVoice
    lda $12
    beq ScriptOp31Next
    tay
    lda $11
    tax
    lda $03
    jsr StartAudioVoice
ScriptOp31Next:
    inc $03
    rts
ScriptOp32:
    lda $61                       ; CONTROL_SCRIPT_OP32
    sta $0730,x
    rts

; Opcodes $33 and $34 transfer one indexed field to an operand, clear it and
; call $F061. $EBAC and the called routine need further tracing.
ScriptOp33:
    jsr SelectSlotFlagsOrAbort                     ; CONTROL_SCRIPT_OP33
    lda $3E,y
    sta $61
    lda #$FF
    sta $62
    lda #$00
    sta $3E,y
ScriptCallF061AndYield:
    jsr UpdateSlotFieldsModeC0
    jmp ScriptYieldIfNonnegative
ScriptOp34:
    jsr SelectSlotFlagsOrAbort                     ; CONTROL_SCRIPT_OP34
    lda $40,y
    sta $62
    lda #$FF
    sta $61
    lda #$00
    sta $40,y
    jmp ScriptCallF061AndYield
.assert (* - BankStart) = $5C1C, error, "bank 0 script handlers through opcode $34"

; Opcode $35 searches slots using operands $63-$65. It follows candidates
; until a match has bit $80 clear in $0620,y, then changes the script pointer.
ScriptOp35:
    lda $63                       ; CONTROL_SCRIPT_OP35
    sta $03
    lda $64
    sta $04
    lda $65
    sta $06
    jsr ScriptDefaultSearchFields
    jsr ScriptFindSlot
ScriptOp35Check:
    bne ScriptFindSlotReturn
    lda $0620,y
    bmi ScriptOp35Next
    jmp ScriptSetPointerFromOperands
ScriptOp35Next:
    jsr ScriptFindNextSlot
    jmp ScriptOp35Check
ScriptDefaultSearchFields:
    lda $06
    bne ScriptDefaultSearchReturn
    lda $04
    bne ScriptDefaultSearchReturn
    lda $70,x
    sta $04
    lda $80,x
    sta $06
ScriptDefaultSearchReturn:
    rts

; Search other slots, preserving the comparison result while restoring X to
; the current slot. $04E0,y == $FF and the current slot are skipped.
ScriptFindSlot:
    ldy #$00
ScriptFindSlotLoop:
    jsr ScriptCheckOtherSlot
    beq ScriptFindNextSlot
    ldx $03
    bne ScriptFindCompareFirst
    lda $A0,y
    cmp $06
    bne ScriptFindNextSlot
    lda $90,y
ScriptFindCompareFirst:
    cmp $04
    beq ScriptFindSlotReturn
ScriptFindNextSlot:
    iny
    cpy #$10
    bne ScriptFindSlotLoop
    cpy #$00
ScriptFindSlotReturn:
    php
    ldx $10
    plp
    rts
ScriptCheckOtherSlot:
    cpy $10
    beq ScriptCheckOtherSlotReturn
ScriptCheckSlotPresent:
    lda $04E0,y
    cmp #$FF
ScriptCheckOtherSlotReturn:
    rts

; Opcode $36 visits matching slots, temporarily changing $06B0,x around each
; call to $D4DA. Operand $62 = $FF selects the alternate scan of flagged slots.
ScriptOp36:
    lda $62
    cmp #$FF                      ; CONTROL_SCRIPT_OP36
    beq ScriptOp36ScanFlagged
    sta $03
    lda $63
    sta $04
    lda $64
    sta $06
    bne ScriptOp36Find
    lda $04
    jsr ScriptOperandOrSlot
    sta $04
ScriptOp36Find:
    jsr ScriptFindSlot
    bne ScriptOp36Return
ScriptOp36Apply:
    lda $06B0,x
    pha
    lda $61
    sta $06B0,x
    jsr ScriptMarkOtherSlot
    pla
    sta $06B0,x
    jsr ScriptFindNextSlot
    beq ScriptOp36Apply
ScriptOp36Return:
    rts
ScriptOp36ScanFlagged:
    ldy #$00
ScriptOp36ScanLoop:
    jsr ScriptCheckOtherSlot
    beq ScriptOp36ScanNext
    lda $0630,y
    bpl ScriptOp36ScanNext
    lda $06B0,x
    pha
    lda $61
    sta $06B0,x
    jsr ScriptMarkOtherSlot
    pla
    sta $06B0,x
ScriptOp36ScanNext:
    iny
    cpy #$10
    bne ScriptOp36ScanLoop
    rts
.assert (* - BankStart) = $5CD4, error, "bank 0 script handlers through opcode $36"

; Opcodes $37-$3A share this handler. After $EB8B selects an indexed field,
; it adds the resolved operand and clamps on carry according to its sign.
ScriptOp37To3A:
    jsr SelectScriptField                    ; CONTROL_SCRIPT_OP37
    bne ScriptOp37Return
    jsr ScriptOperand62OrSlot
    clc
    adc $46,y
    sta $46,y
    ldx $62
    bmi ScriptOp37Negative
    bcc ScriptOp37Return
    lda #$FF
ScriptOp37Clamp:
    sta $46,y
ScriptOp37Return:
    rts
ScriptOp37Negative:
    lda #$00
    bcc ScriptOp37Clamp
    rts
ScriptOp3B:
    jsr SelectScriptField                    ; CONTROL_SCRIPT_OP3B
    bne ScriptOp3BReturn
    jsr ScriptOperand62OrSlot
    sta $46,y
ScriptOp3BReturn:
    rts
ScriptOp3C:
    jsr SelectScriptField                    ; CONTROL_SCRIPT_OP3C
    bne ScriptOp3CReturn
    lda $46,y
    cmp $62
    bcc ScriptOp3CReturn
    lda $63
    sta $61
    lda $64
    sta $62
    jmp ScriptSetPointerFromOperands
ScriptOp3CReturn:
    rts
ScriptOp3D:
    lda $07                      ; CONTROL_SCRIPT_OP3D
    ldy #$00
    sty $07
    cmp #$00
    bne ScriptOp3CReturn
    jmp ScriptSetPointerFromOperands
ScriptOp3E:
    lda $61                      ; CONTROL_SCRIPT_OP3E
    sta $70,x
    lda $62
    sta $80,x
    rts

; Opcode $3F clears the high byte of the slot value, then selects an observed
; value or calculation by operand $61. Unknown selectors fall through to $F3CA.
ScriptOp3F:
    jsr ScriptClearSlotHigh      ; CONTROL_SCRIPT_OP3F
    ldy $61
    lda $0780,x
    cpy #$00
    bne ScriptOp3FCompareOther
ScriptOp3FEarlyStore:
    jmp ScriptStoreSlotLow
ScriptOp3FCompareOther:
    lda $0770,x
    cpy #$2A
    beq ScriptOp3FEarlyStore
    jsr ScriptGetFieldValue
    cpy #$24
    beq ScriptOp3FEarlyStore
    lda $0760,x
    cpy #$23
    beq ScriptOp3FEarlyStore
    lda $07C0,x
    cpy #$45
    beq ScriptOp3FEarlyStore
    lda $E6
    cpy #$AA
    beq ScriptOp3FEarlyStore
    lda $0570,x
    cpy #$1D
    beq ScriptOp3FEarlyStore
    lda $01
    cpy #$0F
    beq ScriptStoreSlotLow
    lda $0520,x
    cpy #$01
    beq ScriptStoreSlotLow
    lda $04E0,x
    cpy #$02
    beq ScriptStoreSlotLow
    lda $0660,x
    and #$C0
    cpy #$4C
    beq ScriptStoreSlotLow
    lda $0700,x
    cpy #$51
    beq ScriptStoreSlotLow
    lda $B0,x
    cpy #$52
    beq ScriptStoreSlotLow
    lda $D0,x
    cpy #$0B
    beq ScriptStoreSlotLow
    lda $0500,x
    cpy #$11
    beq ScriptStoreSlotLow
    lda $0510,x
    cpy #$12
    beq ScriptStoreSlotLow
    cpy #$04
    beq ScriptCountUnusedToSlot
    cpy #$07
    beq ScriptOp3FCompareCoordinates
    cpy #$08
    beq ScriptOp3FCompareCoordinates
    cpy #$19
    beq ScriptOp3FCompareCoordinates
    cpy #$1A
    beq ScriptOp3FCompareCoordinates
    lda $0710,x
    cpy #$16
    beq ScriptStoreSlotLow
    lda $0720,x
    cpy #$17
    beq ScriptStoreSlotLow
    lda $05D0,x
    cpy #$88
    beq ScriptStoreSlotLow
    cpy #$13
    beq ScriptOp3FReadIndirect
    lda $0550,x
    and #$07
    cpy #$21
    beq ScriptStoreSlotLow
    cpy #$0C
    beq ScriptCopySlotPair
    cpy #$18
    beq ScriptCountMarkedSlots
    jsr AdvanceState19To1B
ScriptStoreSlotLow:
    sta $70,x
    rts

; The following helpers are shared branch targets in the selector above.
ScriptStoreSlotPair:
    sta $70,x                    ; CONTROL_SCRIPT_STORE_PAIR
    sta $80,x
    rts
ScriptCountUnusedToSlot:
    jsr ScriptCountUnusedSlots
ScriptStoreYToSlot:
    tya
    ldx $10
    jmp ScriptStoreSlotLow
ScriptCopySlotPair:
    lda $0670,x                  ; CONTROL_SCRIPT_COPY_PAIR
    sta $70,x
    lda $0680,x
    sta $80,x
    rts
ScriptOp3FCompareCoordinates:
    sty $03                      ; CONTROL_SCRIPT_COMPARE_COORDS
    jsr FindSlotCoordinates
    cmp #$FF
    beq ScriptStoreSlotPair
    lda $03
    cmp #$1A
    beq ScriptCoordinateDifferenceY
    cmp #$19
    beq ScriptCoordinateDifferenceX
    cmp #$08
    beq ScriptCoordinateCompareY
    ldy #$00
    lda $FE
    cmp $0700,x
    bcs ScriptStoreYToSlot
    ldy #$01
    jmp ScriptStoreYToSlot
ScriptCoordinateCompareY:
    ldy #$00
    lda $FF
    cmp $B0,x
    bcs ScriptStoreYToSlot
    ldy #$01
    jmp ScriptStoreYToSlot
ScriptOp3FReadIndirect:
    jsr SlotRecordAddressFromCurrent                    ; CONTROL_SCRIPT_READ_INDIRECT
    ldy #$03
    lda ($FE),y
    jmp ScriptStoreSlotLow
ScriptCoordinateDifferenceY:
    lda $FF                      ; CONTROL_SCRIPT_COORD_DIFF
    sec
    sbc $B0,x
ScriptCoordinateMagnitude:
    bpl ScriptCoordinateStore
    jsr NegateA
ScriptCoordinateStore:
    jmp ScriptStoreSlotLow
ScriptCoordinateDifferenceX:
    lda $FE
    sec
    sbc $0700,x
    jmp ScriptCoordinateMagnitude
ScriptCountMarkedSlots:
    ldy #$00                     ; CONTROL_SCRIPT_MARKED_SLOTS
    sty $11
ScriptCountMarkedLoop:
    jsr ScriptCheckOtherSlot
    beq ScriptCountMarkedNext
    beq ScriptCountMarkedNext     ; Original repeated branch retained.
    lda $05D0,y
    and #$04
    beq ScriptCountMarkedNext
    inc $11
ScriptCountMarkedNext:
    iny
    cpy #$10
    bne ScriptCountMarkedLoop
    lda $11
    jmp ScriptStoreSlotLow
ScriptCountUnusedSlots:
    ldy #$00                     ; CONTROL_SCRIPT_UNUSED_SLOTS
    ldx #$00
ScriptCountUnusedLoop:
    lda $04E0,x
    cmp #$FF
    bne ScriptCountUnusedNext
    iny
ScriptCountUnusedNext:
    inx
    cpx #$10
    bne ScriptCountUnusedLoop
    rts
.assert (* - BankStart) = $5E83, error, "bank 0 script handlers through opcode $3F"

; Opcodes $40-$45 operate on the two-byte slot value and script pointer.
ScriptOp40:
    lda $61
    and $70,x                    ; CONTROL_SCRIPT_OP40
    sta $70,x
    lda $62
    and $80,x
    sta $80,x
ScriptOp40Return:
    rts
ScriptOp41:
    lda $70,x                    ; CONTROL_SCRIPT_OP41
    sec
    sbc $63
    lda $80,x
    sbc $64
    bcc ScriptOp40Return
    jmp ScriptSetPointerFromOperands
ScriptOp42:
    lda $61
    clc
    adc $70,x                    ; CONTROL_SCRIPT_OP42
    sta $70,x
    lda $62
    adc $80,x
    sta $80,x
    rts
ScriptOp43:
    lda $61
    eor #$FF                     ; CONTROL_SCRIPT_OP43
    sta $18
    rts
ScriptOp44:
    lda $70,x                    ; CONTROL_SCRIPT_OP44
    asl a
    clc
    adc $53
    sta $53
    bcc ScriptOp44PointerReady
    inc $54
ScriptOp44PointerReady:
    ldx #$02
    jsr FetchVariableRecord
    ldx $10
    lda $61
    sta $62
    lda $60
    sta $61
ScriptOp44Jump:
    jmp ScriptSetPointerFromOperands
ScriptOp45:
    lda $63
    cmp $07C0,x                  ; CONTROL_SCRIPT_OP45
    beq ScriptOp44Jump
    rts

; The selector determines whether opcodes $46-$48 use the single-byte array
; at $0140 or the paired bytes at $0120. $FF selects the current slot's pair.
ScriptOp46:
    jsr ScriptSelectValueArray   ; CONTROL_SCRIPT_OP46
    beq ScriptOp46ReadPair
    lda $0140,y
ScriptStoreSlotLowAndClearHigh:
    sta $70,x
ScriptClearSlotHigh:
    lda #$00
    sta $80,x
    rts
ScriptOp46ReadPair:
    lda $0120,y
    sta $70,x
    lda $0121,y
    sta $80,x
    rts
ScriptOp47:
    jsr ScriptSelectValueArray   ; CONTROL_SCRIPT_OP47
    beq ScriptOp47WritePair
    lda $70,x
    sta $0140,y
    rts
ScriptOp47WritePair:
    lda $70,x
    sta $0120,y
    lda $80,x
    sta $0121,y
    rts
ScriptSelectValueArray:
    ldy $61                      ; CONTROL_SCRIPT_VALUE_ARRAY
    cpy #$FF
    bne ScriptSelectArrayReturn
    lda $10
    asl a
    tay
    lda #$00
ScriptSelectArrayReturn:
    rts
ScriptOp48:
    jsr ScriptSelectValueArray   ; CONTROL_SCRIPT_OP48
    beq ScriptOp48AddPair
    lda $70,x
    clc
    adc $0140,y
    sta $70,x
    bcc ScriptOp48Return
    inc $80,x
ScriptOp48Return:
    rts
ScriptOp48AddPair:
    lda $70,x
    clc
    adc $0120,y
    sta $70,x
    lda $80,x
    adc $0121,y
    sta $80,x
    rts

; Opcode $49 uses the same two unconverted routines as the four-pair loop.
; Opcode $50 enters this sequence at the second load of $62.
ScriptOp49:
    lda $62
    cmp #$FF                     ; CONTROL_SCRIPT_OP49
    beq ScriptOp49Return
    lda #$04
    jsr StopAudioVoice
ScriptOp50:
    lda $62                      ; CONTROL_SCRIPT_OP50
    beq ScriptOp49Return
    cmp #$FF
    beq ScriptOp49Return
    tay
    lda $61
    tax
    lda #$04
    jsr StartAudioVoice
ScriptOp49Return:
    rts
ScriptOp4A:
    jsr ScriptOperand61OrSlot    ; CONTROL_SCRIPT_OP4A
    sta $0370,x
ScriptOp4AReturn:
    rts
ScriptOp4B:
    lda $63
    cmp $0370,x                  ; CONTROL_SCRIPT_OP4B
    bcc ScriptOp4AReturn
    jmp ScriptSetPointerFromOperands
ScriptOp4C:
    jsr ScriptOperand61OrSlot    ; CONTROL_SCRIPT_OP4C
    sta $07F0,x
    rts
.assert (* - BankStart) = $5F6D, error, "bank 0 script handlers through opcode $4C"

; Opcodes $4D and $4E select related $CCxx routines. A zero pair is replaced
; with the current slot's two-byte value before calling the paired routines.
ScriptOp4D:
    ldx $61                     ; CONTROL_SCRIPT_OP4D
    ldy $62
    cpy #$FF
    bne ScriptOp4DPair
    jmp SelectFirstRelatedPointer
ScriptOp4DPair:
    jsr ScriptResolvePair
    jmp ApplyFirstRelatedPointer
ScriptResolvePair:
    cpy #$00
    bne ScriptResolvePairReturn
    cpx #$00
    bne ScriptResolvePairReturn
    ldx $10
    ldy $80,x
    lda $70,x
    tax
ScriptResolvePairReturn:
    rts
ScriptOp4E:
    ldx $61                     ; CONTROL_SCRIPT_OP4E
    ldy $62
    cpy #$FF
    bne ScriptOp4EPair
    jmp SelectSecondRelatedPointer
ScriptOp4EPair:
    jsr ScriptResolvePair
    jmp ApplySecondRelatedPointer
ScriptOp4F:
    lda $61                     ; CONTROL_SCRIPT_OP4F
    sta $03BC
ScriptOp4FReturn:
    rts

; Opcodes $51-$53 compare fields and may jump to the operand pointer.
ScriptOp51:
    lda $63
    cmp $0700,x                 ; CONTROL_SCRIPT_OP51
    bcc ScriptOp4FReturn
ScriptOp51Jump:
    jmp ScriptSetPointerFromOperands
ScriptOp52:
    lda $63
    cmp $B0,x                   ; CONTROL_SCRIPT_OP52
    bcs ScriptOp51Jump
    rts
ScriptOp53:
    lda $63
    cmp $70,x                   ; CONTROL_SCRIPT_OP53
    bne ScriptOp4FReturn
    lda $64
    cmp $80,x
    beq ScriptOp51Jump
    rts

; Opcode $54 fetches a two-byte record from an address formed by adding the
; operands to the slot value, then restores the saved command pointer.
ScriptOp54:
    jsr ScriptSaveSlotPointer   ; CONTROL_SCRIPT_OP54
    lda $61
    clc
    adc $70,x
    sta $53
    lda $62
    adc $80,x
    sta $54
    ldx #$02
    jsr FetchVariableRecord
    ldx $10
    lda $60
    sta $70,x
    lda $61
    sta $80,x
    jmp ScriptLoadSlotPointer
ScriptOp55:
    lda $13
    ora $61                     ; CONTROL_SCRIPT_OP55
    sta $13
    rts
ScriptOp56:
    lda $13
    ora $61
    eor $61                     ; CONTROL_SCRIPT_OP56
    sta $13
    rts

; Opcodes $57 and $58 prepare operands and reuse the 16-bit comparison in $41.
ScriptOp57To58:
    jsr ScriptSelectValueArray  ; CONTROL_SCRIPT_OP57
    beq ScriptOp57ReadPair
    lda #$00
    sta $64
    lda $0140,y
    jmp ScriptOp57Compare
ScriptOp57ReadPair:
    lda $0121,y
    sta $64
    lda $0120,y
ScriptOp57Compare:
    tay
    lda $62
    sta $61
    lda $63
    sta $62
    sty $63
    jmp ScriptOp41
ScriptOp59:
    jsr ScriptResolveOperand61  ; CONTROL_SCRIPT_OP59
    jsr ScriptResolveOperand62
    jsr UpdateSlotFieldsMode00
    jmp ScriptYieldIfNonnegative

; Opcode $5A exchanges the slot value with the selected array value.
ScriptOp5A:
    jsr ScriptSelectValueArray  ; CONTROL_SCRIPT_OP5A
    beq ScriptOp5AExchangePair
    lda $0140,y
    pha
    lda $70,x
    sta $0140,y
ScriptOp5AStoreLow:
    pla
    sta $70,x
    rts
ScriptOp5AExchangePair:
    lda $0120,y
    pha
    lda $0121,y
    pha
    jsr ScriptOp47WritePair
    pla
    sta $80,x
    jmp ScriptOp5AStoreLow
ScriptOp5B:
    lda $61
    eor $70,x                   ; CONTROL_SCRIPT_OP5B
    sta $70,x
    lda $62
    eor $80,x
    sta $80,x
    rts
ScriptOp5CTo5D:
    jsr ScriptOperand61OrSlot   ; CONTROL_SCRIPT_OP5C
    ora $D0,x
    sta $D0,x
    rts
ScriptOp5E:
    jsr ScriptResolveOperand61  ; CONTROL_SCRIPT_OP5E
    ora $D0,x
    eor $61
    sta $D0,x
ScriptOp5EReturn:
    rts
ScriptOp5F:
    lda $63
    and $D0,x                   ; CONTROL_SCRIPT_OP5F
    beq ScriptOp5EReturn
    jmp ScriptSetPointerFromOperands
ScriptOp60:
    lda $63
    and $D0,x                   ; CONTROL_SCRIPT_OP60
    bne ScriptOp5EReturn
    jmp ScriptSetPointerFromOperands
.assert (* - BankStart) = $607A, error, "bank 0 script handlers through opcode $60"

; Opcode $61 prepares another slot similarly to $1F. FindAvailableSlot
; decides whether a destination is available; the two callers share
; the save, initialization and restore sequence beginning at $DAB7.
ScriptOp61:
    jsr FindAvailableSlot                    ; CONTROL_SCRIPT_OP61
    bne ScriptOp5EReturn
    txa
    tay
    ldx $10
    jsr ScriptOperand61OrSlot
    sta $2A
    lda #$FF
    sta $90,y
    sta $A0,y
    lda #$00
    sta $0620,y
    lda $64
    sta $0780,y
    lda $62
    sta $0580,y
    lda $63
    sta $0590,y
    tya
    pha
    jsr ScriptInitializeOtherSlot
    pla
    tay
    lda #$00
    rts

; Opcodes $62 and $66 test offsets via $F424 before changing the pointer.
ScriptOp62:
    lda $0660,x                  ; CONTROL_SCRIPT_OP62
    bpl ScriptOp62Positive
    ldx #$F8
    jmp ScriptOp62Test
ScriptOp62Positive:
    ldx #$08
ScriptOp62Test:
    ldy #$00
    stx $05
    jsr TestSlotOffset
    beq ScriptOp66Return
    lda $63
    asl a
    asl a
    asl a
    jsr NegateA
    tay
    ldx $05
    jsr TestSlotOffset
    bne ScriptOp66Return
ScriptOp62Jump:
    jmp ScriptSetPointerFromOperands
ScriptOp63:
    lda $62                      ; CONTROL_SCRIPT_OP63
    sta $57
    jmp ScriptCallF0D8
ScriptOp64:
    lda $61
    eor #$FF                     ; CONTROL_SCRIPT_OP64
    sta $3B
    rts
ScriptOp65:
    lda $0750,x                  ; CONTROL_SCRIPT_OP65
    ldy $61
    beq ScriptOp65Second
    and #$F0
    ora #$03
ScriptOp65Second:
    ldy $62
    beq ScriptOp65Store
    and #$0F
    ora #$20
ScriptOp65Store:
    sta $0750,x
    rts
ScriptOp66:
    lda $63                      ; CONTROL_SCRIPT_OP66
    asl a
    asl a
    asl a
    tay
    ldx #$00
    jsr TestSlotOffset
    bne ScriptOp62Jump
    dec $63
    bne ScriptOp66
ScriptOp66Return:
    rts

; Opcode $67 finds a slot and stores relative field values before yielding.
; $63 == $23 uses the already selected $0540,x slot instead of a search.
ScriptOp67:
    jsr ScriptOp67FindAndSet     ; CONTROL_SCRIPT_OP67
    jmp ScriptYield
ScriptOp67FindAndSet:
    lda $63
    sta $03
    lda $64
    sta $04
    lda $65
    sta $06
    bne ScriptOp67Select
    lda $04
    jsr ScriptOperandOrSlot
    sta $04
ScriptOp67Select:
    lda $63
    cmp #$23
    bne ScriptOp67Search
    ldy $0540,x
    bmi ScriptOp67Return
    jmp ScriptOp67Selected
ScriptOp67Search:
    jsr ScriptFindSlot
    bne ScriptOp67Return
ScriptOp67Selected:
    tya
    sta $06D0,x
    lda $61
    cmp #$FF
    bne ScriptOp67StoreFirst
    lda $0580,x
    sec
    sbc $0580,y
ScriptOp67StoreFirst:
    sta $0710,x
    lda $62
    cmp #$FF
    bne ScriptOp67StoreSecond
    lda $0590,x
    sec
    sbc $0590,y
ScriptOp67StoreSecond:
    sta $0720,x
ScriptOp67Return:
    rts
ScriptOp68:
    lda #$FF                     ; CONTROL_SCRIPT_OP68
    sta $06D0,x
    lda #$20
    sta $0710,x
    lda #$00
    sta $0720,x
    rts

; Opcode $69 creates a slot with $61/$62 offsets and temporarily makes it
; current for a call to $EFA0. On failure it discards both saved operands.
ScriptOp69:
    lda $62                      ; CONTROL_SCRIPT_OP69
    pha
    lda #$FF
    sta $62
    lda $63
    pha
    lda #$F8
    sec
    sbc $03EC
    sta $63
    jsr ScriptOp61
    bne ScriptOp69Failure
    lda $10
    sta $06D0,y
    pla
    sta $0720,y
    pla
    sta $0710,y
    lda $10
    pha
    sty $10
    jsr UpdateLinkedSlotPosition
    pla
    sta $10
    rts
ScriptOp69Failure:
    pla
    pla
    rts
ScriptOp6A:
    lda $0630,x
    and #$BF                     ; CONTROL_SCRIPT_OP6A
    ldy $61
    cpy #$FF
    beq ScriptOp6AStore
    ora #$40
ScriptOp6AStore:
    sta $0630,x
ScriptOp6AReturn:
    rts
ScriptOp6B:
    lda $06D0,x
    cmp #$FF                     ; CONTROL_SCRIPT_OP6B
    beq ScriptOp6AReturn
    jmp ScriptSetPointerFromOperands
ScriptOp6C:
    lda $61
    cmp #$FF                     ; CONTROL_SCRIPT_OP6C
    beq ScriptOp6CSecond
    jsr ScriptOperandOrSlot
    sta $0710,x
ScriptOp6CSecond:
    lda $62
    cmp #$FF
    beq ScriptOp6CYield
    jsr ScriptOperandOrSlot
    sta $0720,x
ScriptOp6CYield:
    jmp ScriptYield

; Opcodes $6D/$6E and $6F wait when $E7 is nonzero. Otherwise they set a
; command value and parameters for an unconverted consumer of this state.
ScriptOp6DTo6E:
    lda $E7                      ; CONTROL_SCRIPT_OP6D
    beq ScriptOp6DSetup
ScriptWaitForState:
    jsr ScriptLoadSlotPointer
    jmp ScriptYield
ScriptOp6DSetup:
    lda $61
    sta $EA
    lda $62
    sta $EB
    lda $63
    sta $E8
    lda $64
    sta $E9
    lda #$6E
    sta $04D9
    lda $65
    sta $04D8
    lda $66
    sta $E7
    rts
ScriptOp6F:
    lda $E7                      ; CONTROL_SCRIPT_OP6F
    bne ScriptWaitForState
    lda $61
    sta $E8
    lda $62
    sta $E9
    lda $63
    sta $EA
    lda #$6F
    sta $04D9
    lda $64
    sta $04D8
    lda $65
    sta $E7
    rts
.assert (* - BankStart) = $6221, error, "bank 0 script handlers through opcode $6F"

; Opcodes $70/$71 use the selected byte or pair with $9E63, placing its
; results in the slot and selected array. The arithmetic routine is unconverted.
ScriptOp70To71:
    jsr ScriptSelectValueArray   ; CONTROL_SCRIPT_OP70
    beq ScriptOp70Pair
    sty $11
    lda $0140,y
    pha
    lda $80,x
    tay
    lda $70,x
    tax
    pla
    jsr DivideUnsigned16By8
    txa
    ldx $10
    sta $70,x
    tya
    ldy $11
    sta $0140,y
    jmp ScriptClearSlotHigh
ScriptOp70Pair:
    sty $11
    lda $0120,y
    pha
    lda $80,x
    tay
    lda $70,x
    tax
    pla
    jsr DivideUnsigned16By8
    txa
    ldx $10
    sta $70,x
    tya
    ldy $11
    sta $0120,y
    lda #$00
    sta $0121,y
    jmp ScriptClearSlotHigh
ScriptOp72:
    jsr ScriptSelectValueArray   ; CONTROL_SCRIPT_OP72
    bne ScriptOp72Byte
    lda $0120,y
    jmp ScriptOp72Calculate
ScriptOp72Byte:
    lda $0140,y
ScriptOp72Calculate:
    ldy $70,x
    tax
    jsr MultiplyUnsigned8
    txa
    ldx $10
    sta $70,x
    tya
    sta $80,x
    rts
ScriptOp73:
    jsr SelectScriptField                    ; CONTROL_SCRIPT_OP73
    bne ScriptOp73Return
    lda $46,y
    jmp ScriptStoreSlotLowAndClearHigh
ScriptOp73Return:
    rts
ScriptOp74:
    jmp ScriptWaitForState       ; CONTROL_SCRIPT_OP74
ScriptOp75To76:
    jsr ScriptOperand61OrSlot    ; CONTROL_SCRIPT_OP75
    sta $0520,x
    rts

; Opcode $77 examines up to four audio voice states. The helper discards
; its return address on a successful test before jumping to the script target.
ScriptOp77:
    ldx $63                      ; CONTROL_SCRIPT_OP77
    lda #$00
    jsr ScriptOp77Test
    ldx $64
    lda #$01
    jsr ScriptOp77Test
    ldx $65
    lda #$02
    jsr ScriptOp77Test
    ldx $66
    lda #$03
    jmp ScriptOp77Test
ScriptOp77Test:
    cpx #$FF
    beq ScriptOp77Return
    jsr IsAudioVoiceActive
    beq ScriptOp77Return
    pla
    pla
    jmp ScriptSetPointerFromOperands
ScriptOp77Return:
    rts

; Opcode $78 fetches an eight-byte record indexed by $70,x and processes four
; pairs using the same helper as opcode $31. Pointer restoration is shared.
ScriptOp78:
    jsr ScriptFetchIndexedEight   ; CONTROL_SCRIPT_OP78
    lda $FE
    sta $55
    lda $FF
    sta $56
    lda #$00
    sta $03
ScriptOp78Loop:
    asl a
    tay
    lda ($55),y
    sta $11
    iny
    lda ($55),y
    sta $12
    jsr ScriptOp31Pair
    lda $03
    cmp #$04
    bne ScriptOp78Loop
    rts
ScriptFetchIndexedEight:
    jsr ScriptSaveSlotPointer
    lda #$00
    sta $54
    lda $70,x
    jsr ScriptShiftPointerOffset
    jsr ScriptShiftPointerOffset
    jsr ScriptShiftPointerOffset
    clc
    adc $61
    sta $53
    lda $62
    adc $54
    sta $54
    ldx #$08
    jmp ScriptFetchRecordAndRestorePointer
ScriptShiftPointerOffset:
    asl a
    rol $54
    rts
ScriptOp79:
    stx $03                      ; CONTROL_SCRIPT_OP79
    lda #$0F
    sta $10
ScriptOp79Loop:
    lda $10
    cmp $03
    beq ScriptOp79Next
    jsr ReleaseCurrentSlot
ScriptOp79Next:
    dec $10
    bpl ScriptOp79Loop
    ldx $03
    stx $10
    rts
ScriptOp7A:
    jsr ScriptOperand61OrSlot    ; CONTROL_SCRIPT_OP7A
    ldy #$00
    sty $61
ScriptOp7ALoop:
    cmp $04E0,y
    bne ScriptOp7ANext
    inc $61
ScriptOp7ANext:
    iny
    cpy #$10
    bne ScriptOp7ALoop
    lda #$00
    sta $62
    jmp ScriptOp3E
ScriptOp7B:
    ldx $63                      ; CONTROL_SCRIPT_OP7B
    ldy $64
    jsr TestSlotOffset
    beq ScriptOp7BReturn
    jmp ScriptSetPointerFromOperands
ScriptOp7BReturn:
    rts
.assert (* - BankStart) = $634E, error, "bank 0 script handlers through opcode $7B"

; Opcodes $7C/$7D resolve operands and adjust the first using the selected
; slot's $0660 sign before calling $F061 and conditionally yielding.
ScriptOp7CTo7D:
    jsr ScriptResolveOperand61   ; CONTROL_SCRIPT_OP7C
    jsr ScriptResolveOperand62
    ldy $0540,x
    lda $0660,y
    bpl ScriptOp7CCall
    lda $61
    jsr NegateA
    sta $61
ScriptOp7CCall:
    jsr UpdateSlotFieldsModeC0
    jmp ScriptYieldIfNonnegative
ScriptOp7E:
    jsr ComputeSlotScaledPosition                    ; CONTROL_SCRIPT_OP7E
    lda $11
    sta $70,x
    lda $12
    sta $80,x
    rts

; Opcode $7F waits for the shared state, or fetches a pair indexed by the
; current slot value and continues into the $6D/$6E state setup.
ScriptOp7F:
    lda $E7                      ; CONTROL_SCRIPT_OP7F
    beq ScriptOp7FFetch
    jmp ScriptWaitForState
ScriptOp7FFetch:
    jsr ScriptSaveSlotPointer
    lda $70,x
    asl a
    clc
    adc $61
    sta $53
    lda $62
    adc #$00
    sta $54
    ldx #$02
    jsr FetchVariableRecord
    ldx $10
    jsr ScriptLoadSlotPointer
    lda $61
    sta $62
    lda $60
    sta $61
    jmp ScriptOp6DSetup
ScriptOp80:
    lda $61                      ; CONTROL_SCRIPT_OP80
    sec
    sbc $70,x
    lda $62
    sbc $80,x
    bcs ScriptOp80Return
    lda $61
    sta $70,x
    lda $62
    sta $80,x
ScriptOp80Return:
    rts
ScriptOp81:
    jsr ScriptResolveOperand61   ; CONTROL_SCRIPT_OP81
    jsr ScriptResolveOperand62
    lda $0660,x
    bpl ScriptOp81Second
    lda $61
    cmp #$FF
    bne ScriptOp81NegateFirst
    lda #$00
ScriptOp81NegateFirst:
    jsr NegateA
    sta $61
ScriptOp81Second:
    lda $0660,x
    and #$40
    beq ScriptOp81Call
    lda $62
    cmp #$FF
    bne ScriptOp81NegateSecond
    lda #$00
ScriptOp81NegateSecond:
    jsr NegateA
    sta $62
ScriptOp81Call:
    jsr UpdateSlotFieldsMode40
    jmp ScriptYieldIfNonnegative
ScriptOp82:
    lda $63
    cmp $70,x                    ; CONTROL_SCRIPT_OP82
    bne ScriptOp82Jump
    lda $64
    cmp $80,x
    beq ScriptOp80Return
ScriptOp82Jump:
    jmp ScriptSetPointerFromOperands
ScriptOp83:
    lda $E7                      ; CONTROL_SCRIPT_OP83
    bne ScriptOp83Wait
    lda $61
    sta $E9
    lda $62
    sta $E8
    lda #$83
    sta $04D9
    lda #$01
    sta $E7
    rts
ScriptOp83Wait:
    jmp ScriptWaitForState
ScriptOp84:
    jsr SelectSlotFlagsOrAbort                    ; CONTROL_SCRIPT_OP84
    lda $61
    sta $15,y
    rts
ScriptOp85:
    lda $80,x                    ; CONTROL_SCRIPT_OP85
    tay
    lda $70,x
    tax
    lda $61
    jsr DivideUnsigned16By8
    txa
    ldx $10
    jsr ScriptStoreSlotLowAndClearHigh
    rts

; Opcodes $86/$87 use a selector helper. If it cannot select a nonnegative
; index, it discards its caller's return address and returns to the dispatcher.
ScriptOp86:
    jsr ScriptGetSelectedIndex   ; CONTROL_SCRIPT_OP86
    lda $0520,y
    jmp ScriptStoreSlotLowAndClearHigh
ScriptGetSelectedIndex:
    jsr SelectScriptField
    bne ScriptGetSelectedAbort
    lda $3C,y
    tay
    bpl ScriptGetSelectedReturn
ScriptGetSelectedAbort:
    pla
    pla
ScriptGetSelectedReturn:
    rts
ScriptOp87:
    jsr ScriptGetSelectedIndex   ; CONTROL_SCRIPT_OP87
    lda $70,x
    sta $0520,y
    rts
ScriptOp88:
    jsr ScriptOperand61OrSlot    ; CONTROL_SCRIPT_OP88
    sta $05D0,x
    rts
.assert (* - BankStart) = $6452, error, "bank 0 script handlers through opcode $88"

; Opcode $89 reads a seven-byte indexed record and uses its fields to update
; several state and coordinate values. The roles of the values remain inferred.
ScriptOp89:
    jsr ScriptSaveSlotPointer    ; CONTROL_SCRIPT_OP89_FETCH
    ldy #$07
    lda $61
    sta $53
    lda $62
    sta $54
ScriptOp89IndexLoop:
    lda $70,x
    clc
    adc $53
    sta $53
    lda $54
    adc #$00
    sta $54
    dey
    bne ScriptOp89IndexLoop
    ldx #$07
    jsr FetchVariableRecord
    ldx $10
    jsr ScriptLoadSlotPointer
    lda $60
    cmp #$FF
    bne ScriptOp89CheckBounds
ScriptOp89TestRelative:
    jmp ScriptOp89Relative
ScriptOp89CheckBounds:
    lda $64
    cmp #$FF
    bne ScriptOp89Setup
    lda $63
    cmp #$FF
    bne ScriptOp89Setup
    cmp $01
    beq ScriptOp89TestRelative
ScriptOp89Setup:
    lda #$FF                     ; CONTROL_SCRIPT_OP89_SETUP
    sta $0A
    lda $01
    sta $00
    sta $58
    lda #$FF
    sta $03C9
    lda $60
    cmp #$FF
    beq ScriptOp89SetPosition
    sta $00
    cmp $01
    beq ScriptOp89SetPosition
    lda #$00
    sta $03C9
ScriptOp89SetPosition:
    lda $63
    sta $0B
    lda $64
    sta $0C
    cmp #$FF
    bne ScriptOp89SetVertical
    lda $63
    cmp #$FF
    bne ScriptOp89SetVertical
    lda $65
    sec
    sbc #$10
    sta $0B
    lda $66
    sbc #$00
    sta $0C
    bcs ScriptOp89SetVertical
    lda #$00
    sta $0B
    sta $0C
ScriptOp89SetVertical:
    lda $62                      ; CONTROL_SCRIPT_OP89_POSITION
    sta $1C
    cmp #$FF
    bne ScriptOp89Convert
    lda $61
    sec
    sbc #$10
    sta $1C
    bcs ScriptOp89VerticalReady
    lda #$00
    sta $1C
ScriptOp89VerticalReady:
    lda $1C
    sta $62
ScriptOp89Convert:
    lda #$00
    jsr ScriptOp89ShiftVertical
    jsr ScriptOp89ShiftVertical
    jsr ScriptOp89ShiftVertical
    sta $1D
    lda $61
    sec
    sbc $62
    jsr ShiftALeft3
    sta $0590,x
    lda $65
    sec
    sbc $0B
    and #$1F
    jsr ShiftALeft3
    sta $0580,x
    jsr UpdateSlotBounds
    jsr ScriptOp89ShiftHorizontal
    jsr ScriptOp89ShiftHorizontal
    jsr ScriptOp89ShiftHorizontal
    jmp ScriptYield
ScriptOp89RetrySetup:
    jmp ScriptOp89Setup          ; CONTROL_SCRIPT_OP89_SHIFTS
ScriptOp89ShiftVertical:
    asl $1C
    rol a
    rts
ScriptOp89ShiftHorizontal:
    asl $0B
    rol $0C
    rts
ScriptOp89Relative:
    lda $65                      ; CONTROL_SCRIPT_OP89_RELATIVE
    sec
    sbc $0E
    sta $11
    lda $66
    sbc $0F
    bcc ScriptOp89RetrySetup
    bne ScriptOp89RetrySetup
    lda $11
    cmp #$1F
    bcs ScriptOp89RetrySetup
    cmp #$01
    bcc ScriptOp89RetrySetup
    lda $61
    sec
    sbc $4F
    cmp #$18
    bcs ScriptOp89RetrySetup
    cmp #$05
    bcc ScriptOp89RetrySetup
    lda $61
    sec
    sbc $62
    jsr ShiftALeft3
    tay
    sta $0590,x
    lda $65
    sec
    sbc $0E
    and #$1F
    jsr ShiftALeft3
    sta $11
    lda $03EE
    and #$07
    clc
    adc $11
    sta $0580,x
    jsr UpdateSlotBounds
    jmp ScriptYield
.assert (* - BankStart) = $6581, error, "bank 0 script handler opcode $89"

; Opcode $8A clears a 32-byte stack-page buffer when $61 is $FF; otherwise it
; clears a selected bit using the same mask helper as opcode $1E.
ScriptOp8A:
    lda $61                      ; CONTROL_SCRIPT_OP8A
    cmp #$FF
    bne ScriptOp8AClearBit
    lda #$00
    tax
    ldy #$20
ScriptOp8AClearLoop:
    sta $0100,x
    inx
    dey
    bne ScriptOp8AClearLoop
ScriptOp8AReturn:
    rts
ScriptOp8AClearBit:
    jsr ScriptSlotBitMask
    ldx $10
    sta $11
    ora $0100,y
    eor $11
    sta $0100,y
    rts
ScriptOp8B:
    lda $58                      ; CONTROL_SCRIPT_OP8B
    pha
    lda #$00
    sta $58
    pla
    bne ScriptOp8AReturn
    jmp ScriptSetPointerFromOperands

; $8C resets the scan position; $B0 enters immediately after the reset.
; Both scan slots for $06D0,y equal to the current slot, skipping invalid slots.
ScriptOp8C:
    lda #$00                     ; CONTROL_SCRIPT_OP8C
    sta $03C8
ScriptOpB0:
    jsr ScriptSetSlotFFFF        ; CONTROL_SCRIPT_OPB0
    ldy $03C8
ScriptOp8CScan:
    cpy #$10
    beq ScriptOp8CEnd
    jsr ScriptCheckOtherSlot
    beq ScriptOp8CNext
    lda $06D0,y
    cmp $10
    bne ScriptOp8CNext
    sty $03C8
    inc $03C8
    lda $04E0,y
    jmp ScriptStoreSlotLowAndClearHigh
ScriptOp8CNext:
    iny
    jmp ScriptOp8CScan
ScriptOp8CEnd:
    sty $03C8
    rts
ScriptOp8DTo8F:
    lda $70,x                    ; CONTROL_SCRIPT_OP8D
    pha
    lda $80,x
    sta $70,x
    pla
    sta $80,x
    rts

; $90 reads and $91 writes the byte at the address in operands $61/$62.
ScriptOp90:
    jsr ScriptSetIndirectOperand ; CONTROL_SCRIPT_OP90
    lda ($FE),y
    jmp ScriptStoreSlotLowAndClearHigh
ScriptOp91:
    jsr ScriptSetIndirectOperand ; CONTROL_SCRIPT_OP91
    lda $70,x
    sta ($FE),y
    rts
ScriptSetIndirectOperand:
    lda $61                      ; CONTROL_SCRIPT_INDIRECT_OPERAND
    sta $FE
    lda $62
    sta $FF
    ldy #$00
ScriptIndirectReturn:
    rts
ScriptOp92:
    jsr SelectSlotFlagsOrAbort                    ; CONTROL_SCRIPT_OP92
    lda $63
    and $038D,y
    bne ScriptIndirectReturn
    jmp ScriptSetPointerFromOperands
ScriptOp93:
    lda $63
    cmp $0360,x                  ; CONTROL_SCRIPT_OP93
    bcs ScriptIndirectReturn
    jmp ScriptSetPointerFromOperands
ScriptOp94:
    lda $0700,x                  ; CONTROL_SCRIPT_OP94
    bpl ScriptOp94Compare
    jsr NegateA
ScriptOp94Compare:
    cmp $63
    bcs ScriptIndirectReturn
    jmp ScriptSetPointerFromOperands

; $95 reads successive four-byte records and compares the final pair to the
; slot value, advancing the script pointer four bytes per record.
ScriptOp95:
    ldx #$04                     ; CONTROL_SCRIPT_OP95
    jsr FetchVariableRecord
    ldx $10
    jsr AdvanceScriptPointerTwice
    lda $60
    ora $61
    beq ScriptIndirectReturn
    jsr AdvanceScriptPointerTwice
    lda $62
    cmp $70,x
    bne ScriptOp95
    lda $63
    cmp $80,x
    bne ScriptOp95
    lda $61
    sta $62
    lda $60
    sta $61
    jmp ScriptSetPointerFromOperands
ScriptOp96:
    lda $61                      ; CONTROL_SCRIPT_OP96
    ldy $0700,x
    bpl ScriptOp96FirstReady
    jsr NegateA
ScriptOp96FirstReady:
    sta $61
    lda $62
    ldy $B0,x
    bpl ScriptOp96SecondReady
    jsr NegateA
ScriptOp96SecondReady:
    sta $62
    jsr UpdateSlotFieldsMode40
    jmp ScriptYieldIfNonnegative
ScriptOp97:
    jsr ScriptSelectValueArray   ; CONTROL_SCRIPT_OP97
    beq ScriptOp97Pair
    lda $70,x
    and $0140,y
    sta $70,x
    lda $80,x
    and $0141,y
    sta $80,x
    rts
ScriptOp97Pair:
    lda $70,x
    and $0120,y
    sta $70,x
    lda $80,x
    and $0121,y
    sta $80,x
    rts
.assert (* - BankStart) = $6696, error, "bank 0 script handlers through opcode $97"

; $98 saves state fields and calls $890A for all sixteen slots; $99 reloads
; operand fields from $49-$4C and passes the result to the shared state setter.
ScriptOp98:
    lda $01                      ; CONTROL_SCRIPT_OP98
    sta $27
    lda $03EE
    sta $0B
    lda $03EF
    sta $0C
    lda $03F0
    sta $1C
    lda $03F1
    sta $1D
    lda $3C
    sta $5B
    lda $3D
    sta $5C
    lda $15
    sta $4D
    lda $16
    sta $4E
    lda $61
    sta $00
    lda #$0F
    sta $11
    lda #$F8
    sec
    sbc $03EC
    sta $12
ScriptOp98SlotLoop:
    ldx $11
    lda $0630,x
    ora #$20
    sta $0630,x
    lda $11
    ldy $12
    jsr PlaceSlotSprites
    dec $11
    bpl ScriptOp98SlotLoop
    jmp ScriptYield
ScriptOp99:
    lda #$FF                     ; CONTROL_SCRIPT_OP99
    sta $0A
    lda $49
    sta $61
    lda $4A
    sta $62
    lda $4B
    sta $63
    lda $4C
    sta $64
    jsr ConfigureSplitScreen
    lda $27
    bne ScriptOp99Set
    lda #$FF
ScriptOp99Set:
    jmp ScriptSetMainState
ScriptOp9A:
    jsr ScriptCompareState27     ; CONTROL_SCRIPT_OP9A
    beq ScriptCompareStateReturn
    jmp ScriptSetPointerFromOperands
ScriptReadState27:
    jsr ScriptCompareState27
    beq ScriptReadStateReturn
    lda $0A
ScriptReadStateReturn:
    rts
ScriptCompareState27:
    lda $27
    cmp #$FF
ScriptCompareStateReturn:
    rts
ScriptOp9B:
    jmp CallScriptNativeBanked   ; CONTROL_SCRIPT_OP9B
ScriptOp9C:
    lda $61
    eor #$FF                     ; CONTROL_SCRIPT_OP9C
    sta $03ED
    rts
ScriptOp9D:
    rts                          ; CONTROL_SCRIPT_OP9D

; $9E-$A0 compare the command's operand pair with calculated offsets. The
; horizontal and vertical position conventions are provisional.
ScriptOp9E:
    lda $0700,x                  ; CONTROL_SCRIPT_OP9E
    clc
    adc $03EE
    sta $11
    lda $03EF
    adc #$00
    sta $12
ScriptCompareOffset:
    lda $63
    sec
    sbc $11
    lda $64
    sbc $12
    bcc ScriptOp9D
    jmp ScriptSetPointerFromOperands
ScriptOp9F:
    jsr ScriptGetSecondOffset   ; CONTROL_SCRIPT_OP9F
    jmp ScriptCompareOffset
ScriptGetSecondOffset:
    lda $B0,x
    clc
    adc $03F0
    sta $11
    lda $03F1
    adc #$00
    sta $12
    rts
ScriptOpA0:
    jsr ScriptGetSecondOffset   ; CONTROL_SCRIPT_OPA0
    lda #$00
    sta $03
    lda $0396
    jsr ScriptShiftAInto03
    jsr ScriptShiftAInto03
    jsr ScriptShiftAInto03
    sec
    sbc $11
    sta $11
    lda $03
    sbc $12
    sta $12
    jmp ScriptCompareOffset
ScriptShiftAInto03:
    asl a
    rol $03
    rts
ScriptOpA1:
    jsr ScriptSelectValueArray  ; CONTROL_SCRIPT_OPA1
    lda $0140,y
    sta $70,x
    rts
ScriptOpA2:
    ldy $06D0,x                 ; CONTROL_SCRIPT_OPA2
    lda $0500,y
    sta $0500,x
    lda $0510,y
    sta $0510,x
    rts
; $A3 shares the previously reconstructed $01 handler.
ScriptOpA4:
    lda $0630,x
    and #$FB                    ; CONTROL_SCRIPT_OPA4
    ldy $61
    cpy #$FF
    beq ScriptOpA4Store
    ora #$04
ScriptOpA4Store:
    sta $0630,x
    rts
ScriptOpA5:
    lda $0580,x                 ; CONTROL_SCRIPT_OPA5
    clc
    adc $70,x
    sta $03A6
    lda $0590,x
    clc
    adc $80,x
    sta $03A7
    jsr ReadMapByteAtPosition
    ldx $10
    jmp ScriptStoreSlotLowAndClearHigh
ScriptOpA6:
    lda $62                     ; CONTROL_SCRIPT_OPA6
    sta $64
    lda $70,x
    sta $62
    lda $80,x
    sta $63
    jmp ScriptOp1F
.assert (* - BankStart) = $67D3, error, "bank 0 script handlers through opcode $A6"

; $A7 scans other slots against bounds derived from $0580/$0590 and the
; current slot's value, returning a slot field or $FFFF when none qualifies.
ScriptOpA7:
    lda $0580,x                 ; CONTROL_SCRIPT_OPA7
    clc
    adc $70,x
    sta $61
    lda $0590,x
    clc
    adc $80,x
    sta $62
    ldy #$00
ScriptOpA7Scan:
    jsr ScriptCheckOtherSlot
    beq ScriptOpA7Next
    lda $0590,y
    sec
    sbc #$08
    bcs ScriptOpA7FirstLow
    lda #$00
ScriptOpA7FirstLow:
    cmp $62
    bcs ScriptOpA7Next
    lda $B0,y
    clc
    adc #$08
    bcc ScriptOpA7FirstHigh
    lda #$FF
ScriptOpA7FirstHigh:
    cmp $62
    bcc ScriptOpA7Next
    lda $0580,y
    sec
    sbc #$08
    bcs ScriptOpA7SecondLow
    lda #$00
ScriptOpA7SecondLow:
    cmp $61
    bcs ScriptOpA7Next
    lda $0580,y
    clc
    adc $0570,y
    bcc ScriptOpA7SecondExtent
    lda #$FF
ScriptOpA7SecondExtent:
    clc
    adc #$08
    bcc ScriptOpA7SecondHigh
    lda #$FF
ScriptOpA7SecondHigh:
    cmp $61
    bcc ScriptOpA7Next
    lda $04E0,y
    jmp ScriptStoreSlotLowAndClearHigh
ScriptOpA7Next:
    iny
    cpy #$10
    bne ScriptOpA7Scan
ScriptSetSlotFFFF:
    lda #$FF                    ; CONTROL_SCRIPT_SLOT_FFFF
    sta $70,x
    sta $80,x
    rts
ScriptOpA8:
    lda $70,x                   ; CONTROL_SCRIPT_OPA8
    clc
    adc $03EE
    and #$07
    jsr NegateA
    clc
    adc $70,x
    sta $70,x
    lda $80,x
    clc
    adc $03F0
    and #$07
    jsr NegateA
    clc
    adc $80,x
    sta $80,x
    rts
ScriptOpA9:
    lda $61                     ; CONTROL_SCRIPT_OPA9
    bne ScriptOpA9Adjust
    lda $62
    bne ScriptOpA9Adjust
    lda $70,x
    sta $61
    lda $80,x
    sta $62
ScriptOpA9Adjust:
    lda $0580,x
    clc
    adc $61
    sta $0580,x
    lda $0590,x
    clc
    adc $62
    sta $0590,x
    jmp UpdateSlotBounds
ScriptOpAA:
    jsr ScriptOperand61OrSlot   ; CONTROL_SCRIPT_OPAA
    ora #$00
    bpl ScriptOpAANonnegative
    jmp ConfigureBanksFromState
ScriptOpAANonnegative:
    jmp ConfigureBanksFromValue

; $AB and $BF share this busy-state handler and write their command byte to
; $04D9 when the state is available.
ScriptOpABOrBF:
    ldy $60                     ; CONTROL_SCRIPT_OPAB
    lda $E7
    beq ScriptOpABSetup
    jmp ScriptWaitForState
ScriptOpABSetup:
    lda $61
    sta $EA
    lda $62
    sta $EB
    bne ScriptOpABStore
    lda $61
    bne ScriptOpABStore
    lda $70,x
    sta $EA
    lda $80,x
    sta $EB
ScriptOpABStore:
    sty $04D9
    lda #$1C
    sta $E7
    rts
ScriptOpAC:
    ldy $80,x                   ; CONTROL_SCRIPT_OPAC
    lda $0140,y
    sta $70,x
    rts
ScriptOpAD:
    ldy $80,x                   ; CONTROL_SCRIPT_OPAD
    lda $70,x
    sta $0140,y
    rts
ScriptOpAE:
    lda $61                     ; CONTROL_SCRIPT_OPAE
    sta $03
    lda $62
    sta $04
    lda $63
    sta $06
    jsr ScriptDefaultSearchFields
    jsr ScriptFindSlot
    bne ScriptOpAEReturn
    lda $0630,y
    and #$DF
    sta $0630,y
ScriptOpAEReturn:
    rts
.assert (* - BankStart) = $68E3, error, "bank 0 script handlers through opcode $AE"

; Opcode $AF selects a value or pointer from three tables using $27 and the
; selector in $61. Table contents and their higher-level meaning are unresolved.
ScriptOpAF:
    jsr ScriptClearSlotHigh       ; CONTROL_SCRIPT_OPAF
    lda $27
    ldy $61
    cpy #$0F
    beq ScriptOpAFStore
    tay
    asl a
    sta $03
    lda $A37E,y
    ldy $61
    cpy #$AA
    beq ScriptOpAFStore
    ldy $03
    lda $A395,y
    sta $80,x
    lda $A394,y
    ldy $61
    cpy #$4D
    beq ScriptOpAFStore
    ldy $03
    lda $A3C1,y
    sta $80,x
    lda $A3C0,y
ScriptOpAFStore:
    sta $70,x
    rts

; $B0 shares the earlier $8C scan. $B1 iterates four-byte records until a
; zero terminator; after a first match it preserves the matched replacement.
ScriptOpB1:
    lda #$00                      ; CONTROL_SCRIPT_OPB1
    sta $03
ScriptOpB1Loop:
    ldx #$04
    jsr FetchVariableRecord
    ldx $10
    jsr AdvanceScriptPointerTwice
    lda $60
    ora $61
    beq ScriptOpB1End
    jsr AdvanceScriptPointerTwice
    lda $03
    bne ScriptOpB1Loop
    lda $60
    cmp $70,x
    bne ScriptOpB1Loop
    lda $61
    cmp $80,x
    bne ScriptOpB1Loop
    lda $62
    sta $70,x
    lda $63
    sta $80,x
    lda #$FF
    sta $03
    jmp ScriptOpB1Loop
ScriptOpB1End:
    lda $03
    bne ScriptOpB1Return
    jsr ScriptSetSlotFFFF
ScriptOpB1Return:
    rts
ScriptOpB2:
    lda $05E0,x
    and #$BF                      ; CONTROL_SCRIPT_OPB2
    ldy $61
    cpy #$FF
    beq ScriptOpB2Store
    ora #$40
ScriptOpB2Store:
    sta $05E0,x
    rts

; $B3 fetches a pair from an indexed address, restores the script pointer,
; and enters the previously reconstructed shared $50 sequence.
ScriptOpB3:
    jsr ScriptSaveSlotPointer     ; CONTROL_SCRIPT_OPB3
    lda $70,x
    sta $53
    lda $80,x
    sta $54
    asl $53
    rol $54
    lda $61
    clc
    adc $53
    sta $53
    lda $62
    adc $54
    sta $54
    ldx #$02
    jsr FetchVariableRecord
    ldx $10
    lda $61
    sta $62
    lda $60
    sta $61
    jsr ScriptLoadSlotPointer
    jmp ScriptOp50
ScriptOpB4ToB5:
    jsr CalculateSlotCoordinate                     ; CONTROL_SCRIPT_OPB4
    lda $11
    jmp ScriptStoreSlotLowAndClearHigh

; $B6 finds a slot and repeatedly follows other slots whose $06D0 points to
; the selected one. No cycle check is visible, so the original loop is kept.
ScriptOpB6:
    jsr ScriptOp67FindAndSet      ; CONTROL_SCRIPT_OPB6
    lda $06D0,x
    bmi ScriptOpB6Yield
ScriptOpB6Follow:
    sta $11
    ldy #$00
ScriptOpB6Scan:
    jsr ScriptCheckOtherSlot
    beq ScriptOpB6Next
    lda $06D0,y
    cmp $11
    bne ScriptOpB6Next
    tya
    sta $06D0,x
    jmp ScriptOpB6Follow
ScriptOpB6Next:
    iny
    cpy #$10
    bne ScriptOpB6Scan
ScriptOpB6Yield:
    jmp ScriptYield
ScriptOpB7:
    lda $06D0,x                   ; CONTROL_SCRIPT_OPB7
    sta $11
    jsr ScriptOp68
    ldy #$00
ScriptOpB7Scan:
    jsr ScriptCheckOtherSlot
    beq ScriptOpB7Next
    lda $06D0,y
    cmp $10
    bne ScriptOpB7Next
    lda $11
    sta $06D0,y
    sty $11
    rts
ScriptOpB7Next:
    iny
    cpy #$10
    bne ScriptOpB7Scan
    rts
ScriptOpB8:
    lda $0710,x                   ; CONTROL_SCRIPT_OPB8
    pha
    lda $0720,x
    pha
    jsr ScriptOpB7
    pla
    sta $0720,x
    pla
    sta $0710,x
ScriptOpB8Restart:
    ldy #$00
ScriptOpB8Scan:
    jsr ScriptCheckOtherSlot
    beq ScriptOpB8Next
    lda $06D0,y
    cmp $11
    bne ScriptOpB8Next
    sty $11
    jmp ScriptOpB8Restart
ScriptOpB8Next:
    iny
    cpy #$10
    bne ScriptOpB8Scan
    lda $11
    sta $06D0,x
    rts
ScriptOpB9:
    lda $61                       ; CONTROL_SCRIPT_OPB9
    ora $0640,x
    eor $61
    sta $0640,x
    lda $62
    ora $0650,x
    eor $62
    sta $0650,x
    rts
ScriptOpBA:
    lda $61                       ; CONTROL_SCRIPT_OPBA
    ora $0640,x
    sta $0640,x
    lda $62
    ora $0650,x
    sta $0650,x
    rts
ScriptOpBB:
    lda $0620,x
    and #$10                      ; CONTROL_SCRIPT_OPBB
    bne ScriptOpBBReturn
    jmp ScriptSetPointerFromOperands
ScriptOpBBReturn:
    rts

; $BC/$BD follow a chain of $06D0 references to a requested depth. $BC calls
; $D4DA with a temporary value, while $BD clears a bit in the found slot.
ScriptOpBC:
    lda $62                       ; CONTROL_SCRIPT_OPBC
    jsr ScriptFindRelatedDepth
    beq ScriptOpBCReturn
    lda $06B0,x
    pha
    lda $61
    sta $06B0,x
    jsr ScriptMarkOtherSlot
    pla
    sta $06B0,x
ScriptOpBCReturn:
    rts
ScriptFindRelatedDepth:
    sta $11                       ; CONTROL_SCRIPT_RELATED_DEPTH
    stx $12
ScriptFindDepthRestart:
    ldy #$00
ScriptFindDepthScan:
    jsr ScriptCheckOtherSlot
    beq ScriptFindDepthNext
    lda $06D0,y
    cmp $12
    bne ScriptFindDepthNext
    sty $12
    dec $11
    bne ScriptFindDepthRestart
    lda #$FF
    rts
ScriptFindDepthNext:
    iny
    cpy #$10
    bne ScriptFindDepthScan
    rts
ScriptOpBD:
    lda $61                       ; CONTROL_SCRIPT_OPBD
    jsr ScriptFindRelatedDepth
    beq ScriptOpBDReturn
    lda $0630,y
    and #$DF
    sta $0630,y
ScriptOpBDReturn:
    rts
ScriptOpBE:
    lda $0630,x
    ora #$20                      ; CONTROL_SCRIPT_OPBE
    sta $0630,x
    rts
; $BF shares the previously reconstructed $AB handler.
ScriptOpC0:
    lda $61
    ora $70,x                     ; CONTROL_SCRIPT_OPC0
    sta $70,x
    lda $62
    ora $80,x
    sta $80,x
    rts
ScriptOpC1:
    jsr ScriptSelectValueArray    ; CONTROL_SCRIPT_OPC1
    beq ScriptOpC1Pair
    lda $70,x
    ora $0140,y
    sta $70,x
    rts
ScriptOpC1Pair:
    lda $70,x
    ora $0120,y
    sta $70,x
    lda $80,x
    ora $0121,y
    sta $80,x
    rts
ScriptOpC2:
    lda $0630,x
    and #$02                      ; CONTROL_SCRIPT_OPC2
    beq ScriptOpC2Return
    jmp ScriptSetPointerFromOperands
ScriptOpC2Return:
    rts
ScriptOpC3:
    jsr RefreshSlotRecordPosition                     ; CONTROL_SCRIPT_OPC3
    rts
ScriptOpC4:
    lda $10                       ; CONTROL_SCRIPT_OPC4
    jsr ReleaseSpriteRecord
    ldx $10
    jsr ScriptOperand61OrSlot
    sta $04DC
    lda $10
    jsr StoreSlotRecordField0A
    lda #$00
    sta $61
    lda #$01
    sta $62
    ldx $10
    jmp ScriptOp63
.assert (* - BankStart) = $6AF6, error, "bank 0 script handlers through opcode $C4"

; Configure the split-screen state from script operands $61-$64. The saved
; operands are updated only when the main state is $FF.
ConfigureSplitScreen:
    jsr ScriptCompareState27     ; CONTROL_CONFIGURE_SPLIT_SCREEN
    bne SplitScreenSetBounds
    lda $61
    sta $49
    lda $62
    sta $4A
    lda $63
    sta $4B
    lda $64
    sta $4C
SplitScreenSetBounds:
    lda #$F8                     ; CONTROL_SPLIT_SCREEN_SET_BOUNDS
    sta $03B9
    lda $61
    sta $03B8
    beq SplitScreenSetControl
    lda #$F0
    sec
    sbc $61
    sta $03B8
    lda $62
    sec
    sbc #$09
    sta $03B9
; Set the control fields and derive mapper selection from the packed operand.
SplitScreenSetControl:
    lda $63                      ; CONTROL_SPLIT_SCREEN_SET_CONTROL
    sta $03BA
    lda $64
    and #$01
    jsr ShiftALeft4
    ora #$08
    sta $03BB
    lda $64
    rol a
    rol a
    rol a
    and #$F0
    jsr ComputeBankSelection
    sta $03BE
    stx $03BF
    lda $62
    clc                          ; Original SBC intentionally includes borrow.
    sbc $63
    sta $03EC
    jsr InitializeSplitSprite
; Compute the attribute base by subtracting four times the rounded-up $61.
    lda #$27                     ; CONTROL_SPLIT_SCREEN_ATTRIBUTE_BASE
    sta $04DA
    lda #$C0
    sta $04DB
    lda $61
    clc
    adc #$07
    and #$F8
    asl a
    asl a
    sta $62
    lda $04DB
    sec
    sbc $62
    sta $04DB
    lda $04DA
    sbc #$00
    sta $04DA
    rts
.assert (* - BankStart) = $6B7A, error, "bank 0 split-screen configuration end"
; Convert a packed state byte into the mapper selection value in A and the
; associated index in X. The incoming value is retained in Y during shifting.
ComputeBankSelection:
    tay                           ; CONTROL_COMPUTE_BANK_SELECTION
    and #$01
    sta $11
    tya
    jsr ShiftARight3
    ora $11
    tax
    tya
    ora #$0C
    tay
    rts
.assert (* - BankStart) = $6B8B, error, "bank 0 bank selection helper end"


; Select one of two indexed fields from $61, or use the current/related
; slot's $0630 flags. A nonzero result indicates an unavailable selection.
SelectScriptField:
    lda $61                       ; CONTROL_SELECT_SCRIPT_FIELD
    cmp #$02
    bcc ScriptFieldSelected
    bne ScriptFieldRelatedSlot
    lda $0630,x
    bpl ScriptFieldMask
ScriptFieldReturn:
    rts
ScriptFieldRelatedSlot:
    lda $0540,x
    cmp #$FF
    beq ScriptFieldReturn
    tay
    lda $0630,y
    bmi ScriptFieldReturn
ScriptFieldMask:
    and #$01
ScriptFieldSelected:
    tay
    lda #$00
    rts

; On $0630,x & $81 >= $80 this deliberately discards the caller's return
; address. Otherwise it returns normally, preserving the incoming A value.
SelectSlotFlagsOrAbort:
    pha                           ; CONTROL_SELECT_FLAGS_ABORT
    lda $0630,x
    and #$81
    tay
    pla
    cpy #$80
    bcc SelectSlotFlagsReturn
    pla
    pla
SelectSlotFlagsReturn:
    rts
.assert (* - BankStart) = $6BBB, error, "bank 0 script selector helpers end"

; After script processing, skip slots when the global state is active or their
; $04E0 entry is $FF. Unattached slots apply two signed field adjustments;
; attached slots go directly to the shared update at $EC51.
UpdateSlotAfterScript:
    lda $00                       ; CONTROL_SLOT_UPDATE_ENTRY
    bne SelectSlotFlagsReturn
    lda $04E0,x
    cmp #$FF
    bne SlotUpdateCheckLink
    rts
SlotUpdateCheckLink:
    lda $06D0,x
    bmi SlotUpdateFirstDamping
    jmp SlotUpdateApplyLimits
SlotUpdateFirstDamping:
    lda #$FF                      ; CONTROL_SLOT_UPDATE_FIRST
    sta $03
    lda $05D0,x
    and #$01
    bne SlotUpdateFirstCounter
    lda $0620,x
    and #$10
    bne SlotUpdateFirstCounter
    lda #$00
    sta $03
SlotUpdateFirstCounter:
    lda $0750,x
    and #$0F
    beq SlotUpdateFirstAdjust
    dec $0750,x
    jmp SlotUpdateSecondCounter
SlotUpdateFirstAdjust:
    lda $03
    beq SlotUpdateSecondCounter
    lda $0500,x
    beq SlotUpdateSecondCounter
    bmi SlotUpdateFirstNegative
    sec
    sbc $0710,x
    beq SlotUpdateFirstPositiveFloor
    bpl SlotUpdateFirstStore
SlotUpdateFirstPositiveFloor:
    lda #$01
SlotUpdateFirstStore:
    sta $0500,x
    jmp SlotUpdateSecondCounter
SlotUpdateFirstNegative:
    clc
    adc $0710,x
    bmi SlotUpdateFirstNegativeStore
    lda #$FF
SlotUpdateFirstNegativeStore:
    sta $0500,x
SlotUpdateSecondCounter:
    lda $0750,x                   ; CONTROL_SLOT_UPDATE_SECOND
    and #$F0
    beq SlotUpdateSecondAdjust
    lda $0750,x
    sec
    sbc #$10
    sta $0750,x
    jmp SlotUpdateApplyLimits
SlotUpdateSecondAdjust:
    lda $03
    beq SlotUpdateApplyLimits
    lda $0510,x
    beq SlotUpdateApplyLimits
    bmi SlotUpdateSecondNegative
    sec
    sbc $0720,x
    beq SlotUpdateSecondPositiveFloor
    bpl SlotUpdateSecondStore
SlotUpdateSecondPositiveFloor:
    lda #$01
SlotUpdateSecondStore:
    sta $0510,x
    jmp SlotUpdateApplyLimits
SlotUpdateSecondNegative:
    clc
    adc $0720,x
    bmi SlotUpdateSecondNegativeStore
    lda #$FF
SlotUpdateSecondNegativeStore:
    sta $0510,x

; Add $C0 to the second field only if signed overflow is clear. Then clamp
; both signed fields to the magnitudes in $05F0/$0600, preserving signs.
SlotUpdateApplyLimits:
    lda $C0,x                     ; CONTROL_SLOT_UPDATE_LIMITS
    clc
    adc $0510,x
    bvs SlotUpdateLimitFirst
    sta $0510,x
SlotUpdateLimitFirst:
    ldy #$00
    lda $0500,x
    bpl SlotUpdateFirstMagnitude
    jsr NegateA
    ldy #$01
SlotUpdateFirstMagnitude:
    cmp $05F0,x
    bcc SlotUpdateFirstSign
    lda $05F0,x
SlotUpdateFirstSign:
    cpy #$00
    beq SlotUpdateFirstLimited
    jsr NegateA
SlotUpdateFirstLimited:
    sta $0500,x
    ldy #$00
    lda $0510,x
    bpl SlotUpdateSecondMagnitude
    jsr NegateA
    ldy #$01
SlotUpdateSecondMagnitude:
    cmp $0600,x
    bcc SlotUpdateSecondSign
    lda $0600,x
SlotUpdateSecondSign:
    cpy #$00
    beq SlotUpdateSecondLimited
    jsr NegateA
SlotUpdateSecondLimited:
    sta $0510,x
    lda $06D0,x
    bmi SlotUpdateUnlinked
    jsr UpdateLinkedSlotPosition
    jmp TrackSlotPositionChanges
.assert (* - BankStart) = $6CA3, error, "bank 0 slot update prefix end"

; For an unlinked slot, derive a signed step from $0510, in eighths, and
; constrain it against the vertical bounds selected by $05D0 bits $08/$20.
SlotUpdateUnlinked:
    lda $0510,x                   ; CONTROL_UNLINKED_VERTICAL
    bpl UnlinkedVerticalMagnitude
    jsr NegateA
UnlinkedVerticalMagnitude:
    jsr ShiftARight3
    sta $03
    ldy $0510,x
    bpl UnlinkedVerticalSigned
    jsr NegateA
UnlinkedVerticalSigned:
    sta $04
    lda $05D0,x
    and #$28
    beq UnlinkedSplitVertical
    lda $04
    bpl UnlinkedVerticalPositive
    lda $0590,x
    sta $11
    lda $05D0,x
    and #$20
    bne UnlinkedVerticalNegativeLimit
    lda $B0,x
    sta $11
UnlinkedVerticalNegativeLimit:
    lda $03
    cmp $11
    bcc UnlinkedSplitVertical
    lda $11
    sta $03
    jsr NegateA
    jmp UnlinkedVerticalStoreSigned
UnlinkedVerticalPositive:
    lda $05D0,x
    and #$08
    bne UnlinkedVerticalBottom
    lda $04
    clc
    adc $0590,x
    bcs UnlinkedVerticalClampTop
    cmp #$EF
    bcc UnlinkedSplitVertical
UnlinkedVerticalClampTop:
    lda #$EF
    sec
    sbc $0590,x
    jmp UnlinkedVerticalClampStore
UnlinkedVerticalBottom:
    lda $04
    clc
    adc $B0,x
    bcs UnlinkedVerticalClampBottom
    cmp #$EF
    bcc UnlinkedSplitVertical
UnlinkedVerticalClampBottom:
    lda #$EF
    sec
    sbc $B0,x
UnlinkedVerticalClampStore:
    sta $03
UnlinkedVerticalStoreSigned:
    sta $04

; Split each component into an initial step of at most eight and a remainder.
; Negative components retain their sign using the original two's complement.
UnlinkedSplitVertical:
    lda $04                       ; CONTROL_UNLINKED_SPLIT_VERTICAL
    sta $06
    lda #$00
    sta $04
    lda $03
    sec
    sbc #$08
    bcc UnlinkedSplitHorizontal
    beq UnlinkedSplitHorizontal
    sta $04
    lda #$08
    sta $06
    lda $0510,x
    bpl UnlinkedSplitHorizontal
    lda $04
    jsr NegateA
    sta $04
    lda $06
    jsr NegateA
    sta $06
UnlinkedSplitHorizontal:
    lda #$00
    sta $03
    lda $0500,x
    bpl UnlinkedHorizontalPositive
    jsr NegateA
    jsr ShiftARight3
    ldx #$FF
    jmp UnlinkedHorizontalSplit
UnlinkedHorizontalPositive:
    jsr ShiftARight3
    sta $05
    lda $05D0,x
    and #$10
    beq UnlinkedHorizontalUseMagnitude
    lda $0580,x
    bpl UnlinkedHorizontalUseMagnitude
    jsr NegateA
    sec
    sbc $0570,x
    bcs UnlinkedHorizontalCompare
    lda #$00
    sta $05
UnlinkedHorizontalCompare:
    cmp $05
    bcs UnlinkedHorizontalUseMagnitude
    sta $05
UnlinkedHorizontalUseMagnitude:
    ldx #$00
    lda $05
UnlinkedHorizontalSplit:
    sta $05
    sec
    sbc #$08
    bcc UnlinkedHorizontalSign
    beq UnlinkedHorizontalSign
    sta $03
    lda #$08
    sta $05
UnlinkedHorizontalSign:
    cpx #$00
    beq UnlinkedMoveSetup
    lda $03
    jsr NegateA
    sta $03
    lda $05
    jsr NegateA
    sta $05

; Try the combined step. If it succeeds, flag moved axes and continue with
; the remainders. A failed step enters separate horizontal and vertical probes.
UnlinkedMoveSetup:
    ldx $10                       ; CONTROL_UNLINKED_MOVE_SETUP
    lda $0620,x
    ldy $06
    bne UnlinkedKeepVerticalFlag
    and #$FE
UnlinkedKeepVerticalFlag:
    ldy $05
    bne UnlinkedKeepHorizontalFlag
    and #$FD
UnlinkedKeepHorizontalFlag:
    sta $0620,x
UnlinkedMoveLoop:
    ldx $05
    ldy $06
    txa
    ora $06
    bne UnlinkedMoveAttempt
    jmp UnlinkedMoveFinish
UnlinkedMoveAttempt:
    jsr ApplySlotOffsetIfClear
    bne UnlinkedHorizontalAttempt
    lda $05
    beq UnlinkedMovedVertical
    jsr SetSlotFlag02
UnlinkedMovedVertical:
    lda $06
    beq UnlinkedUseRemainders
    jsr SetSlotFlag01
    lda $0620,x
    and #$EF
    sta $0620,x
UnlinkedUseRemainders:
    lda $04
    sta $06
    lda $03
    sta $05
    lda #$00
    sta $03
    sta $04
    jmp UnlinkedMoveLoop

; A blocked horizontal component is repeatedly halved while testing offsets.
; The original sign-extension sequence and its stopping conditions are kept.
UnlinkedHorizontalAttempt:
    ldx $05                       ; CONTROL_UNLINKED_HORIZONTAL
    beq UnlinkedVerticalAttempt
    ldy #$00
    jsr ApplySlotOffsetIfClear
    bne UnlinkedHorizontalBlocked
    jsr SetSlotFlag02
    lda $03
    sta $05
    lda #$00
    sta $03
    jmp UnlinkedHorizontalAttempt
UnlinkedHorizontalBlocked:
    lda $0620,x
    and #$02
    bne UnlinkedHorizontalReflect
    lda $0500,x
    and #$80
    beq UnlinkedHorizontalStore
    lda #$FF
    jmp UnlinkedHorizontalStore
UnlinkedHorizontalReflect:
    lda $0500,x
    jsr TransformSlotSignedValue
UnlinkedHorizontalStore:
    sta $0500,x
UnlinkedHorizontalRetry:
    lda $05
    rol a
    lda $05
    ror a
    sta $05
    tax
    bne UnlinkedHorizontalProbe
    inx
UnlinkedHorizontalProbe:
    ldy #$00
    jsr ApplySlotOffsetIfClear
    bne UnlinkedHorizontalCheckRetry
    jsr SetSlotFlag02
    jmp UnlinkedHorizontalRetry
UnlinkedHorizontalCheckRetry:
    lda $05
    beq UnlinkedVerticalAttempt
    cmp #$FF
    bne UnlinkedHorizontalRetry

; Apply the same probing strategy vertically, setting bit $10 for positive
; blocked movement and selecting the original response from $0620 bit 0.
UnlinkedVerticalAttempt:
    ldy $06                       ; CONTROL_UNLINKED_VERTICAL_ATTEMPT
    beq UnlinkedMoveFinish
    ldx #$00
    jsr ApplySlotOffsetIfClear
    bne UnlinkedVerticalBlocked
    jsr SetSlotFlag01
    lda $04
    sta $06
    lda #$00
    sta $04
    jmp UnlinkedVerticalAttempt
UnlinkedVerticalBlocked:
    lda $06
    bmi UnlinkedVerticalResponse
    lda $0620,x
    ora #$10
    sta $0620,x
UnlinkedVerticalResponse:
    lda $0620,x
    and #$01
    bne UnlinkedVerticalReflect
    lda $0510,x
    and #$80
    beq UnlinkedVerticalStore
    lda #$FF
    jmp UnlinkedVerticalStore
UnlinkedVerticalReflect:
    lda $0510,x
    jsr TransformSlotSignedValue
UnlinkedVerticalStore:
    sta $0510,x
UnlinkedVerticalRetry:
    lda $06
    rol a
    lda $06
    ror a
    sta $06
    tay
    bne UnlinkedVerticalProbe
    iny
UnlinkedVerticalProbe:
    ldx #$00
    jsr ApplySlotOffsetIfClear
    bne UnlinkedVerticalCheckRetry
    jsr SetSlotFlag01
    jmp UnlinkedVerticalRetry
UnlinkedVerticalCheckRetry:
    lda $06
    beq UnlinkedMoveFinish
    cmp #$FF
    bne UnlinkedVerticalRetry
UnlinkedMoveFinish:
    jsr UpdateSlotDirectionBits
    jsr SyncSlotDirection
.assert (* - BankStart) = $6EA6, error, "bank 0 unlinked movement end"


; When $05D0 is negative, calculate three values and call $D067 only if one
; differs from its saved copy. The downstream consumer is not yet recovered.
TrackSlotPositionChanges:
    ldx $10                       ; CONTROL_TRACK_SLOT_POSITION
    lda $05D0,x
    bpl TrackSlotPositionReturn
    jsr ComputeSlotScaledPosition
    lda $11
    cmp $07D0,x
    bne TrackSlotPositionStore
    lda $12
    cmp $07E0,x
    bne TrackSlotPositionStore
    lda $04
    cmp $05A0,x
    beq TrackSlotPositionReturn
TrackSlotPositionStore:
    lda $11
    sta $07D0,x
    lda $12
    sta $07E0,x
    lda $04
    sta $05A0,x
    jsr UpdateSlotFromPosition
TrackSlotPositionReturn:
    rts

; Select bits $80/$40 of $0660 based on mode bits in $07F0, slot flags or the
; signs of $0500/$0510. The bit operations and carry state are preserved.
UpdateSlotDirectionBits:
    ldx $10                       ; CONTROL_SLOT_DIRECTION_BITS
    lda $07F0,x
    bpl SlotDirectionMode
    jmp SyncSlotDirectionReturn
SlotDirectionMode:
    tay
    and #$40
    bne SlotDirectionFirstSign
    tya
    and #$10
    bne SlotDirectionFirstFlag
    tya
    and #$03
    beq SlotDirectionSecond
    lsr a
    jmp SlotDirectionStoreFirst
SlotDirectionFirstFlag:
    ldy $06D0,x
    bmi SlotDirectionCurrentFlag
    lda $0630,y
    jmp SlotDirectionTestFlag
SlotDirectionCurrentFlag:
    lda $0630,x
SlotDirectionTestFlag:
    and #$10
    bne SlotDirectionFirstOne
    lda #$00
    jmp SlotDirectionStoreFirst
SlotDirectionFirstSign:
    lda #$00
    ldy $0500,x
    bpl SlotDirectionStoreFirst
SlotDirectionFirstOne:
    lda #$01
SlotDirectionStoreFirst:
    asl $0660,x
    ror a
    ror $0660,x
SlotDirectionSecond:
    ldx $10
    lda $07F0,x
    tay
    and #$20
    bne SlotDirectionSecondSign
    tya
    and #$0C
    beq SlotDirectionBitsReturn
    jsr ShiftARight3
    jmp SlotDirectionStoreSecond
SlotDirectionSecondSign:
    lda #$00
    ldy $0510,x
    bpl SlotDirectionStoreSecond
    lda #$01
SlotDirectionStoreSecond:
    clc
    ror a
    ror a
    ror a
    sta $11
    lda $0660,x
    and #$BF
    ora $11
    sta $0660,x
SlotDirectionBitsReturn:
    rts

; Apply the two direction bits through the sprite attribute helpers.
SyncSlotDirection:
    ldx $10                       ; CONTROL_SYNC_SLOT_DIRECTION
    lda $0660,x
    and #$80
    tax
    lda $10
    jsr SetSpriteAttributeBit40
    ldx $10
    lda $0660,x
    and #$40
    tax
    lda $10
    jsr SetSpriteAttributeBit80
    ldx $10
SyncSlotDirectionReturn:
    rts
.assert (* - BankStart) = $6F68, error, "bank 0 slot direction helpers end"


; Derive a 16-bit value from $0700 and $03EE/$03EF, then shift it right by
; three. CalculateSlotCoordinate returns a value in $11, saved to $04.
ComputeSlotScaledPosition:
    jsr CalculateSlotCoordinate                     ; CONTROL_SLOT_SCALED_POSITION
    lda $11
    sta $04
    lda $0700,x
    clc
    adc $03EE
    sta $11
    lda $03EF
    adc #$00
    sta $12
    jsr ShiftPositionRight
    jsr ShiftPositionRight
    jsr ShiftPositionRight
    rts
ShiftPositionRight:
    lsr $12                       ; CONTROL_SLOT_POSITION_SHIFT
    ror $11
    rts
SetSlotFlag02:
    lda $0620,x                   ; CONTROL_SLOT_FLAG02
    ora #$02
    sta $0620,x
    rts
SetSlotFlag01:
    lda $0620,x                   ; CONTROL_SLOT_FLAG01
    ora #$01
    sta $0620,x
    rts

; Resolve the linked slot in $06D0,x. If it exists, copy or calculate mode
; bits and update the current slot's position from the linked slot and offsets.
UpdateLinkedSlotPosition:
    ldx $10                       ; CONTROL_LINKED_SLOT_POSITION
    ldy $06D0,x
    jsr ScriptCheckSlotPresent
    bne LinkedSlotValid
    sta $06D0,x
    rts
LinkedSlotValid:
    lda $0630,x
    and #$04
    beq LinkedSlotCopyMode
    jsr UpdateSlotDirectionBits
    jmp LinkedSlotPosition
LinkedSlotCopyMode:
    lda $0660,y
    and #$C0
    sta $11
    lda $0660,x
    and #$3F
    ora $11
    sta $0660,x
LinkedSlotPosition:
    jsr SyncSlotDirection
    ldy $06D0,x
    lda $0660,y
    sta $11
    lda $0710,x
    cmp #$80
    bne LinkedSlotFirstOffset
    lda $0570,x
    lsr a
    sta $12
    lda $0700,y
    sec
    sbc $12
    bcs LinkedSlotFirstStore
    lda #$00
    jmp LinkedSlotFirstStore
LinkedSlotFirstOffset:
    lda $11
    rol a
    lda $0710,x
    bcc LinkedSlotFirstAdd
    jsr NegateA
    clc
    adc $0570,y
    sec
    sbc $0570,x
LinkedSlotFirstAdd:
    clc
    adc $0580,y
LinkedSlotFirstStore:
    sta $0580,x
    lda $0720,x
    rol $11
    rol $11
    bcc LinkedSlotSecondAdd
    jsr NegateA
    clc
    adc $0560,y
    sec
    sbc $0560,x
LinkedSlotSecondAdd:
    clc
    adc $0590,y
    sta $0590,x
    jsr UpdateSlotBounds
    rts

; Transform a signed byte using the slot's $0730 parameter. The precise role
; of the resulting value is unresolved; preserve $FF and zero edge behavior.
TransformSlotSignedValue:
    sta $12                       ; CONTROL_TRANSFORM_SLOT_SIGNED
    bpl TransformSlotMagnitude
    jsr NegateA
TransformSlotMagnitude:
    sta $11
    lda $0730,x
    beq TransformSlotZeroScale
    tax
    ldy $11
    inx
    beq TransformSlotSignedReady
    jsr MultiplyUnsigned8
TransformSlotSignedReady:
    tya
    ldy $12
    bmi TransformSlotReturn
    jsr NegateA
TransformSlotReturn:
    ldx $10
    rts
TransformSlotZeroScale:
    lda $12
    and #$80
    beq TransformSlotReturn
    lda #$FF
    jmp TransformSlotReturn
.assert (* - BankStart) = $7057, error, "bank 0 linked slot helpers end"


; Four entries select mode bits for the shared two-field update. Depending on
; the mode, the routine transforms operands via $F2D6 or stores/adds them to
; $0500/$0510. Additions that set overflow retain the original field value.
UpdateSlotFieldsMode00:
    lda #$00                      ; CONTROL_SLOT_FIELDS_00
    jmp UpdateSlotFields
UpdateSlotFieldsMode80:
    lda #$80                      ; CONTROL_SLOT_FIELDS_80
    jmp UpdateSlotFields
UpdateSlotFieldsModeC0:
    lda #$C0                      ; CONTROL_SLOT_FIELDS_C0
    jmp UpdateSlotFields
UpdateSlotFieldsMode40:
    lda #$40                      ; CONTROL_SLOT_FIELDS_40
UpdateSlotFields:
    sta $05                       ; CONTROL_SLOT_FIELDS_COMMON
    ldx $10
    lda $0750,x
    ldy $61
    sty $03
    beq UpdateSlotFieldsSecondFlags
    and #$F0
    ora #$03
UpdateSlotFieldsSecondFlags:
    ldy $62
    sty $04
    beq UpdateSlotFieldsStoreFlags
    and #$0F
    ora #$20
UpdateSlotFieldsStoreFlags:
    sta $0750,x
    lda $05
    and #$40
    bne UpdateSlotFieldsChooseMode
    jsr ComputeSlotDirectionFlags
    bpl UpdateSlotFieldsSecondSign
    lda $61
    jsr NegateA
    sta $61
UpdateSlotFieldsSecondSign:
    lda $03DE
    and #$01
    beq UpdateSlotFieldsChooseMode
    lda $62
    jsr NegateA
    sta $62
UpdateSlotFieldsChooseMode:
    lda $05
    bpl UpdateSlotFieldsAdd
    lda $03
    cmp #$FF
    beq UpdateSlotFieldsStoreSecond
    lda $61
    sta $0500,x
UpdateSlotFieldsStoreSecond:
    lda $04
    cmp #$FF
    beq UpdateSlotFieldsReturn
    lda $62
    sta $0510,x
UpdateSlotFieldsReturn:
    rts
UpdateSlotFieldsAdd:
    lda $61
    clc
    adc $0500,x
    bvs UpdateSlotFieldsAddSecond
    sta $0500,x
UpdateSlotFieldsAddSecond:
    lda $62
    clc
    adc $0510,x
    bvs UpdateSlotFieldsAddReturn
    sta $0510,x
UpdateSlotFieldsAddReturn:
    rts
.assert (* - BankStart) = $70D8, error, "bank 0 slot field helper end"

; Use the current slot record with an offset in A, or enter at $F0DC with its
; address already in $FE/$FF and a saved offset. $57 selects offset direction.
LoadSlotRecord:
    pha                          ; CONTROL_SLOT_RECORD_ENTRY
    jsr SlotRecordAddressFromCurrent
LoadSlotRecordIndirect:
    ldy #$00                     ; CONTROL_SLOT_RECORD_LOOKUP
    lda ($FE),y
    pha
    iny
    lda ($FE),y
    sta $FF
    pla
    sta $FE
    pla
    ldy $57
    bpl SlotRecordOffsetAdd
    tay
    lda $FE
    sty $FE
    sec
    sbc $FE
    sta $FE
    lda $FF
    sbc #$00
    sta $FF
    jmp LoadSlotRecordAtFE
SlotRecordOffsetAdd:
    clc
    adc $FE
    sta $FE
    lda $FF
    adc #$00
    sta $FF

; Fetch ten bytes without losing the current command pointer. Some modes may
; replace the current slot pointer with the pointer in bytes 2 and 3.
LoadSlotRecordAtFE:
    lda $53                      ; CONTROL_SLOT_RECORD_FETCH
    pha
    lda $54
    pha
    lda $FE
    sta $53
    lda $FF
    sta $54
    ldx #$0A
    jsr FetchVariableRecord
    pla
    sta $54
    pla
    sta $53
    jsr ScriptSetRecordBufferPointer
    ldx $10
    ldy #$03
    lda $57
    bne SlotRecordCheckData
    lda ($FE),y
    cmp #$FF
    beq SlotRecordCheckData
    dey
    sta $05C0,x
    sta $54
    lda ($FE),y
    sta $05B0,x
    sta $53
SlotRecordCheckData:
    ldy #$01
    lda ($FE),y
    cmp #$FF
    bne SlotRecordReadFields
    jmp SlotRecordFinish
SlotRecordReadFields:
    ldy #$04                     ; CONTROL_SLOT_RECORD_FIELDS
    lda $57
    bpl SlotRecordReadMode
    ldy #$02
SlotRecordReadMode:
    lda ($FE),y
    sta $11
    lda $57
    bmi SlotRecordReadPointer
    cmp #$01
    beq SlotRecordReadPointer
    iny
    lda ($FE),y
    sta $0690,x
    iny
    lda ($FE),y
    sta $06A0,x
    iny
    lda ($FE),y
    sta $06B0,x
    iny
    lda ($FE),y
    sta $06C0,x
    lda $0620,x
    ora #$28
    eor #$08
    sta $0620,x
SlotRecordReadPointer:
    ldy #$00
    lda ($FE),y
    sta $55
    pha
    iny
    lda ($FE),y
    sta $56
    sta $FF
    pla
    sta $FE
    ldy #$00
    lda ($55),y
    cmp #$53
    bne SlotRecordSizeFields
    ldy #$03
    lda ($55),y
    pha
    iny
    lda ($55),y
    sta $56
    pla
    sta $55

; Read packed dimensions and update slot geometry. A leading $53 selects a
; second pointer; the exact record format and higher-level names are tentative.
SlotRecordSizeFields:
    ldy #$00                     ; CONTROL_SLOT_RECORD_SIZE
    lda ($55),y
    rol a
    ldy #$01
    lda ($55),y
    and #$0F
    bcc SlotRecordHeightReady
    asl a
SlotRecordHeightReady:
    jsr ShiftALeft3
    ldy $0560,x
    sta $0560,x
    tya
    beq SlotRecordWidth
    sec
    sbc $0560,x
    clc
    adc $0590,x
    sta $0590,x
SlotRecordWidth:
    ldy #$01
    lda ($55),y
    jsr ShiftARight4
    jsr ShiftALeft3
    sta $0570,x
    lsr a
    sta $12
    lda $0700,x
    beq SlotRecordAllocate
    sec
    sbc $12
    bcs SlotRecordLeftReady
    lda #$00
SlotRecordLeftReady:
    sta $0580,x

; Temporarily mark the slot inactive while AllocateSpriteRecord loads it.
SlotRecordAllocate:
    lda $04E0,x                  ; CONTROL_SLOT_RECORD_ALLOCATE
    pha
    lda #$FF
    sta $04E0,x
    txa
    jsr ReleaseSpriteRecord
    ldy $FF
    ldx $FE
    lda $10
    jsr AllocateSpriteRecord
    beq SlotRecordPlace
    pla
    pha
    jsr ScriptOp18
    ldx $10
    pla
    cmp #$00
    rts
SlotRecordPlace:
    ldx $10                      ; CONTROL_SLOT_RECORD_PLACE
    ldy $0590,x
    lda $0580,x
    tax
    lda $10
    jsr PlaceSlotSprites
    jsr UpdateSlotBounds
    pla
    sta $04E0,x
    lda $0620,x
    and #$04
    beq SlotRecordApplyFlags
    jsr ScriptSetSlotMode
    ldy $0590,x
    lda $0580,x
    tax
    lda $10
    jsr QuerySlotAtPosition
    beq SlotRecordApplyFlags
    ldx $10
    ldy $0590,x
    lda $0580,x
    sec
    sbc #$08
    bcs SlotRecordLeftTest
    lda #$00
SlotRecordLeftTest:
    tax
    lda $10
    jsr QuerySlotAtPosition
    beq SlotRecordUseAdjustedPosition
    ldx $10
    ldy $0590,x
    lda $0580,x
    clc
    adc #$08
    bcc SlotRecordRightTest
    lda #$FF
SlotRecordRightTest:
    tax
    lda $10
    jsr QuerySlotAtPosition
    bne SlotRecordApplyFlags
SlotRecordUseAdjustedPosition:
    ldx $10
    lda $03A6
    sta $0580,x
    lda $03A7
    sta $0590,x
SlotRecordApplyFlags:
    lda $11                      ; CONTROL_SLOT_RECORD_FLAGS
    and #$30
    beq SlotRecordApplyBit40
    tax
    lda $11
    and #$07
    tay
    lda $10
    jsr SetSpriteRecordMode
SlotRecordApplyBit40:
    lda $11
    and #$40
    beq SlotRecordFinish
    lda $10
    jsr SetSpriteRecordBit10
SlotRecordFinish:
    ldx $10
    lda #$00
    rts

; Address calculation: $9F06 + 4*index + low byte of 2*index. This equals
; $9F06 + 6*index below $80; higher indices lose the carry from the first
; doubling. The second entry accepts A; the first loads $04E0 for the slot.
SlotRecordAddressFromCurrent:
    ldx $10                      ; CONTROL_SLOT_RECORD_CURRENT
    lda $04E0,x
SlotRecordAddressFromIndex:
    sta $FE                      ; CONTROL_SLOT_RECORD_ADDRESS
    lda #$00
    sta $FF
    jsr DoubleFEPointer
    lda $FE
    jsr DoubleFEPointer
    clc
    adc $FE
    sta $FE
    lda $FF
    adc #$00
    sta $FF
    lda #$06
    clc
    adc $FE
    sta $FE
    lda #$9F
    adc $FF
    sta $FF
    rts
DoubleFEPointer:
    asl $FE                      ; CONTROL_DOUBLE_FE_POINTER
    rol $FF
    rts
.assert (* - BankStart) = $72CC, error, "bank 0 slot record loader end"


; Advance the 16-bit script pointer by two bytes. Entry at $F2CF advances
; once; $F2CC calls that entry and then falls through for a second increment.
AdvanceScriptPointerTwice:
    jsr AdvanceScriptPointerOnce  ; CONTROL_SCRIPT_ADVANCE_TWICE
AdvanceScriptPointerOnce:
    inc $53
    bne ScriptPointerIncremented
    inc $54
ScriptPointerIncremented:
    rts
.assert (* - BankStart) = $72D6, error, "bank 0 script pointer advance helper"
; Compute flag bits in $03DE from $0660 and selected-slot comparisons.
; When the low mode bits equal 3, a $EF68 result also participates.
ComputeSlotDirectionFlags:
    lda #$00                     ; CONTROL_SLOT_DIRECTION_FLAGS
    sta $03DE
    jsr FindSlotCoordinates
    cmp #$FF
    beq DirectionFlagsMode3
    lda $0660,x
    and #$03
    beq DirectionFlagsSecond
    cmp #$03
    beq DirectionFlagsSecond
    and #$01
    sta $03E1
    ldy #$00
    lda $FE
    cmp $0700,x
    bcs DirectionFlagsFirstValue
    ldy #$80
DirectionFlagsFirstValue:
    tya
    ldy $03E1
    bne DirectionFlagsFirstStore
    eor #$80
DirectionFlagsFirstStore:
    sta $03DE
DirectionFlagsSecond:
    lda $0660,x
    and #$30
    beq DirectionFlagsMode3
    and #$10
    sta $03E1
    ldy #$00
    lda $FF
    cmp $B0,x
    bcs DirectionFlagsSecondValue
    ldy #$01
DirectionFlagsSecondValue:
    tya
    ldy $03E1
    bne DirectionFlagsSecondStore
    eor #$01
DirectionFlagsSecondStore:
    ora $03DE
    sta $03DE
DirectionFlagsMode3:
    lda $0660,x
    and #$03
    eor #$03
    bne DirectionFlagsReturn
    jsr ComputeSlotScaledPosition
    ldy #$00
    lda $90,x
    sec
    sbc $11
    lda $A0,x
    sbc $12
    bcs DirectionFlagsMode3Store
    ldy #$80
DirectionFlagsMode3Store:
    sty $11
    lda $03DE
    and #$7F
    ora $11
    sta $03DE
DirectionFlagsReturn:
    lda $03DE
    rts

; Use $0540,x if enabled and valid; otherwise scan other valid slots whose
; $0640/$0650 bits intersect $0670/$0680 and choose the smallest wrapped
; absolute difference between their $0580 fields. $FE/$FF receive the chosen
; slot's $0700/$B0 fields, or $FF/$FF if no slot qualifies.
FindSlotCoordinates:
    lda $0680,x                  ; CONTROL_FIND_SLOT_COORDINATES
    bpl FindSlotByFields
    lda $0540,x
    cmp #$FF
    beq FindSlotByFields
    tay
    jsr ScriptCheckSlotPresent
    bne FindSlotCoordinatesSelected
    sta $0540,x
    jmp FindSlotByFields
FindSlotCoordinatesSelected:
    lda $0700,y
    sta $FE
    lda $B0,y
    sta $FF
    rts
FindSlotByFields:
    lda #$FF
    sta $FE
    sta $FF
    ldy #$00
FindSlotByFieldsLoop:
    jsr ScriptCheckSlotPresent
    beq FindSlotByFieldsNext
    tya
    cmp $10
    beq FindSlotByFieldsNext
    lda $0640,y
    and $0670,x
    bne FindSlotByFieldsCompare
    lda $0650,y
    and $0680,x
    beq FindSlotByFieldsNext
FindSlotByFieldsCompare:
    lda $0580,y
    sec
    sbc $0580,x
    bcs FindSlotDistanceReady
    jsr NegateA
FindSlotDistanceReady:
    cmp $FE
    bcs FindSlotByFieldsNext
    sta $FE
    sty $FF
FindSlotByFieldsNext:
    iny
    cpy #$10
    bne FindSlotByFieldsLoop
    ldy $FF
    cpy #$FF
    bne FindSlotCoordinatesSelected
    tya
    rts

; Initialize and advance the three-byte $19-$1B state. The update also reads
; from ($1E), advances and masks that pointer, and conditionally flips bit 7.
InitializeState19To1B:
    lda #$FD                     ; CONTROL_INIT_STATE_19
    sta $19
    lda #$43
    sta $1A
    lda #$03
    sta $1B
    rts
AdvanceState19To1B:
    lda $19                      ; CONTROL_ADVANCE_STATE_19
    clc
    adc #$C3
    sta $19
    lda $1A
    adc #$9E
    sta $1A
    lda $1B
    adc #$26
    sta $1B
    ldy #$00
    lda ($1E),y
    clc
    adc $1B
    sta $1B
    pha
    lda $1E
    clc
    adc #$01
    sta $1E
    and #$01
    tay
    lda $1F
    adc #$00
    ora #$80
    and #$BF
    sta $1F
    pla
    cpy #$00
    beq AdvanceStateReturn
    eor #$80
AdvanceStateReturn:
    rts

; Query the offset first; if $8A4C returns zero, copy the calculated position
; into the current slot, update bounds and optionally check its mode.
ApplySlotOffsetIfClear:
    jsr TestSlotOffset           ; CONTROL_APPLY_SLOT_OFFSET
    bne ApplySlotOffsetReturn
    lda $03A6
    sta $0580,x
    lda $03A7
    sta $0590,x
    jsr UpdateSlotBounds
    lda $0620,x
    and #$40
    beq ApplySlotOffsetSuccess
    jsr ScriptCheckSlotMode
ApplySlotOffsetSuccess:
    lda #$00
ApplySlotOffsetReturn:
    rts
.assert (* - BankStart) = $7424, error, "bank 0 coordinate helper end"


; Apply signed X/Y offsets to the current slot's fields with saturation, then
; query $8A4C and return its zero/nonzero result with X restored to the slot.
TestSlotOffset:
    jsr ClampSlotOffsets          ; CONTROL_TEST_SLOT_OFFSET
    lda $10
    jsr QuerySlotAtPosition
    ldx $10
    cmp #$00
    rts
ClampSlotOffsets:
    stx $03A6                     ; CONTROL_CLAMP_SLOT_OFFSETS
    ldx $10
    clc
    tya
    bmi ClampSlotVerticalNegative
    adc $0590,x
    bcs ClampSlotVerticalMax
    cmp #$F0
    bcc ClampSlotVerticalReady
ClampSlotVerticalMax:
    lda #$EF
    jmp ClampSlotVerticalReady
ClampSlotVerticalNegative:
    adc $0590,x
    bcs ClampSlotVerticalReady
    lda #$00
ClampSlotVerticalReady:
    tay
    clc
    lda $03A6
    bmi ClampSlotHorizontalNegative
    adc $0580,x
    bcc ClampSlotHorizontalReady
    lda #$FF
    jmp ClampSlotHorizontalReady
ClampSlotHorizontalNegative:
    adc $0580,x
    bcs ClampSlotHorizontalReady
    lda #$00
ClampSlotHorizontalReady:
    tax
    rts

; Recalculate $0700,x from half $0570 plus $0580, clamping carry to $FF.
UpdateSlotMidpoint:
    lda $0570,x                   ; CONTROL_SLOT_MIDPOINT
    lsr a
    clc
    adc $0580,x
    bcc UpdateSlotMidpointStore
    lda #$FF
UpdateSlotMidpointStore:
    sta $0700,x
    rts
UpdateSlotBounds:
    ldx $10                       ; CONTROL_SLOT_BOUNDS
    jsr UpdateSlotMidpoint
UpdateSlotVerticalBound:
    lda $0590,x
    clc
    adc $0560,x
    sta $B0,x
    dec $B0,x
    rts
.assert (* - BankStart) = $748A, error, "bank 0 slot coordinate helpers end"

; Tick the deferred update timer when the engine is active. Preserve $10.
; The original ADC of $E7 uses the incoming carry; do not insert CLC.
ProcessPendingPpuUpdate:
    lda $28 ; CONTROL_PROCESS_PENDING_PPU_UPDATE
    ora $00
    beq PendingPpuFrameTick
    rts
PendingPpuFrameTick:
    lda $10 ; CONTROL_PENDING_PPU_FRAME_TICK
    pha
    dec $09
    beq PendingPpuTickExpired
    jmp PendingPpuCheckQueue
PendingPpuRestoreTick:
    inc $09
    jmp PendingPpuCheckQueue
PendingPpuTickExpired:
    lda $14
    and #$01
    bne PendingPpuRestoreTick
    lda $0D
    sta $09
    inc $14
    inc $20
PendingPpuCheckQueue:
    lda $E7 ; CONTROL_PENDING_PPU_CHECK_QUEUE
    beq PendingPpuReturn
    adc #$04
    sta $FE
    jsr PpuQueueRemaining
    sta $03E1
    cmp $FE
    bcc PendingPpuReturn
    jsr BuildPendingPpuUpdate
PendingPpuReturn:
    pla
    sta $10
    rts
; Reserve $21 stack bytes while dispatching the pending PPU update type.
; Banked payloads are copied to the stack before constructing queue entries.
BuildPendingPpuUpdate:
    tsx ; CONTROL_BUILD_PENDING_PPU_UPDATE
    txa
    sec
    sbc #$21
    tax
    txs
    lda $04D9
    cmp #$AB
    beq PendingPpuStreamJump
    cmp #$BF
    bne PendingPpuCheckPalette
PendingPpuStreamJump:
    jmp PendingPpuStream
PendingPpuCheckPalette:
    cmp #$83 ; CONTROL_PENDING_PPU_CHECK_PALETTE
    bne PendingPpuCheckBanked
    jmp PendingPpuPaletteAddress
PendingPpuCheckBanked:
    cmp #$70 ; CONTROL_PENDING_PPU_CHECK_BANKED
    beq PendingPpuCopyBanked
    cmp #$6E
    bne PendingPpuSelectAddress
PendingPpuCopyBanked:
    jsr PendingPpuSetSource ; CONTROL_PENDING_PPU_COPY_BANKED
    lda $E7
    sta $03E0
    jsr CopyToStack
    tsx
    inx
    stx $EA
    lda #$01
    sta $EB
    lda $04D9
    cmp #$70
    bne PendingPpuSelectAddress
    jmp PendingPpuReverseRow
PendingPpuSetSource:
    lda $EA ; CONTROL_PENDING_PPU_SET_SOURCE
    sta $FE
    lda $EB
    sta $FF
    rts
; Form a PPU address from the pending row/column and either a nametable
; selector or the configured base address.
PendingPpuSelectAddress:
    lda $04D8 ; CONTROL_PENDING_PPU_SELECT_ADDRESS
    cmp #$FF
    beq PendingPpuBaseAddress
    ldx $E8
    ldy #$20
    jsr MultiplyUnsigned8
    lda $E9
    jsr AddAToXY
    stx $FE
    sty $FF
    lda $04D8
    asl a
    asl a
    ora #$20
    clc
    adc $FF
    sta $FF
    jmp PendingPpuFormatNumber
PendingPpuBaseAddress:
    lda $E8 ; CONTROL_PENDING_PPU_BASE_ADDRESS
    sta $FE
    lda #$00
    sta $FF
    jsr DoubleFEPointer
    jsr DoubleFEPointer
    jsr DoubleFEPointer
    jsr DoubleFEPointer
    jsr DoubleFEPointer
    clc
    lda $E9
    adc $FE
    sta $FE
    lda $FF
    adc #$00
    sta $FF
    lda $FE
    clc
    adc $04DB
    sta $FE
    lda $FF
    adc $04DA
    sta $FF
PendingPpuFormatNumber:
    lda $04D9 ; CONTROL_PENDING_PPU_FORMAT_NUMBER
    cmp #$74
    bne PendingPpuCheckImmediateNumber
    jsr FormatPendingPpuCounter
    jmp PendingPpuQueueHeader
PendingPpuCheckImmediateNumber:
    cmp #$75 ; CONTROL_PENDING_PPU_CHECK_IMMEDIATE_NUMBER
    bne PendingPpuQueueHeader
    lda $EA
    sta $03E0
    lda $EB
    sta $03E1
    jsr FormatPendingPpuNumber5
; Append a normal PPU queue header and either copy the payload or fill it
; with the byte in $EA. Release the temporary stack space on completion.
PendingPpuQueueHeader:
    ldx $0380 ; CONTROL_PENDING_PPU_QUEUE_HEADER
    lda #$00
    sta $0300,x
    inx
    lda $FF
    sta $0300,x
    inx
    lda $FE
    sta $0300,x
    inx
    lda $E7
    sta $0300,x
    sta $FE
    inx
    lda $04D9
    cmp #$6F
    beq PendingPpuFill
    ldy #$00
PendingPpuCopyData:
    lda ($EA),y ; CONTROL_PENDING_PPU_COPY_DATA
    sta $0300,x
    inx
    iny
    dec $FE
    bne PendingPpuCopyData
    jmp PendingPpuClear
PendingPpuFill:
    lda $EA ; CONTROL_PENDING_PPU_FILL
PendingPpuFillLoop:
    sta $0300,x
    inx
    dec $FE
    bne PendingPpuFillLoop
PendingPpuClear:
    lda #$00 ; CONTROL_PENDING_PPU_CLEAR
    sta $E7
PendingPpuStoreQueueEnd:
    stx $0380 ; CONTROL_PENDING_PPU_STORE_QUEUE_END
PendingPpuReleaseStack:
    tsx ; CONTROL_PENDING_PPU_RELEASE_STACK
    txa
    clc
    adc #$21
    tax
    txs
    rts
PendingPpuReverseRow:
    lda $E8 ; CONTROL_PENDING_PPU_REVERSE_ROW
    asl a
    asl a
    asl a
    sta $E8
    lda #$F8
    sec
    sbc $E8
    sta $FE
    lda #$27
    sbc #$00
    sta $FF
    lda #$6E
    sta $04D9
    jmp PendingPpuFormatNumber
PendingPpuPaletteAddress:
    lda #$3F ; CONTROL_PENDING_PPU_PALETTE_ADDRESS
    sta $FF
    lda $E9
    sta $FE
    lda #$E8
    sta $EA
    lda #$00
    sta $EB
    jmp PendingPpuQueueHeader
CopyDirectToStack:
    tsx ; CONTROL_COPY_DIRECT_TO_STACK
    inx
    inx
    inx
    lda $FF
    pha
    ldy #$00
CopyDirectToStackLoop:
    lda ($FE),y
    sta $0100,x
    iny
    inx
    dec $03E0
    bne CopyDirectToStackLoop
    pla
    sta $FF
    rts
; Types $AB/$BF copy a 32-byte command window from banked or direct memory.
; Bytes $FE/$FF change a 16-bit destination; zero ends input.
PendingPpuStream:
    lda $03E1 ; CONTROL_PENDING_PPU_STREAM
    cmp #$20
    bcc PendingPpuReleaseStack
    jsr PendingPpuSetSource
    lda #$20
    sta $03E0
    sta $03DE
    ldx $04D9
    cpx #$BF
    bne PendingPpuStreamBanked
    jsr CopyDirectToStack
    jmp PendingPpuStreamBegin
PendingPpuStreamBanked:
    jsr CopyToStack
PendingPpuStreamBegin:
    tsx ; CONTROL_PENDING_PPU_STREAM_BEGIN
    txa
    tay
    iny
    ldx $0380
    lda #$00
    sta $03E0
; Group ordinary bytes into queue entries, stopping when the local input or
; available queue count is exhausted. Pointer advancement is preserved.
PendingPpuStreamNext:
    lda $0100,y ; CONTROL_PENDING_PPU_STREAM_NEXT
    beq PendingPpuStreamEnd
    cmp #$FE
    bcc PendingPpuStreamCharacter
    lda $03E0
    bne PendingPpuStreamPause
    jsr PendingPpuStreamAddress
    jmp PendingPpuStreamNext
PendingPpuStreamCharacter:
    lda $03E0 ; CONTROL_PENDING_PPU_STREAM_CHARACTER
    bne PendingPpuStreamWrite
    jsr PendingPpuStreamHeader
PendingPpuStreamWrite:
    lda $0100,y
    iny
    sta $0300,x
    inx
    lda #$01
    jsr AdvancePendingPpuSource
    inc $03E0
    dec $03DE
    beq PendingPpuStreamEnd
    dec $03E1
    bne PendingPpuStreamNext
PendingPpuStreamEnd:
    jsr PendingPpuStreamFinishEntry ; CONTROL_PENDING_PPU_STREAM_END
    jmp PendingPpuClear
PendingPpuStreamPause:
    jsr PendingPpuStreamFinishEntry ; CONTROL_PENDING_PPU_STREAM_PAUSE
    jmp PendingPpuStoreQueueEnd
PendingPpuStreamFinishEntry:
    lda $03E0 ; CONTROL_PENDING_PPU_STREAM_FINISH_ENTRY
    beq PendingPpuStreamFinishReturn
    ldy $03DF
    sta $0300,y
PendingPpuStreamFinishReturn:
    rts
; $FF installs an absolute destination and $FE adds a relative offset.
PendingPpuStreamAddress:
    lda $0100,y ; CONTROL_PENDING_PPU_STREAM_ADDRESS
    cmp #$FE
    beq PendingPpuStreamRelativeAddress
    lda $0101,y
    sta $03C6
    lda $0102,y
PendingPpuStreamAddressStore:
    sta $03C7
    iny
    iny
    iny
    lda #$03
    jsr AdvancePendingPpuSource
    lda $03DE
    sec
    sbc #$03
    sta $03DE
    rts
PendingPpuStreamRelativeAddress:
    lda $0101,y ; CONTROL_PENDING_PPU_STREAM_RELATIVE_ADDRESS
    clc
    adc $03C6
    sta $03C6
    lda $0102,y
    adc $03C7
    jmp PendingPpuStreamAddressStore
; Start a queue entry and reserve its length byte for the completed group.
PendingPpuStreamHeader:
    lda #$00 ; CONTROL_PENDING_PPU_STREAM_HEADER
    sta $0300,x
    inx
    lda $03C7
    sta $0300,x
    inx
    lda $03C6
    sta $0300,x
    inx
    stx $03DF
    inx
    lda $03E1
    sec
    sbc #$04
    sta $03E1
    rts
.assert (* - BankStart) = $76F3, error, "bank 0 pending PPU update end"

; Select a valid tracked slot and calculate horizontal motion. When two
; are present, compare their signed $0700 values before choosing a slot.
UpdateHorizontalMotion:
    ldx $3C ; CONTROL_UPDATE_HORIZONTAL_MOTION
    ldy $3D
    bmi HorizontalResolveMotion
    ldx $3D
    ldy $3C
    bmi HorizontalResolveMotion
    jsr ScriptCheckSlotPresent
    beq HorizontalResolveMotion
    lda $04E0,x
    cmp #$FF
    bne HorizontalCompareSlots
    sta $3D
    jmp UpdateHorizontalMotion
HorizontalCompareSlots:
    lda #$00 ; CONTROL_HORIZONTAL_COMPARE_SLOTS
    sta $36
    lda $0700,x
    eor $0700,y
    bmi HorizontalMotionGate
    lda $0700,x
    bpl HorizontalComparePositive
    cmp $0700,y
    bcs HorizontalResolveMotion
    jmp HorizontalUseFirstSlot
HorizontalComparePositive:
    cmp $0700,y
    bcc HorizontalResolveMotion
HorizontalUseFirstSlot:
    ldx $3C
HorizontalResolveMotion:
    jsr CalculateHorizontalMotion ; CONTROL_HORIZONTAL_RESOLVE_MOTION
    sta $36
; Direction mask $13 can suppress the result. Split nonzero motion into
; half- and quarter-rate components, retaining remainders in $35 and $34.
HorizontalMotionGate:
    lda $36 ; CONTROL_HORIZONTAL_MOTION_GATE
    bpl HorizontalMotionPositiveGate
    lda $13
    and #$01
    bne HorizontalMotionClear
    jmp HorizontalMotionSplit
HorizontalMotionPositiveGate:
    lda $13
    and #$02
    beq HorizontalMotionSplit
HorizontalMotionClear:
    lda #$00
    sta $36
HorizontalMotionSplit:
    lda $36 ; CONTROL_HORIZONTAL_MOTION_SPLIT
    bne HorizontalMotionAccumulate
    sta $37
    sta $38
    rts
HorizontalMotionAccumulate:
    clc ; CONTROL_HORIZONTAL_MOTION_ACCUMULATE
    adc $35
    sta $FE
    jsr ArithmeticShiftRightA
    sta $37
    asl a
    sta $FF
    lda $FE
    sec
    sbc $FF
    sta $35
    lda $36
    clc
    adc $34
    sta $FE
    jsr ArithmeticShiftRightA
    jsr ArithmeticShiftRightA
    sta $38
    asl a
    asl a
    sta $FF
    lda $FE
    sec
    sbc $FF
    sta $34
    rts
; Repeat the two-slot selection for the vertical $B0 coordinates; retain
; half- and quarter-rate remainders in $30 and $2F.
UpdateVerticalMotion:
    ldx $3C ; CONTROL_UPDATE_VERTICAL_MOTION
    ldy $3D
    bmi VerticalResolveMotion
    ldx $3D
    ldy $3C
    bmi VerticalResolveMotion
    jsr ScriptCheckSlotPresent
    beq VerticalResolveMotion
    lda $04E0,x
    cmp #$FF
    bne VerticalCompareSlots
    sta $3D
    jmp UpdateVerticalMotion
VerticalCompareSlots:
    lda #$00 ; CONTROL_VERTICAL_COMPARE_SLOTS
    sta $31
    lda $B0,x
    eor $B0,y
    bmi VerticalMotionGate
    lda $B0,x
    bpl VerticalComparePositive
    cmp $B0,y
    bcs VerticalResolveMotion
    jmp VerticalUseFirstSlot
VerticalComparePositive:
    cmp $B0,y
    bcc VerticalResolveMotion
VerticalUseFirstSlot:
    ldx $3C
VerticalResolveMotion:
    jsr CalculateVerticalMotion ; CONTROL_VERTICAL_RESOLVE_MOTION
    sta $31
VerticalMotionGate:
    lda $31 ; CONTROL_VERTICAL_MOTION_GATE
    bpl VerticalMotionPositiveGate
    lda $13
    and #$04
    bne VerticalMotionClear
    jmp VerticalMotionSplit
VerticalMotionPositiveGate:
    lda $13
    and #$08
    beq VerticalMotionSplit
VerticalMotionClear:
    lda #$00
    sta $31
VerticalMotionSplit:
    lda $31 ; CONTROL_VERTICAL_MOTION_SPLIT
    bne VerticalMotionAccumulate
    sta $32
    sta $33
    rts
VerticalMotionAccumulate:
    clc ; CONTROL_VERTICAL_MOTION_ACCUMULATE
    adc $30
    sta $FE
    jsr ArithmeticShiftRightA
    sta $32
    asl a
    sta $FF
    lda $FE
    sec
    sbc $FF
    sta $30
    lda $31
    clc
    adc $2F
    sta $FE
    jsr ArithmeticShiftRightA
    jsr ArithmeticShiftRightA
    sta $33
    asl a
    asl a
    sta $FF
    lda $FE
    sec
    sbc $FF
    sta $2F
    rts
; Arithmetic right shift: copy bit 7 to carry before rotating the saved A.
ArithmeticShiftRightA:
    pha ; CONTROL_ARITHMETIC_SHIFT_RIGHT_A
    rol a
    pla
    ror a
    rts
; Determine horizontal motion from slot $0700 relative to $60/$A0. Clamp
; positive motion to eight and to the left scroll and position-record limits.
CalculateHorizontalMotion:
    lda #$00 ; CONTROL_CALCULATE_HORIZONTAL_MOTION
    sta $03E0
    cpx #$FF
    beq HorizontalMotionReturnJump2
    lda $04E0,x
    cmp #$FF
    bne HorizontalMotionLeftDistance
HorizontalMotionReturnJump:
    jmp HorizontalMotionReturn
HorizontalMotionLeftDistance:
    lda #$60 ; CONTROL_HORIZONTAL_MOTION_LEFT_DISTANCE
    sec
    sbc $0700,x
    beq HorizontalMotionReturnJump
    bcc HorizontalMotionRightDistance
    cmp #$08
    bcc HorizontalMotionLeftBound
    lda #$08
HorizontalMotionLeftBound:
    sta $03E1 ; CONTROL_HORIZONTAL_MOTION_LEFT_BOUND
    lda $03EE
    sta $5E
    lda $03EF
    sta $5F
    jsr ShiftSearchCoordinateRight
    jsr ShiftSearchCoordinateRight
    jsr ShiftSearchCoordinateRight
    lda $5F
    bne HorizontalMotionCheckRecord
    lda $0E
    cmp #$02
    bcs HorizontalMotionCheckRecord
    lda $03EE
    cmp $03E1
    bcs HorizontalMotionCheckRecord
    sta $03E1
HorizontalMotionCheckRecord:
    jsr SearchPositionRecordsA ; CONTROL_HORIZONTAL_MOTION_CHECK_RECORD
    cmp #$F3
    bne HorizontalMotionCheckOtherRecord
    jsr FindSlotWithFlag04
    beq HorizontalMotionSetPositive
    jmp HorizontalMotionTileLimit
HorizontalMotionCheckOtherRecord:
    cmp #$F1
    bne HorizontalMotionSetPositive
HorizontalMotionTileLimit:
    lda $03EE ; CONTROL_HORIZONTAL_MOTION_TILE_LIMIT
    and #$07
    beq HorizontalMotionReturn
    sta $03DF
    lda $03E1
    cmp $03DF
    bcc HorizontalMotionSetPositive
    lda $03DF
    sta $03E1
HorizontalMotionSetPositive:
    lda $03E1 ; CONTROL_HORIZONTAL_MOTION_SET_POSITIVE
    sta $03E0
HorizontalMotionReturnJump2:
    jmp HorizontalMotionReturn
ShiftSearchCoordinateRight:
    lsr $5F ; CONTROL_SHIFT_SEARCH_COORDINATE_RIGHT
    ror $5E
    rts
; For the opposite direction, clamp to eight and the right map limit,
; then negate the selected amount.
HorizontalMotionRightDistance:
    lda $0700,x ; CONTROL_HORIZONTAL_MOTION_RIGHT_DISTANCE
    sec
    sbc #$A0
    beq HorizontalMotionReturn
    bcc HorizontalMotionReturn
    cmp #$08
    bcc HorizontalMotionRightBound
    lda #$08
HorizontalMotionRightBound:
    sta $03E1 ; CONTROL_HORIZONTAL_MOTION_RIGHT_BOUND
    jsr HorizontalMotionRightLimit
    stx $03DF
    lda $03E1
    cmp $03DF
    bcc HorizontalMotionSetNegative
    lda $03DF
HorizontalMotionSetNegative:
    jsr NegateA ; CONTROL_HORIZONTAL_MOTION_SET_NEGATIVE
    sta $03E0
HorizontalMotionReturn:
    lda $03E0 ; CONTROL_HORIZONTAL_MOTION_RETURN
    rts
; Determine vertical motion from slot $B0 relative to $78/$B0. The $4F
; gate and vertical scroll alignment can further limit positive motion.
CalculateVerticalMotion:
    lda #$00 ; CONTROL_CALCULATE_VERTICAL_MOTION
    sta $03E0
    cpx #$FF
    beq VerticalMotionReturnJump
    lda $04E0,x
    cmp #$FF
    beq VerticalMotionReturn
    lda #$78
    sec
    sbc $B0,x
    beq VerticalMotionReturn
    bcc VerticalMotionBottomDistance
    cmp #$10
    bcc VerticalMotionTopBound
    lda #$10
VerticalMotionTopBound:
    sta $03E1 ; CONTROL_VERTICAL_MOTION_TOP_BOUND
    lda $4F
    bne VerticalMotionSetPositive
    lda $03F0
    and #$07
    beq VerticalMotionReturn
    sta $03DF
    lda $03E1
    cmp $03DF
    bcc VerticalMotionSetPositive
    lda $03DF
    sta $03E1
VerticalMotionSetPositive:
    lda $03E1 ; CONTROL_VERTICAL_MOTION_SET_POSITIVE
    sta $03E0
VerticalMotionReturnJump:
    jmp VerticalMotionReturn
; Clamp negative vertical motion to sixteen and the bottom map limit.
VerticalMotionBottomDistance:
    lda $B0,x ; CONTROL_VERTICAL_MOTION_BOTTOM_DISTANCE
    sec
    sbc #$B0
    beq VerticalMotionReturn
    bcc VerticalMotionReturn
    cmp #$10
    bcc VerticalMotionBottomBound
    lda #$10
VerticalMotionBottomBound:
    sta $03E1 ; CONTROL_VERTICAL_MOTION_BOTTOM_BOUND
    jsr VerticalMotionMapBottomLimit
    stx $03DF
    lda $03E1
    cmp $03DF
    bcc VerticalMotionSetNegative
    lda $03DF
VerticalMotionSetNegative:
    jsr NegateA ; CONTROL_VERTICAL_MOTION_SET_NEGATIVE
    sta $03E0
VerticalMotionReturn:
    lda $03E0 ; CONTROL_VERTICAL_MOTION_RETURN
    rts
.assert (* - BankStart) = $7941, error, "bank 0 frame motion calculations end"

; Update one slot's draw coordinates unless absent or disabled. Out-of-range
; slots can be released or reinitialized according to their flags and link.
UpdateSlotDrawPosition:
    jsr SlotDrawCheckPresent ; CONTROL_UPDATE_SLOT_DRAW_POSITION
    beq SlotDrawReturn
    jsr SlotDrawCheckDisabled
    bne SlotDrawReturn
    lda $0620,x
    bmi SlotDrawCheckDistance
    jsr CalculateSlotDrawHorizontal
    bne SlotDrawStoreHorizontal
SlotDrawCheckRelease:
    lda $05E0,x ; CONTROL_SLOT_DRAW_CHECK_RELEASE
    bpl SlotDrawReleaseIfUnlinked
    lda $06D0,x
    cmp #$FF
    bne SlotDrawReturn
    jsr InitializeScrolledSlot
    rts
SlotDrawReleaseIfUnlinked:
    lda $06D0,x ; CONTROL_SLOT_DRAW_RELEASE_UNLINKED
    cmp #$FF
    bne SlotDrawReturn
    jmp ReleaseCurrentSlot
SlotDrawStoreHorizontal:
    sta $0580,x ; CONTROL_SLOT_DRAW_STORE_HORIZONTAL
    jsr UpdateSlotMidpoint
    jsr CalculateSlotDrawVertical
    beq SlotDrawCheckRelease
    sta $0590,x
    jsr UpdateSlotVerticalBound
SlotDrawReturn:
    rts ; CONTROL_SLOT_DRAW_RETURN
SlotDrawCheckPresent:
    lda $04E0,x ; CONTROL_SLOT_DRAW_CHECK_PRESENT
    cmp #$FF
    rts
SlotDrawCheckDisabled:
    lda $0630,x ; CONTROL_SLOT_DRAW_CHECK_DISABLED
    and #$20
    rts
SlotDrawCheckDistance:
    jsr SlotDistanceFromReference ; CONTROL_SLOT_DRAW_CHECK_DISTANCE
    cmp #$10
    bcs SlotDrawReleaseIfUnlinked
    rts
; Reinitialize a scrolling slot, form absolute coordinates from the current
; scroll and draw offsets, then apply the slot's selected fractional motion.
InitializeScrolledSlot:
    ldx $10 ; CONTROL_INITIALIZE_SCROLLED_SLOT
    lda $04E0,x
    sta $2A
    jsr ReleaseCurrentSlot
    ldx $10
    lda #$80
    sta $0620,x
    lda #$FE
    sta $70,x
    ldx $10
    jsr InitializeCurrentSlot
    lda $0630,x
    ora #$02
    sta $0630,x
    lda $03EE
    clc
    adc $0580,x
    sta $07D0,x
    lda $03EF
    adc #$00
    sta $07E0,x
    jsr SelectSlotHorizontalMotion
    ora #$00
    bpl ScrolledSlotAddHorizontal
    jsr NegateA
    sta $11
    lda $07D0,x
    sec
    sbc $11
    sta $07D0,x
    bcs ScrolledSlotHorizontalFraction
    dec $07E0,x
    jmp ScrolledSlotHorizontalFraction
ScrolledSlotAddHorizontal:
    clc ; CONTROL_SCROLLED_SLOT_ADD_HORIZONTAL
    adc $07D0,x
    sta $07D0,x
    bcc ScrolledSlotHorizontalFraction
    inc $07E0,x
ScrolledSlotHorizontalFraction:
    lda $07D0,x ; CONTROL_SCROLLED_SLOT_HORIZONTAL_FRACTION
    and #$07
    sta $05A0,x
    jsr ShiftScrolledSlotHorizontal
    jsr ShiftScrolledSlotHorizontal
    jsr ShiftScrolledSlotHorizontal
    lda $03F0
    clc
    adc $0590,x
    sta $80,x
    lda $03F1
    adc #$00
    sta $12
    jsr SelectSlotVerticalMotion
    ora #$00
    bpl ScrolledSlotAddVertical
    jsr NegateA
    sta $11
    lda $80,x
    sec
    sbc $11
    sta $80,x
    bcs ScrolledSlotVerticalFraction
    dec $12
    jmp ScrolledSlotVerticalFraction
ShiftScrolledSlotHorizontal:
    lsr $07E0,x ; CONTROL_SHIFT_SCROLLED_SLOT_HORIZONTAL
    ror $07D0,x
    rts
ScrolledSlotAddVertical:
    clc ; CONTROL_SCROLLED_SLOT_ADD_VERTICAL
    adc $80,x
    sta $80,x
    bcc ScrolledSlotVerticalFraction
    inc $12
ScrolledSlotVerticalFraction:
    lda $80,x ; CONTROL_SCROLLED_SLOT_VERTICAL_FRACTION
    and #$07
    sta $0590,x
    jsr ShiftScrolledSlotVertical
    jsr ShiftScrolledSlotVertical
ShiftScrolledSlotVertical:
    lsr $12 ; CONTROL_SHIFT_SCROLLED_SLOT_VERTICAL
    ror $80,x
    rts
; Apply the selected horizontal motion to $0580. On byte overflow or
; underflow, $05D0 bit $02 selects clamping versus the zero-return path.
CalculateSlotDrawHorizontal:
    jsr SelectSlotHorizontalMotion ; CONTROL_CALCULATE_SLOT_DRAW_HORIZONTAL
    clc
    ora #$00
    bpl SlotDrawHorizontalPositive
    adc $0580,x
    bcs SlotDrawHorizontalReturn
    lda $05D0,x
    and #$02
    beq SlotDrawHorizontalBlocked
    lda #$00
    jmp SlotDrawHorizontalReturn
SlotDrawHorizontalPositive:
    adc $0580,x ; CONTROL_SLOT_DRAW_HORIZONTAL_POSITIVE
    bcc SlotDrawHorizontalReturn
    lda $05D0,x
    and #$02
    bne SlotDrawHorizontalMaximum
SlotDrawHorizontalBlocked:
    ldy #$00 ; CONTROL_SLOT_DRAW_HORIZONTAL_BLOCKED
    rts
SlotDrawHorizontalMaximum:
    lda #$FF ; CONTROL_SLOT_DRAW_HORIZONTAL_MAXIMUM
SlotDrawHorizontalReturn:
    ldy #$FF ; CONTROL_SLOT_DRAW_HORIZONTAL_RETURN
    rts
; Select horizontal full, half, quarter or zero motion from $05E0 bits 0-1.
SelectSlotHorizontalMotion:
    lda $05E0,x ; CONTROL_SELECT_SLOT_HORIZONTAL_MOTION
    and #$03
    cmp #$03
    beq SlotHorizontalMotionZero
    tay
    lda $36
    beq SlotHorizontalMotionZero
    cpy #$00
    beq SlotHorizontalMotionReturn
    lda $37
    cpy #$01
    beq SlotHorizontalMotionReturn
    lda $38
SlotHorizontalMotionReturn:
    rts ; CONTROL_SLOT_HORIZONTAL_MOTION_RETURN
SlotHorizontalMotionZero:
    lda #$00 ; CONTROL_SLOT_HORIZONTAL_MOTION_ZERO
    rts
; Apply vertical motion to $0590, with the original $EF maximum and the
; same $05D0 bit $02 clamp choice.
CalculateSlotDrawVertical:
    jsr SelectSlotVerticalMotion ; CONTROL_CALCULATE_SLOT_DRAW_VERTICAL
    clc
    ora #$00
    bpl SlotDrawVerticalPositive
    adc $0590,x
    bcs SlotDrawVerticalReturn
    lda $05D0,x
    and #$02
    beq SlotDrawVerticalBlocked
    lda #$00
    jmp SlotDrawVerticalReturn
SlotDrawVerticalPositive:
    adc $0590,x ; CONTROL_SLOT_DRAW_VERTICAL_POSITIVE
    bcs SlotDrawVerticalOverflow
    cmp #$EF
    bcc SlotDrawVerticalReturn
SlotDrawVerticalOverflow:
    lda $05D0,x ; CONTROL_SLOT_DRAW_VERTICAL_OVERFLOW
    and #$02
    bne SlotDrawVerticalMaximum
SlotDrawVerticalBlocked:
    ldy #$00 ; CONTROL_SLOT_DRAW_VERTICAL_BLOCKED
    rts
SlotDrawVerticalMaximum:
    lda #$EF ; CONTROL_SLOT_DRAW_VERTICAL_MAXIMUM
SlotDrawVerticalReturn:
    ldy #$FF ; CONTROL_SLOT_DRAW_VERTICAL_RETURN
    rts
; Select vertical full, half, quarter or zero motion from $05E0 bits 2-3.
SelectSlotVerticalMotion:
    lda $05E0,x ; CONTROL_SELECT_SLOT_VERTICAL_MOTION
    and #$0C
    cmp #$0C
    beq SlotVerticalMotionZero
    tay
    lda $31
    beq SlotVerticalMotionZero
    cpy #$00
    beq SlotVerticalMotionReturn
    lda $32
    cpy #$04
    beq SlotVerticalMotionReturn
    lda $33
SlotVerticalMotionReturn:
    rts ; CONTROL_SLOT_VERTICAL_MOTION_RETURN
SlotVerticalMotionZero:
    lda #$00 ; CONTROL_SLOT_VERTICAL_MOTION_ZERO
    rts
.assert (* - BankStart) = $7AE9, error, "bank 0 slot draw motion end"
; Check position records near the right edge before computing the remaining
; horizontal scroll range; return a capped low-byte distance in X.
HorizontalMotionRightLimit:
    lda $0E ; CONTROL_HORIZONTAL_MOTION_RIGHT_LIMIT
    clc
    adc #$1F
    sta $5E
    lda $0F
    adc #$00
    sta $5F
    jsr SearchPositionRecordsA
    cmp #$F4
    bne HorizontalMotionCheckOtherLimit
    jsr FindSlotWithFlag04
    bne HorizontalMotionNoRight
    jmp HorizontalMotionMapRightLimit
HorizontalMotionCheckOtherLimit:
    cmp #$F2 ; CONTROL_HORIZONTAL_MOTION_CHECK_OTHER_LIMIT
    bne HorizontalMotionMapRightLimit
HorizontalMotionNoRight:
    ldx #$00 ; CONTROL_HORIZONTAL_MOTION_NO_RIGHT
    rts
HorizontalMotionMapRightLimit:
    lda $03A2 ; CONTROL_HORIZONTAL_MOTION_MAP_RIGHT_LIMIT
    sec
    sbc $03EE
    tax
    lda $03A3
    sbc $03EF
    beq HorizontalMotionRightLimitReturn
    ldx #$FF
HorizontalMotionRightLimitReturn:
    rts
; Return the remaining vertical scroll range in X, capped at $FF when the
; high-byte difference is nonzero.
VerticalMotionMapBottomLimit:
    lda $03A8 ; CONTROL_VERTICAL_MOTION_MAP_BOTTOM_LIMIT
    sec
    sbc $03F0
    tax
    lda $03A9
    sbc $03F1
    beq VerticalMotionBottomLimitReturn
    ldx #$FF
VerticalMotionBottomLimitReturn:
    rts
.assert (* - BankStart) = $7B32, error, "bank 0 frame motion bounds end"
; Select one of two counters or use the supplied value, then format five
; decimal tile bytes with $40 for leading blanks. A second entry emits three.
FormatPendingPpuCounter:
    ldy $EA ; CONTROL_FORMAT_PENDING_PPU_COUNTER
    lda $42,y
    sta $03E0
    lda $44,y
    sta $03E1
FormatPendingPpuNumber5:
    lda #$05 ; CONTROL_FORMAT_PENDING_PPU_NUMBER5
    sta $E7
    jmp FormatPendingPpuDigits
FormatPendingPpuNumber3:
    lda #$03 ; CONTROL_FORMAT_PENDING_PPU_NUMBER3
    sta $E7
FormatPendingPpuDigits:
    lda #$20 ; CONTROL_FORMAT_PENDING_PPU_DIGITS
    sta $EA
    lda #$00
    sta $EB
    lda #$00
    sta $20
; Repeated subtraction yields the ten-thousands digit; the remaining digits
; come from divisions by 100 and 10.
FormatPendingPpuTenThousands:
    sec ; CONTROL_FORMAT_PENDING_PPU_TEN_THOUSANDS
    lda $03E0
    sbc #$10
    sta $03DE
    lda $03E1
    sbc #$27
    bcc FormatPendingPpuRemainder
    sta $03E1
    lda $03DE
    sta $03E0
    inc $20
    jmp FormatPendingPpuTenThousands
FormatPendingPpuRemainder:
    ldx $03E0 ; CONTROL_FORMAT_PENDING_PPU_REMAINDER
    ldy $03E1
    lda #$64
    jsr DivideUnsigned16By8
    stx $03E0
    sty $03E1
    ldx $03E0
    ldy #$00
    lda #$0A
    jsr DivideUnsigned16By8
    stx $21
    sty $22
    ldx $03E1
    ldy #$00
    lda #$0A
    jsr DivideUnsigned16By8
    stx $23
    sty $24
    ldx #$00
    ldy #$00
FormatPendingPpuDigitLoop:
    lda $20,y ; CONTROL_FORMAT_PENDING_PPU_DIGIT_LOOP
    bne FormatPendingPpuDigit
    cpx #$00
    bne FormatPendingPpuDigit
    cpy #$04
    beq FormatPendingPpuDigit
    lda #$40
    jmp FormatPendingPpuDigitStore
FormatPendingPpuDigit:
    inx
    clc
    adc #$30
FormatPendingPpuDigitStore:
    sta $20,y
    iny
    cpy #$05
    bne FormatPendingPpuDigitLoop
    lda $E7
    cmp #$05
    beq AdvancePendingPpuSourceReturn
    lda #$02
; Advance the 16-bit stream pointer by A, preserving carry into its high byte.
AdvancePendingPpuSource:
    clc ; CONTROL_ADVANCE_PENDING_PPU_SOURCE
    adc $EA
    sta $EA
    lda $EB
    adc #$00
    sta $EB
AdvancePendingPpuSourceReturn:
    rts
.assert (* - BankStart) = $7BD8, error, "bank 0 pending PPU number format end"

; Controller entry points choose one of two slot indices. This path requests
; action $24 unless the slot is absent or has bit $08 set in $0790.
ControllerAction24First:
    lda #$00 ; CONTROL_CONTROLLER_ACTION24_FIRST
    jmp ControllerAction24
ControllerAction24Second:
    lda #$01 ; CONTROL_CONTROLLER_ACTION24_SECOND
ControllerAction24:
    sta $3A ; CONTROL_CONTROLLER_ACTION24
    jsr RequireControllerActive
    ldx $3A
    lda $3C,x
    cmp #$FF
    beq ControllerAction24Return
    tay
    lda #$08
    and $0790,y
    bne ControllerAction24Return
    lda #$24
    sta $04F0,y
ControllerAction24Return:
    rts
; If $00 or $28 is nonzero, discard the caller return address so RTS returns
; from that caller. Preserve this stack-based early-exit convention.
RequireControllerActive:
    lda $00 ; CONTROL_REQUIRE_CONTROLLER_ACTIVE
    ora $28
    beq RequireControllerReturn
    pla
    pla
RequireControllerReturn:
    rts
; Request action $2D when neither controller state has $30 set and the
; selected slot does not have bit $10 set in $0790.
ControllerAction2DFirst:
    lda #$00 ; CONTROL_CONTROLLER_ACTION2D_FIRST
    jmp ControllerAction2D
ControllerAction2DSecond:
    lda #$01 ; CONTROL_CONTROLLER_ACTION2D_SECOND
ControllerAction2D:
    sta $3A ; CONTROL_CONTROLLER_ACTION2D
    jsr RequireControllerActive
    lda $038D
    ora $038E
    and #$30
    bne ControllerAction2DReturn
    ldx $3A
    lda $3C,x
    cmp #$FF
    beq ControllerAction2DReturn
    tay
    lda #$10
    and $0790,y
    bne ControllerAction2DReturn
    lda #$2D
    sta $04F0,y
ControllerAction2DReturn:
    rts
; In the special $3B state, a $60 controller combination updates mode flags.
; Otherwise request the configured action unless the selected slot blocks it.
ControllerConfiguredActionFirst:
    lda #$00 ; CONTROL_CONTROLLER_CONFIGURED_FIRST
    jmp ControllerConfiguredAction
ControllerConfiguredActionSecond:
    lda #$01 ; CONTROL_CONTROLLER_CONFIGURED_SECOND
ControllerConfiguredAction:
    sta $3A ; CONTROL_CONTROLLER_CONFIGURED_ACTION
    jsr RequireControllerActive
    lda $3B
    beq ControllerConfiguredSlot
    jsr RequireControllerMode
    lda $038D
    cmp #$60
    bne ControllerConfiguredSlot
    lda $01
    tay
    iny
    cpy #$10
    bcc ControllerModeSet
    ldy #$01
ControllerModeSet:
    sty $00 ; CONTROL_CONTROLLER_MODE_SET
    lda #$FF
    sta $08
    sta $58
ControllerActionReturn:
    rts
ControllerConfiguredSlot:
    ldx $3A ; CONTROL_CONTROLLER_CONFIGURED_SLOT
    lda $3C,x
    bmi ControllerActionReturn
    tay
    lda #$20
    and $0790,y
    bne ControllerActionReturn
    lda $15,x
    cmp #$FF
    beq ControllerActionReturn
    sta $04F0,y
    rts
; Toggle $28 when the game-state gates allow it. Pausing writes zero then
; the saved $03E8 value to the APU enable register.
ControllerTogglePause:
    lda $00 ; CONTROL_CONTROLLER_TOGGLE_PAUSE
    bne ControllerActionReturn
    lda $01
    beq ControllerActionReturn
    lda $18
    beq ControllerActionReturn
    lda #$00
    ldx $28
    bne ControllerStorePause
    lda #$00
    sta $4015
    lda $03E8
    sta $4015
    lda #$FF
ControllerStorePause:
    sta $28 ; CONTROL_CONTROLLER_STORE_PAUSE
    rts
; These paired entry points select controller 0 or 1, then select one of four
; signed X/Y delta pairs. Horizontal paths also update slot flag $10.
ControllerPositiveYFirst:
    ldy #$00 ; CONTROL_CONTROLLER_POSITIVE_Y_FIRST
    jmp ControllerPositiveY
ControllerPositiveYSecond:
    ldy #$01 ; CONTROL_CONTROLLER_POSITIVE_Y_SECOND
ControllerPositiveY:
    lda #$06 ; CONTROL_CONTROLLER_POSITIVE_Y
    ldx #$02
    jmp ApplyControllerDelta
ControllerNegativeXFirst:
    ldy #$00 ; CONTROL_CONTROLLER_NEGATIVE_X_FIRST
    jmp ControllerNegativeX
ControllerNegativeXSecond:
    ldy #$01 ; CONTROL_CONTROLLER_NEGATIVE_X_SECOND
ControllerNegativeX:
    lda $3C,y ; CONTROL_CONTROLLER_NEGATIVE_X
    bmi ControllerNegativeXApply
    tax
    lda $0630,x
    ora #$10
    sta $0630,x
ControllerNegativeXApply:
    lda #$00 ; CONTROL_CONTROLLER_NEGATIVE_X_APPLY
    ldx #$00
    jmp ApplyControllerDelta
ControllerPositiveXFirst:
    ldy #$00 ; CONTROL_CONTROLLER_POSITIVE_X_FIRST
    jmp ControllerPositiveX
ControllerPositiveXSecond:
    ldy #$01 ; CONTROL_CONTROLLER_POSITIVE_X_SECOND
ControllerPositiveX:
    lda $3C,y ; CONTROL_CONTROLLER_POSITIVE_X
    bmi ControllerPositiveXApply
    tax
    lda $0630,x
    and #$EF
    sta $0630,x
ControllerPositiveXApply:
    lda #$02 ; CONTROL_CONTROLLER_POSITIVE_X_APPLY
    ldx #$00
    jmp ApplyControllerDelta
ControllerNegativeYFirst:
    ldy #$00 ; CONTROL_CONTROLLER_NEGATIVE_Y_FIRST
    jmp ControllerNegativeY
ControllerNegativeYSecond:
    ldy #$01 ; CONTROL_CONTROLLER_NEGATIVE_Y_SECOND
ControllerNegativeY:
    lda #$04 ; CONTROL_CONTROLLER_NEGATIVE_Y
    ldx #$01
; Add the selected signed deltas to $3E/$40. The original discards each
; addition independently when its 6502 overflow flag is set.
ApplyControllerDelta:
    sta $39 ; CONTROL_APPLY_CONTROLLER_DELTA
    sty $3A
    stx $17
    jsr RequireControllerActive
    ldy $39
    ldx $3A
    lda $3E,x
    clc
    adc ControllerDeltas,y
    bvs ApplyControllerDeltaY
    sta $3E,x
ApplyControllerDeltaY:
    lda $40,x ; CONTROL_APPLY_CONTROLLER_DELTA_Y
    clc
    adc ControllerDeltas + 1,y
    bvs ApplyControllerDeltaFlags
    sta $40,x
ApplyControllerDeltaFlags:
    lda $17 ; CONTROL_APPLY_CONTROLLER_DELTA_FLAGS
    beq ApplyControllerDeltaReturn
    lda $3C,x
    bmi ApplyControllerDeltaReturn
    tax
    lda #$FF
    sta $05A0,x
    lda $17
    cmp #$02
    bne ApplyControllerDeltaReturn
    lda #$40
    and $0790,x
    bne ApplyControllerDeltaReturn
    lda #$36
    sta $04F0,x
ApplyControllerDeltaReturn:
    rts ; CONTROL_APPLY_CONTROLLER_DELTA_RETURN
.assert (* - BankStart) = $7D29, error, "bank 0 controller handlers end"
; Opcode $18 restarts voice 4 with the same sound pointer used by $49.
ScriptOp18:
    lda #$04                     ; CONTROL_SCRIPT_OP18
    jsr StopAudioVoice
    ldx #$C8
    ldy #$26
    lda #$04
    jsr StartAudioVoice
    rts
.assert (* - BankStart) = $7D38, error, "bank 0 script handler opcode $18"

; A zero $01 discards the caller return address and returns from that caller.
RequireControllerMode:
    lda $01 ; CONTROL_REQUIRE_CONTROLLER_MODE
    bne RequireControllerModeReturn
    pla
    pla
RequireControllerModeReturn:
    rts
.assert (* - BankStart) = $7D3F, error, "bank 0 controller mode gate end"

    .incbin "bank0_fd3f_fd88.bin"
    BankScriptNativeCall
.assert (* - BankStart) = $7DA7, error, "bank 0 native script call end"
ScriptRecordLengths:
    ScriptTable 0
.assert (* - BankStart) = $7E6C, error, "bank 0 common helpers offset"
    BankHelpers
.assert (* - BankStart) = $7FB3, error, "bank 0 tail offset"
    BankTail $03C0, $03C1, "bank0_fff4_fffa.bin"
.assert (* - BankStart) = $8000, error, "bank 0 size"
.endscope

.segment "PRG1"
.scope Bank1
BankStart:
    .incbin "bank1_8000_aca0.bin"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordACA0:
    SlotCompactRecord $B725, $00 ; CONTROL_RUNTIME_RECORD_ACA0
.assert (* - BankStart) = $2CA3, error, "bank 1 runtime records $ACA0 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeACA3:
    SlotRuntimeRecord $BF27, (CandidateAD45 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_ACA3
.assert (* - BankStart) = $2CAC, error, "bank 1 slot record ACA3 end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordACAC:
    SlotRuntimeRecord $FFFF, (RuntimeScriptADDD - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_RUNTIME_RECORD_ACAC
RuntimeRecordACB5:
    SlotRuntimeRecord $FFFF, (RuntimeScriptAF84 - BankStart), $00, $FF, $00, $00, $00
RuntimeRecordACBE:
    SlotRuntimeRecord $FFFF, (RuntimeScriptB191 - BankStart), $13, $FF, $00, $00, $00
RuntimeRecordACC7:
    SlotRuntimeRecord $FFFF, (RuntimeScriptAFBA - BankStart), $00, $FF, $00, $00, $00
.assert (* - BankStart) = $2CD0, error, "bank 1 runtime records $ACAC end"
; Observed in zero mode; fields gated by $FFFF may be skipped.
InteractionRecordACD0:
    SlotRuntimeRecord $FFFF, (InteractionScriptB04C - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_INTERACTION_RECORD_ACD0
.assert (* - BankStart) = $2CD9, error, "bank 1 interaction record $ACD0 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
DirectedRecordACD9:
    SlotRuntimeRecord $FFFF, (DirectedScriptB157 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_DIRECTED_RECORD_ACD9
.assert (* - BankStart) = $2CE2, error, "bank 1 directed record $ACD9 end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordACE2:
    SlotRuntimeRecord $FFFF, (RuntimeScriptB12E - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_RUNTIME_RECORD_ACE2
RuntimeRecordACEB:
    SlotRuntimeRecord $FFFF, (RuntimeScriptAD93 - BankStart), $23, $FF, $00, $00, $00
RuntimeRecordACF4:
    SlotRuntimeRecord $BF27, $FFFF, $40, $FF, $00, $00, $00
.assert (* - BankStart) = $2CFD, error, "bank 1 runtime records $ACE2 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
DirectedRecordACFD:
    SlotRuntimeRecord $BFAB, $FFFF, $40, $FF, $00, $00, $00 ; CONTROL_DIRECTED_RECORD_ACFD
.assert (* - BankStart) = $2D06, error, "bank 1 directed record $ACFD end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordAD06:
    SlotRuntimeRecord $B745, $FFFF, $23, $FF, $00, $00, $00 ; CONTROL_RUNTIME_RECORD_AD06
.assert (* - BankStart) = $2D0F, error, "bank 1 runtime records $AD06 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordAD0F:
    SlotRuntimeRecord $B715, $FFFF, $23, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_AD0F
.assert (* - BankStart) = $2D18, error, "bank 1 sweep record $AD0F end"
; Resource pointer read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordAD18Resource:
    .word $B725 ; CONTROL_PARTIAL_RESOURCE_AD18
.assert (* - BankStart) = $2D1A, error, "bank 1 partial record $AD18 end"
    .incbin "bank1_ad1a_ad1b.bin"
; In the observed zero mode, $FF suppresses installing a script pointer.
ObservedRecordAD18ScriptSentinel:
    .byte $FF ; CONTROL_AD18_SCRIPT_SENTINEL
.assert (* - BankStart) = $2D1C, error, "bank 1 record $AD18 script sentinel end"
; Mode-specific flags and fields read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordAD18Fields:
    .byte $00 ; CONTROL_PARTIAL_FIELDS_AD18
.assert (* - BankStart) = $2D1D, error, "bank 1 partial record $AD1C end"
; The zero-mode loader reads the four visual fields after the flags byte.
ObservedRecordAD18VisualFields:
    .byte $FF, $00, $00, $00 ; CONTROL_AD18_VISUAL_FIELDS
.assert (* - BankStart) = $2D21, error, "bank 1 record $AD18 visual fields end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
DirectedRecordAD21:
    SlotRuntimeRecord $B71E, $FFFF, $13, $FF, $00, $00, $00 ; CONTROL_DIRECTED_RECORD_AD21
.assert (* - BankStart) = $2D2A, error, "bank 1 directed record $AD21 end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordAD2A:
    SlotRuntimeRecord $BFF1, $FFFF, $23, $FF, $00, $00, $00 ; CONTROL_RUNTIME_RECORD_AD2A
RuntimeRecordAD33:
    SlotRuntimeRecord $BFF1, $FFFF, $23, $FF, $00, $00, $00
.assert (* - BankStart) = $2D3C, error, "bank 1 runtime records $AD2A end"
; Candidate direct-record target of the script at $B391. The resource pointer
; is read when the loader returns through this record; mode-dependent bytes stay local.
CandidateDirectRecordAD3CResource:
    .word $BFD3 ; CONTROL_AD3C_RESOURCE
.assert (* - BankStart) = $2D3E, error, "bank 1 direct record $AD3C resource end"
    .incbin "bank1_ad3e_ad45.bin"
; Candidate script path; object role and execution remain unverified.
CandidateAD45:
    BogusSetDispatchCounter $8F ; CONTROL_BOGUS_AD45
    BogusBranchIfMatchingSlotReady (BankStart + $398E), $01, $01, $00
    BogusReloadSlotRecordMode1 $06
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual CandidateAD58, $000F
    BogusReloadSlotRecordMode1 $08
CandidateAD58:
    BogusLoadSlotValueArray $26
    BogusSetSlot0520 $00
    BogusSetSlotValue $0024
    BogusStoreSlotValueArray $27
    BogusSetSlotValue $003C
    BogusStoreSlotValueArray $28
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueAtLeast CandidateAD83, $0005
    BogusSetSlotValue $0030
    BogusStoreSlotValueArray $27
    BogusSetSlotValue $0048
    BogusStoreSlotValueArray $28
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual CandidateAD83, $0004
    BogusMarkMatchingSlots $08, $01, $08, $00
CandidateAD83:
    BogusSetSlotAssociation $00
    BogusClearSelected3E
    BogusClearSelected40
    BogusSetSlot0640Pair $01, $00
    BogusSetSelectedState15 $36
    BogusInitializeOtherSlotAbsolute $03, $FF, $C0, $00
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $2D93, error, "bank 1 candidate script AD45 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptAD93:
    BogusSetDispatchCounter $0A ; CONTROL_RUNTIME_SCRIPT_AD93
RuntimeScriptAD95:
    BogusSetSlot0670Pair $04, $40
RuntimeScriptAD98:
    BogusSetSlot07F0 $14
RuntimeScriptAD9A:
    BogusClearSlot0790Bits $BF
RuntimeScriptAD9C:
    BogusSetSlotC0 $FF
RuntimeScriptAD9E:
    BogusSetSlot0640Pair $01, $00
RuntimeScriptADA1:
    BogusFindLinkedSlot
RuntimeScriptADA2:
    BogusBranchIfSlotValueNotEqual (BankStart + $2DAD), $FFFF
RuntimeScriptADA7:
    BogusLoadSlotRecordAtPointer $2D06
RuntimeScriptADAA:
    BogusJumpBank1 RuntimeScriptADB0
.assert (* - BankStart) = $2DAD, error, "bank 1 runtime script $AD93 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptADAD:
    BogusLoadSlotRecordAtPointer $2D0F ; CONTROL_EXTENDED_SCRIPT_ADAD
.assert (* - BankStart) = $2DB0, error, "bank 1 extended script $ADAD end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptADB0:
    BogusApplyAndClearSelected3E
RuntimeScriptADB1:
    BogusSetDispatchCounter $04 ; CONTROL_RUNTIME_SCRIPT_ADB0
RuntimeScriptADB3:
    BogusBranchIfSlotFieldsWithin RuntimeScriptADC5, $07, $FF
RuntimeScriptADB8:
    BogusSetSlot0360 $06
RuntimeScriptADBA:
    BogusBranchIfSelectedFlags (BankStart + $2DD1), $40
RuntimeScriptADBE:
    BogusSetDispatchCounter $02
RuntimeScriptADC0:
    BogusLoadSlotValueArray $27
RuntimeScriptADC2:
    BogusSetSlot05F0Pair $00, $FF
RuntimeScriptADC5:
    BogusBranchIfSlot0360AtMost (BankStart + $2DCF), $01
RuntimeScriptADC9:
    BogusApplyAndClearSelected3E
RuntimeScriptADCA:
    BogusBranchIfSlot0620Bit10 RuntimeScriptADB0
.assert (* - BankStart) = $2DCD, error, "bank 1 runtime script $ADB0 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptADCD:
    BogusLoadRecordAndClearSavedState $12 ; CONTROL_SUCCESSOR_SCRIPT_ADCD
SuccessorScriptADCF:
    BogusLoadRecordAndClearSavedState $3F
SuccessorScriptADD1:
    BogusSetDispatchCounter $02
SuccessorScriptADD3:
    BogusLoadSlotValueArray $28
SuccessorScriptADD5:
    BogusSetSlot05F0Pair $00, $FF
SuccessorScriptADD8:
    BogusBranchIfSlot0620Bit10 RuntimeScriptADB0
SuccessorScriptADDB:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $2DDD, error, "bank 1 candidate successor $ADCD end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptADDD:
    BogusSetDispatchCounter $0B ; CONTROL_RUNTIME_SCRIPT_ADDD
RuntimeScriptADDF:
    BogusLoadSlotValueArray $29
RuntimeScriptADE1:
    BogusSetSlotMode $00
RuntimeScriptADE3:
    BogusSetSlotMode $02
RuntimeScriptADE5:
    BogusSubtractSlotPriorityFromField0520
RuntimeScriptADE6:
    BogusReadSlotValue $01
RuntimeScriptADE8:
    BogusStoreSlotValueArray $26
RuntimeScriptADEA:
    BogusReadSlotValue $24
RuntimeScriptADEC:
    BogusBranchIfSlotValueEqual (BankStart + $2E7C), $07, $00
RuntimeScriptADF1:
    BogusBranchIfSlotValueEqual (BankStart + $2EB9), $0F, $00
RuntimeScriptADF6:
    BogusLoadSlotRecord $03, $FF
RuntimeScriptADF9:
    BogusMarkRelatedSlotAtDepth $18, $01
RuntimeScriptADFC:
    BogusSetDispatchCounter $05
RuntimeScriptADFE:
    BogusBranchIfSlotD0BitsClear RuntimeScriptAE06, $80
.assert (* - BankStart) = $2E02, error, "bank 1 runtime script $ADDD end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAE02:
    BogusSetSlotC0 $FF ; CONTROL_SUCCESSOR_SCRIPT_AE02
SuccessorScriptAE04:
    BogusClearSlotD0Bits $80
.assert (* - BankStart) = $2E06, error, "bank 1 candidate successor $AE02 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptAE06:
    BogusSetDispatchCounter $02 ; CONTROL_RUNTIME_SCRIPT_AE06
RuntimeScriptAE08:
    BogusReadSlotValue $24
RuntimeScriptAE0A:
    BogusLookupSlotValue
.assert (* - BankStart) = $2E0B, error, "bank 1 runtime script $AE06 end"
; $95 compares each value to the slot value and branches to its target.
; The two-byte zero target terminates the inline table.
    BogusLookupCaseBank1 SuccessorScriptAE2F, $0001 ; CONTROL_SUCCESSOR_LOOKUP_AE0B
    BogusLookupCaseBank1 SuccessorScriptAEA6, $0004
    BogusLookupCaseBank1 SuccessorScriptAF59, $0005
    BogusLookupCaseBank1 RuntimeScriptAE51, $0006
    BogusLookupEnd
.assert (* - BankStart) = $2E1D, error, "bank 1 successor lookup $AE0B end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAE1D:
    BogusSetDispatchCounter $06 ; CONTROL_SUCCESSOR_SCRIPT_AE1D
SuccessorScriptAE1F:
    BogusReadSlotValue $01
SuccessorScriptAE21:
    BogusMaskSlotValue $0003
SuccessorScriptAE24:
    BogusBranchIfSlotValueEqual SuccessorScriptAE2F, $00, $00
SuccessorScriptAE29:
    BogusSetLinkedSlotFieldsC0 $18, $00
SuccessorScriptAE2C:
    BogusJumpBank1 SuccessorScriptAE41
SuccessorScriptAE2F:
    BogusSetDispatchCounter $86
SuccessorScriptAE31:
    BogusSetLinkedSlotFieldsC0 $60, $A0
SuccessorScriptAE34:
    BogusLoadSlotValueArray $27
SuccessorScriptAE36:
    BogusSetSlot05F0Pair $00, $FF
SuccessorScriptAE39:
    BogusBranchIfAbsSlot0700Below SuccessorScriptAE48, $18
SuccessorScriptAE3D:
    BogusBranchIfSlot0520AtMost SuccessorScriptAEF1, $00
SuccessorScriptAE41:
    BogusRestartVoice4 $284D
SuccessorScriptAE44:
    BogusWait $06
SuccessorScriptAE46:
    BogusLoadRecordAndClearSavedState $12
SuccessorScriptAE48:
    BogusSetSlotFields80 $00, $FF
SuccessorScriptAE4B:
    BogusSetSlotFields40Signed $60, $00
SuccessorScriptAE4E:
    BogusJumpBank1 SuccessorScriptAE3D
.assert (* - BankStart) = $2E51, error, "bank 1 candidate successor $AE1D end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptAE51:
    BogusSetDispatchCounter $82 ; CONTROL_RUNTIME_SCRIPT_AE51
RuntimeScriptAE53:
    BogusSetSlot05F0Pair $40, $FF
RuntimeScriptAE56:
    BogusRestartVoice4 $2724
RuntimeScriptAE59:
    BogusSetLinkedSlotFieldsC0 $60, $D0
RuntimeScriptAE5C:
    BogusBranchIfAbsSlot0700Below (BankStart + $2E48), $18
RuntimeScriptAE60:
    BogusAddSlotFields00 $00, $F0
RuntimeScriptAE63:
    BogusAddSlotFields00 $00, $F0
RuntimeScriptAE66:
    BogusAddSlotFields00 $00, $F0
RuntimeScriptAE69:
    BogusAddSlotFields00 $00, $F0
RuntimeScriptAE6C:
    BogusAddSlotFields00 $00, $F0
RuntimeScriptAE6F:
    BogusLoadSlotValueArray $27
RuntimeScriptAE71:
    BogusSetSlot05F0Pair $00, $FF
RuntimeScriptAE74:
    BogusBranchIfSlot0520AtMost (BankStart + $2EF1), $00
RuntimeScriptAE78:
    BogusWait $06
RuntimeScriptAE7A:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $2E7C, error, "bank 1 runtime script $AE51 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAE7C:
    BogusSetDispatchCounter $85 ; CONTROL_SUCCESSOR_SCRIPT_AE7C
SuccessorScriptAE7E:
    BogusSetSlot05F0Pair $FF, $7E
SuccessorScriptAE81:
    BogusLoadSlotRecord $24, $01
SuccessorScriptAE84:
    BogusSetSlotFields80 $FF, $82
SuccessorScriptAE87:
    BogusLoadSlotValueArray $3C
SuccessorScriptAE89:
    BogusSetSlotMode $00
SuccessorScriptAE8B:
    BogusClearSlot0790Bits $11
SuccessorScriptAE8D:
    BogusSetSlotFields80 $FF, $82
SuccessorScriptAE90:
    BogusApplyAndClearSelected3E
.assert (* - BankStart) = $2E91, error, "bank 1 candidate successor $AE7C end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptAE91:
    BogusSetSlotFields80 $FF, $82 ; CONTROL_LONG_SCRIPT_AE91
LongScriptAE94:
    BogusSetSlotFields80 $FF, $82
LongScriptAE97:
    BogusApplyAndClearSelected3E
LongScriptAE98:
    BogusSetSlotFields80 $FF, $82
LongScriptAE9B:
    BogusApplyAndClearSelected3E
LongScriptAE9C:
    BogusBranchIfSlotFieldsWithin LongScriptAEA4, $FF, $10
LongScriptAEA1:
    BogusJumpBank1 LongScriptAE9B
LongScriptAEA4:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $2EA6, error, "bank 1 long-run script $AE91 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAEA6:
    BogusSetSlotC0 $FF ; CONTROL_SUCCESSOR_SCRIPT_AEA6
SuccessorScriptAEA8:
    BogusLoadSlotValueArray $3C
SuccessorScriptAEAA:
    BogusSetSlotMode $00
SuccessorScriptAEAC:
    BogusClearSlotD0Bits $80
SuccessorScriptAEAE:
    BogusRestartVoice4 $273C
SuccessorScriptAEB1:
    BogusWait $08
SuccessorScriptAEB3:
    BogusBranchIfSlot0520AtMost SuccessorScriptAEF1, $00
SuccessorScriptAEB7:
    BogusLoadRecordAndClearSavedState $12
SuccessorScriptAEB9:
    BogusAdjustSlotBounds $00, $01
SuccessorScriptAEBC:
    BogusSetSlotMode $02
SuccessorScriptAEBE:
    BogusLoadRecordAndClearSavedState $12
SuccessorScriptAEC0:
    BogusSetDispatchCounter $85
SuccessorScriptAEC2:
    BogusSetSlot0790Bits $FF
SuccessorScriptAEC4:
    BogusSetSlotFields80 $00, $00
SuccessorScriptAEC7:
    BogusSetSlotC0 $00
SuccessorScriptAEC9:
    BogusSetSlot0640Pair $00, $00
SuccessorScriptAECC:
    BogusSetVoicePointers $2C88, $2C97, $2890, $0000
SuccessorScriptAED5:
    BogusInitializeOtherSlotRelative $54, $00, $F8, $00
SuccessorScriptAEDA:
    BogusInitializeOtherSlotRelative $54, $08, $F8, $00
SuccessorScriptAEDF:
    BogusInitializeOtherSlotRelative $54, $00, $08, $00
SuccessorScriptAEE4:
    BogusInitializeOtherSlotRelative $54, $08, $08, $00
SuccessorScriptAEE9:
    BogusWait $05
SuccessorScriptAEEB:
    BogusLoadSlotRecordAtPointer $3936
.assert (* - BankStart) = $2EEE, error, "bank 1 candidate successor $AEA6 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptAEEE:
    BogusJumpBank1 LongScriptAF2C ; CONTROL_EXTENDED_SCRIPT_AEEE
.assert (* - BankStart) = $2EF1, error, "bank 1 extended script $AEEE end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAEF1:
    BogusSetSlot0790Bits $FF ; CONTROL_SUCCESSOR_SCRIPT_AEF1
SuccessorScriptAEF3:
    BogusSetSlotFields80 $00, $00
SuccessorScriptAEF6:
    BogusSetSlot0640Pair $00, $00
SuccessorScriptAEF9:
    BogusLoadSlotRecordAtPointer $2D18
.assert (* - BankStart) = $2EFC, error, "bank 1 candidate successor $AEF1 end"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptAEFC:
    BogusSetSlot07F0 $80 ; CONTROL_INTERACTION_SCRIPT_AEFC
InteractionScriptAEFE:
    BogusJumpBank1 InteractionScriptAF05
.assert (* - BankStart) = $2F01, error, "bank 1 interaction script $AEFC end"
    .incbin "bank1_af01_af05.bin"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptAF05:
    BogusSetSlotFields80 $00, $82 ; CONTROL_INTERACTION_SCRIPT_AF05
InteractionScriptAF08:
    BogusSetSlotMode $FF
InteractionScriptAF0A:
    BogusMarkRelatedSlotAtDepth $1A, $01
InteractionScriptAF0D:
    BogusSetVoicePointers $2C88, $2C97, $0000, $0000
InteractionScriptAF16:
    BogusMarkRelatedSlotAtDepth $1A, $02
InteractionScriptAF19:
    BogusSetSlotFields80 $00, $82
InteractionScriptAF1C:
    BogusMarkRelatedSlotAtDepth $1A, $03
InteractionScriptAF1F:
    BogusSetSlotFields80 $00, $82
InteractionScriptAF22:
    BogusMarkRelatedSlotAtDepth $1A, $04
InteractionScriptAF25:
    BogusSetSlotFields80 $00, $82
InteractionScriptAF28:
    BogusBranchIfSlotB0AtMost InteractionScriptAF28, $DC
.assert (* - BankStart) = $2F2C, error, "bank 1 interaction script $AF05 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptAF2C:
    BogusSetDispatchCounter $82 ; CONTROL_LONG_SCRIPT_AF2C
LongScriptAF2E:
    BogusSetSlotC0 $00
LongScriptAF30:
    BogusSetSlotFields80 $00, $00
LongScriptAF33:
    BogusLoadSlotRecordAtPointer $3936
LongScriptAF36:
    BogusBranchIfSelectedFlags LongScriptAF41, $E0
LongScriptAF3A:
    BogusBranchIfAudioVoiceActive LongScriptAF36, $01, $01, $01, $01
LongScriptAF41:
    BogusSetVoicePointers $0000, $0000, $0000, $0000
LongScriptAF4A:
    BogusReadSlotValue $0F
LongScriptAF4C:
    BogusStoreSlotValueArray $3A
LongScriptAF4E:
    BogusCallNativeEncoded $B51B
LongScriptAF51:
    BogusSetBackgroundPalettePointer $C83E
LongScriptAF54:
    BogusSetSpritePalettePointer $C83E
LongScriptAF57:
    BogusSetMainState $11
.assert (* - BankStart) = $2F59, error, "bank 1 long-run script $AF2C end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAF59:
    BogusSetDispatchCounter $02 ; CONTROL_SUCCESSOR_SCRIPT_AF59
SuccessorScriptAF5B:
    BogusBranchIfSlot0760Equal SuccessorScriptAF61, $14
SuccessorScriptAF5F:
    BogusLoadRecordAndClearSavedState $48
SuccessorScriptAF61:
    BogusWait $01
.assert (* - BankStart) = $2F63, error, "bank 1 candidate successor $AF59 end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptAF63:
    BogusSelectRelativeSlotAndYield $00, $07, $23, $14, $00 ; CONTROL_PATH_SCRIPT_AF63
.assert (* - BankStart) = $2F69, error, "bank 1 candidate successor $AF63 end"
; Possible resume paths; scheduling and entry conditions remain unverified.
ResumeScriptAF69:
    BogusSetSlot0360 $3C ; CONTROL_RESUME_SCRIPT_AF69
ResumeScriptAF6B:
    BogusBranchIfSlot06D0Present ResumeScriptAF71
ResumeScriptAF6E:
    BogusJumpBank1 ResumeScriptAF7A
ResumeScriptAF71:
    BogusBranchIfSecondWorldOffsetAtMost ResumeScriptAF7A, $0040
ResumeScriptAF76:
    BogusBranchIfSlot0360Above ResumeScriptAF6B, $00
ResumeScriptAF7A:
    BogusClearSelected3E
ResumeScriptAF7B:
    BogusClearSelected40
ResumeScriptAF7C:
    BogusInitializeSlotMotionFields
ResumeScriptAF7D:
    BogusSetSlotFields80 $00, $00
ResumeScriptAF80:
    BogusSetSlotMode $02
ResumeScriptAF82:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $2F84, error, "bank 1 candidate successor $AF69 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptAF84:
    BogusSetDispatchCounter $0A ; CONTROL_RUNTIME_SCRIPT_AF84
RuntimeScriptAF86:
    BogusLoadSlotValueArray $29
RuntimeScriptAF88:
    BogusSetSlotMode $00
RuntimeScriptAF8A:
    BogusSetSlotMode $02
RuntimeScriptAF8C:
    BogusClearSlotD0Bits $80
RuntimeScriptAF8E:
    BogusSetSlotC0 $FF
RuntimeScriptAF90:
    BogusClearSlot0790Bits $BF
RuntimeScriptAF92:
    BogusSetSlot05F0Pair $FF, $60
RuntimeScriptAF95:
    BogusFindLinkedSlot
RuntimeScriptAF96:
    BogusBranchIfSlotValueNotEqual RuntimeScriptAF9E, $FFFF
RuntimeScriptAF9B:
    BogusLoadSlotRecordAtPointer $2D2A
RuntimeScriptAF9E:
    BogusApplyAndClearSelected3E
RuntimeScriptAF9F:
    BogusSetDispatchCounter $08
RuntimeScriptAFA1:
    BogusBranchIfRemainingVerticalOffsetAtMost (BankStart + $2EF1), $0004
RuntimeScriptAFA6:
    BogusReadSlotValue $AA
RuntimeScriptAFA8:
    BogusBranchIfSlotValueNotEqual RuntimeScriptAFB2, $0008
RuntimeScriptAFAD:
    BogusBranchIfRemainingVerticalOffsetAtMost (BankStart + $2EC0), $0028
RuntimeScriptAFB2:
    BogusBranchIfSlot0620Bit10Clear RuntimeScriptAF9E
RuntimeScriptAFB5:
    BogusStartVoice4 $281D
RuntimeScriptAFB8:
    BogusLoadRecordAndClearSavedState $48
RuntimeScriptAFBA:
    BogusBranchIfSlot0620Bit10 RuntimeScriptAFED
.assert (* - BankStart) = $2FBD, error, "bank 1 runtime script $AF84 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptAFBD:
    BogusBranchIfSlotD0Bits RuntimeScriptAFED, $80 ; CONTROL_SUCCESSOR_SCRIPT_AFBD
SuccessorScriptAFC1:
    BogusBranchIfPositiveOffsetProbe SuccessorScriptAFC6, $05
SuccessorScriptAFC5:
    BogusRestoreSavedScriptAndSlotFlags
SuccessorScriptAFC6:
    BogusApplyAndClearSelected3E
.assert (* - BankStart) = $2FC7, error, "bank 1 candidate successor $AFBD end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptAFC7:
    BogusBranchIfSlot0620Bit10 RuntimeScriptAFED
LongScriptAFCA:
    BogusBranchIfSelectedFlagsClear RuntimeScriptAF9E, $80 ; CONTROL_LONG_SCRIPT_AFC7
LongScriptAFCE:
    BogusApplyAndClearSelected3E
LongScriptAFCF:
    BogusBranchIfSlot0620Bit10 RuntimeScriptAFED
.assert (* - BankStart) = $2FD2, error, "bank 1 long-run script $AFC7 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptAFD2:
    BogusBranchIfSelectedFlagsClear RuntimeScriptAF9E, $80 ; CONTROL_EXTENDED_SCRIPT_AFD2
ExtendedScriptAFD6:
    BogusApplyAndClearSelected3E
.assert (* - BankStart) = $2FD7, error, "bank 1 extended script $AFD2 end"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptAFD7:
    BogusBranchIfSlot0620Bit10 RuntimeScriptAFED
InteractionScriptAFDA:
    BogusBranchIfSelectedFlagsClear RuntimeScriptAF9E, $80 ; CONTROL_INTERACTION_SCRIPT_AFD7
.assert (* - BankStart) = $2FDE, error, "bank 1 interaction script $AFD7 end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptAFDE:
    BogusApplyAndClearSelected3E ; CONTROL_PATH_SCRIPT_AFDE
.assert (* - BankStart) = $2FDF, error, "bank 1 candidate successor $AFDE end"
; Command entries observed during the directed-input exploration.
DirectedScriptAFDF:
    BogusBranchIfSlot0620Bit10 RuntimeScriptAFED ; CONTROL_DIRECTED_SCRIPT_AFDF
.assert (* - BankStart) = $2FE2, error, "bank 1 directed script $AFDF end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptAFE2:
    BogusBranchIfSelectedFlagsClear RuntimeScriptAF9E, $80 ; CONTROL_EXPANDED_SCRIPT_AFE2
ExpandedScriptAFE6:
    BogusApplyAndClearSelected3E
ExpandedScriptAFE7:
    BogusBranchIfSlot0620Bit10 RuntimeScriptAFED
ExpandedScriptAFEA:
    BogusJumpBank1 RuntimeScriptAF9E
.assert (* - BankStart) = $2FED, error, "bank 1 candidate successor $AFE2 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptAFED:
    BogusSetDispatchCounter $0C ; CONTROL_RUNTIME_SCRIPT_AFED
RuntimeScriptAFEF:
    BogusClearSlot0790Bits $B7
RuntimeScriptAFF1:
    BogusClearSlotD0Bits $80
RuntimeScriptAFF3:
    BogusBranchIfSelectedFlags (BankStart + $3031), $04
RuntimeScriptAFF7:
    BogusFindLinkedSlot
RuntimeScriptAFF8:
    BogusBranchIfSlotValueNotEqual RuntimeScriptB000, $FFFF
RuntimeScriptAFFD:
    BogusLoadSlotRecordAtPointer $2D33
RuntimeScriptB000:
    BogusSetSlot0360 $03
RuntimeScriptB002:
    BogusRestartVoice4 $274E
RuntimeScriptB005:
    BogusLoadSlotValueArray $3C
RuntimeScriptB007:
    BogusSetSlotMode $00
RuntimeScriptB009:
    BogusSetSlotFields80 $FF, $A0
RuntimeScriptB00C:
    BogusSetDispatchCounter $85
RuntimeScriptB00E:
    BogusSetSlotFields80 $FF, $A0
RuntimeScriptB011:
    BogusApplyAndClearSelected3E
RuntimeScriptB012:
    BogusBranchIfSelectedFlagsClear RuntimeScriptB01D, $80
RuntimeScriptB016:
    BogusBranchIfSlot0360AtMost RuntimeScriptB022, $00
RuntimeScriptB01A:
    BogusJumpBank1 RuntimeScriptB00C
RuntimeScriptB01D:
    BogusSetSlotFields80 $FF, $E0
RuntimeScriptB020:
    BogusLoadRecordAndClearSavedState $12
RuntimeScriptB022:
    BogusSetDispatchCounter $82
RuntimeScriptB024:
    BogusSetSlotFields80 $FF, $B0
RuntimeScriptB027:
    BogusApplyAndClearSelected3E
RuntimeScriptB028:
    BogusSetDispatchCounter $82
RuntimeScriptB02A:
    BogusSetSlotFields80 $FF, $C0
RuntimeScriptB02D:
    BogusApplyAndClearSelected3E
RuntimeScriptB02E:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $3030, error, "bank 1 runtime script $AFED end"
    .incbin "bank1_b030_b031.bin"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB031:
    BogusBranchIfSelectedFlags RuntimeScriptAFF7, $03 ; CONTROL_SUCCESSOR_SCRIPT_B031
SuccessorScriptB035:
    BogusFindLinkedSlot
SuccessorScriptB036:
    BogusBranchIfSlotValueNotEqual SuccessorScriptB03E, $FFFF
SuccessorScriptB03B:
    BogusLoadSlotRecordAtPointer $2D33
SuccessorScriptB03E:
    BogusSetDispatchCounter $03
SuccessorScriptB040:
    BogusLoadSlotValueArray $3C
SuccessorScriptB042:
    BogusSetSlotMode $00
SuccessorScriptB044:
    BogusSetSlotFields80 $FF, $E0
SuccessorScriptB047:
    BogusApplyAndClearSelected3E
.assert (* - BankStart) = $3048, error, "bank 1 candidate successor $B031 end"
; Command entries observed during the directed-input exploration.
DirectedScriptB048:
    BogusApplyAndClearSelected3E
DirectedScriptB049:
    BogusApplyAndClearSelected3E
DirectedScriptB04A:
    BogusLoadRecordAndClearSavedState $12 ; CONTROL_DIRECTED_SCRIPT_B048
.assert (* - BankStart) = $304C, error, "bank 1 directed script $B048 end"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptB04C:
    BogusSetDispatchCounter $89 ; CONTROL_INTERACTION_SCRIPT_B04C
InteractionScriptB04E:
    BogusStoreSlotValueArray $FF
InteractionScriptB050:
    BogusBranchIfSlotCoordinatesA3 InteractionScriptB06A, $10, $0C
InteractionScriptB055:
    BogusFindLinkedSlot
InteractionScriptB056:
    BogusBranchIfSlotValueNotEqual (BankStart + $30C0), $FFFF
InteractionScriptB05B:
    BogusReadSlotValue $0F
InteractionScriptB05D:
    BogusBranchIfSlotValueEqual (BankStart + $3080), $0F, $00
InteractionScriptB062:
    BogusBranchIfSlotFieldsWithin InteractionScriptB06A, $20, $FF
InteractionScriptB067:
    BogusJumpBank1 InteractionScriptB074
InteractionScriptB06A:
    BogusBranchIfSlot0620Bit10 (BankStart + $3070)
InteractionScriptB06D:
    BogusJumpBank1 InteractionScriptB074
.assert (* - BankStart) = $3070, error, "bank 1 interaction script $B04C end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptB070:
    BogusBranchIfSlotD0BitsClear BranchScriptB121, $80 ; CONTROL_BRANCH_SCRIPT_B070
.assert (* - BankStart) = $3074, error, "bank 1 branch script $B070 end"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptB074:
    BogusLoadSlotValueArray $FF ; CONTROL_INTERACTION_SCRIPT_B074
InteractionScriptB076:
    BogusRestoreSavedScriptAndSlotFlags
.assert (* - BankStart) = $3077, error, "bank 1 interaction script $B074 end"
    .incbin "bank1_b077_b080.bin"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptB080:
    BogusSetDispatchCounter $87 ; CONTROL_BRANCH_SCRIPT_B080
BranchScriptB082:
    BogusLoadSlotRecordAtPointer $3077
.assert (* - BankStart) = $3085, error, "bank 1 branch script $B080 end"
; Possible continuation after a direct-record load; runtime mode and reachability are unverified.
DirectNextScriptB085:
    BogusRestartVoice4 $277A ; CONTROL_DIRECT_NEXT_SCRIPT_B085
DirectNextScriptB088:
    BogusSetDispatchCounter $84
DirectNextScriptB08A:
    BogusLoadSlotValueArray $29
DirectNextScriptB08C:
    BogusSetSlotMode $00
DirectNextScriptB08E:
    BogusSetSlotMode $02
DirectNextScriptB090:
    BogusSetDispatchCounter $8F
DirectNextScriptB092:
    BogusBranchIfAbsSlot0700Below DirectNextScriptB0A0, $12
DirectNextScriptB096:
    BogusWait $05
DirectNextScriptB098:
    BogusCreateLinkedSlot $66, $19, $F8, $00
DirectNextScriptB09D:
    BogusCheckSlotFlagsAndRestorePointer
DirectNextScriptB09E:
    BogusLoadRecordAndClearSavedState $3F
DirectNextScriptB0A0:
    BogusBranchIfSlot0700AtMost DirectNextScriptB0B3, $7F
DirectNextScriptB0A4:
    BogusReadSlotValue $4C
DirectNextScriptB0A6:
    BogusMaskSlotValue $0080
DirectNextScriptB0A9:
    BogusBranchIfSlotValueEqual DirectNextScriptB096, $80, $00
DirectNextScriptB0AE:
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $30B0, error, "bank 1 candidate successor $B085 end"
    .incbin "bank1_b0b0_b0b3.bin"
; Possible continuation after a direct-record load; runtime mode and reachability are unverified.
DirectNextScriptB0B3:
    BogusReadSlotValue $4C ; CONTROL_DIRECT_NEXT_SCRIPT_B0B3
DirectNextScriptB0B5:
    BogusMaskSlotValue $0080
DirectNextScriptB0B8:
    BogusBranchIfSlotValueEqual DirectNextScriptB096, $00, $00
DirectNextScriptB0BD:
    BogusJumpBank1 DirectNextScriptB09D
.assert (* - BankStart) = $30C0, error, "bank 1 candidate successor $B0B3 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptB0C0:
    BogusBranchIfSlot0620Bit10 BranchScriptB0E1
BranchScriptB0C3:
    BogusSetDispatchCounter $85 ; CONTROL_BRANCH_SCRIPT_B0C0
BranchScriptB0C5:
    BogusBranchIfSelectedFlags BranchScriptB110, $08
BranchScriptB0C9:
    BogusBranchIfSelectedFlags BranchScriptB0DA, $04
BranchScriptB0CD:
    BogusRestartVoice4 $277A
BranchScriptB0D0:
    BogusSetDirectionalSlotFields40 $10, $D8
BranchScriptB0D3:
    BogusMarkRelatedSlotAtDepth $18, $01
BranchScriptB0D6:
    BogusWait $04
BranchScriptB0D8:
    BogusLoadRecordAndClearSavedState $12
BranchScriptB0DA:
    BogusMarkRelatedSlotAtDepth $38, $01
BranchScriptB0DD:
    BogusWait $04
BranchScriptB0DF:
    BogusLoadRecordAndClearSavedState $12
BranchScriptB0E1:
    BogusBranchIfSelectedFlags InteractionScriptB074, $03
BranchScriptB0E5:
    BogusSetDispatchCounter $85
BranchScriptB0E7:
    BogusBranchIfSelectedFlags BranchScriptB106, $08
BranchScriptB0EB:
    BogusBranchIfSelectedFlags BranchScriptB0FF, $04
BranchScriptB0EF:
    BogusSetDirectionalSlotFields40 $10, $D8
BranchScriptB0F2:
    BogusMarkRelatedSlotAtDepth $1A, $01
BranchScriptB0F5:
    BogusRestartVoice4 $277A
BranchScriptB0F8:
    BogusSetSlotFields80 $00, $00
BranchScriptB0FB:
    BogusWait $03
BranchScriptB0FD:
    BogusLoadRecordAndClearSavedState $3F
BranchScriptB0FF:
    BogusMarkRelatedSlotAtDepth $38, $01
BranchScriptB102:
    BogusWait $03
BranchScriptB104:
    BogusLoadRecordAndClearSavedState $3F
BranchScriptB106:
    BogusRestartVoice4 $286C
BranchScriptB109:
    BogusMarkRelatedSlotAtDepth $E8, $01
BranchScriptB10C:
    BogusWait $01
BranchScriptB10E:
    BogusLoadRecordAndClearSavedState $3F
BranchScriptB110:
    BogusRestartVoice4 $286C
BranchScriptB113:
    BogusMarkRelatedSlotAtDepth $E8, $01
BranchScriptB116:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $3118, error, "bank 1 branch script $B0C0 end"
; Observed in modes $00, $01, $02 and $FF; byte 2 is negative-mode flags.
SweepRecordB118:
    SlotRuntimeRecord $B72C, $FFFF, $40, $00, $60, $08, $12 ; CONTROL_SWEEP_RECORD_B118
.assert (* - BankStart) = $3121, error, "bank 1 sweep record $B118 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptB121:
    BogusLoadSlotRecordAtPointer $3118 ; CONTROL_BRANCH_SCRIPT_B121
.assert (* - BankStart) = $3124, error, "bank 1 branch script $B121 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptB124:
    BogusMarkRelatedSlotAtDepth $38, $05 ; CONTROL_SWEEP_SCRIPT_B124
SweepScriptB127:
    BogusWait $07
SweepScriptB129:
    BogusMarkRelatedSlotAtDepth $38, $05
SweepScriptB12C:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $312E, error, "bank 1 sweep script $B124 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptB12E:
    BogusSetDispatchCounter $05 ; CONTROL_RUNTIME_SCRIPT_B12E
RuntimeScriptB130:
    BogusClearSlot0790Bits $BF
RuntimeScriptB132:
    BogusFindLinkedSlot
RuntimeScriptB133:
    BogusBranchIfSlotValueNotEqual (BankStart + $313E), $FFFF
RuntimeScriptB138:
    BogusLoadSlotRecordAtPointer $2CF4
RuntimeScriptB13B:
    BogusJumpBank1 RuntimeScriptB144
.assert (* - BankStart) = $313E, error, "bank 1 runtime script $B12E end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptB13E:
    BogusLoadSlotRecordAtPointer $2CFD ; CONTROL_EXTENDED_SCRIPT_B13E
.assert (* - BankStart) = $3141, error, "bank 1 extended script $B13E end"
; Command entries observed during the directed-input exploration.
DirectedScriptB141:
    BogusMarkRelatedSlotAtDepth $38, $05 ; CONTROL_DIRECTED_SCRIPT_B141
.assert (* - BankStart) = $3144, error, "bank 1 directed script $B141 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptB144:
    BogusApplyAndClearSelected3E
RuntimeScriptB145:
    BogusBranchIfSlotFieldsWithin RuntimeScriptB14C, $07, $FF ; CONTROL_RUNTIME_SCRIPT_B144
RuntimeScriptB14A:
    BogusLoadRecordAndClearSavedState $48
RuntimeScriptB14C:
    BogusApplyAndClearSelected3E
RuntimeScriptB14D:
    BogusBranchIfRemainingVerticalOffsetAtMost (BankStart + $2EF1), $0004
RuntimeScriptB152:
    BogusBranchIfSlot0620Bit10 RuntimeScriptB144
.assert (* - BankStart) = $3155, error, "bank 1 runtime script $B144 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptB155:
    BogusLoadRecordAndClearSavedState $12 ; CONTROL_EXTENDED_SCRIPT_B155
.assert (* - BankStart) = $3157, error, "bank 1 extended script $B155 end"
; Command entries observed during the directed-input exploration.
DirectedScriptB157:
    BogusSetDispatchCounter $0A ; CONTROL_DIRECTED_SCRIPT_B157
DirectedScriptB159:
    BogusStoreSlotValueArray $3E
DirectedScriptB15B:
    BogusSwapSlotValueBytes
DirectedScriptB15C:
    BogusStoreSlotValueArray $3F
DirectedScriptB15E:
    BogusReadSlotValue $0F
DirectedScriptB160:
    BogusBranchIfSlotValueAtLeast DirectedScriptB16B, $0005
DirectedScriptB165:
    BogusAddSlotValue $00F7
DirectedScriptB168:
    BogusJumpBank1 DirectedScriptB184
DirectedScriptB16B:
    BogusBranchIfSlotValueAtLeast DirectedScriptB176, $000B
DirectedScriptB170:
    BogusSetSlotValue $002B
DirectedScriptB173:
    BogusJumpBank1 DirectedScriptB184
DirectedScriptB176:
    BogusBranchIfSlotValueAtLeast (BankStart + $3181), $000F
DirectedScriptB17B:
    BogusSetSlotValue $0012
DirectedScriptB17E:
    BogusJumpBank1 DirectedScriptB184
.assert (* - BankStart) = $3181, error, "bank 1 directed script $B157 end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptB181:
    BogusSetSlotValue $0027 ; CONTROL_EXPANDED_SCRIPT_B181
.assert (* - BankStart) = $3184, error, "bank 1 candidate successor $B181 end"
; Command entries observed during the directed-input exploration.
DirectedScriptB184:
    BogusStoreSlotValueArray $3D ; CONTROL_DIRECTED_SCRIPT_B184
DirectedScriptB186:
    BogusLoadSlotLowFromByteArray $3F
DirectedScriptB188:
    BogusSwapSlotValueBytes
DirectedScriptB189:
    BogusLoadSlotLowFromByteArray $3E
DirectedScriptB18B:
    BogusCallNativeEncoded $B51B
DirectedScriptB18E:
    BogusSaveStateAndPlaceSlots $10
DirectedScriptB190:
    BogusRestoreSavedScriptAndSlotFlags
.assert (* - BankStart) = $3191, error, "bank 1 directed script $B184 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptB191:
    BogusSetDispatchCounter $0C ; CONTROL_RUNTIME_SCRIPT_B191
RuntimeScriptB193:
    BogusStoreSlotValueArray $3E
RuntimeScriptB195:
    BogusSwapSlotValueBytes
RuntimeScriptB196:
    BogusStoreSlotValueArray $3F
RuntimeScriptB198:
    BogusReadSlotValue $2A
RuntimeScriptB19A:
    BogusLookupSlotValue
.assert (* - BankStart) = $319B, error, "bank 1 runtime script $B191 end"
; $95 compares each value to the slot value and branches to its target.
; The two-byte zero target terminates the inline table.
    BogusLookupCaseBank1 SuccessorScriptB218, $0007 ; CONTROL_SUCCESSOR_LOOKUP_B19B
    BogusLookupCaseBank1 SuccessorScriptB26A, $0000
    BogusLookupCaseBank1 SuccessorScriptB26A, $0080
    BogusLookupCaseBank1 RuntimeScriptB2A8, $0001
    BogusLookupCaseBank1 SuccessorScriptB34A, $000D
    BogusLookupCaseBank1 SuccessorScriptB1BB, $0009
    BogusLookupEnd
.assert (* - BankStart) = $31B5, error, "bank 1 successor lookup $B19B end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptB1B5:
    BogusLoadSlotLowFromByteArray $3F ; CONTROL_RUNTIME_SCRIPT_B1B5
RuntimeScriptB1B7:
    BogusSwapSlotValueBytes
RuntimeScriptB1B8:
    BogusLoadSlotLowFromByteArray $3E
RuntimeScriptB1BA:
    BogusRestoreSavedScriptAndSlotFlags
.assert (* - BankStart) = $31BB, error, "bank 1 runtime script $B1B5 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB1BB:
    BogusSetDispatchCounter $07 ; CONTROL_SUCCESSOR_SCRIPT_B1BB
SuccessorScriptB1BD:
    BogusBranchIfMatchingSlotReady SuccessorScriptB1C6, $01, $6F, $00
SuccessorScriptB1C3:
    BogusJumpBank1 RuntimeScriptB1B5
SuccessorScriptB1C6:
    BogusSetDispatchCounter $06
SuccessorScriptB1C8:
    BogusSetSlotValue $0000
SuccessorScriptB1CB:
    BogusStoreSlotValueArray $2B
SuccessorScriptB1CD:
    BogusMarkMatchingSlots $E0, $01, $6F, $00
SuccessorScriptB1D2:
    BogusSetSlotMode $02
SuccessorScriptB1D4:
    BogusWait $02
SuccessorScriptB1D6:
    BogusSetDispatchCounter $06
SuccessorScriptB1D8:
    BogusLoadSlotValueArray $2B
SuccessorScriptB1DA:
    BogusBranchIfSlotValueEqual RuntimeScriptB1B5, $00, $00
SuccessorScriptB1DF:
    BogusSetSlotFields80 $00, $00
SuccessorScriptB1E2:
    BogusWait $26
SuccessorScriptB1E4:
    BogusLoadSlotValueArray $2A
SuccessorScriptB1E6:
    BogusBranchIfSlotValueAtLeast SuccessorScriptB1F7, $0004
SuccessorScriptB1EB:
    BogusSetSlotValue $002F
SuccessorScriptB1EE:
    BogusStoreSlotValueArray $3D
SuccessorScriptB1F0:
    BogusCallNativeEncoded $B51B
SuccessorScriptB1F3:
    BogusSaveStateAndPlaceSlots $10
.assert (* - BankStart) = $31F5, error, "bank 1 candidate successor $B1BB end"
; Possible continuation after state restoration; slot survival is unverified.
RestoreScriptB1F5:
    BogusLoadRecordAndClearSavedState $48 ; CONTROL_RESTORE_SCRIPT_B1F5
.assert (* - BankStart) = $31F7, error, "bank 1 restore candidate B1F5 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB1F7:
    BogusRestartVoice4 $0000 ; CONTROL_SUCCESSOR_SCRIPT_B1F7
SuccessorScriptB1FA:
    BogusSetSlotValue $0030
SuccessorScriptB1FD:
    BogusStoreSlotValueArray $3D
SuccessorScriptB1FF:
    BogusReadSlotValue $0F
SuccessorScriptB201:
    BogusAddSlotValue $0001
SuccessorScriptB204:
    BogusBranchIfSlotValueNotEqual SuccessorScriptB211, $000F
SuccessorScriptB209:
    BogusSetSlotValue $0027
SuccessorScriptB20C:
    BogusStoreSlotValueArray $3D
SuccessorScriptB20E:
    BogusSetSlotValue $000F
SuccessorScriptB211:
    BogusStoreSlotValueArray $23
SuccessorScriptB213:
    BogusCallNativeEncoded $B51B
SuccessorScriptB216:
    BogusSetMainState $10
SuccessorScriptB218:
    BogusBranchIfMatchingSlotReady SuccessorScriptB22C, $01, $6A, $00
SuccessorScriptB21E:
    BogusSetSlotValue $002D
SuccessorScriptB221:
    BogusStoreSlotValueArray $3D
SuccessorScriptB223:
    BogusReadSlotValue $0F
SuccessorScriptB225:
    BogusStoreSlotValueArray $23
SuccessorScriptB227:
    BogusCallNativeEncoded $B51B
SuccessorScriptB22A:
    BogusSetMainState $10
SuccessorScriptB22C:
    BogusSetSlot0670Pair $00, $10
SuccessorScriptB22F:
    BogusBranchIfSlotCoordinatesA3 SuccessorScriptB237, $10, $FF
SuccessorScriptB234:
    BogusJumpBank1 RuntimeScriptB1B5
SuccessorScriptB237:
    BogusRestartVoice4 $0000
SuccessorScriptB23A:
    BogusReadSlotValue $0F
SuccessorScriptB23C:
    BogusBranchIfSlotValueEqual SuccessorScriptB252, $0A, $00
SuccessorScriptB241:
    BogusSetSlotValue $0031
SuccessorScriptB244:
    BogusStoreSlotValueArray $3D
SuccessorScriptB246:
    BogusReadSlotValue $0F
SuccessorScriptB248:
    BogusAddSlotValue $0001
SuccessorScriptB24B:
    BogusStoreSlotValueArray $23
SuccessorScriptB24D:
    BogusCallNativeEncoded $B51B
SuccessorScriptB250:
    BogusSetMainState $10
SuccessorScriptB252:
    BogusSetVoicePointers $0000, $0000, $0000, $0000
SuccessorScriptB25B:
    BogusSetSlotValue $002E
SuccessorScriptB25E:
    BogusStoreSlotValueArray $3D
SuccessorScriptB260:
    BogusSetSlotValue $0014
SuccessorScriptB263:
    BogusStoreSlotValueArray $23
SuccessorScriptB265:
    BogusCallNativeEncoded $B51B
SuccessorScriptB268:
    BogusSetMainState $10
SuccessorScriptB26A:
    BogusBranchIfSlot0620Bit10Clear RuntimeScriptB1B5
SuccessorScriptB26D:
    BogusReadSlotValue $00
SuccessorScriptB26F:
    BogusMaskSlotValue $007F
SuccessorScriptB272:
    BogusClampSlotValueAtMost $00C8
SuccessorScriptB275:
    BogusCallNativeEncoded $B51B
SuccessorScriptB278:
    BogusSetSpritePalettePointer $C83E
.assert (* - BankStart) = $327B, error, "bank 1 candidate successor $B1F7 end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptB27B:
    BogusLoadIndexedStateRecord $332E ; CONTROL_PATH_SCRIPT_B27B
.assert (* - BankStart) = $327E, error, "bank 1 candidate successor $B27B end"
; Possible resume paths; scheduling and entry conditions remain unverified.
ResumeScriptB27E:
    BogusReadSlotValue $00 ; CONTROL_RESUME_SCRIPT_B27E
ResumeScriptB280:
    BogusMaskSlotValue $0080
ResumeScriptB283:
    BogusBranchIfSlotValueEqual ResumeScriptB29E, $80, $00
ResumeScriptB288:
    BogusReadSlotValue $0F
ResumeScriptB28A:
    BogusBranchIfSlotValueNotEqual ResumeScriptB299, $0004
ResumeScriptB28F:
    BogusSetBackgroundPalettePointer $FFFF
ResumeScriptB292:
    BogusMarkMatchingSlots $D0, $01, $08, $00
ResumeScriptB297:
    BogusLoadRecordAndClearSavedState $48
ResumeScriptB299:
    BogusSetBackgroundPalettePointer $C7DF
ResumeScriptB29C:
    BogusLoadRecordAndClearSavedState $48
ResumeScriptB29E:
    BogusSetBackgroundPalettePointer $FFFF
ResumeScriptB2A1:
    BogusMarkMatchingSlots $D0, $01, $08, $00
ResumeScriptB2A6:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $32A8, error, "bank 1 candidate successor $B27E end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptB2A8:
    BogusBranchIfSlotD0Bits (BankStart + $32CC), $80 ; CONTROL_RUNTIME_SCRIPT_B2A8
RuntimeScriptB2AC:
    BogusSetDispatchCounter $07
RuntimeScriptB2AE:
    BogusBranchIfSelectedFlags (BankStart + $32B9), $08
RuntimeScriptB2B2:
    BogusBranchIfSlot0620Bit10 RuntimeScriptB1B5
.assert (* - BankStart) = $32B5, error, "bank 1 runtime script $B2A8 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB2B5:
    BogusBranchIfSelectedFlagsClear RuntimeScriptB1B5, $04 ; CONTROL_SUCCESSOR_SCRIPT_B2B5
SuccessorScriptB2B9:
    BogusSetDispatchCounter $08
SuccessorScriptB2BB:
    BogusSetDispatchCounter $06
SuccessorScriptB2BD:
    BogusSetSlotD0Bits $80
SuccessorScriptB2BF:
    BogusLoadSlotRecordAtPointer $2D21
.assert (* - BankStart) = $32C2, error, "bank 1 candidate successor $B2B5 end"
; Command entries observed during the directed-input exploration.
DirectedScriptB2C2:
    BogusSetSlotC0 $00 ; CONTROL_DIRECTED_SCRIPT_B2C2
DirectedScriptB2C4:
    BogusSetSlotFields80 $00, $00
DirectedScriptB2C7:
    BogusClearSlot0790Bits $25
DirectedScriptB2C9:
    BogusMarkSlot05A0AndYield
.assert (* - BankStart) = $32CA, error, "bank 1 directed script $B2C2 end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptB2CA:
    BogusLoadRecordAndClearSavedState $12 ; CONTROL_EXPANDED_SCRIPT_B2CA
.assert (* - BankStart) = $32CC, error, "bank 1 candidate successor $B2CA end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB2CC:
    BogusSetDispatchCounter $8F ; CONTROL_SUCCESSOR_SCRIPT_B2CC
SuccessorScriptB2CE:
    BogusBranchIfRemainingVerticalOffsetAtMost SuccessorScriptB2DA, $0060
SuccessorScriptB2D3:
    BogusLoadSlotValueArray $3C
SuccessorScriptB2D5:
    BogusSetSlotMode $00
SuccessorScriptB2D7:
    BogusJumpBank1 SuccessorScriptB2E3
SuccessorScriptB2DA:
    BogusLoadSlotValueArray $29
SuccessorScriptB2DC:
    BogusSetSlotMode $00
SuccessorScriptB2DE:
    BogusSetSlotMode $02
SuccessorScriptB2E0:
    BogusBranchIfSlot0620Bit10 SuccessorScriptB326
SuccessorScriptB2E3:
    BogusBranchIfSelectedFlags SuccessorScriptB2ED, $03
SuccessorScriptB2E7:
    BogusSetSlotFields80 $00, $FF
SuccessorScriptB2EA:
    BogusJumpBank1 SuccessorScriptB2EE
SuccessorScriptB2ED:
    BogusApplyAndClearSelected3E
SuccessorScriptB2EE:
    BogusBranchIfSelectedFlags SuccessorScriptB306, $08
SuccessorScriptB2F2:
    BogusBranchIfSelectedFlagsClear SuccessorScriptB31C, $04
SuccessorScriptB2F6:
    BogusSetSlotFields80 $FF, $10
SuccessorScriptB2F9:
    BogusBranchIfSelectedFlagsClear SuccessorScriptB316, $40
SuccessorScriptB2FD:
    BogusSetSlotFields80 $FF, $20
SuccessorScriptB300:
    BogusStartVoice4 $2769
SuccessorScriptB303:
    BogusJumpBank1 SuccessorScriptB321
SuccessorScriptB306:
    BogusSetSlotFields80 $FF, $F0
SuccessorScriptB309:
    BogusBranchIfSelectedFlagsClear SuccessorScriptB316, $40
SuccessorScriptB30D:
    BogusSetSlotFields80 $FF, $E0
SuccessorScriptB310:
    BogusStartVoice4 $2769
SuccessorScriptB313:
    BogusJumpBank1 SuccessorScriptB321
SuccessorScriptB316:
    BogusStartVoice4 $2760
SuccessorScriptB319:
    BogusJumpBank1 SuccessorScriptB321
SuccessorScriptB31C:
    BogusSetSlotFields80 $FF, $00
SuccessorScriptB31F:
    BogusClearSlot0790Bits $08
SuccessorScriptB321:
    BogusClearSlot0790Bits $25
.assert (* - BankStart) = $3323, error, "bank 1 candidate successor $B2CC end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptB323:
    BogusMarkSlot05A0AndYield ; CONTROL_EXTENDED_SCRIPT_B323
.assert (* - BankStart) = $3324, error, "bank 1 extended script $B323 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB324:
    BogusLoadRecordAndClearSavedState $12 ; CONTROL_SUCCESSOR_SCRIPT_B324
SuccessorScriptB326:
    BogusBranchIfSelectedFlags SuccessorScriptB2E3, $08
SuccessorScriptB32A:
    BogusClearSlotD0Bits $80
SuccessorScriptB32C:
    BogusLoadRecordAndClearSavedState $3F
.assert (* - BankStart) = $332E, error, "bank 1 candidate successor $B324 end"
; Candidate records selected by the opcode $89 operand at $B27B when the
; alternate mapping selects this bank. The next known script begins at $B34A;
; that boundary does not prove the runtime index is limited to these entries.
IndexedStateRecordsB32E:
    IndexedStateRecord $FF, $32, $1E, $0180, $0193 ; CONTROL_INDEXED_STATE_RECORDS_B32E
    IndexedStateRecord $FF, $31, $1E, $0011, $001C
    IndexedStateRecord $FF, $21, $15, $0180, $018B
    IndexedStateRecord $FF, $21, $15, $0011, $0024
.assert (* - BankStart) = $334A, error, "bank 1 indexed state records end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptB34A:
    BogusSetDispatchCounter $03 ; CONTROL_SUCCESSOR_SCRIPT_B34A
SuccessorScriptB34C:
    BogusBranchIfSlot0620Bit10Clear RuntimeScriptB1B5
SuccessorScriptB34F:
    BogusBranchIfSelectedFlags RuntimeScriptB1B5, $03
SuccessorScriptB353:
    BogusSetDispatchCounter $07
SuccessorScriptB355:
    BogusRestartVoice4 $27A9
SuccessorScriptB358:
    BogusSetSlotValue $2B00
.assert (* - BankStart) = $335B, error, "bank 1 candidate successor $B34A end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptB35B:
    BogusStoreSlotLowAtIndexedPage ; CONTROL_EXTENDED_SCRIPT_B35B
.assert (* - BankStart) = $335C, error, "bank 1 extended script $B35B end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptB35C:
    BogusSwapSlotValueBytes
ExpandedScriptB35D:
    BogusStoreSlotValueArray $2A ; CONTROL_EXPANDED_SCRIPT_B35C
ExpandedScriptB35F:
    BogusMarkRelatedSlotAtDepth $48, $01
ExpandedScriptB362:
    BogusWait $02
ExpandedScriptB364:
    BogusSetDispatchCounter $06
ExpandedScriptB366:
    BogusSetSlotValue $2C00
ExpandedScriptB369:
    BogusStoreSlotLowAtIndexedPage
ExpandedScriptB36A:
    BogusSwapSlotValueBytes
ExpandedScriptB36B:
    BogusStoreSlotValueArray $2A
ExpandedScriptB36D:
    BogusMarkRelatedSlotAtDepth $48, $02
ExpandedScriptB370:
    BogusWait $02
ExpandedScriptB372:
    BogusSetDispatchCounter $06
ExpandedScriptB374:
    BogusSetSlotValue $2D00
ExpandedScriptB377:
    BogusStoreSlotLowAtIndexedPage
ExpandedScriptB378:
    BogusSwapSlotValueBytes
ExpandedScriptB379:
    BogusStoreSlotValueArray $2A
ExpandedScriptB37B:
    BogusMarkRelatedSlotAtDepth $48, $03
ExpandedScriptB37E:
    BogusWait $02
ExpandedScriptB380:
    BogusSetDispatchCounter $06
ExpandedScriptB382:
    BogusSetSlotValue $2E00
ExpandedScriptB385:
    BogusStoreSlotLowAtIndexedPage
ExpandedScriptB386:
    BogusSwapSlotValueBytes
ExpandedScriptB387:
    BogusStoreSlotValueArray $2A
ExpandedScriptB389:
    BogusMarkRelatedSlotAtDepth $48, $04
ExpandedScriptB38C:
    BogusWait $02
ExpandedScriptB38E:
    BogusCallNativeEncoded $B51B
ExpandedScriptB391:
    BogusLoadSlotRecordAtPointer $2D3C
.assert (* - BankStart) = $3394, error, "bank 1 candidate successor $B35C end"
; Possible continuation after a direct-record load; runtime mode and reachability are unverified.
DirectNextScriptB394:
    BogusSetSpriteAttribute20 $20 ; CONTROL_DIRECT_NEXT_SCRIPT_B394
DirectNextScriptB396:
    BogusJumpBank1 DirectNextScriptD253
.assert (* - BankStart) = $3399, error, "bank 1 candidate successor $B394 end"
; Candidate path after a saved slot is restored. Its direct record load can
; preserve the next pointer; actual mode, restoration and reachability are unknown.
RestoreScriptB399:
    BogusSetSlotC0 $FF ; CONTROL_RESTORE_SCRIPT_B399
    BogusSetSpriteAttribute20 $00
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueEqual RestoreScriptB3BA, $00, $00
    BogusLoadSlotRecordAtPointer $53AE
RestoreScriptB3A7:
    BogusSetSlotValue $0003
    BogusStoreSlotValueArray $3D
    BogusCallNativeEncoded $B51B
    BogusSaveStateAndPlaceSlots $10
RestoreScriptB3B1:
    BogusReadSlotValue $0F
    BogusStoreSlotValueArray $3D
    BogusCallNativeEncoded $B51B
    BogusSetMainState $13
RestoreScriptB3BA:
    BogusSetBackgroundPalettePointer $FFFF
    BogusSetSpritePalettePointer $FFFF
    BogusMarkMatchingSlots $D0, $01, $08, $00
    BogusLoadRecordAndClearSavedState $3F
.assert (* - BankStart) = $33C7, error, "bank 1 restore candidate B399 end"
; Candidate descriptor $B3E5, command $B67F, mode $FF.
SlotFlowB3C7:
    SlotCompactRecord $BF1B, $00 ; CONTROL_SLOT_FLOW_B3C7
; Candidate descriptor $B3E5, command $B679, mode $FF.
SlotFlowB3CA:
    SlotCompactRecord $BF0F, $00
; Candidate descriptor $B3E5, command $B673, mode $FF.
SlotFlowB3CD:
    SlotCompactRecord $BF03, $00
; Candidate descriptor $B3E5, command $B66D, mode $FF.
SlotFlowB3D0:
    SlotCompactRecord $BEF7, $00
; Candidate descriptor $B3E5, command $B667, mode $FF.
SlotFlowB3D3:
    SlotCompactRecord $BEEB, $00
; Candidate descriptor $B3E5, command $B661, mode $FF.
SlotFlowB3D6:
    SlotCompactRecord $BEDF, $00
; Candidate descriptor $B3E5, command $B65B, mode $FF.
SlotFlowB3D9:
    SlotCompactRecord $BED3, $00
; Candidate descriptor $B3E5, command $B655, mode $FF.
SlotFlowB3DC:
    SlotCompactRecord $BEC7, $00
; Candidate descriptor $B3E5, command $B64F, mode $FF.
SlotFlowB3DF:
    SlotCompactRecord $BEBB, $00
; Candidate descriptor $B3E5, command $B649, mode $FF.
SlotFlowB3E2:
    SlotCompactRecord $BEAF, $00
.assert (* - BankStart) = $33E5, error, "bank 1 slot record flow B3C7 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB3E5:
    SlotRuntimeRecord $BEA3, (ScriptB3EE - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B3E5
.assert (* - BankStart) = $33EE, error, "bank 1 slot record B3E5 end"
; Map and slot selection script; unconverted branch targets remain address aliases.
ScriptB3EE:
    BogusSetSlotC0 $00 ; CONTROL_BOGUS_B3EE
    BogusSetSlotPositionFromOperands $10, $5F
    BogusSetSlot0640Pair $10, $00
    BogusReadSlotValue $0F
    BogusSetSlotD0Bits $10
    BogusBranchIfSlotValueAtLeast ScriptB415, $000F
    BogusClearSlotD0Bits $10
    BogusSetSlotD0Bits $08
    BogusBranchIfSlotValueAtLeast ScriptB415, $000B
    BogusClearSlotD0Bits $08
    BogusSetSlotD0Bits $04
    BogusBranchIfSlotValueAtLeast ScriptB415, $0005
    BogusClearSlotD0Bits $04
    BogusSetSlotD0Bits $02
ScriptB415:
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
ScriptB41A:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlot0370AtMost ScriptB620, $00
ScriptB420:
    BogusSetDispatchCounter $0A
    BogusLoadSlotValueArray $FF
    BogusFindSlotAtValueOffset
    BogusBranchIfSlotValueNotEqual ScriptB4BF, $FFFF
    BogusLoadSlotValueArray $FF
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 ScriptB4E7, $006C
    BogusLookupCaseBank1 ScriptB503, $006D
    BogusLookupCaseBank1 ScriptB509, $008C
    BogusLookupCaseBank1 ScriptB50F, $008D
    BogusLookupCaseBank1 ScriptB515, $006F
    BogusLookupCaseBank1 ScriptB538, $0071
    BogusLookupCaseBank1 ScriptB53E, $004D
    BogusLookupCaseBank1 ScriptB544, $008E
    BogusLookupCaseBank1 ScriptB54A, $0041
    BogusLookupCaseBank1 ScriptB56D, $0014
    BogusLookupCaseBank1 ScriptB573, $00BC
    BogusLookupCaseBank1 ScriptB579, $0061
    BogusLookupCaseBank1 ScriptB57F, $0045
    BogusLookupCaseBank1 ScriptB5A2, $0047
    BogusLookupCaseBank1 ScriptB5A8, $00C8
    BogusLookupCaseBank1 ScriptB5AE, $009B
    BogusLookupCaseBank1 ScriptB57F, $0090
    BogusLookupCaseBank1 ScriptB57F, $0040
    BogusLookupCaseBank1 ScriptB57F, $0013
    BogusLookupCaseBank1 ScriptB57F, $0040
    BogusLookupCaseBank1 ScriptB5B4, $0027
    BogusLookupCaseBank1 ScriptB5D9, $0029
    BogusLookupCaseBank1 ScriptB5DF, $0066
    BogusLookupCaseBank1 ScriptB5E5, $0068
    BogusLookupCaseBank1 ScriptB5EB, $00AA
    BogusLookupCaseBank1 ScriptB60E, $00AC
    BogusLookupCaseBank1 ScriptB614, $00AB
    BogusLookupCaseBank1 ScriptB61A, $00AD
    BogusLookupEnd
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $10
    BogusBranchIfSlot0360Above ScriptB4BF, $00
    BogusSetSlot0360 $18
    BogusBranchIfSecondWorldOffsetAtMost ScriptB4BF, $0140
    BogusBranchIfFirstWorldOffsetAtMost ScriptB4BF, $0200
    BogusReadSlotValue $05
    BogusMaskSlotValue $00FF
    BogusAddSlotValue $0100
    BogusCreateSlotFromValue $53, $00
ScriptB4BF:
    BogusSetDispatchCounter $06
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $0010
    BogusStoreSlotValueArray $FF
    BogusMaskSlotValue $00FF
    BogusBranchIfSlotValueAtLeast ScriptB4D3, $00E0
    BogusJumpBank1 ScriptB41A
ScriptB4D3:
    BogusSetDispatchCounter $05
    BogusLoadSlotValueArray $FF
    BogusMaskSlotValue $FF00
    BogusAddSlotValue $1000
    BogusStoreSlotValueArray $FF
    BogusBranchIfSlotValueAtLeast ScriptB415, $E000
    BogusJumpBank1 ScriptB41A
ScriptB4E7:
    BogusSetSlotValue $0000
ScriptB4EA:
    BogusSetDispatchCounter $06
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $02
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusAdvanceAndBranchState1B ScriptB4FD, $C0
    BogusCreateSlotFromValue $0B, $00
    BogusJumpBank1 ScriptB4BF
ScriptB4FD:
    BogusCreateSlotFromValue $0C, $00
    BogusJumpBank1 ScriptB4BF
ScriptB503:
    BogusSetSlotValue $FFF8
    BogusJumpBank1 ScriptB4EA
ScriptB509:
    BogusSetSlotValue $F800
    BogusJumpBank1 ScriptB4EA
ScriptB50F:
    BogusSetSlotValue $F7F8
    BogusJumpBank1 ScriptB4EA
ScriptB515:
    BogusSetSlotValue $0000
ScriptB518:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $08
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $51
    BogusBranchIfSlotValueAtLeast ScriptB4BF, $0003
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
.assert (* - BankStart) = $3532, error, "bank 1 script B3EE end"
; Map-selection continuation; indexed jump-table data remains local.
ScriptB532:
    BogusCreateSlotFromValue $51, $AA ; CONTROL_BOGUS_B532
    BogusJumpBank1 ScriptB4BF
ScriptB538:
    BogusSetSlotValue $FFF8
    BogusJumpBank1 ScriptB518
ScriptB53E:
    BogusSetSlotValue $F800
    BogusJumpBank1 ScriptB518
ScriptB544:
    BogusSetSlotValue $F7F8
    BogusJumpBank1 ScriptB518
ScriptB54A:
    BogusSetSlotValue $E000
ScriptB54D:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $10
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $55
    BogusBranchIfSlotValueAtLeast ScriptB4BF, $0002
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $55, $00
    BogusJumpBank1 ScriptB4BF
ScriptB56D:
    BogusSetSlotValue $E0F8
    BogusJumpBank1 ScriptB54D
ScriptB573:
    BogusSetSlotValue $D800
    BogusJumpBank1 ScriptB54D
ScriptB579:
    BogusSetSlotValue $D8F8
    BogusJumpBank1 ScriptB54D
ScriptB57F:
    BogusSetSlotValue $0000
ScriptB582:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $04
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $6C
    BogusBranchIfSlotValueAtLeast ScriptB4BF, $0003
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $6C, $00
    BogusJumpBank1 ScriptB4BF
ScriptB5A2:
    BogusSetSlotValue $FFF8
    BogusJumpBank1 ScriptB582
ScriptB5A8:
    BogusSetSlotValue $F800
    BogusJumpBank1 ScriptB582
ScriptB5AE:
    BogusSetSlotValue $F8F8
    BogusJumpBank1 ScriptB582
ScriptB5B4:
    BogusSetSlotValue $E800
ScriptB5B7:
    BogusSetDispatchCounter $0E
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $04
    BogusExchangeSlotValueArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusAddSlotValueFromArray $FF
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $70
    BogusBranchIfSlotValueAtLeast ScriptB4BF, $0002
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $70, $00
    BogusJumpBank1 ScriptB4BF
ScriptB5D9:
    BogusSetSlotValue $E7F8
    BogusJumpBank1 ScriptB5B7
ScriptB5DF:
    BogusSetSlotValue $E000
    BogusJumpBank1 ScriptB5B7
ScriptB5E5:
    BogusSetSlotValue $DFF8
    BogusJumpBank1 ScriptB5B7
ScriptB5EB:
    BogusSetSlotValue $F810
ScriptB5EE:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear ScriptB4BF, $04
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $02
    BogusBranchIfSlotValueAtLeast ScriptB4BF, $0002
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $02, $00
    BogusJumpBank1 ScriptB4BF
ScriptB60E:
    BogusSetSlotValue $F808
    BogusJumpBank1 ScriptB5EE
ScriptB614:
    BogusSetSlotValue $F010
    BogusJumpBank1 ScriptB5EE
ScriptB61A:
    BogusSetSlotValue $F008
    BogusJumpBank1 ScriptB5EE
ScriptB620:
    BogusSetSlot0370 $0A
    BogusReadSelectedSlot0520 $00
    BogusClampSlotValueAtMost $0014
    BogusAddSlotValue $0001
    BogusDivideSlotValueByByte $02
    BogusJumpViaSlotIndexedTable
.assert (* - BankStart) = $362D, error, "bank 1 script B532 end"
; The predecessor clamps and divides the selected value to the range 0..10.
; Other possible callers into the indexed jump remain unverified.
    BogusIndexedTargetBank1 ScriptB643 ; CONTROL_BOGUS_B62D
    BogusIndexedTargetBank1 ScriptB649
    BogusIndexedTargetBank1 ScriptB64F
    BogusIndexedTargetBank1 ScriptB655
    BogusIndexedTargetBank1 ScriptB65B
    BogusIndexedTargetBank1 ScriptB661
    BogusIndexedTargetBank1 ScriptB667
    BogusIndexedTargetBank1 ScriptB66D
    BogusIndexedTargetBank1 ScriptB673
    BogusIndexedTargetBank1 ScriptB679
    BogusIndexedTargetBank1 ScriptB67F
ScriptB643:
    BogusLoadSlotRecord $00, $01
    BogusJumpBank1 ScriptB420
ScriptB649:
    BogusLoadSlotRecord $03, $FF
    BogusJumpBank1 ScriptB420
ScriptB64F:
    BogusLoadSlotRecord $06, $FF
    BogusJumpBank1 ScriptB420
ScriptB655:
    BogusLoadSlotRecord $09, $FF
    BogusJumpBank1 ScriptB420
ScriptB65B:
    BogusLoadSlotRecord $0C, $FF
    BogusJumpBank1 ScriptB420
ScriptB661:
    BogusLoadSlotRecord $0F, $FF
    BogusJumpBank1 ScriptB420
ScriptB667:
    BogusLoadSlotRecord $12, $FF
    BogusJumpBank1 ScriptB420
ScriptB66D:
    BogusLoadSlotRecord $15, $FF
    BogusJumpBank1 ScriptB420
ScriptB673:
    BogusLoadSlotRecord $18, $FF
    BogusJumpBank1 ScriptB420
ScriptB679:
    BogusLoadSlotRecord $1B, $FF
    BogusJumpBank1 ScriptB420
ScriptB67F:
    BogusLoadSlotRecord $1E, $FF
    BogusJumpBank1 ScriptB420
.assert (* - BankStart) = $3685, error, "bank 1 indexed script table B62D end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB685:
    SlotRuntimeRecord $BC83, (CandidateB6A0 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B685
.assert (* - BankStart) = $368E, error, "bank 1 slot record B685 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordB68E:
    SlotRuntimeRecord $C00D, (SweepScriptB6B1 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_B68E
.assert (* - BankStart) = $3697, error, "bank 1 sweep record $B68E end"
; Candidate descriptor $B685, command $B6AF, mode $00.
SlotFlowB697:
    SlotRuntimeRecord $B755, $36B8, $40, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_B697
.assert (* - BankStart) = $36A0, error, "bank 1 slot record flow B697 end"
; Candidate script path; object role and execution remain unverified.
CandidateB6A0:
    BogusSetSlotC0 $00 ; CONTROL_BOGUS_B6A0
    BogusBranchIfSlot0630Bit02 CandidateB6A8
    BogusAdjustSlotBounds $00, $FE
CandidateB6A8:
    BogusSetSlot0670Pair $01, $00
    BogusWait $28
    BogusClearSlot0790Bits $01
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $36B1, error, "bank 1 candidate script B6A0 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptB6B1:
    BogusStartVoice4 $2724 ; CONTROL_SWEEP_SCRIPT_B6B1
SweepScriptB6B4:
    BogusWait $04
SweepScriptB6B6:
    BogusYieldAndSlotAction $01
.assert (* - BankStart) = $36B8, error, "bank 1 sweep script $B6B1 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptB6B8:
    BogusSetSlot0660LowBits $01 ; CONTROL_CONTEXT_B6B8
    BogusSetSlotFields80 $01, $00
    BogusBranchIfSlotRecord06AtLeast ContextScriptB6C4, $07
    BogusJumpBank1 ContextScriptB6B8
ContextScriptB6C4:
    BogusCreateLinkedSlot $6D, $12, $00, $FF
    BogusStartVoice4 $277A
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadSlotRecord $00, $02
    BogusJumpBank1 (BankStart + $36AB)
.assert (* - BankStart) = $36D3, error, "bank 1 contextual script B6B8 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB6D3:
    SlotRuntimeRecord $B693, (ScriptB6EE - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B6D3
.assert (* - BankStart) = $36DC, error, "bank 1 slot record B6D3 end"
    .incbin "bank1_b6dc_b6dd.bin"
; A possible contact event reads the resource sentinel and script pointer.
ContactRecordB6DD:
    .byte $FF ; CONTROL_CONTACT_RECORD_B6DD
    .word ContactScriptB787 - BankStart
.assert (* - BankStart) = $36E0, error, "bank 1 contact record B6DD end"
    .incbin "bank1_b6e0_b6e5.bin"
; Observed in Moses level two through $B718 with loader mode $02. The
; pointer and the five later fields are consumed; the intervening bytes are
; skipped in this mode and remain local. The pointed-to sprite stays local.
MosesStageTwoResourceB6E5:
    .word $B693 ; CONTROL_MOSES_STAGE2_RESOURCE_B6E5
.assert (* - BankStart) = $36E7, error, "bank 1 stage-two resource B6E5 end"
    .incbin "bank1_b6e7_b6e9.bin"
MosesStageTwoFieldsB6E9:
    .byte $00, $00, $20, $50, $12 ; CONTROL_MOSES_STAGE2_FIELDS_B6E9
.assert (* - BankStart) = $36EE, error, "bank 1 stage-two fields B6E9 end"
; Connected slot-action script with coordinate checks, linked-slot search and
; original wait/loop behaviour. The gameplay object is not yet identified.
ScriptB6EE:
    BogusSetSlot0670Pair $01, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlotC0 $00
    BogusClearSlot0790Bits $01
ScriptB6F8:
    BogusSetSlotFields40Signed $18, $00
ScriptB6FB:
    BogusBranchIfAbsSlot0700Below ScriptB6F8, $18
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual ScriptB709, $00, $00
    BogusJumpBank1 ScriptB6FB
ScriptB709:
    BogusBranchIfSlotCoordinatesA3 ScriptB6F8, $FF, $30
    BogusSetSlotFields80 $00, $00
    BogusWait $06
    BogusBranchIfSlotCoordinatesA3 ScriptB6F8, $FF, $30
    BogusLoadSlotRecord $12, $02
    BogusSetSlotBit40 $FF
    BogusSetSlot0360 $64         ; CONTROL_BOGUS_B6EE
ScriptB71F:
    BogusSetDispatchCounter $05
    BogusSetSlot0620Bit20
    BogusSetSlot0660LowBits $01
    BogusSetSlot0660HighBits $01
    BogusAddSlotFields00 $06, $06
    BogusSetDispatchCounter $07
    BogusBranchAndClearSlot0620Bit08 ScriptB754
    BogusBranchIfSlot0360AtMost ScriptB77B, $00
    BogusBranchIfSlotB0AtMost ScriptB74E, $14
    BogusAdvanceAndBranchState1B ScriptB741, $C0
    BogusAdvanceAndBranchState1B ScriptB748, $80
    BogusStartVoice4 $37AC
ScriptB741:
    BogusBranchIfSlotB0AtMost ScriptB71F, $D2
    BogusJumpBank1 ScriptB77B
ScriptB748:
    BogusStartVoice4 $37A3
    BogusJumpBank1 ScriptB741
ScriptB74E:
    BogusSetSlotFields80 $FF, $00
    BogusJumpBank1 ScriptB71F
ScriptB754:
    BogusSetDispatchCounter $84
    BogusSetSlot0790Bits $01
    BogusLoadSlotRecord $00, $02
    BogusSetSlot0660HighBits $00
    BogusSetSlot0660LowBits $00
    BogusSetSlotFields40Signed $E8, $FF
    BogusSetSlotFields80 $FF, $C0
ScriptB765:
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual ScriptB765, $FFFF
    BogusSetSlotFields80 $30, $FF
ScriptB76E:
    BogusBranchIfSlotB0AtMost ScriptB779, $10
    BogusBranchIfAbsSlot0700Below ScriptB779, $0A
    BogusJumpBank1 ScriptB76E
ScriptB779:
    BogusYieldAndSlotAction $01
ScriptB77B:
    BogusSetSlot0660HighBits $00
    BogusSetSlotFields80 $FF, $C0
ScriptB780:
    BogusBranchIfSlotB0AtMost ScriptB6EE, $3C
    BogusJumpBank1 ScriptB780
.assert (* - BankStart) = $3787, error, "bank 1 script B6EE end"
; Possible contact-event script; descriptor association and execution are provisional.
ContactScriptB787:
    BogusBranchIfSelectedFieldEqual ContactScriptB78C, $1D ; CONTROL_CONTACT_SCRIPT_B787
    BogusRestoreSavedScriptAndSlotFlags
ContactScriptB78C:
    BogusSetSlot0660LowBits $00
    BogusSetSlot0660HighBits $00
    BogusSetSlot0670Pair $00, $80
    BogusSetLinkedSlotFieldsC0 $20, $FF
    BogusSetSlotFields80 $FF, $C0
    BogusWait $04
    BogusSetSlotC0 $FF
ContactScriptB79D:
    BogusBranchIfSlotB0AtMost ContactScriptB79D, $E6
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $37A3, error, "bank 1 contact script B787 end"
    .incbin "bank1_b7a3_b7b5.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB7B5:
    SlotRuntimeRecord $BC83, (CandidateB7C7 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B7B5
.assert (* - BankStart) = $37BE, error, "bank 1 slot record B7B5 end"
; Zero-mode record observed in longer exploratory gameplay.
; Fields after a $FFFF resource pointer may be skipped by the loader.
LongRecordB7BE:
    SlotRuntimeRecord $BA1A, $FFFF, $00, $FE, $20, $40, $11 ; CONTROL_LONG_RECORD_B7BE
.assert (* - BankStart) = $37C7, error, "bank 1 long-run records $B7BE end"
; Candidate script path; object role and execution remain unverified.
CandidateB7C7:
    BogusSetSlotC0 $00 ; CONTROL_BOGUS_B7C7
    BogusSetSlot0360 $32
    BogusSetSlotBit40 $01
    BogusSetSlot0670Pair $01, $00
CandidateB7D0:
    BogusBranchIfSlot0360AtMost CandidateB7DC, $00
    BogusBranchIfSlotCoordinatesA3 CandidateB7DC, $10, $18
    BogusJumpBank1 CandidateB7D0
CandidateB7DC:
    BogusLoadRecordAndClearSavedState $09
.assert (* - BankStart) = $37DE, error, "bank 1 candidate script B7C7 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptB7DE:
    BogusStartVoice4 $272F ; CONTROL_LONG_SCRIPT_B7DE
LongScriptB7E1:
    BogusWait $0F
LongScriptB7E3:
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $37E5, error, "bank 1 long-run script $B7DE end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB7E5:
    SlotRuntimeRecord $B945, (CandidateB809 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B7E5
.assert (* - BankStart) = $37EE, error, "bank 1 slot record B7E5 end"
; Observed in zero mode; fields gated by $FFFF may be skipped.
InteractionRecordB7EE:
    SlotRuntimeRecord $C5B9, (InteractionScriptB87D - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_INTERACTION_RECORD_B7EE
.assert (* - BankStart) = $37F7, error, "bank 1 interaction record $B7EE end"
; Candidate descriptor $B7E5, command $B831, mode $00.
SlotFlowB7F7:
    SlotRuntimeRecord $B930, $3833, $00, $FE, $40, $41, $41 ; CONTROL_SLOT_FLOW_B7F7
; Candidate descriptor $B7E5, command $B872, mode $00.
SlotFlowB800:
    SlotRuntimeRecord $B93E, $387A, $40, $FF, $00, $00, $00
.assert (* - BankStart) = $3809, error, "bank 1 slot record flow B7F7 end"
; Candidate script path; object role and execution remain unverified.
CandidateB809:
    BogusSetDispatchCounter $8B ; CONTROL_BOGUS_B809
    BogusRestartVoice4 $2745
    BogusSetSlotC0 $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot07F0 $60
    BogusBranchIfSlot0630Bit02 CandidateB81B
    BogusAdjustSlotBounds $04, $00
CandidateB81B:
    BogusClearSlot0790Bits $01
    BogusSetSlotFields80 $00, $07
    BogusBranchIfSlotB0AtMost CandidateB82D, $74
    BogusSetSlotFields80 $00, $F9
    BogusBranchIfSlot0630Bit02 CandidateB82D
    BogusAdjustSlotBounds $00, $EC
CandidateB82D:
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetDirectionalSlotFields40 $FF, $09
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $3833, error, "bank 1 candidate script B809 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptB833:
    BogusReadSlotValue $12 ; CONTROL_CONTEXT_B833
    BogusBranchIfSlotValueAtLeast ContextScriptB857, $0080
    BogusBranchIfPositiveOffsetProbe ContextScriptB874, $03
    BogusBranchIfSlotB0AtMost ContextScriptB845, $DC
    BogusJumpBank1 ContextScriptB874
ContextScriptB845:
    BogusSetSlotValue $2404
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 ContextScriptB86D, $008C
    BogusLookupCaseBank1 ContextScriptB86D, $008D
    BogusLookupEnd
    BogusJumpBank1 ContextScriptB833
ContextScriptB857:
    BogusBranchIfSlotB0AtMost ContextScriptB874, $30
    BogusSetSlotValue $FF04
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 ContextScriptB86D, $006C
    BogusLookupCaseBank1 ContextScriptB86D, $006D
    BogusLookupEnd
    BogusJumpBank1 ContextScriptB833
ContextScriptB86D:
    BogusSetSlot07F0 $80
    BogusSetSlotFields80 $00, $00
    BogusLoadRecordAndClearSavedState $1B
ContextScriptB874:
    BogusSetDirectionalSlotFields40 $FF, $E0
    BogusJumpBank1 ContextScriptB833
ContextScriptB87A:
    BogusCheckSlotFlagsAndRestorePointer
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $387D, error, "bank 1 contextual script B833 end"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptB87D:
    BogusSetSlotC0 $FF ; CONTROL_INTERACTION_SCRIPT_B87D
InteractionScriptB87F:
    BogusSetSlotMode $FF
InteractionScriptB881:
    BogusSetLinkedSlotFieldsC0 $40, $A0
InteractionScriptB884:
    BogusBranchIfSlotB0AtMost InteractionScriptB884, $E6
InteractionScriptB888:
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $388A, error, "bank 1 interaction script $B87D end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB88A:
    SlotRuntimeRecord $B5FD, (ScriptB89C - BankStart), $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_B88A
.assert (* - BankStart) = $3893, error, "bank 1 slot record B88A end"
; Candidate descriptor $B88A, script $B8E8, mode $02.
ModeRecordB893Resource:
    .word $B5FD ; CONTROL_MODE_RECORD_B893_RESOURCE
.assert (* - BankStart) = $3895, error, "bank 1 candidate mode record b893 resource end"
    .incbin "bank1_b895_b897.bin"
; Candidate descriptor $B88A, script $B8E8, mode $02.
ModeRecordB893Fields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_B893_FIELDS
.assert (* - BankStart) = $389C, error, "bank 1 candidate mode record b893 fields end"
; Slot-field updates and conditional checks lead to one of several loops or
; a slot release. The script's gameplay role remains provisional.
ScriptB89C:
    BogusSetSlot0730 $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlotMode $02
    BogusSetSlot05F0Pair $40, $58
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0360 $3C         ; CONTROL_BOGUS_B89C
    BogusSetSlotFields80 $10, $FF
    BogusAdvanceAndBranchState1B ScriptB8B5, $80
    BogusSetSlotFields80 $F0, $FF
ScriptB8B5:
    BogusAdvanceAndBranchState1B ScriptB8BC, $80
    BogusSetDirectionalSlotFields40 $10, $FF
ScriptB8BC:
    BogusSetDispatchCounter $85
    BogusSetSlot0620Bit20
    BogusBranchIfSlot0620Bit10Clear ScriptB8CB
    BogusRestartVoice4 $2724
    BogusAddSlotFields00 $FF, $E8
    BogusJumpBank1 ScriptB8BC
ScriptB8CB:
    BogusSetDispatchCounter $03
    BogusBranchAndClearSlot0620Bit08 ScriptB8E8
    BogusBranchIfAbsSlot0700Below ScriptB8E0, $0C
    BogusBranchIfSlot0360Above ScriptB8BC, $00
ScriptB8D8:
    BogusSetSlotMode $FF
ScriptB8DA:
    BogusBranchIfSlotB0AtMost ScriptB8DA, $E6
    BogusYieldAndSlotAction $00
ScriptB8E0:
    BogusSetSlotFields40Signed $18, $00
    BogusWait $04
    BogusJumpBank1 ScriptB8BC
ScriptB8E8:
    BogusLoadSlotRecord $09, $02
    BogusJumpBank1 ScriptB8D8
.assert (* - BankStart) = $38EE, error, "bank 1 script B89C end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB8EE:
    SlotRuntimeRecord $B9FF, (ScriptB900 - BankStart), $22, $00, $20, $01, $01 ; CONTROL_SLOT_RUNTIME_B8EE
.assert (* - BankStart) = $38F7, error, "bank 1 slot record B8EE end"
    .incbin "bank1_b8f7_b900.bin"
; Descriptor-derived script. Nonzero record mode preserves the command pointer;
; the record-loading helper's gameplay effects remain provisional.
ScriptB900:
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0730 $DC         ; CONTROL_BOGUS_B900
    BogusSetUnlinkedFields $00, $00
    BogusRestartVoice4 $289B
    BogusBranchIfSlot0700AtMost ScriptB915, $80
    BogusSetSlotFields80 $E8, $00
    BogusJumpBank1 ScriptB918
ScriptB915:
    BogusSetSlotFields80 $18, $00
ScriptB918:
    BogusWait $04
ScriptB91A:
    BogusSetSlot0620Bit20
    BogusBranchIfAbsSlot0700Below ScriptB934, $0C
    BogusBranchIfSlot0620Bit10 ScriptB928
    BogusBranchAndClearSlot0620Bit08 ScriptB92E
    BogusJumpBank1 ScriptB91A
ScriptB928:
    BogusStartVoice4 $289B
    BogusJumpBank1 ScriptB91A
ScriptB92E:
    BogusLoadSlotRecord $09, $02
.assert (* - BankStart) = $3931, error, "bank 1 script B900 block end"
    BogusJumpBank1 ScriptB91A    ; CONTROL_BOGUS_B931
ScriptB934:
    BogusYieldAndSlotAction $00  ; CONTROL_BOGUS_B934
.assert (* - BankStart) = $3936, error, "bank 1 script B934 end"
; Observed in zero and negative modes: byte 2 is both script-pointer low
; (zero mode) and flags (negative mode); both interpretations share bytes.
ExtendedRecordB936:
    SlotRuntimeRecord $BC79, $FFFF, $00, $FF, $00, $00, $00 ; CONTROL_EXTENDED_RECORD_B936
.assert (* - BankStart) = $393F, error, "bank 1 dual-mode record $B936 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB93F:
    SlotRuntimeRecord $BC79, $3948, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B93F
.assert (* - BankStart) = $3948, error, "bank 1 slot record B93F end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptB948:
    BogusSetSlotC0 $00 ; CONTROL_CONTEXT_B948
    BogusInitializeOtherSlotRelative $04, $00, $00, $00
    BogusWait $05
    BogusInitializeOtherSlotRelative $04, $00, $00, $00
    BogusWait $05
    BogusInitializeSlotMotionFields
    BogusSetSlotFields80 $00, $00
    BogusLoadSlotRecordAtPointer $395F
.assert (* - BankStart) = $395F, error, "bank 1 contextual script B948 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB95F:
    SlotRuntimeRecord $C7DB, (ScriptB968 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B95F
.assert (* - BankStart) = $3968, error, "bank 1 slot record B95F end"
; Eight slot-field updates form a loop while $0360 is above the threshold.
; Slot action $00 yields and releases the current slot.
ScriptB968:
    BogusSetSlotC0 $00
    BogusSetSlot0360 $14         ; CONTROL_BOGUS_B968
    BogusSetSlot07F0 $01
    BogusSetSlotBit40 $01
ScriptB970:
    BogusSetSlotFields80 $F0, $F0
    BogusSetSlotFields80 $F8, $E8
    BogusSetSlotFields80 $F8, $E8
    BogusSetSlotFields80 $10, $F0
    BogusSetSlotFields80 $10, $F0
    BogusSetSlotFields80 $08, $E8
    BogusSetSlotFields80 $08, $E8
    BogusSetSlotFields80 $F0, $F0
    BogusBranchIfSlot0360Above ScriptB970, $01
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $398E, error, "bank 1 script B968 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptB98E:
    BogusYieldAndSlotAction $00 ; CONTROL_EXTENDED_SCRIPT_B98E
.assert (* - BankStart) = $3990, error, "bank 1 extended script $B98E end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeB990:
    SlotRuntimeRecord $BC79, (ScriptB999 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_B990
.assert (* - BankStart) = $3999, error, "bank 1 slot record B990 end"
; The indexed bases below are local data. The command at $B99E clears a
; stack-page bitset; its runtime stack interaction needs separate validation.
ScriptB999:
    BogusSetDispatchCounter $9F
    BogusBranchIfState58ZeroAndClear ScriptB9A0
    BogusClearSlotBitset $FF
ScriptB9A0:
    BogusSetInvertedState18 $01
    BogusReadSlotValue $0F
    BogusLoadSlotValueIndexedBank1 DataB9E5
    BogusStoreSlotValueArray $3C
    BogusReadSlotValue $0F
    BogusLoadSlotValueIndexedBank1 DataB9FB
    BogusStoreSlotValueArray $29
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $24
    BogusStoreSlotValueArray $33
    BogusStoreSlotValueArray $34
    BogusStoreSlotValueArray $35
    BogusStoreSlotValueArray $36
    BogusStoreSlotValueArray $37
    BogusStoreSlotValueArray $38
    BogusStoreSlotValueArray $39
    BogusStoreSlotValueArray $3A
    BogusStoreSlotValueArray $3B
    BogusStoreSlotValueArray $2A
    BogusSetSlotValue $0005       ; CONTROL_BOGUS_B999
    BogusStoreSlotValueArray $2B
    BogusReadSlotValue $0F
    BogusLoadSlotValueIndexedBank1 DataB9E0
    BogusStoreSlotValueArray $32
    BogusSetVoicePointers $2AD8, $FFFF, $FFFF, $FFFF
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $39E0, error, "bank 1 script B999 end"
; Two-byte indexed reads can cross this label and the adjacent region.
DataB9E0:
    .byte $00, $06, $07, $08, $08 ; CONTROL_EXTENDED_STATE_B9E0
.assert (* - BankStart) = $39E5, error, "bank 1 state bytes $B9E0 end"
; Two-byte indexed reads can cross this label and the adjacent region.
DataB9E5:
    .byte $F0, $F0, $F0, $F0, $F0, $FB, $FB, $FB ; CONTROL_EXTENDED_STATE_B9E5
    .byte $FB, $FB, $FB, $FA, $FA, $FA, $FA, $FA
    .byte $F0, $F0, $F0, $F0, $F0, $F0
.assert (* - BankStart) = $39FB, error, "bank 1 state bytes $B9E5 end"
; Two-byte indexed reads can cross this label and the adjacent region.
DataB9FB:
    .byte $E0, $E0, $E0, $E0, $E0, $DA, $DA, $DA ; CONTROL_EXTENDED_STATE_B9FB
    .byte $DA, $DA, $DA, $E0, $E0, $E0, $E0, $E0
    .byte $E0, $E0, $E0, $E0, $E0, $E0
.assert (* - BankStart) = $3A11, error, "bank 1 state bytes $B9FB end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBA11:
    SlotRuntimeRecord $C4BF, (CandidateBA23 - BankStart), $00, $00, $30, $70, $11 ; CONTROL_SLOT_RUNTIME_BA11
.assert (* - BankStart) = $3A1A, error, "bank 1 slot record BA11 end"
; Resource pointer read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordBA1AResource:
    .word $B8AF ; CONTROL_PARTIAL_RESOURCE_BA1A
.assert (* - BankStart) = $3A1C, error, "bank 1 partial record $BA1A end"
    .incbin "bank1_ba1c_ba1e.bin"
; Mode-specific flags and fields read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordBA1AFields:
    .byte $40 ; CONTROL_PARTIAL_FIELDS_BA1A
.assert (* - BankStart) = $3A1F, error, "bank 1 partial record $BA1E end"
    .incbin "bank1_ba1f_ba23.bin"
; Candidate script path; object role and execution remain unverified.
CandidateBA23:
    BogusSetDispatchCounter $08 ; CONTROL_BOGUS_BA23
    BogusSetSlotC0 $00
    BogusBranchIfSlot0630Bit02 CandidateBA2D
    BogusAdjustSlotBounds $00, $FD
CandidateBA2D:
    BogusSetSlot07F0 $01
    BogusSetSlot0670Pair $05, $40
CandidateBA32:
    BogusBranchIfSlotCoordinatesA3 CandidateBA3A, $08, $08
    BogusJumpBank1 CandidateBA32
CandidateBA3A:
    BogusSetSlot0620Bit20
    BogusStartVoice4 $2887
    BogusLoadSlotRecord $09, $01
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetDispatchCounter $03
    BogusBranchAndClearSlot0620Bit08 CandidateBA47
CandidateBA47:
    BogusJumpBank1 CandidateBA32
.assert (* - BankStart) = $3A4A, error, "bank 1 candidate script BA23 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBA4A:
    SlotRuntimeRecord $B6AC, (ScriptBA53 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BA4A
.assert (* - BankStart) = $3A53, error, "bank 1 slot record BA4A end"
; This descriptor-derived entry reaches a self-loop after setting two fields.
ScriptBA53:
    BogusSetSlotC0 $00
    BogusSetSlotBit40 $01       ; CONTROL_BOGUS_BA53
ScriptBA57:
    BogusJumpBank1 ScriptBA57
.assert (* - BankStart) = $3A5A, error, "bank 1 script BA53 end"
; Candidate descriptor $BA63, command $BB04, mode $FF.
SlotFlowBA5A:
    SlotCompactRecord $C723, $00 ; CONTROL_SLOT_FLOW_BA5A
; Candidate descriptor $BA63, command $BAE7, mode $FF.
SlotFlowBA5D:
    SlotCompactRecord $B9C3, $40
.assert (* - BankStart) = $3A60, error, "bank 1 slot record flow BA5A end"
; Compact record observed in negative loader mode.
SweepRecordBA60:
    SlotCompactRecord $B9B8, $00 ; CONTROL_SWEEP_RECORD_BA60
.assert (* - BankStart) = $3A63, error, "bank 1 sweep record $BA60 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBA63:
    SlotRuntimeRecord $B9B8, (ScriptBA75 - BankStart), $00, $00, $20, $61, $11 ; CONTROL_SLOT_RUNTIME_BA63
.assert (* - BankStart) = $3A6C, error, "bank 1 slot record BA63 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordBA6C:
    SlotRuntimeRecord $FFFF, (SweepScriptBB20 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_BA6C
.assert (* - BankStart) = $3A75, error, "bank 1 sweep record $BA6C end"
; This entry selects offsets using a slot-value lookup.
ScriptBA75:
    BogusSetDispatchCounter $8A
    BogusRestartVoice4 $2745
    BogusReadSlotValue $0F
    BogusLookupSlotValue
    BogusLookupCaseBank1 ScriptBA95, $0005 ; CONTROL_BOGUS_BA75
    BogusLookupCaseBank1 ScriptBA95, $0006
    BogusLookupCaseBank1 ScriptBA9B, $0007
    BogusLookupCaseBank1 ScriptBA9B, $0008
    BogusLookupEnd
    BogusSetSlot05F0Pair $18, $7E
    BogusJumpBank1 ScriptBA9E
ScriptBA95:
    BogusSetSlot05F0Pair $08, $7E
    BogusJumpBank1 ScriptBA9E
ScriptBA9B:
    BogusSetSlot05F0Pair $10, $7E
ScriptBA9E:
    BogusSetUnlinkedFields $00, $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot0660LowBits $00
    BogusClearSlot0790Bits $01
    BogusSetSlotValue $0003
    BogusStoreSlotValueArray $FF
    BogusSetSlot0670Pair $01, $00
ScriptBAB0:
    BogusSetSlotFields40Signed $18, $00
    BogusWait $08
ScriptBAB5:
    BogusLoadSlotRecord $00, $02
ScriptBAB8:
    BogusBranchIfAbsSlot0700Below ScriptBB11, $18
    BogusSetSlot0620Bit20
.assert (* - BankStart) = $3ABD, error, "bank 1 script BA75 block end"
    BogusBranchIfRemainingVerticalOffsetAtMost ScriptBB0F, $000F ; CONTROL_BOGUS_BABD
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptBAD1, $0080
    BogusBranchIfSlotOffset ScriptBB11, $02, $00
    BogusJumpBank1 ScriptBAD6
ScriptBAD1:
    BogusBranchIfSlotOffset ScriptBB11, $FE, $00
ScriptBAD6:
    BogusSetSlot0620Bit20
    BogusBranchIfSlotFieldsWithin ScriptBAB0, $01, $FF
    BogusAdvanceAndBranchState1B ScriptBAB8, $FA
    BogusSetSlotFields80 $00, $FF
    BogusWait $0A
    BogusSetSlot0660LowBits $01
    BogusLoadSlotRecord $06, $FF
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $18, $82
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $82
    BogusSetSlotFields80 $FF, $82
    BogusSetSlotFields80 $FF, $82
ScriptBAFA:
    BogusBranchIfSlotFieldsWithin ScriptBB02, $FF, $10
    BogusJumpBank1 ScriptBAFA
ScriptBB02:
    BogusSetSlot0660LowBits $00
    BogusLoadSlotRecord $09, $FF
ScriptBB07:
    BogusBranchIfSlot0620Bit10 ScriptBAB5
    BogusSetSlot0620Bit20
    BogusBranchIfSlotB0AtMost ScriptBB07, $DE
ScriptBB0F:
    BogusYieldAndSlotAction $00
ScriptBB11:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $E8, $FF
ScriptBB19:
    BogusBranchIfAbsSlot0700Below ScriptBB19, $18
    BogusJumpBank1 ScriptBAD6
.assert (* - BankStart) = $3B20, error, "bank 1 script BABD end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptBB20:
    BogusReadSlotValue $23 ; CONTROL_SWEEP_SCRIPT_BB20
SweepScriptBB22:
    BogusLookupSlotValue
.assert (* - BankStart) = $3B23, error, "bank 1 sweep script $BB20 end"
; Slot-value cases for the preceding $95 command, followed by a zero target.
    BogusLookupCaseBank1 SweepScriptBB30, $0063 ; CONTROL_SWEEP_LOOKUP_BB23
    BogusLookupCaseBank1 (BankStart + $3B4C), $006D
    BogusLookupEnd
.assert (* - BankStart) = $3B2D, error, "bank 1 sweep lookup $BB23 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptBB2D:
    BogusJumpBank1 RuntimeScriptE764
SweepScriptBB30:
    BogusLoadSlotRecord $06, $FF ; CONTROL_SWEEP_SCRIPT_BB2D
SweepScriptBB33:
    BogusSetSlotFields80 $FF, $82
SweepScriptBB36:
    BogusSetSlotFields80 $FF, $82
SweepScriptBB39:
    BogusClearSlot0790Bits $01
SweepScriptBB3B:
    BogusBranchIfSlotFieldsWithin SweepScriptBB43, $FF, $10
SweepScriptBB40:
    BogusJumpBank1 SweepScriptBB3B
SweepScriptBB43:
    BogusLoadSlotRecord $09, $FF
SweepScriptBB46:
    BogusBranchIfSlot0620Bit10 (BankStart + $3AB5)
SweepScriptBB49:
    BogusJumpBank1 SweepScriptBB46
.assert (* - BankStart) = $3B4C, error, "bank 1 sweep script $BB2D end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptBB4C:
    BogusSetSlotFields80 $00, $FF ; CONTROL_PATH_SCRIPT_BB4C
PathScriptBB4F:
    BogusJumpBank1 RuntimeScriptE764
.assert (* - BankStart) = $3B52, error, "bank 1 candidate successor $BB4C end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBB52:
    SlotRuntimeRecord $B977, $3B5B, $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BB52
.assert (* - BankStart) = $3B5B, error, "bank 1 slot record BB52 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptBB5B:
    BogusSetSlotC0 $00 ; CONTROL_CONTEXT_BB5B
    BogusCheckSlotFlagsAndRestorePointer
    BogusYieldAndSlotAction $01
.assert (* - BankStart) = $3B60, error, "bank 1 contextual script BB5B end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBB60:
    SlotRuntimeRecord $C69B, (ScriptBB69 - BankStart), $00, $00, $00, $F0, $11 ; CONTROL_SLOT_RUNTIME_BB60
.assert (* - BankStart) = $3B69, error, "bank 1 slot record BB60 end"
; This connected graph tests two map positions, uses lookup tables and updates
; slot bounds. Its labels describe control flow rather than inferred game roles.
ScriptBB69:
    BogusSetDispatchCounter $09
    BogusSetSlotC0 $00
    BogusBranchIfSlot0630Bit02 ScriptBB73
    BogusAdjustSlotBounds $00, $FD ; CONTROL_BOGUS_BB69
ScriptBB73:
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot07F0 $01
    BogusSetSlotValue $0000
    BogusBranchIfSlot0700AtMost ScriptBB82, $80
    BogusSetSlotValue $0001
ScriptBB82:
    BogusStoreSlotValueArray $FF
    BogusJumpBank1 ScriptBB8A
ScriptBB87:
    BogusSetDispatchCounter $03
    BogusSetSlot0620Bit20
ScriptBB8A:
    BogusBranchAndClearSlot0620Bit08 ScriptBC14
    BogusLoadSlotValueArray $FF
    BogusBranchIfSlotValueEqual ScriptBBB8, $01, $00
    BogusBranchIfSlot0700AtMost ScriptBB9B, $D0
    BogusJumpBank1 ScriptBBAE
ScriptBB9B:
    BogusSetSlotValue $041C
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 ScriptBC06, $00ED
    BogusLookupCaseBank1 ScriptBBE5, $00FE
    BogusLookupCaseBank1 ScriptBBE5, $00FF
    BogusLookupEnd
ScriptBBAE:
    BogusLoadSlotValueArray $FF
    BogusXorSlotValue $0001
    BogusStoreSlotValueArray $FF
    BogusJumpBank1 ScriptBB8A
ScriptBBB8:
    BogusBranchIfSlot0700AtMost ScriptBBAE, $30
    BogusSetSlotValue $04FC
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 ScriptBBF3, $00ED
    BogusLookupCaseBank1 ScriptBBD2, $00FE
    BogusLookupCaseBank1 ScriptBBD2, $00FF
    BogusLookupEnd
    BogusJumpBank1 ScriptBBAE
ScriptBBD2:
    BogusSetDispatchCounter $02
    BogusBranchIfSlot0700AtMost ScriptBC0C, $12
    BogusAdjustSlotBounds $F0, $00
ScriptBBDB:
    BogusSetSlot0360 $08
ScriptBBDD:
    BogusBranchIfSlot0360AtMost ScriptBB87, $00
    BogusSetSlot0620Bit20
    BogusJumpBank1 ScriptBBDD
ScriptBBE5:
    BogusSetDispatchCounter $02
    BogusBranchIfSlot0700AtMost ScriptBBED, $ED
    BogusYieldAndSlotAction $00
ScriptBBED:
    BogusAdjustSlotBounds $10, $00
    BogusJumpBank1 ScriptBBDB
ScriptBBF3:
    BogusSetDispatchCounter $02
    BogusBranchIfSlot0700AtMost ScriptBC0C, $0A
    BogusAdjustSlotBounds $F8, $00
ScriptBBFC:
    BogusSetSlot0360 $04
ScriptBBFE:
    BogusBranchIfSlot0360AtMost ScriptBB87, $00
    BogusSetSlot0620Bit20
    BogusJumpBank1 ScriptBBFE
ScriptBC06:
    BogusSetDispatchCounter $02
    BogusBranchIfSlot0700AtMost ScriptBC0E, $F5
ScriptBC0C:
    BogusYieldAndSlotAction $00
ScriptBC0E:
    BogusAdjustSlotBounds $08, $00
    BogusJumpBank1 ScriptBBFC
ScriptBC14:
    BogusWait $14
    BogusJumpBank1 ScriptBB87
.assert (* - BankStart) = $3C19, error, "bank 1 script BB69 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBC19:
    SlotRuntimeRecord $BC7D, (ScriptBC22 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BC19
.assert (* - BankStart) = $3C22, error, "bank 1 slot record BC19 end"
; Candidate slot search and repeated palette/audio sequence.
ScriptBC22:
    BogusSetSlotBit40 $01 ; CONTROL_BOGUS_BC22
    BogusJumpBank1 ScriptBC3D
ScriptBC27:
    BogusBranchIfMatchingSlotReady ScriptBC27, $01, $08, $00
    BogusSetSlot0360 $1E
ScriptBC2F:
    BogusBranchIfSlot0360AtMost ScriptBC36, $00
    BogusJumpBank1 ScriptBC2F
ScriptBC36:
    BogusAdvanceAndBranchState1B ScriptBC3D, $A0
    BogusJumpBank1 ScriptBC27
ScriptBC3D:
    BogusBranchIfMatchingSlotReady ScriptBC27, $01, $08, $00
    BogusRestartVoice4 $28BA
    BogusWait $02
    BogusSetBackgroundPalettePointer $C864
    BogusWait $01
    BogusSetBackgroundPalettePointer $FFFF
    BogusWait $01
    BogusSetBackgroundPalettePointer $C864
    BogusWait $02
    BogusSetBackgroundPalettePointer $FFFF
    BogusAdvanceAndBranchState1B ScriptBC27, $80
    BogusRestartVoice4 $28BA
    BogusSetBackgroundPalettePointer $C864
    BogusWait $03
    BogusSetBackgroundPalettePointer $FFFF
    BogusJumpBank1 ScriptBC27
.assert (* - BankStart) = $3C6C, error, "bank 1 script BC22 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBC6C:
    SlotRuntimeRecord $BAB7, (CandidateBC75 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BC6C
.assert (* - BankStart) = $3C75, error, "bank 1 slot record BC6C end"
; Candidate script path; object role and execution remain unverified.
CandidateBC75:
    BogusSetSlotC0 $00 ; CONTROL_BOGUS_BC75
    BogusSetInvertedState18 $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetDirectionalSlotFields40 $FF, $F4
    BogusSetVoicePointers $2944, $29F4, $0000, $0000
    BogusSetSlotFields80 $08, $FF
CandidateBC8B:
    BogusSetSlotFields80 $FF, $F8
    BogusSetDispatchCounter $81
    BogusSetSlotFields80 $FF, $08
    BogusBranchIfSlot0700AtMost CandidateBC8B, $F0
    BogusRestartVoice4 $0000
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusCallNativeEncoded $B51B
    BogusSetMainState $FF
.assert (* - BankStart) = $3CA8, error, "bank 1 candidate script BC75 end"
; Candidate descriptor $BCAE, command $BD03, negative mode.
CompactContextBCA8:
    SlotCompactRecord $C1E5, $00 ; CONTROL_COMPACT_CONTEXT_BCA8
.assert (* - BankStart) = $3CAB, error, "bank 1 compact candidate bca8 end"
; Candidate descriptor $BCAE, command $BCEB, negative mode.
CompactContextBCAB:
    SlotCompactRecord $B5DE, $00 ; CONTROL_COMPACT_CONTEXT_BCAB
.assert (* - BankStart) = $3CAE, error, "bank 1 compact candidate bcab end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBCAE:
    SlotRuntimeRecord $B5D3, (ScriptBCC0 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BCAE
.assert (* - BankStart) = $3CB7, error, "bank 1 slot record BCAE end"
    .incbin "bank1_bcb7_bcb8.bin"
; A possible contact event reads the resource sentinel and script pointer.
ContactRecordBCB8:
    .byte $FF ; CONTROL_CONTACT_RECORD_BCB8
    .word ContactScriptBCE3 - BankStart
.assert (* - BankStart) = $3CBB, error, "bank 1 contact record BCB8 end"
    .incbin "bank1_bcbb_bcc0.bin"
; Candidate entry from a slot descriptor. The full graph is contained here;
; gameplay role and runtime use are not yet established.
ScriptBCC0:
    BogusSetSlotC0 $00
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusSetUnlinkedFields $00, $00
    BogusSetSlotBit40 $01
    BogusClearSlot0790Bits $01
    BogusWait $05                ; CONTROL_BOGUS_BCC0
ScriptBCC0Loop:
    BogusSetSlotFields80 $FF, $F8
    BogusWait $02
    BogusSetSlotFields80 $FF, $08
    BogusWait $01
    BogusSetDispatchCounter $01
    BogusJumpBank1 ScriptBCC0Loop
.assert (* - BankStart) = $3CE3, error, "bank 1 script BCC0 end"
; Possible contact-event path. Mode-dependent record targets and its indirect
; slot-field write have not been checked in gameplay.
ContactScriptBCE3:
    BogusBranchIfSelectedFieldEqual ContactScriptBCF3, $01 ; CONTROL_CONTACT_SCRIPT_BCE3
    BogusBranchIfSelectedFieldEqual ContactScriptBD06, $02
    BogusLoadSlotRecord $03, $FF
    BogusClearSlot0790Bits $01
    BogusJumpBank1 ScriptBCC0Loop
ContactScriptBCF3:
    BogusMarkMatchingSlots $00, $01, $64, $00
    BogusSetSlotValue $000C
    BogusStoreSlotLowAt $05E2
    BogusSetSlotFields80 $00, $00
    BogusWait $01
    BogusLoadSlotRecord $06, $FF
ContactScriptBD06:
    BogusJumpBank1 ContactScriptBD06
.assert (* - BankStart) = $3D09, error, "bank 1 contact script BCE3 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBD09:
    SlotRuntimeRecord $B7F2, (ScriptBD1B - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BD09
.assert (* - BankStart) = $3D12, error, "bank 1 slot record BD09 end"
    .incbin "bank1_bd12_bd13.bin"
; A possible contact event reads the resource sentinel and script pointer.
ContactRecordBD13:
    .byte $FF ; CONTROL_CONTACT_RECORD_BD13
    .word ContactScriptBD4D - BankStart
.assert (* - BankStart) = $3D16, error, "bank 1 contact record BD13 end"
    .incbin "bank1_bd16_bd1b.bin"
; Repeated slot-record and voice-pointer sequence with the original retry.
ScriptBD1B:
    BogusSetDispatchCounter $85 ; CONTROL_BOGUS_BD1B
    BogusClearSlot0790Bits $01
    BogusSetSlotC0 $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot07F0 $02
ScriptBD26:
    BogusSetVoicePointers $FFFF, $FFFF, $2890, $0000
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetSlot07F0 $01
    BogusAdjustSlotBounds $28, $00
    BogusLoadSlotRecord $00, $01
    BogusSetVoicePointers $FFFF, $FFFF, $2890, $0000
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetSlot07F0 $02
    BogusAdjustSlotBounds $D8, $00
    BogusLoadSlotRecord $00, $01
    BogusJumpBank1 ScriptBD26
.assert (* - BankStart) = $3D4D, error, "bank 1 script BD1B end"
ContactScriptBD4D:
    BogusYieldAndSlotAction $00 ; CONTROL_CONTACT_SCRIPT_BD4D
.assert (* - BankStart) = $3D4F, error, "bank 1 contact script BD4D end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBD4F:
    SlotRuntimeRecord $BC79, (ScriptBD58 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BD4F
.assert (* - BankStart) = $3D58, error, "bank 1 slot record BD4F end"
; Connected slot, audio and fade state sequence.
ScriptBD58:
    BogusSetSlotC0 $00 ; CONTROL_BOGUS_BD58
    BogusSetInvertedState18 $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlotAssociation $00
    BogusSetSlotFields80 $00, $08
    BogusSetVoicePointers $2944, $29F4, $0000, $0000
ScriptBD6D:
    BogusBranchIfRemainingVerticalOffsetAtMost ScriptBD75, $002C
    BogusJumpBank1 ScriptBD6D
ScriptBD75:
    BogusSetSlotFields80 $00, $00
    BogusMarkMatchingSlots $00, $01, $17, $00
    BogusSetBackgroundPalettePointer $C8E2
    BogusInitializeOtherSlotAbsolute $26, $67, $B4, $00
    BogusSetSlotPositionFromOperands $00, $8C
    BogusSetSlotFields80 $00, $F8
ScriptBD8B:
    BogusBranchIfSlotB0AtMost ScriptBD92, $10
    BogusJumpBank1 ScriptBD8B
ScriptBD92:
    BogusMarkMatchingSlots $20, $01, $17, $00
ScriptBD97:
    BogusBranchIfSelectedFlagsClear ScriptBD97, $F0
    BogusSetSlotValue $001E
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $FFFF
    BogusStoreSlotValueArray $23
    BogusRestartVoice4 $0000
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusCallNativeEncoded Bank0::FadeOutPalettes - 1
    BogusSetMainState $10
.assert (* - BankStart) = $3DB6, error, "bank 1 script BD58 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBDB6:
    SlotRuntimeRecord $C269, (ScriptBDBF - BankStart), $00, $00, $00, $10, $06 ; CONTROL_SLOT_RUNTIME_BDB6
.assert (* - BankStart) = $3DBF, error, "bank 1 slot record BDB6 end"
; Another descriptor-derived graph: set a slot bit, then branch when bit $08
; is set and clear it. Both destinations are local loops.
ScriptBDBF:
    BogusSetSlotC0 $00
    BogusSetSpriteAttribute20 $20 ; CONTROL_BOGUS_BDBF
ScriptBDBFLoop:
    BogusSetSlot0620Bit20
    BogusBranchAndClearSlot0620Bit08 ScriptBDBFDone
    BogusJumpBank1 ScriptBDBFLoop
ScriptBDBFDone:
    BogusJumpBank1 ScriptBDBFDone
.assert (* - BankStart) = $3DCD, error, "bank 1 script BDBF end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBDCD:
    SlotRuntimeRecord $B64D, (ScriptBDD6 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BDCD
.assert (* - BankStart) = $3DD6, error, "bank 1 slot record BDCD end"
; Compare the slot value to $0001, choose a field update, wait, then loop
; until the magnitude of $0700 is below $10 and release the current slot.
ScriptBDD6:
    BogusSetSlotC0 $00
    BogusSetUnlinkedFields $00, $00
    BogusReadSlotValue $00
    BogusBranchIfSlotValueEqual ScriptBDE8, $01, $00
    BogusSetSlotFields80 $08, $00 ; CONTROL_BOGUS_BDD6
    BogusJumpBank1 ScriptBDEB
ScriptBDE8:
    BogusSetSlotFields80 $F8, $00
ScriptBDEB:
    BogusWait $08
ScriptBDED:
    BogusBranchIfAbsSlot0700Below ScriptBDF4, $10
    BogusJumpBank1 ScriptBDED
ScriptBDF4:
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $3DF6, error, "bank 1 script BDD6 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeBDF6:
    SlotRuntimeRecord $BC89, (ScriptBDFF - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_BDF6
.assert (* - BankStart) = $3DFF, error, "bank 1 slot record BDF6 end"
ScriptBDFF:
    BogusSetSlotC0 $00           ; CONTROL_BOGUS_BDFF
    BogusLoadSlotValueArray $3D
.assert (* - BankStart) = $3E03, error, "bank 1 script BDFF end"
ScriptBE03:
    BogusLookupSlotValue
    BogusLookupCaseBank1 ScriptBE26, $0027 ; CONTROL_BOGUS_BE03
    BogusLookupCaseBank1 ScriptBE26, $0029
    BogusLookupCaseBank1 ScriptBE26, $002E
    BogusLookupCaseBank1 ScriptBE26, $0030
    BogusLookupCaseBank1 ScriptBE26, $0031
    BogusLookupEnd
    BogusSetVoicePointers $2AD8, $0000, $0000, $0000
    BogusJumpBank1 ScriptBE2F
ScriptBE26:
    BogusSetVoicePointers $2C58, $2C70, $0000, $0000
ScriptBE2F:
    BogusSetSlotAssociation $00
    BogusSetSlotValue $0002
    BogusStoreSlotValueArray $FF
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueAtLeast ScriptCFC7, $00F8
    BogusMultiplySlotValueByArray $FF
.assert (* - BankStart) = $3E3F, error, "bank 1 script BE03 partial graph end"
    BogusLoadSlotValueIndexedBank1 DataBE82 ; CONTROL_BOGUS_BE3F
.assert (* - BankStart) = $3E42, error, "bank 1 script BE3F end"
; Set the two-byte text pointer, call the banked decoder until the selected
; array reaches $00FF, then wait for the selected input flags.
    BogusStoreSlotLowAt $0055   ; CONTROL_BOGUS_BE42
    BogusSwapSlotValueBytes
    BogusStoreSlotLowAt $0056
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $00
ScriptBE4E:
    BogusCallNativeBank1 DecodePackedText
    BogusRestartVoice4 $28AD
    BogusWait $03
    BogusLoadSlotValueArray $00
    BogusBranchIfSlotValueNotEqual ScriptBE4E, $00FF
    BogusRestartVoice4 $0000
ScriptBE60:
    BogusBranchIfSelectedFlags ScriptBE67, $F0
    BogusJumpBank1 ScriptBE60
ScriptBE67:
    BogusClearSelected3E
    BogusClearSelected40
    BogusCallNativeEncoded Bank0::FadeOutPalettes - 1
    BogusBranchIfState27Set ScriptBE81
    BogusLoadSlotValueArray $23
    BogusBranchIfSlotValueEqual ScriptBE81, $FF, $FF
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusSetMainState $00
ScriptBE81:
    BogusInitializeSplitAndMainState
.assert (* - BankStart) = $3E82, error, "bank 1 script BE42 end"
; Fifty-two CPU addresses select packed-text records in bank 1. The index is
; supplied by the script; runtime bounds and exact message roles are unknown.
DataBE82:
    .word $C03E, $C071, $C0AF, $C0EB ; CONTROL_PACKED_TEXT_POINTERS
    .word $C11A, $C160, $C179, $C19C
    .word $C1BE, $C1F4, $C24B, $C326
    .word $C364, $C399, $C40E, $C469
    .word $C494, $C4F1, $C540, $C666
    .word $C69A, $C6B7, $C701, $C73C
    .word $C7A2, $C7EF, $C832, $C872
    .word $C8B2, $C91C, $C966, $C9F9
    .word $CA51, $CAA4, $CAEE, $CB3D
    .word $CB87, $CBB7, $CBF2, $CC37
    .word $CC70, $CC93, $CD14, $CD69
    .word $CE92, $CEF8, $CF17, $CF2D
    .word $CF52, $CF6E, $CF8E, $CF9C
.assert (* - BankStart) = $3EEA, error, "bank 1 packed text pointer table end"
; Native helper reached by opcode $9B: consume packed five-bit symbols from
; ($55), fill the stack-page buffer, and queue it as a $BF state update.
; The exact higher-level message and control meanings remain provisional.
DecodePackedText:
    ldx #$00                    ; CONTROL_PACKED_TEXT_DECODE
    lda $0140
    bne PackedTextNextSymbol
    sta a:$52
    ldy #$00
    lda #$FF
    sta $0142
    lda ($55),y
    sta $0143
    iny
    lda ($55),y
    sta $0144
    lda #$7F
    sta $0140
    lda #$02
    clc
    adc a:$55
    sta a:$55
    lda a:$56
    adc #$00
    sta a:$56
    ldx #$03
PackedTextNextSymbol:
    jsr ReadPackedTextSymbol
    cmp #$0B
    beq PackedTextLineBreak
    cmp #$1A
    beq PackedTextFinish
    cmp #$00
    bne PackedTextPrimaryCharacter
    jsr ReadPackedTextSymbol
    tay
    lda PackedTextSecondaryCharacters,y
    jmp PackedTextStoreCharacter
PackedTextPrimaryCharacter:
    tay
    lda PackedTextPrimaryCharacters,y
PackedTextStoreCharacter:
    sta $0142,x
    inx
    txa
    pha
    pla
    tax
    jmp PackedTextNextSymbol
PackedTextFinish:
    lda #$FF
    sta $0140
    jmp PackedTextQueue
PackedTextLineBreak:
    lda #$FE
    sta $0142,x
    inx
    lda #$20
    sta $0142,x
    inx
    lda #$00
    sta $0142,x
    inx
PackedTextQueue:
    lda #$00
    sta $0142,x
    lda #$42
    sta a:$EA
    lda #$01
    sta a:$EB
    lda #$BF
    sta $04D9
    lda #$1C
    sta a:$E7
    rts
.assert (* - BankStart) = $3F7A, error, "bank 1 packed text decoder end"

; The eight phase entries describe masks, shifts and source-pointer advances
; for a five-bit stream. Absolute zero-page operands preserve the ROM encoding.
ReadPackedTextSymbol:
    ldy #$00
    lda ($55),y                 ; CONTROL_PACKED_TEXT_SYMBOL
    ldy a:$52
    and PackedTextFirstMasks,y
    pha
    lda PackedTextFirstShifts,y
    tay
    pla
    jsr ShiftPackedTextRight
    sta $0141
    ldy #$01
    lda ($55),y
    ldy a:$52
    and PackedTextSecondMasks,y
    pha
    lda PackedTextSecondShifts,y
    tay
    pla
    jsr ShiftPackedTextRight
    clc
    adc $0141
    pha
    ldy a:$52
    lda PackedTextAdvances,y
    clc
    adc a:$55
    sta a:$55
    lda a:$56
    adc #$00
    sta a:$56
    inc a:$52
    lda a:$52
    and #$07
    sta a:$52
    pla
    and #$1F
    rts
ShiftPackedTextRight:
    cpy #$00
    beq ShiftPackedTextReturn
    clc
ShiftPackedTextLoop:
    ror a
    dey
    bne ShiftPackedTextLoop
ShiftPackedTextReturn:
    rts
.assert (* - BankStart) = $3FD6, error, "bank 1 packed text symbol helper end"

PackedTextFirstMasks:
    .byte $F8, $07, $3E, $01, $0F, $00, $03, $00 ; CONTROL_PACKED_TEXT_TABLES
PackedTextSecondMasks:
    .byte $00, $C0, $00, $F0, $80, $7C, $E0, $1F
PackedTextFirstShifts:
    .byte $03, $07, $01, $05, $08, $00, $06, $00
PackedTextSecondShifts:
    .byte $00, $06, $00, $04, $07, $02, $05, $00
PackedTextAdvances:
    .byte $00, $01, $00, $01, $00, $01, $00, $02
PackedTextPrimaryCharacters:
    .byte "| EOTAHINRS", $0A, "LDU.FMWYGPCBV,", $5C, "1:K<3"
PackedTextSecondaryCharacters:
    .byte "247J59!6;08", $27, "X-)*QZ?xxxxxxxxxxxxx"
.assert (* - BankStart) = $403E, error, "bank 1 packed text tables end"
    .incbin "bank1_c03e_cfc7.bin"
; This branch target adjusts the slot value and queues one of two state
; requests; downstream indirect operations remain local.
ScriptCFC7:
    BogusAddSlotValue $FF08     ; CONTROL_BOGUS_CFC7
    BogusBranchIfSlotValueNotEqual ScriptCFD7, $0002
    BogusQueueStateAB $5083
    BogusSetSlotD0Bits $01
    BogusJumpBank1 ScriptCFDA
ScriptCFD7:
    BogusQueueStateAB $5067
ScriptCFDA:
    BogusMultiplySlotValueByArray $FF
.assert (* - BankStart) = $4FDC, error, "bank 1 script CFC7 end"
; Continue the shared value-selection path. Indexed reads may extend beyond
; the named entries below; their runtime index bounds are not established.
    BogusClampSlotValueAtMost $0008 ; CONTROL_BOGUS_CFDC
    BogusLoadSlotValueIndexedBank1 DataD05F
    BogusQueueStateAB $0000
    BogusQueueStateAB $5099
    BogusSetSlotValue $FFFF
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $0000
ScriptCFF0:
    BogusSetDispatchCounter $8F
    BogusStoreSlotValueArray $FF
    BogusBranchIfSlotValueAtLeastArray $32, ScriptD052
    BogusAddSlotValue $0033
    BogusSwapSlotValueBytes
    BogusLoadPage0140BySlotHigh
    BogusMaskSlotValue $00FF
    BogusBranchIfSlotD0BitsClear ScriptD039, $01
    BogusBranchIfSlotValueEqual ScriptD00D, $07, $00
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3D
    BogusSwapSlotValueBytes
ScriptD00D:
    BogusOrSlotValue $8000
    BogusRemapSlotValue
    BogusRemapCase $8000, $50C9
    BogusRemapCase $8001, $50D2
    BogusRemapCase $8002, $50DB
    BogusRemapCase $8003, $50E4
    BogusRemapCase $8004, $50ED
    BogusRemapCase $8005, $50F6
    BogusRemapCase $8006, $50FF
    BogusRemapCase $8007, $5108
    BogusRemapEnd
    BogusQueueStateAB $0000
    BogusJumpBank1 ScriptD048
ScriptD039:
    BogusBranchIfSlotValueEqual ScriptD042, $06, $00
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3D
    BogusSwapSlotValueBytes
ScriptD042:
    BogusLoadSlotValueIndexedBank1 DataD09D
    BogusQueueStateAB $0000
ScriptD048:
    BogusSetDispatchCounter $8F
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $0001
    BogusJumpBank1 ScriptCFF0
ScriptD052:
    BogusBranchIfSelectedFlags ScriptD059, $B0
    BogusJumpBank1 ScriptD052
ScriptD059:
    BogusClearSelected3E
    BogusClearSelected40
    BogusCallNativeEncoded Bank0::FadeOutPalettes - 1
    BogusInitializeSplitAndMainState
.assert (* - BankStart) = $505F, error, "bank 1 script CFDC end"
DataD05F:
    ; Encoded bank-1 pointers into the locally supplied inventory lists.
    .word $5111, $518D, $51D8, $5143 ; CONTROL_INVENTORY_LIST_POINTERS
.assert (* - BankStart) = $5067, error, "bank 1 inventory list pointer entries end"
    .incbin "bank1_d067_d09d.bin"
DataD09D:
    ; Encoded pointers to four local inventory display templates.
    .word $50A5, $50AE, $50B7, $50C0 ; CONTROL_INVENTORY_TEMPLATE_POINTERS
.assert (* - BankStart) = $50A5, error, "bank 1 inventory template pointer entries end"
    .incbin "bank1_d0a5_d21c.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD21C:
    SlotRuntimeRecord $BF27, $522E, $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_D21C
.assert (* - BankStart) = $5225, error, "bank 1 slot record D21C end"
    .incbin "bank1_d225_d226.bin"
; A possible contact event reads the resource sentinel and script pointer.
ContactRecordD226:
    .byte $FF ; CONTROL_CONTACT_RECORD_D226
    .word ContactScriptD237 - BankStart
.assert (* - BankStart) = $5229, error, "bank 1 contact record D226 end"
    .incbin "bank1_d229_d22e.bin"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptD22E:
    BogusClearMatchingSlotFlag20 $01, $01, $00 ; CONTROL_CONTEXT_D22E
    BogusClearSlot0790Bits $01
ContextScriptD234:
    BogusJumpBank1 ContextScriptD234
.assert (* - BankStart) = $5237, error, "bank 1 contextual script D22E end"
; Possible contact-event sequence; the selected state and execution are unverified.
ContactScriptD237:
    BogusWait $0A ; CONTROL_CONTACT_SCRIPT_D237
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueEqual ContactScriptD242, $00, $00
    BogusWait $09
ContactScriptD242:
    BogusSelectStateTableValue $0F
    BogusAddSlotValue $00F7
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $FFFF
    BogusStoreSlotValueArray $23
    BogusCallNativeEncoded $B51B
    BogusSetMainState $10
.assert (* - BankStart) = $5253, error, "bank 1 contact script D237 end"
; Possible continuation after a direct-record load; runtime mode and reachability are unverified.
DirectNextScriptD253:
    BogusSetSlotC0 $00 ; CONTROL_DIRECT_NEXT_SCRIPT_D253
DirectNextScriptD255:
    BogusSetSlotFields80 $00, $00
DirectNextScriptD258:
    BogusSaveStateAndPlaceSlots $12
.assert (* - BankStart) = $525A, error, "bank 1 candidate successor $D253 end"
; Candidate continuation after $98 changes state and a later restore
; re-enables the retained slot. The state change does not itself prove resumption.
RestoreScriptD25A:
    BogusSetDispatchCounter $8F ; CONTROL_RESTORE_SCRIPT_D25A
    BogusSelectStateTableValue $AA
    BogusConfigureBanksFromOperand $00
    BogusSelectStateTableValue $4E
    BogusSetSpritePalettePointer $0000
    BogusSelectStateTableValue $0F
    BogusBranchIfSlotValueNotEqual RestoreScriptD272, $0004
    BogusSetBackgroundPalettePointer $C864
    BogusSetSpritePalettePointer $C818
RestoreScriptD272:
    BogusSetSlotValue $2E00
    BogusStoreSlotValueArray $3D
    BogusStoreSlotValueArray $FF
    BogusLoadPage0140BySlotHigh
    BogusMaskSlotValue $00FF
    BogusRemapSlotValue
.assert (* - BankStart) = $527E, error, "bank 1 restore candidate D25A end"
; Four-byte value/replacement cases; the handler fetches four bytes even
; when the two-byte zero terminator ends the table.
RestoreRemapD27E:
    BogusRemapCase $000E, $3302 ; CONTROL_RESTORE_REMAP_D27E
    BogusRemapCase $0015, $3304
    BogusRemapCase $0011, $3402
    BogusRemapCase $0012, $3404
    BogusRemapCase $001C, $3502
    BogusRemapCase $001D, $3504
    BogusRemapCase $001A, $3602
    BogusRemapCase $001B, $3604
    BogusRemapCase $002A, $3702
    BogusRemapCase $002B, $3704
    BogusRemapCase $0018, $3802
    BogusRemapCase $0019, $3804
    BogusRemapCase $002E, $3302
    BogusRemapCase $002F, $3304
    BogusRemapCase $0030, $3402
    BogusRemapCase $0031, $3404
    BogusRemapCase $0032, $3502
    BogusRemapCase $0033, $3504
    BogusRemapCase $0034, $3602
    BogusRemapCase $0035, $3604
    BogusRemapCase $0036, $3702
    BogusRemapCase $0037, $3704
    BogusRemapCase $0023, $3802
    BogusRemapCase $0024, $3804
    BogusRemapCase $0038, $3902
    BogusRemapCase $0039, $3904
    BogusRemapCase $0056, $3A02
    BogusRemapCase $0057, $3A04
    BogusRemapCase $004E, $3302
    BogusRemapCase $004F, $3304
    BogusRemapCase $003C, $3402
    BogusRemapCase $003D, $3404
    BogusRemapCase $003E, $3502
    BogusRemapCase $003F, $3504
    BogusRemapCase $0042, $3602
    BogusRemapCase $0043, $3604
    BogusRemapCase $0044, $3702
    BogusRemapCase $0045, $3704
    BogusRemapCase $0048, $3802
    BogusRemapCase $0049, $3804
    BogusRemapCase $004A, $3902
    BogusRemapCase $004B, $3904
    BogusRemapCase $005A, $3301
    BogusRemapCase $005B, $3401
    BogusRemapCase $0010, $3501
    BogusRemapCase $005E, $3601
    BogusRemapCase $005C, $3701
    BogusRemapCase $005F, $3801
    BogusRemapCase $0068, $3901
    BogusRemapCase $0069, $3A01
    BogusRemapEnd
.assert (* - BankStart) = $5348, error, "bank 1 restore remap D27E end"
RestoreScriptD348:
    BogusBranchIfSlotValueEqual RestoreScriptD399, $FF, $FF ; CONTROL_RESTORE_SCRIPT_D348
    BogusSetDispatchCounter $0C
    BogusStoreSlotValueArray $3D
    BogusLoadPage0140BySlotHigh
    BogusAddSlotValueFromArray $3D
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3D
    BogusSwapSlotValueBytes
    BogusMaskSlotValue $00FF
    BogusClampSlotValueAtMost $0007
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $3D
    BogusSwapSlotValueBytes
    BogusStoreSlotLowAtIndexedPage
    BogusSetDispatchCounter $08
    BogusLoadSlotValueArray $FF
    BogusLookupSlotValue
    BogusLookupCaseBank1 RestoreScriptD37A, $2B00
    BogusLookupCaseBank1 RestoreScriptD382, $2C00
    BogusLookupCaseBank1 RestoreScriptD38A, $2D00
    BogusLookupCaseBank1 RestoreScriptD392, $2E00
    BogusLookupEnd
RestoreScriptD37A:
    BogusClearRelatedSlotBit20 $01
    BogusMarkRelatedSlotAtDepth $28, $01
    BogusJumpBank1 RestoreScriptD397
RestoreScriptD382:
    BogusClearRelatedSlotBit20 $02
    BogusMarkRelatedSlotAtDepth $28, $02
    BogusJumpBank1 RestoreScriptD397
RestoreScriptD38A:
    BogusClearRelatedSlotBit20 $03
    BogusMarkRelatedSlotAtDepth $28, $03
    BogusJumpBank1 RestoreScriptD397
RestoreScriptD392:
    BogusClearRelatedSlotBit20 $04
    BogusMarkRelatedSlotAtDepth $28, $04
RestoreScriptD397:
    BogusWait $1B
RestoreScriptD399:
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $FF00
    BogusBranchIfSlotValueAtLeast (BankStart + $5277), $2B00
    BogusSetDispatchCounter $83
    BogusMarkMatchingSlots $00, $01, $13, $00
    BogusSetCurrentSlotBit20
    BogusJumpBank1 RestoreScriptB399
.assert (* - BankStart) = $53AE, error, "bank 1 restore candidate D348 end"
; A candidate direct $16 target. Its inherited mode is unknown: byte 2
; is negative-mode flags and also the skipped low byte of a $FFFF script
; sentinel in zero mode. The resource payload remains local.
RestoreRecordD3AE:
    SlotRuntimeRecord $BC89, $FFFF, $00, $FF, $00, $00, $00 ; CONTROL_RESTORE_RECORD_D3AE
.assert (* - BankStart) = $53B7, error, "bank 1 restore candidate record D3AE end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD3B7:
    SlotRuntimeRecord $C70D, (ScriptD3C9 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_D3B7
.assert (* - BankStart) = $53C0, error, "bank 1 slot record D3B7 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordD3C0:
    SlotRuntimeRecord $BC79, $FFFF, $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_D3C0
.assert (* - BankStart) = $53C9, error, "bank 1 sweep record $D3C0 end"
; Linked-slot update and position sequence.
ScriptD3C9:
    BogusSetSlot0640Pair $00, $40 ; CONTROL_BOGUS_D3C9
    BogusSetSlot05F0Pair $FF, $7E
    BogusSetSlotBit40 $01
ScriptD3D1:
    BogusBranchIfSlot0760Equal ScriptD3D8, $01
    BogusJumpBank1 ScriptD3D1
ScriptD3D8:
    BogusBranchIfSelectedFieldEqual ScriptD3DF, $10
    BogusJumpBank1 ScriptD3D1
ScriptD3DF:
    BogusSetSlotBit40 $FF
    BogusFollowLinkedSlotsAndYield $FF, $FF, $01, $01, $00
    BogusRestartVoice4 $26FA
    BogusSetLinkedFieldsAndYield $FF, $FE
    BogusSetLinkedFieldsAndYield $FF, $FC
    BogusSetLinkedFieldsAndYield $FF, $F8
    BogusSetLinkedFieldsAndYield $FF, $F4
    BogusSetLinkedFieldsAndYield $80, $F2
    BogusSetDispatchCounter $86
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $00
    BogusRelinkSlots
    BogusSetSlotMode $FF
    BogusSetUnlinkedFields $00, $00
ScriptD406:
    BogusSetDispatchCounter $F0
    BogusAdjustSlotBounds $00, $FF
    BogusRefreshSlotDrawPosition
    BogusBranchIfSlotB0AtMost ScriptD41D, $10
    BogusSetSlotValue $0100
ScriptD413:
    BogusDivideSlotValueByByte $02
    BogusBranchIfSlotValueAtLeast ScriptD413, $0002
    BogusJumpBank1 ScriptD406
ScriptD41D:
    BogusSetDispatchCounter $F0
    BogusReadSelectedSlot0520 $00
    BogusAddSlotValue $0004
    BogusClampSlotValueAtMost $00FF
    BogusWriteSelectedSlot0520 $00
    BogusStoreSlotValueArray $26
    BogusLoadSlotRecordAtPointer $53C0
.assert (* - BankStart) = $542E, error, "bank 1 script D3C9 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptD42E:
    BogusReadSlotValue $00 ; CONTROL_SWEEP_SCRIPT_D42E
SweepScriptD430:
    BogusStoreSlotValueArray $3D
SweepScriptD432:
    BogusCallNativeEncoded $B51B
SweepScriptD435:
    BogusSaveStateAndPlaceSlots $10
SweepScriptD437:
    BogusSetSlotValue $0000
SweepScriptD43A:
    BogusStoreSlotValueArray $25
SweepScriptD43C:
    BogusYieldAndSlotAction $01
.assert (* - BankStart) = $543E, error, "bank 1 sweep script $D42E end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD43E:
    SlotRuntimeRecord $C533, (ScriptD450 - BankStart), $00, $FE, $20, $61, $10 ; CONTROL_SLOT_RUNTIME_D43E
.assert (* - BankStart) = $5447, error, "bank 1 slot record D43E end"
; Possible contact for descriptor base $D43E; execution remains unverified.
ReviewedContactD447:
    SlotRuntimeRecord $C533, $547F, $00, $FF, $00, $00, $00 ; CONTROL_REVIEWED_CONTACT_D447
.assert (* - BankStart) = $5450, error, "bank 1 candidate contact d447 end"
ScriptD450:
    BogusSetDispatchCounter $86 ; CONTROL_BOGUS_D450
    BogusSetSlot05F0Pair $78, $78
    BogusSetDirectionalSlotFields40 $40, $E0
    BogusSetSlotC0 $04
    BogusSetSlot0640Pair $40, $00
    BogusSetSlot0670Pair $04, $00
    BogusInitializeSlotMotionFields
    BogusClearSlot0790Bits $01
.assert (* - BankStart) = $5463, error, "bank 1 script D450 end"
; The branch to $B98E is still a bank-relative alias to local script data.
ScriptD463:
    BogusBranchAndClearSlot0620Bit08 ScriptD47F ; CONTROL_BOGUS_D463
    BogusBranchIfAbsSlot0700Below ScriptB98E, $08
    BogusBranchIfSlotB0AtMost ScriptD463, $E4
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $5470, error, "bank 1 script D463 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD470:
    SlotRuntimeRecord $BE93, (ScriptD479 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_D470
.assert (* - BankStart) = $5479, error, "bank 1 slot record D470 end"
ScriptD479:
    BogusSetSlotC0 $00           ; CONTROL_BOGUS_D479
    BogusWait $01
    BogusYieldAndSlotAction $00
ScriptD47F:
    BogusSetDispatchCounter $87
    BogusLoadSlotRecord $09, $02
    BogusSetSlotFields80 $00, $E0
    BogusSetDirectionalSlotFields40 $C0, $FF
    BogusReadSlotValue $05
    BogusMaskSlotValue $0003
    BogusJumpViaSlotIndexedTable
; The preceding $0003 mask bounds this path to four table entries.
    BogusIndexedTargetBank1 ScriptD498
    BogusIndexedTargetBank1 ScriptD4A0
    BogusIndexedTargetBank1 ScriptD4A8
    BogusIndexedTargetBank1 ScriptD4B0
ScriptD498:
    BogusInitializeOtherSlotRelative $05, $FA, $FE, $00
    BogusJumpBank1 ScriptD4B8
ScriptD4A0:
    BogusInitializeOtherSlotRelative $05, $FA, $02, $00
    BogusJumpBank1 ScriptD4B8
ScriptD4A8:
    BogusInitializeOtherSlotRelative $05, $FE, $FE, $00
    BogusJumpBank1 ScriptD4B8
ScriptD4B0:
    BogusInitializeOtherSlotRelative $05, $FE, $02, $00
    BogusJumpBank1 ScriptD4B8
ScriptD4B8:
    BogusRestartVoice4 $2724
    BogusJumpBank1 ScriptD463
.assert (* - BankStart) = $54BE, error, "bank 1 script D479 end"
; Candidate descriptor $D4C1, command $D6C6, negative mode.
CompactContextD4BE:
    SlotCompactRecord $B6F8, $00 ; CONTROL_COMPACT_CONTEXT_D4BE
.assert (* - BankStart) = $54C1, error, "bank 1 compact candidate d4be end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD4C1:
    SlotRuntimeRecord $BFD3, $551B, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_D4C1
.assert (* - BankStart) = $54CA, error, "bank 1 slot record D4C1 end"
    .incbin "bank1_d4ca_d4cb.bin"
; Possible contact event after a later script clears the slot's flag.
ContextContactRecordD4CB:
    .byte $FF ; CONTROL_CONTEXT_CONTACT_D4CB
    .word ContextContactScriptD67C - BankStart
.assert (* - BankStart) = $54CE, error, "bank 1 context contact record D4CB end"
    .incbin "bank1_d4ce_d4d4.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD4D3:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D4D4
.assert (* - BankStart) = $54D5, error, "bank 1 candidate record field $D4D4 end"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script pointer is installed in mode $00.
ContextScriptPointerD4D3:
    .word $5970 ; CONTROL_CONTEXT_FIELDS_D4D5
.assert (* - BankStart) = $54D7, error, "bank 1 candidate record field $D4D5 end"
    .incbin "bank1_d4d7_d4dd.bin"
; Possible position-event record: both high sentinels skip their low bytes.
PositionSentinelD4DD:
    .byte $FF ; CONTROL_POSITION_SENTINEL_D4DD
    .incbin "bank1_d4de_d4df.bin"
PositionSentinelD4DF:
    .byte $FF ; CONTROL_POSITION_SENTINEL_D4DF
    .incbin "bank1_d4e0_d4e6.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD4E5:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D4E6
.assert (* - BankStart) = $54E7, error, "bank 1 candidate record field $D4E6 end"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script pointer is installed in mode $00.
ContextScriptPointerD4E5:
    .word (LongScriptD98E - BankStart) ; CONTROL_CONTEXT_FIELDS_D4E7
.assert (* - BankStart) = $54E9, error, "bank 1 candidate record field $D4E7 end"
    .incbin "bank1_d4e9_d4ee.bin"
; Candidate descriptor $D4C1, script $D928, mode $00.
ModeRecordD4EEFull:
    SlotRuntimeRecord $B701, $593D, $40, $01, $C4, $65, $21 ; CONTROL_MODE_RECORD_D4EE_FULL
.assert (* - BankStart) = $54F7, error, "bank 1 candidate mode record d4ee full end"
    .incbin "bank1_d4f7_d4f8.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD4F7:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D4F8
.assert (* - BankStart) = $54F9, error, "bank 1 candidate record field $D4F8 end"
    .incbin "bank1_d4f9_d4fa.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script high sentinel; any following bytes are consumed visual fields.
ContextRecordFieldsD4F7:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D4FA
.assert (* - BankStart) = $54FB, error, "bank 1 candidate record field $D4FA end"
    .incbin "bank1_d4fb_d500.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource pointer is consumed when its high byte is not $FF.
ContextResourceD500:
    .word $B6E1 ; CONTROL_CONTEXT_FIELDS_D500
.assert (* - BankStart) = $5502, error, "bank 1 candidate record field $D500 end"
    .incbin "bank1_d502_d503.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script high sentinel; any following bytes are consumed visual fields.
ContextRecordFieldsD500:
    .byte $FF, $00, $FF, $00, $00, $00 ; CONTROL_CONTEXT_FIELDS_D503
.assert (* - BankStart) = $5509, error, "bank 1 candidate record field $D503 end"
; Candidate descriptor $D4C1, command $D607, mode $00.
SlotFlowD509:
    SlotRuntimeRecord $B6E8, $577B, $23, $FE, $61, $61, $32 ; CONTROL_SLOT_FLOW_D509
.assert (* - BankStart) = $5512, error, "bank 1 slot record flow D509 end"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource pointer is consumed when its high byte is not $FF.
ContextResourceD512:
    .word $B6F1 ; CONTROL_CONTEXT_FIELDS_D512
.assert (* - BankStart) = $5514, error, "bank 1 candidate record field $D512 end"
    .incbin "bank1_d514_d515.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script high sentinel; any following bytes are consumed visual fields.
ContextRecordFieldsD512:
    .byte $FF, $40, $FF, $00, $00, $00 ; CONTROL_CONTEXT_FIELDS_D515
.assert (* - BankStart) = $551B, error, "bank 1 candidate record field $D515 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptD51B:
    BogusBranchIfMatchingSlotReady ContextScriptD51B, $01, $5D, $00 ; CONTROL_CONTEXT_D51B
    BogusSetSlotD0Bits $52
    BogusCreateLinkedSlot $28, $1C, $FE, $00
    BogusJumpBank1 (BankStart + $55F8)
.assert (* - BankStart) = $552B, error, "bank 1 contextual script D51B end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD52B:
    SlotRuntimeRecord $C587, $557C, $40, $FE, $45, $62, $31 ; CONTROL_SLOT_RUNTIME_D52B
.assert (* - BankStart) = $5534, error, "bank 1 slot record D52B end"
; Possible contact for descriptor base $D52B; execution remains unverified.
ReviewedContactD534:
    SlotRuntimeRecord $C5B1, $5609, $40, $FF, $00, $00, $00 ; CONTROL_REVIEWED_CONTACT_D534
.assert (* - BankStart) = $553D, error, "bank 1 candidate contact d534 end"
    .incbin "bank1_d53d_d53e.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD53D:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D53E
.assert (* - BankStart) = $553F, error, "bank 1 candidate record field $D53E end"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script pointer is installed in mode $00.
ContextScriptPointerD53D:
    .word $5970 ; CONTROL_CONTEXT_FIELDS_D53F
.assert (* - BankStart) = $5541, error, "bank 1 candidate record field $D53F end"
    .incbin "bank1_d541_d547.bin"
; Possible position-event record: both high sentinels skip their low bytes.
PositionSentinelD547:
    .byte $FF ; CONTROL_POSITION_SENTINEL_D547
    .incbin "bank1_d548_d549.bin"
PositionSentinelD549:
    .byte $FF ; CONTROL_POSITION_SENTINEL_D549
    .incbin "bank1_d54a_d550.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD54F:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D550
.assert (* - BankStart) = $5551, error, "bank 1 candidate record field $D550 end"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script pointer is installed in mode $00.
ContextScriptPointerD54F:
    .word (LongScriptD98E - BankStart) ; CONTROL_CONTEXT_FIELDS_D551
.assert (* - BankStart) = $5553, error, "bank 1 candidate record field $D551 end"
    .incbin "bank1_d553_d562.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD561:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D562
.assert (* - BankStart) = $5563, error, "bank 1 candidate record field $D562 end"
    .incbin "bank1_d563_d564.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script high sentinel; any following bytes are consumed visual fields.
ContextRecordFieldsD561:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D564
.assert (* - BankStart) = $5565, error, "bank 1 candidate record field $D564 end"
    .incbin "bank1_d565_d56a.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource pointer is consumed when its high byte is not $FF.
ContextResourceD56A:
    .word $C587 ; CONTROL_CONTEXT_FIELDS_D56A
.assert (* - BankStart) = $556C, error, "bank 1 candidate record field $D56A end"
    .incbin "bank1_d56c_d56d.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script high sentinel; any following bytes are consumed visual fields.
ContextRecordFieldsD56A:
    .byte $FF, $40, $FE, $45, $62, $31 ; CONTROL_CONTEXT_FIELDS_D56D
.assert (* - BankStart) = $5573, error, "bank 1 candidate record field $D56D end"
; Candidate descriptor $D52B, command $D607, mode $00.
SlotFlowD573:
    SlotRuntimeRecord $B927, $577B, $23, $FE, $45, $62, $31 ; CONTROL_SLOT_FLOW_D573
.assert (* - BankStart) = $557C, error, "bank 1 slot record flow D573 end"
    .incbin "bank1_d57c_d584.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD584:
    SlotRuntimeRecord $C5F5, (ScriptD5DE - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_D584
.assert (* - BankStart) = $558D, error, "bank 1 slot record D584 end"
; Zero-mode record observed in longer exploratory gameplay.
; Fields after a $FFFF resource pointer may be skipped by the loader.
LongRecordD58D:
    SlotRuntimeRecord $FFFF, (LongScriptD609 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_LONG_RECORD_D58D
LongRecordD596:
    SlotRuntimeRecord $FFFF, $5970, $40, $FF, $00, $00, $00
.assert (* - BankStart) = $559F, error, "bank 1 long-run records $D58D end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordD59F:
    SlotRuntimeRecord $FFFF, $FFFF, $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_D59F
.assert (* - BankStart) = $55A8, error, "bank 1 sweep record $D59F end"
; Zero-mode record observed in longer exploratory gameplay.
; Fields after a $FFFF resource pointer may be skipped by the loader.
LongRecordD5A8:
    SlotRuntimeRecord $FFFF, (LongScriptD98E - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_LONG_RECORD_D5A8
LongRecordD5B1:
    SlotRuntimeRecord $B94E, (LongScriptD92D - BankStart), $40, $FE, $25, $61, $11
.assert (* - BankStart) = $55BA, error, "bank 1 long-run records $D5A8 end"
    .incbin "bank1_d5ba_d5bb.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Resource high byte $FF skips visual fields and low pointer byte.
ContextResourceSentinelD5BA:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D5BB
.assert (* - BankStart) = $55BC, error, "bank 1 candidate record field $D5BB end"
    .incbin "bank1_d5bc_d5bd.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
; Script high sentinel; any following bytes are consumed visual fields.
ContextRecordFieldsD5BA:
    .byte $FF ; CONTROL_CONTEXT_FIELDS_D5BD
.assert (* - BankStart) = $55BE, error, "bank 1 candidate record field $D5BD end"
    .incbin "bank1_d5be_d5c3.bin"
; Zero-mode record observed in longer exploratory gameplay.
; Fields after a $FFFF resource pointer may be skipped by the loader.
LongRecordD5C3:
    SlotRuntimeRecord $C5F5, $FFFF, $40, $FF, $00, $00, $00 ; CONTROL_LONG_RECORD_D5C3
.assert (* - BankStart) = $55CC, error, "bank 1 long-run records $D5C3 end"
; Candidate descriptor $D584, command $D607, mode $00.
SlotFlowD5CC:
    SlotRuntimeRecord $B96E, $577B, $23, $FE, $35, $61, $11 ; CONTROL_SLOT_FLOW_D5CC
.assert (* - BankStart) = $55D5, error, "bank 1 slot record flow D5CC end"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordD5D5:
    SlotRuntimeRecord $B95E, $5835, $40, $00, $60, $08, $12 ; CONTROL_CONTEXT_FIELDS_D5D5
.assert (* - BankStart) = $55DE, error, "bank 1 candidate record field $D5D5 end"
ScriptD5DE:
    BogusSetSlotD0Bits $02 ; CONTROL_BOGUS_D5DE
    BogusReadSlotValue $02
    BogusBranchIfSlotValueNotEqual ScriptD5F1, $0002
    BogusSetSlotValue $1000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $08
    BogusJumpBank1 ScriptD5F8
ScriptD5F1:
    BogusSetSlotD0Bits $10
    BogusSetSlotD0Bits $40
    BogusJumpBank1 ScriptD5F8
ScriptD5F8:
    BogusSetDispatchCounter $05
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $08, $00
    BogusSetSlot05F0Pair $3C, $FF
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetSlotFields80 $01, $00
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $5609, error, "bank 1 script D5DE end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD609:
    BogusSetDispatchCounter $08 ; CONTROL_LONG_SCRIPT_D609
LongScriptD60B:
    BogusBranchIfSlot06D0Present (BankStart + $5729)
LongScriptD60E:
    BogusSubtractSlotPriorityFromField0520
LongScriptD60F:
    BogusLoadSlotValueArray $29
LongScriptD611:
    BogusSetSlotMode $00
LongScriptD613:
    BogusSetSlotMode $02
LongScriptD615:
    BogusReadSlotValue $24
LongScriptD617:
    BogusBranchIfSlotValueEqual SuccessorScriptAE7C, $07, $00
LongScriptD61C:
    BogusSetSlot07F0 $80
LongScriptD61E:
    BogusBranchIfSlot0520AtMost LongScriptD668, $00
.assert (* - BankStart) = $5622, error, "bank 1 long-run script $D609 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD622:
    BogusBranchIfSelectedFieldEqual ExtendedScriptD702, $10 ; CONTROL_EXTENDED_SCRIPT_D622
ExtendedScriptD626:
    BogusReadSlotValue $24
ExtendedScriptD628:
    BogusLookupSlotValue
.assert (* - BankStart) = $5629, error, "bank 1 extended script $D622 end"
; $95 compares the slot value with each case and branches to its target.
    BogusLookupCaseBank1 ExtendedScriptD637, $0000 ; CONTROL_EXTENDED_LOOKUP_D629
    BogusLookupCaseBank1 ExtendedScriptD645, $0006
    BogusLookupCaseBank1 LongScriptD668, $001D
    BogusLookupEnd
.assert (* - BankStart) = $5637, error, "bank 1 extended lookup $D629 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD637:
    BogusSetDispatchCounter $04 ; CONTROL_EXTENDED_SCRIPT_D637
ExtendedScriptD639:
    BogusSetLinkedSlotFieldsC0 $18, $FF
ExtendedScriptD63C:
    BogusAdvanceAndBranchState1B ExtendedScriptD645, $40
ExtendedScriptD640:
    BogusWait $01
ExtendedScriptD642:
    BogusJumpBank1 ExtendedScriptD65B
ExtendedScriptD645:
    BogusSetDispatchCounter $85
ExtendedScriptD647:
    BogusSetLinkedSlotFieldsC0 $60, $B8
ExtendedScriptD64A:
    BogusAdvanceAndBranchState1B ExtendedScriptD651, $80
ExtendedScriptD64E:
    BogusAddSlotFields00 $00, $E8
ExtendedScriptD651:
    BogusSetDispatchCounter $03
ExtendedScriptD653:
    BogusStartVoice4 $2724
ExtendedScriptD656:
    BogusWait $06
ExtendedScriptD658:
    BogusJumpBank1 ExtendedScriptD65B
ExtendedScriptD65B:
    BogusSetSlotD0Bits $20
ExtendedScriptD65D:
    BogusBranchIfSlot0520AtMost ExtendedScriptD663, $04
ExtendedScriptD661:
    BogusLoadRecordAndClearSavedState $48
ExtendedScriptD663:
    BogusSetSlotD0Bits $40
ExtendedScriptD665:
    BogusJumpBank1 ExtendedScriptD661
.assert (* - BankStart) = $5668, error, "bank 1 extended script $D637 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD668:
    BogusStartVoice4 $2724 ; CONTROL_LONG_SCRIPT_D668
LongScriptD66B:
    BogusSetSlotFields80 $D0, $88
LongScriptD66E:
    BogusSetSlotMode $FF
LongScriptD670:
    BogusSetSlot0360 $28
LongScriptD672:
    BogusBranchIfSlot0360AtMost LongScriptD67A, $01
LongScriptD676:
    BogusBranchIfSlotB0AtMost LongScriptD672, $E6
LongScriptD67A:
    BogusYieldAndSlotAction $01
.assert (* - BankStart) = $567C, error, "bank 1 long-run script $D668 end"
; Possible contact script for descriptor $D4C1 after a later flag clear.
; Its slot association and execution have not been observed.
ContextContactScriptD67C:
    BogusBranchIfSlot0760Equal ContextContactScriptD698, $28 ; CONTROL_CONTEXT_CONTACT_SCRIPT_D67C
    BogusClearSlot0790Bits $01
    BogusSetSlot0670Pair $01, $00
    BogusSetSlotFields80 $01, $FF
    BogusLoadSlotRecord $3F, $02
    BogusWait $14
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $568F, error, "bank 1 context contact script D67C end"
; Candidate direct target at $D6A2. Its inherited mode is unknown; these
; fields cover the possible mode classes. The tenth fetched byte is the
; following script's opcode, not part of this nine-byte record.
ContextDirectRecordD68F:
    SlotRuntimeRecord $BE09, $FFFF, $00, $FF, $00, $00, $00 ; CONTROL_CONTEXT_DIRECT_RECORD_D68F
.assert (* - BankStart) = $5698, error, "bank 1 context direct record D68F end"
ContextContactScriptD698:
    BogusLoadSlotRecord $51, $02 ; CONTROL_CONTEXT_CONTACT_SCRIPT_D698
    BogusSetLinkedSlotFieldsC0 $40, $C0
    BogusWait $14
    BogusSetDispatchCounter $05
    BogusLoadSlotRecordAtPointer $568F
    BogusSetSlotFields80 $00, $A0
ContextContactScriptD6A8:
    BogusBranchIfSlot0620Bit10Clear ContextContactScriptD6A8
    BogusSetState03BC $01
    BogusWait $01
    BogusSetState03BC $05
    BogusWait $01
    BogusSetState03BC $01
    BogusWait $01
    BogusSetState03BC $05
    BogusWait $01
    BogusSetState03BC $03
    BogusSetVoicePointers $2C58, $2C70, $0000, $0000
    BogusLoadSlotRecord $03, $FF
    BogusWait $5A
    BogusSetSlotValue $0029
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $FFFF
    BogusStoreSlotValueArray $23
    BogusSetMainState $10
.assert (* - BankStart) = $56D7, error, "bank 1 context contact script D698 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeD6D7:
    SlotRuntimeRecord $BC79, (ScriptD6E0 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_D6D7
.assert (* - BankStart) = $56E0, error, "bank 1 slot record D6D7 end"
; A slot-field comparison gates three matching-slot updates and waits.
ScriptD6E0:
    BogusSetSlot0640Pair $04, $00
    BogusBranchIfSlot0760Equal ScriptD6EA, $66
    BogusJumpBank1 ScriptD6E0
ScriptD6EA:
    BogusMarkMatchingSlots $00, $01, $20, $00
    BogusWait $04                ; CONTROL_BOGUS_D6E0
    BogusMarkMatchingSlots $00, $01, $20, $00
    BogusWait $04
    BogusMarkMatchingSlots $00, $01, $20, $00
    BogusRestartVoice4 $289B
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $5702, error, "bank 1 script D6E0 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD702:
    BogusBranchIfSlotD0Bits ExtendedScriptD661, $40 ; CONTROL_EXTENDED_SCRIPT_D702
ExtendedScriptD706:
    BogusSetSlot0790Bits $FF
ExtendedScriptD708:
    BogusLoadRecordAndClearSavedState $1B
.assert (* - BankStart) = $570A, error, "bank 1 extended script $D702 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptD70A:
    BogusFollowLinkedSlotsAndYield $FF, $FF, $01, $01, $00 ; CONTROL_SWEEP_SCRIPT_D70A
SweepScriptD710:
    BogusSetLinkedFieldsAndYield $FF, $FC
SweepScriptD713:
    BogusSetLinkedFieldsAndYield $FF, $F8
SweepScriptD716:
    BogusSetLinkedFieldsAndYield $FF, $F0
SweepScriptD719:
    BogusSetLinkedFieldsAndYield $FF, $E8
SweepScriptD71C:
    BogusSetLinkedFieldsAndYield $80, $E2
SweepScriptD71F:
    BogusSetSlot07F0 $14
SweepScriptD721:
    BogusSetSlot0630Bit04UnlessFF $01
SweepScriptD723:
    BogusCopyLinkedMotionFields
SweepScriptD724:
    BogusClearSlot0790Bits $01
SweepScriptD726:
    BogusJumpBank1 SweepScriptD723
.assert (* - BankStart) = $5729, error, "bank 1 sweep script $D70A end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD729:
    BogusBranchIfSelectedFieldEqual ExtendedScriptD73C, $11 ; CONTROL_EXTENDED_SCRIPT_D729
ExtendedScriptD72D:
    BogusBranchIfSelectedFieldEqual ExtendedScriptD738, $1E
ExtendedScriptD731:
    BogusWait $0A
ExtendedScriptD733:
    BogusLoadRecordAndClearSavedState $1B
.assert (* - BankStart) = $5735, error, "bank 1 extended script $D729 end"
; Possible continuation when a position-event record preserves the pointer.
ContextPositionScriptD735:
    BogusJumpBank1 SweepScriptD71F ; CONTROL_CONTEXT_POSITION_SCRIPT_D735
.assert (* - BankStart) = $5738, error, "bank 1 context position script D735 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD738:
    BogusRelinkToLastRelatedSlot ; CONTROL_EXTENDED_SCRIPT_D738
.assert (* - BankStart) = $5739, error, "bank 1 extended script $D738 end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptD739:
    BogusJumpBank1 ExtendedScriptE7B2 ; CONTROL_EXPANDED_SCRIPT_D739
.assert (* - BankStart) = $573C, error, "bank 1 candidate successor $D739 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD73C:
    BogusSetDispatchCounter $87 ; CONTROL_EXTENDED_SCRIPT_D73C
ExtendedScriptD73E:
    BogusSetSlot05F0Pair $7F, $7F
ExtendedScriptD741:
    BogusCopyLinkedMotionFields
.assert (* - BankStart) = $5742, error, "bank 1 extended script $D73C end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptD742:
    BogusSetDirectionalSlotFields40 $28, $00 ; CONTROL_SWEEP_SCRIPT_D742
SweepScriptD745:
    BogusAddSlotFields00 $00, $A0
SweepScriptD748:
    BogusLoadSlotValueArray $3C
SweepScriptD74A:
    BogusSetSlotMode $00
SweepScriptD74C:
    BogusRelinkSlots
SweepScriptD74D:
    BogusSetDispatchCounter $03
SweepScriptD74F:
    BogusAddSlotFields00 $00, $F8
SweepScriptD752:
    BogusBranchIfSlotFieldsWithin SweepScriptD75E, $FF, $08
SweepScriptD757:
    BogusBranchIfSlotB0AtMost SweepScriptD74D, $E6
.assert (* - BankStart) = $575B, error, "bank 1 sweep script $D742 end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptD75B:
    BogusLoadRecordAndClearSavedState $1E ; CONTROL_PATH_SCRIPT_D75B
.assert (* - BankStart) = $575D, error, "bank 1 candidate successor $D75B end"
    .incbin "bank1_d75d_d75e.bin"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptD75E:
    BogusLoadSlotValueArray $29 ; CONTROL_SWEEP_SCRIPT_D75E
SweepScriptD760:
    BogusSetSlotMode $00
SweepScriptD762:
    BogusSetSlotMode $02
SweepScriptD764:
    BogusSetSlot07F0 $44
SweepScriptD766:
    BogusBranchIfSlot0620Bit10 SweepScriptD76F
SweepScriptD769:
    BogusBranchIfSlotB0AtMost SweepScriptD766, $E6
.assert (* - BankStart) = $576D, error, "bank 1 sweep script $D75E end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptD76D:
    BogusYieldAndSlotAction $01 ; CONTROL_PATH_SCRIPT_D76D
.assert (* - BankStart) = $576F, error, "bank 1 candidate successor $D76D end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptD76F:
    BogusStartVoice4 $2724 ; CONTROL_SWEEP_SCRIPT_D76F
SweepScriptD772:
    BogusSubtractSlotPriorityFromField0520
SweepScriptD773:
    BogusBranchIfSlot0520AtMost LongScriptD668, $00
SweepScriptD777:
    BogusWait $0A
SweepScriptD779:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $577B, error, "bank 1 sweep script $D76F end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptD77B:
    BogusSetDispatchCounter $06 ; CONTROL_CONTEXT_D77B
    BogusSetSlot07F0 $44
    BogusClearSlot0790Bits $FF
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusBranchIfSlot0620Bit10 (BankStart + $5794)
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $578B, error, "bank 1 contextual script D77B end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD78B:
    BogusSetSlotFields80 $01, $FF ; CONTROL_LONG_SCRIPT_D78B
LongScriptD78E:
    BogusLoadRecordAndClearSavedState $3F
LongScriptD790:
    BogusWait $14
LongScriptD792:
    BogusLoadRecordAndClearSavedState $48
LongScriptD794:
    BogusSetDispatchCounter $84
LongScriptD796:
    BogusConfigureSlot0750 $01, $00
LongScriptD799:
    BogusBranchIfSlotCoordinates01 LongScriptD7D6, $FF, $07
LongScriptD79E:
    BogusReadSlotValue $08
LongScriptD7A0:
    BogusBranchIfSlotValueEqual LongScriptD7AD, $00, $00
LongScriptD7A5:
    BogusConfigureSlot0750 $01, $00
LongScriptD7A8:
    BogusBranchIfSlot0620Bit10 LongScriptD8C3
.assert (* - BankStart) = $57AB, error, "bank 1 long-run script $D78B end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD7AB:
    BogusLoadRecordAndClearSavedState $12 ; CONTROL_EXTENDED_SCRIPT_D7AB
.assert (* - BankStart) = $57AD, error, "bank 1 extended script $D7AB end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD7AD:
    BogusBranchIfSlotD0Bits LongScriptD7D6, $10 ; CONTROL_LONG_SCRIPT_D7AD
LongScriptD7B1:
    BogusWait $14
LongScriptD7B3:
    BogusBranchIfSlotCoordinates01 LongScriptD7D6, $FF, $07
LongScriptD7B8:
    BogusReadSlotValue $08
LongScriptD7BA:
    BogusBranchIfSlotValueEqual LongScriptD7D6, $01, $00
LongScriptD7BF:
    BogusBranchIfSlotD0BitsClear LongScriptD7D1, $01
.assert (* - BankStart) = $57C3, error, "bank 1 long-run script $D7AD end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD7C3:
    BogusBranchIfSlotCoordinates01 LongScriptD7D1, $40, $FF ; CONTROL_EXTENDED_SCRIPT_D7C3
ExtendedScriptD7C8:
    BogusAdvanceAndBranchState1B LongScriptD7D1, $80
ExtendedScriptD7CC:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD867, $FF, $30
.assert (* - BankStart) = $57D1, error, "bank 1 extended script $D7C3 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD7D1:
    BogusSetSlotValue $0001 ; CONTROL_LONG_SCRIPT_D7D1
LongScriptD7D4:
    BogusLoadRecordAndClearSavedState $24
LongScriptD7D6:
    BogusConfigureSlot0750 $01, $00
LongScriptD7D9:
    BogusBranchIfDirectionalOffsetClear LongScriptD883, $00
LongScriptD7DD:
    BogusConfigureSlot0750 $01, $00
LongScriptD7E0:
    BogusBranchIfDirectionalOffsetClear (BankStart + $587D), $08
LongScriptD7E4:
    BogusConfigureSlot0750 $01, $00
LongScriptD7E7:
    BogusBranchIfDirectionalOffsetClear (BankStart + $587D), $10
LongScriptD7EB:
    BogusConfigureSlot0750 $01, $00
LongScriptD7EE:
    BogusBranchIfSlotCoordinates01 (BankStart + $582A), $28, $FF
LongScriptD7F3:
    BogusBranchIfSlotD0BitsClear (BankStart + $5856), $08
LongScriptD7F7:
    BogusConfigureSlot0750 $01, $00
LongScriptD7FA:
    BogusLoadSlotValueArray $FF
LongScriptD7FC:
    BogusSetSlot0670Pair $00, $00
LongScriptD7FF:
    BogusBranchIfSlotCoordinatesA3 (BankStart + $580D), $40, $10
LongScriptD804:
    BogusConfigureSlot0750 $01, $00
LongScriptD807:
    BogusSetSlot0670Pair $01, $00
LongScriptD80A:
    BogusJumpBank1 (BankStart + $5856)
.assert (* - BankStart) = $580D, error, "bank 1 long-run script $D7D1 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD80D:
    BogusSetDispatchCounter $85 ; CONTROL_EXTENDED_SCRIPT_D80D
ExtendedScriptD80F:
    BogusSetSlotFields80 $01, $00
ExtendedScriptD812:
    BogusBranchIfDirectionalOffsetClear LongScriptD804, $20
ExtendedScriptD816:
    BogusSetSlotFields80 $20, $00
ExtendedScriptD819:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD828, $10, $08
ExtendedScriptD81E:
    BogusBranchIfSlot0620Bit10Clear (BankStart + $5970)
ExtendedScriptD821:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD816, $40, $10
ExtendedScriptD826:
    BogusLoadRecordAndClearSavedState $48
ExtendedScriptD828:
    BogusLoadRecordAndClearSavedState $51
ExtendedScriptD82A:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD832, $FF, $10
ExtendedScriptD82F:
    BogusJumpBank1 LongScriptD78B
ExtendedScriptD832:
    BogusJumpBank1 LongScriptD90E
.assert (* - BankStart) = $5835, error, "bank 1 extended script $D80D end"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptD835:
    BogusWait $07 ; CONTROL_RETAINED_SCRIPT_D835
RetainedScriptD837:
    BogusMarkRelatedSlotAtDepth $38, $02
RetainedScriptD83A:
    BogusFindLinkedSlot
RetainedScriptD83B:
    BogusBranchIfSlotValueEqual RetainedScriptD854, $FF, $FF
RetainedScriptD840:
    BogusLoadSlotRecord $03, $FF
RetainedScriptD843:
    BogusSetDirectionalSlotFields40 $10, $D8
RetainedScriptD846:
    BogusMarkRelatedSlotAtDepth $1A, $01
RetainedScriptD849:
    BogusRestartVoice4 $277A
RetainedScriptD84C:
    BogusSetSlotFields80 $00, $00
RetainedScriptD84F:
    BogusWait $05
RetainedScriptD851:
    BogusMarkRelatedSlotAtDepth $1A, $01
RetainedScriptD854:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $5856, error, "bank 1 candidate successor $D835 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD856:
    BogusBranchIfSlotD0BitsClear LongScriptD86D, $01 ; CONTROL_EXTENDED_SCRIPT_D856
ExtendedScriptD85A:
    BogusBranchIfSlotCoordinates01 LongScriptD86D, $40, $FF
ExtendedScriptD85F:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD867, $FF, $30
ExtendedScriptD864:
    BogusJumpBank1 LongScriptD86D
ExtendedScriptD867:
    BogusAdvanceAndBranchState1B LongScriptD86D, $40
ExtendedScriptD86B:
    BogusLoadRecordAndClearSavedState $36
.assert (* - BankStart) = $586D, error, "bank 1 extended script $D856 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD86D:
    BogusBranchIfSlotD0Bits (BankStart + $5877), $60 ; CONTROL_LONG_SCRIPT_D86D
LongScriptD871:
    BogusSetSlotFields80 $18, $00
LongScriptD874:
    BogusJumpBank1 LongScriptD794
.assert (* - BankStart) = $5877, error, "bank 1 long-run script $D86D end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD877:
    BogusSetSlotFields80 $20, $00 ; CONTROL_EXTENDED_SCRIPT_D877
ExtendedScriptD87A:
    BogusJumpBank1 LongScriptD794
ExtendedScriptD87D:
    BogusSetSlotFields80 $08, $00
ExtendedScriptD880:
    BogusJumpBank1 LongScriptD794
.assert (* - BankStart) = $5883, error, "bank 1 extended script $D877 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD883:
    BogusSetDispatchCounter $82 ; CONTROL_LONG_SCRIPT_D883
LongScriptD885:
    BogusSetSlotFields80 $00, $00
LongScriptD888:
    BogusSetDirectionalSlotFields40 $01, $FF
LongScriptD88B:
    BogusLoadRecordAndClearSavedState $3F
LongScriptD88D:
    BogusWait $14
LongScriptD88F:
    BogusBranchIfSlotD0Bits (BankStart + $58AE), $10
LongScriptD893:
    BogusBranchIfDirectionalOffsetClear LongScriptD89E, $08
.assert (* - BankStart) = $5897, error, "bank 1 long-run script $D883 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD897:
    BogusBranchIfDirectionalOffsetClear LongScriptD89E, $00 ; CONTROL_EXTENDED_SCRIPT_D897
ExtendedScriptD89B:
    BogusJumpBank1 ExtendedScriptD8A8
.assert (* - BankStart) = $589E, error, "bank 1 extended script $D897 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD89E:
    BogusSetSlotValue $0002 ; CONTROL_LONG_SCRIPT_D89E
LongScriptD8A1:
    BogusSetDispatchCounter $82
LongScriptD8A3:
    BogusSetSlotFields80 $20, $00
LongScriptD8A6:
    BogusLoadRecordAndClearSavedState $24
.assert (* - BankStart) = $58A8, error, "bank 1 long-run script $D89E end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD8A8:
    BogusLoadSlotRecord $48, $02 ; CONTROL_EXTENDED_SCRIPT_D8A8
ExtendedScriptD8AB:
    BogusJumpBank1 LongScriptD794
ExtendedScriptD8AE:
    BogusLoadSlotRecord $48, $02
ExtendedScriptD8B1:
    BogusSetDirectionalSlotFields40 $F0, $FF
ExtendedScriptD8B4:
    BogusWait $02
ExtendedScriptD8B6:
    BogusSetDirectionalSlotFields40 $F0, $FF
ExtendedScriptD8B9:
    BogusWait $02
ExtendedScriptD8BB:
    BogusSetDirectionalSlotFields40 $F0, $FF
ExtendedScriptD8BE:
    BogusWait $02
ExtendedScriptD8C0:
    BogusJumpBank1 LongScriptD78B
.assert (* - BankStart) = $58C3, error, "bank 1 extended script $D8A8 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD8C3:
    BogusSetDispatchCounter $04 ; CONTROL_LONG_SCRIPT_D8C3
LongScriptD8C5:
    BogusBranchIfSlotD0BitsClear LongScriptD8D7, $01
.assert (* - BankStart) = $58C9, error, "bank 1 long-run script $D8C3 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD8C9:
    BogusBranchIfSlotCoordinates01 LongScriptD8D7, $40, $FF ; CONTROL_EXTENDED_SCRIPT_D8C9
ExtendedScriptD8CE:
    BogusAdvanceAndBranchState1B LongScriptD8D7, $80
ExtendedScriptD8D2:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD867, $FF, $30
.assert (* - BankStart) = $58D7, error, "bank 1 extended script $D8C9 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD8D7:
    BogusBranchIfOffsetProbe LongScriptD8FE, $04 ; CONTROL_LONG_SCRIPT_D8D7
LongScriptD8DB:
    BogusBranchOnDirectionalOffset LongScriptD906, $04
LongScriptD8DF:
    BogusConfigureSlot0750 $01, $00
LongScriptD8E2:
    BogusBranchIfDirectionalOffsetClear LongScriptD883, $08
LongScriptD8E6:
    BogusSetSlotFields80 $18, $FF
LongScriptD8E9:
    BogusConfigureSlot0750 $01, $00
LongScriptD8EC:
    BogusConfigureSlot0750 $01, $00
LongScriptD8EF:
    BogusBranchIfDirectionalOffsetClear LongScriptD883, $08
LongScriptD8F3:
    BogusBranchIfSlotCoordinates01 LongScriptD78B, $10, $FF
LongScriptD8F8:
    BogusConfigureSlot0750 $01, $00
LongScriptD8FB:
    BogusJumpBank1 LongScriptD794
LongScriptD8FE:
    BogusSetSlotFields80 $01, $00
LongScriptD901:
    BogusSetSlotValue $0000
LongScriptD904:
    BogusLoadRecordAndClearSavedState $24
LongScriptD906:
    BogusSetSlotValue $0003
LongScriptD909:
    BogusSetSlotFields80 $01, $00
LongScriptD90C:
    BogusLoadRecordAndClearSavedState $24
LongScriptD90E:
    BogusSetDispatchCounter $86
LongScriptD910:
    BogusLoadRecordAndClearSavedState $3F
LongScriptD912:
    BogusSetSlotFields80 $01, $00
LongScriptD915:
    BogusSetSlot0370 $01
LongScriptD917:
    BogusBranchIfSlotD0BitsClear (BankStart + $591D), $60
.assert (* - BankStart) = $591B, error, "bank 1 long-run script $D8D7 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD91B:
    BogusSetSlot0370 $01 ; CONTROL_EXTENDED_SCRIPT_D91B
ExtendedScriptD91D:
    BogusBranchIfSlot0370AtMost ExtendedScriptD928, $01
ExtendedScriptD921:
    BogusBranchIfSlotCoordinates01 ExtendedScriptD91D, $28, $0F
ExtendedScriptD926:
    BogusLoadRecordAndClearSavedState $48
ExtendedScriptD928:
    BogusLoadRecordAndClearSavedState $2D
.assert (* - BankStart) = $592A, error, "bank 1 extended script $D91B end"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptD92A:
    BogusSetSlotFields80 $3C, $D8 ; CONTROL_RETAINED_SCRIPT_D92A
.assert (* - BankStart) = $592D, error, "bank 1 candidate successor $D92A end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD92D:
    BogusSetSlotFields80 $20, $00 ; CONTROL_LONG_SCRIPT_D92D
LongScriptD930:
    BogusSetSlotFields80 $08, $00
LongScriptD933:
    BogusCheckSlotFlagsAndRestorePointer
LongScriptD934:
    BogusBranchAndClearSlot0620Bit08 (BankStart + $5939)
LongScriptD937:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $5939, error, "bank 1 long-run script $D92D end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD939:
    BogusClearSlotD0Bits $20 ; CONTROL_EXTENDED_SCRIPT_D939
ExtendedScriptD93B:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $593D, error, "bank 1 extended script $D939 end"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptD93D:
    BogusSetSlotFields80 $20, $00 ; CONTROL_RETAINED_SCRIPT_D93D
RetainedScriptD940:
    BogusSetSlotFields80 $20, $00
RetainedScriptD943:
    BogusSetSlotFields80 $08, $00
RetainedScriptD946:
    BogusCheckSlotFlagsAndRestorePointer
RetainedScriptD947:
    BogusRestartVoice4 $2724
RetainedScriptD94A:
    BogusSetState03BC $01
RetainedScriptD94C:
    BogusWait $01
RetainedScriptD94E:
    BogusSetState03BC $05
RetainedScriptD950:
    BogusWait $01
RetainedScriptD952:
    BogusSetState03BC $01
RetainedScriptD954:
    BogusWait $01
RetainedScriptD956:
    BogusSetState03BC $05
RetainedScriptD958:
    BogusWait $01
RetainedScriptD95A:
    BogusSetState03BC $03
RetainedScriptD95C:
    BogusBranchAndClearSlot0620Bit08 RetainedScriptD961
RetainedScriptD95F:
    BogusLoadRecordAndClearSavedState $48
RetainedScriptD961:
    BogusSetDispatchCounter $82
RetainedScriptD963:
    BogusSetSlotFields80 $00, $FF
RetainedScriptD966:
    BogusSetDirectionalSlotFields40 $01, $FF
RetainedScriptD969:
    BogusLoadSlotRecord $3F, $02
RetainedScriptD96C:
    BogusWait $14
RetainedScriptD96E:
    BogusLoadRecordAndClearSavedState $48
.assert (* - BankStart) = $5970, error, "bank 1 candidate successor $D93D end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptD970:
    BogusSetDispatchCounter $03 ; CONTROL_CONTEXT_D970
    BogusLoadSlotValueArray $29
    BogusSetSlotMode $00
    BogusSetSlotMode $02
ContextScriptD978:
    BogusBranchIfSlot0620Bit10 ContextScriptD981
    BogusBranchIfSlotB0AtMost ContextScriptD978, $E1
    BogusYieldAndSlotAction $01
ContextScriptD981:
    BogusSetSlot05F0Pair $3C, $60
    BogusBranchIfSlotCoordinates01 ContextScriptD98B, $28, $10
    BogusLoadRecordAndClearSavedState $48
ContextScriptD98B:
    BogusJumpBank1 (BankStart + $590E)
.assert (* - BankStart) = $598E, error, "bank 1 contextual script D970 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD98E:
    BogusSetDispatchCounter $04 ; CONTROL_LONG_SCRIPT_D98E
LongScriptD990:
    BogusBranchIfSlotValueEqual LongScriptD9DD, $01, $00
LongScriptD995:
    BogusBranchIfSlotValueEqual LongScriptD9D0, $02, $00
LongScriptD99A:
    BogusSetDispatchCounter $82
LongScriptD99C:
    BogusSetSlotFields80 $FF, $A0
LongScriptD99F:
    BogusSetSlotMode $03
LongScriptD9A1:
    BogusSetSlotFields80 $FF, $A0
LongScriptD9A4:
    BogusSetSlotFields80 $FF, $A0
LongScriptD9A7:
    BogusBranchIfSlotD0BitsClear LongScriptD9B4, $04
.assert (* - BankStart) = $59AB, error, "bank 1 long-run script $D98E end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD9AB:
    BogusSetSlotFields80 $FF, $A0 ; CONTROL_EXTENDED_SCRIPT_D9AB
ExtendedScriptD9AE:
    BogusSetSlotFields80 $FF, $A0
ExtendedScriptD9B1:
    BogusSetSlotFields80 $FF, $A0
.assert (* - BankStart) = $59B4, error, "bank 1 extended script $D9AB end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD9B4:
    BogusSetSlotFields80 $FF, $B0 ; CONTROL_LONG_SCRIPT_D9B4
LongScriptD9B7:
    BogusSetSlotFields80 $FF, $C8
LongScriptD9BA:
    BogusBranchIfSlotValueEqual LongScriptD9C1, $03, $00
LongScriptD9BF:
    BogusLoadRecordAndClearSavedState $12
LongScriptD9C1:
    BogusAddSlotFields00 $08, $00
LongScriptD9C4:
    BogusWait $02
LongScriptD9C6:
    BogusAddSlotFields00 $10, $00
LongScriptD9C9:
    BogusWait $02
LongScriptD9CB:
    BogusAddSlotFields00 $10, $00
LongScriptD9CE:
    BogusLoadRecordAndClearSavedState $12
LongScriptD9D0:
    BogusSetDispatchCounter $82
LongScriptD9D2:
    BogusSetSlotFields80 $FF, $A0
LongScriptD9D5:
    BogusSetSlotMode $03
LongScriptD9D7:
    BogusSetSlotFields80 $FF, $A0
LongScriptD9DA:
    BogusJumpBank1 LongScriptD9B4
LongScriptD9DD:
    BogusLoadSlotValueArray $3C
LongScriptD9DF:
    BogusSetSlotMode $00
LongScriptD9E1:
    BogusBranchIfSlot0620Bit10 LongScriptD9EB
.assert (* - BankStart) = $59E4, error, "bank 1 long-run script $D9B4 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptD9E4:
    BogusSetSlotFields80 $FF, $E0 ; CONTROL_EXTENDED_SCRIPT_D9E4
ExtendedScriptD9E7:
    BogusWait $04
ExtendedScriptD9E9:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $59EB, error, "bank 1 extended script $D9E4 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptD9EB:
    BogusLoadSlotRecord $48, $01 ; CONTROL_LONG_SCRIPT_D9EB
LongScriptD9EE:
    BogusSetSlotFields80 $18, $FF
LongScriptD9F1:
    BogusConfigureSlot0750 $01, $00
LongScriptD9F4:
    BogusSetDispatchCounter $04
LongScriptD9F6:
    BogusReadSlotValue $08
LongScriptD9F8:
    BogusBranchIfSlotValueEqual (BankStart + $5A14), $01, $00
LongScriptD9FD:
    BogusBranchIfSlotCoordinates01 (BankStart + $5A14), $FF, $07
LongScriptDA02:
    BogusBranchIfSlotCoordinates01 LongScriptD78B, $02, $FF
LongScriptDA07:
    BogusBranchIfSlotFieldsWithin (BankStart + $5A14), $07, $FF
LongScriptDA0C:
    BogusConfigureSlot0750 $01, $00
LongScriptDA0F:
    BogusBranchIfSlot0620Bit10 LongScriptD9F1
LongScriptDA12:
    BogusLoadRecordAndClearSavedState $12
.assert (* - BankStart) = $5A14, error, "bank 1 long-run script $D9EB end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptDA14:
    BogusLoadRecordAndClearSavedState $48 ; CONTROL_EXTENDED_SCRIPT_DA14
.assert (* - BankStart) = $5A16, error, "bank 1 extended script $DA14 end"
; Candidate descriptor $DA1C, command $E89D, negative mode.
CompactContextDA16:
    SlotCompactRecord $B65B, $22 ; CONTROL_COMPACT_CONTEXT_DA16
.assert (* - BankStart) = $5A19, error, "bank 1 compact candidate da16 end"
; Candidate descriptor $DA1C, command $E784, negative mode.
CompactContextDA19:
    SlotCompactRecord $B654, $00 ; CONTROL_COMPACT_CONTEXT_DA19
.assert (* - BankStart) = $5A1C, error, "bank 1 compact candidate da19 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDA1C:
    SlotRuntimeRecord $B65B, (ScriptE9BC - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DA1C
.assert (* - BankStart) = $5A25, error, "bank 1 slot record DA1C end"
    .incbin "bank1_da25_da26.bin"
; Possible contact for descriptor base $DA1C; execution remains unverified.
ReviewedContactDA25:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DA25
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5A29, error, "bank 1 candidate contact da25 end"
    .incbin "bank1_da29_da37.bin"
; Candidate descriptor $DA1C, command $EA26, mode $00.
SlotFlowDA37:
    SlotRuntimeRecord $B654, $6AA2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_DA37
.assert (* - BankStart) = $5A40, error, "bank 1 slot record flow DA37 end"
    .incbin "bank1_da40_da46.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDA46:
    SlotRuntimeRecord $B644, (ScriptE9BA - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DA46
.assert (* - BankStart) = $5A4F, error, "bank 1 slot record DA46 end"
    .incbin "bank1_da4f_da61.bin"
; Candidate descriptor $DA46, command $EA26, mode $00.
SlotFlowDA61:
    SlotRuntimeRecord $B63D, $6AA2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_DA61
; Candidate descriptor $DA46, command $EA3E, mode $00.
SlotFlowDA6A:
    SlotRuntimeRecord $B644, $6ADA, $22, $FE, $27, $62, $21
.assert (* - BankStart) = $5A73, error, "bank 1 slot record flow DA61 end"
; Candidate descriptor $DA79, command $E89D, negative mode.
CompactContextDA73:
    SlotCompactRecord $B83F, $22 ; CONTROL_COMPACT_CONTEXT_DA73
.assert (* - BankStart) = $5A76, error, "bank 1 compact candidate da73 end"
; Candidate descriptor $DA79, command $E784, negative mode.
CompactContextDA76:
    SlotCompactRecord $C313, $00 ; CONTROL_COMPACT_CONTEXT_DA76
.assert (* - BankStart) = $5A79, error, "bank 1 compact candidate da76 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDA79:
    SlotRuntimeRecord $B83F, (ScriptE9BA - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DA79
.assert (* - BankStart) = $5A82, error, "bank 1 slot record DA79 end"
    .incbin "bank1_da82_da83.bin"
; Possible contact for descriptor base $DA79; execution remains unverified.
ReviewedContactDA82:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DA82
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5A86, error, "bank 1 candidate contact da82 end"
    .incbin "bank1_da86_da94.bin"
; Candidate descriptor $DA79, command $EA26, mode $00.
SlotFlowDA94:
    SlotRuntimeRecord $B838, $6AA2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_DA94
; Candidate descriptor $DA79, command $EA3E, mode $00.
SlotFlowDA9D:
    SlotRuntimeRecord $B83F, $6ADA, $22, $FE, $27, $62, $21
.assert (* - BankStart) = $5AA6, error, "bank 1 slot record flow DA94 end"
; Candidate descriptor $DAAC, command $E89D, negative mode.
CompactContextDAA6:
    SlotCompactRecord $B67A, $22 ; CONTROL_COMPACT_CONTEXT_DAA6
.assert (* - BankStart) = $5AA9, error, "bank 1 compact candidate daa6 end"
; Candidate descriptor $DAAC, command $E784, negative mode.
CompactContextDAA9:
    SlotCompactRecord $BBCF, $00 ; CONTROL_COMPACT_CONTEXT_DAA9
.assert (* - BankStart) = $5AAC, error, "bank 1 compact candidate daa9 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDAAC:
    SlotRuntimeRecord $B67A, $6D11, $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DAAC
.assert (* - BankStart) = $5AB5, error, "bank 1 slot record DAAC end"
    .incbin "bank1_dab5_dab6.bin"
; Possible contact for descriptor base $DAAC; execution remains unverified.
ReviewedContactDAB5:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DAB5
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5AB9, error, "bank 1 candidate contact dab5 end"
    .incbin "bank1_dab9_dabe.bin"
; Candidate descriptor $DAAC, script $EE2A, mode $01.
ModeRecordDABEResource:
    .word $B664 ; CONTROL_MODE_RECORD_DABE_RESOURCE
.assert (* - BankStart) = $5AC0, error, "bank 1 candidate mode record dabe resource end"
    .incbin "bank1_dac0_dac2.bin"
; Candidate descriptor $DAAC, script $EE2A, mode $01.
ModeRecordDABEFields:
    .byte $00 ; CONTROL_MODE_RECORD_DABE_FIELDS
.assert (* - BankStart) = $5AC3, error, "bank 1 candidate mode record dabe fields end"
    .incbin "bank1_dac3_dac7.bin"
; Candidate descriptor $DAAC, command $EDFC, mode $00.
SlotFlowDAC7:
    SlotRuntimeRecord $B66B, $6DFE, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_DAC7
.assert (* - BankStart) = $5AD0, error, "bank 1 slot record flow DAC7 end"
; Candidate descriptor $DAD6, command $E6A1, mode $FF.
SlotFlowDAD0:
    SlotCompactRecord $B8A6, $23 ; CONTROL_SLOT_FLOW_DAD0
.assert (* - BankStart) = $5AD3, error, "bank 1 slot record flow DAD0 end"
; Compact record observed in negative loader mode.
DirectedRecordDAD3:
    SlotCompactRecord $C42F, $00 ; CONTROL_DIRECTED_RECORD_DAD3
.assert (* - BankStart) = $5AD6, error, "bank 1 directed record $DAD3 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDAD6:
    SlotRuntimeRecord $C42F, (ScriptE691 - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DAD6
.assert (* - BankStart) = $5ADF, error, "bank 1 slot record DAD6 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
DirectedRecordDADF:
    SlotRuntimeRecord $FFFF, (RuntimeScriptE764 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_DIRECTED_RECORD_DADF
.assert (* - BankStart) = $5AE8, error, "bank 1 directed record $DADF end"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialDAE8Resource:
    .word $B89F ; CONTROL_SWEEP_RESOURCE_DAE8
.assert (* - BankStart) = $5AEA, error, "bank 1 sweep record field $DAE8 end"
    .incbin "bank1_daea_daec.bin"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialDAE8Fields:
    .byte $00 ; CONTROL_SWEEP_FIELDS_DAE8
.assert (* - BankStart) = $5AED, error, "bank 1 sweep record field $DAEC end"
    .incbin "bank1_daed_daf1.bin"
; Candidate descriptor $DAD6, command $E6DA, mode $00.
SlotFlowDAF1:
    SlotRuntimeRecord $C41D, $674D, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_DAF1
; Candidate descriptor $DAD6, command $E703, mode $00.
SlotFlowDAFA:
    SlotRuntimeRecord $C3C3, $675D, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $5B03, error, "bank 1 slot record flow DAF1 end"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialDB03Resource:
    .word $B896 ; CONTROL_SWEEP_RESOURCE_DB03
.assert (* - BankStart) = $5B05, error, "bank 1 sweep record field $DB03 end"
    .incbin "bank1_db05_db07.bin"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialDB03Fields:
    .byte $00 ; CONTROL_SWEEP_FIELDS_DB03
.assert (* - BankStart) = $5B08, error, "bank 1 sweep record field $DB07 end"
    .incbin "bank1_db08_db0c.bin"
; Candidate descriptor $DB12, command $E6A1, mode $FF.
SlotFlowDB0C:
    SlotCompactRecord $B88D, $23 ; CONTROL_SLOT_FLOW_DB0C
.assert (* - BankStart) = $5B0F, error, "bank 1 slot record flow DB0C end"
; Candidate descriptor $DB12, command $E784, negative mode.
CompactContextDB0F:
    SlotCompactRecord $C4AD, $00 ; CONTROL_COMPACT_CONTEXT_DB0F
.assert (* - BankStart) = $5B12, error, "bank 1 compact candidate db0f end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDB12:
    SlotRuntimeRecord $C4AD, (ScriptE691 - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DB12
.assert (* - BankStart) = $5B1B, error, "bank 1 slot record DB12 end"
    .incbin "bank1_db1b_db1c.bin"
; Observed zero-mode record: resource sentinel and installed script pointer.
; Unread neighbouring bytes stay local; a separate static walk also decodes
; the pointer bytes as a candidate script and has not established reachability.
ObservedRecordDB1BScript:
    .byte $FF
    .word RuntimeScriptE764 - BankStart ; CONTROL_OBSERVED_RECORD_DB1B
.assert (* - BankStart) = $5B1F, error, "bank 1 observed record db1b end"
    .incbin "bank1_db1f_db24.bin"
; Resource pointer read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordDB24Resource:
    .word $B87F ; CONTROL_PARTIAL_RESOURCE_DB24
.assert (* - BankStart) = $5B26, error, "bank 1 partial record $DB24 end"
    .incbin "bank1_db26_db28.bin"
; Mode-specific flags and fields read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordDB24Fields:
    .byte $00 ; CONTROL_PARTIAL_FIELDS_DB24
.assert (* - BankStart) = $5B29, error, "bank 1 partial record $DB28 end"
    .incbin "bank1_db29_db2d.bin"
; Candidate descriptor $DB12, command $E6DA, mode $00.
SlotFlowDB2D:
    SlotRuntimeRecord $C49B, $674D, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_DB2D
; Candidate descriptor $DB12, command $E703, mode $00.
SlotFlowDB36:
    SlotRuntimeRecord $C441, $675D, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $5B3F, error, "bank 1 slot record flow DB2D end"
; Resource pointer read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordDB3FResource:
    .word $B886 ; CONTROL_PARTIAL_RESOURCE_DB3F
.assert (* - BankStart) = $5B41, error, "bank 1 partial record $DB3F end"
    .incbin "bank1_db41_db43.bin"
; Mode-specific flags and fields read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordDB3FFields:
    .byte $00 ; CONTROL_PARTIAL_FIELDS_DB3F
.assert (* - BankStart) = $5B44, error, "bank 1 partial record $DB43 end"
    .incbin "bank1_db44_db48.bin"
; Candidate descriptor $DB4E, command $E89D, negative mode.
CompactContextDB48:
    SlotCompactRecord $B937, $23 ; CONTROL_COMPACT_CONTEXT_DB48
.assert (* - BankStart) = $5B4B, error, "bank 1 compact candidate db48 end"
; Candidate descriptor $DB4E, command $E784, negative mode.
CompactContextDB4B:
    SlotCompactRecord $C5CB, $00 ; CONTROL_COMPACT_CONTEXT_DB4B
.assert (* - BankStart) = $5B4E, error, "bank 1 compact candidate db4b end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDB4E:
    SlotRuntimeRecord $B937, (ScriptED7C - BankStart), $23, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DB4E
.assert (* - BankStart) = $5B57, error, "bank 1 slot record DB4E end"
    .incbin "bank1_db57_db58.bin"
; Possible contact for descriptor base $DB4E; execution remains unverified.
ReviewedContactDB57:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DB57
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5B5B, error, "bank 1 candidate contact db57 end"
    .incbin "bank1_db5b_db60.bin"
; Candidate descriptor $DB66, command $E89D, negative mode.
CompactContextDB60:
    SlotCompactRecord $B876, $22 ; CONTROL_COMPACT_CONTEXT_DB60
.assert (* - BankStart) = $5B63, error, "bank 1 compact candidate db60 end"
    .incbin "bank1_db63_db66.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDB66:
    SlotRuntimeRecord $B876, (ScriptDB81 - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DB66
.assert (* - BankStart) = $5B6F, error, "bank 1 slot record DB66 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordDB6F:
    SlotRuntimeRecord $FFFF, (RuntimeScriptE764 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_DB6F
.assert (* - BankStart) = $5B78, error, "bank 1 sweep record $DB6F end"
; Candidate descriptor $DB66, command $DBC6, mode $00.
SlotFlowDB78:
    SlotRuntimeRecord $B86F, $5BDA, $00, $01, $25, $FF, $12 ; CONTROL_SLOT_FLOW_DB78
.assert (* - BankStart) = $5B81, error, "bank 1 slot record flow DB78 end"
; Slot movement and contact state sequence.
ScriptDBE9 = BankStart + $5BE9
ScriptDB81:
    BogusSetDispatchCounter $86 ; CONTROL_BOGUS_DB81
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot0670Pair $F8, $00
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $40
    BogusSetSlot05F0Pair $20, $FF
    BogusClearSlot0790Bits $01
    BogusSetUnlinkedFields $00, $00
    BogusBranchIfSlotD0Bits ScriptDBC8, $20
    BogusSetSlot0660LowBits $01
    BogusSetSlot0360 $28
ScriptDBA0:
    BogusAddSlotFields00 $08, $00
    BogusSetDispatchCounter $03
    BogusBranchIfSlotCoordinates01 ScriptDBE9, $0C, $08
    BogusBranchIfSlotCoordinates01 ScriptDBBE, $10, $08
    BogusBranchIfSlot0700AtMost ScriptDBA0, $FC
    BogusBranchIfSlot0360Above ScriptDBA0, $01
    BogusBranchIfSlotCoordinatesA3 ScriptDBA0, $C8, $20
    BogusYieldAndSlotAction $00
ScriptDBBE:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadRecordAndClearSavedState $12
ScriptDBC8:
    BogusClearSlotD0Bits $20
    BogusSetSlot05F0Pair $60, $FF
    BogusSetSlotFields40Signed $60, $FF
    BogusSetSlotFields80 $FF, $C0
    BogusStartVoice4 $277A
    BogusWait $0A
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $5BDA, error, "bank 1 script DB81 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptDBDA:
    BogusReadSlotValue $0F ; CONTROL_CONTEXT_DBDA
    BogusBranchIfSlotValueEqual ContextScriptDBE3, $03, $00
    BogusClearSlotD0Bits $40
ContextScriptDBE3:
    BogusWait $28
    BogusSetSlotD0Bits $40
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $5BE9, error, "bank 1 contextual script DBDA end"
; Candidate script path; object role and execution remain unverified.
CandidateDBE9:
    BogusSetDispatchCounter $83 ; CONTROL_BOGUS_DBE9
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast CandidateDC03, $0080
CandidateDBF8:
    BogusAdjustSlotBounds $FF, $00
    BogusBranchIfSlotCoordinatesA3 CandidateDBF8, $10, $FF
    BogusJumpBank1 (BankStart + $5BBE)
CandidateDC03:
    BogusAdjustSlotBounds $01, $00
    BogusBranchIfSlotCoordinatesA3 CandidateDC03, $10, $FF
    BogusJumpBank1 (BankStart + $5BBE)
.assert (* - BankStart) = $5C0E, error, "bank 1 candidate script DBE9 end"
; Candidate descriptor $DC1A, command $DCF9, mode $FF.
SlotFlowDC0E:
    SlotCompactRecord $B6CF, $00 ; CONTROL_SLOT_FLOW_DC0E
; Candidate descriptor $DC1A, command $DCE0, mode $FF.
SlotFlowDC11:
    SlotCompactRecord $BCE9, $00
; Candidate descriptor $DC1A, command $DC4A, mode $FF.
SlotFlowDC14:
    SlotCompactRecord $BCE9, $00
.assert (* - BankStart) = $5C17, error, "bank 1 slot record flow DC0E end"
; Candidate descriptor $DC1A, command $E784, negative mode.
CompactContextDC17:
    SlotCompactRecord $BCE1, $00 ; CONTROL_COMPACT_CONTEXT_DC17
.assert (* - BankStart) = $5C1A, error, "bank 1 compact candidate dc17 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDC1A:
    SlotRuntimeRecord $B6D8, (ScriptDC35 - BankStart), $23, $00, $16, $61, $22 ; CONTROL_SLOT_RUNTIME_DC1A
.assert (* - BankStart) = $5C23, error, "bank 1 slot record DC1A end"
    .incbin "bank1_dc23_dc2c.bin"
; Candidate descriptor $DC1A, script $DCFE, mode $02.
ModeRecordDC2CResource:
    .word $B6D8 ; CONTROL_MODE_RECORD_DC2C_RESOURCE
.assert (* - BankStart) = $5C2E, error, "bank 1 candidate mode record dc2c resource end"
    .incbin "bank1_dc2e_dc30.bin"
; Candidate descriptor $DC1A, script $DCFE, mode $02.
ModeRecordDC2CFields:
    .byte $23, $00, $16, $61, $22 ; CONTROL_MODE_RECORD_DC2C_FIELDS
.assert (* - BankStart) = $5C35, error, "bank 1 candidate mode record dc2c fields end"
; Connected movement and interaction state-machine paths. The byte-level
; conditions are reconstructed; the associated gameplay role remains unknown.
ScriptDC35:
    BogusSetSlot05F0Pair $40, $60
    BogusSetSlot0640Pair $04, $02
    BogusSetSlot0670Pair $01, $08
    BogusSetUnlinkedFields $00, $00
    BogusClearSlot0790Bits $01
ScriptDC43:
    BogusBranchIfSlotD0BitsClear ScriptDC50, $20
    BogusRestartVoice4 $277A
    BogusLoadSlotRecord $06, $FF
    BogusSetLinkedSlotFieldsC0 $18, $A0
ScriptDC50:
    BogusBranchIfSlot0620Bit10Clear ScriptDC50
    BogusLoadSlotRecord $00, $02
    BogusBranchIfSlotFieldsWithin ScriptDCC5, $07, $FF
ScriptDC5B:
    BogusSetSlot0620Bit20
    BogusBranchIfAbsSlot0700Below ScriptDCAE, $18
    BogusBranchIfDirectionalOffsetClear ScriptDCAE, $0C
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptDC73, $0080
    BogusBranchIfSlotOffset ScriptDCAE, $02, $00
    BogusJumpBank1 ScriptDC78
ScriptDC73:
    BogusBranchIfSlotOffset ScriptDCAE, $FE, $00
ScriptDC78:
    BogusSetSlot0620Bit20
    BogusBranchIfSlotCoordinates01 ScriptDCD2, $28, $18
    BogusBranchIfSlotCoordinates01 ScriptDCF1, $48, $18
    BogusBranchIfSlotCoordinatesA3 ScriptDCAA, $FF, $17
    BogusSetSlot0620Bit20
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual ScriptDC97, $0001
    BogusBranchIfOffsetProbe ScriptDD3D, $05
    BogusJumpBank1 ScriptDCAA
ScriptDC97:
    BogusBranchIfSlotValueNotEqual ScriptDCAA, $0000
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusWait $03
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusLoadRecordAndClearSavedState $00
ScriptDCAA:
    BogusSetSlot0620Bit20
    BogusJumpBank1 ScriptDC43
ScriptDCAE:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusSetSlot0620Bit20
    BogusWait $04
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusSetSlot0620Bit20
    BogusWait $08
    BogusSetDirectionalSlotFields40 $F8, $FF
    BogusJumpBank1 ScriptDC50
ScriptDCC5:
    BogusSetSlot0620Bit20
    BogusSetDispatchCounter $83
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $10, $FF ; CONTROL_BOGUS_DC35
    BogusSetSlot0660LowBits $00
    BogusJumpBank1 ScriptDC5B
ScriptDCD2:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $28, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetUnlinkedFields $20, $00
    BogusBranchAndClearSlot0620Bit08 ScriptDD55
    BogusLoadRecordAndClearSavedState $00
ScriptDCF1:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $0C, $FF
    BogusWait $14
    BogusLoadSlotRecord $12, $02
    BogusBranchIfSlotCoordinates01 ScriptDCD2, $28, $18
    BogusBranchIfSlotCoordinates01 ScriptDD0E, $48, $18
    BogusJumpBank1 ScriptDCC5
ScriptDD0E:
    BogusSetDirectionalSlotFields40 $40, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlotFields80 $FF, $D0
    BogusSetUnlinkedFields $20, $00
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusBranchAndClearSlot0620Bit08 ScriptDD55
    BogusLoadRecordAndClearSavedState $00
ScriptDD3D:
    BogusSetDispatchCounter $84
    BogusLoadSlotRecord $06, $FF
    BogusSetSlotFields80 $00, $A0
    BogusSetDirectionalSlotFields40 $02, $FF
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusLoadRecordAndClearSavedState $00
ScriptDD55:
    BogusWait $0F
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $5D59, error, "bank 1 script DC35 end"
; Candidate descriptor $DD62, command $DED7, mode $FF.
SlotFlowDD59:
    SlotCompactRecord $C117, $00 ; CONTROL_SLOT_FLOW_DD59
.assert (* - BankStart) = $5D5C, error, "bank 1 slot record flow DD59 end"
; Candidate descriptor $DD62, command $E89D, negative mode.
CompactContextDD5C:
    SlotCompactRecord $B7AA, $22 ; CONTROL_COMPACT_CONTEXT_DD5C
.assert (* - BankStart) = $5D5F, error, "bank 1 compact candidate dd5c end"
; Candidate descriptor $DD62, command $E784, negative mode.
CompactContextDD5F:
    SlotCompactRecord $C0F9, $00 ; CONTROL_COMPACT_CONTEXT_DD5F
.assert (* - BankStart) = $5D62, error, "bank 1 compact candidate dd5f end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDD62:
    SlotRuntimeRecord $B7AA, (ScriptDE0D - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DD62
.assert (* - BankStart) = $5D6B, error, "bank 1 slot record DD62 end"
    .incbin "bank1_dd6b_dd6c.bin"
; Possible contact for descriptor base $DD62; execution remains unverified.
ReviewedContactDD6B:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DD6B
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5D6F, error, "bank 1 candidate contact dd6b end"
    .incbin "bank1_dd6f_dd74.bin"
; Candidate descriptor $DD62, command $DE81, mode $00.
SlotFlowDD74:
    SlotRuntimeRecord $B7AA, $5ED0, $23, $00, $16, $61, $22 ; CONTROL_SLOT_FLOW_DD74
; Candidate descriptor $DD62, command $DE60, mode $00.
SlotFlowDD7D:
    SlotRuntimeRecord $B7A3, $5EC7, $00, $00, $25, $FF, $12
.assert (* - BankStart) = $5D86, error, "bank 1 slot record flow DD74 end"
; Candidate descriptor $DD8F, command $DED7, mode $FF.
SlotFlowDD86:
    SlotCompactRecord $C0B1, $00 ; CONTROL_SLOT_FLOW_DD86
.assert (* - BankStart) = $5D89, error, "bank 1 slot record flow DD86 end"
; Candidate descriptor $DD8F, command $E89D, negative mode.
CompactContextDD89:
    SlotCompactRecord $B7B3, $22 ; CONTROL_COMPACT_CONTEXT_DD89
.assert (* - BankStart) = $5D8C, error, "bank 1 compact candidate dd89 end"
; Candidate descriptor $DD8F, command $E784, negative mode.
CompactContextDD8C:
    SlotCompactRecord $C0A7, $00 ; CONTROL_COMPACT_CONTEXT_DD8C
.assert (* - BankStart) = $5D8F, error, "bank 1 compact candidate dd8c end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDD8F:
    SlotRuntimeRecord $B7B3, (ScriptDE0D - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DD8F
.assert (* - BankStart) = $5D98, error, "bank 1 slot record DD8F end"
    .incbin "bank1_dd98_dd99.bin"
; Possible contact for descriptor base $DD8F; execution remains unverified.
ReviewedContactDD98:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DD98
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5D9C, error, "bank 1 candidate contact dd98 end"
    .incbin "bank1_dd9c_dda1.bin"
; Candidate descriptor $DD8F, command $DE81, mode $00.
SlotFlowDDA1:
    SlotRuntimeRecord $B7B3, $5ED0, $23, $00, $16, $61, $22 ; CONTROL_SLOT_FLOW_DDA1
; Candidate descriptor $DD8F, command $DE60, mode $00.
SlotFlowDDAA:
    SlotRuntimeRecord $B7BC, $5EC7, $00, $01, $65, $FF, $12
.assert (* - BankStart) = $5DB3, error, "bank 1 slot record flow DDA1 end"
; Candidate descriptor $DDBC, command $DED7, mode $FF.
SlotFlowDDB3:
    SlotCompactRecord $C389, $00 ; CONTROL_SLOT_FLOW_DDB3
.assert (* - BankStart) = $5DB6, error, "bank 1 slot record flow DDB3 end"
; Candidate descriptor $DDBC, command $E89D, negative mode.
CompactContextDDB6:
    SlotCompactRecord $B866, $22 ; CONTROL_COMPACT_CONTEXT_DDB6
.assert (* - BankStart) = $5DB9, error, "bank 1 compact candidate ddb6 end"
; Candidate descriptor $DDBC, command $E784, negative mode.
CompactContextDDB9:
    SlotCompactRecord $C36B, $00 ; CONTROL_COMPACT_CONTEXT_DDB9
.assert (* - BankStart) = $5DBC, error, "bank 1 compact candidate ddb9 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDDBC:
    SlotRuntimeRecord $B866, (ScriptDE0D - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DDBC
.assert (* - BankStart) = $5DC5, error, "bank 1 slot record DDBC end"
    .incbin "bank1_ddc5_ddc6.bin"
; Possible contact for descriptor base $DDBC; execution remains unverified.
ReviewedContactDDC5:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DDC5
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5DC9, error, "bank 1 candidate contact ddc5 end"
    .incbin "bank1_ddc9_ddce.bin"
; Candidate descriptor $DDBC, command $DE81, mode $00.
SlotFlowDDCE:
    SlotRuntimeRecord $B866, $5ED0, $23, $00, $16, $61, $22 ; CONTROL_SLOT_FLOW_DDCE
; Candidate descriptor $DDBC, command $DE60, mode $00.
SlotFlowDDD7:
    SlotRuntimeRecord $B85F, $5EC7, $00, $01, $25, $FF, $12
.assert (* - BankStart) = $5DE0, error, "bank 1 slot record flow DDCE end"
; Candidate descriptor $DDE9, command $DED7, mode $FF.
SlotFlowDDE0:
    SlotCompactRecord $C06D, $00 ; CONTROL_SLOT_FLOW_DDE0
.assert (* - BankStart) = $5DE3, error, "bank 1 slot record flow DDE0 end"
; Candidate descriptor $DDE9, command $E89D, negative mode.
CompactContextDDE3:
    SlotCompactRecord $B79A, $22 ; CONTROL_COMPACT_CONTEXT_DDE3
.assert (* - BankStart) = $5DE6, error, "bank 1 compact candidate dde3 end"
; Candidate descriptor $DDE9, command $E784, negative mode.
CompactContextDDE6:
    SlotCompactRecord $C075, $00 ; CONTROL_COMPACT_CONTEXT_DDE6
.assert (* - BankStart) = $5DE9, error, "bank 1 compact candidate dde6 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDDE9:
    SlotRuntimeRecord $B79A, (ScriptDE0D - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DDE9
.assert (* - BankStart) = $5DF2, error, "bank 1 slot record DDE9 end"
    .incbin "bank1_ddf2_ddf3.bin"
; Possible contact for descriptor base $DDE9; execution remains unverified.
ReviewedContactDDF2:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_DDF2
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $5DF6, error, "bank 1 candidate contact ddf2 end"
    .incbin "bank1_ddf6_ddfb.bin"
; Candidate descriptor $DDE9, command $DE81, mode $00.
SlotFlowDDFB:
    SlotRuntimeRecord $B79A, $5ED0, $23, $00, $16, $61, $22 ; CONTROL_SLOT_FLOW_DDFB
; Candidate descriptor $DDE9, command $DE60, mode $00.
SlotFlowDE04:
    SlotRuntimeRecord $B793, $5EC7, $00, $01, $25, $FF, $12
.assert (* - BankStart) = $5E0D, error, "bank 1 slot record flow DDFB end"
; Descriptor-derived movement and interaction state machine; gameplay role is provisional.
ScriptDE0D:
    BogusSetDispatchCounter $86 ; CONTROL_BOGUS_DE0D
    BogusSetSlot0640Pair $04, $00
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlot05F0Pair $20, $60
    BogusClearSlot0790Bits $01
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0660LowBits $01
ScriptDE21:
    BogusSetSlot0670Pair $40, $00
    BogusReadSlotValue $07
    BogusBranchIfSlotValueEqual ScriptDE62, $FF, $FF
    BogusBranchIfSlotCoordinates01 ScriptDEA2, $14, $08
    BogusBranchIfSlotCoordinates01 ScriptDE58, $1C, $08
    BogusSetDispatchCounter $84
    BogusBranchIfSlotCoordinatesA3 ScriptDE50, $FF, $40
ScriptDE3C:
    BogusBranchIfAbsSlot0700Below ScriptDE48, $40
    BogusSetDirectionalSlotFields40 $08, $FF
    BogusWait $04
    BogusJumpBank1 ScriptDE21
ScriptDE48:
    BogusSetSlotFields40Signed $08, $00
    BogusWait $02
    BogusJumpBank1 ScriptDE21
ScriptDE50:
    BogusSetSlotFields80 $20, $FF
    BogusWait $04
    BogusJumpBank1 ScriptDE21
ScriptDE58:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadRecordAndClearSavedState $1B
ScriptDE62:
    BogusSetDispatchCounter $05
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinates01 ScriptDE77, $40, $28
    BogusAdvanceAndBranchState1B ScriptDE3C, $80
    BogusAdvanceAndBranchState1B ScriptDE83, $80
    BogusJumpBank1 ScriptDE3C
ScriptDE77:
    BogusSetDispatchCounter $84
    BogusSetSlot0660LowBits $00
    BogusSetSlot05F0Pair $60, $60
    BogusSetDirectionalSlotFields40 $30, $FF
    BogusLoadRecordAndClearSavedState $12
ScriptDE83:
    BogusBranchIfSlot0700AtMost ScriptDE3C, $40
    BogusBranchIfSlot0700AtMost ScriptDE8E, $60
    BogusJumpBank1 ScriptDE3C
ScriptDE8E:
    BogusSetSlot0360 $50
ScriptDE90:
    BogusSetSlotFields80 $00, $FF
    BogusSetSlot0670Pair $41, $00
    BogusBranchIfSlotCoordinatesA3 ScriptDE21, $80, $28
    BogusBranchIfSlot0360Above ScriptDE90, $01
    BogusJumpBank1 ScriptDE21
ScriptDEA2:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptDEBC, $0080
ScriptDEB1:
    BogusAdjustSlotBounds $FF, $00
    BogusBranchIfSlotCoordinatesA3 ScriptDEB1, $18, $FF
    BogusJumpBank1 ScriptDE58
ScriptDEBC:
    BogusAdjustSlotBounds $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptDEBC, $18, $FF
    BogusJumpBank1 ScriptDE58
.assert (* - BankStart) = $5EC7, error, "bank 1 script DE0D end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptDEC7:
    BogusSetSlot0670Pair $40, $00 ; CONTROL_CONTEXT_DEC7
    BogusSetSlot0620Bit20
    BogusWait $3C
    BogusSetSlot0620Bit20
    BogusLoadRecordAndClearSavedState $00
ContextScriptDED0:
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $FF, $B0
    BogusSetSlotMode $03
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
ContextScriptDEE9:
    BogusBranchIfSlot0620Bit10Clear ContextScriptDEE9
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $5EEE, error, "bank 1 contextual script DEC7 end"
; Candidate descriptor $DEF4, command $DF34, mode $FF.
SlotFlowDEEE:
    SlotCompactRecord $B7B3, $23 ; CONTROL_SLOT_FLOW_DEEE
.assert (* - BankStart) = $5EF1, error, "bank 1 slot record flow DEEE end"
; Compact record observed in negative loader mode.
SweepRecordDEF1:
    SlotCompactRecord $C0BB, $00 ; CONTROL_SWEEP_RECORD_DEF1
.assert (* - BankStart) = $5EF4, error, "bank 1 sweep record $DEF1 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeDEF4:
    SlotRuntimeRecord $B7BC, (ScriptDF0F - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_DEF4
.assert (* - BankStart) = $5EFD, error, "bank 1 slot record DEF4 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordDEFD:
    SlotRuntimeRecord $FFFF, (RuntimeScriptE764 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_DEFD
.assert (* - BankStart) = $5F06, error, "bank 1 sweep record $DEFD end"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialDF06Resource:
    .word $C0B1 ; CONTROL_SWEEP_RESOURCE_DF06
.assert (* - BankStart) = $5F08, error, "bank 1 sweep record field $DF06 end"
    .incbin "bank1_df08_df0a.bin"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialDF06Fields:
    .byte $00, $00, $25, $D9, $22 ; CONTROL_SWEEP_FIELDS_DF06
.assert (* - BankStart) = $5F0F, error, "bank 1 sweep record field $DF0A end"
; Slot movement and linked-slot checks with branches into several update paths.
; The final $00 command can load a new record and change the script pointer.
ScriptDF0F:
    BogusSetDispatchCounter $86
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot05F0Pair $40, $60
    BogusSetSlotD0Bits $40
    BogusClearSlot0790Bits $01
    BogusSetSlot0670Pair $00, $08
    BogusBranchIfSlotD0Bits ScriptDFE9, $20
ScriptDF22:
    BogusReadSlotValue $07
    BogusBranchIfSlotValueNotEqual ScriptDF34, $FFFF
    BogusLoadSlotRecord $00, $01
    BogusSetUnlinkedFields $20, $00
    BogusWait $0A
    BogusJumpBank1 ScriptDF22
ScriptDF34:
    BogusLoadSlotRecord $06, $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0660LowBits $01
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $10, $FF ; CONTROL_BOGUS_DF0F
    BogusBranchIfSlotCoordinatesA3 ScriptDFAA, $48, $28
    BogusBranchIfSlotCoordinatesA3 ScriptDF4E, $58, $FF
    BogusSetSlotFields80 $20, $FF
ScriptDF4E:
    BogusBranchIfSlotCoordinatesA3 ScriptDF82, $FF, $08
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual ScriptDF69, $01, $00
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusWait $01
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusJumpBank1 ScriptDF7C
ScriptDF69:
    BogusBranchIfOffsetProbe ScriptDF72, $05
    BogusWait $0A
    BogusJumpBank1 ScriptDF22
ScriptDF72:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $A0
ScriptDF7C:
    BogusBranchIfSlot0620Bit10Clear ScriptDF7C
    BogusJumpBank1 ScriptDF22
ScriptDF82:
    BogusBranchIfDirectionalOffsetClear ScriptDF9D, $28
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptDF95, $0080
    BogusBranchIfSlotOffset ScriptDF9D, $02, $00
    BogusJumpBank1 ScriptDF9A
ScriptDF95:
    BogusBranchIfSlotOffset ScriptDF9D, $FE, $00
ScriptDF9A:
    BogusJumpBank1 ScriptDF22
ScriptDF9D:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $A0
    BogusSetDirectionalSlotFields40 $30, $FF
    BogusSetSlotMode $03
    BogusJumpBank1 ScriptDF7C
ScriptDFAA:
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual ScriptDFB9, $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptDFB9, $FF, $08
    BogusJumpBank1 ScriptDF4E
ScriptDFB9:
    BogusLoadSlotRecord $12, $02
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $40, $D8
    BogusSetSlotMode $03
    BogusBranchIfSlotCoordinatesA3 ScriptDFCB, $FF, $10
    BogusSetSlotFields80 $FF, $B0
ScriptDFCB:
    BogusSetSlot0620Bit20
    BogusAddSlotFields00 $00, $F0
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusLoadSlotRecord $06, $FF
    BogusSetUnlinkedFields $20, $00
    BogusWait $0A
    BogusJumpBank1 ScriptDF22
ScriptDFE9:
    BogusLoadSlotRecord $12, $01
    BogusSetLinkedSlotFieldsC0 $40, $B0
    BogusSetUnlinkedFields $20, $00
    BogusClearSlotD0Bits $20
ScriptDFF4:
    BogusBranchIfSlot0620Bit10Clear ScriptDFF4
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $5FF9, error, "bank 1 script DF0F end"
; Candidate descriptor $E008, command $E24B, mode $FF.
SlotFlowDFF9:
    SlotCompactRecord $B831, $00 ; CONTROL_SLOT_FLOW_DFF9
; Candidate descriptor $E008, command $E19A, mode $FF.
SlotFlowDFFC:
    SlotCompactRecord $B82A, $00
; Candidate descriptor $E008, command $E172, mode $FF.
SlotFlowDFFF:
    SlotCompactRecord $B831, $00
.assert (* - BankStart) = $6002, error, "bank 1 slot record flow DFF9 end"
    .incbin "bank1_e002_e008.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE008:
    SlotRuntimeRecord $B82A, (ScriptE02C - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E008
.assert (* - BankStart) = $6011, error, "bank 1 slot record E008 end"
    .incbin "bank1_e011_e02c.bin"
; Four entry points choose slot flags before entering the shared $E120 path.
ScriptE02C:
    BogusSetSlotD0Bits $03       ; CONTROL_BOGUS_E02C
    BogusSetSlotValue $0007
    BogusJumpBank1 ScriptE120
.assert (* - BankStart) = $6034, error, "bank 1 script E02C end"
; Candidate descriptor $E043, command $E24B, mode $FF.
SlotFlowE034:
    SlotCompactRecord $B9F1, $00 ; CONTROL_SLOT_FLOW_E034
; Candidate descriptor $E043, command $E19A, mode $FF.
SlotFlowE037:
    SlotCompactRecord $B9EA, $00
; Candidate descriptor $E043, command $E172, mode $FF.
SlotFlowE03A:
    SlotCompactRecord $B9F8, $00
.assert (* - BankStart) = $603D, error, "bank 1 slot record flow E034 end"
    .incbin "bank1_e03d_e043.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE043:
    SlotRuntimeRecord $B9E1, (ScriptE067 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E043
.assert (* - BankStart) = $604C, error, "bank 1 slot record E043 end"
    .incbin "bank1_e04c_e04d.bin"
; Possible contact for descriptor base $E043; execution remains unverified.
ReviewedContactE04C:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_E04C
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6050, error, "bank 1 candidate contact e04c end"
    .incbin "bank1_e050_e05e.bin"
; Candidate descriptor $E043, script $E262, mode $02.
ModeRecordE05EResource:
    .word $B9F1 ; CONTROL_MODE_RECORD_E05E_RESOURCE
.assert (* - BankStart) = $6060, error, "bank 1 candidate mode record e05e resource end"
    .incbin "bank1_e060_e062.bin"
; Candidate descriptor $E043, script $E262, mode $02.
ModeRecordE05EFields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_E05E_FIELDS
.assert (* - BankStart) = $6067, error, "bank 1 candidate mode record e05e fields end"
ScriptE067:
    BogusSetSlotD0Bits $02       ; CONTROL_BOGUS_E067
    BogusSetSlotValue $0007
    BogusJumpBank1 ScriptE120
.assert (* - BankStart) = $606F, error, "bank 1 script E067 end"
; Candidate descriptor $E07E, command $E24B, mode $FF.
SlotFlowE06F:
    SlotCompactRecord $B693, $00 ; CONTROL_SLOT_FLOW_E06F
; Candidate descriptor $E07E, command $E19A, mode $FF.
SlotFlowE072:
    SlotCompactRecord $B69E, $00
; Candidate descriptor $E07E, command $E172, mode $FF.
SlotFlowE075:
    SlotCompactRecord $B69E, $00
.assert (* - BankStart) = $6078, error, "bank 1 slot record flow E06F end"
    .incbin "bank1_e078_e07e.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE07E:
    SlotRuntimeRecord $BCB1, (ScriptE0A2 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E07E
.assert (* - BankStart) = $6087, error, "bank 1 slot record E07E end"
    .incbin "bank1_e087_e099.bin"
; Candidate descriptor $E07E, script $E262, mode $02.
ModeRecordE099Resource:
    .word $B693 ; CONTROL_MODE_RECORD_E099_RESOURCE
.assert (* - BankStart) = $609B, error, "bank 1 candidate mode record e099 resource end"
    .incbin "bank1_e09b_e09d.bin"
; Candidate descriptor $E07E, script $E262, mode $02.
ModeRecordE099Fields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_E099_FIELDS
.assert (* - BankStart) = $60A2, error, "bank 1 candidate mode record e099 fields end"
ScriptE0A2:
    BogusSetSlotD0Bits $02       ; CONTROL_BOGUS_E0A2
    BogusSetSlotValue $0007
    BogusJumpBank1 ScriptE120
.assert (* - BankStart) = $60AA, error, "bank 1 script E0A2 end"
; Candidate descriptor $E0B9, command $E24B, mode $FF.
SlotFlowE0AA:
    SlotCompactRecord $B611, $00 ; CONTROL_SLOT_FLOW_E0AA
; Candidate descriptor $E0B9, command $E19A, mode $FF.
SlotFlowE0AD:
    SlotCompactRecord $B61F, $00
; Candidate descriptor $E0B9, command $E172, mode $FF.
SlotFlowE0B0:
    SlotCompactRecord $B618, $00
.assert (* - BankStart) = $60B3, error, "bank 1 slot record flow E0AA end"
    .incbin "bank1_e0b3_e0b9.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE0B9:
    SlotRuntimeRecord $BB1F, (ScriptE0DD - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E0B9
.assert (* - BankStart) = $60C2, error, "bank 1 slot record E0B9 end"
    .incbin "bank1_e0c2_e0c3.bin"
; Possible contact for descriptor base $E0B9; execution remains unverified.
ReviewedContactE0C2:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_E0C2
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $60C6, error, "bank 1 candidate contact e0c2 end"
    .incbin "bank1_e0c6_e0cb.bin"
; Candidate descriptor $E0B9, script $E232, mode $02.
ModeRecordE0CBResource:
    .word $B611 ; CONTROL_MODE_RECORD_E0CB_RESOURCE
.assert (* - BankStart) = $60CD, error, "bank 1 candidate mode record e0cb resource end"
    .incbin "bank1_e0cd_e0cf.bin"
; Candidate descriptor $E0B9, script $E232, mode $02.
ModeRecordE0CBFields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_E0CB_FIELDS
.assert (* - BankStart) = $60D4, error, "bank 1 candidate mode record e0cb fields end"
; Candidate descriptor $E0B9, script $E262, mode $02.
ModeRecordE0D4Resource:
    .word $B611 ; CONTROL_MODE_RECORD_E0D4_RESOURCE
.assert (* - BankStart) = $60D6, error, "bank 1 candidate mode record e0d4 resource end"
    .incbin "bank1_e0d6_e0d8.bin"
; Candidate descriptor $E0B9, script $E262, mode $02.
ModeRecordE0D4Fields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_E0D4_FIELDS
.assert (* - BankStart) = $60DD, error, "bank 1 candidate mode record e0d4 fields end"
ScriptE0DD:
    BogusSetSlotD0Bits $0B       ; CONTROL_BOGUS_E0DD
    BogusSetSlotValue $0007
    BogusJumpBank1 ScriptE120
.assert (* - BankStart) = $60E5, error, "bank 1 script E0DD end"
; Candidate descriptor $E0F4, command $E24B, mode $FF.
SlotFlowE0E5:
    SlotCompactRecord $BB43, $00 ; CONTROL_SLOT_FLOW_E0E5
; Candidate descriptor $E0F4, command $E19A, mode $FF.
SlotFlowE0E8:
    SlotCompactRecord $B62F, $00
; Candidate descriptor $E0F4, command $E172, mode $FF.
SlotFlowE0EB:
    SlotCompactRecord $B62F, $00
.assert (* - BankStart) = $60EE, error, "bank 1 slot record flow E0E5 end"
    .incbin "bank1_e0ee_e0f4.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE0F4:
    SlotRuntimeRecord $BB3D, (ScriptE118 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E0F4
.assert (* - BankStart) = $60FD, error, "bank 1 slot record E0F4 end"
    .incbin "bank1_e0fd_e10f.bin"
; Candidate descriptor $E0F4, script $E262, mode $02.
ModeRecordE10FResource:
    .word $B626 ; CONTROL_MODE_RECORD_E10F_RESOURCE
.assert (* - BankStart) = $6111, error, "bank 1 candidate mode record e10f resource end"
    .incbin "bank1_e111_e113.bin"
; Candidate descriptor $E0F4, script $E262, mode $02.
ModeRecordE10FFields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_E10F_FIELDS
.assert (* - BankStart) = $6118, error, "bank 1 candidate mode record e10f fields end"
; Connected shared slot state machine. Its higher-level object and role remain unknown.
ScriptE118:
    BogusSetSlotD0Bits $1E ; CONTROL_BOGUS_E118
    BogusSetSlotValue $0007
    BogusJumpBank1 ScriptE120
ScriptE120:
    BogusSetDispatchCounter $04
    BogusStoreSlotValueArray $FF
    BogusSetSlotC0 $FF
    BogusClearSlot0790Bits $01
    BogusBranchIfSlot0620Bit10Clear ScriptE120
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot05F0Pair $40, $60
    BogusSetSlot0660LowBits $00
    BogusSetSlot0660HighBits $00
ScriptE135:
    BogusBranchIfSlotD0BitsClear ScriptE141, $08
    BogusSetSlot0670Pair $28, $04
    BogusBranchIfSlotCoordinatesA3 ScriptE179, $28, $10
ScriptE141:
    BogusBranchIfSlotD0BitsClear ScriptE14D, $03
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE1A5, $40, $40
ScriptE14D:
    BogusSetDispatchCounter $84
    BogusBranchIfSlotD0BitsClear ScriptE160, $04
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FF, $FF
    BogusBranchIfDirectionalOffsetClear ScriptE160, $28
    BogusJumpBank1 ScriptE280
ScriptE160:
    BogusWait $03
    BogusAdvanceAndBranchState1B ScriptE135, $E8
    BogusAdvanceAndBranchState1B ScriptE135, $80
    BogusAdvanceAndBranchState1B ScriptE172, $80
    BogusBranchIfSlotD0Bits ScriptE24B, $10
ScriptE172:
    BogusLoadSlotRecord $09, $FF
    BogusWait $14
    BogusLoadRecordAndClearSavedState $00
ScriptE179:
    BogusLoadSlotRecord $00, $02
    BogusSetSlot0670Pair $28, $04
    BogusSetSlot0660LowBits $01
    BogusSetSlotC0 $FF
    BogusSetUnlinkedFields $20, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE197, $10, $10
    BogusSetSlotFields80 $08, $C0
    BogusWait $07
ScriptE190:
    BogusBranchIfSlotCoordinatesA3 ScriptE179, $28, $10
    BogusLoadRecordAndClearSavedState $00
ScriptE197:
    BogusSetSlotFields80 $01, $FF
    BogusLoadSlotRecord $0C, $FF
ScriptE19D:
    BogusBranchIfSlotCoordinatesA3 ScriptE19D, $10, $10
    BogusJumpBank1 ScriptE190
ScriptE1A5:
    BogusBranchIfSlotD0BitsClear ScriptE24B, $01
    BogusBranchIfSlotB0AtMost ScriptE1B9, $30
    BogusBranchIfOffsetProbe ScriptE1D5, $05
    BogusBranchIfSlotB0AtMost ScriptE1B9, $60
    BogusBranchIfOffsetProbe ScriptE207, $0B
ScriptE1B9:
    BogusBranchIfSlotB0AtMost ScriptE1C0, $B8
    BogusJumpBank1 ScriptE1CF
ScriptE1C0:
    BogusBranchIfPositiveOffsetProbe ScriptE224, $06
    BogusBranchIfSlotB0AtMost ScriptE1CB, $88
    BogusJumpBank1 ScriptE1CF
ScriptE1CB:
    BogusBranchIfOffsetProbe ScriptE224, $0C
ScriptE1CF:
    BogusBranchIfSlotD0Bits ScriptE24B, $02
    BogusLoadRecordAndClearSavedState $00
ScriptE1D5:
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual ScriptE1B9, $01, $00
    BogusLoadSlotRecord $12, $02
    BogusRestartVoice4 $285F
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $F8
    BogusSetSlotMode $03
ScriptE1ED:
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusLoadRecordAndClearSavedState $00
ScriptE207:
    BogusLoadSlotRecord $12, $02
    BogusRestartVoice4 $285F
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $F8
    BogusSetSlotMode $03
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusJumpBank1 ScriptE1ED
ScriptE224:
    BogusReadSlotValue $1A
    BogusBranchIfSlotValueEqual ScriptE232, $00, $00
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual ScriptE1CF, $00, $00
ScriptE232:
    BogusLoadSlotRecord $12, $02
    BogusRestartVoice4 $285F
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotC0 $02
    BogusWait $04
    BogusBranchIfSlot0620Bit10Clear ScriptE247
    BogusBranchIfSlotD0BitsClear ScriptE207, $02
ScriptE247:
    BogusSetSlotMode $02
    BogusLoadRecordAndClearSavedState $00
ScriptE24B:
    BogusLoadSlotRecord $0F, $FF
    BogusSetSlotC0 $04
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $02
    BogusSetSlot0660HighBits $00
    BogusSetSlotFields80 $40, $E0
    BogusWait $08
    BogusSetSlotC0 $00
    BogusLoadSlotRecord $1B, $02
    BogusRestartVoice4 $285F
ScriptE268:
    BogusSetSlotFields40Signed $08, $08
    BogusSetDispatchCounter $83
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusBranchIfPositiveOffsetProbe ScriptE27E, $06
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusJumpBank1 ScriptE268
ScriptE27E:
    BogusLoadRecordAndClearSavedState $00
ScriptE280:
    BogusSetSlot05F0Pair $40, $78
    BogusSetSlotC0 $20
    BogusSetUnlinkedFields $20, $00
ScriptE288:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $88
    BogusSetDirectionalSlotFields40 $08, $FF
    BogusLoadSlotRecord $00, $02
ScriptE293:
    BogusBranchIfSlot0620Bit10Clear ScriptE293
    BogusSetDispatchCounter $06
    BogusSetSlot0670Pair $28, $04
    BogusBranchIfSlotCoordinates01 ScriptE179, $1E, $10
    BogusBranchIfAbsSlot0700Below ScriptE2CD, $18
    BogusBranchIfDirectionalOffsetClear ScriptE2CD, $0C
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptE2B7, $0080
    BogusBranchIfSlotOffset ScriptE2CD, $02, $00
    BogusJumpBank1 ScriptE2BC
ScriptE2B7:
    BogusBranchIfSlotOffset ScriptE2CD, $FE, $00
ScriptE2BC:
    BogusAdvanceAndBranchState1B ScriptE2D8, $20
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE27E, $28, $28
    BogusWait $04
    BogusJumpBank1 ScriptE288
ScriptE2CD:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusJumpBank1 ScriptE288
ScriptE2D8:
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0360 $14
    BogusSetSlot0670Pair $01, $00
ScriptE2E8:
    BogusBranchIfSlotCoordinatesA3 ScriptE2F4, $28, $28
    BogusBranchIfSlot0360Above ScriptE2E8, $01
    BogusJumpBank1 ScriptE288
ScriptE2F4:
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $62F6, error, "bank 1 script E118 end"
; Candidate descriptor $E2FC, command $E89D, negative mode.
CompactContextE2F6:
    SlotCompactRecord $B8E7, $23 ; CONTROL_COMPACT_CONTEXT_E2F6
.assert (* - BankStart) = $62F9, error, "bank 1 compact candidate e2f6 end"
; Candidate descriptor $E2FC, command $E784, negative mode.
CompactContextE2F9:
    SlotCompactRecord $B8D5, $00 ; CONTROL_COMPACT_CONTEXT_E2F9
.assert (* - BankStart) = $62FC, error, "bank 1 compact candidate e2f9 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE2FC:
    SlotRuntimeRecord $B8E7, (ScriptE486 - BankStart), $23, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E2FC
.assert (* - BankStart) = $6305, error, "bank 1 slot record E2FC end"
    .incbin "bank1_e305_e306.bin"
; Possible contact for descriptor base $E2FC; execution remains unverified.
ReviewedContactE305:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_E305
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6309, error, "bank 1 candidate contact e305 end"
    .incbin "bank1_e309_e30e.bin"
; Candidate descriptor $E2FC, command $E4B0, mode $00.
SlotFlowE30E:
    SlotRuntimeRecord $C4E9, $68F2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E30E
.assert (* - BankStart) = $6317, error, "bank 1 slot record flow E30E end"
; Candidate native position-event record; resource payload remains local.
PositionRecordE317:
    SlotRuntimeRecord $B8DC, (LongScriptE527 - BankStart), $13, $FF, $00, $00, $00 ; CONTROL_POSITION_RECORD_E317
.assert (* - BankStart) = $6320, error, "bank 1 position record E317 end"
; Candidate descriptor $E2FC, command $E56C, mode $00.
SlotFlowE320:
    SlotRuntimeRecord $C501, $6592, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E320
; Candidate descriptor $E2FC, command $E683, mode $00.
SlotFlowE329:
    SlotRuntimeRecord $B8F0, $65AA, $40, $FF, $00, $00, $00
; Candidate descriptor $E2FC, command $E503, mode $00.
SlotFlowE332:
    SlotRuntimeRecord $B8E7, $6605, $00, $FF, $00, $00, $00
; Candidate descriptor $E2FC, command $E590, mode $00.
SlotFlowE33B:
    SlotRuntimeRecord $B8CE, $6640, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $6344, error, "bank 1 slot record flow E320 end"
; Candidate descriptor $E34A, command $E89D, negative mode.
CompactContextE344:
    SlotCompactRecord $B99F, $23 ; CONTROL_COMPACT_CONTEXT_E344
.assert (* - BankStart) = $6347, error, "bank 1 compact candidate e344 end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordE347:
    SlotCompactRecord $C6DB, $00 ; CONTROL_RUNTIME_RECORD_E347
.assert (* - BankStart) = $634A, error, "bank 1 runtime records $E347 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE34A:
    SlotRuntimeRecord $B99F, (ScriptE484 - BankStart), $23, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E34A
.assert (* - BankStart) = $6353, error, "bank 1 slot record E34A end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordE353:
    SlotRuntimeRecord $FFFF, (RuntimeScriptE764 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_RUNTIME_RECORD_E353
.assert (* - BankStart) = $635C, error, "bank 1 runtime records $E353 end"
; Candidate descriptor $E34A, command $E4B0, mode $00.
SlotFlowE35C:
    SlotRuntimeRecord $C6B7, $68F2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E35C
.assert (* - BankStart) = $6365, error, "bank 1 slot record flow E35C end"
; Zero-mode record observed in longer exploratory gameplay.
; Fields after a $FFFF resource pointer may be skipped by the loader.
LongRecordE365:
    SlotRuntimeRecord $B994, (LongScriptE527 - BankStart), $13, $FF, $00, $00, $00 ; CONTROL_LONG_RECORD_E365
.assert (* - BankStart) = $636E, error, "bank 1 long-run records $E365 end"
; Candidate descriptor $E34A, command $E56C, mode $00.
SlotFlowE36E:
    SlotRuntimeRecord $C6C1, $6592, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E36E
; Candidate descriptor $E34A, command $E683, mode $00.
SlotFlowE377:
    SlotRuntimeRecord $B9A8, $65AA, $40, $FF, $00, $00, $00
; Candidate descriptor $E34A, command $E503, mode $00.
SlotFlowE380:
    SlotRuntimeRecord $B99F, $6605, $00, $FF, $00, $00, $00
; Candidate descriptor $E34A, command $E590, mode $00.
SlotFlowE389:
    SlotRuntimeRecord $B986, $6640, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $6392, error, "bank 1 slot record flow E36E end"
; Candidate descriptor $E398, command $E89D, negative mode.
CompactContextE392:
    SlotCompactRecord $B823, $23 ; CONTROL_COMPACT_CONTEXT_E392
.assert (* - BankStart) = $6395, error, "bank 1 compact candidate e392 end"
; Candidate descriptor $E398, command $E784, negative mode.
CompactContextE395:
    SlotCompactRecord $B804, $00 ; CONTROL_COMPACT_CONTEXT_E395
.assert (* - BankStart) = $6398, error, "bank 1 compact candidate e395 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE398:
    SlotRuntimeRecord $B823, (ScriptE48E - BankStart), $23, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E398
.assert (* - BankStart) = $63A1, error, "bank 1 slot record E398 end"
    .incbin "bank1_e3a1_e3a2.bin"
; Possible contact for descriptor base $E398; execution remains unverified.
ReviewedContactE3A1:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_E3A1
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $63A5, error, "bank 1 candidate contact e3a1 end"
    .incbin "bank1_e3a5_e3aa.bin"
; Candidate descriptor $E398, command $E4B0, mode $00.
SlotFlowE3AA:
    SlotRuntimeRecord $C225, $68F2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E3AA
.assert (* - BankStart) = $63B3, error, "bank 1 slot record flow E3AA end"
; Candidate native position-event record; resource payload remains local.
PositionRecordE3B3:
    SlotRuntimeRecord $B7FD, (LongScriptE527 - BankStart), $13, $FF, $00, $00, $00 ; CONTROL_POSITION_RECORD_E3B3
.assert (* - BankStart) = $63BC, error, "bank 1 position record E3B3 end"
; Candidate descriptor $E398, command $E56C, mode $00.
SlotFlowE3BC:
    SlotRuntimeRecord $C233, $6592, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E3BC
; Candidate descriptor $E398, command $E683, mode $00.
SlotFlowE3C5:
    SlotRuntimeRecord $B80B, $65AA, $40, $FF, $00, $00, $00
; Candidate descriptor $E398, command $E503, mode $00.
SlotFlowE3CE:
    SlotRuntimeRecord $B823, $6605, $00, $FF, $00, $00, $00
; Candidate descriptor $E398, command $E590, mode $00.
SlotFlowE3D7:
    SlotRuntimeRecord $B814, $6640, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $63E0, error, "bank 1 slot record flow E3BC end"
; Candidate descriptor $E3E6, command $E89D, negative mode.
CompactContextE3E0:
    SlotCompactRecord $B7EB, $23 ; CONTROL_COMPACT_CONTEXT_E3E0
.assert (* - BankStart) = $63E3, error, "bank 1 compact candidate e3e0 end"
; Candidate descriptor $E3E6, command $E784, negative mode.
CompactContextE3E3:
    SlotCompactRecord $B7CA, $00 ; CONTROL_COMPACT_CONTEXT_E3E3
.assert (* - BankStart) = $63E6, error, "bank 1 compact candidate e3e3 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE3E6:
    SlotRuntimeRecord $B7EB, (ScriptE48E - BankStart), $23, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E3E6
.assert (* - BankStart) = $63EF, error, "bank 1 slot record E3E6 end"
; Observed in zero mode; fields gated by $FFFF may be skipped.
InteractionRecordE3EF:
    SlotRuntimeRecord $FFFF, (RuntimeScriptE764 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_INTERACTION_RECORD_E3EF
.assert (* - BankStart) = $63F8, error, "bank 1 interaction record $E3EF end"
; Candidate descriptor $E3E6, command $E4B0, mode $00.
SlotFlowE3F8:
    SlotRuntimeRecord $C133, $68F2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E3F8
.assert (* - BankStart) = $6401, error, "bank 1 slot record flow E3F8 end"
; Observed in zero mode; fields gated by $FFFF may be skipped.
InteractionRecordE401:
    SlotRuntimeRecord $B7C3, (LongScriptE527 - BankStart), $13, $FF, $00, $00, $00 ; CONTROL_INTERACTION_RECORD_E401
.assert (* - BankStart) = $640A, error, "bank 1 interaction record $E401 end"
; Candidate descriptor $E3E6, command $E56C, mode $00.
SlotFlowE40A:
    SlotRuntimeRecord $C141, $6592, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E40A
; Candidate descriptor $E3E6, command $E683, mode $00.
SlotFlowE413:
    SlotRuntimeRecord $B7D1, $65AA, $40, $FF, $00, $00, $00
; Candidate descriptor $E3E6, command $E503, mode $00.
SlotFlowE41C:
    SlotRuntimeRecord $B7EB, $6605, $00, $FF, $00, $00, $00
; Candidate descriptor $E3E6, command $E590, mode $00.
SlotFlowE425:
    SlotRuntimeRecord $B7DA, $6640, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $642E, error, "bank 1 slot record flow E40A end"
; Candidate descriptor $E434, command $E89D, negative mode.
CompactContextE42E:
    SlotCompactRecord $B77E, $23 ; CONTROL_COMPACT_CONTEXT_E42E
.assert (* - BankStart) = $6431, error, "bank 1 compact candidate e42e end"
; Candidate descriptor $E434, command $E784, negative mode.
CompactContextE431:
    SlotCompactRecord $C049, $00 ; CONTROL_COMPACT_CONTEXT_E431
.assert (* - BankStart) = $6434, error, "bank 1 compact candidate e431 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeE434:
    SlotRuntimeRecord $B77E, (ScriptE47C - BankStart), $23, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_E434
.assert (* - BankStart) = $643D, error, "bank 1 slot record E434 end"
    .incbin "bank1_e43d_e43e.bin"
; Possible contact for descriptor base $E434; execution remains unverified.
ReviewedContactE43D:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_E43D
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6441, error, "bank 1 candidate contact e43d end"
    .incbin "bank1_e441_e446.bin"
; Candidate descriptor $E434, command $E4B0, mode $00.
SlotFlowE446:
    SlotRuntimeRecord $C049, $68F2, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E446
.assert (* - BankStart) = $644F, error, "bank 1 slot record flow E446 end"
; Candidate native position-event record; resource payload remains local.
PositionRecordE44F:
    SlotRuntimeRecord $B785, (LongScriptE527 - BankStart), $13, $FF, $00, $00, $00 ; CONTROL_POSITION_RECORD_E44F
.assert (* - BankStart) = $6458, error, "bank 1 position record E44F end"
; Candidate descriptor $E434, command $E56C, mode $00.
SlotFlowE458:
    SlotRuntimeRecord $C04F, $6592, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_E458
; Candidate descriptor $E434, command $E683, mode $00.
SlotFlowE461:
    SlotRuntimeRecord $B77E, $65AA, $40, $FF, $00, $00, $00
; Candidate descriptor $E434, command $E503, mode $00.
SlotFlowE46A:
    SlotRuntimeRecord $B77E, $6605, $00, $FF, $00, $00, $00
; Candidate descriptor $E434, command $E590, mode $00.
SlotFlowE473:
    SlotRuntimeRecord $B78C, $6640, $00, $FF, $00, $00, $00
.assert (* - BankStart) = $647C, error, "bank 1 slot record flow E458 end"
; Slot and movement state graph; unconverted destinations remain address aliases.
ScriptE562 = BankStart + $6562
ScriptE590 = BankStart + $6590
ScriptE63E = BankStart + $663E
ScriptE47C:
    BogusSetSlotD0Bits $01 ; CONTROL_BOGUS_E47C
    BogusSetSlotValue $0000
    BogusJumpBank1 ScriptE491
ScriptE484:
    BogusSetSlotD0Bits $04
ScriptE486:
    BogusSetSlotValue $0000
    BogusSetSlotD0Bits $02
    BogusJumpBank1 ScriptE491
ScriptE48E:
    BogusSetSlotValue $0002
ScriptE491:
    BogusSetDispatchCounter $0A
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual ScriptE4A7, $0003
    BogusSetSlotD0Bits $40
ScriptE4A7:
    BogusBranchIfSlotD0Bits ScriptE562, $20
ScriptE4AB:
    BogusClearSlot0790Bits $05
    BogusBranchIfSlot0620Bit10 ScriptE4B2
    BogusLoadRecordAndClearSavedState $12
ScriptE4B2:
    BogusBranchIfSlotD0Bits ScriptE51C, $01
    BogusSetSlot0670Pair $10, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE505, $80, $30
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE503, $40, $10
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual ScriptE4D5, $0000
    BogusBranchIfSlotCoordinatesA3 ScriptE4D5, $FF, $30
    BogusJumpBank1 ScriptE590
ScriptE4D5:
    BogusSetDispatchCounter $84
    BogusBranchIfSlotFieldsWithin ScriptE4F3, $18, $FF
    BogusBranchIfAbsSlot0700Below ScriptE4FB, $18
    BogusAdvanceAndBranchState1B ScriptE4AB, $C8
    BogusSetDispatchCounter $85
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $20, $FF
    BogusSetSlot0660LowBits $00
    BogusJumpBank1 ScriptE63E
ScriptE4F3:
    BogusSetSlotFields40Signed $18, $FF
    BogusWait $04
    BogusJumpBank1 ScriptE4AB
ScriptE4FB:
    BogusSetDirectionalSlotFields40 $D0, $FF
    BogusWait $04
    BogusJumpBank1 ScriptE4AB
ScriptE503:
    BogusLoadRecordAndClearSavedState $36
ScriptE505:
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $18, $FF
    BogusWait $04
ScriptE50C:
    BogusBranchIfSlotCoordinatesA3 ScriptE514, $14, $10
    BogusJumpBank1 ScriptE4B2
ScriptE514:
    BogusSetSlotFields80 $01, $C0
    BogusWait $08
    BogusJumpBank1 ScriptE50C
ScriptE51C:
    BogusSetSlotFields40Signed $08, $00
    BogusSetSlotFields80 $FF, $E0
    BogusWait $0A
    BogusJumpBank1 ScriptE51C
.assert (* - BankStart) = $6527, error, "bank 1 script E47C end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptE527:
    BogusSetDispatchCounter $05 ; CONTROL_LONG_SCRIPT_E527
LongScriptE529:
    BogusSetSlot0660LowBits $00
LongScriptE52B:
    BogusClearSlot0790Bits $01
LongScriptE52D:
    BogusLoadSlotValueArray $3C
LongScriptE52F:
    BogusSetSlotMode $00
LongScriptE531:
    BogusSetSlotFields80 $00, $D0
LongScriptE534:
    BogusSetDispatchCounter $0C
LongScriptE536:
    BogusReadSlotValue $13
LongScriptE538:
    BogusSetSlotMode $00
LongScriptE53A:
    BogusSetSlotMode $02
LongScriptE53C:
    BogusBranchIfSlot0700AtMost LongScriptE543, $E4
.assert (* - BankStart) = $6540, error, "bank 1 long-run script $E527 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE540:
    BogusJumpBank1 LongScriptE551 ; CONTROL_EXTENDED_SCRIPT_E540
.assert (* - BankStart) = $6543, error, "bank 1 extended script $E540 end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptE543:
    BogusBranchIfSlotOffset (BankStart + $656E), $0C, $00 ; CONTROL_LONG_SCRIPT_E543
LongScriptE548:
    BogusBranchIfSlotOffset (BankStart + $656E), $04, $00
LongScriptE54D:
    BogusBranchIfSlot0700AtMost LongScriptE55B, $1A
LongScriptE551:
    BogusBranchIfSlotOffset LongScriptE576, $F4, $00
LongScriptE556:
    BogusBranchIfSlotOffset LongScriptE576, $FC, $00
LongScriptE55B:
    BogusBranchIfSlotB0AtMost (BankStart + $6562), $18
LongScriptE55F:
    BogusClearSlot0790Bits $05
LongScriptE561:
    BogusMarkSlot05A0AndYield
.assert (* - BankStart) = $6562, error, "bank 1 long-run script $E543 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptE562:
    BogusSetDispatchCounter $83 ; CONTROL_CONTEXT_E562
    BogusClearSlotD0Bits $20
    BogusSetSlotFields40Signed $40, $00
    BogusRestartVoice4 $277A
    BogusLoadRecordAndClearSavedState $24
.assert (* - BankStart) = $656E, error, "bank 1 contextual script E562 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE56E:
    BogusSetDispatchCounter $83 ; CONTROL_EXTENDED_SCRIPT_E56E
ExtendedScriptE570:
    BogusSetSlotFields80 $20, $C0
ExtendedScriptE573:
    BogusJumpBank1 LongScriptE57B
.assert (* - BankStart) = $6576, error, "bank 1 extended script $E56E end"
; Observed at the bank-0 command fetcher during longer exploratory runs.
; Names describe handler behaviour; independent entry points are retained.
LongScriptE576:
    BogusSetDispatchCounter $82 ; CONTROL_LONG_SCRIPT_E576
LongScriptE578:
    BogusSetSlotFields80 $E0, $C0
LongScriptE57B:
    BogusSetDispatchCounter $03
LongScriptE57D:
    BogusLoadSlotValueArray $3C
LongScriptE57F:
    BogusSetSlotMode $00
LongScriptE581:
    BogusWait $04
LongScriptE583:
    BogusSetDispatchCounter $84
LongScriptE585:
    BogusReadSlotValue $13
LongScriptE587:
    BogusSetSlotMode $00
LongScriptE589:
    BogusSetSlotMode $02
LongScriptE58B:
    BogusSetSlotFields80 $00, $FF
LongScriptE58E:
    BogusWait $04
.assert (* - BankStart) = $6590, error, "bank 1 long-run script $E576 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptE590:
    BogusLoadRecordAndClearSavedState $3F ; CONTROL_CONTEXT_E590
ContextScriptE592:
    BogusSetDispatchCounter $04
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusBranchIfSlotB0AtMost ContextScriptE5A8, $40
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
ContextScriptE5A8:
    BogusLoadRecordAndClearSavedState $12
ContextScriptE5AA:
    BogusSetDispatchCounter $89
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $01, $00
    BogusBranchIfSlotD0Bits ContextScriptE5F2, $02
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual ContextScriptE5EC, $0003
    BogusReadSlotValue $02
    BogusBranchIfSlotValueNotEqual ContextScriptE5E6, $002C
    BogusAdvanceAndBranchState1B ContextScriptE5DE, $80
    BogusAdvanceAndBranchState1B ContextScriptE5D6, $80
    BogusCreateLinkedSlot $10, $10, $10, $2C
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
ContextScriptE5D6:
    BogusCreateLinkedSlot $5E, $10, $10, $2C
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
ContextScriptE5DE:
    BogusCreateLinkedSlot $5A, $10, $10, $2C
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
ContextScriptE5E6:
    BogusSetSlotValue $005B
    BogusJumpBank1 ContextScriptE5F5
ContextScriptE5EC:
    BogusSetSlotValue $0021
    BogusJumpBank1 ContextScriptE5F5
ContextScriptE5F2:
    BogusSetSlotValue $003A
ContextScriptE5F5:
    BogusSetSlot0790Bits $01
    BogusCreateLinkedSlot $00, $10, $10, $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusBranchIfSlotD0Bits ContextScriptE603, $04
    BogusWait $0A
ContextScriptE603:
    BogusLoadRecordAndClearSavedState $3F
ContextScriptE605:
    BogusLoadSlotValueArray $FF
    BogusStartVoice4FromIndexedPair $26D0
    BogusSetSlot0670Pair $01, $00
ContextScriptE60D:
    BogusBranchIfAbsSlot0700Below ContextScriptE619, $30
    BogusSetSlot0660LowBits $02
    BogusSetSlotFields80 $40, $FF
    BogusJumpBank1 ContextScriptE622
ContextScriptE619:
    BogusSetSlotFields40Signed $40, $FF
    BogusAdvanceAndBranchState1B ContextScriptE622, $C8
    BogusLoadRecordAndClearSavedState $24
ContextScriptE622:
    BogusBranchIfOffsetProbe ContextScriptE63B, $05
    BogusBranchIfDirectionalOffsetClear ContextScriptE63E, $10
    BogusBranchIfSlotCoordinates01 ContextScriptE63E, $20, $10
    BogusBranchIfSlotCoordinatesA3 ContextScriptE636, $40, $10
    BogusLoadRecordAndClearSavedState $00
ContextScriptE636:
    BogusBranchIfSlot0620Bit10 ContextScriptE60D
    BogusLoadRecordAndClearSavedState $12
ContextScriptE63B:
    BogusSetSlotFields80 $00, $FF
ContextScriptE63E:
    BogusLoadRecordAndClearSavedState $24
ContextScriptE640:
    BogusClearSlot0790Bits $01
    BogusBranchIfSlot0620Bit10 ContextScriptE647
    BogusLoadRecordAndClearSavedState $12
ContextScriptE647:
    BogusBranchIfSlotD0Bits ContextScriptE647, $01
    BogusAdvanceAndBranchState1B ContextScriptE669, $80
    BogusLoadSlotValueArray $FF
    BogusStartVoice4FromIndexedPair $26D0
    BogusSetSlot0670Pair $10, $00
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual ContextScriptE669, $0000
    BogusBranchIfSlotCoordinatesA3 ContextScriptE669, $01, $FF
    BogusSetSlotMode $FF
    BogusWait $01
    BogusLoadRecordAndClearSavedState $12
ContextScriptE669:
    BogusWait $14
    BogusSetSlot0670Pair $01, $00
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual ContextScriptE685, $0000
    BogusBranchIfSlotCoordinatesA3 ContextScriptE687, $30, $28
    BogusBranchIfSlotCoordinatesA3 ContextScriptE685, $FF, $10
    BogusAdvanceAndBranchState1B ContextScriptE647, $80
    BogusLoadRecordAndClearSavedState $2D
ContextScriptE685:
    BogusLoadRecordAndClearSavedState $00
ContextScriptE687:
    BogusBranchIfSlotB0AtMost ContextScriptE68F, $40
    BogusBranchIfOffsetProbe ContextScriptE63E, $05
ContextScriptE68F:
    BogusLoadRecordAndClearSavedState $36
.assert (* - BankStart) = $6691, error, "bank 1 contextual script E590 end"
; Movement and indexed-audio state sequence.
ScriptE691:
    BogusSetDispatchCounter $06 ; CONTROL_BOGUS_E691
    BogusSetSlotValue $8001
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
    BogusLoadSlotRecord $06, $FF
ScriptE6A4:
    BogusClearSlot0790Bits $01
    BogusAdvanceAndBranchState1B ScriptE6C2, $D4
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $12, $01
    BogusLoadSlotValueArray $FF
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $26E4
    BogusWait $0A
    BogusLoadSlotRecord $06, $FF
ScriptE6C2:
    BogusSetSlot0670Pair $28, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE6CD, $E0, $28
    BogusJumpBank1 ScriptE6DC
ScriptE6CD:
    BogusBranchIfSlotCoordinatesA3 ScriptE6DA, $20, $10
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $18, $FF
    BogusJumpBank1 ScriptE745
ScriptE6DA:
    BogusLoadRecordAndClearSavedState $1B
ScriptE6DC:
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptE6E7, $60, $10
    BogusJumpBank1 ScriptE705
ScriptE6E7:
    BogusSetSlotFields40Signed $40, $00
    BogusSetSlot0360 $12
ScriptE6EC:
    BogusBranchIfSlotCoordinates01 ScriptE703, $38, $20
    BogusBranchIfSlot0360Above ScriptE6EC, $00
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetSlotFields40Signed $01, $00
    BogusLoadSlotRecord $06, $FF
    BogusJumpBank1 ScriptE6A4
ScriptE703:
    BogusLoadRecordAndClearSavedState $24
ScriptE705:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusBranchIfAbsSlot0700Below ScriptE714, $20
    BogusJumpBank1 ScriptE717
ScriptE714:
    BogusSetSlotFields40Signed $02, $FF
ScriptE717:
    BogusReadSlotValue $05
    BogusMaskSlotValue $0007
    BogusJumpViaSlotIndexedTable
.assert (* - BankStart) = $671D, error, "bank 1 script E691 end"
; The preceding $0007 mask bounds this path to eight entries; repeated
; targets are retained exactly. Other callers are not yet inventoried.
    BogusIndexedTargetBank1 ScriptE72D ; CONTROL_BOGUS_E71D
    BogusIndexedTargetBank1 ScriptE737
    BogusIndexedTargetBank1 ScriptE72F
    BogusIndexedTargetBank1 ScriptE73D
    BogusIndexedTargetBank1 ScriptE73D
    BogusIndexedTargetBank1 ScriptE73D
    BogusIndexedTargetBank1 ScriptE73D
    BogusIndexedTargetBank1 ScriptE73D
ScriptE72D:
    BogusLoadRecordAndClearSavedState $24
ScriptE72F:
    BogusLoadSlotRecord $2D, $01
ScriptE732:
    BogusWait $0A
    BogusJumpBank1 ScriptE6A4
ScriptE737:
    BogusLoadSlotRecord $12, $01
    BogusJumpBank1 ScriptE732
ScriptE73D:
    BogusLoadSlotRecord $1B, $01
    BogusWait $04
    BogusJumpBank1 ScriptE6A4
ScriptE745:
    BogusLoadSlotRecord $06, $FF
    BogusWait $04
    BogusJumpBank1 ScriptE6A4
.assert (* - BankStart) = $674D, error, "bank 1 indexed script table E71D end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptE74D:
    BogusSetSlot0660LowBits $01 ; CONTROL_CONTEXT_E74D
    BogusSetSlotFields80 $01, $FF
    BogusBranchIfSlotCoordinatesA3 ContextScriptE74D, $20, $10
    BogusLoadSlotRecord $06, $FF
    BogusJumpBank1 (BankStart + $66A4)
ContextScriptE75D:
    BogusSetDirectionalSlotFields40 $10, $A0
    BogusWait $09
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6764, error, "bank 1 contextual script E74D end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptE764:
    BogusSetDispatchCounter $07 ; CONTROL_RUNTIME_SCRIPT_E764
RuntimeScriptE766:
    BogusBranchIfSelectedFieldEqual (BankStart + $686F), $12
RuntimeScriptE76A:
    BogusBranchIfSlot06D0Present (BankStart + $67F0)
RuntimeScriptE76D:
    BogusBranchIfSelectedFieldEqual (BankStart + $677C), $10
RuntimeScriptE771:
    BogusBranchIfSelectedFieldEqual RuntimeScriptE905, $1D
.assert (* - BankStart) = $6775, error, "bank 1 runtime script $E764 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE775:
    BogusRestoreSavedScriptAndSlotFlags
SuccessorScriptE776:
    BogusSetSlotD0Bits $20 ; CONTROL_SUCCESSOR_SCRIPT_E775
SuccessorScriptE778:
    BogusSetSlot07F0 $44
SuccessorScriptE77A:
    BogusLoadRecordAndClearSavedState $00
SuccessorScriptE77C:
    BogusBranchIfSlotD0Bits SuccessorScriptE776, $40
SuccessorScriptE780:
    BogusSetDispatchCounter $06
SuccessorScriptE782:
    BogusSetSlot0790Bits $FF
SuccessorScriptE784:
    BogusLoadSlotRecord $03, $FF
SuccessorScriptE787:
    BogusFollowLinkedSlotsAndYield $FF, $FF, $23, $00, $00
.assert (* - BankStart) = $678D, error, "bank 1 candidate successor $E775 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE78D:
    BogusSetSlot05E0Bit40 $01 ; CONTROL_EXTENDED_SCRIPT_E78D
.assert (* - BankStart) = $678F, error, "bank 1 extended script $E78D end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE78F:
    BogusStartVoice4 $2826 ; CONTROL_SWEEP_SCRIPT_E78F
SweepScriptE792:
    BogusSetLinkedFieldsAndYield $FF, $FE
SweepScriptE795:
    BogusSetLinkedFieldsAndYield $FF, $FC
SweepScriptE798:
    BogusSetLinkedFieldsAndYield $FF, $F8
SweepScriptE79B:
    BogusSetLinkedFieldsAndYield $FF, $F4
SweepScriptE79E:
    BogusSetLinkedFieldsAndYield $80, $F2
SweepScriptE7A1:
    BogusSetSlot0360 $FC
SweepScriptE7A3:
    BogusReadSlotValue $02
SweepScriptE7A5:
    BogusBranchIfSlotValueEqual (BankStart + $67AF), $11, $00
SweepScriptE7AA:
    BogusBranchIfSlotValueNotEqual ExtendedScriptE7B2, $0012
.assert (* - BankStart) = $67AF, error, "bank 1 sweep script $E78F end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptE7AF:
    BogusSetLinkedFieldsAndYield $80, $E2 ; CONTROL_PATH_SCRIPT_E7AF
.assert (* - BankStart) = $67B2, error, "bank 1 candidate successor $E7AF end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE7B2:
    BogusSetSlot07F0 $14 ; CONTROL_EXTENDED_SCRIPT_E7B2
.assert (* - BankStart) = $67B4, error, "bank 1 extended script $E7B2 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE7B4:
    BogusSetSlot0630Bit04UnlessFF $01 ; CONTROL_SWEEP_SCRIPT_E7B4
.assert (* - BankStart) = $67B6, error, "bank 1 sweep script $E7B4 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE7B6:
    BogusSetSlot0660LowBits $00 ; CONTROL_SUCCESSOR_SCRIPT_E7B6
SuccessorScriptE7B8:
    BogusSetSlot0660HighBits $00
.assert (* - BankStart) = $67BA, error, "bank 1 candidate successor $E7B6 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE7BA:
    BogusClearSlot0640PairBits $04, $00 ; CONTROL_EXTENDED_SCRIPT_E7BA
.assert (* - BankStart) = $67BD, error, "bank 1 extended script $E7BA end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE7BD:
    BogusCopyLinkedMotionFields
SweepScriptE7BE:
    BogusClearSlot0790Bits $01 ; CONTROL_SWEEP_SCRIPT_E7BD
SweepScriptE7C0:
    BogusReadSlotValue $02
SweepScriptE7C2:
    BogusLookupSlotValue
.assert (* - BankStart) = $67C3, error, "bank 1 sweep script $E7BD end"
; Slot-value cases for the preceding $95 command, followed by a zero target.
    BogusLookupCaseBank1 (BankStart + $67E6), $0052 ; CONTROL_SWEEP_LOOKUP_E7C3
    BogusLookupCaseBank1 (BankStart + $67E6), $0053
    BogusLookupEnd
.assert (* - BankStart) = $67CD, error, "bank 1 sweep lookup $E7C3 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE7CD:
    BogusBranchIfSlotD0BitsClear SweepScriptE7BD, $80 ; CONTROL_SWEEP_SCRIPT_E7CD
.assert (* - BankStart) = $67D1, error, "bank 1 sweep script $E7CD end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptE7D1:
    BogusReadSlotValue $12 ; CONTROL_PATH_SCRIPT_E7D1
PathScriptE7D3:
    BogusBranchIfSlotValueAtLeast PathScriptE7DB, $0080
PathScriptE7D8:
    BogusJumpBank1 (BankStart + $67BD)
PathScriptE7DB:
    BogusSetSlot0640PairBits $04, $00
.assert (* - BankStart) = $67DE, error, "bank 1 candidate successor $E7D1 end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptE7DE:
    BogusSetSlotMode $03 ; CONTROL_EXPANDED_SCRIPT_E7DE
ExpandedScriptE7E0:
    BogusRelinkSlots
ExpandedScriptE7E1:
    BogusSetSlot05E0Bit40 $FF
ExpandedScriptE7E3:
    BogusJumpBank1 SweepScriptE84D
.assert (* - BankStart) = $67E6, error, "bank 1 candidate successor $E7DE end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptE7E6:
    BogusBranchIfSlot0360Above (BankStart + $67CD), $A0 ; CONTROL_PATH_SCRIPT_E7E6
PathScriptE7EA:
    BogusRestartVoice4 $284D
PathScriptE7ED:
    BogusJumpBank1 SuccessorScriptE835
.assert (* - BankStart) = $67F0, error, "bank 1 candidate successor $E7E6 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE7F0:
    BogusReadSlotValue $24 ; CONTROL_SUCCESSOR_SCRIPT_E7F0
SuccessorScriptE7F2:
    BogusLookupSlotValue
.assert (* - BankStart) = $67F3, error, "bank 1 candidate successor $E7F0 end"
; $95 compares each value to the slot value and branches to its target.
; The two-byte zero target terminates the inline table.
    BogusLookupCaseBank1 SuccessorScriptE80C, $000E ; CONTROL_SUCCESSOR_LOOKUP_E7F3
    BogusLookupCaseBank1 SuccessorScriptE835, $0011
    BogusLookupCaseBank1 SuccessorScriptE864, $0013
    BogusLookupCaseBank1 SuccessorScriptE8E8, $0014
    BogusLookupCaseBank1 (BankStart + $6831), $001E
    BogusLookupEnd
.assert (* - BankStart) = $6809, error, "bank 1 successor lookup $E7F3 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE809:
    BogusJumpBank1 (BankStart + $67B2) ; CONTROL_SUCCESSOR_SCRIPT_E809
SuccessorScriptE80C:
    BogusSetDispatchCounter $8B
SuccessorScriptE80E:
    BogusSetSlotValue $0001
SuccessorScriptE811:
    BogusStoreSlotValueArray $2B
SuccessorScriptE813:
    BogusLoadSlotValueArray $2A
SuccessorScriptE815:
    BogusAddSlotValue $0001
SuccessorScriptE818:
    BogusStoreSlotValueArray $2A
SuccessorScriptE81A:
    BogusSetSlot0730 $F5
SuccessorScriptE81C:
    BogusSetSlot07F0 $44
SuccessorScriptE81E:
    BogusSetSlotFields80 $50, $FF
SuccessorScriptE821:
    BogusSetSlotC0 $FF
SuccessorScriptE823:
    BogusRelinkSlots
SuccessorScriptE824:
    BogusSetUnlinkedFields $00, $FF
SuccessorScriptE827:
    BogusRestartVoice4 $26FA
SuccessorScriptE82A:
    BogusSetSlotFields80 $50, $FF
SuccessorScriptE82D:
    BogusWait $1E
SuccessorScriptE82F:
    BogusYieldAndSlotAction $01
.assert (* - BankStart) = $6831, error, "bank 1 candidate successor $E809 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE831:
    BogusRelinkToLastRelatedSlot ; CONTROL_EXTENDED_SCRIPT_E831
.assert (* - BankStart) = $6832, error, "bank 1 extended script $E831 end"
; Command entries observed during the directed-input exploration.
DirectedScriptE832:
    BogusJumpBank1 ExtendedScriptE7B2 ; CONTROL_DIRECTED_SCRIPT_E832
.assert (* - BankStart) = $6835, error, "bank 1 directed script $E832 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE835:
    BogusSetDispatchCounter $88 ; CONTROL_SUCCESSOR_SCRIPT_E835
SuccessorScriptE837:
    BogusLoadSlotRecord $03, $FF
SuccessorScriptE83A:
    BogusSetSlot05F0Pair $7F, $7F
.assert (* - BankStart) = $683D, error, "bank 1 candidate successor $E835 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE83D:
    BogusCopyLinkedMotionFields ; CONTROL_EXTENDED_SCRIPT_E83D
.assert (* - BankStart) = $683E, error, "bank 1 extended script $E83D end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE83E:
    BogusSetDirectionalSlotFields40 $38, $FF ; CONTROL_SWEEP_SCRIPT_E83E
.assert (* - BankStart) = $6841, error, "bank 1 sweep script $E83E end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE841:
    BogusSetSlotMode $03 ; CONTROL_SUCCESSOR_SCRIPT_E841
SuccessorScriptE843:
    BogusSetSlot07F0 $44
.assert (* - BankStart) = $6845, error, "bank 1 candidate successor $E841 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE845:
    BogusSetSlot0640PairBits $04, $00 ; CONTROL_EXTENDED_SCRIPT_E845
.assert (* - BankStart) = $6848, error, "bank 1 extended script $E845 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE848:
    BogusRelinkSlots
SweepScriptE849:
    BogusSetSlot05E0Bit40 $FF ; CONTROL_SWEEP_SCRIPT_E848
SweepScriptE84B:
    BogusSetSlotC0 $FF
SweepScriptE84D:
    BogusSetSlot07F0 $44
SweepScriptE84F:
    BogusBranchIfSlot0620Bit10 SweepScriptE858
SweepScriptE852:
    BogusBranchIfSlotB0AtMost SweepScriptE84F, $E6
.assert (* - BankStart) = $6856, error, "bank 1 sweep script $E848 end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptE856:
    BogusYieldAndSlotAction $00 ; CONTROL_PATH_SCRIPT_E856
.assert (* - BankStart) = $6858, error, "bank 1 candidate successor $E856 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptE858:
    BogusStartVoice4 $2724 ; CONTROL_SWEEP_SCRIPT_E858
SweepScriptE85B:
    BogusClearSlot0790Bits $01
SweepScriptE85D:
    BogusWait $0A
SweepScriptE85F:
    BogusSetUnlinkedFields $00, $00
SweepScriptE862:
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6864, error, "bank 1 sweep script $E858 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE864:
    BogusSetDispatchCounter $88 ; CONTROL_SUCCESSOR_SCRIPT_E864
SuccessorScriptE866:
    BogusLoadSlotRecord $03, $FF
SuccessorScriptE869:
    BogusSetSlotFields80 $00, $E0
SuccessorScriptE86C:
    BogusJumpBank1 SuccessorScriptE841
SuccessorScriptE86F:
    BogusSetDispatchCounter $0E
SuccessorScriptE871:
    BogusRelinkSlots
.assert (* - BankStart) = $6872, error, "bank 1 candidate successor $E864 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE872:
    BogusSetSlot05E0Bit40 $FF ; CONTROL_EXTENDED_SCRIPT_E872
.assert (* - BankStart) = $6874, error, "bank 1 extended script $E872 end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptE874:
    BogusSetDispatchCounter $8F ; CONTROL_EXPANDED_SCRIPT_E874
ExpandedScriptE876:
    BogusSetSlot07F0 $44
ExpandedScriptE878:
    BogusReadSlotValue $13
ExpandedScriptE87A:
    BogusSetSlotMode $00
ExpandedScriptE87C:
    BogusSetSlotMode $02
ExpandedScriptE87E:
    BogusSetSlotC0 $FF
ExpandedScriptE880:
    BogusSetSlot0790Bits $FF
ExpandedScriptE882:
    BogusSetUnlinkedFields $00, $00
ExpandedScriptE885:
    BogusSetSlot05F0Pair $60, $60
ExpandedScriptE888:
    BogusReadSlotValue $0F
ExpandedScriptE88A:
    BogusBranchIfSlotValueEqual ExpandedScriptE8B0, $13, $00
ExpandedScriptE88F:
    BogusSetVoicePointers $278C, $2795, $0000, $0000
ExpandedScriptE898:
    BogusSetSlotPositionFromOperands $60, $A7
ExpandedScriptE89B:
    BogusSetSlot0660LowBits $00
ExpandedScriptE89D:
    BogusLoadSlotRecord $06, $FF
ExpandedScriptE8A0:
    BogusSetSlotFields80 $01, $00
ExpandedScriptE8A3:
    BogusWait $09
ExpandedScriptE8A5:
    BogusSetSlotFields80 $40, $00
ExpandedScriptE8A8:
    BogusWait $0C
ExpandedScriptE8AA:
    BogusSetSpriteAttribute20 $20
ExpandedScriptE8AC:
    BogusWait $06
ExpandedScriptE8AE:
    BogusYieldAndSlotAction $01
ExpandedScriptE8B0:
    BogusSetDispatchCounter $05
ExpandedScriptE8B2:
    BogusSetSlotC0 $04
ExpandedScriptE8B4:
    BogusSetSlotFields80 $60, $00
ExpandedScriptE8B7:
    BogusSetVoicePointers $278C, $2795, $0000, $0000
ExpandedScriptE8C0:
    BogusBranchIfSlot0700AtMost ExpandedScriptE8C0, $80
ExpandedScriptE8C4:
    BogusSetSlotFields80 $00, $00
ExpandedScriptE8C7:
    BogusSetVoicePointers $0000, $0000, $0000, $0000
ExpandedScriptE8D0:
    BogusRestartVoice4 $27A0
ExpandedScriptE8D3:
    BogusWait $07
ExpandedScriptE8D5:
    BogusMarkMatchingSlots $00, $01, $1E, $00
ExpandedScriptE8DA:
    BogusWait $09
ExpandedScriptE8DC:
    BogusSetSlotFields80 $78, $00
ExpandedScriptE8DF:
    BogusBranchIfAbsSlot0700Below ExpandedScriptE8E6, $20
ExpandedScriptE8E3:
    BogusJumpBank1 ExpandedScriptE8DF
ExpandedScriptE8E6:
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $68E8, error, "bank 1 candidate successor $E874 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE8E8:
    BogusReadSlotValue $02 ; CONTROL_SUCCESSOR_SCRIPT_E8E8
SuccessorScriptE8EA:
    BogusSwapSlotValueBytes
SuccessorScriptE8EB:
    BogusLoadSlotLowFromByteArray $2A
SuccessorScriptE8ED:
    BogusSwapSlotValueBytes
.assert (* - BankStart) = $68EE, error, "bank 1 candidate successor $E8E8 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptE8EE:
    BogusStoreSlotLowAtIndexedPage ; CONTROL_EXTENDED_SCRIPT_E8EE
.assert (* - BankStart) = $68EF, error, "bank 1 extended script $E8EE end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptE8EF:
    BogusJumpBank1 ExtendedScriptE7B2 ; CONTROL_EXPANDED_SCRIPT_E8EF
.assert (* - BankStart) = $68F2, error, "bank 1 candidate successor $E8EF end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptE8F2:
    BogusSetDispatchCounter $04 ; CONTROL_CONTEXT_E8F2
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
ContextScriptE8FA:
    BogusBranchIfSlot0620Bit10 ContextScriptE903
    BogusBranchIfSlotB0AtMost ContextScriptE8FA, $E6
    BogusYieldAndSlotAction $00
ContextScriptE903:
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6905, error, "bank 1 contextual script E8F2 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptE905:
    BogusLoadSlotRecord $03, $FF ; CONTROL_RUNTIME_SCRIPT_E905
RuntimeScriptE908:
    BogusClearSlotD0Bits $40
RuntimeScriptE90A:
    BogusSetLinkedSlotFieldsC0 $20, $A0
RuntimeScriptE90D:
    BogusSetSlotMode $03
RuntimeScriptE90F:
    BogusSetUnlinkedFields $20, $00
RuntimeScriptE912:
    BogusSetSlot07F0 $0A
RuntimeScriptE914:
    BogusClearSlot0790Bits $01
RuntimeScriptE916:
    BogusWait $14
RuntimeScriptE918:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE91D:
    BogusWait $06
RuntimeScriptE91F:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE924:
    BogusWait $06
RuntimeScriptE926:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE92B:
    BogusWait $28
RuntimeScriptE92D:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE932:
    BogusWait $06
RuntimeScriptE934:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE939:
    BogusWait $06
RuntimeScriptE93B:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE940:
    BogusWait $28
RuntimeScriptE942:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE947:
    BogusWait $06
RuntimeScriptE949:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE94E:
    BogusWait $06
RuntimeScriptE950:
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
RuntimeScriptE955:
    BogusAdjustSlotBounds $FF, $00
RuntimeScriptE958:
    BogusWait $01
RuntimeScriptE95A:
    BogusAdjustSlotBounds $02, $00
RuntimeScriptE95D:
    BogusWait $01
RuntimeScriptE95F:
    BogusAdjustSlotBounds $FE, $00
RuntimeScriptE962:
    BogusWait $01
RuntimeScriptE964:
    BogusAdjustSlotBounds $02, $00
RuntimeScriptE967:
    BogusWait $01
RuntimeScriptE969:
    BogusAdjustSlotBounds $FE, $00
RuntimeScriptE96C:
    BogusLoadSlotValueArray $FF
RuntimeScriptE96E:
    BogusBranchIfSlotValueAtLeast (BankStart + $6979), $8000
RuntimeScriptE973:
    BogusStartVoice4FromIndexedPair $26D0
RuntimeScriptE976:
    BogusJumpBank1 RuntimeScriptE97F
.assert (* - BankStart) = $6979, error, "bank 1 runtime script $E905 end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE979:
    BogusMaskSlotValue $7FFF ; CONTROL_SUCCESSOR_SCRIPT_E979
SuccessorScriptE97C:
    BogusSetVoicesFromIndexedRecord $26E4
.assert (* - BankStart) = $697F, error, "bank 1 candidate successor $E979 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptE97F:
    BogusAdjustSlotBounds $02, $00 ; CONTROL_RUNTIME_SCRIPT_E97F
RuntimeScriptE982:
    BogusWait $01
RuntimeScriptE984:
    BogusAdjustSlotBounds $FE, $00
RuntimeScriptE987:
    BogusWait $01
RuntimeScriptE989:
    BogusAdjustSlotBounds $02, $00
RuntimeScriptE98C:
    BogusWait $01
RuntimeScriptE98E:
    BogusAdjustSlotBounds $FE, $00
RuntimeScriptE991:
    BogusWait $01
RuntimeScriptE993:
    BogusAdjustSlotBounds $02, $00
RuntimeScriptE996:
    BogusWait $01
RuntimeScriptE998:
    BogusAdjustSlotBounds $FE, $00
RuntimeScriptE99B:
    BogusWait $01
.assert (* - BankStart) = $699D, error, "bank 1 runtime script $E97F end"
; Candidate successors of opening-observed scripts, from reviewed handler rules.
; Independent labels preserve alternate entries; reachability remains unproven.
SuccessorScriptE99D:
    BogusAdjustSlotBounds $02, $00 ; CONTROL_SUCCESSOR_SCRIPT_E99D
SuccessorScriptE9A0:
    BogusWait $01
SuccessorScriptE9A2:
    BogusAdjustSlotBounds $FE, $00
SuccessorScriptE9A5:
    BogusWait $01
SuccessorScriptE9A7:
    BogusAdjustSlotBounds $02, $00
SuccessorScriptE9AA:
    BogusWait $01
SuccessorScriptE9AC:
    BogusAdjustSlotBounds $FE, $00
SuccessorScriptE9AF:
    BogusWait $01
SuccessorScriptE9B1:
    BogusAdjustSlotBounds $01, $00
SuccessorScriptE9B4:
    BogusWait $14
SuccessorScriptE9B6:
    BogusSetSlot07F0 $44
SuccessorScriptE9B8:
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $69BA, error, "bank 1 candidate successor $E99D end"
; Linked slot and movement state graph; gameplay role remains unverified.
ScriptB98E = BankStart + $398E
ScriptE9BA:
    BogusSetSlotD0Bits $01 ; CONTROL_BOGUS_E9BA
ScriptE9BC:
    BogusSetSlotD0Bits $80
    BogusSetSlotValue $8000
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
ScriptE9CC:
    BogusClearSlot0790Bits $01
    BogusReadSlotLowFrom $0381
    BogusBranchIfSlotValueNotEqual ScriptE9F4, $0000
    BogusAdvanceAndBranchState1B ScriptEA0E, $D4
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $1B, $01
    BogusWait $07
    BogusLoadSlotValueArray $FF
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $26E4
    BogusWait $0A
    BogusLoadSlotRecord $00, $01
ScriptE9F4:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $28, $FF
    BogusLoadSlotRecord $00, $01
    BogusBranchIfAbsSlot0700Below ScriptB98E, $11
    BogusReadSlotLowFrom $0381
    BogusBranchIfSlotValueNotEqual ScriptE9F4, $0000
    BogusJumpBank1 ScriptE9CC
ScriptEA0E:
    BogusSetSlot0670Pair $08, $00
    BogusBranchIfSlotCoordinatesA3 ScriptEA19, $E0, $28
    BogusJumpBank1 ScriptEA28
ScriptEA19:
    BogusBranchIfSlotCoordinatesA3 ScriptEA26, $1E, $10
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $18, $FF
    BogusJumpBank1 ScriptEA9A
ScriptEA26:
    BogusLoadRecordAndClearSavedState $1B
ScriptEA28:
    BogusSetDispatchCounter $05
    BogusBranchIfSlotD0BitsClear ScriptEA49, $01
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinates01 ScriptEA39, $60, $10
    BogusJumpBank1 ScriptEA49
ScriptEA39:
    BogusBranchIfSlotCoordinates01 ScriptEA40, $20, $FF
    BogusLoadRecordAndClearSavedState $24
ScriptEA40:
    BogusLoadSlotRecord $00, $02
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusJumpBank1 ScriptEA66
ScriptEA49:
    BogusSetSlot0660LowBits $00
    BogusBranchIfSlotD0BitsClear ScriptEA73, $01
    BogusAdvanceAndBranchState1B ScriptEA73, $80
    BogusSetDispatchCounter $85
    BogusLoadSlotRecord $00, $02
    BogusBranchIfAbsSlot0700Below ScriptEA6B, $20
    BogusSetSlotFields80 $F0, $FF
    BogusAdvanceAndBranchState1B ScriptEA66, $80
    BogusSetSlotFields80 $10, $FF
ScriptEA66:
    BogusWait $0C
    BogusJumpBank1 ScriptEA9D
ScriptEA6B:
    BogusSetSlotFields40Signed $18, $00
    BogusWait $14
    BogusJumpBank1 ScriptEA9D
ScriptEA73:
    BogusBranchIfSlotFieldsWithin ScriptEA84, $07, $FF
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusBranchIfAbsSlot0700Below ScriptEA94, $20
ScriptEA84:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $1B, $01
    BogusWait $04
    BogusJumpBank1 ScriptE9CC
ScriptEA94:
    BogusSetSlotFields40Signed $02, $FF
    BogusJumpBank1 ScriptEA84
ScriptEA9A:
    BogusLoadSlotRecord $00, $02
ScriptEA9D:
    BogusWait $04
    BogusJumpBank1 ScriptE9CC
.assert (* - BankStart) = $6AA2, error, "bank 1 script E9BA end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptEAA2:
    BogusSetSlot0660LowBits $01 ; CONTROL_CONTEXT_EAA2
    BogusSetSlotFields80 $01, $FF
    BogusBranchIfSlotCoordinatesA3 ContextScriptEAB7, $14, $FF
    BogusBranchIfSlotCoordinatesA3 ContextScriptEAA2, $1E, $10
    BogusLoadSlotRecord $00, $02
    BogusJumpBank1 (BankStart + $69CC)
ContextScriptEAB7:
    BogusLoadSlotRecord $00, $02
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ContextScriptEACC, $0080
ContextScriptEAC1:
    BogusAdjustSlotBounds $FF, $00
    BogusBranchIfSlotCoordinatesA3 ContextScriptEAC1, $14, $FF
    BogusJumpBank1 ContextScriptEAD4
ContextScriptEACC:
    BogusAdjustSlotBounds $01, $00
    BogusBranchIfSlotCoordinatesA3 ContextScriptEACC, $14, $FF
ContextScriptEAD4:
    BogusLoadSlotRecord $1B, $02
    BogusJumpBank1 ContextScriptEAA2
ContextScriptEADA:
    BogusSetDirectionalSlotFields40 $40, $FF
    BogusWait $08
    BogusSetSlotFields80 $00, $00
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6AE4, error, "bank 1 contextual script EAA2 end"
; Candidate descriptor $EAED, command $EC74, mode $FF.
SlotFlowEAE4:
    SlotCompactRecord $B608, $22 ; CONTROL_SLOT_FLOW_EAE4
.assert (* - BankStart) = $6AE7, error, "bank 1 slot record flow EAE4 end"
; Candidate descriptor $EAED, command $E89D, negative mode.
CompactContextEAE7:
    SlotCompactRecord $B608, $22 ; CONTROL_COMPACT_CONTEXT_EAE7
.assert (* - BankStart) = $6AEA, error, "bank 1 compact candidate eae7 end"
; Candidate descriptor $EAED, command $E784, negative mode.
CompactContextEAEA:
    SlotCompactRecord $BAE1, $00 ; CONTROL_COMPACT_CONTEXT_EAEA
.assert (* - BankStart) = $6AED, error, "bank 1 compact candidate eaea end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEAED:
    SlotRuntimeRecord $B608, (ScriptEC03 - BankStart), $22, $00, $16, $61, $12 ; CONTROL_SLOT_RUNTIME_EAED
.assert (* - BankStart) = $6AF6, error, "bank 1 slot record EAED end"
    .incbin "bank1_eaf6_eaf7.bin"
; Possible contact for descriptor base $EAED; execution remains unverified.
ReviewedContactEAF6:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EAF6
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6AFA, error, "bank 1 candidate contact eaf6 end"
    .incbin "bank1_eafa_eaff.bin"
; Candidate descriptor $EAED, script $ECE2, mode $02.
ModeRecordEAFFResource:
    .word $BAE9 ; CONTROL_MODE_RECORD_EAFF_RESOURCE
.assert (* - BankStart) = $6B01, error, "bank 1 candidate mode record eaff resource end"
    .incbin "bank1_eb01_eb03.bin"
; Candidate descriptor $EAED, script $ECE2, mode $02.
ModeRecordEAFFFields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_EAFF_FIELDS
.assert (* - BankStart) = $6B08, error, "bank 1 candidate mode record eaff fields end"
    .incbin "bank1_eb08_eb0a.bin"
; Candidate descriptor $EB13, command $EC74, mode $FF.
SlotFlowEB0A:
    SlotCompactRecord $B608, $22 ; CONTROL_SLOT_FLOW_EB0A
.assert (* - BankStart) = $6B0D, error, "bank 1 slot record flow EB0A end"
    .incbin "bank1_eb0d_eb13.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEB13:
    SlotRuntimeRecord $B608, (ScriptEC03 - BankStart), $22, $00, $16, $61, $22 ; CONTROL_SLOT_RUNTIME_EB13
.assert (* - BankStart) = $6B1C, error, "bank 1 slot record EB13 end"
    .incbin "bank1_eb1c_eb1d.bin"
; Possible contact for descriptor base $EB13; execution remains unverified.
ReviewedContactEB1C:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EB1C
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6B20, error, "bank 1 candidate contact eb1c end"
    .incbin "bank1_eb20_eb25.bin"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialEB25Resource:
    .word $B5F0 ; CONTROL_SWEEP_RESOURCE_EB25
.assert (* - BankStart) = $6B27, error, "bank 1 sweep record field $EB25 end"
    .incbin "bank1_eb27_eb29.bin"
; Observed mode-specific record fields; unread neighbouring bytes stay local.
SweepPartialEB25Fields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_FIELDS_EB25
.assert (* - BankStart) = $6B2E, error, "bank 1 sweep record field $EB29 end"
; Candidate descriptor $EB37, command $EC74, mode $FF.
SlotFlowEB2E:
    SlotCompactRecord $C537, $22 ; CONTROL_SLOT_FLOW_EB2E
.assert (* - BankStart) = $6B31, error, "bank 1 slot record flow EB2E end"
    .incbin "bank1_eb31_eb37.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEB37:
    SlotRuntimeRecord $B909, (CandidateEB52 - BankStart), $22, $00, $20, $41, $12 ; CONTROL_SLOT_RUNTIME_EB37
.assert (* - BankStart) = $6B40, error, "bank 1 slot record EB37 end"
    .incbin "bank1_eb40_eb49.bin"
; Candidate descriptor $EB37, script $ECE2, mode $02.
ModeRecordEB49Resource:
    .word $B8F7 ; CONTROL_MODE_RECORD_EB49_RESOURCE
.assert (* - BankStart) = $6B4B, error, "bank 1 candidate mode record eb49 resource end"
    .incbin "bank1_eb4b_eb4d.bin"
; Candidate descriptor $EB37, script $ECE2, mode $02.
ModeRecordEB49Fields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_EB49_FIELDS
.assert (* - BankStart) = $6B52, error, "bank 1 candidate mode record eb49 fields end"
; Candidate script path; object role and execution remain unverified.
CandidateEB52:
    BogusSetSlotValue $0000 ; CONTROL_BOGUS_EB52
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $42
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0640Pair $04, $00
    BogusBranchIfSlot0780Equal CandidateEB66, $AA
    BogusJumpBank1 (BankStart + $6C33)
CandidateEB66:
    BogusSetSlotD0Bits $08
    BogusJumpBank1 (BankStart + $6C33)
.assert (* - BankStart) = $6B6B, error, "bank 1 candidate script EB52 end"
; Candidate descriptor $EB74, command $EC74, mode $FF.
SlotFlowEB6B:
    SlotCompactRecord $B848, $22 ; CONTROL_SLOT_FLOW_EB6B
.assert (* - BankStart) = $6B6E, error, "bank 1 slot record flow EB6B end"
; Candidate descriptor $EB74, command $E89D, negative mode.
CompactContextEB6E:
    SlotCompactRecord $B848, $22 ; CONTROL_COMPACT_CONTEXT_EB6E
.assert (* - BankStart) = $6B71, error, "bank 1 compact candidate eb6e end"
; Candidate descriptor $EB74, command $E784, negative mode.
CompactContextEB71:
    SlotCompactRecord $B851, $00 ; CONTROL_COMPACT_CONTEXT_EB71
.assert (* - BankStart) = $6B74, error, "bank 1 compact candidate eb71 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEB74:
    SlotRuntimeRecord $B848, (ScriptEBFD - BankStart), $22, $00, $16, $61, $22 ; CONTROL_SLOT_RUNTIME_EB74
.assert (* - BankStart) = $6B7D, error, "bank 1 slot record EB74 end"
    .incbin "bank1_eb7d_eb7e.bin"
; Possible contact for descriptor base $EB74; execution remains unverified.
ReviewedContactEB7D:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EB7D
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6B81, error, "bank 1 candidate contact eb7d end"
    .incbin "bank1_eb81_eb86.bin"
; Candidate descriptor $EB74, script $ECE2, mode $02.
ModeRecordEB86Resource:
    .word $B858 ; CONTROL_MODE_RECORD_EB86_RESOURCE
.assert (* - BankStart) = $6B88, error, "bank 1 candidate mode record eb86 resource end"
    .incbin "bank1_eb88_eb8a.bin"
; Candidate descriptor $EB74, script $ECE2, mode $02.
ModeRecordEB86Fields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_MODE_RECORD_EB86_FIELDS
.assert (* - BankStart) = $6B8F, error, "bank 1 candidate mode record eb86 fields end"
    .incbin "bank1_eb8f_eb91.bin"
; Candidate descriptor $EB9A, command $EC74, mode $FF.
SlotFlowEB91:
    SlotCompactRecord $B91E, $22 ; CONTROL_SLOT_FLOW_EB91
.assert (* - BankStart) = $6B94, error, "bank 1 slot record flow EB91 end"
; Candidate descriptor $EB9A, command $E89D, negative mode.
CompactContextEB94:
    SlotCompactRecord $B91E, $22 ; CONTROL_COMPACT_CONTEXT_EB94
.assert (* - BankStart) = $6B97, error, "bank 1 compact candidate eb94 end"
; Compact record observed in negative loader mode.
SweepRecordEB97:
    SlotCompactRecord $C577, $00 ; CONTROL_SWEEP_RECORD_EB97
.assert (* - BankStart) = $6B9A, error, "bank 1 sweep record $EB97 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEB9A:
    SlotRuntimeRecord $B91E, (CandidateEBB5 - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EB9A
.assert (* - BankStart) = $6BA3, error, "bank 1 slot record EB9A end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordEBA3:
    SlotRuntimeRecord $FFFF, (RuntimeScriptE764 - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_EBA3
.assert (* - BankStart) = $6BAC, error, "bank 1 sweep record $EBA3 end"
; Resource pointer read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordEBACResource:
    .word $B910 ; CONTROL_PARTIAL_RESOURCE_EBAC
.assert (* - BankStart) = $6BAE, error, "bank 1 partial record $EBAC end"
    .incbin "bank1_ebae_ebb0.bin"
; Mode-specific flags and fields read by the slot-record loader. Unread neighbouring bytes remain local.
PartialRecordEBACFields:
    .byte $00, $FF, $00, $00, $00 ; CONTROL_PARTIAL_FIELDS_EBAC
.assert (* - BankStart) = $6BB5, error, "bank 1 partial record $EBB0 end"
; Candidate script path; object role and execution remain unverified.
CandidateEBB5:
    BogusSetSlot0670Pair $08, $00 ; CONTROL_BOGUS_EBB5
    BogusSetSlotValue $0008
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $02
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0640Pair $04, $08
    BogusClearSlot0790Bits $01
    BogusJumpBank1 (BankStart + $6C33)
.assert (* - BankStart) = $6BCA, error, "bank 1 candidate script EBB5 end"
; Candidate descriptor $EBD3, command $EC74, mode $FF.
SlotFlowEBCA:
    SlotCompactRecord $C743, $00 ; CONTROL_SLOT_FLOW_EBCA
.assert (* - BankStart) = $6BCD, error, "bank 1 slot record flow EBCA end"
; Candidate descriptor $EBD3, command $E89D, negative mode.
CompactContextEBCD:
    SlotCompactRecord $B9D8, $27 ; CONTROL_COMPACT_CONTEXT_EBCD
.assert (* - BankStart) = $6BD0, error, "bank 1 compact candidate ebcd end"
; Candidate descriptor $EBD3, command $E784, negative mode.
CompactContextEBD0:
    SlotCompactRecord $C74D, $00 ; CONTROL_COMPACT_CONTEXT_EBD0
.assert (* - BankStart) = $6BD3, error, "bank 1 compact candidate ebd0 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEBD3:
    SlotRuntimeRecord $C72F, (ScriptEBEE - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EBD3
.assert (* - BankStart) = $6BDC, error, "bank 1 slot record EBD3 end"
    .incbin "bank1_ebdc_ebdd.bin"
; Possible contact for descriptor base $EBD3; execution remains unverified.
ReviewedContactEBDC:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EBDC
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6BE0, error, "bank 1 candidate contact ebdc end"
    .incbin "bank1_ebe0_ebe5.bin"
; Candidate descriptor $EBD3, script $ECE2, mode $02.
ModeRecordEBE5Resource:
    .word $B9CA ; CONTROL_MODE_RECORD_EBE5_RESOURCE
.assert (* - BankStart) = $6BE7, error, "bank 1 candidate mode record ebe5 resource end"
    .incbin "bank1_ebe7_ebe9.bin"
; Candidate descriptor $EBD3, script $ECE2, mode $02.
ModeRecordEBE5Fields:
    .byte $00, $01, $25, $FF, $12 ; CONTROL_MODE_RECORD_EBE5_FIELDS
.assert (* - BankStart) = $6BEE, error, "bank 1 candidate mode record ebe5 fields end"
; Related entry paths converge on the already recovered EC2B and EC33 loops.
ScriptEBEE:
    BogusSetSlot0670Pair $40, $00 ; CONTROL_BOGUS_EBEE
    BogusSetSlotValue $0000
    BogusSetSlotC0 $08
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $40
    BogusJumpBank1 ScriptEC2B
ScriptEBFD:
    BogusSetSlot0670Pair $20, $00
    BogusJumpBank1 ScriptEC06
ScriptEC03:
    BogusSetSlot0670Pair $00, $02
ScriptEC06:
    BogusSetSlotC0 $18
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $42
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0640Pair $04, $00
    BogusClearSlot0790Bits $01
    BogusJumpBank1 ScriptEC33
.assert (* - BankStart) = $6C1A, error, "bank 1 script EBEE end"
    .incbin "bank1_ec1a_ec2b.bin"
; Slot interactions and indexed audio paths; external data payloads remain local.
ScriptEC2B:
    BogusSetSlot0640Pair $04, $00 ; CONTROL_BOGUS_EC2B
    BogusSetUnlinkedFields $20, $00
    BogusClearSlot0790Bits $01
ScriptEC33:
    BogusBranchIfSlotD0Bits ScriptEC3F, $20
    BogusSetDispatchCounter $02
    BogusBranchIfSlot0620Bit10 ScriptEC7D
    BogusJumpBank1 ScriptEC33
ScriptEC3F:
    BogusSetDispatchCounter $02
    BogusRestartVoice4 $277A
    BogusSetDispatchCounter $86
    BogusBranchIfSlotD0Bits ScriptEC4D, $02
    BogusSetSlotFields80 $FF, $A0
ScriptEC4D:
    BogusSetSlotFields80 $00, $FF
    BogusSetSlotFields40Signed $20, $00
    BogusJumpBank1 ScriptEC74
ScriptEC56:
    BogusSetDispatchCounter $86
    BogusBranchIfSlotD0Bits ScriptEC66, $02
    BogusSetSlotFields80 $FF, $C0
    BogusBranchIfSlotD0BitsClear ScriptEC66, $01
    BogusStartVoice4 $284D
ScriptEC66:
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $0C, $FF
    BogusBranchIfSlotCoordinates01 ScriptEC74, $28, $10
    BogusSetDirectionalSlotFields40 $0C, $FF
ScriptEC74:
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusClearSlotD0Bits $20
    BogusJumpBank1 ScriptEC33
ScriptEC7D:
    BogusLoadSlotRecord $00, $02
    BogusSetSlot0620Bit20
    BogusWait $02
    BogusBranchIfSlotD0BitsClear ScriptEC8F, $01
    BogusLoadSlotRecord $12, $02
    BogusWait $0A
    BogusLoadSlotRecord $00, $02
ScriptEC8F:
    BogusSetDispatchCounter $05
    BogusBranchIfSlotCoordinates01 ScriptECFD, $1E, $10
    BogusBranchIfAbsSlot0700Below ScriptECBE, $11
    BogusBranchIfSlotD0Bits ScriptECA2, $08
    BogusBranchIfDirectionalOffsetClear ScriptECCD, $0C
ScriptECA2:
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptECB1, $0080
    BogusBranchIfSlotOffset ScriptECCD, $02, $00
    BogusJumpBank1 ScriptECB6
ScriptECB1:
    BogusBranchIfSlotOffset ScriptECCD, $FE, $00
ScriptECB6:
    BogusSetSlot0620Bit20
    BogusAdvanceAndBranchState1B ScriptECDA, $20
    BogusJumpBank1 ScriptEC56
ScriptECBE:
    BogusSetDispatchCounter $82
    BogusBranchIfSlotD0BitsClear ScriptECCD, $08
    BogusBranchIfSlotFieldsWithin ScriptECCD, $07, $FF
    BogusWait $02
    BogusYieldAndSlotAction $00
ScriptECCD:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusWait $0A
    BogusJumpBank1 ScriptEC56
ScriptECDA:
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $12, $02
    BogusLoadSlotValueArray $FF
    BogusBranchIfSlotValueAtLeast ScriptECF2, $8000
    BogusStartVoice4FromIndexedPair $26D0
    BogusJumpBank1 ScriptECF8
ScriptECF2:
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $26E4
ScriptECF8:
    BogusWait $0A
    BogusJumpBank1 ScriptEC56
ScriptECFD:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $12, $02
    BogusClearSlotD0Bits $40
ScriptED0A:
    BogusBranchIfSlotCoordinates01 ScriptED0A, $1E, $10
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6D11, error, "bank 1 script EC2B end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptED11:
    BogusSetSlotD0Bits $02 ; CONTROL_CONTEXT_ED11
    BogusSetSlotValue $0001
    BogusSetSlotD0Bits $01
    BogusJumpBank1 (BankStart + $6D7F)
.assert (* - BankStart) = $6D1B, error, "bank 1 contextual script ED11 end"
; Candidate descriptor $ED21, command $E89D, negative mode.
CompactContextED1B:
    SlotCompactRecord $BA0A, $22 ; CONTROL_COMPACT_CONTEXT_ED1B
.assert (* - BankStart) = $6D1E, error, "bank 1 compact candidate ed1b end"
; Candidate descriptor $ED21, command $E784, negative mode.
CompactContextED1E:
    SlotCompactRecord $C7BF, $00 ; CONTROL_COMPACT_CONTEXT_ED1E
.assert (* - BankStart) = $6D21, error, "bank 1 compact candidate ed1e end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeED21:
    SlotRuntimeRecord $BA0A, $6D45, $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_ED21
.assert (* - BankStart) = $6D2A, error, "bank 1 slot record ED21 end"
    .incbin "bank1_ed2a_ed2b.bin"
; Possible contact for descriptor base $ED21; execution remains unverified.
ReviewedContactED2A:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_ED2A
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6D2E, error, "bank 1 candidate contact ed2a end"
    .incbin "bank1_ed2e_ed34.bin"
; Candidate descriptor $ED21, script $EE2A, mode $01.
ModeRecordED33Sentinel:
    .byte $FF ; CONTROL_MODE_RECORD_ED33_SENTINEL
.assert (* - BankStart) = $6D35, error, "bank 1 candidate mode record ed33 sentinel end"
    .incbin "bank1_ed35_ed3c.bin"
; Candidate descriptor $ED21, command $EDFC, mode $00.
SlotFlowED3C:
    SlotRuntimeRecord $BA13, $6E0D, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_FLOW_ED3C
.assert (* - BankStart) = $6D45, error, "bank 1 slot record flow ED3C end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptED45:
    BogusSetSlotValue $0000 ; CONTROL_CONTEXT_ED45
    BogusSetSlotD0Bits $02
    BogusSetSlot05F0Pair $08, $60
    BogusJumpBank1 (BankStart + $6D7F)
.assert (* - BankStart) = $6D50, error, "bank 1 contextual script ED45 end"
; Candidate descriptor $ED56, command $E89D, negative mode.
CompactContextED50:
    SlotCompactRecord $B68A, $22 ; CONTROL_COMPACT_CONTEXT_ED50
.assert (* - BankStart) = $6D53, error, "bank 1 compact candidate ed50 end"
; Candidate descriptor $ED56, command $E784, negative mode.
CompactContextED53:
    SlotCompactRecord $BC6D, $00 ; CONTROL_COMPACT_CONTEXT_ED53
.assert (* - BankStart) = $6D56, error, "bank 1 compact candidate ed53 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeED56:
    SlotRuntimeRecord $B68A, (ScriptED71 - BankStart), $22, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_ED56
.assert (* - BankStart) = $6D5F, error, "bank 1 slot record ED56 end"
    .incbin "bank1_ed5f_ed60.bin"
; Possible contact for descriptor base $ED56; execution remains unverified.
ReviewedContactED5F:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_ED5F
    .word RuntimeScriptE764 - BankStart
.assert (* - BankStart) = $6D63, error, "bank 1 candidate contact ed5f end"
    .incbin "bank1_ed63_ed68.bin"
; Candidate descriptor $ED56, script $EE2A, mode $01.
ModeRecordED68Resource:
    .word $B683 ; CONTROL_MODE_RECORD_ED68_RESOURCE
.assert (* - BankStart) = $6D6A, error, "bank 1 candidate mode record ed68 resource end"
    .incbin "bank1_ed6a_ed6c.bin"
; Candidate descriptor $ED56, script $EE2A, mode $01.
ModeRecordED68Fields:
    .byte $00 ; CONTROL_MODE_RECORD_ED68_FIELDS
.assert (* - BankStart) = $6D6D, error, "bank 1 candidate mode record ed68 fields end"
    .incbin "bank1_ed6d_ed71.bin"
; Shared slot state graph with one unconverted branch destination.
ScriptEE1A = BankStart + $6E1A
ScriptED71:
    BogusSetSlotValue $0009 ; CONTROL_BOGUS_ED71
    BogusSetSlotD0Bits $09
    BogusSetSlot05F0Pair $10, $60
    BogusJumpBank1 ScriptED7F
ScriptED7C:
    BogusSetSlotValue $0003
ScriptED7F:
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusClearSlot0790Bits $01
    BogusBranchIfSlotFieldsWithin ScriptED91, $07, $FF
    BogusJumpBank1 ScriptED9B
ScriptED91:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusWait $0A
ScriptED9B:
    BogusSetDispatchCounter $06
    BogusBranchIfSlotD0BitsClear ScriptEDAA, $08
    BogusAdvanceAndBranchState1B ScriptEDAA, $E8
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
ScriptEDAA:
    BogusBranchIfDirectionalOffsetClear ScriptEDEF, $0C
    BogusBranchIfAbsSlot0700Below ScriptEDEF, $20
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast ScriptEDC1, $0080
    BogusBranchIfSlotOffset ScriptEDEF, $02, $00
    BogusJumpBank1 ScriptEDC6
ScriptEDC1:
    BogusBranchIfSlotOffset ScriptEDEF, $02, $00
ScriptEDC6:
    BogusSetSlot0670Pair $05, $00
    BogusBranchIfSlotD0BitsClear ScriptEDD6, $02
    BogusBranchIfSlotCoordinatesA3 ScriptEDD6, $30, $FF
    BogusAdvanceAndBranchState1B ScriptEDFC, $10
ScriptEDD6:
    BogusBranchIfSlotCoordinatesA3 ScriptEDE0, $28, $FF
    BogusBranchIfSlotCoordinates01 ScriptEE1A, $30, $10
ScriptEDE0:
    BogusBranchIfSlotD0BitsClear ScriptED9B, $04
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 ScriptEDFC, $40, $40
    BogusJumpBank1 ScriptED9B
ScriptEDEF:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $E8, $FF
    BogusWait $0A
    BogusJumpBank1 ScriptED9B
ScriptEDFC:
    BogusLoadRecordAndClearSavedState $1B
.assert (* - BankStart) = $6DFE, error, "bank 1 script ED71 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptEDFE:
    BogusSetDispatchCounter $82 ; CONTROL_CONTEXT_EDFE
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusWait $28
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusLoadRecordAndClearSavedState $00
ContextScriptEE0D:
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusWait $28
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6E1A, error, "bank 1 contextual script EDFE end"
; Candidate script path; object role and execution remain unverified.
CandidateEE1A:
    BogusLoadSlotValueArray $FF ; CONTROL_BOGUS_EE1A
    BogusBranchIfSlotValueAtLeast CandidateEE3A, $8000
    BogusStartVoice4FromIndexedPair $26D0
    BogusBranchIfSlotD0BitsClear CandidateEE38, $01
    BogusSetDispatchCounter $84
    BogusLoadSlotRecord $12, $01
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusWait $0A
    BogusSetDirectionalSlotFields40 $18, $FF
CandidateEE38:
    BogusLoadRecordAndClearSavedState $00
CandidateEE3A:
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $26E4
    BogusLoadRecordAndClearSavedState $00
.assert (* - BankStart) = $6E42, error, "bank 1 candidate script EE1A end"
; Candidate descriptor $EE45, command $F009, mode $FF.
SlotFlowEE42:
    SlotCompactRecord $B5E7, $00 ; CONTROL_SLOT_FLOW_EE42
.assert (* - BankStart) = $6E45, error, "bank 1 slot record flow EE42 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEE45:
    SlotRuntimeRecord $BA45, $6E57, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EE45
.assert (* - BankStart) = $6E4E, error, "bank 1 slot record EE45 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordEE4E:
    SlotRuntimeRecord $BA45, (InteractionScriptF00F - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_EE4E
.assert (* - BankStart) = $6E57, error, "bank 1 sweep record $EE4E end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptEE57:
    BogusSetSlot0640Pair $00, $50 ; CONTROL_RUNTIME_SCRIPT_EE57
RuntimeScriptEE5A:
    BogusSetSlotD0Bits $01
RuntimeScriptEE5C:
    BogusBranchIfSlot0630Bit02 (BankStart + $6E62)
RuntimeScriptEE5F:
    BogusJumpBank1 (BankStart + $6FF3)
.assert (* - BankStart) = $6E62, error, "bank 1 runtime script $EE57 end"
; Candidate successor of a longer-run command; control flow remains provisional.
; Labels preserve independent branch and resume entries.
ExtendedScriptEE62:
    BogusBranchIfSlot0620Bit10 (BankStart + $6FF3) ; CONTROL_EXTENDED_SCRIPT_EE62
.assert (* - BankStart) = $6E65, error, "bank 1 extended script $EE62 end"
    .incbin "bank1_ee65_ee68.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEE68:
    SlotRuntimeRecord $B6B7, $6E7A, $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EE68
.assert (* - BankStart) = $6E71, error, "bank 1 slot record EE68 end"
    .incbin "bank1_ee71_ee72.bin"
; Possible contact for descriptor base $EE68; execution remains unverified.
ReviewedContactEE71:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EE71
    .word InteractionScriptF00F - BankStart
.assert (* - BankStart) = $6E75, error, "bank 1 candidate contact ee71 end"
    .incbin "bank1_ee75_ee7a.bin"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptEE7A:
    BogusSetSlot0640Pair $00, $40 ; CONTROL_RETAINED_SCRIPT_EE7A
RetainedScriptEE7D:
    BogusSetSlotD0Bits $04
.assert (* - BankStart) = $6E7F, error, "bank 1 candidate successor $EE7A end"
    .incbin "bank1_ee7f_ee82.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEE82:
    SlotRuntimeRecord $BE9D, (ScriptEFDD - BankStart), $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EE82
.assert (* - BankStart) = $6E8B, error, "bank 1 slot record EE82 end"
    .incbin "bank1_ee8b_ee8c.bin"
; Possible contact for descriptor base $EE82; execution remains unverified.
ReviewedContactEE8B:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EE8B
    .word InteractionScriptF00F - BankStart
.assert (* - BankStart) = $6E8F, error, "bank 1 candidate contact ee8b end"
    .incbin "bank1_ee8f_ee91.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordEE91:
    SlotCompactRecord $0000, $00 ; CONTROL_CONTEXT_FIELDS_EE91
.assert (* - BankStart) = $6E94, error, "bank 1 candidate record field $EE91 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEE94:
    SlotRuntimeRecord $BE99, (ScriptEFE9 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EE94
.assert (* - BankStart) = $6E9D, error, "bank 1 slot record EE94 end"
    .incbin "bank1_ee9d_ee9e.bin"
; Possible contact for descriptor base $EE94; execution remains unverified.
ReviewedContactEE9D:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EE9D
    .word InteractionScriptF00F - BankStart
.assert (* - BankStart) = $6EA1, error, "bank 1 candidate contact ee9d end"
    .incbin "bank1_eea1_eea3.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordEEA3:
    SlotCompactRecord $0000, $00 ; CONTROL_CONTEXT_FIELDS_EEA3
.assert (* - BankStart) = $6EA6, error, "bank 1 candidate record field $EEA3 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEEA6:
    SlotRuntimeRecord $C7C5, (ScriptEFDD - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EEA6
.assert (* - BankStart) = $6EAF, error, "bank 1 slot record EEA6 end"
    .incbin "bank1_eeaf_eeb5.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordEEB5:
    SlotCompactRecord $0000, $00 ; CONTROL_CONTEXT_FIELDS_EEB5
.assert (* - BankStart) = $6EB8, error, "bank 1 candidate record field $EEB5 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEEB8:
    SlotRuntimeRecord $BAD5, $6ECA, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EEB8
.assert (* - BankStart) = $6EC1, error, "bank 1 slot record EEB8 end"
    .incbin "bank1_eec1_eeca.bin"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptEECA:
    BogusSetSlot0640Pair $00, $44 ; CONTROL_RETAINED_SCRIPT_EECA
.assert (* - BankStart) = $6ECD, error, "bank 1 candidate successor $EECA end"
    .incbin "bank1_eecd_eed0.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEED0:
    SlotRuntimeRecord $C7D5, $6EE2, $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EED0
.assert (* - BankStart) = $6ED9, error, "bank 1 slot record EED0 end"
    .incbin "bank1_eed9_eee2.bin"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptEEE2:
    BogusSetSlot0640Pair $40, $40 ; CONTROL_RETAINED_SCRIPT_EEE2
.assert (* - BankStart) = $6EE5, error, "bank 1 candidate successor $EEE2 end"
    .incbin "bank1_eee5_eee8.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEEE8:
    SlotRuntimeRecord $B74E, $6EFA, $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EEE8
.assert (* - BankStart) = $6EF1, error, "bank 1 slot record EEE8 end"
    .incbin "bank1_eef1_eef2.bin"
; Possible contact for descriptor base $EEE8; execution remains unverified.
ReviewedContactEEF1:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EEF1
    .word InteractionScriptF00F - BankStart
.assert (* - BankStart) = $6EF5, error, "bank 1 candidate contact eef1 end"
    .incbin "bank1_eef5_eefa.bin"
; Possible continuation after a retained script pointer; reachability is unverified.
RetainedScriptEEFA:
    BogusSetSlot0640Pair $00, $42 ; CONTROL_RETAINED_SCRIPT_EEFA
.assert (* - BankStart) = $6EFD, error, "bank 1 candidate successor $EEFA end"
    .incbin "bank1_eefd_ef00.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF00:
    SlotRuntimeRecord $C393, (ScriptEFE9 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EF00
.assert (* - BankStart) = $6F09, error, "bank 1 slot record EF00 end"
    .incbin "bank1_ef09_ef0a.bin"
; Possible contact for descriptor base $EF00; execution remains unverified.
ReviewedContactEF09:
    .byte $FF ; CONTROL_REVIEWED_CONTACT_EF09
    .word InteractionScriptF00F - BankStart
.assert (* - BankStart) = $6F0D, error, "bank 1 candidate contact ef09 end"
    .incbin "bank1_ef0d_ef0f.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordEF0F:
    SlotCompactRecord $0000, $00 ; CONTROL_CONTEXT_FIELDS_EF0F
.assert (* - BankStart) = $6F12, error, "bank 1 candidate record field $EF0F end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF12:
    SlotRuntimeRecord $C397, (ScriptEFE9 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EF12
.assert (* - BankStart) = $6F1B, error, "bank 1 slot record EF12 end"
    .incbin "bank1_ef1b_ef21.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordEF21:
    SlotCompactRecord $0000, $00 ; CONTROL_CONTEXT_FIELDS_EF21
.assert (* - BankStart) = $6F24, error, "bank 1 candidate record field $EF21 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF24:
    SlotRuntimeRecord $BAAF, (ScriptEFE9 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EF24
.assert (* - BankStart) = $6F2D, error, "bank 1 slot record EF24 end"
    .incbin "bank1_ef2d_ef33.bin"
; Candidate descriptor-context access; runtime reachability remains unverified.
ContextRecordEF33:
    SlotCompactRecord $0000, $00 ; CONTROL_CONTEXT_FIELDS_EF33
.assert (* - BankStart) = $6F36, error, "bank 1 candidate record field $EF33 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF36:
    SlotRuntimeRecord $BAB3, (ScriptEFF0 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_EF36
.assert (* - BankStart) = $6F3F, error, "bank 1 slot record EF36 end"
    .incbin "bank1_ef3f_ef48.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF48:
    SlotRuntimeRecord $BA23, (ScriptEF87 - BankStart), $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EF48
.assert (* - BankStart) = $6F51, error, "bank 1 slot record EF48 end"
; Zero-mode record; bytes gated by sentinel values may be skipped.
SweepRecordEF51:
    SlotRuntimeRecord $FFFF, (InteractionScriptF00F - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SWEEP_RECORD_EF51
.assert (* - BankStart) = $6F5A, error, "bank 1 sweep record $EF51 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF5A:
    SlotRuntimeRecord $BB8B, (ScriptEF87 - BankStart), $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EF5A
.assert (* - BankStart) = $6F63, error, "bank 1 slot record EF5A end"
; Observed in zero mode; fields gated by $FFFF may be skipped.
InteractionRecordEF63:
    SlotRuntimeRecord $FFFF, (InteractionScriptF00F - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_INTERACTION_RECORD_EF63
.assert (* - BankStart) = $6F6C, error, "bank 1 interaction record $EF63 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeEF6C:
    SlotRuntimeRecord $C533, (ScriptEF7E - BankStart), $00, $00, $20, $D9, $11 ; CONTROL_SLOT_RUNTIME_EF6C
.assert (* - BankStart) = $6F75, error, "bank 1 slot record EF6C end"
    .incbin "bank1_ef75_ef7e.bin"
; Slot sequence joining the existing $EFF3 path.
ScriptEF7E:
    BogusSetSlot0640Pair $00, $40 ; CONTROL_BOGUS_EF7E
    BogusSetSlotC0 $0C
    BogusBranchIfSlot0780Equal ScriptEFF3, $00
ScriptEF87:
    BogusSetSlot0640Pair $20, $40
    BogusSetDispatchCounter $8C
    BogusSetSlot05F0Pair $60, $60
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusSetSlot0730 $80
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotFields80 $00, $A0
    BogusRelinkSlots
    BogusBranchIfSlotCoordinatesA3 ScriptEFB6, $10, $FF
    BogusAddSlotFields00 $10, $00
    BogusBranchIfSlotCoordinatesA3 ScriptEFB6, $30, $FF
    BogusAddSlotFields00 $10, $00
    BogusBranchIfSlotCoordinatesA3 ScriptEFB6, $60, $FF
    BogusAddSlotFields00 $20, $00
ScriptEFB6:
    BogusSetSlot0620Bit20
    BogusBranchIfSlotCoordinatesA3 ScriptEFC5, $FF, $20
    BogusBranchIfSlot0620Bit10 ScriptEFC5
    BogusBranchIfSlotB0AtMost ScriptEFB6, $E6
    BogusYieldAndSlotAction $00
ScriptEFC5:
    BogusSetDispatchCounter $03
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusSetSlot0620Bit20
    BogusClearSlot0790Bits $01
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $19
    BogusSetSlotMode $FF
ScriptEFD7:
    BogusBranchIfSlotB0AtMost ScriptEFD7, $E6
    BogusYieldAndSlotAction $00
ScriptEFDD:
    BogusSetSlot0640Pair $08, $40
    BogusJumpBank1 ScriptEFF3
ScriptEFE3:
    BogusSetSlot0640Pair $20, $40
    BogusJumpBank1 ScriptEFF3
ScriptEFE9:
    BogusBranchIfSlot0780Equal ScriptEF87, $2C
    BogusJumpBank1 ScriptEFE3
.assert (* - BankStart) = $6FF0, error, "bank 1 script EF7E end"

; Shared target of several candidate entries. The bit tests and record load
; loop here are decoded; the roles of the values remain provisional.
ScriptEFF0:
    BogusSetSlot0640Pair $10, $40
ScriptEFF3:
    BogusSetSlotC0 $FF
    BogusClearSlot0790Bits $01
    BogusClearSlotD0Bits $02
ScriptEFF9:
    BogusBranchIfSlotD0Bits ScriptF000, $01
    BogusJumpBank1 ScriptEFF9
ScriptF000:
    BogusBranchIfSlot0620Bit10Clear ScriptEFF3
    BogusBranchIfSlotD0Bits ScriptEFF9, $02
    BogusSetSlotD0Bits $02       ; CONTROL_BOGUS_EFF0
    BogusLoadSlotRecord $03, $FF
    BogusJumpBank1 ScriptEFF9
.assert (* - BankStart) = $700F, error, "bank 1 script EFF0 end"
; Command entries observed in the varied-input emulator exploration.
InteractionScriptF00F:
    BogusSetDispatchCounter $07 ; CONTROL_INTERACTION_SCRIPT_F00F
InteractionScriptF011:
    BogusBranchIfSelectedFieldEqual (BankStart + $7058), $12
InteractionScriptF015:
    BogusBranchIfSlot06D0Present (BankStart + $708A)
InteractionScriptF018:
    BogusBranchIfSelectedFieldEqual (BankStart + $7025), $10
InteractionScriptF01C:
    BogusBranchIfSelectedFieldEqual (BankStart + $7128), $1F
InteractionScriptF020:
    BogusBranchIfSelectedFieldEqual (BankStart + $712C), $07
InteractionScriptF024:
    BogusRestoreSavedScriptAndSlotFlags
.assert (* - BankStart) = $7025, error, "bank 1 interaction script $F00F end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF025:
    BogusSetSlot0790Bits $FF ; CONTROL_BRANCH_SCRIPT_F025
BranchScriptF027:
    BogusFollowLinkedSlotsAndYield $FF, $FF, $23, $00, $00
BranchScriptF02D:
    BogusSetSlot05E0Bit40 $01
.assert (* - BankStart) = $702F, error, "bank 1 branch script $F025 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptF02F:
    BogusStartVoice4 $2826 ; CONTROL_SWEEP_SCRIPT_F02F
SweepScriptF032:
    BogusSetLinkedFieldsAndYield $FF, $FE
SweepScriptF035:
    BogusSetLinkedFieldsAndYield $FF, $FC
SweepScriptF038:
    BogusSetLinkedFieldsAndYield $FF, $F8
SweepScriptF03B:
    BogusSetLinkedFieldsAndYield $FF, $F4
SweepScriptF03E:
    BogusSetLinkedFieldsAndYield $80, $F2
SweepScriptF041:
    BogusBranchIfSlotD0BitsClear BranchScriptF04B, $04
.assert (* - BankStart) = $7045, error, "bank 1 sweep script $F02F end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptF045:
    BogusSetBackgroundPalettePointer $C864 ; CONTROL_PATH_SCRIPT_F045
PathScriptF048:
    BogusSetSpritePalettePointer $C818
.assert (* - BankStart) = $704B, error, "bank 1 candidate successor $F045 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF04B:
    BogusSetSlot07F0 $14 ; CONTROL_BRANCH_SCRIPT_F04B
BranchScriptF04D:
    BogusSetSlot0630Bit04UnlessFF $01
BranchScriptF04F:
    BogusClearSlot0640PairBits $00, $40
.assert (* - BankStart) = $7052, error, "bank 1 branch script $F04B end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptF052:
    BogusCopyLinkedMotionFields
SweepScriptF053:
    BogusClearSlot0790Bits $01 ; CONTROL_SWEEP_SCRIPT_F052
SweepScriptF055:
    BogusJumpBank1 SweepScriptF052
.assert (* - BankStart) = $7058, error, "bank 1 sweep script $F052 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF058:
    BogusRelinkSlots
BranchScriptF059:
    BogusSetDispatchCounter $8F ; CONTROL_BRANCH_SCRIPT_F058
BranchScriptF05B:
    BogusSetSlotC0 $FF
BranchScriptF05D:
    BogusReadSlotValue $13
BranchScriptF05F:
    BogusSetSlotMode $00
BranchScriptF061:
    BogusSetSlotMode $02
BranchScriptF063:
    BogusSetSlot05E0Bit40 $FF
.assert (* - BankStart) = $7065, error, "bank 1 branch script $F058 end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptF065:
    BogusSetSlot05F0Pair $60, $60 ; CONTROL_EXPANDED_SCRIPT_F065
ExpandedScriptF068:
    BogusSetVoicePointers $278C, $2795, $0000, $0000
ExpandedScriptF071:
    BogusSetSlot0730 $80
ExpandedScriptF073:
    BogusSetSlotPositionFromOperands $60, $A7
ExpandedScriptF076:
    BogusSetSlot0660LowBits $00
ExpandedScriptF078:
    BogusSelectStateTableValue $4E
ExpandedScriptF07A:
    BogusSetSpritePalettePointer $0000
ExpandedScriptF07D:
    BogusSetSlotFields80 $40, $A0
ExpandedScriptF080:
    BogusBranchIfSlot0620Bit10Clear ExpandedScriptF080
ExpandedScriptF083:
    BogusWait $01
ExpandedScriptF085:
    BogusBranchIfSlot0620Bit10Clear ExpandedScriptF080
ExpandedScriptF088:
    BogusYieldAndSlotAction $01
.assert (* - BankStart) = $708A, error, "bank 1 candidate successor $F065 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF08A:
    BogusBranchIfSelectedFieldEqual BranchScriptF0A5, $11 ; CONTROL_BRANCH_SCRIPT_F08A
BranchScriptF08E:
    BogusBranchIfSelectedFieldEqual BranchScriptF0FB, $13
BranchScriptF092:
    BogusBranchIfSelectedFieldEqual BranchScriptF13D, $14
BranchScriptF096:
    BogusBranchIfSelectedFieldEqual BranchScriptF0A1, $1E
BranchScriptF09A:
    BogusBranchIfSelectedFieldEqual BranchScriptF11F, $0D
BranchScriptF09E:
    BogusJumpBank1 BranchScriptF04B
BranchScriptF0A1:
    BogusRelinkToLastRelatedSlot
.assert (* - BankStart) = $70A2, error, "bank 1 branch script $F08A end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptF0A2:
    BogusJumpBank1 BranchScriptF04B ; CONTROL_EXPANDED_SCRIPT_F0A2
.assert (* - BankStart) = $70A5, error, "bank 1 candidate successor $F0A2 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF0A5:
    BogusSetDispatchCounter $88 ; CONTROL_BRANCH_SCRIPT_F0A5
BranchScriptF0A7:
    BogusSetSlot05F0Pair $7F, $7F
BranchScriptF0AA:
    BogusCopyLinkedMotionFields
.assert (* - BankStart) = $70AB, error, "bank 1 branch script $F0A5 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptF0AB:
    BogusSetDirectionalSlotFields40 $38, $FF ; CONTROL_SWEEP_SCRIPT_F0AB
SweepScriptF0AE:
    BogusSetSlot0730 $80
SweepScriptF0B0:
    BogusSetSlotMode $03
SweepScriptF0B2:
    BogusSetSlot0640PairBits $00, $40
SweepScriptF0B5:
    BogusRelinkSlots
SweepScriptF0B6:
    BogusSetSlot07F0 $44
SweepScriptF0B8:
    BogusSetSlot05E0Bit40 $FF
SweepScriptF0BA:
    BogusClearSlot0790Bits $01
SweepScriptF0BC:
    BogusBranchIfSlotD0BitsClear SweepScriptF0C9, $04
.assert (* - BankStart) = $70C0, error, "bank 1 sweep script $F0AB end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptF0C0:
    BogusSetBackgroundPalettePointer $FFFF ; CONTROL_PATH_SCRIPT_F0C0
PathScriptF0C3:
    BogusSetSpritePalettePointer $FFFF
PathScriptF0C6:
    BogusJumpBank1 (BankStart + $70DC)
.assert (* - BankStart) = $70C9, error, "bank 1 candidate successor $F0C0 end"
; Command entries observed during the 16,000-frame exploratory sweep.
SweepScriptF0C9:
    BogusBranchIfSlotD0BitsClear (BankStart + $70DC), $01 ; CONTROL_SWEEP_SCRIPT_F0C9
SweepScriptF0CD:
    BogusBranchIfSlot0760Equal (BankStart + $7147), $02
.assert (* - BankStart) = $70D1, error, "bank 1 sweep script $F0C9 end"
; Candidate script path; object role and execution remain unverified.
CandidateF0D1:
    BogusBranchIfRemainingVerticalOffsetAtMost (BankStart + $7157), $0028 ; CONTROL_BOGUS_F0D1
    BogusBranchIfSlot0620Bit10 CandidateF0F0
    BogusJumpBank1 CandidateF0D1
CandidateF0DC:
    BogusSetSlot0620Bit20
    BogusBranchIfSlot0620Bit10 CandidateF0F0
CandidateF0E0:
    BogusBranchIfSlotB0AtMost CandidateF0DC, $E6
    BogusBranchIfSlotD0Bits CandidateF0EA, $01
    BogusYieldAndSlotAction $00
CandidateF0EA:
    BogusSetSlotFields80 $00, $00
    BogusJumpBank1 CandidateF0E0
CandidateF0F0:
    BogusStartVoice4 $2724
    BogusWait $01
    BogusBranchIfSlot0620Bit10Clear CandidateF0DC
    BogusJumpBank1 (BankStart + $6FF3)
.assert (* - BankStart) = $70FB, error, "bank 1 candidate script F0D1 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF0FB:
    BogusSetDispatchCounter $87 ; CONTROL_BRANCH_SCRIPT_F0FB
BranchScriptF0FD:
    BogusSetSlotFields80 $00, $E0
BranchScriptF100:
    BogusSetSlotMode $03
BranchScriptF102:
    BogusSetSlot0640PairBits $00, $40
.assert (* - BankStart) = $7105, error, "bank 1 branch script $F0FB end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptF105:
    BogusRelinkSlots
ExpandedScriptF106:
    BogusSetSlot07F0 $44 ; CONTROL_EXPANDED_SCRIPT_F105
ExpandedScriptF108:
    BogusSetSlot05E0Bit40 $FF
ExpandedScriptF10A:
    BogusClearSlot0790Bits $01
ExpandedScriptF10C:
    BogusBranchIfSlot0620Bit10Clear ExpandedScriptF10C
ExpandedScriptF10F:
    BogusStartVoice4 $2724
ExpandedScriptF112:
    BogusBranchIfSlotD0BitsClear (BankStart + $6FF3), $04
ExpandedScriptF116:
    BogusSetBackgroundPalettePointer $FFFF
ExpandedScriptF119:
    BogusSetSpritePalettePointer $FFFF
ExpandedScriptF11C:
    BogusJumpBank1 (BankStart + $6FF3)
.assert (* - BankStart) = $711F, error, "bank 1 candidate successor $F105 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptF11F:
    BogusSetBackgroundPalettePointer $C864 ; CONTROL_BRANCH_SCRIPT_F11F
BranchScriptF122:
    BogusSetSpritePalettePointer $C818
BranchScriptF125:
    BogusJumpBank1 (BankStart + $6FF3)
BranchScriptF128:
    BogusWait $1E
BranchScriptF12A:
    BogusYieldAndSlotAction $00
BranchScriptF12C:
    BogusSetDirectionalSlotFields40 $08, $FF
BranchScriptF12F:
    BogusSetSlotFields80 $FF, $A0
BranchScriptF132:
    BogusSetSlotFields80 $FF, $A0
BranchScriptF135:
    BogusSetSlotFields80 $FF, $A0
BranchScriptF138:
    BogusClearSlot0790Bits $01
BranchScriptF13A:
    BogusJumpBank1 (BankStart + $70DC)
BranchScriptF13D:
    BogusReadSlotValue $02
BranchScriptF13F:
    BogusSwapSlotValueBytes
BranchScriptF140:
    BogusLoadSlotLowFromByteArray $2A
BranchScriptF142:
    BogusSwapSlotValueBytes
BranchScriptF143:
    BogusStoreSlotLowAtIndexedPage
.assert (* - BankStart) = $7144, error, "bank 1 branch script $F11F end"
; Candidate successors after reviewed handler returns; reachability is unverified.
ExpandedScriptF144:
    BogusJumpBank1 BranchScriptF04B ; CONTROL_EXPANDED_SCRIPT_F144
.assert (* - BankStart) = $7147, error, "bank 1 candidate successor $F144 end"
; Static candidate successors; independent entries do not prove reachability.
PathScriptF147:
    BogusSetSlotMode $FF ; CONTROL_PATH_SCRIPT_F147
PathScriptF149:
    BogusSetSlot05F0Pair $FF, $40
PathScriptF14C:
    BogusBranchIfRemainingVerticalOffsetAtMost (BankStart + $7157), $0028
PathScriptF151:
    BogusBranchIfSecondWorldOffsetAtMost PathScriptF14C, $1EE5
.assert (* - BankStart) = $7156, error, "bank 1 candidate successor $F147 end"
    .incbin "bank1_f156_f157.bin"
; Candidate script path; object role and execution remain unverified.
CandidateF157:
    BogusSetDispatchCounter $85 ; CONTROL_BOGUS_F157
    BogusSetSlotFields80 $00, $00
    BogusSetSlotC0 $00
    BogusSetSlot0640Pair $00, $00
    BogusRestartVoice4 $2890
    BogusInitializeOtherSlotRelative $54, $00, $02, $00
    BogusWait $05
    BogusYieldAndSlotAction $00
.assert (* - BankStart) = $716D, error, "bank 1 candidate script F157 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeF16D:
    SlotRuntimeRecord $B9AF, (ScriptF176 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_F16D
.assert (* - BankStart) = $7176, error, "bank 1 slot record F16D end"
; State-update and palette setup sequence; data payloads remain local.
ScriptF176:
    BogusSetDispatchCounter $8F ; CONTROL_BOGUS_F176
    BogusSetState13Bits $0F
    BogusSetSlotC0 $00
    BogusSetState03BC $00
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusQueueState6E $73CD, $0B, $0C, $00, $09
    BogusQueueState6E $73D6, $0C, $0C, $00, $09
    BogusQueueState6E $73DF, $0D, $0C, $00, $11
    BogusQueueState6E $73F0, $0E, $0C, $00, $11
    BogusQueueState6E $73A2, $19, $0B, $00, $12
    BogusQueueState6E $73B4, $1A, $0D, $00, $11
    BogusQueueState6E $73C5, $1B, $0D, $00, $08
    BogusInitializeOtherSlotAbsolute $06, $22, $A6, $00
    BogusReadSlotValue $00
    BogusBranchIfSlotValueNotEqual ScriptF1E8, $0000
    BogusQueueState6E $737C, $10, $11, $00, $01
    BogusQueueState6E $737D, $11, $0D, $00, $0A
    BogusQueueState6E $7387, $13, $0D, $00, $0A
    BogusQueueState6E $7391, $15, $0D, $00, $11
    BogusMarkMatchingSlots $10, $01, $06, $00
    BogusJumpBank1 ScriptF223
ScriptF1E8:
    BogusQueueState6E $7361, $11, $0D, $00, $0A
    BogusQueueState6E $7357, $13, $0D, $00, $0A
    BogusQueueState6E $736B, $15, $0D, $00, $11
    BogusSetSlotValue $000C
    BogusStoreSlotValueArray $26
    BogusLoadSlotValueArray $3A
    BogusBranchIfSlotValueAtLeast ScriptF211, $0005
    BogusMarkMatchingSlots $00, $01, $06, $00
    BogusJumpBank1 ScriptF223
ScriptF211:
    BogusBranchIfSlotValueAtLeast ScriptF21E, $000B
    BogusMarkMatchingSlots $10, $01, $06, $00
    BogusJumpBank1 ScriptF223
ScriptF21E:
    BogusMarkMatchingSlots $20, $01, $06, $00
ScriptF223:
    BogusSetDispatchCounter $03
    BogusSetBackgroundPalettePointer $CA37
    BogusSetSpritePalettePointer $CA4A
    BogusBranchIfState07ZeroAndClear ScriptF230
    BogusSetInvertedState3B $FF
ScriptF230:
    BogusSetInvertedState18 $FF
    BogusSetSlotValue $000C
    BogusStoreSlotValueArray $26
    BogusSetInvertedState03ED $01
    BogusSetSlotAssociation $00
    BogusSetSelectedField $02, $01
    BogusWait $05
    BogusSetVoicePointers $2A58, $2AA3, $0000, $0000
    BogusJumpBank1 ScriptF27E
.assert (* - BankStart) = $724C, error, "bank 1 script F176 end"
; Input-controlled state sequence; downstream targets remain local.
ScriptF313 = BankStart + $7313
ScriptF24C:
    BogusSetSlotPositionFromOperands $58, $78 ; CONTROL_BOGUS_F24C
    BogusSetVoicePointers $FFFF, $FFFF, $2783, $FFFF
    BogusReadSlotValue $00
    BogusBranchIfSlotValueNotEqual ScriptF264, $0000
    BogusMarkMatchingSlots $00, $01, $06, $00
ScriptF264:
    BogusWait $03
ScriptF266:
    BogusBranchIfSelectedFlags ScriptF275, $24
    BogusBranchIfSelectedFlags ScriptF29E, $08
    BogusBranchIfSelectedFlags ScriptF2C7, $D0
    BogusJumpBank1 ScriptF266
ScriptF275:
    BogusSetVoicePointers $FFFF, $FFFF, $2783, $FFFF
ScriptF27E:
    BogusSetSlotPositionFromOperands $58, $88
    BogusReadSlotValue $00
    BogusBranchIfSlotValueNotEqual ScriptF28D, $0000
    BogusMarkMatchingSlots $10, $01, $06, $00
ScriptF28D:
    BogusWait $03
ScriptF28F:
    BogusBranchIfSelectedFlags ScriptF29E, $24
    BogusBranchIfSelectedFlags ScriptF24C, $08
    BogusBranchIfSelectedFlags ScriptF2C7, $D0
    BogusJumpBank1 ScriptF28F
ScriptF29E:
    BogusSetSlotPositionFromOperands $58, $98
    BogusSetVoicePointers $FFFF, $FFFF, $2783, $FFFF
    BogusReadSlotValue $00
    BogusBranchIfSlotValueNotEqual ScriptF2B6, $0000
    BogusMarkMatchingSlots $20, $01, $06, $00
ScriptF2B6:
    BogusWait $03
ScriptF2B8:
    BogusBranchIfSelectedFlags ScriptF24C, $24
    BogusBranchIfSelectedFlags ScriptF275, $08
    BogusBranchIfSelectedFlags ScriptF2C7, $D0
    BogusJumpBank1 ScriptF2B8
ScriptF2C7:
    BogusReadSlotValue $00
    BogusBranchIfSlotValueEqual ScriptF313, $00, $00
    BogusSetDispatchCounter $8F
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusClearSlotBitset $FF
.assert (* - BankStart) = $72DB, error, "bank 1 script F24C end"
; Candidate script path; object role and execution remain unverified.
CandidateF2DB:
    BogusClearState13Bits $0F ; CONTROL_BOGUS_F2DB
    BogusReadSlotValue $52
    BogusLookupSlotValue
    BogusLookupCaseBank1 CandidateF2F7, $0078
    BogusLookupCaseBank1 CandidateF2EE, $0088
    BogusLookupCaseBank1 CandidateF30E, $0098
    BogusLookupEnd
CandidateF2EE:
    BogusLoadSlotValueArray $3A
    BogusCallNativeEncoded $B51B
    BogusSetState03BC $03
    BogusSetMainState $00
CandidateF2F7:
    BogusCallNativeEncoded $B51B
    BogusSetState03BC $03
    BogusLoadSlotValueArray $3A
    BogusBranchIfSlotValueAtLeast CandidateF305, $0005
    BogusSetMainState $01
CandidateF305:
    BogusBranchIfSlotValueAtLeast CandidateF30C, $000B
    BogusSetMainState $05
CandidateF30C:
    BogusSetMainState $0B
CandidateF30E:
    BogusCallNativeEncoded $B51B
    BogusSetMainState $FF
    BogusSetDispatchCounter $8F
    BogusClearSlotBitset $FF
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusClearState13Bits $0F
    BogusReadSlotValue $52
    BogusLookupSlotValue
    BogusLookupCaseBank1 CandidateF333, $0078
    BogusLookupCaseBank1 CandidateF33E, $0088
    BogusLookupCaseBank1 CandidateF349, $0098
    BogusLookupEnd
CandidateF333:
    BogusSetSlotValue $000A
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $0001
    BogusJumpBank1 (BankStart + $7401)
CandidateF33E:
    BogusSetSlotValue $002B
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $0005
    BogusJumpBank1 (BankStart + $7401)
CandidateF349:
    BogusSetSlotValue $0012
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $000B
    BogusJumpBank1 (BankStart + $7401)
.assert (* - BankStart) = $7354, error, "bank 1 candidate script F2DB end"
    .incbin "bank1_f354_f401.bin"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptF401:
    BogusCallNativeEncoded $B51B ; CONTROL_CONTEXT_F401
    BogusSetState03BC $03
    BogusStoreSlotValueArray $23
    BogusSetMainState $10
.assert (* - BankStart) = $740A, error, "bank 1 contextual script F401 end"
    .incbin "bank1_f40a_f410.bin"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordF410:
    SlotCompactRecord $BA4B, $00 ; CONTROL_RUNTIME_RECORD_F410
RuntimeRecordF413:
    SlotCompactRecord $BBF7, $00
RuntimeRecordF416:
    SlotCompactRecord $C28F, $00
.assert (* - BankStart) = $7419, error, "bank 1 runtime records $F410 end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeF419:
    SlotRuntimeRecord $BC89, $742B, $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_F419
.assert (* - BankStart) = $7422, error, "bank 1 slot record F419 end"
; Record accesses observed at the bank-0 loader in the opening scenarios.
; Fields behind a $FFFF resource pointer may not be read by the loader.
RuntimeRecordF422:
    SlotRuntimeRecord $FFFF, (RuntimeScriptF432 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_RUNTIME_RECORD_F422
.assert (* - BankStart) = $742B, error, "bank 1 runtime records $F422 end"
; Candidate script entries from the reviewed slot-record context trace.
ContextScriptF42B:
    BogusSetSlotC0 $00 ; CONTROL_CONTEXT_F42B
    BogusClearSlot0790Bits $01
ContextScriptF42F:
    BogusJumpBank1 ContextScriptF42F
.assert (* - BankStart) = $7432, error, "bank 1 contextual script F42B end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptF432:
    BogusReadSlotValue $24 ; CONTROL_RUNTIME_SCRIPT_F432
RuntimeScriptF434:
    BogusJumpViaSlotIndexedTable
.assert (* - BankStart) = $7435, error, "bank 1 runtime script $F432 end"
; Three adjacent indexed targets. The handler does not bound its index.
    BogusIndexedTargetBank1 RuntimeScriptF43B ; CONTROL_EXTENDED_JUMP_F435
    BogusIndexedTargetBank1 RuntimeScriptF441
    BogusIndexedTargetBank1 RuntimeScriptF447
.assert (* - BankStart) = $743B, error, "bank 1 indexed targets $F435 end"
; Observed at the bank-0 command fetcher during the opening scenarios.
; Names describe handler behaviour; independent entry points are retained.
RuntimeScriptF43B:
    BogusLoadSlotRecord $03, $FF ; CONTROL_RUNTIME_SCRIPT_F43B
RuntimeScriptF43E:
    BogusJumpBank1 (BankStart + $742D)
RuntimeScriptF441:
    BogusLoadSlotRecord $09, $FF
RuntimeScriptF444:
    BogusJumpBank1 (BankStart + $742D)
RuntimeScriptF447:
    BogusLoadSlotRecord $06, $FF
RuntimeScriptF44A:
    BogusJumpBank1 (BankStart + $742D)
.assert (* - BankStart) = $744D, error, "bank 1 runtime script $F43B end"
    .incbin "bank1_f44d_fc58.bin"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeFC58:
    SlotRuntimeRecord $BF6B, (CandidateFC6A - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_FC58
.assert (* - BankStart) = $7C61, error, "bank 1 slot record FC58 end"
; Possible contact-event record; its resource payload remains local.
ContactRecordFC61:
    SlotRuntimeRecord $BF61, (ContactScriptFC81 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_CONTACT_RECORD_FC61
.assert (* - BankStart) = $7C6A, error, "bank 1 contact record FC61 end"
; Candidate script path; object role and execution remain unverified.
CandidateFC6A:
    BogusSetDispatchCounter $03 ; CONTROL_BOGUS_FC6A
    BogusSetVoicePointers $2AD8, $0000, $0000, $0000
    BogusSetSlot07F0 $02
    BogusInitializeOtherSlotAbsolute $1F, $00, $91, $00
    BogusClearSlot0790Bits $01
CandidateFC7E:
    BogusJumpBank1 CandidateFC7E
.assert (* - BankStart) = $7C81, error, "bank 1 candidate script FC6A end"
; Possible contact-event entry. The fallthrough's record access has a
; competing candidate interpretation over the earlier FC6A script.
ContactScriptFC81:
    BogusBranchIfSelectedFieldEqual ContactScriptFC9F, $00 ; CONTROL_CONTACT_SCRIPT_FC81
    BogusLoadRecordAndClearSavedState $1A
.assert (* - BankStart) = $7C87, error, "bank 1 contact script FC81 end"
    .incbin "bank1_fc87_fc9f.bin"
ContactScriptFC9F:
    BogusWait $12 ; CONTROL_CONTACT_SCRIPT_FC9F
    BogusLoadSlotRecord $00, $01
    BogusJumpBank1 (BankStart + $7C7C)
.assert (* - BankStart) = $7CA7, error, "bank 1 contact script FC9F end"
; Candidate $FD05 walks these zero-terminated byte lists, selecting their base
; through CandidateListPointersFCE3. Each nonzero value occurs as a key in the
; $D27E remap table; actual list selection and the values' roles are unverified.
; The indexed load reads two bytes even on the final zero before masking low.
CandidateValuesFCA7:
    .byte $0E, $15, $11, $12, $1C, $1D, $1A, $1B, $2A, $2B, $18, $19, $00 ; CONTROL_CANDIDATE_VALUES_FCA7
CandidateValuesFCB4:
    .byte $4E, $4F, $3C, $3D, $3E, $3F, $42, $43, $44, $45, $48, $49, $4A, $4B, $00
CandidateValuesFCC3:
    .byte $68, $68, $68, $68, $68, $68, $68, $69, $69, $69, $69, $69, $69, $69, $00
CandidateValuesFCD2:
    .byte $2E, $2F, $30, $31, $32, $33, $34, $35, $36, $37, $23, $24, $38, $39, $56, $57, $00
.assert (* - BankStart) = $7CE3, error, "bank 1 candidate value lists end"
; These indexed entries are read by the candidate $FD05 script. The first
; table points to the value lists; the second contains palette pointers.
; The next byte sequence is also read as overlapping two-byte values, and a
; read near its end can include bytes of the following slot record.
CandidateListPointersFCE3:
    .word CandidateValuesFCA7 - BankStart, CandidateValuesFCA7 - BankStart, CandidateValuesFCB4 - BankStart, CandidateValuesFCC3 - BankStart, CandidateValuesFCD2 - BankStart ; CONTROL_CANDIDATE_LIST_POINTERS
CandidatePalettePointersFCED:
    .word $C7F2, $C7F2, $C805, $C7F2, $C818 ; CONTROL_CANDIDATE_PALETTE_POINTERS
CandidateStateValuesFCF7:
    .byte $00, $05, $28, $07, $1E ; CONTROL_CANDIDATE_STATE_VALUES
.assert (* - BankStart) = $7CFC, error, "bank 1 candidate indexed entries end"
; Descriptor-linked slot record; resource data remains local.
SlotRuntimeFCFC:
    SlotRuntimeRecord $BC79, (CandidateFD05 - BankStart), $00, $FF, $00, $00, $00 ; CONTROL_SLOT_RUNTIME_FCFC
.assert (* - BankStart) = $7D05, error, "bank 1 slot record FCFC end"
; Candidate script path; object role and execution remain unverified.
CandidateFD05:
    BogusSetSlotC0 $00 ; CONTROL_BOGUS_FD05
    BogusSetSlotValue $0002
    BogusMultiplySlotValueByArray $3D
    BogusStoreSlotValueArray $FF
    BogusLoadSlotValueIndexedBank1 CandidatePalettePointersFCED
    BogusSetSpritePalettePointer $0000
    BogusLoadSlotValueArray $FF
    BogusLoadSlotValueIndexedBank1 CandidateListPointersFCE3
CandidateFD19:
    BogusStoreSlotValueArray $FF
    BogusLoadSlotValueIndexedBank1 (BankStart + $0000)
    BogusMaskSlotValue $00FF
    BogusBranchIfSlotValueEqual CandidateFD3C, $00, $00
    BogusInitializeOtherSlotAbsolute $00, $04, $82, $00
    BogusWait $03
    BogusMarkMatchingSlots $28, $01, $00, $00
    BogusWait $1E
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $0001
    BogusJumpBank1 CandidateFD19
CandidateFD3C:
    BogusMarkMatchingSlots $80, $01, $1E, $00
    BogusWait $28
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueEqual (BankStart + $7D65), $04, $00
    BogusStoreSlotValueArray $FF
    BogusLoadSlotValueIndexedBank1 CandidateStateValuesFCF7
    BogusStoreSlotValueArray $3D
    BogusCallNativeEncoded $B51B
    BogusSaveStateAndPlaceSlots $10
.assert (* - BankStart) = $7D56, error, "bank 1 candidate script FD05 end"
; Possible resumed slot continuation after state restoration.
RestoreScriptFD56:
    BogusLoadSlotValueArray $FF ; CONTROL_RESTORE_SCRIPT_FD56
    BogusAddSlotValue $0001
    BogusBranchIfSlotValueEqual BranchScriptFD65, $05, $00
    BogusCallNativeEncoded $B51B
    BogusSetMainState $00
.assert (* - BankStart) = $7D65, error, "bank 1 restore candidate FD56 end"
; Candidate path from a literal branch target in maintained source.
; Independent entries are labelled; runtime reachability is not implied.
BranchScriptFD65:
    BogusCallNativeEncoded $B51B ; CONTROL_BRANCH_SCRIPT_FD65
BranchScriptFD68:
    BogusSetMainState $15
.assert (* - BankStart) = $7D6A, error, "bank 1 branch script $FD65 end"
    .incbin "bank1_fd6a_fd88.bin"
    BankScriptNativeCall
.assert (* - BankStart) = $7DA7, error, "bank 1 native script call end"
ScriptRecordLengths:
    ScriptTable 0
.assert (* - BankStart) = $7E6C, error, "bank 1 common helpers offset"
    BankHelpers
.assert (* - BankStart) = $7FB3, error, "bank 1 tail offset"
    BankTail $03C2, $03C3, "bank1_fff4_fffa.bin"
.assert (* - BankStart) = $8000, error, "bank 1 size"
.endscope

.segment "CHR"
    .incbin "chr.bin"             ; Local, unconverted graphics data.
