.setcpu "6502"
.include "nes.inc"

; Record layout is established by $F0D8 and the slot initializer at $CF84.
.macro SlotDescriptor record_pointer, field_05d0, field_0610, field_05e0, field_0520
    .word record_pointer
    .byte field_05d0, field_0610, field_05e0, field_0520
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

    .incbin "bank0_85c0_867f.bin"
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
    lda #$DE
    clc
    adc $F0
    sta $F0
    lda #$A1
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

    .incbin "bank0_872f_8a4c.bin"
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

    .incbin "bank0_8c72_8d7d.bin"
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

    .incbin "bank0_8db7_9e3c.bin"
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

    .incbin "bank0_9efa_9f06.bin"
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

    .incbin "bank0_a1de_cc82.bin"
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

    .incbin "bank0_cc8c_cf02.bin"
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

    .incbin "bank0_d002_d4da.bin"
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
    jsr $8D14
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
    jsr $D2F8
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
; that slot selected, and restores the current slot's pointer. $D002 is still
; unconverted, so do not assume how the destination slot is selected.
ScriptOp1F:
    jsr $D002                     ; CONTROL_SCRIPT_OP1F
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
    jmp $8CB7
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

; Opcode $31 processes four pairs of operands. A $FF second byte skips the
; pair; other meanings depend on the unconverted routines at $848F and $844B.
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
    jsr $848F
    lda $12
    beq ScriptOp31Next
    tay
    lda $11
    tax
    lda $03
    jsr $844B
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
    jsr $848F
ScriptOp50:
    lda $62                      ; CONTROL_SCRIPT_OP50
    beq ScriptOp49Return
    cmp #$FF
    beq ScriptOp49Return
    tay
    lda $61
    tax
    lda #$04
    jsr $844B
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
    jmp $CCE3
ScriptOp4DPair:
    jsr ScriptResolvePair
    jmp $CCEC
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
    jmp $CCCB
ScriptOp4EPair:
    jsr ScriptResolvePair
    jmp $CCD4
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

; Opcode $61 prepares another slot similarly to $1F. The unresolved $D002
; routine decides whether a destination is available; the two callers share
; the save, initialization and restore sequence beginning at $DAB7.
ScriptOp61:
    jsr $D002                    ; CONTROL_SCRIPT_OP61
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

; Opcode $77 examines up to four operands through $8507. The helper discards
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
    jsr $8507
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
    jsr $D2F8
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
    jsr $890A
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
    jsr $EAF6
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
    jmp $FD88                    ; CONTROL_SCRIPT_OP9B
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
    jmp $CC8C
ScriptOpAANonnegative:
    jmp $CC95

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
    jsr $D0B3                     ; CONTROL_SCRIPT_OPB4
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
    jsr $CD93                     ; CONTROL_SCRIPT_OPC3
    rts
ScriptOpC4:
    lda $10                       ; CONTROL_SCRIPT_OPC4
    jsr $8C72
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

    .incbin "bank0_eaf6_eb8b.bin"
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
    jsr $D067
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

; Apply the two direction bits via the still-unconverted $8D32/$8D59 paths.
SyncSlotDirection:
    ldx $10                       ; CONTROL_SYNC_SLOT_DIRECTION
    lda $0660,x
    and #$80
    tax
    lda $10
    jsr $8D32
    ldx $10
    lda $0660,x
    and #$40
    tax
    lda $10
    jsr $8D59
    ldx $10
SyncSlotDirectionReturn:
    rts
.assert (* - BankStart) = $6F68, error, "bank 0 slot direction helpers end"


; Derive a 16-bit value from $0700 and $03EE/$03EF, then shift it right by
; three. $D0B3 is still unconverted and its return in $11 is saved to $04.
ComputeSlotScaledPosition:
    jsr $D0B3                     ; CONTROL_SLOT_SCALED_POSITION
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

; Temporarily mark the slot inactive while $87FA attempts to load the record.
SlotRecordAllocate:
    lda $04E0,x                  ; CONTROL_SLOT_RECORD_ALLOCATE
    pha
    lda #$FF
    sta $04E0,x
    txa
    jsr $8C72
    ldy $FF
    ldx $FE
    lda $10
    jsr $87FA
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
    jsr $890A
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
    jsr $8CED
SlotRecordApplyBit40:
    lda $11
    and #$40
    beq SlotRecordFinish
    lda $10
    jsr $8D6F
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
    lda $0590,x
    clc
    adc $0560,x
    sta $B0,x
    dec $B0,x
    rts
.assert (* - BankStart) = $748A, error, "bank 0 slot coordinate helpers end"

    .incbin "bank0_f48a_fd29.bin"
; Opcode $18 invokes the same two unconverted $84xx routines used by $49.
ScriptOp18:
    lda #$04                     ; CONTROL_SCRIPT_OP18
    jsr $848F
    ldx #$C8
    ldy #$26
    lda #$04
    jsr $844B
    rts
.assert (* - BankStart) = $7D38, error, "bank 0 script handler opcode $18"

    .incbin "bank0_fd38_fda7.bin"
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
    .incbin "bank1_8000_fda7.bin"
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
