.setcpu "6502"
.include "nes.inc"

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
    lda $FDA7,x
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
    jsr $8C66
    jsr InitializeEngineSlots
    jsr $CA5D
    jsr EnablePpuNmi
MainLoop:
    jsr $CA9E
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

; Each carry bit dispatches to one engine handler. Their button names and
; effects are not assumed until the handler paths are traced.
DispatchControllerChanges:
    lda $038F
    and $038D
    beq FrameEngineWork
    ror $038F
    bcc ControllerHandler1Done
    jsr $FCC0
ControllerHandler1Done:
    ror $038F
    bcc ControllerHandler2Done
    jsr $FCA4
ControllerHandler2Done:
    ror $038F
    bcc ControllerHandler3Done
    jsr $FC96
ControllerHandler3Done:
    ror $038F
    bcc ControllerHandler4Done
    jsr $FCDC
ControllerHandler4Done:
    ror $038F
    bcc ControllerHandler5Done
    jsr $FC74
ControllerHandler5Done:
    ror $038F
    bcc ControllerHandler6Done
    jsr $FC2F
ControllerHandler6Done:
    ror $038F
    bcc ControllerHandler7Done
    jsr $FC03
ControllerHandler7Done:
    ror $038F
    bcc FrameEngineWork
    jsr $FBD8
FrameEngineWork:
    lda a:$28                    ; Original uses absolute addressing for $0028.
    bne RestoreNmiState
    jsr $F48A
    jsr $95D1
    jsr $9414
    lda $03F2
    bne SkipFrameRoutine
    jsr $8F10
SkipFrameRoutine:
    jsr $8FBA
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

    .incbin "bank0_840a_8420.bin"

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

    .incbin "bank0_844b_8480.bin"
; Clear five eight-byte entries in the $04B0 state array.
InitializeEngineSlots:
    lda #$00
    sta $03FB
    tax
ClearEngineSlotBytes:
    sta $04B0,x
    inx
    cpx #$28                     ; CONTROL_SLOT_INIT
    bne ClearEngineSlotBytes
    rts
.assert (* - BankStart) = $048F, error, "bank 0 engine slot initializer size"

    .incbin "bank0_848f_85b7.bin"
; Writes the PPUCTRL mirror with the NMI bit set; the mirror itself is not
; updated here. This routine is a shared tail return from the NMI frame work.
EnablePpuNmi:
    lda $03FF
    ora #$80                     ; CONTROL_ENABLE_NMI
    sta PPUCTRL
    rts
.assert (* - BankStart) = $05C0, error, "bank 0 NMI enable routine size"

    .incbin "bank0_85c0_9e97.bin"
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

    .incbin "bank0_9efa_fe6c.bin"
.assert (* - BankStart) = $7E6C, error, "bank 0 common helpers offset"
    BankHelpers
.assert (* - BankStart) = $7FB3, error, "bank 0 tail offset"
    BankTail $03C0, $03C1, "bank0_fff4_fffa.bin"
.assert (* - BankStart) = $8000, error, "bank 0 size"
.endscope

.segment "PRG1"
.scope Bank1
BankStart:
    .incbin "bank1_8000_fe6c.bin"
.assert (* - BankStart) = $7E6C, error, "bank 1 common helpers offset"
    BankHelpers
.assert (* - BankStart) = $7FB3, error, "bank 1 tail offset"
    BankTail $03C2, $03C3, "bank1_fff4_fffa.bin"
.assert (* - BankStart) = $8000, error, "bank 1 size"
.endscope

.segment "CHR"
    .incbin "chr.bin"             ; Local, unconverted graphics data.
