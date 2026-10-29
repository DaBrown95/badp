; Own21-state position pointer tables and420 eight-byte records.
; Native search/copy consumers retain their original field and range-bit
; behavior. The one nonmonotonic stream remains in its reference order.
.macro UnversionedPositionData
PositionRecordPointersA:
    .word UnversionedPositionStreamA559 ; CONTROL_UNVERSIONED_POSITION_POINTERS_A
    .word UnversionedPositionStreamA6B9
    .word UnversionedPositionStreamA775
    .word UnversionedPositionStreamA841
    .word UnversionedPositionStreamA841
    .word UnversionedPositionStreamA91D
    .word UnversionedPositionStreamAAF5
    .word UnversionedPositionStreamABB1
    .word UnversionedPositionStreamAC7D
    .word UnversionedPositionStreamAD09
    .word UnversionedPositionStreamADBD
    .word UnversionedPositionStreamAE39
    .word UnversionedPositionStreamAF69
    .word UnversionedPositionStreamB02D
    .word UnversionedPositionStreamB0B9
    .word UnversionedPositionStreamB13D
    .word UnversionedPositionStreamB209
    .word UnversionedPositionStreamA56D
    .word UnversionedPositionStreamB2BD
    .word UnversionedPositionStreamA581
    .word UnversionedPositionStreamB2D1
.assert * = $A52F, error, "unversioned position pointersA end"
PositionRecordPointersB:
    .word UnversionedPositionStreamA559 ; CONTROL_UNVERSIONED_POSITION_POINTERS_B
    .word UnversionedPositionStreamA595
    .word UnversionedPositionStreamA595
    .word UnversionedPositionStreamA595
    .word UnversionedPositionStreamA595
    .word UnversionedPositionStreamA595
    .word UnversionedPositionStreamAAA9
    .word UnversionedPositionStreamAABD
    .word UnversionedPositionStreamAAD9
    .word UnversionedPositionStreamAABD
    .word UnversionedPositionStreamAAA9
    .word UnversionedPositionStreamAAD9
    .word UnversionedPositionStreamAEFD
    .word UnversionedPositionStreamAF31
    .word UnversionedPositionStreamAF3D
    .word UnversionedPositionStreamAF49
    .word UnversionedPositionStreamAF5D
    .word UnversionedPositionStreamB2E5
    .word UnversionedPositionStreamB2E5
    .word UnversionedPositionStreamB2E5
    .word UnversionedPositionStreamB2E5
.assert * = $A559, error, "unversioned position pointersB end"
UnversionedPositionStreamA559:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A559
    PositionRecord $0000, $0000, $F0, $00, $10, $00, $FF, $FF ; CONTROL_UNVERSIONED_POSITION_CONSTRUCTOR_A559
    PositionRecordEnd
.assert * = $A56D, error, "unversioned position stream end"
UnversionedPositionStreamA56D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A56D
    PositionRecord $001F, $0000, $F0, $09, $00, $00, $FF, $FF
    PositionRecordEnd
.assert * = $A581, error, "unversioned position stream end"
UnversionedPositionStreamA581:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A581
    PositionRecord $000A, $0000, $F0, $13, $10, $00, $FF, $FF
    PositionRecordEnd
.assert * = $A595, error, "unversioned position stream end"
UnversionedPositionStreamA595:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A595
    PositionRecord $0003, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $000B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $001B, $8000, $32, $36, $80, $00, $08, $08
    PositionRecord $0023, $8000, $22, $26, $80, $02, $08, $08
    PositionRecord $003B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0043, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $004B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0053, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $005B, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $0063, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $006B, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $0073, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $007B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0083, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $008B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0093, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $009E, $8000, $31, $3C, $01, $00, $00, $00
    PositionRecord $00D3, $8000, $23, $25, $0D, $00, $08, $08
    PositionRecord $00D5, $8000, $23, $25, $0D, $00, $08, $08
    PositionRecord $0113, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $011B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0123, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $012B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0133, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $0153, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $015B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0163, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $016B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0173, $8000, $01, $3E, $01, $00, $00, $00
    PositionRecord $017B, $8000, $01, $3B, $01, $00, $00, $00
    PositionRecord $0181, $8000, $1A, $46, $01, $00, $00, $00
    PositionRecord $0189, $8000, $34, $3D, $01, $00, $00, $00
    PositionRecord $018B, $8000, $22, $26, $00, $83, $08, $08
    PositionRecord $0193, $8000, $32, $36, $00, $81, $08, $08
    PositionRecord $0199, $8000, $1E, $46, $01, $00, $00, $00
    PositionRecordEnd
.assert * = $A6B9, error, "unversioned position stream end"
UnversionedPositionStreamA6B9:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A6B9
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF
    PositionRecord $0005, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0014, $0000, $F0, $0E, $3C, $00, $FF, $02
    PositionRecord $0040, $0000, $F0, $19, $3C, $00, $FF, $03
    PositionRecord $005C, $0000, $F0, $0A, $3C, $13, $FF, $01
    PositionRecord $0087, $0000, $F0, $11, $3A, $00, $FF, $04
    PositionRecord $00B0, $0000, $F0, $18, $3C, $00, $FF, $05
    PositionRecord $00B9, $0000, $F0, $2B, $34, $00, $FF, $06
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00E1, $0000, $F0, $1C, $19, $00, $FF, $07
    PositionRecord $00E2, $0000, $F0, $0A, $2C, $1A, $FF, $08
    PositionRecord $00F4, $0000, $F0, $0F, $37, $00, $FF, $3E
    PositionRecord $00F6, $0000, $F0, $15, $13, $00, $FF, $09
    PositionRecord $0126, $0000, $F0, $0A, $3C, $17, $FF, $0A
    PositionRecord $0127, $0000, $F0, $22, $34, $00, $FF, $3F
    PositionRecord $013E, $0000, $F0, $2A, $3C, $00, $FF, $0B
    PositionRecord $0160, $0000, $F0, $1D, $2A, $00, $FF, $0C
    PositionRecord $016F, $0000, $F0, $12, $3A, $00, $FF, $0D
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecord $018E, $0000, $F0, $1B, $44, $00, $FF, $0E
    PositionRecord $0195, $0000, $F0, $1A, $1C, $00, $FF, $0F
    PositionRecordEnd
.assert * = $A775, error, "unversioned position stream end"
UnversionedPositionStreamA775:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A775
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF
    PositionRecord $0003, $0000, $F0, $37, $3C, $00, $FF, $10
    PositionRecord $000A, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0024, $0000, $F0, $0A, $33, $0C, $FF, $01
    PositionRecord $0027, $0000, $F0, $60, $16, $00, $FF, $40
    PositionRecord $0039, $0000, $F0, $38, $1E, $00, $FF, $11
    PositionRecord $0041, $0000, $F0, $2F, $3C, $00, $FF, $12
    PositionRecord $0081, $0000, $F0, $33, $20, $00, $FF, $13
    PositionRecord $008D, $0000, $F0, $2E, $31, $00, $FF, $14
    PositionRecord $00A2, $0000, $F0, $23, $13, $00, $FF, $15
    PositionRecord $00A4, $0000, $F0, $0A, $30, $0A, $FF, $16
    PositionRecord $00B4, $0000, $F0, $30, $34, $00, $FF, $17
    PositionRecord $00BC, $0000, $F0, $32, $24, $00, $FF, $18
    PositionRecord $00D3, $0000, $F0, $60, $30, $00, $FF, $42
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00DC, $0000, $F0, $0A, $34, $19, $FF, $19
    PositionRecord $00E1, $0000, $F0, $34, $0B, $00, $FF, $1A
    PositionRecord $00E6, $0000, $F0, $31, $1C, $00, $FF, $1B
    PositionRecord $0101, $0000, $F0, $39, $1C, $00, $FF, $1C
    PositionRecord $0126, $0000, $F0, $24, $3C, $00, $FF, $1D
    PositionRecord $0135, $0000, $F0, $36, $3C, $00, $FF, $1E
    PositionRecord $0151, $0000, $F0, $35, $39, $00, $FF, $1F
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecordEnd
.assert * = $A841, error, "unversioned position stream end"
UnversionedPositionStreamA841:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A841
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF
    PositionRecord $0005, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0006, $0000, $F0, $43, $2C, $00, $FF, $20
    PositionRecord $001C, $0000, $F0, $3E, $2A, $00, $FF, $22
    PositionRecord $002A, $0000, $F0, $27, $3C, $00, $FF, $23
    PositionRecord $0056, $0000, $F0, $0F, $31, $00, $FF, $43
    PositionRecord $0057, $0000, $F0, $44, $16, $00, $FF, $04
    PositionRecord $0061, $0000, $F0, $4B, $22, $00, $FF, $25
    PositionRecord $0071, $0000, $F0, $49, $1E, $00, $FF, $26
    PositionRecord $0079, $0000, $F0, $0A, $2E, $26, $FF, $27
    PositionRecord $0086, $0000, $F0, $62, $24, $00, $FF, $00
    PositionRecord $00A4, $0000, $F0, $14, $30, $00, $FF, $44
    PositionRecord $00B1, $0000, $F0, $3D, $3C, $00, $FF, $29
    PositionRecord $00BD, $0000, $F0, $14, $18, $00, $FF, $45
    PositionRecord $00C2, $0000, $F0, $3C, $24, $00, $FF, $2B
    PositionRecord $00C6, $0000, $F0, $4A, $0D, $00, $FF, $2C
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00E3, $0000, $F0, $28, $3C, $00, $FF, $2D
    PositionRecord $0116, $0000, $F0, $48, $2E, $00, $FF, $2E
    PositionRecord $0129, $0000, $F0, $0A, $1E, $11, $FF, $2F
    PositionRecord $0136, $0000, $F0, $61, $31, $00, $FF, $46
    PositionRecord $0150, $0000, $F0, $42, $30, $00, $FF, $30
    PositionRecord $0157, $0000, $F0, $3F, $26, $00, $FF, $31
    PositionRecord $0166, $0000, $F0, $45, $24, $00, $FF, $32
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecordEnd
.assert * = $A91D, error, "unversioned position stream end"
UnversionedPositionStreamA91D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_A91D
    PositionRecord $0002, $0000, $F0, $0D, $2B, $00, $FF, $FF
    PositionRecord $0005, $0000, $F0, $01, $3A, $00, $FF, $FF
    PositionRecord $0007, $0000, $F0, $2C, $1F, $00, $FF, $53
    PositionRecord $0009, $0000, $F0, $0A, $3C, $0D, $FF, $54
    PositionRecord $000A, $0000, $F0, $69, $3C, $00, $FF, $55
    PositionRecord $0020, $0000, $F0, $0A, $16, $04, $FF, $56
    PositionRecord $0029, $0000, $F0, $68, $3C, $00, $FF, $57
    PositionRecord $002A, $0000, $F0, $2C, $13, $00, $FF, $58
    PositionRecord $0048, $0000, $F0, $68, $3C, $00, $FF, $5A
    PositionRecord $0049, $0000, $F0, $2D, $1F, $00, $FF, $5B
    PositionRecord $0061, $0000, $F0, $5C, $30, $00, $FF, $5D
    PositionRecord $0070, $0000, $F0, $2C, $28, $00, $FF, $5E
    PositionRecord $0071, $0000, $F0, $5F, $34, $00, $FF, $5F
    PositionRecord $0091, $0000, $F0, $5F, $18, $00, $FF, $62
    PositionRecord $0096, $0000, $F0, $5F, $22, $00, $FF, $63
    PositionRecord $00A2, $0000, $F0, $68, $0D, $00, $FF, $64
    PositionRecord $00A7, $0000, $F0, $69, $24, $00, $FF, $65
    PositionRecord $00A8, $0000, $F0, $68, $13, $00, $FF, $66
    PositionRecord $00AB, $0000, $F0, $69, $34, $00, $FF, $67
    PositionRecord $00BF, $0000, $F0, $68, $24, $00, $FF, $68
    PositionRecord $00C0, $0000, $F0, $2C, $22, $00, $FF, $69
    PositionRecord $00CD, $0000, $F0, $69, $2C, $00, $FF, $6A
    PositionRecord $00D4, $0000, $F0, $6B, $1E, $00, $FF, $FF
    PositionRecord $00DA, $0000, $F0, $0A, $28, $15, $FF, $6B
    PositionRecord $00DC, $0000, $F0, $5C, $19, $00, $FF, $6C
    PositionRecord $00DD, $0000, $F0, $5F, $30, $00, $FF, $6D
    PositionRecord $00EE, $0000, $F0, $69, $1C, $00, $FF, $6E
    PositionRecord $00F2, $0000, $F0, $5F, $37, $00, $FF, $6F
    PositionRecord $00F5, $0000, $F0, $0A, $37, $01, $FF, $71
    PositionRecord $00F9, $0000, $F0, $69, $2C, $00, $FF, $72
    PositionRecord $00FA, $0000, $F0, $2C, $0B, $00, $FF, $73
    PositionRecord $0101, $0000, $F0, $68, $13, $00, $FF, $74
    PositionRecord $0119, $0000, $F0, $5F, $2C, $00, $FF, $75
    PositionRecord $011A, $0000, $F0, $68, $3C, $00, $FF, $76
    PositionRecord $0136, $0000, $F0, $2D, $2F, $00, $FF, $78
    PositionRecord $0144, $0000, $F0, $69, $3C, $00, $FF, $79
    PositionRecord $0151, $0000, $F0, $5C, $1E, $00, $FF, $7A
    PositionRecord $015D, $0000, $F0, $2C, $16, $00, $FF, $7B
    PositionRecord $015E, $0000, $F0, $29, $3C, $00, $FF, $7C
    PositionRecord $0168, $0000, $F0, $5F, $24, $00, $FF, $7D
    PositionRecord $016C, $0000, $F0, $5C, $3C, $00, $FF, $7F
    PositionRecord $0177, $0000, $F0, $5C, $16, $00, $FF, $80
    PositionRecord $0178, $0000, $F0, $68, $3C, $00, $FF, $81
    PositionRecord $017F, $0000, $F2, $00, $00, $00, $00, $00
    PositionRecord $0180, $0000, $F1, $00, $00, $00, $00, $00
    PositionRecord $0185, $0000, $F0, $5C, $34, $00, $FF, $82
    PositionRecord $0192, $0000, $F0, $0A, $1C, $02, $FF, $83
    PositionRecord $0195, $0000, $F0, $5C, $44, $00, $FF, $84
    PositionRecordEnd
.assert * = $AAA9, error, "unversioned position stream end"
UnversionedPositionStreamAAA9:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AAA9
    PositionRecord $0112, $8000, $01, $38, $07, $00, $00, $00
    PositionRecordEnd
.assert * = $AABD, error, "unversioned position stream end"
UnversionedPositionStreamAABD:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AABD
    PositionRecord $000B, $8000, $0F, $19, $01, $00, $00, $00
    PositionRecord $0111, $8000, $01, $38, $07, $00, $00, $00
    PositionRecordEnd
.assert * = $AAD9, error, "unversioned position stream end"
UnversionedPositionStreamAAD9:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AAD9
    PositionRecord $000B, $8000, $0F, $18, $01, $00, $00, $00
    PositionRecord $0120, $8000, $01, $38, $07, $00, $00, $00
    PositionRecordEnd
.assert * = $AAF5, error, "unversioned position stream end"
UnversionedPositionStreamAAF5:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AAF5
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000C, $0000, $F0, $6A, $2E, $00, $FF, $01
    PositionRecord $002C, $0000, $F0, $63, $2F, $00, $FF, $02
    PositionRecord $0040, $0000, $F0, $63, $2B, $00, $FF, $03
    PositionRecord $0045, $0000, $F0, $63, $18, $00, $FF, $04
    PositionRecord $004B, $0000, $F0, $6C, $2A, $00, $FF, $05
    PositionRecord $0052, $0000, $F0, $0A, $11, $08, $FF, $6F
    PositionRecord $005A, $0000, $F0, $63, $12, $00, $FF, $06
    PositionRecord $006D, $0000, $F0, $6C, $11, $00, $FF, $07
    PositionRecord $0074, $0000, $F0, $6C, $2A, $00, $FF, $08
    PositionRecord $0087, $0000, $F0, $63, $2F, $00, $FF, $09
    PositionRecord $009D, $0000, $F0, $6C, $16, $00, $FF, $0A
    PositionRecord $00A4, $0000, $F0, $0A, $16, $14, $FF, $71
    PositionRecord $00AF, $0000, $F0, $02, $18, $00, $FF, $0B
    PositionRecord $00B0, $0000, $F0, $02, $2C, $00, $FF, $0C
    PositionRecord $00BD, $0000, $F0, $63, $2F, $00, $FF, $0D
    PositionRecord $00C7, $0000, $F0, $6C, $2A, $00, $FF, $0E
    PositionRecord $00CA, $0000, $F0, $0A, $2E, $09, $FF, $70
    PositionRecord $00EB, $0000, $F0, $6C, $2A, $00, $FF, $0F
    PositionRecord $00FC, $0000, $F0, $02, $28, $00, $FF, $10
    PositionRecord $010B, $0000, $F0, $02, $2C, $00, $FF, $11
    PositionRecordEnd
.assert * = $ABB1, error, "unversioned position stream end"
UnversionedPositionStreamABB1:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_ABB1
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000A, $0000, $F0, $0A, $1E, $13, $FF, $7B
    PositionRecord $000B, $0000, $F0, $6A, $24, $00, $FF, $12
    PositionRecord $0010, $0000, $F0, $6C, $16, $00, $FF, $13
    PositionRecord $0013, $0000, $F0, $63, $0F, $00, $FF, $14
    PositionRecord $0015, $0000, $F0, $6C, $2C, $00, $FF, $15
    PositionRecord $0027, $0000, $F0, $14, $1C, $00, $FF, $16
    PositionRecord $0032, $0000, $F0, $6C, $09, $00, $FF, $17
    PositionRecord $0046, $0000, $F0, $63, $27, $00, $FF, $18
    PositionRecord $004D, $0000, $F0, $0A, $2E, $1D, $FF, $79
    PositionRecord $0052, $0000, $F0, $6C, $22, $00, $FF, $19
    PositionRecord $0068, $0000, $F0, $63, $2F, $00, $FF, $1A
    PositionRecord $0096, $0000, $F0, $6C, $16, $00, $FF, $1B
; The next key decreases from0096 to006D in the reference. Preserve the
; stored order; no original intention or runtime-route claim is inferred.
    PositionRecord $006D, $0000, $F0, $6C, $2E, $00, $FF, $1C
    PositionRecord $0075, $0000, $F0, $6C, $2A, $00, $FF, $1D
    PositionRecord $0085, $0000, $F0, $02, $2C, $00, $FF, $1E
    PositionRecord $00A1, $0000, $F0, $14, $28, $00, $FF, $1F
    PositionRecord $00B9, $0000, $F0, $14, $08, $00, $FF, $20
    PositionRecord $00C2, $0000, $F0, $6C, $0B, $00, $FF, $21
    PositionRecord $00C6, $0000, $F0, $0A, $2E, $0F, $FF, $7A
    PositionRecord $00D7, $0000, $F0, $02, $24, $00, $FF, $22
    PositionRecord $00F1, $0000, $F0, $6C, $2E, $00, $FF, $23
    PositionRecord $010A, $0000, $F0, $6C, $2E, $00, $FF, $24
    PositionRecordEnd
.assert * = $AC7D, error, "unversioned position stream end"
UnversionedPositionStreamAC7D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AC7D
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $0015, $0000, $F0, $02, $16, $00, $FF, $25
    PositionRecord $001A, $0000, $F0, $6A, $1E, $00, $FF, $26
    PositionRecord $0020, $0000, $F0, $70, $0E, $00, $FF, $27
    PositionRecord $003B, $0000, $F0, $0A, $2C, $14, $FF, $83
    PositionRecord $0048, $0000, $F0, $02, $18, $00, $FF, $28
    PositionRecord $005A, $0000, $F0, $6C, $2E, $01, $FF, $29
    PositionRecord $006B, $0000, $F0, $14, $14, $00, $FF, $2A
    PositionRecord $007A, $0000, $F0, $02, $24, $00, $FF, $2B
    PositionRecord $008E, $0000, $F0, $70, $26, $00, $FF, $2C
    PositionRecord $0098, $0000, $F0, $6C, $2A, $01, $FF, $2D
    PositionRecord $00C8, $0000, $F0, $02, $18, $00, $FF, $2E
    PositionRecord $00CD, $0000, $F0, $0A, $2E, $16, $FF, $84
    PositionRecord $00DC, $0000, $F0, $6C, $16, $01, $FF, $2F
    PositionRecord $0109, $0000, $F0, $02, $2A, $00, $FF, $30
    PositionRecordEnd
.assert * = $AD09, error, "unversioned position stream end"
UnversionedPositionStreamAD09:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AD09
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF
    PositionRecord $0003, $0000, $F0, $6C, $2E, $01, $FF, $31
    PositionRecord $000A, $0000, $F0, $6C, $1E, $01, $FF, $32
    PositionRecord $000D, $0000, $F0, $01, $26, $00, $FF, $FF
    PositionRecord $000F, $0000, $F0, $63, $0F, $00, $FF, $33
    PositionRecord $0016, $0000, $F0, $6A, $2E, $00, $FF, $34
    PositionRecord $0024, $0000, $F0, $0A, $2E, $1F, $FF, $8D
    PositionRecord $0037, $0000, $F0, $6C, $2E, $01, $FF, $35
    PositionRecord $0046, $0000, $F0, $02, $24, $00, $FF, $36
    PositionRecord $005C, $0000, $F0, $02, $2C, $00, $FF, $37
    PositionRecord $005D, $0000, $F0, $6C, $14, $01, $FF, $38
    PositionRecord $0068, $0000, $F0, $6C, $0D, $01, $FF, $39
    PositionRecord $007B, $0000, $F0, $0A, $11, $22, $FF, $8E
    PositionRecord $0080, $0000, $F0, $02, $2C, $00, $FF, $3A
    PositionRecord $0094, $0000, $F0, $6C, $2E, $01, $FF, $3B
    PositionRecord $00A3, $0000, $F0, $02, $1C, $00, $FF, $3C
    PositionRecord $00B6, $0000, $F0, $02, $2C, $00, $FF, $3D
    PositionRecord $00BC, $0000, $F0, $6C, $0C, $01, $FF, $3E
    PositionRecord $00C6, $0000, $F0, $6C, $22, $01, $FF, $3F
    PositionRecord $00F5, $0000, $F0, $02, $2C, $00, $FF, $40
    PositionRecord $0108, $0000, $F0, $6C, $2E, $01, $FF, $41
    PositionRecordEnd
.assert * = $ADBD, error, "unversioned position stream end"
UnversionedPositionStreamADBD:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_ADBD
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000C, $0000, $F0, $6A, $2E, $00, $FF, $42
    PositionRecord $001D, $0000, $F0, $02, $2C, $00, $FF, $43
    PositionRecord $0040, $0000, $F0, $02, $28, $00, $FF, $44
    PositionRecord $0059, $0000, $F0, $6C, $2E, $02, $FF, $45
    PositionRecord $006B, $0000, $F0, $02, $25, $00, $FF, $46
    PositionRecord $0099, $0000, $F0, $63, $2F, $00, $FF, $47
    PositionRecord $00A3, $0000, $F0, $0A, $16, $23, $FF, $97
    PositionRecord $00AB, $0000, $F0, $0A, $24, $20, $FF, $98
    PositionRecord $00AD, $0000, $F0, $63, $2F, $00, $FF, $48
    PositionRecord $00CC, $0000, $F0, $02, $2C, $00, $FF, $49
    PositionRecord $00DB, $0000, $F0, $6C, $2E, $02, $FF, $4A
    PositionRecord $00FD, $0000, $F0, $02, $28, $00, $FF, $4B
    PositionRecordEnd
.assert * = $AE39, error, "unversioned position stream end"
UnversionedPositionStreamAE39:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AE39
    PositionRecord $0002, $0000, $F0, $0D, $1C, $00, $FF, $FF
    PositionRecord $0008, $0000, $F0, $01, $2C, $00, $FF, $FF
    PositionRecord $000C, $0000, $F0, $02, $0C, $00, $FF, $4C
    PositionRecord $0013, $0000, $F0, $6A, $1C, $00, $FF, $4D
    PositionRecord $002A, $0000, $F0, $02, $0C, $00, $FF, $4E
    PositionRecord $0047, $0000, $F0, $02, $2C, $00, $FF, $4F
    PositionRecord $0051, $0000, $F0, $0A, $1E, $25, $FF, $A1
    PositionRecord $0058, $0000, $F0, $70, $22, $00, $FF, $50
    PositionRecord $005A, $0000, $F0, $6C, $2E, $00, $FF, $51
    PositionRecord $0078, $0000, $F0, $6C, $01, $02, $FF, $52
    PositionRecord $0081, $0000, $F0, $6C, $2C, $02, $FF, $53
    PositionRecord $0089, $0000, $F0, $02, $24, $00, $FF, $54
    PositionRecord $0094, $0000, $F0, $6C, $2A, $02, $FF, $55
    PositionRecord $0097, $0000, $F0, $6C, $2A, $00, $FF, $56
    PositionRecord $009D, $0000, $F0, $02, $24, $00, $FF, $57
    PositionRecord $00CD, $0000, $F0, $02, $26, $00, $FF, $58
    PositionRecord $00D7, $0000, $F0, $6C, $0F, $02, $FF, $59
    PositionRecord $00DF, $0000, $F0, $6C, $2E, $00, $FF, $5A
    PositionRecord $00E4, $0000, $F0, $0A, $2E, $2A, $FF, $A2
    PositionRecord $00F1, $0000, $F0, $14, $1E, $00, $FF, $5B
    PositionRecord $0108, $0000, $F0, $6C, $2A, $02, $FF, $5C
    PositionRecord $010D, $0000, $F0, $14, $1C, $00, $FF, $5D
    PositionRecord $0110, $0000, $F0, $02, $26, $00, $FF, $5E
    PositionRecordEnd
.assert * = $AEFD, error, "unversioned position stream end"
UnversionedPositionStreamAEFD:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AEFD
    PositionRecord $0030, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $0040, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $0078, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $0090, $8000, $14, $25, $01, $00, $00, $00
    PositionRecord $00C0, $8000, $14, $25, $01, $00, $00, $00
    PositionRecordEnd
.assert * = $AF31, error, "unversioned position stream end"
UnversionedPositionStreamAF31:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AF31
    PositionRecordEnd
.assert * = $AF3D, error, "unversioned position stream end"
UnversionedPositionStreamAF3D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AF3D
    PositionRecordEnd
.assert * = $AF49, error, "unversioned position stream end"
UnversionedPositionStreamAF49:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AF49
    PositionRecord $0070, $8000, $1C, $2D, $01, $00, $00, $00
    PositionRecordEnd
.assert * = $AF5D, error, "unversioned position stream end"
UnversionedPositionStreamAF5D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AF5D
    PositionRecordEnd
.assert * = $AF69, error, "unversioned position stream end"
UnversionedPositionStreamAF69:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_AF69
    PositionRecord $0002, $0000, $F0, $0D, $13, $00, $FF, $FF
    PositionRecord $0004, $0000, $F0, $01, $22, $00, $FF, $FF
    PositionRecord $0006, $0000, $F0, $0A, $24, $0E, $FF, $BE
    PositionRecord $0009, $0000, $F0, $6E, $19, $00, $FF, $01
    PositionRecord $001C, $0000, $F0, $6E, $1C, $00, $FF, $02
    PositionRecord $0023, $0000, $F0, $6F, $24, $00, $FF, $03
    PositionRecord $002E, $0000, $F0, $6E, $1E, $00, $FF, $04
    PositionRecord $0042, $0000, $F0, $6E, $1D, $00, $FF, $05
    PositionRecord $004F, $0000, $F0, $71, $14, $00, $FF, $43
    PositionRecord $0054, $0000, $F0, $6E, $1C, $00, $FF, $06
    PositionRecord $005B, $0000, $F0, $6F, $0E, $00, $FF, $07
    PositionRecord $0064, $0000, $F0, $6F, $24, $00, $FF, $08
    PositionRecord $0067, $0000, $F0, $0A, $16, $21, $FF, $09
    PositionRecord $007A, $0000, $F0, $6E, $1D, $00, $FF, $0A
    PositionRecord $008B, $0000, $F0, $75, $22, $00, $FF, $0B
    PositionRecord $008F, $0000, $F0, $0A, $24, $13, $FF, $49
    PositionRecord $00A0, $0000, $F0, $73, $0E, $00, $FF, $44
    PositionRecord $00A1, $0000, $F0, $6E, $19, $00, $FF, $0D
    PositionRecord $00A4, $0000, $F0, $6F, $0E, $00, $FF, $0E
    PositionRecord $00A9, $0000, $F0, $0A, $19, $2C, $FF, $0F
    PositionRecord $00AB, $0000, $F0, $6E, $1C, $00, $FF, $10
    PositionRecord $00BE, $0000, $F0, $6E, $1E, $00, $FF, $11
    PositionRecord $00D9, $0000, $F0, $6B, $11, $00, $FF, $FF
    PositionRecordEnd
.assert * = $B02D, error, "unversioned position stream end"
UnversionedPositionStreamB02D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B02D
    PositionRecord $0002, $0000, $F0, $0D, $35, $00, $FF, $FF
    PositionRecord $0004, $0000, $F0, $01, $42, $00, $FF, $FF
    PositionRecord $0005, $0000, $F0, $73, $26, $00, $FF, $12
    PositionRecord $0006, $0000, $F0, $0A, $37, $0C, $FF, $48
    PositionRecord $000B, $0000, $F0, $73, $17, $00, $FF, $13
    PositionRecord $0019, $0000, $F0, $73, $31, $00, $FF, $14
    PositionRecord $001A, $0000, $F0, $6F, $0E, $00, $FF, $15
    PositionRecord $001B, $0000, $F0, $6F, $3A, $00, $FF, $16
    PositionRecord $0025, $0000, $F0, $73, $21, $00, $FF, $17
    PositionRecord $0027, $0000, $F0, $73, $0E, $00, $FF, $18
    PositionRecord $002D, $0000, $F0, $0A, $2F, $1C, $FF, $19
    PositionRecord $002E, $0000, $F0, $73, $39, $00, $FF, $1A
    PositionRecord $0039, $0000, $F0, $6F, $1E, $00, $FF, $1B
    PositionRecord $0043, $0000, $F0, $73, $26, $00, $FF, $1C
    PositionRecord $0049, $0000, $F0, $6B, $22, $00, $FF, $FF
    PositionRecord $004A, $0000, $F0, $6F, $39, $00, $FF, $1D
    PositionRecordEnd
.assert * = $B0B9, error, "unversioned position stream end"
UnversionedPositionStreamB0B9:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B0B9
    PositionRecord $0002, $0000, $F0, $0D, $0D, $00, $FF, $FF
    PositionRecord $0004, $0000, $F0, $01, $16, $00, $FF, $FF
    PositionRecord $001C, $0000, $F0, $73, $0E, $00, $FF, $1E
    PositionRecord $0020, $0000, $F0, $6F, $1C, $00, $FF, $1F
    PositionRecord $0038, $0000, $F0, $73, $0E, $00, $FF, $20
    PositionRecord $0040, $0000, $F0, $6F, $12, $00, $FF, $21
    PositionRecord $0044, $0000, $F0, $75, $19, $00, $FF, $22
    PositionRecord $004C, $0000, $F0, $73, $0A, $00, $FF, $23
    PositionRecord $0051, $0000, $F0, $74, $0E, $00, $FF, $46
    PositionRecord $0053, $0000, $F0, $6F, $16, $00, $FF, $24
    PositionRecord $0054, $0000, $F0, $6F, $0E, $00, $FF, $25
    PositionRecord $0062, $0000, $F0, $0A, $0E, $14, $FF, $26
    PositionRecord $006B, $0000, $F0, $74, $12, $00, $FF, $47
    PositionRecord $0079, $0000, $F0, $75, $0C, $00, $FF, $27
    PositionRecord $0089, $0000, $F0, $6B, $09, $00, $FF, $FF
    PositionRecordEnd
.assert * = $B13D, error, "unversioned position stream end"
UnversionedPositionStreamB13D:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B13D
    PositionRecord $0002, $0000, $F0, $0D, $0F, $00, $FF, $FF
    PositionRecord $0004, $0000, $F0, $01, $14, $00, $FF, $FF
    PositionRecord $000B, $0000, $F0, $71, $1E, $00, $FF, $28
    PositionRecord $0021, $0000, $F0, $73, $0E, $00, $FF, $29
    PositionRecord $0028, $0000, $F0, $6F, $0E, $00, $FF, $2A
    PositionRecord $002D, $0000, $F0, $6E, $1C, $00, $FF, $2B
    PositionRecord $002F, $0000, $F0, $6F, $2C, $00, $FF, $2F
    PositionRecord $003B, $0000, $F0, $0A, $1E, $18, $FF, $2C
    PositionRecord $003F, $0000, $F0, $72, $27, $00, $FF, $2D
    PositionRecord $004D, $0000, $F0, $6E, $24, $00, $FF, $2E
    PositionRecord $005E, $0000, $F0, $75, $2A, $00, $FF, $30
    PositionRecord $006E, $0000, $F0, $6E, $26, $00, $FF, $31
    PositionRecord $007E, $0000, $F0, $71, $16, $00, $FF, $32
    PositionRecord $0088, $0000, $F0, $0A, $24, $24, $FF, $2C
    PositionRecord $008C, $0000, $F0, $6E, $20, $00, $FF, $33
    PositionRecord $008F, $0000, $F0, $6F, $0E, $00, $FF, $34
    PositionRecord $00A0, $0000, $F0, $75, $2A, $00, $FF, $35
    PositionRecord $00A4, $0000, $F0, $6E, $23, $00, $FF, $36
    PositionRecord $00B4, $0000, $F0, $6F, $16, $00, $FF, $37
    PositionRecord $00B6, $0000, $F0, $71, $16, $00, $FF, $38
    PositionRecord $00C0, $0000, $F0, $72, $24, $00, $FF, $39
    PositionRecord $00D1, $0000, $F0, $73, $0E, $00, $FF, $3A
    PositionRecord $00ED, $0000, $F0, $6E, $23, $00, $FF, $3B
    PositionRecord $00F9, $0000, $F0, $6B, $19, $00, $FF, $FF
    PositionRecordEnd
.assert * = $B209, error, "unversioned position stream end"
UnversionedPositionStreamB209:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B209
    PositionRecord $0002, $0000, $F0, $0D, $5B, $00, $FF, $FF
    PositionRecord $0004, $0000, $F0, $01, $6A, $00, $FF, $FF
    PositionRecord $0018, $0000, $F0, $78, $5C, $00, $FF, $96
    PositionRecord $0023, $0000, $F0, $0A, $4E, $1B, $FF, $3D
    PositionRecord $002D, $0000, $F0, $74, $16, $00, $FF, $AE
    PositionRecord $0032, $0000, $F0, $78, $4A, $00, $FF, $FF
    PositionRecord $0033, $0000, $F0, $74, $1A, $00, $FF, $9D
    PositionRecord $0034, $0000, $F0, $78, $2A, $00, $FF, $FF
    PositionRecord $003B, $0000, $F0, $74, $29, $00, $FF, $AD
    PositionRecord $0040, $0000, $F0, $78, $0C, $00, $FF, $9E
    PositionRecord $0043, $0000, $F0, $74, $5A, $00, $FF, $AC
    PositionRecord $0045, $0000, $F0, $0A, $0E, $10, $FF, $3F
    PositionRecord $004B, $0000, $F0, $0A, $3E, $1C, $FF, $9A
    PositionRecord $0054, $0000, $F0, $74, $3E, $00, $FF, $99
    PositionRecord $005D, $0000, $F0, $0A, $54, $0B, $FF, $3E
    PositionRecord $0068, $0000, $F0, $79, $14, $00, $FF, $40
    PositionRecord $006C, $0000, $F0, $74, $52, $00, $FF, $AB
    PositionRecord $0073, $0000, $F0, $74, $22, $00, $FF, $AA
    PositionRecord $007B, $0000, $F0, $78, $31, $00, $FF, $FF
    PositionRecord $007C, $0000, $F0, $78, $42, $00, $FF, $FF
    PositionRecord $007E, $0000, $F0, $20, $08, $00, $FF, $42
    PositionRecordEnd
.assert * = $B2BD, error, "unversioned position stream end"
UnversionedPositionStreamB2BD:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B2BD
    PositionRecord $0000, $0000, $F0, $00, $10, $01, $FF, $FF
    PositionRecordEnd
.assert * = $B2D1, error, "unversioned position stream end"
UnversionedPositionStreamB2D1:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B2D1
    PositionRecord $001A, $0000, $F0, $1E, $0A, $00, $FF, $FF
    PositionRecordEnd
.assert * = $B2E5, error, "unversioned position stream end"
UnversionedPositionStreamB2E5:
    PositionRecord $0000, $0000, $00, $00, $00, $00, $00, $00 ; CONTROL_UNVERSIONED_POSITION_STREAM_B2E5
    PositionRecordEnd
.assert * = $B2F1, error, "unversioned position stream end"
.endmacro
