; v1.3 reset-state dispatcher and mapper pulse sequence, CPU $8011-$806F.
; Included after the common Boot prefix; InitializeGame follows this block.
; Self-addressed ROM stores preserve the original bus-conflict operands.
CheckResetState:
    lda $04DE
    eor $04DF
    cmp #$FF ; CONTROL_STATE_DISPATCH
    beq ResetStateValid
SelectReset8A:
    lda #$8A
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence8A
ResetStateValid:
    lda $04DE
    cmp #$0A
    beq ResetSequence8A
    cmp #$0B
    beq ResetSequence8B
    cmp #$8A
    bne SelectReset8A
    lda #$8B
    sta $04DE
    eor #$FF
    sta $04DF
    jmp ResetSequence8B
ResetSequence8A:
    jsr PulseMapper08Then00
    jsr PulseMapper08Then00
    jmp InitializeGame
ResetSequence8B:
PulseReset8B:
    lda #$0C
    sta PulseReset8B+1
    jmp InitializeGame
PulseMapper08Then00:
PulseMapper08:
    lda #$08
    sta PulseMapper08+1
    jsr ResetDelayMedium
PulseMapper00:
    lda #$00
    sta PulseMapper00+1
    jmp ResetDelayMedium
ResetDelayMedium:
    ldy #$04
    ldx #$3A
ResetDelayLoop:
    dex
    bne ResetDelayLoop
    dey
    bne ResetDelayLoop
    rts
