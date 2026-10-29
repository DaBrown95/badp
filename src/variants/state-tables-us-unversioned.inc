; Own 21-state tables. The state bank selector is also the negative-fourth-
; operand fallback of command 6D. Values retain both supported consumers.
InitialVerticalBaseSeeds:
    .byte $03, $28, $28, $28, $28, $28, $19, $19, $19, $19, $19, $19, $10, $32, $0A, $08, $58, $00, $03, $00, $00 ; CONTROL_UNVERSIONED_STATE_INITIALVERTICALBASESEEDS
.assert * = $A49C, error, "unversioned InitialVerticalBaseSeeds end"
StateBankSelectors:
    .byte $0E, $00, $06, $04, $04, $00, $08, $08, $08, $08, $08, $08, $0A, $0A, $0A, $0A, $0C, $0E, $0E, $FF, $FF ; CONTROL_UNVERSIONED_STATE_STATEBANKSELECTORS
.assert * = $A4B1, error, "unversioned StateBankSelectors end"
BackgroundPalettePointers:
    .word UnversionedPalette23 ; CONTROL_UNVERSIONED_STATE_BACKGROUNDPALETTEPOINTERS
    .word UnversionedPalette06
    .word UnversionedPalette07
    .word UnversionedPalette06
    .word UnversionedPalette06
    .word UnversionedPalette06
    .word UnversionedPalette15
    .word UnversionedPalette16
    .word UnversionedPalette17
    .word UnversionedPalette18
    .word UnversionedPalette19
    .word UnversionedPalette20
    .word UnversionedPalette11
    .word UnversionedPalette11
    .word UnversionedPalette13
    .word UnversionedPalette11
    .word UnversionedPalette12
    .word UnversionedPalette23
    .word UnversionedPalette23
    .word UnversionedPalette05
    .word UnversionedPalette06
.assert * = $A4DB, error, "unversioned BackgroundPalettePointers end"
SpritePalettePointers:
    .word UnversionedPalette23 ; CONTROL_UNVERSIONED_STATE_SPRITEPALETTEPOINTERS
    .word UnversionedPalette01
    .word UnversionedPalette03
    .word UnversionedPalette02
    .word UnversionedPalette02
    .word UnversionedPalette01
    .word UnversionedPalette14
    .word UnversionedPalette14
    .word UnversionedPalette14
    .word UnversionedPalette21
    .word UnversionedPalette21
    .word UnversionedPalette21
    .word UnversionedPalette09
    .word UnversionedPalette09
    .word UnversionedPalette09
    .word UnversionedPalette09
    .word UnversionedPalette10
    .word UnversionedPalette23
    .word UnversionedPalette23
    .word UnversionedPalette05
    .word UnversionedPalette01
.assert * = $A505, error, "unversioned SpritePalettePointers end"
