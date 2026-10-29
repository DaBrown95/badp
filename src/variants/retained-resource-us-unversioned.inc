; Retained resource-shaped data after the final grid. The complete five-byte
; frame view is identical to bank0 BA8D, including the zero attribute byte
; that also begins the following zero-storage run.
; The word points to the following frame-shaped data in the bank-relative
; namespace. The 8A/01/01 header agrees with this release's separate-dimension
; frame format; its tile/attribute pair remains a local editable input. This is a provisional
; data interpretation, not a claim that the engine renders this frame.
; Several record resources contain literal CPU address $7C37. Native sprite
; consumers do not convert that address to $FC37. Preserve that distinction;
; neither an ordinary valid PRG resource use nor original purpose is proved.
UnversionedRetainedResourceFC37:
    .word UnversionedRetainedFrameFC39 - BankStart ; CONTROL_UNVERSIONED_RETAINED_RESOURCE_WORD
UnversionedRetainedFrameFC39:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_RETAINED_FRAME_FLAGS
    .byte $01, $01 ; Separate width and height, provisional frame view.
    .incbin "unversioned-retained-resource-tile.bin"
.assert * = $FC3E, error, "own retained resource/frame overlap end"
