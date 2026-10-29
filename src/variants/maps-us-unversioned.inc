; Own map metadata. The nominal table has21 state pointers and144 indices.
; Actual grid headers/strides retain the shared format; tile indices remain
; editable local assets. Conditional overlapping uses are not excluded.
.macro UnversionedBank0MapData
SlotRelatedAddressTable:
    .word UnversionedMapLayoutA44D ; CONTROL_UNVERSIONED_MAP_STATE_00
    .word Bank1::UnversionedMapLayoutF42C - $8000
    .word Bank1::UnversionedMapLayoutF42C - $8000
    .word Bank1::UnversionedMapLayoutF42C - $8000
    .word Bank1::UnversionedMapLayoutF42C - $8000
    .word Bank1::UnversionedMapLayoutF42C - $8000
    .word Bank1::UnversionedMapLayoutF944 - $8000
    .word Bank1::UnversionedMapLayoutFA3B - $8000
    .word Bank1::UnversionedMapLayoutFB32 - $8000
    .word Bank1::UnversionedMapLayoutFA3B - $8000
    .word Bank1::UnversionedMapLayoutF944 - $8000
    .word Bank1::UnversionedMapLayoutFB32 - $8000
    .word Bank1::UnversionedMapLayoutF604 - $8000
    .word Bank1::UnversionedMapLayoutF6AE - $8000
    .word Bank1::UnversionedMapLayoutF714 - $8000
    .word Bank1::UnversionedMapLayoutF770 - $8000
    .word Bank1::UnversionedMapLayoutF852 - $8000
    .word UnversionedMapLayoutA475
    .word UnversionedMapLayoutA44D
    .word UnversionedMapLayoutA463
    .word UnversionedMapLayoutA463
.assert * = $A32D, error, "unversioned map pointer table end"
MapChunkOffsets:
    .word $44 * $00 ; CONTROL_UNVERSIONED_MAP_CHUNK_OFFSETS
    .word $44 * $00
    .word $44 * $01
    .word $44 * $02
    .word $44 * $03
    .word $44 * $04
    .word $44 * $05
    .word $44 * $06
    .word $44 * $07
    .word $44 * $08
    .word $44 * $09
    .word $44 * $0A
    .word $44 * $0B
    .word $44 * $0C
    .word $44 * $4E
    .word $44 * $60
    .word $44 * $0D
    .word $44 * $0E
    .word $44 * $0F
    .word $44 * $10
    .word $44 * $11
    .word $44 * $12
    .word $44 * $5A
    .word $44 * $13
    .word $44 * $14
    .word $44 * $15
    .word $44 * $87
    .word $44 * $17
    .word $44 * $18
    .word $44 * $19
    .word $44 * $1A
    .word $44 * $1B
    .word $44 * $1C
    .word $44 * $1D
    .word $44 * $1E
    .word $44 * $1F
    .word $44 * $20
    .word $44 * $21
    .word $44 * $22
    .word $44 * $23
    .word $44 * $24
    .word $44 * $25
    .word $44 * $26
    .word $44 * $27
    .word $44 * $28
    .word $44 * $29
    .word $44 * $2A
    .word $44 * $2B
    .word $44 * $2C
    .word $44 * $2D
    .word $44 * $2E
    .word $44 * $2F
    .word $44 * $30
    .word $44 * $31
    .word $44 * $32
    .word $44 * $33
    .word $44 * $34
    .word $44 * $35
    .word $44 * $36
    .word $44 * $59
    .word $44 * $38
    .word $44 * $39
    .word $44 * $3A
    .word $44 * $3B
    .word $44 * $55
    .word $44 * $3C
    .word $44 * $3D
    .word $44 * $3E
    .word $44 * $3F
    .word $44 * $79
    .word $44 * $40
    .word $44 * $53
    .word $44 * $5F
    .word $44 * $41
    .word $44 * $42
    .word $44 * $69
    .word $44 * $54
    .word $44 * $7B
    .word $44 * $4F
    .word $44 * $7A
    .word $44 * $5B
    .word $44 * $43
    .word $44 * $45
    .word $44 * $46
    .word $44 * $47
    .word $44 * $48
    .word $44 * $49
    .word $44 * $4A
    .word $44 * $4B
    .word $44 * $4C
    .word $44 * $4D
    .word $44 * $57
    .word $44 * $50
    .word $44 * $7C
    .word $44 * $61
    .word $44 * $62
    .word $44 * $63
    .word $44 * $64
    .word $44 * $65
    .word $44 * $66
    .word $44 * $67
    .word $44 * $68
    .word $44 * $6A
    .word $44 * $75
    .word $44 * $76
    .word $44 * $77
    .word $44 * $78
    .word $44 * $7D
    .word $44 * $7E
    .word $44 * $7F
    .word $44 * $80
    .word $44 * $5E
    .word $44 * $81
    .word $44 * $82
    .word $44 * $83
    .word $44 * $84
    .word $44 * $51
    .word $44 * $5C
    .word $44 * $5D
    .word $44 * $6B
    .word $44 * $6C
    .word $44 * $6D
    .word $44 * $6E
    .word $44 * $6F
    .word $44 * $70
    .word $44 * $71
    .word $44 * $72
    .word $44 * $56
    .word $44 * $52
    .word $44 * $73
    .word $44 * $74
    .word $44 * $58
    .word $44 * $85
    .word $44 * $86
    .word $44 * $88
    .word $44 * $89
    .word $44 * $8A
    .word $44 * $8B
    .word $44 * $44
    .word $44 * $8C
    .word $44 * $8D
    .word $44 * $8E
    .word $44 * $8F
    .word $44 * $37
.assert * = $A44D, error, "unversioned chunk offset table end"
UnversionedMapLayoutA44D:
    MapLayoutDimensions $04, $05 ; CONTROL_UNVERSIONED_MAP_HEADER_A44D
    .incbin "unversioned-map-layout-0-a44d.bin"
.assert * = $A463, error, "unversioned map layout extent"
UnversionedMapLayoutA463:
    MapLayoutDimensions $04, $04 ; CONTROL_UNVERSIONED_MAP_HEADER_A463
    .incbin "unversioned-map-layout-0-a463.bin"
.assert * = $A475, error, "unversioned map layout extent"
UnversionedMapLayoutA475:
    MapLayoutDimensions $04, $04 ; CONTROL_UNVERSIONED_MAP_HEADER_A475
    .incbin "unversioned-map-layout-0-a475.bin"
.assert * = $A487, error, "unversioned map layout extent"
.endmacro

.macro UnversionedBank1MapData
UnversionedMapLayoutF42C:
    MapLayoutDimensions $34, $09 ; CONTROL_UNVERSIONED_MAP_HEADER_F42C
    .incbin "unversioned-map-layout-1-f42c.bin"
.assert * = $F602, error, "unversioned map layout extent"
; Retained suffix after the52*9 grid. Its first byte is discarded high-byte
; lookahead. No extra-cell interpretation or original purpose is claimed.
RetainedMapSuffixF623:
    .byte $1E, $15 ; CONTROL_UNVERSIONED_RETAINED_MAP_SUFFIX
.assert * = $F604, error, "unversioned retained map suffix end"
UnversionedMapLayoutF604:
    MapLayoutDimensions $1C, $06 ; CONTROL_UNVERSIONED_MAP_HEADER_F604
    .incbin "unversioned-map-layout-1-f604.bin"
.assert * = $F6AE, error, "unversioned map layout extent"
UnversionedMapLayoutF6AE:
    MapLayoutDimensions $0A, $0A ; CONTROL_UNVERSIONED_MAP_HEADER_F6AE
    .incbin "unversioned-map-layout-1-f6ae.bin"
.assert * = $F714, error, "unversioned map layout extent"
UnversionedMapLayoutF714:
    MapLayoutDimensions $12, $05 ; CONTROL_UNVERSIONED_MAP_HEADER_F714
    .incbin "unversioned-map-layout-1-f714.bin"
.assert * = $F770, error, "unversioned map layout extent"
UnversionedMapLayoutF770:
    MapLayoutDimensions $20, $07 ; CONTROL_UNVERSIONED_MAP_HEADER_F770
    .incbin "unversioned-map-layout-1-f770.bin"
.assert * = $F852, error, "unversioned map layout extent"
UnversionedMapLayoutF852:
    MapLayoutDimensions $10, $0F ; CONTROL_UNVERSIONED_MAP_HEADER_F852
    .incbin "unversioned-map-layout-1-f852.bin"
.assert * = $F944, error, "unversioned map layout extent"
UnversionedMapLayoutF944:
    MapLayoutDimensions $23, $07 ; CONTROL_UNVERSIONED_MAP_HEADER_F944
    .incbin "unversioned-map-layout-1-f944.bin"
.assert * = $FA3B, error, "unversioned map layout extent"
UnversionedMapLayoutFA3B:
    MapLayoutDimensions $23, $07 ; CONTROL_UNVERSIONED_MAP_HEADER_FA3B
    .incbin "unversioned-map-layout-1-fa3b.bin"
.assert * = $FB32, error, "unversioned map layout extent"
UnversionedMapLayoutFB32:
    MapLayoutDimensions $25, $07 ; CONTROL_UNVERSIONED_MAP_HEADER_FB32
    .incbin "unversioned-map-layout-1-fb32.bin"
.assert * = $FC37, error, "unversioned map layout extent"
.endmacro
