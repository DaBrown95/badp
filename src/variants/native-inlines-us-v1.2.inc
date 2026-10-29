; Earlier forms shared with the v1.3 source. These emit native operations,
; preserving original ordering, flags, stack effects and addressing modes.
.macro V12RestoreDefaultBankInline
    lda DefaultBankValue
    ldy DefaultBankIndex
    sta BankValues,y
.endmacro

; The PPU-control tail retains a call to the standalone mapper helper.
.macro V12RestoreDefaultBankByCall
    lda DefaultBankValue
    ldy DefaultBankIndex
    jsr SwitchBank
    rts
.endmacro

.macro V12InitialMapTilePosition
    lda ScrollTargetXLow
    sta MapTileXLow
    lda ScrollTargetXHigh
    sta MapTileXHigh
    LegacyShiftPairRight MapTileXHigh, MapTileXLow
    LegacyShiftPairRight MapTileXHigh, MapTileXLow
    LegacyShiftPairRight MapTileXHigh, MapTileXLow
    lda ScrollTargetYLow
    sta MapTileY
    lda ScrollTargetYHigh
    LegacyShiftAccumulatorRightInto MapTileY
    LegacyShiftAccumulatorRightInto MapTileY
    LegacyShiftAccumulatorRightInto MapTileY
    rts
.endmacro

.macro V12ReadScrollXTileCoordinate
    ldx ScrollCurrentXLow
    ldy ScrollCurrentXHigh
    jsr ShiftXYRight3
.endmacro
.macro V12ReadScrollYTileCoordinate
    ldx ScrollCurrentYLow
    ldy ScrollCurrentYHigh
    jsr ShiftXYRight3
.endmacro

; The loop exhaustion jumps over this PLA. Its original purpose and an
; ordinary entry to the pop remain unproven; it is not another whole routine.
.macro V12AudioShadowReturnTail
    jmp StopAudioVoiceReturn
StopAudioConditionalPopReturn:
    pla
.endmacro

; Two map-state callers use a separate unrolled copy, while the generic
; coordinate helper retains its three JSRs. Preserve both implementations.
.macro V12MainShiftXYRight3
    .repeat 3
        tya
        lsr a
        tay
        txa
        ror a
        tax
    .endrepeat
    rts
.endmacro

; This secondary-bank fragment mirrors the bank-0 gate's branch and return
; at the same CPU addresses. Ordinary bank-1 entry and purpose are unproven.
.macro V12ModeGateReturnTail
    .local returnReady
    bne returnReady
    pla
    pla
returnReady:
    rts
.endmacro
