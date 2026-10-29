; Own compact/normal slot records and connected scripts, AA45-B77B.
; Resource words resolve to the independently reconstructed bank0 animation
; or frame boundaries. Script words use this release's encoded namespace.
; Record lookahead and conditional saved-pointer/record modes retain their
; separate meanings; source names do not prove ordinary reachability.
.macro UnversionedAddSelectedByte selector, value
    .byte $3A, selector, value
.endmacro
.macro UnversionedReadSelectedByte selector
    .byte $73, selector
.endmacro
.macro UnversionedBank1OpeningScripts
UnversionedCompactAA45:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation032, $00
UnversionedRecordAA48:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame090, (UnversionedScriptAAEA - BankStart), $40, $FF, $00, $00, $00 ; CONTROL_UNVERSIONED_PREFIX_AA48
UnversionedRecordAA51:
    SlotRuntimeRecord $FFFF, (UnversionedScriptAB44 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordAA5A:
    SlotRuntimeRecord $FFFF, (UnversionedScriptACC5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordAA63:
    SlotRuntimeRecord $FFFF, (UnversionedScriptAEC4 - BankStart), $13, $FF, $00, $00, $00
UnversionedRecordAA6C:
    SlotRuntimeRecord $FFFF, (UnversionedScriptACFE - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordAA75:
    SlotRuntimeRecord $FFFF, (UnversionedScriptAD90 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordAA7E:
    SlotRuntimeRecord $FFFF, (UnversionedScriptAE8D - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordAA87:
    SlotRuntimeRecord $FFFF, (UnversionedScriptAE66 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordAA90:
    SlotRuntimeRecord $FFFF, (UnversionedScriptAB02 - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordAA99:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame090, $FFFF, $40, $FF, $00, $00, $00
UnversionedRecordAAA2:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame100, $FFFF, $40, $FF, $00, $00, $00
UnversionedRecordAAAB:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation037, $FFFF, $23, $FF, $00, $00, $00
UnversionedRecordAAB4:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation030, $FFFF, $23, $FF, $00, $00, $00
UnversionedRecordAABD:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation032, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordAAC6:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation031, $FFFF, $13, $FF, $00, $00, $00
UnversionedRecordAACF:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame107, $FFFF, $23, $FF, $00, $00, $00
UnversionedRecordAAD8:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame107, $FFFF, $23, $FF, $00, $00, $00
UnversionedRecordAAE1:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame104, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptAAEA:
    BogusSetDispatchCounter $8F ; CONTROL_UNVERSIONED_PREFIX_AAEA
    BogusBranchIfMatchingSlotReady UnversionedScriptB590, $01, $01, $00
    BogusSetSlotAssociation $00
    BogusClearSelected3E
    BogusClearSelected40
    BogusSetSlot0640Pair $01, $00
    BogusSetSelectedState15 $36
    BogusInitializeOtherSlotAbsolute $03, $FF, $C0, $00
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptAB02:
    BogusSetDispatchCounter $0A
    BogusSetSlot0670Pair $04, $40
    BogusSetSlot07F0 $14
    BogusClearSlot0790Bits $BF
    BogusSetSlotC0 $FF
    BogusSetSlot0640Pair $01, $00
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptAB1C, $FFFF
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAAB - BankStart)
    BogusJumpBank1 UnversionedScriptAB1F
UnversionedScriptAB1C:
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAB4 - BankStart)
UnversionedScriptAB1F:
    BogusApplyAndClearSelected3E
    BogusSetDispatchCounter $04
    BogusBranchIfSlotFieldsWithin UnversionedScriptAB30, $07, $FF
    BogusSetSlot0360 $06
    BogusBranchIfSelectedFlags UnversionedScriptAB3C, $40
    BogusSetSlot05F0Pair $24, $FF
UnversionedScriptAB30:
    BogusBranchIfSlot0360AtMost UnversionedScriptAB3A, $01
    BogusApplyAndClearSelected3E
    BogusBranchIfSlot0620Bit10 UnversionedScriptAB1F
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAB3A:
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptAB3C:
    BogusSetSlot05F0Pair $3C, $FF
    BogusBranchIfSlot0620Bit10 UnversionedScriptAB1F
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAB44:
    BogusSetDispatchCounter $09
    BogusLoadSlotValueArray $29
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusReadSlotValue $21
    BogusSubtractSlotPriorityFromField0520
    BogusReadSlotValue $24
    BogusBranchIfSlotValueEqual UnversionedScriptABD8, $07, $00
    BogusLoadSlotRecord $03, $FF
    BogusMarkRelatedSlotAtDepth $18, $01
    BogusSetDispatchCounter $05
    BogusBranchIfSlotD0BitsClear UnversionedScriptAB66, $80
    BogusSetSlotC0 $FF
    BogusClearSlotD0Bits $80
UnversionedScriptAB66:
    BogusSetDispatchCounter $02
    BogusReadSlotValue $24
    BogusLookupSlotValue ; CONTROL_UNVERSIONED_PREFIX_AB6A
    BogusLookupCaseBank1 UnversionedScriptAB8F, $0001
    BogusLookupCaseBank1 UnversionedScriptAC02, $0004
    BogusLookupCaseBank1 UnversionedScriptACA0, $0005
    BogusLookupCaseBank1 UnversionedScriptABAF, $0006
    BogusLookupEnd
    BogusSetDispatchCounter $06
    BogusReadSlotValue $01
    BogusMaskSlotValue $0003
    BogusBranchIfSlotValueEqual UnversionedScriptAB8F, $00, $00
    BogusSetLinkedSlotFieldsC0 $18, $00
    BogusJumpBank1 UnversionedScriptAB9F
UnversionedScriptAB8F:
    BogusSetDispatchCounter $85
    BogusSetLinkedSlotFieldsC0 $60, $A0
    BogusSetSlot05F0Pair $24, $FF
    BogusBranchIfAbsSlot0700Below UnversionedScriptABA6, $18
UnversionedScriptAB9B:
    BogusBranchIfSlot0520AtMost UnversionedScriptAC3C, $00
UnversionedScriptAB9F:
    BogusRestartVoice4 $27B4
    BogusWait $06
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptABA6:
    BogusSetSlotFields80 $00, $FF
    BogusSetSlotFields40Signed $60, $00
    BogusJumpBank1 UnversionedScriptAB9B
UnversionedScriptABAF:
    BogusSetDispatchCounter $82
    BogusSetSlot05F0Pair $40, $FF
    BogusRestartVoice4 $2694
    BogusSetLinkedSlotFieldsC0 $60, $D0
    BogusBranchIfAbsSlot0700Below UnversionedScriptABA6, $18
    BogusAddSlotFields00 $00, $F0
    BogusAddSlotFields00 $00, $F0
    BogusAddSlotFields00 $00, $F0
    BogusAddSlotFields00 $00, $F0
    BogusAddSlotFields00 $00, $F0
    BogusSetSlot05F0Pair $24, $FF
    BogusBranchIfSlot0520AtMost UnversionedScriptAC3C, $00
    BogusWait $06
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptABD8:
    BogusSetDispatchCounter $85
    BogusSetSlot05F0Pair $FF, $7E
    BogusLoadSlotRecord $24, $01
    BogusSetSlotFields80 $FF, $82
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusClearSlot0790Bits $11
    BogusSetSlotFields80 $FF, $82
    BogusApplyAndClearSelected3E
    BogusSetSlotFields80 $FF, $82
    BogusSetSlotFields80 $FF, $82
    BogusApplyAndClearSelected3E
    BogusSetSlotFields80 $FF, $82
UnversionedScriptABF7:
    BogusApplyAndClearSelected3E
    BogusBranchIfSlotFieldsWithin UnversionedScriptAC00, $FF, $10
    BogusJumpBank1 UnversionedScriptABF7
UnversionedScriptAC00:
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAC02:
    BogusSetSlotC0 $FF
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusClearSlotD0Bits $80
    BogusRestartVoice4 $26AC
    BogusWait $08
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAC11:
    BogusSetDispatchCounter $85
    BogusSetSlot0790Bits $FF
    BogusSetSlotFields80 $00, $00
    BogusSetSlotC0 $00
    BogusSetSlot0640Pair $00, $00
    BogusRestartVoice4 $27F7
    BogusInitializeOtherSlotRelative $77, $00, $F8, $00
    BogusInitializeOtherSlotRelative $77, $08, $F8, $00
    BogusInitializeOtherSlotRelative $77, $00, $08, $00
    BogusInitializeOtherSlotRelative $77, $08, $08, $00
    BogusWait $05
    BogusLoadSlotRecordAtPointer (UnversionedRecordB538 - BankStart)
    BogusJumpBank1 UnversionedScriptAC76
UnversionedScriptAC3C:
    BogusSetSlot0790Bits $FF
    BogusSetSlotFields80 $00, $00
    BogusSetSlot0640Pair $00, $00
    BogusLoadSlotRecordAtPointer (UnversionedRecordAABD - BankStart)
    BogusSetSlot07F0 $80
    BogusWait $14
    BogusBranchIfSelectedFlags UnversionedScriptAC4F, $E0
UnversionedScriptAC4F:
    UnversionedAddSelectedByte $02, $FF
    UnversionedReadSelectedByte $02
    BogusBranchIfSlotValueEqual UnversionedScriptAC67, $00, $00
    BogusBranchIfRemainingVerticalOffsetAtMost UnversionedScriptAC62, $0006
    BogusSetSlot0520 $0F
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptAC62:
    BogusReadSlotValue $0F
    BogusJumpBank1 ($8000 + $7426)
UnversionedScriptAC67:
    BogusSetSlotFields40Signed $C0, $00
    BogusSetSlotFields80 $FF, $C0
    BogusSetSlotMode $FF
    BogusRestartVoice4 $27B4
UnversionedScriptAC72:
    BogusBranchIfSlotB0AtMost UnversionedScriptAC72, $C8
UnversionedScriptAC76:
    BogusSetDispatchCounter $82
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $00
    BogusRestartVoice4 $0000
    BogusSetVoicePointers $2A2D, $2A3C, $0000, $0000
    BogusWait $3C
    BogusSetSpritePalettePointer Bank0::UnversionedPalette05
    BogusSetBackgroundPalettePointer Bank0::UnversionedPalette05
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusReadSlotValue $0F
    BogusStoreSlotValueArray $3A
    BogusSetMainState $12
UnversionedScriptACA0:
    BogusSetDispatchCounter $02
    BogusSetSlot0790Bits $DF
    BogusSelectRelativeSlotAndYield $00, $07, $01, $14, $00
    BogusSetSlot0360 $3C
UnversionedScriptACAC:
    BogusBranchIfSlot06D0Present UnversionedScriptACB2
    BogusJumpBank1 UnversionedScriptACBB
UnversionedScriptACB2:
    BogusBranchIfSecondWorldOffsetAtMost UnversionedScriptACBB, $0040
    BogusBranchIfSlot0360Above UnversionedScriptACAC, $00
UnversionedScriptACBB:
    BogusClearSelected3E
    BogusClearSelected40
    BogusInitializeSlotMotionFields
    BogusSetSlotFields80 $00, $00
    BogusSetSlotMode $02
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptACC5:
    BogusSetDispatchCounter $0A
    BogusLoadSlotValueArray $29
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusClearSlotD0Bits $80
    BogusSetSlotC0 $FF
    BogusClearSlot0790Bits $BF
    BogusSetSlot05F0Pair $FF, $60
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptACDF, $FFFF
    BogusLoadSlotRecordAtPointer (UnversionedRecordAACF - BankStart)
UnversionedScriptACDF:
    BogusApplyAndClearSelected3E
    BogusSetDispatchCounter $08
    BogusBranchIfSlot0620Bit10 UnversionedScriptACF9
    BogusBranchIfRemainingVerticalOffsetAtMost UnversionedScriptAC3C, $0006
    BogusReadSlotValue $AA
    BogusBranchIfSlotValueNotEqual UnversionedScriptACDF, $0008
    BogusBranchIfRemainingVerticalOffsetAtMost UnversionedScriptAC11, $0020
    BogusJumpBank1 UnversionedScriptACDF
UnversionedScriptACF9:
    BogusStartVoice4 $2784
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptACFE:
    BogusBranchIfSlot0620Bit10 UnversionedScriptAD31
    BogusBranchIfSlotD0Bits UnversionedScriptAD31, $80
    BogusBranchIfPositiveOffsetProbe UnversionedScriptAD0A, $05
    BogusRestoreSavedScriptAndSlotFlags
UnversionedScriptAD0A:
    BogusApplyAndClearSelected3E
    BogusBranchIfSlot0620Bit10 UnversionedScriptAD31
    BogusBranchIfSelectedFlagsClear UnversionedScriptACDF, $80
    BogusApplyAndClearSelected3E
    BogusBranchIfSlot0620Bit10 UnversionedScriptAD31
    BogusBranchIfSelectedFlagsClear UnversionedScriptACDF, $80
    BogusApplyAndClearSelected3E
    BogusBranchIfSlot0620Bit10 UnversionedScriptAD31
    BogusBranchIfSelectedFlagsClear UnversionedScriptACDF, $80
    BogusApplyAndClearSelected3E
    BogusBranchIfSlot0620Bit10 UnversionedScriptAD31
    BogusBranchIfSelectedFlagsClear UnversionedScriptACDF, $80
    BogusApplyAndClearSelected3E
    BogusBranchIfSlot0620Bit10 UnversionedScriptAD31
    BogusJumpBank1 UnversionedScriptACDF
UnversionedScriptAD31:
    BogusSetDispatchCounter $0C
    BogusClearSlot0790Bits $B7
    BogusClearSlotD0Bits $80
    BogusBranchIfSelectedFlags UnversionedScriptAD75, $04
UnversionedScriptAD3B:
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptAD44, $FFFF
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAD8 - BankStart)
UnversionedScriptAD44:
    BogusSetSlot0360 $03
    BogusRestartVoice4 $26BE
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotFields80 $FF, $A0
UnversionedScriptAD50:
    BogusSetDispatchCounter $85
    BogusSetSlotFields80 $FF, $A0
    BogusApplyAndClearSelected3E
    BogusBranchIfSelectedFlagsClear UnversionedScriptAD61, $80
    BogusBranchIfSlot0360AtMost UnversionedScriptAD66, $00
    BogusJumpBank1 UnversionedScriptAD50
UnversionedScriptAD61:
    BogusSetSlotFields80 $FF, $E0
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAD66:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $FF, $B0
    BogusApplyAndClearSelected3E
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $FF, $C0
    BogusApplyAndClearSelected3E
    BogusLoadRecordAndClearSavedState $12
    BogusRestoreSavedScriptAndSlotFlags
UnversionedScriptAD75:
    BogusBranchIfSelectedFlags UnversionedScriptAD3B, $03
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptAD82, $FFFF
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAD8 - BankStart)
UnversionedScriptAD82:
    BogusSetDispatchCounter $03
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotFields80 $FF, $E0
    BogusApplyAndClearSelected3E
    BogusApplyAndClearSelected3E
    BogusApplyAndClearSelected3E
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAD90:
    BogusSetDispatchCounter $89
    BogusStoreSlotValueArray $FF
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptAE59, $0C, $0C
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptADE5, $FFFF
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueEqual UnversionedScriptADCB, $10, $00
    BogusBranchIfSlot0620Bit10 UnversionedScriptADAC
    BogusJumpBank1 UnversionedScriptADBF
UnversionedScriptADAC:
    BogusBranchIfSlotFieldsWithin UnversionedScriptADB8, $01, $FF
    BogusBranchIfSlotD0Bits UnversionedScriptADBF, $80
    BogusJumpBank1 UnversionedScriptADBF
UnversionedScriptADB8:
    BogusLoadSlotRecordAtPointer (UnversionedRecordAE50 - BankStart)
    BogusWait $05
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptADBF:
    BogusLoadSlotValueArray $FF
    BogusRestoreSavedScriptAndSlotFlags
UnversionedRecordADC2:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation029, $FFFF, $40, $FF, $00, $00, $00
UnversionedScriptADCB:
    BogusSetDispatchCounter $87
    BogusLoadSlotRecordAtPointer (UnversionedRecordADC2 - BankStart)
    BogusRestartVoice4 $26EA
    BogusSetDispatchCounter $84
    BogusLoadSlotValueArray $29
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusWait $05
    BogusCreateLinkedSlot $7A, $19, $F8, $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptADE5:
    BogusBranchIfSlot0620Bit10 UnversionedScriptAE06
    BogusSetDispatchCounter $85
    BogusBranchIfSelectedFlags UnversionedScriptAE39, $08
    BogusBranchIfSelectedFlags UnversionedScriptADFF, $04
    BogusRestartVoice4 $26EA
    BogusSetDirectionalSlotFields40 $10, $D8
    BogusMarkRelatedSlotAtDepth $18, $01
    BogusWait $04
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptADFF:
    BogusMarkRelatedSlotAtDepth $38, $01
    BogusWait $04
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAE06:
    BogusBranchIfSelectedFlags UnversionedScriptADBF, $03
    BogusSetDispatchCounter $85
    BogusBranchIfSelectedFlags UnversionedScriptAE2B, $08
    BogusBranchIfSelectedFlags UnversionedScriptAE24, $04
    BogusSetDirectionalSlotFields40 $10, $D8
    BogusMarkRelatedSlotAtDepth $1A, $01
    BogusRestartVoice4 $26EA
    BogusSetSlotFields80 $00, $00
    BogusWait $03
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptAE24:
    BogusMarkRelatedSlotAtDepth $38, $01
    BogusWait $03
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptAE2B:
    BogusRestartVoice4 $27D3
    BogusMarkRelatedSlotAtDepth $E8, $01
UnversionedScriptAE31:
    BogusWait $01
    BogusBranchIfSelectedFlags UnversionedScriptAE31, $40
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptAE39:
    BogusRestartVoice4 $27D3
    BogusMarkRelatedSlotAtDepth $E8, $01
UnversionedScriptAE3F:
    BogusWait $01
    BogusBranchIfSelectedFlags UnversionedScriptAE3F, $40
    BogusLoadRecordAndClearSavedState $12
UnversionedRecordAE47:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation033, $FFFF, $40, $00, $60, $08, $12
UnversionedRecordAE50:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame103, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptAE59:
    BogusLoadSlotRecordAtPointer (UnversionedRecordAE47 - BankStart)
    BogusMarkRelatedSlotAtDepth $38, $05
    BogusWait $07
    BogusMarkRelatedSlotAtDepth $38, $05
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptAE66:
    BogusSetDispatchCounter $05
    BogusClearSlot0790Bits $BF
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptAE76, $FFFF
    BogusLoadSlotRecordAtPointer (UnversionedRecordAA99 - BankStart)
    BogusJumpBank1 UnversionedScriptAE7C
UnversionedScriptAE76:
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAA2 - BankStart)
    BogusMarkRelatedSlotAtDepth $38, $05
UnversionedScriptAE7C:
    BogusApplyAndClearSelected3E
    BogusBranchIfSlotFieldsWithin UnversionedScriptAE84, $07, $FF
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptAE84:
    BogusApplyAndClearSelected3E
    BogusBranchIfRemainingVerticalOffsetAtMost UnversionedScriptAC3C, $0006
    BogusJumpBank1 UnversionedScriptAE7C
UnversionedScriptAE8D:
    BogusSetDispatchCounter $0A
    BogusStoreSlotValueArray $3E
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3F
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueAtLeast UnversionedScriptAEA1, $0006
    BogusAddSlotValue $00F7
    BogusJumpBank1 UnversionedScriptAEBA
UnversionedScriptAEA1:
    BogusBranchIfSlotValueAtLeast UnversionedScriptAEAC, $000C
    BogusSetSlotValue $002B
    BogusJumpBank1 UnversionedScriptAEBA
UnversionedScriptAEAC:
    BogusBranchIfSlotValueAtLeast UnversionedScriptAEB7, $0010
    BogusSetSlotValue $0012
    BogusJumpBank1 UnversionedScriptAEBA
UnversionedScriptAEB7:
    BogusSetSlotValue $0027
UnversionedScriptAEBA:
    BogusStoreSlotValueArray $3D
    BogusLoadSlotLowFromByteArray $3F
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $3E
    BogusSaveStateAndPlaceSlots $11
    BogusRestoreSavedScriptAndSlotFlags
UnversionedScriptAEC4:
    BogusSetDispatchCounter $0C
    BogusStoreSlotValueArray $3E
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3F
    BogusBranchIfSlot0770Equal UnversionedScriptAEE5, $07
    BogusBranchIfSlot0770Equal UnversionedScriptAF4D, $00
    BogusBranchIfSlot0770Equal UnversionedScriptAF3D, $80
    BogusBranchIfSlot0770Equal UnversionedScriptAF7C, $01
    BogusBranchIfSlot0770Equal UnversionedScriptB01E, $0D
UnversionedScriptAEDF:
    BogusLoadSlotLowFromByteArray $3F
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $3E
    BogusRestoreSavedScriptAndSlotFlags
UnversionedScriptAEE5:
    BogusBranchIfMatchingSlotReady UnversionedScriptAEF6, $01, $6A, $00
    BogusSetSlotValue $002D
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusReadSlotValue $0F
    BogusSetMainState $00
UnversionedScriptAEF6:
    BogusSetSlot0670Pair $00, $10
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptAF01, $10, $20
    BogusJumpBank1 UnversionedScriptAEDF
UnversionedScriptAF01:
    BogusRestartVoice4 $0000
    BogusSetVoicePointers $29FD, $2A15, $0000, $0000
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueEqual UnversionedScriptAF2B, $0B, $00
    BogusSetSlotValue $0031
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusReadSlotValue $0F
    BogusAddSlotValue $0001
    BogusSetMainState $00
UnversionedScriptAF2B:
    BogusSetSlotValue $002E
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusSetMainState $FF
UnversionedScriptAF3D:
    BogusFindLinkedSlot
    BogusBranchIfSlotValueEqual UnversionedScriptAF4D, $FF, $FF
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusJumpBank1 UnversionedScriptAEDF
UnversionedScriptAF4D:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptAEDF
    BogusReadSlotValue $00
    BogusMaskSlotValue $007F
    BogusClampSlotValueAtMost $00C8
    BogusSetBackgroundPalettePointer Bank0::UnversionedPalette05
    BogusSetSpritePalettePointer Bank0::UnversionedPalette05
    BogusLoadIndexedStateRecord $3002
    BogusReadSlotValue $00
    BogusMaskSlotValue $0080
    BogusBranchIfSlotValueEqual UnversionedScriptAF72, $80, $00
    BogusConfigureBanksFromOperand $02
    BogusSetBackgroundPalettePointer Bank0::UnversionedPalette00
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptAF72:
    BogusConfigureBanksFromOperand $FF
    BogusSetBackgroundPalettePointer $FFFF
    BogusSetSpritePalettePointer $FFFF
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptAF7C:
    BogusBranchIfSlotD0Bits UnversionedScriptAFA0, $80
    BogusSetDispatchCounter $07
    BogusBranchIfSelectedFlags UnversionedScriptAF8D, $08
    BogusBranchIfSlot0620Bit10 UnversionedScriptAEDF
    BogusBranchIfSelectedFlagsClear UnversionedScriptAEDF, $04
UnversionedScriptAF8D:
    BogusSetDispatchCounter $08
    BogusSetDispatchCounter $06
    BogusSetSlotD0Bits $80
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAC6 - BankStart)
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $00
    BogusClearSlot0790Bits $25
    BogusMarkSlot05A0AndYield
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAFA0:
    BogusSetDispatchCounter $8F
    BogusBranchIfRemainingVerticalOffsetAtMost UnversionedScriptAFAE, $0060
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusJumpBank1 UnversionedScriptAFB7
UnversionedScriptAFAE:
    BogusLoadSlotValueArray $29
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusBranchIfSlot0620Bit10 UnversionedScriptAFFA
UnversionedScriptAFB7:
    BogusBranchIfSelectedFlags UnversionedScriptAFC1, $03
    BogusSetSlotFields80 $00, $FF
    BogusJumpBank1 UnversionedScriptAFC2
UnversionedScriptAFC1:
    BogusApplyAndClearSelected3E
UnversionedScriptAFC2:
    BogusBranchIfSelectedFlags UnversionedScriptAFDA, $08
    BogusBranchIfSelectedFlagsClear UnversionedScriptAFF0, $04
    BogusSetSlotFields80 $FF, $10
    BogusBranchIfSelectedFlagsClear UnversionedScriptAFEA, $40
    BogusSetSlotFields80 $FF, $20
    BogusStartVoice4 $26D9
    BogusJumpBank1 UnversionedScriptAFF5
UnversionedScriptAFDA:
    BogusSetSlotFields80 $FF, $F0
    BogusBranchIfSelectedFlagsClear UnversionedScriptAFEA, $40
    BogusSetSlotFields80 $FF, $E0
    BogusStartVoice4 $26D9
    BogusJumpBank1 UnversionedScriptAFF5
UnversionedScriptAFEA:
    BogusStartVoice4 $26D0
    BogusJumpBank1 UnversionedScriptAFF5
UnversionedScriptAFF0:
    BogusSetSlotFields80 $FF, $00
    BogusClearSlot0790Bits $08
UnversionedScriptAFF5:
    BogusClearSlot0790Bits $25
    BogusMarkSlot05A0AndYield
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptAFFA:
    BogusBranchIfSelectedFlags UnversionedScriptAFB7, $08
    BogusClearSlotD0Bits $80
    BogusLoadRecordAndClearSavedState $3F
UnversionedIndexedStateB002:
; Four indexed seven-byte state records, base read by AF5E. The next
; script boundary limits the stored table, not every possible index.
    IndexedStateRecord $FF, $32, $1E, $0180, $0193
    IndexedStateRecord $FF, $31, $1E, $0011, $001C
    IndexedStateRecord $FF, $21, $15, $0180, $018B
    IndexedStateRecord $FF, $21, $15, $0011, $0024
UnversionedScriptB01E:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptAEDF
    BogusSetDispatchCounter $06
    BogusSetSlotValue $2B00
    BogusStoreSlotLowAtIndexedPage
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $2A
    BogusMarkRelatedSlotAtDepth $48, $01
    BogusWait $02
    BogusSetDispatchCounter $06
    BogusSetSlotValue $2C00
    BogusStoreSlotLowAtIndexedPage
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $2A
    BogusMarkRelatedSlotAtDepth $48, $02
    BogusWait $02
    BogusSetDispatchCounter $06
    BogusSetSlotValue $2D00
    BogusStoreSlotLowAtIndexedPage
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $2A
    BogusMarkRelatedSlotAtDepth $48, $03
    BogusWait $02
    BogusSetDispatchCounter $06
    BogusSetSlotValue $2E00
    BogusStoreSlotLowAtIndexedPage
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $2A
    BogusMarkRelatedSlotAtDepth $48, $04
    BogusWait $02
    BogusSetBackgroundPalettePointer Bank0::UnversionedPalette05
    BogusSetSpritePalettePointer Bank0::UnversionedPalette05
    BogusWait $02
    BogusLoadSlotRecordAtPointer (UnversionedRecordAAE1 - BankStart)
    BogusSetSpriteAttribute20 $20
    BogusJumpBank1 ($8000 + $51CD)
    BogusSetSlotC0 $FF
    BogusSetSpriteAttribute20 $00
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueEqual UnversionedScriptB081, $00, $00
    BogusSetSlotValue $0003
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusReadSlotValue $0F
    BogusStoreSlotValueArray $3D
    BogusSetMainState $14
UnversionedScriptB081:
    BogusSetBackgroundPalettePointer $FFFF
    BogusSetSpritePalettePointer $FFFF
    BogusLoadRecordAndClearSavedState $3F
UnversionedCompactB089:
; Five compact resources precede the normal B098 descriptor record.
; B2D8 dispatches six cases after a clamp to20 and division by4;
; its 63 commands select the normal record or backward compact offsets.
    SlotCompactRecord Bank0::UnversionedSpriteFrame089, $00
UnversionedCompactB08C:
    SlotCompactRecord Bank0::UnversionedSpriteFrame087, $00
UnversionedCompactB08F:
    SlotCompactRecord Bank0::UnversionedSpriteFrame085, $00
UnversionedCompactB092:
    SlotCompactRecord Bank0::UnversionedSpriteFrame083, $00
UnversionedCompactB095:
    SlotCompactRecord Bank0::UnversionedSpriteFrame081, $00
UnversionedRecordB098:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame079, (UnversionedScriptB0A1 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptB0A1:
    BogusSetSlotC0 $00
    BogusSetSlotPositionFromOperands $0C, $67
    BogusReadSlotValue $0F
    BogusSetSlotD0Bits $10
    BogusBranchIfSlotValueAtLeast UnversionedScriptB0C5, $0010
    BogusClearSlotD0Bits $10
    BogusSetSlotD0Bits $08
    BogusBranchIfSlotValueAtLeast UnversionedScriptB0C5, $000C
    BogusClearSlotD0Bits $08
    BogusSetSlotD0Bits $04
    BogusBranchIfSlotValueAtLeast UnversionedScriptB0C5, $0006
    BogusClearSlotD0Bits $04
    BogusSetSlotD0Bits $02
UnversionedScriptB0C5:
    BogusSetSlotValue $1000
    BogusStoreSlotValueArray $FF
UnversionedScriptB0CA:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlot0370AtMost UnversionedScriptB2CE, $00
UnversionedScriptB0D0:
    BogusSetDispatchCounter $0A
    BogusLoadSlotValueArray $FF
    BogusFindSlotAtValueOffset
    BogusBranchIfSlotValueNotEqual UnversionedScriptB16F, $FFFF
    BogusLoadSlotValueArray $FF
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptB197, $006C
    BogusLookupCaseBank1 UnversionedScriptB1B3, $006D
    BogusLookupCaseBank1 UnversionedScriptB1B9, $008C
    BogusLookupCaseBank1 UnversionedScriptB1BF, $008D
    BogusLookupCaseBank1 UnversionedScriptB1C5, $006F
    BogusLookupCaseBank1 UnversionedScriptB1E8, $0071
    BogusLookupCaseBank1 UnversionedScriptB1EE, $004D
    BogusLookupCaseBank1 UnversionedScriptB1F4, $008E
    BogusLookupCaseBank1 UnversionedScriptB1FA, $0041
    BogusLookupCaseBank1 UnversionedScriptB21D, $0014
    BogusLookupCaseBank1 UnversionedScriptB223, $00BC
    BogusLookupCaseBank1 UnversionedScriptB229, $0061
    BogusLookupCaseBank1 UnversionedScriptB22F, $0045
    BogusLookupCaseBank1 UnversionedScriptB252, $0047
    BogusLookupCaseBank1 UnversionedScriptB258, $00C8
    BogusLookupCaseBank1 UnversionedScriptB25E, $009B
    BogusLookupCaseBank1 UnversionedScriptB22F, $0090
    BogusLookupCaseBank1 UnversionedScriptB22F, $0040
    BogusLookupCaseBank1 UnversionedScriptB22F, $0013
    BogusLookupCaseBank1 UnversionedScriptB22F, $0045
    BogusLookupCaseBank1 UnversionedScriptB264, $0027
    BogusLookupCaseBank1 UnversionedScriptB287, $0029
    BogusLookupCaseBank1 UnversionedScriptB28D, $0066
    BogusLookupCaseBank1 UnversionedScriptB293, $0068
    BogusLookupCaseBank1 UnversionedScriptB299, $00AA
    BogusLookupCaseBank1 UnversionedScriptB2BC, $00AC
    BogusLookupCaseBank1 UnversionedScriptB2C2, $00AB
    BogusLookupCaseBank1 UnversionedScriptB2C8, $00AD
    BogusLookupEnd
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $10
    BogusBranchIfSlot0360Above UnversionedScriptB16F, $00
    BogusSetSlot0360 $18
    BogusBranchIfSecondWorldOffsetAtMost UnversionedScriptB16F, $0140
    BogusBranchIfFirstWorldOffsetAtMost UnversionedScriptB16F, $0200
    BogusReadSlotValue $05
    BogusMaskSlotValue $00FF
    BogusAddSlotValue $0100
    BogusCreateSlotFromValue $76, $00
UnversionedScriptB16F:
    BogusSetDispatchCounter $06
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $0010
    BogusStoreSlotValueArray $FF
    BogusMaskSlotValue $00FF
    BogusBranchIfSlotValueAtLeast UnversionedScriptB183, $00E0
    BogusJumpBank1 UnversionedScriptB0CA
UnversionedScriptB183:
    BogusSetDispatchCounter $05
    BogusLoadSlotValueArray $FF
    BogusMaskSlotValue $FF00
    BogusAddSlotValue $1000
    BogusStoreSlotValueArray $FF
    BogusBranchIfSlotValueAtLeast UnversionedScriptB0C5, $E000
    BogusJumpBank1 UnversionedScriptB0CA
UnversionedScriptB197:
    BogusSetSlotValue $0000
UnversionedScriptB19A:
    BogusSetDispatchCounter $06
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $02
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusAdvanceAndBranchState1B UnversionedScriptB1AD, $C0
    BogusCreateSlotFromValue $0B, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB1AD:
    BogusCreateSlotFromValue $0C, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB1B3:
    BogusSetSlotValue $FFF8
    BogusJumpBank1 UnversionedScriptB19A
UnversionedScriptB1B9:
    BogusSetSlotValue $F800
    BogusJumpBank1 UnversionedScriptB19A
UnversionedScriptB1BF:
    BogusSetSlotValue $F8F8
    BogusJumpBank1 UnversionedScriptB19A
UnversionedScriptB1C5:
    BogusSetSlotValue $0000
UnversionedScriptB1C8:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $08
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $74
    BogusBranchIfSlotValueAtLeast UnversionedScriptB16F, $0003
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $74, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB1E8:
    BogusSetSlotValue $FFF8
    BogusJumpBank1 UnversionedScriptB1C8
UnversionedScriptB1EE:
    BogusSetSlotValue $F800
    BogusJumpBank1 UnversionedScriptB1C8
UnversionedScriptB1F4:
    BogusSetSlotValue $F8F8
    BogusJumpBank1 UnversionedScriptB1C8
UnversionedScriptB1FA:
    BogusSetSlotValue $E000
UnversionedScriptB1FD:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $10
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $78
    BogusBranchIfSlotValueAtLeast UnversionedScriptB16F, $0002
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $78, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB21D:
    BogusSetSlotValue $E0F8
    BogusJumpBank1 UnversionedScriptB1FD
UnversionedScriptB223:
    BogusSetSlotValue $D800
    BogusJumpBank1 UnversionedScriptB1FD
UnversionedScriptB229:
    BogusSetSlotValue $D8F8
    BogusJumpBank1 UnversionedScriptB1FD
UnversionedScriptB22F:
    BogusSetSlotValue $0000
UnversionedScriptB232:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $04
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $6C
    BogusBranchIfSlotValueAtLeast UnversionedScriptB16F, $0003
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $6C, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB252:
    BogusSetSlotValue $FFF8
    BogusJumpBank1 UnversionedScriptB232
UnversionedScriptB258:
    BogusSetSlotValue $F800
    BogusJumpBank1 UnversionedScriptB232
UnversionedScriptB25E:
    BogusSetSlotValue $F8F8
    BogusJumpBank1 UnversionedScriptB232
UnversionedScriptB264:
    BogusSetSlotValue $E800
UnversionedScriptB267:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $04
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $70
    BogusBranchIfSlotValueAtLeast UnversionedScriptB16F, $0002
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $70, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB287:
    BogusSetSlotValue $E8F8
    BogusJumpBank1 UnversionedScriptB267
UnversionedScriptB28D:
    BogusSetSlotValue $E000
    BogusJumpBank1 UnversionedScriptB267
UnversionedScriptB293:
    BogusSetSlotValue $E0F8
    BogusJumpBank1 UnversionedScriptB267
UnversionedScriptB299:
    BogusSetSlotValue $F810
UnversionedScriptB29C:
    BogusSetDispatchCounter $0D
    BogusBranchIfSlotD0BitsClear UnversionedScriptB16F, $04
    BogusAddSlotValueFromArray $FF
    BogusAlignSlotValueToScrollGrid
    BogusStoreSlotValueArray $2F
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $30
    BogusCountSlotsByRecord $02
    BogusBranchIfSlotValueAtLeast UnversionedScriptB16F, $0002
    BogusLoadSlotValueArray $30
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2F
    BogusCreateSlotFromValue $02, $00
    BogusJumpBank1 UnversionedScriptB16F
UnversionedScriptB2BC:
    BogusSetSlotValue $F808
    BogusJumpBank1 UnversionedScriptB29C
UnversionedScriptB2C2:
    BogusSetSlotValue $F010
    BogusJumpBank1 UnversionedScriptB29C
UnversionedScriptB2C8:
    BogusSetSlotValue $F008
    BogusJumpBank1 UnversionedScriptB29C
UnversionedScriptB2CE:
    BogusSetSlot0370 $0A
    BogusReadSelectedSlot0520 $00
    BogusClampSlotValueAtMost $0014
    BogusDivideSlotValueByByte $04
    BogusJumpViaSlotIndexedTable ; CONTROL_UNVERSIONED_PREFIX_B2D7
UnversionedIndexedTargetB2D8:
    BogusIndexedTargetBank1 UnversionedScriptB2E4
    BogusIndexedTargetBank1 UnversionedScriptB2EA
    BogusIndexedTargetBank1 UnversionedScriptB2F0
    BogusIndexedTargetBank1 UnversionedScriptB2F6
    BogusIndexedTargetBank1 UnversionedScriptB2FC
    BogusIndexedTargetBank1 UnversionedScriptB302
UnversionedScriptB2E4:
    BogusLoadSlotRecord $00, $01
    BogusJumpBank1 UnversionedScriptB0D0
UnversionedScriptB2EA:
    BogusLoadSlotRecord $03, $FF
    BogusJumpBank1 UnversionedScriptB0D0
UnversionedScriptB2F0:
    BogusLoadSlotRecord $06, $FF
    BogusJumpBank1 UnversionedScriptB0D0
UnversionedScriptB2F6:
    BogusLoadSlotRecord $09, $FF
    BogusJumpBank1 UnversionedScriptB0D0
UnversionedScriptB2FC:
    BogusLoadSlotRecord $0C, $FF
    BogusJumpBank1 UnversionedScriptB0D0
UnversionedScriptB302:
    BogusLoadSlotRecord $0F, $FF
    BogusJumpBank1 UnversionedScriptB0D0
UnversionedRecordB308:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame051, (UnversionedScriptB323 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordB311:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame114, (UnversionedScriptB331 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordB31A:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation039, (UnversionedScriptB338 - BankStart), $40, $FF, $00, $00, $00
UnversionedScriptB323:
    BogusSetSlotC0 $00
    BogusAdjustSlotBounds $00, $FE
    BogusSetSlot0670Pair $01, $00
UnversionedScriptB32B:
    BogusWait $28
    BogusClearSlot0790Bits $01
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptB331:
    BogusStartVoice4 $2694
    BogusWait $04
    BogusYieldAndSlotAction $01
UnversionedScriptB338:
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $01, $00
    BogusBranchIfSlotRecord06AtLeast UnversionedScriptB344, $07
    BogusJumpBank1 UnversionedScriptB338
UnversionedScriptB344:
    BogusCreateLinkedSlot $6D, $12, $00, $FF
    BogusStartVoice4 $26EA
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadSlotRecord $00, $02
    BogusJumpBank1 UnversionedScriptB32B
UnversionedRecordB353:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation017, (UnversionedScriptB365 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordB35C:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation017, $FFFF, $00, $00, $20, $50, $12
UnversionedScriptB365:
    BogusSetSlot0670Pair $01, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlotC0 $00
UnversionedScriptB36D:
    BogusSetSlotFields40Signed $18, $00
UnversionedScriptB370:
    BogusBranchIfAbsSlot0700Below UnversionedScriptB36D, $18
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptB37E, $00, $00
    BogusJumpBank1 UnversionedScriptB370
UnversionedScriptB37E:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptB36D, $FF, $30
    BogusSetSlotFields80 $00, $00
    BogusWait $06
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptB36D, $FF, $30
    BogusLoadSlotRecord $09, $02
    BogusSetSlotBit40 $FF
    BogusSetSlot0360 $64
UnversionedScriptB394:
    BogusSetDispatchCounter $05
    BogusSetSlot0620Bit20
    BogusSetSlot0660LowBits $01
    BogusSetSlot0660HighBits $01
    BogusAddSlotFields00 $06, $06
    BogusSetDispatchCounter $07
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptB3C9
    BogusBranchIfSlot0360AtMost UnversionedScriptB3EA, $00
    BogusBranchIfSlotB0AtMost UnversionedScriptB3C3, $14
    BogusAdvanceAndBranchState1B UnversionedScriptB3B6, $C0
    BogusAdvanceAndBranchState1B UnversionedScriptB3BD, $80
    BogusStartVoice4 $33FF
UnversionedScriptB3B6:
    BogusBranchIfSlotB0AtMost UnversionedScriptB394, $D2
    BogusJumpBank1 UnversionedScriptB3EA
UnversionedScriptB3BD:
    BogusStartVoice4 $33F6
    BogusJumpBank1 UnversionedScriptB3B6
UnversionedScriptB3C3:
    BogusSetSlotFields80 $FF, $00
    BogusJumpBank1 UnversionedScriptB394
UnversionedScriptB3C9:
    BogusLoadSlotRecord $00, $02
    BogusSetSlot0660HighBits $00
    BogusSetSlotFields40Signed $E8, $FF
    BogusSetSlotFields80 $FF, $C0
UnversionedScriptB3D4:
    BogusFindLinkedSlot
    BogusBranchIfSlotValueNotEqual UnversionedScriptB3D4, $FFFF
    BogusSetSlotFields80 $30, $FF
UnversionedScriptB3DD:
    BogusBranchIfSlotB0AtMost UnversionedScriptB3E8, $10
    BogusBranchIfAbsSlot0700Below UnversionedScriptB3E8, $0A
    BogusJumpBank1 UnversionedScriptB3DD
UnversionedScriptB3E8:
    BogusYieldAndSlotAction $01
UnversionedScriptB3EA:
    BogusSetSlot0660HighBits $00
    BogusSetSlotFields80 $FF, $C0
UnversionedScriptB3EF:
    BogusBranchIfSlotB0AtMost UnversionedScriptB365, $3C
    BogusJumpBank1 UnversionedScriptB3EF
UnversionedAudioB3F6:
    AudioSelectChannel $00
    AudioWriteFive $A7, $A5, $3A, $00
    AudioDelay $08
    AudioStopVoice
    AudioSelectChannel $00
    AudioWriteFive $A7, $A5, $4A, $00
    AudioDelay $08
    AudioStopVoice
UnversionedRecordB408:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame051, (UnversionedScriptB41A - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordB411:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation116, $FFFF, $00, $FE, $20, $40, $11
UnversionedScriptB41A:
    BogusSetSlotC0 $00
    BogusSetSlot0360 $32
    BogusSetSlotBit40 $01
    BogusSetSlot0670Pair $01, $00
UnversionedScriptB423:
    BogusBranchIfSlot0360AtMost UnversionedScriptB42F, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptB42F, $10, $18
    BogusJumpBank1 UnversionedScriptB423
UnversionedScriptB42F:
    BogusLoadRecordAndClearSavedState $09
    BogusStartVoice4 $269F
    BogusWait $0F
    BogusYieldAndSlotAction $00
UnversionedRecordB438:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation094, (UnversionedScriptB45C - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordB441:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame231, (UnversionedScriptB4CA - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordB44A:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation091, (UnversionedScriptB480 - BankStart), $00, $FE, $40, $41, $41
UnversionedRecordB453:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation093, (UnversionedScriptB4C7 - BankStart), $40, $FF, $00, $00, $00
UnversionedScriptB45C:
    BogusSetDispatchCounter $8B
    BogusRestartVoice4 $26B5
    BogusSetSlotC0 $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot07F0 $60
    BogusAdjustSlotBounds $04, $00
    BogusClearSlot0790Bits $01
    BogusSetSlotFields80 $00, $07
    BogusBranchIfSlotB0AtMost UnversionedScriptB47A, $74
    BogusSetSlotFields80 $00, $F9
    BogusAdjustSlotBounds $00, $EC
UnversionedScriptB47A:
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetDirectionalSlotFields40 $FF, $09
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptB480:
    BogusReadSlotValue $12
    BogusBranchIfSlotValueAtLeast UnversionedScriptB4A4, $0080
    BogusBranchIfPositiveOffsetProbe UnversionedScriptB4C1, $03
    BogusBranchIfSlotB0AtMost UnversionedScriptB492, $DC
    BogusJumpBank1 UnversionedScriptB4C1
UnversionedScriptB492:
    BogusSetSlotValue $2404
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptB4BA, $008C
    BogusLookupCaseBank1 UnversionedScriptB4BA, $008D
    BogusLookupEnd
    BogusJumpBank1 UnversionedScriptB480
UnversionedScriptB4A4:
    BogusBranchIfSlotB0AtMost UnversionedScriptB4C1, $30
    BogusSetSlotValue $FF04
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptB4BA, $006C
    BogusLookupCaseBank1 UnversionedScriptB4BA, $006D
    BogusLookupEnd
    BogusJumpBank1 UnversionedScriptB480
UnversionedScriptB4BA:
    BogusSetSlot07F0 $80
    BogusSetSlotFields80 $00, $00
    BogusLoadRecordAndClearSavedState $1B
UnversionedScriptB4C1:
    BogusSetDirectionalSlotFields40 $FF, $E0
    BogusJumpBank1 UnversionedScriptB480
UnversionedScriptB4C7:
    BogusCheckSlotFlagsAndRestorePointer
    BogusYieldAndSlotAction $00
UnversionedScriptB4CA:
    BogusSetSlotC0 $FF
    BogusSetSlotMode $FF
    BogusSetLinkedSlotFieldsC0 $40, $A0
UnversionedScriptB4D1:
    BogusBranchIfSlotB0AtMost UnversionedScriptB4D1, $E6
    BogusYieldAndSlotAction $00
UnversionedRecordB4D7:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation002, (UnversionedScriptB4E9 - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordB4E0:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation002, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptB4E9:
    BogusSetSlot0730 $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlotMode $02
    BogusSetSlot05F0Pair $40, $58
    BogusSetSlot0360 $3C
    BogusSetSlotFields80 $10, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptB4FF, $80
    BogusSetSlotFields80 $F0, $FF
UnversionedScriptB4FF:
    BogusAdvanceAndBranchState1B UnversionedScriptB506, $80
    BogusSetDirectionalSlotFields40 $10, $FF
UnversionedScriptB506:
    BogusSetDispatchCounter $85
    BogusSetSlot0620Bit20
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptB515
    BogusRestartVoice4 $2694
    BogusAddSlotFields00 $FF, $E8
    BogusJumpBank1 UnversionedScriptB506
UnversionedScriptB515:
    BogusSetDispatchCounter $03
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptB532
    BogusBranchIfAbsSlot0700Below UnversionedScriptB52A, $0C
    BogusBranchIfSlot0360Above UnversionedScriptB506, $00
UnversionedScriptB522:
    BogusSetSlotMode $FF
UnversionedScriptB524:
    BogusBranchIfSlotB0AtMost UnversionedScriptB524, $E6
    BogusYieldAndSlotAction $00
UnversionedScriptB52A:
    BogusSetSlotFields40Signed $18, $00
    BogusWait $04
    BogusJumpBank1 UnversionedScriptB506
UnversionedScriptB532:
    BogusLoadSlotRecord $09, $02
    BogusJumpBank1 UnversionedScriptB522
UnversionedRecordB538:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame049, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordB541:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame049, (UnversionedScriptB54A - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptB54A:
    BogusSetSlotC0 $00
    BogusInitializeOtherSlotRelative $04, $00, $00, $00
    BogusWait $05
    BogusInitializeOtherSlotRelative $04, $00, $00, $00
    BogusWait $05
    BogusInitializeSlotMotionFields
    BogusSetSlotFields80 $00, $00
    BogusLoadSlotRecordAtPointer (UnversionedRecordB561 - BankStart)
UnversionedRecordB561:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame297, (UnversionedScriptB56A - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptB56A:
    BogusSetSlotC0 $00
    BogusSetSlot0360 $14
    BogusSetSlot07F0 $01
    BogusSetSlotBit40 $01
UnversionedScriptB572:
    BogusSetSlotFields80 $F0, $F0
    BogusSetSlotFields80 $F8, $E8
    BogusSetSlotFields80 $F8, $E8
    BogusSetSlotFields80 $10, $F0
    BogusSetSlotFields80 $10, $F0
    BogusSetSlotFields80 $08, $E8
    BogusSetSlotFields80 $08, $E8
    BogusSetSlotFields80 $F0, $F0
    BogusBranchIfSlot0360Above UnversionedScriptB572, $01
    BogusYieldAndSlotAction $00
UnversionedScriptB590:
    BogusYieldAndSlotAction $00
UnversionedRecordB592:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame049, (UnversionedScriptB59B - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptB59B:
    BogusSetDispatchCounter $9F
    BogusBranchIfState58ZeroAndClear UnversionedScriptB5A2
    BogusClearSlotBitset $FF
UnversionedScriptB5A2:
    BogusSetState03BC $03
    BogusSetInvertedState18 $01
    BogusReadSlotValue $0F
    BogusLoadSlotValueIndexedBank1 UnversionedStateBytesB5E8 ; CONTROL_UNVERSIONED_PREFIX_B5A8
    BogusStoreSlotValueArray $3C
    BogusReadSlotValue $0F
    BogusLoadSlotValueIndexedBank1 UnversionedStateBytesB5FD
    BogusStoreSlotValueArray $29
    BogusSetSlotValue $0000
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
    BogusSetSlotValue $0005
    BogusStoreSlotValueArray $2B
    BogusReadSlotValue $0F
    BogusLoadSlotValueIndexedBank1 UnversionedStateBytesB5E2
    BogusStoreSlotValueArray $32
    BogusSetVoicePointers $2882, $FFFF, $FFFF, $FFFF
    BogusYieldAndSlotAction $00
UnversionedStateBytesB5E2:
; Three indexed byte bases: six state choices,21 vertical values and21
; horizontal values. Two-byte reads have lookahead across named extents.
    .byte $00, $06, $07, $07, $09, $08
UnversionedStateBytesB5E8:
    .byte $F0, $F2, $F2, $F2, $F0, $F2, $FE, $FE
    .byte $FE, $FE, $FE, $FE, $FA, $FA, $FA, $FA
    .byte $FA, $F0, $F0, $F0, $F0
UnversionedStateBytesB5FD:
    .byte $E0, $E0, $E0, $E0, $E0, $E0, $DE, $DE
    .byte $DE, $DE, $DE, $DE, $E0, $E0, $E0, $E0
    .byte $E0, $E0, $E0, $E0, $E0
UnversionedRecordB612:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame200, (UnversionedScriptB624 - BankStart), $00, $00, $30, $70, $11
UnversionedRecordB61B:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation078, $FFFF, $40, $FF, $00, $00, $00
UnversionedScriptB624:
    BogusSetSlotC0 $00
    BogusSetSlot07F0 $01
    BogusAdjustSlotBounds $00, $FD
    BogusSetSlot0670Pair $05, $40
UnversionedScriptB62E:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptB636, $08, $08
    BogusJumpBank1 UnversionedScriptB62E
UnversionedScriptB636:
    BogusSetSlot0620Bit20
    BogusStartVoice4 $27EE
    BogusLoadSlotRecord $09, $01
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetDispatchCounter $03
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptB643
UnversionedScriptB643:
    BogusJumpBank1 UnversionedScriptB62E
UnversionedRecordB646:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation020, (UnversionedScriptB64F - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptB64F:
    BogusSetSlotC0 $00
    BogusSetSlotBit40 $01
UnversionedScriptB653:
    BogusJumpBank1 UnversionedScriptB653
UnversionedCompactB656:
    SlotCompactRecord Bank0::UnversionedSpriteFrame273, $00
UnversionedCompactB659:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation108, $40
UnversionedCompactB65C:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation107, $00
UnversionedRecordB65F:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation107, (UnversionedScriptB671 - BankStart), $00, $00, $20, $61, $11
UnversionedRecordB668:
    SlotRuntimeRecord $FFFF, (UnversionedScriptB71D - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptB671:
    BogusSetDispatchCounter $8A
    BogusRestartVoice4 $26B5
    BogusReadSlotValue $0F
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptB691, $0006
    BogusLookupCaseBank1 UnversionedScriptB691, $0007
    BogusLookupCaseBank1 UnversionedScriptB697, $0008
    BogusLookupCaseBank1 UnversionedScriptB697, $0009
    BogusLookupEnd
    BogusSetSlot05F0Pair $18, $7E
    BogusJumpBank1 UnversionedScriptB69A
UnversionedScriptB691:
    BogusSetSlot05F0Pair $08, $7E
    BogusJumpBank1 UnversionedScriptB69A
UnversionedScriptB697:
    BogusSetSlot05F0Pair $10, $7E
UnversionedScriptB69A:
    BogusSetUnlinkedFields $00, $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot0660LowBits $00
    BogusClearSlot0790Bits $01
    BogusSetSlotValue $0003
    BogusStoreSlotValueArray $FF
    BogusSetSlot0670Pair $01, $00
UnversionedScriptB6AC:
    BogusSetSlotFields40Signed $18, $00
    BogusWait $08
UnversionedScriptB6B1:
    BogusLoadSlotRecord $00, $02
UnversionedScriptB6B4:
    BogusBranchIfSlotB0AtMost UnversionedScriptB6BA, $DE
    BogusYieldAndSlotAction $00
UnversionedScriptB6BA:
    BogusBranchIfAbsSlot0700Below UnversionedScriptB70E, $18
    BogusSetSlot0620Bit20
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptB6CE, $0080
    BogusBranchIfSlotOffset UnversionedScriptB70E, $02, $00
    BogusJumpBank1 UnversionedScriptB6D3
UnversionedScriptB6CE:
    BogusBranchIfSlotOffset UnversionedScriptB70E, $FE, $00
UnversionedScriptB6D3:
    BogusSetSlot0620Bit20
    BogusBranchIfSlotFieldsWithin UnversionedScriptB6AC, $01, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptB6B4, $FA
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
UnversionedScriptB6F7:
    BogusBranchIfSlotFieldsWithin UnversionedScriptB6FF, $FF, $10
    BogusJumpBank1 UnversionedScriptB6F7
UnversionedScriptB6FF:
    BogusSetSlot0660LowBits $00
    BogusLoadSlotRecord $09, $FF
UnversionedScriptB704:
    BogusBranchIfSlot0620Bit10 UnversionedScriptB6B1
    BogusSetSlot0620Bit20
    BogusBranchIfSlotB0AtMost UnversionedScriptB704, $DE
    BogusYieldAndSlotAction $00
UnversionedScriptB70E:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $E8, $FF
UnversionedScriptB716:
    BogusBranchIfAbsSlot0700Below UnversionedScriptB716, $18
    BogusJumpBank1 UnversionedScriptB6D3
UnversionedScriptB71D:
    BogusReadSlotValue $23
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptB72D, $0063
    BogusLookupCaseBank1 UnversionedScriptB749, $006D
    BogusLookupEnd
    BogusJumpBank1 ($8000 + $6763)
UnversionedScriptB72D:
    BogusLoadSlotRecord $06, $FF
    BogusSetSlotFields80 $FF, $82
    BogusSetSlotFields80 $FF, $82
    BogusClearSlot0790Bits $01
UnversionedScriptB738:
    BogusBranchIfSlotFieldsWithin UnversionedScriptB740, $FF, $10
    BogusJumpBank1 UnversionedScriptB738
UnversionedScriptB740:
    BogusLoadSlotRecord $09, $FF
UnversionedScriptB743:
    BogusBranchIfSlot0620Bit10 UnversionedScriptB6B1
    BogusJumpBank1 UnversionedScriptB743
UnversionedScriptB749:
    BogusSetSlotFields80 $00, $FF
    BogusJumpBank1 ($8000 + $6763)
UnversionedRecordB74F:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation100, (UnversionedScriptB758 - BankStart), $40, $FF, $00, $00, $00
UnversionedScriptB758:
    BogusSetSlotC0 $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusYieldAndSlotAction $01
UnversionedRecordB75D:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame049, (UnversionedScriptB766 - BankStart), $40, $FF, $00, $00, $00
UnversionedScriptB766:
    BogusSetSlotC0 $00
    BogusSetSlotAssociation $00
    BogusSetSlotValue $0002
    BogusStoreSlotValueArray $FF
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueAtLeast ($8000 + $4F07), $00F8
    BogusMultiplySlotValueByArray $FF
    BogusLoadSlotValueIndexedBank1 ($8000 + $3788)
; Explicit aliases preserve supported transfers into an existing operand.
.assert * = $B77B, error, "own opening scripts end"
.endmacro
