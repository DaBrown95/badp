; Bank-0 script pointers retain bit15. The shared bank-1 command forms clear
; that bit; these explicit forms preserve the same dispatcher operations.
.macro UnversionedJumpEncoded target
    .byte $04
    .word target
.endmacro
.macro UnversionedBranchFieldEqual target, value
    .byte $24
    .word target
    .byte value
.endmacro
.macro UnversionedBranchSlot0360AtMost target, value
    .byte $1B
    .word target
    .byte value
.endmacro
.macro UnversionedBranchValueEqual target, value
    .byte $53
    .word target, value
.endmacro
.macro UnversionedLoadIndexed pointer
    .byte $54
    .word pointer
.endmacro

; These records use the existing nine-byte loader format. Descriptor 1E names
; A1E5, and descriptor 1F names A294. A1EE retains the same valid frame/script
; relationships, with no ordinary caller claimed. Their tenth fetch is
; lookahead outside the record; it is not another record field.
.macro UnversionedBank0SlotScripts
UnversionedRecordA1E5:
    SlotRuntimeRecord UnversionedSpriteFrame096, UnversionedScriptA1F7, $00, $FF, $00, $00, $00 ; CONTROL_UNVERSIONED_RECORD_A1E5
UnversionedRecordA1EE:
    SlotRuntimeRecord UnversionedSpriteFrame095, UnversionedScriptA203, $00, $FF, $00, $00, $00 ; CONTROL_UNVERSIONED_RECORD_A1EE
UnversionedScriptA1F7:
    BogusSetSlot07F0 $02 ; CONTROL_UNVERSIONED_SCRIPT_A1F7
    BogusInitializeOtherSlotAbsolute $1F, $00, $91, $00
UnversionedScriptA1FE:
    BogusClearSlot0790Bits $01
UnversionedScriptA200:
    UnversionedJumpEncoded UnversionedScriptA200
UnversionedScriptA203:
    UnversionedBranchFieldEqual UnversionedScriptA221, $00 ; CONTROL_UNVERSIONED_SCRIPT_A203
    BogusLoadRecordAndClearSavedState $1A
    BogusLoadSlotRecordAtPointer $002D
UnversionedScriptA20C:
    BogusRelinkToLastRelatedSlot
    BogusWait $01
    BogusSetSlotFields80 $00, $48
    BogusWait $01
    BogusRestartVoice4 $2710
    UnversionedBranchSlot0360AtMost UnversionedScriptA21E, $00
    ; This successor enters the low pointer byte of the preceding 16 command.
    ; Its 2D/00/B8 view overlaps the record-load command and the B8
    ; command. The source preserves both actual byte interpretations.
UnversionedScriptA20A = UnversionedScriptA20C - 2
    UnversionedJumpEncoded UnversionedScriptA20A
UnversionedScriptA21E:
    UnversionedJumpEncoded UnversionedScriptA21E
UnversionedScriptA221:
    BogusWait $12
    BogusLoadSlotRecord $00, $01
    UnversionedJumpEncoded UnversionedScriptA1FE
.assert * = $A229, error, "unversioned first slot scripts end"

; ScriptA29D selects one of six pointers, then reads these lists bytewise
; through 54, masks away the fetched high-byte lookahead, and creates the
; selected descriptor through 61. Zero ends each list. All IDs name entries
; within the own 123-entry descriptor table. These are descriptor IDs, not
; tile artwork or another speculative script decode.
UnversionedDescriptorListA229:
    .byte $0E, $15, $11, $12, $1C, $1D, $1A, $1B, $2A, $2B, $18, $19, $00 ; CONTROL_UNVERSIONED_DESCRIPTOR_LIST_A229
UnversionedDescriptorListA236:
    .byte $2E, $2F, $30, $31, $32, $33, $34, $35, $36, $37, $23, $24, $38, $39, $00
UnversionedDescriptorListA245:
    .byte $27, $28, $3C, $3D, $3E, $3F, $42, $43, $44, $45, $48, $49, $4A, $4B, $00
UnversionedDescriptorListA254:
    .byte $4C, $4D, $4E, $4F, $50, $51, $52, $53, $54, $55, $25, $26, $56, $57, $58, $59, $16, $17, $00
UnversionedDescriptorListA267:
    .byte $68, $68, $68, $68, $68, $68, $68, $69, $69, $69, $69, $69, $69, $69, $00
UnversionedDescriptorListsA276:
    .word UnversionedDescriptorListA229, UnversionedDescriptorListA229 ; CONTROL_UNVERSIONED_DESCRIPTOR_LIST_POINTERS
    .word UnversionedDescriptorListA236, UnversionedDescriptorListA245
    .word UnversionedDescriptorListA254, UnversionedDescriptorListA267
UnversionedListPalettesA282:
    .word UnversionedPalette01, UnversionedPalette01, UnversionedPalette03 ; CONTROL_UNVERSIONED_LIST_PALETTE_POINTERS
    .word UnversionedPalette02, UnversionedPalette02, UnversionedPalette01
; The indexed two-byte read has byte lookahead here too: selector 3D stores
; only the low byte at $0140+$3D. Preserve the following record as the lookahead
; after the sixth value rather than inventing a seventh named entry.
UnversionedStateChoicesA28E:
    .byte $00, $05, $06, $28, $28, $1E ; CONTROL_UNVERSIONED_STATE_CHOICES
UnversionedRecordA294:
    SlotRuntimeRecord UnversionedSpriteFrame049, UnversionedScriptA29D, $00, $FF, $00, $00, $00 ; CONTROL_UNVERSIONED_RECORD_A294
UnversionedScriptA29D:
    BogusSetSlotC0 $00 ; CONTROL_UNVERSIONED_SCRIPT_A29D
    BogusSetSlotValue $0002
    BogusMultiplySlotValueByArray $3D
    BogusStoreSlotValueArray $FF
    UnversionedLoadIndexed UnversionedListPalettesA282
    BogusSetSpritePalettePointer $0000
    BogusLoadSlotValueArray $FF
    UnversionedLoadIndexed UnversionedDescriptorListsA276
UnversionedScriptA2B1:
    BogusStoreSlotValueArray $FF
    UnversionedLoadIndexed $0000
    BogusMaskSlotValue $00FF
    UnversionedBranchValueEqual UnversionedScriptA2D4, $0000
    BogusInitializeOtherSlotAbsolute $00, $04, $82, $00
    BogusWait $03
    BogusMarkMatchingSlots $28, $01, $00, $00
    BogusWait $1E
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $0001
    UnversionedJumpEncoded UnversionedScriptA2B1
UnversionedScriptA2D4:
    BogusMarkMatchingSlots $80, $01, $1E, $00
    BogusWait $28
    BogusSetBackgroundPalettePointer UnversionedPalette05
    BogusSetSpritePalettePointer UnversionedPalette05
    BogusLoadSlotValueArray $3D
    BogusStoreSlotValueArray $FF
    UnversionedLoadIndexed UnversionedStateChoicesA28E
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusLoadSlotValueArray $FF
UnversionedScriptA2EE:
    BogusAddSlotValue $0001
    UnversionedBranchValueEqual UnversionedScriptA2FD, $0006
    UnversionedBranchValueEqual UnversionedScriptA2EE, $0004
    BogusSetMainState $00
UnversionedScriptA2FD:
    BogusSetSlotValue $00FF
    UnversionedJumpEncoded $7426 ; Bank 1 $F426; incoming/outgoing bank1 source integration remains open.
.assert * = $A303, error, "unversioned bank0 slot scripts end"
.endmacro
