; The unversioned $9B handler uses the complete little-endian RTS word.
; It pushes high then low and returns directly into that word plus one.
; No bank write or high-bit OR occurs here. Ordinary callers and their active
; mapping require the target's own script inventory.
.macro UnversionedDirectNativeCall
    lda RecordBuffer2 ; CONTROL_UNVERSIONED_DIRECT_NATIVE_CALL
    pha
    lda RecordBuffer1
    pha
    rts
.endmacro

; Byte5 is the high target byte of the six-byte $39 command.
UnversionedRecordBuffer5 = RecordBuffer0 + 5

; These three entries operate on the selected $42/$44 word pair. The $3A
; entry still uses the shared byte operation on $46. A zero addend uses the
; existing current-slot fallback; carry and the addend sign preserve the
; original saturation at $0000/$FFFF.
.macro UnversionedSelectedPairHandlers
UnversionedScriptOp37:
    lda RecordBuffer3 ; CONTROL_UNVERSIONED_SELECTED_PAIR_ADD
    sta $06
    lda RecordBuffer2
    sta $04
    jsr ScriptDefaultSearchFields
    jsr SelectScriptField
    bne UnversionedPair37Return
    lda $42,y
    clc
    adc $04
    sta $42,y
    lda $44,y
    adc $06
    sta $44,y
    ldx $06
    bmi UnversionedPair37Negative
    bcc UnversionedPair37Return
    lda #$FF
UnversionedPair37Clamp:
    sta $42,y
    sta $44,y
UnversionedPair37Return:
    rts
UnversionedPair37Negative:
    lda #$00
    bcc UnversionedPair37Clamp
    rts
UnversionedScriptOp38:
    jsr SelectScriptField
    bne UnversionedPair38Return
    lda RecordBuffer2 ; CONTROL_UNVERSIONED_SELECTED_PAIR_SET
    sta $42,y
    lda RecordBuffer3
    sta $44,y
UnversionedPair38Return:
    rts
UnversionedScriptOp39:
    jsr SelectScriptField
    bne UnversionedPair39Return
    sec
    lda $42,y ; CONTROL_UNVERSIONED_SELECTED_PAIR_COMPARE
    sbc RecordBuffer2
    lda $44,y
    sbc RecordBuffer3
    bcc UnversionedPair39Return
    lda RecordBuffer4
    sta RecordBuffer1
    lda UnversionedRecordBuffer5
    sta RecordBuffer2
    jmp ScriptSetPointerFromOperands
UnversionedPair39Return:
    rts
.endmacro

; Own native bodies and record lengths establish these word-valued forms.
; Their gameplay uses and source locations remain separate inventory work.
.macro UnversionedBogusAddSelectedPair selector, value
    .byte $37, selector
    .word value
.endmacro
.macro UnversionedBogusSetSelectedPair selector, value
    .byte $38, selector
    .word value
.endmacro
.macro UnversionedBogusBranchIfSelectedPairAtLeast target, selector, value
    .byte $39, selector
    .word value, target - $8000
.endmacro

; $57 writes the resolved word to the current slot's $90/$A0 fields.
; $58 continues to use the later family's array-comparison body.
.macro UnversionedSlotPair57
UnversionedScriptOp57:
    lda RecordBuffer1 ; CONTROL_UNVERSIONED_SLOT_PAIR_57
    sta $04
    lda RecordBuffer2
    sta $06
    jsr ScriptDefaultSearchFields
    lda $04
    sta $90,x
    lda $06
    sta $A0,x
    rts
.endmacro

; $5C preserves bits1-4 of the $03FE shadow and ORs the resolved operand.
; $5D retains the existing per-slot $07F0 flag operation.
.macro UnversionedShadowMask5C
UnversionedScriptOp5C:
    lda RecordBuffer1 ; CONTROL_UNVERSIONED_SHADOW_MASK_5C
    jsr ScriptOperandOrSlot
    sta RecordBuffer1
    lda $03FE
    and #$1E
    ora RecordBuffer1
    sta $03FE
    rts
.endmacro

; $8D/$8E store the current slot word into the selected $42/$44 pair.
; $8F retains the existing byte-swap body.
.macro UnversionedSelectedPair8D
UnversionedScriptOp8DTo8E:
    jsr SelectScriptField
    bne ScriptIndirectReturn
    lda $70,x ; CONTROL_UNVERSIONED_SELECTED_PAIR_8D
    sta $42,y
    lda $80,x
    sta $44,y
    rts
.endmacro

; $6D configures split-screen state with NMI disabled, then enables NMI.
; A negative fourth operand also reads the state bank-selector byte; this is
; a second consumer of the same physical table, not separate storage.
.macro UnversionedSplit6D
UnversionedScriptOp6D:
    lda RecordBuffer4            ; CONTROL_UNVERSIONED_SPLIT_6D
    bpl UnversionedSplit6DReady
    ldy $01
    lda StateBankSelectors,y
    sta RecordBuffer4
UnversionedSplit6DReady:
    lda $03FF
    sta PPUCTRL
    jsr ConfigureSplitScreen
    lda $03FF
    ora #$80
    sta PPUCTRL
    rts
.endmacro

; Separate deferred PPU commands. These entries share queue state with $6E/$6F
; but are not aliases of the later revisions' arithmetic/slot operations.
.macro UnversionedQueue70
UnversionedScriptOp70:
    lda $E7                      ; CONTROL_UNVERSIONED_QUEUE_70
    bne ScriptWaitForState
    lda RecordBuffer1
    sta $E8
    jsr ScriptGetSlotPointer
    clc
    adc #$02
    sta $EA
    tya
    adc #$00
    sta $EB
    lda #$70
    sta $E4
    lda #$08
    sta $E7
    rts
.endmacro

.macro UnversionedQueue74
ScriptOp74:
    lda $E7                      ; CONTROL_UNVERSIONED_QUEUE_74
    bne UnversionedQueueWait
    jsr SelectScriptField
    bne ScriptOp73Return
    sty $EA
    lda RecordBuffer2
    sta $E8
    lda RecordBuffer3
    sta $E9
    lda RecordBuffer4
    sta $E3
    lda #$74
    sta $E4
    lda #$05
    sta $E7
    rts
UnversionedQueueWait:
    jmp ScriptWaitForState
.endmacro

.macro UnversionedQueue75
UnversionedScriptOp75:
    lda $E7                      ; CONTROL_UNVERSIONED_QUEUE_75
    bne UnversionedQueueWait
    lda RecordBuffer1
    sta $E8
    lda RecordBuffer2
    sta $E9
    lda RecordBuffer3
    sta $E3
    lda #$75
    sta $E4
    lda $70,x
    sta $EA
    lda $80,x
    sta $EB
    lda #$05
    sta $E7
    rts
.endmacro

; $7C queues alternating rows while waiting for the NMI queue between writes.
; It finally waits for $0380 and enters the shared $0F slot operation.
.macro UnversionedRows7C
UnversionedScriptOp7C:
    lda #$00                     ; CONTROL_UNVERSIONED_ROWS_7C
    sta $03
    sta $05
    sta $04
    lda #$1D
    sta $06
UnversionedRowsWait:
    lda $E7
    bne UnversionedRowsWait
    ldy $04
    lda $05
    beq UnversionedRowsSelect
    ldy $06
UnversionedRowsSelect:
    sty $E8
    lda $03
    sta $E3
    lda #$40
    sta $EA
    lda #$00
    sta $E9
    lda #$6F
    sta $E4
    lda #$20
    sta $E7
    lda $03
    eor #$01
    sta $03
    bne UnversionedRowsWait
    lda $05
    eor #$01
    sta $05
    bne UnversionedRowsWait
    inc $04
    dec $06
    lda $06
    cmp #$0F
    bcs UnversionedRowsWait
UnversionedRowsFinishWait:
    lda $E7
    bne UnversionedRowsFinishWait
    lda $0380
    bne UnversionedRowsFinishWait
    jsr StopAllAudioVoices
    ldy #$00
    ldx $10
    jmp ScriptOp0F
.endmacro

; Nonzero $03B8 enters this split-screen PPU sequence. The ordinary scroll path
; skips it and joins ApplyNmiPpuCtrl. Preserve the incoming X in both polling
; timeouts, the PPU latch/status reads, mapper call, fallback and exact delay.
; Labels describe hardware operations; observed raster timing is not claimed.
.macro UnversionedNmiSplitSequence
UnversionedNmiSplit:
    lda PPUSTATUS
    lda #$27                     ; CONTROL_UNVERSIONED_NMI_SPLIT
    sta PPUADDR
    lda #$A0
    sta PPUADDR
    lda #$FE
    sta PPUDATA
    lda $03BE
    ldy $03BF
    jsr SwitchBank
    lda $03FF
    and #$E7
    ora $03BB
    sta $03FF
    and #$FE
    sta PPUCTRL
    lda $03FE
    sta PPUMASK
    lda #$FF
    sta PPUSCROLL
    lda $03B8
    clc
    adc $03BC
    sta PPUSCROLL
    ldy #$0A
    lda #$40
UnversionedNmiWaitHitClear:
    bit PPUSTATUS
    beq UnversionedNmiWaitHitSet
    dex
    bne UnversionedNmiWaitHitClear
    dey
    bne UnversionedNmiWaitHitClear
    jmp UnversionedNmiSplitDelay
UnversionedNmiWaitHitSetSetup:
    ldy #$0A
UnversionedNmiWaitHitSet:
    bit PPUSTATUS
    bne UnversionedNmiSplitDelay
    dex
    bne UnversionedNmiWaitHitSet
    dey
    bne UnversionedNmiWaitHitSet
UnversionedNmiSplitDelay:
    ldx $03E6
UnversionedNmiSplitDelayLoop:
    dex
    bne UnversionedNmiSplitDelayLoop
    lda $03FC
    sta PPUSCROLL
    lda $03FD
    sta PPUSCROLL
.endmacro

; A non-FF 9D operand sets bit $20 of the own C0 slot field; FF clears it.
; Later versions retain the command length while replacing its body with RTS.
.macro UnversionedSlotFlag9D
ScriptOp9D:
    lda $C0,x                    ; CONTROL_UNVERSIONED_SLOT_FLAG_9D
    and #$DF
    ldy RecordBuffer1
    cpy #$FF
    beq UnversionedSlotFlag9DStore
    ora #$20
UnversionedSlotFlag9DStore:
    sta $C0,x
UnversionedSlotFlag9DReturn:
    rts
.endmacro

; B4 conditionally negates each stored motion field. B5 keeps the shared
; coordinate getter, so the two nominal entries have separate native bodies.
.macro UnversionedNegateFieldsB4
UnversionedScriptOpB4:
    lda RecordBuffer1            ; CONTROL_UNVERSIONED_NEGATE_B4
    cmp #$FF
    beq UnversionedNegateSecondB4
    lda $04F0,x
    jsr NegateA
    sta $04F0,x
UnversionedNegateSecondB4:
    lda RecordBuffer2
    cmp #$FF
    beq UnversionedNegateReturnB4
    lda $0500,x
    jsr NegateA
    sta $0500,x
UnversionedNegateReturnB4:
    rts
.endmacro
