.setcpu "6502"
.include "nes.inc"

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

    .incbin "bank0_9efa_d54e.bin"
; Fetch the next variable-length command, advance the script pointer by the
; fetched length and dispatch its opcode. The surrounding loop and many
; handlers remain unconverted, so their semantics are not assumed here.
ScriptLoopContinue = BankStart + $5543
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
    jmp $EBBB
ScriptCountNonnegative:
    dec $48
    bpl ScriptLoopContinue
    jmp $EBBB
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
    lda $61
    jmp $F0D8

ScriptPushZeroAndCall:
    lda #$00
    sta $57
    lda $2A
    jsr $F2A0
    lda #$00
    pha
    jmp $F0DC

; Opcodes $01 and $A3 share this handler. It compares values returned by
; $F357 with per-slot coordinates and command-provided limits. The $A3 variant
; also accepts the opposite orientation before setting the script pointer.
ScriptOp01OrA3:
    jsr $F357
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
    jsr $9E91
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
    jsr $9E91
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
    jsr $9E91
    tay
    ldx #$00                     ; CONTROL_SCRIPT_OP02
    jsr $F424
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
    jsr $9E91
ScriptOp03DirectionReady:
    tax
    ldy #$02                     ; CONTROL_SCRIPT_OP03
    jsr $F424
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
    jsr $F3CA
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
    jsr $F057                    ; CONTROL_SCRIPT_OP08
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
; paths depend on the unconverted $8A4C routine; retain the original tests.
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
    jsr $8A4C
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
    jsr $EBAC
    lda $3E,y                    ; CONTROL_SCRIPT_OP11
    sta $61
    lda #$00
    sta $62
    sta $3E,y
ScriptApplyOperandPair:
    jsr $F066
    jmp ScriptYieldIfNonnegative
ScriptOp12:
    jsr $EBAC
    lda $40,y                    ; CONTROL_SCRIPT_OP12
    sta $62
    lda #$00
    sta $61
    sta $40,y
    jmp ScriptApplyOperandPair
ScriptOp13:
    jsr $EBAC
    lda #$00
    sta $3E,y                    ; CONTROL_SCRIPT_OP13
    rts
ScriptOp14:
    jsr $EBAC
    lda #$00
    sta $40,y                    ; CONTROL_SCRIPT_OP14
    rts
ScriptOp15:
    jsr $EBAC
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
    jmp $F10C

; Fetch a record using the caller's X, restore the current slot's pointer, and
; return a pointer to the copied record in $FE/$FF, set to $0060.
ScriptFetchRecordAndRestorePointer:
    jsr FetchVariableRecord
    ldx $10
    jsr ScriptLoadSlotPointer
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
    jsr $8D95
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
    jmp $F479

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
    jsr $CC88
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
    jsr ScriptSaveSlotPointer
    lda $10
    pha
    sty $10
    lda #$FF
    sta $07B0,y
    jsr $CF02
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
    jsr $CC87
    clc
    adc $FE
    rts
ScriptOp25:
    lda $0500,x                   ; CONTROL_SCRIPT_OP25
    bpl ScriptOp25FirstReady
    jsr $9E91
ScriptOp25FirstReady:
    sta $05
    lda $0510,x
    bpl ScriptOp25SecondReady
    jsr $9E91
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
    jsr $8D8B
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
    jsr $F05C                     ; CONTROL_SCRIPT_OP2D
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
    jsr $EBAC                     ; CONTROL_SCRIPT_OP33
    lda $3E,y
    sta $61
    lda #$FF
    sta $62
    lda #$00
    sta $3E,y
ScriptCallF061AndYield:
    jsr $F061
    jmp ScriptYieldIfNonnegative
ScriptOp34:
    jsr $EBAC                     ; CONTROL_SCRIPT_OP34
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
    jsr $D4DA
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
    jsr $D4DA
    pla
    sta $06B0,x
ScriptOp36ScanNext:
    iny
    cpy #$10
    bne ScriptOp36ScanLoop
    rts
.assert (* - BankStart) = $5CD4, error, "bank 0 script handlers through opcode $36"

    .incbin "bank0_dcd4_fda7.bin"
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
