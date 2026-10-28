; v1.4 reset-state dispatcher and mapper pulse sequences, CPU $8011-$8164.
; Included after the common Boot prefix; InitializeGame follows this block.
; The self-addressed stores target their own ROM immediate operands. Preserve
; those addresses, values, ordering and delay loops, including the $00 counter.
CheckResetState:
    lda $04DE
    eor $04DF
    cmp #$FF ; CONTROL_STATE_DISPATCH
    beq ResetStateValid
ResetSelect83Trampoline:
    jmp SelectReset83
ResetStateValid:
    lda $04DE
    cmp #$03 ; CONTROL_V14_RESET_STATE
    beq ResetSelect83Trampoline
    cmp #$04
    beq ResetSelect83Trampoline
    cmp #$05
    beq SelectReset85
    cmp #$06
    beq SelectReset85
    cmp #$07
    beq SelectReset85
    cmp #$08
    beq SelectReset85
    cmp #$09
    beq SelectReset85
    cmp #$0A
    beq SelectReset85
    cmp #$0B
    beq SelectReset8A
    cmp #$83
    beq SelectReset84
    cmp #$84
    beq SelectReset85
    cmp #$85
    beq SelectReset86
    cmp #$86
    beq SelectReset87
    cmp #$87
    beq SelectReset88
    cmp #$88
    beq SelectReset89
    cmp #$89
    beq SelectReset8A
    cmp #$8A
    beq SelectReset8B
    jmp ResetSelect83Trampoline
SelectReset83:
    lda #$83
    jsr StoreResetState
    jmp ResetSequence83
StoreResetState:
    sta $04DE
    eor #$FF
    sta $04DF
    rts
SelectReset84:
    lda #$84
    jsr StoreResetState
    jmp ResetSequence84
SelectReset89:
    lda #$89
    jsr StoreResetState
    jmp ResetSequence89
SelectReset8A:
    lda #$8A
    jsr StoreResetState
    jmp ResetSequence8A
SelectReset8B:
    lda #$8B
    jsr StoreResetState
    jmp ResetSequence8B
SelectReset85:
    lda #$85
    jsr StoreResetState
    jmp ResetSequence85
SelectReset86:
    lda #$86
    jsr StoreResetState
    jmp ResetSequence86
SelectReset87:
    lda #$87
    jsr StoreResetState
    jmp ResetSequence87
SelectReset88:
    lda #$88
    jsr StoreResetState
    jmp ResetSequence88
ResetSequence83:
PulseReset83X:
    ldx #$0C
PulseReset83Y:
    ldy #$04
    sty PulseReset83Y+1
    stx PulseReset83X+1
    jmp InitializeGame
ResetSequence84:
    jsr PulseMapper0C04
    jsr PulseMapper0C04
    jmp InitializeGame
ResetSequence85:
    jsr PulseMapper0C
    jsr ResetDelayShort
ResetSequence89:
PulseReset89X:
    ldx #$0C
PulseReset89Y:
    ldy #$08
    sty PulseReset89Y+1
    stx PulseReset89X+1
    jmp InitializeGame
ResetSequence86:
    jsr PulseMapper0C
    jsr ResetDelayMedium
    jmp ResetSequence89
ResetSequence87:
    jsr PulseMapper0C
    jsr ResetDelayMedium
    jsr ResetDelayMedium
    jmp ResetSequence89
ResetSequence88:
    jsr PulseMapper0C
    jsr ResetDelayMedium
    jsr ResetDelayMedium
    jsr ResetDelayMedium
    jmp ResetSequence89
PulseMapper0C:
    jsr PulseMapper0C04
PulseMapper0CY:
    ldy #$0C
    sty PulseMapper0CY+1
    rts
ResetSequence8A:
PulseReset8A08:
    lda #$08
    sta PulseReset8A08+1
    jsr ResetDelayLong
PulseReset8A0C:
    lda #$0C
    sta PulseReset8A0C+1
    jmp InitializeGame
ResetSequence8B:
    lda #$0F
; BUG: the loaded $0F is not stored as a loop count. The loop decrements the
; pre-existing zero-page $00 instead; retain the unused load and exact stores.
ResetSequence8BLoop:
PulseReset8B08:
    ldx #$08
    stx PulseReset8B08+1
    jsr ResetDelayMedium
PulseReset8B0C:
    ldx #$0C
    stx PulseReset8B0C+1
    jsr ResetDelayLong
    dec $00 ; CONTROL_V14_RESET_COUNTER
    bne ResetSequence8BLoop
    jmp InitializeGame
PulseMapper0C04:
PulseMapper0C04High:
    lda #$0C
    sta PulseMapper0C04High+1
    jsr ResetDelayMedium
PulseMapper0C04Low:
    lda #$04
    sta PulseMapper0C04Low+1
    jmp ResetDelayMedium
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
    ldy #$40
    ldx #$48
ResetDelayLongLoop:
    dex
    bne ResetDelayLongLoop
    dey
    bne ResetDelayLongLoop
    rts
