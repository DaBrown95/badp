; v1.3 keeps several operations inline that later releases share through JSR.
; These macros emit ordinary labelled instructions; preserve the native count
; and ordering at each call site, including shifts through the carry flag.
.macro LegacyShiftPairLeft lowOperand, highOperand
    asl lowOperand
    rol highOperand
.endmacro
.macro LegacyShiftPairRight highOperand, lowOperand
    lsr highOperand
    ror lowOperand
.endmacro
.macro LegacyRotatePairRight highOperand, lowOperand
    ror highOperand
    ror lowOperand
.endmacro
.macro LegacyShiftAccumulatorLeft4
    asl a
    asl a
    asl a
    asl a
.endmacro
.macro LegacyShiftAccumulatorRight4
    lsr a
    lsr a
    lsr a
    lsr a
.endmacro
.macro LegacyScalePositionByEight
    LegacyShiftPairLeft $11, $12
    LegacyShiftPairLeft $11, $12
    LegacyShiftPairLeft $11, $12
.endmacro
.macro LegacyStoreSlotPositionPair
    lda $70,x
    sta $0120,y
    lda $80,x
    sta $0121,y
.endmacro
.macro LegacyGetSecondOffset
    lda $B0,x
    clc
    adc ScrollTargetYLow
    sta $11
    lda ScrollTargetYHigh
    adc #$00
    sta $12
.endmacro
.macro LegacySetPpuSource
    lda $EA
    sta $FE
    lda $EB
    sta $FF
.endmacro
; Concrete accumulator/indexed forms keep the emitted addressing modes visible
; to the source inventory as well as the assembler.
.macro LegacyShiftAccumulatorLeftInto highOperand
    asl a
    rol highOperand
.endmacro
.macro LegacyShiftLowIntoAccumulator lowOperand
    asl lowOperand
    rol a
.endmacro
.macro LegacyShiftAccumulatorRightInto lowOperand
    lsr a
    ror lowOperand
.endmacro
.macro LegacyRotateAccumulatorRightInto lowOperand
    ror a
    ror lowOperand
.endmacro
.macro LegacyShiftIndexedPairRight highOperand, lowOperand
    lsr highOperand,x
    ror lowOperand,x
.endmacro
.macro LegacyShiftRightIntoIndexed highOperand, lowOperand
    lsr highOperand
    ror lowOperand,x
.endmacro
.macro LegacyModeGateReturnTail
    pla
    pla
    rts
.endmacro
.macro LegacyEncodedPointerAndByte pointer, field_value
    .word pointer
    .byte field_value
.endmacro
