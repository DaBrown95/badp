; v1.2 mapper pulse/reset prefix, CPU $8011-$803D.
; Boot falls through here; InitializeGame begins at $803E. The three ROM
; constants are explicit mapper-write operands, skipped by the startup JMP.
; They are data, not three more instructions or an inferred extra routine.
MapperResetSequence:
    jsr PulseMapper08Then00
    jsr PulseMapper08Then00
    lda #$0C                     ; CONTROL_V12_RESET_MAPPER_VALUE
    sta MapperConflict0C
    jmp InitializeGame
PulseMapper08Then00:
    lda #$08
    sta MapperConflict08
    jsr ResetDelayMedium
    lda #$00
    sta MapperConflict00
    jsr ResetDelayMedium
    rts
ResetDelayMedium:
    ldy #$04
    ldx #$3A
ResetDelayLoop:
    dex
    bne ResetDelayLoop
    dey
    bne ResetDelayLoop
    rts
MapperConflict00:
    .byte $00
MapperConflict08:
    .byte $08
MapperConflict0C:
    .byte $0C
