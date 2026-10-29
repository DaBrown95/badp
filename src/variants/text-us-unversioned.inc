; Own message caller and encoded bank-1 pointer table. The AB consumer
; reads ordinary PPU streams; message tile bytes remain local assets.
; The table has 51 entries before the first stream, with no runtime bound claim.
    BogusQueueStateAB $0000 ; CONTROL_UNVERSIONED_MESSAGE_QUEUE
ScriptBE60:
    BogusBranchIfSelectedFlags ScriptBE67, $B0
    BogusJumpBank1 ScriptBE60
ScriptBE67:
    BogusClearSelected3E
    BogusClearSelected40
    BogusInitializeSplitAndMainState
.assert * = $B788, error, "unversioned message caller end"
DataBE82:
UnversionedMessagePointers:
    .word UnversionedMessage00 - BankStart ; CONTROL_UNVERSIONED_MESSAGE_POINTERS
    .word UnversionedMessage01 - BankStart
    .word UnversionedMessage02 - BankStart
    .word UnversionedMessage03 - BankStart
    .word UnversionedMessage04 - BankStart
    .word UnversionedMessage05 - BankStart
    .word UnversionedMessage06 - BankStart
    .word UnversionedMessage07 - BankStart
    .word UnversionedMessage08 - BankStart
    .word UnversionedMessage09 - BankStart
    .word UnversionedMessage10 - BankStart
    .word UnversionedMessage11 - BankStart
    .word UnversionedMessage12 - BankStart
    .word UnversionedMessage13 - BankStart
    .word UnversionedMessage14 - BankStart
    .word UnversionedMessage15 - BankStart
    .word UnversionedMessage16 - BankStart
    .word UnversionedMessage17 - BankStart
    .word UnversionedMessage18 - BankStart
    .word UnversionedMessage19 - BankStart
    .word UnversionedMessage20 - BankStart
    .word UnversionedMessage21 - BankStart
    .word UnversionedMessage22 - BankStart
    .word UnversionedMessage23 - BankStart
    .word UnversionedMessage24 - BankStart
    .word UnversionedMessage25 - BankStart
    .word UnversionedMessage26 - BankStart
    .word UnversionedMessage27 - BankStart
    .word UnversionedMessage28 - BankStart
    .word UnversionedMessage29 - BankStart
    .word UnversionedMessage30 - BankStart
    .word UnversionedMessage31 - BankStart
    .word UnversionedMessage32 - BankStart
    .word UnversionedMessage33 - BankStart
    .word UnversionedMessage34 - BankStart
    .word UnversionedMessage35 - BankStart
    .word UnversionedMessage36 - BankStart
    .word UnversionedMessage37 - BankStart
    .word UnversionedMessage38 - BankStart
    .word UnversionedMessage39 - BankStart
    .word UnversionedMessage40 - BankStart
    .word UnversionedMessage41 - BankStart
    .word UnversionedMessage42 - BankStart
    .word UnversionedMessage43 - BankStart
    .word UnversionedMessage44 - BankStart
    .word UnversionedMessage45 - BankStart
    .word UnversionedMessage46 - BankStart
    .word UnversionedMessage47 - BankStart
    .word UnversionedMessage48 - BankStart
    .word UnversionedMessage49 - BankStart
    .word UnversionedMessage50 - BankStart
.assert * = $B7EE, error, "unversioned message pointer table end"
UnversionedMessage00:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_00_00
    .incbin "unversioned-message-00-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_00_02
    .incbin "unversioned-message-00-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_00_04
    .incbin "unversioned-message-00-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_00_06
    .incbin "unversioned-message-00-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_00_08
    .incbin "unversioned-message-00-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_00_10
.assert * = $B866, error, "unversioned message00 extent"
UnversionedMessage01:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_01_00
    .incbin "unversioned-message-01-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_01_02
    .incbin "unversioned-message-01-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_01_04
    .incbin "unversioned-message-01-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_01_06
    .incbin "unversioned-message-01-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_01_08
.assert * = $B8C7, error, "unversioned message01 extent"
UnversionedMessage02:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_02_00
    .incbin "unversioned-message-02-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_02_02
    .incbin "unversioned-message-02-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_02_04
    .incbin "unversioned-message-02-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_02_06
    .incbin "unversioned-message-02-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_02_08
.assert * = $B927, error, "unversioned message02 extent"
UnversionedMessage03:
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_03_00
    .incbin "unversioned-message-03-01.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_03_02
    .incbin "unversioned-message-03-03.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_03_04
    .incbin "unversioned-message-03-05.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_03_06
.assert * = $B973, error, "unversioned message03 extent"
UnversionedMessage04:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_04_00
    .incbin "unversioned-message-04-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_04_02
    .incbin "unversioned-message-04-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_04_04
    .incbin "unversioned-message-04-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_04_06
    .incbin "unversioned-message-04-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_04_08
    .incbin "unversioned-message-04-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_04_10
.assert * = $B9E3, error, "unversioned message04 extent"
UnversionedMessage05:
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_05_00
    .incbin "unversioned-message-05-01.bin"
    PpuStreamAbsolute $2207 ; CONTROL_UNVERSIONED_MESSAGE_05_02
    .incbin "unversioned-message-05-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_05_04
.assert * = $BA17, error, "unversioned message05 extent"
UnversionedMessage06:
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_06_00
    .incbin "unversioned-message-06-01.bin"
    PpuStreamAbsolute $220B ; CONTROL_UNVERSIONED_MESSAGE_06_02
    .incbin "unversioned-message-06-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_06_04
.assert * = $BA3F, error, "unversioned message06 extent"
UnversionedMessage07:
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_07_00
    .incbin "unversioned-message-07-01.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_07_02
.assert * = $BA5C, error, "unversioned message07 extent"
UnversionedMessage08:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_08_00
    .incbin "unversioned-message-08-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_08_02
    .incbin "unversioned-message-08-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_08_04
    .incbin "unversioned-message-08-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_08_06
    .incbin "unversioned-message-08-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_08_08
.assert * = $BAB0, error, "unversioned message08 extent"
UnversionedMessage09:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_09_00
    .incbin "unversioned-message-09-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_09_02
    .incbin "unversioned-message-09-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_09_04
    .incbin "unversioned-message-09-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_09_06
    .incbin "unversioned-message-09-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_09_08
    .incbin "unversioned-message-09-09.bin"
    PpuStreamAbsolute $2223 ; CONTROL_UNVERSIONED_MESSAGE_09_10
    .incbin "unversioned-message-09-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_09_12
.assert * = $BB3D, error, "unversioned message09 extent"
UnversionedMessage10:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_10_00
    .incbin "unversioned-message-10-01.bin"
    PpuStreamAbsolute $20E3 ; CONTROL_UNVERSIONED_MESSAGE_10_02
    .incbin "unversioned-message-10-03.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_10_04
    .incbin "unversioned-message-10-05.bin"
    PpuStreamAbsolute $2123 ; CONTROL_UNVERSIONED_MESSAGE_10_06
    .incbin "unversioned-message-10-07.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_10_08
    .incbin "unversioned-message-10-09.bin"
    PpuStreamAbsolute $2163 ; CONTROL_UNVERSIONED_MESSAGE_10_10
    .incbin "unversioned-message-10-11.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_10_12
    .incbin "unversioned-message-10-13.bin"
    PpuStreamAbsolute $21A3 ; CONTROL_UNVERSIONED_MESSAGE_10_14
    .incbin "unversioned-message-10-15.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_10_16
    .incbin "unversioned-message-10-17.bin"
    PpuStreamAbsolute $21E3 ; CONTROL_UNVERSIONED_MESSAGE_10_18
    .incbin "unversioned-message-10-19.bin"
    PpuStreamAbsolute $2223 ; CONTROL_UNVERSIONED_MESSAGE_10_20
    .incbin "unversioned-message-10-21.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_10_22
    .incbin "unversioned-message-10-23.bin"
    PpuStreamAbsolute $2263 ; CONTROL_UNVERSIONED_MESSAGE_10_24
    .incbin "unversioned-message-10-25.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_10_26
    .incbin "unversioned-message-10-27.bin"
    PpuStreamAbsolute $22C3 ; CONTROL_UNVERSIONED_MESSAGE_10_28
    .incbin "unversioned-message-10-29.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_10_30
.assert * = $BCAF, error, "unversioned message10 extent"
UnversionedMessage11:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_11_00
    .incbin "unversioned-message-11-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_11_02
    .incbin "unversioned-message-11-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_11_04
    .incbin "unversioned-message-11-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_11_06
    .incbin "unversioned-message-11-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_11_08
.assert * = $BD10, error, "unversioned message11 extent"
UnversionedMessage12:
    PpuStreamAbsolute $21A3 ; CONTROL_UNVERSIONED_MESSAGE_12_00
    .incbin "unversioned-message-12-01.bin"
    PpuStreamAbsolute $21E3 ; CONTROL_UNVERSIONED_MESSAGE_12_02
    .incbin "unversioned-message-12-03.bin"
    PpuStreamAbsolute $2223 ; CONTROL_UNVERSIONED_MESSAGE_12_04
    .incbin "unversioned-message-12-05.bin"
    PpuStreamAbsolute $2263 ; CONTROL_UNVERSIONED_MESSAGE_12_06
    .incbin "unversioned-message-12-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_12_08
.assert * = $BD66, error, "unversioned message12 extent"
UnversionedMessage13:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_13_00
    .incbin "unversioned-message-13-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_13_02
    .incbin "unversioned-message-13-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_13_04
    .incbin "unversioned-message-13-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_13_06
    .incbin "unversioned-message-13-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_13_08
    .incbin "unversioned-message-13-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_13_10
    .incbin "unversioned-message-13-11.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_13_12
    .incbin "unversioned-message-13-13.bin"
    PpuStreamAbsolute $22C3 ; CONTROL_UNVERSIONED_MESSAGE_13_14
    .incbin "unversioned-message-13-15.bin"
    PpuStreamAbsolute $2303 ; CONTROL_UNVERSIONED_MESSAGE_13_16
    .incbin "unversioned-message-13-17.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_13_18
.assert * = $BE21, error, "unversioned message13 extent"
UnversionedMessage14:
    PpuStreamAbsolute $2163 ; CONTROL_UNVERSIONED_MESSAGE_14_00
    .incbin "unversioned-message-14-01.bin"
    PpuStreamAbsolute $21A3 ; CONTROL_UNVERSIONED_MESSAGE_14_02
    .incbin "unversioned-message-14-03.bin"
    PpuStreamAbsolute $21E3 ; CONTROL_UNVERSIONED_MESSAGE_14_04
    .incbin "unversioned-message-14-05.bin"
    PpuStreamAbsolute $2223 ; CONTROL_UNVERSIONED_MESSAGE_14_06
    .incbin "unversioned-message-14-07.bin"
    PpuStreamAbsolute $2263 ; CONTROL_UNVERSIONED_MESSAGE_14_08
    .incbin "unversioned-message-14-09.bin"
    PpuStreamAbsolute $22A3 ; CONTROL_UNVERSIONED_MESSAGE_14_10
    .incbin "unversioned-message-14-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_14_12
.assert * = $BEB4, error, "unversioned message14 extent"
UnversionedMessage15:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_15_00
    .incbin "unversioned-message-15-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_15_02
    .incbin "unversioned-message-15-03.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_15_04
    .incbin "unversioned-message-15-05.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_15_06
.assert * = $BEF7, error, "unversioned message15 extent"
UnversionedMessage16:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_16_00
    .incbin "unversioned-message-16-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_16_02
    .incbin "unversioned-message-16-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_16_04
    .incbin "unversioned-message-16-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_16_06
    .incbin "unversioned-message-16-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_16_08
    .incbin "unversioned-message-16-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_16_10
    .incbin "unversioned-message-16-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_16_12
.assert * = $BF8D, error, "unversioned message16 extent"
UnversionedMessage17:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_17_00
    .incbin "unversioned-message-17-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_17_02
    .incbin "unversioned-message-17-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_17_04
    .incbin "unversioned-message-17-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_17_06
    .incbin "unversioned-message-17-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_17_08
    .incbin "unversioned-message-17-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_17_10
    .incbin "unversioned-message-17-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_17_12
.assert * = $C00D, error, "unversioned message17 extent"
UnversionedMessage18:
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_18_00
    .incbin "unversioned-message-18-01.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_18_02
    .incbin "unversioned-message-18-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_18_04
.assert * = $C042, error, "unversioned message18 extent"
UnversionedMessage19:
    PpuStreamAbsolute $2184 ; CONTROL_UNVERSIONED_MESSAGE_19_00
    .incbin "unversioned-message-19-01.bin"
    PpuStreamAbsolute $21C4 ; CONTROL_UNVERSIONED_MESSAGE_19_02
    .incbin "unversioned-message-19-03.bin"
    PpuStreamAbsolute $2204 ; CONTROL_UNVERSIONED_MESSAGE_19_04
    .incbin "unversioned-message-19-05.bin"
    PpuStreamAbsolute $2244 ; CONTROL_UNVERSIONED_MESSAGE_19_06
    .incbin "unversioned-message-19-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_19_08
.assert * = $C097, error, "unversioned message19 extent"
UnversionedMessage20:
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_20_00
    .incbin "unversioned-message-20-01.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_20_02
    .incbin "unversioned-message-20-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_20_04
.assert * = $C0C5, error, "unversioned message20 extent"
UnversionedMessage21:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_21_00
    .incbin "unversioned-message-21-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_21_02
    .incbin "unversioned-message-21-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_21_04
    .incbin "unversioned-message-21-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_21_06
    .incbin "unversioned-message-21-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_21_08
    .incbin "unversioned-message-21-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_21_10
    .incbin "unversioned-message-21-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_21_12
.assert * = $C13E, error, "unversioned message21 extent"
UnversionedMessage22:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_22_00
    .incbin "unversioned-message-22-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_22_02
    .incbin "unversioned-message-22-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_22_04
    .incbin "unversioned-message-22-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_22_06
    .incbin "unversioned-message-22-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_22_08
.assert * = $C19B, error, "unversioned message22 extent"
UnversionedMessage23:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_23_00
    .incbin "unversioned-message-23-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_23_02
    .incbin "unversioned-message-23-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_23_04
    .incbin "unversioned-message-23-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_23_06
    .incbin "unversioned-message-23-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_23_08
    .incbin "unversioned-message-23-09.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_23_10
    .incbin "unversioned-message-23-11.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_23_12
    .incbin "unversioned-message-23-13.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_23_14
.assert * = $C23F, error, "unversioned message23 extent"
UnversionedMessage24:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_24_00
    .incbin "unversioned-message-24-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_24_02
    .incbin "unversioned-message-24-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_24_04
    .incbin "unversioned-message-24-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_24_06
    .incbin "unversioned-message-24-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_24_08
    .incbin "unversioned-message-24-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_24_10
.assert * = $C2BA, error, "unversioned message24 extent"
UnversionedMessage25:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_25_00
    .incbin "unversioned-message-25-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_25_02
    .incbin "unversioned-message-25-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_25_04
    .incbin "unversioned-message-25-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_25_06
    .incbin "unversioned-message-25-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_25_08
    .incbin "unversioned-message-25-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_25_10
.assert * = $C323, error, "unversioned message25 extent"
UnversionedMessage26:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_26_00
    .incbin "unversioned-message-26-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_26_02
    .incbin "unversioned-message-26-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_26_04
    .incbin "unversioned-message-26-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_26_06
    .incbin "unversioned-message-26-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_26_08
    .incbin "unversioned-message-26-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_26_10
.assert * = $C38C, error, "unversioned message26 extent"
UnversionedMessage27:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_27_00
    .incbin "unversioned-message-27-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_27_02
    .incbin "unversioned-message-27-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_27_04
    .incbin "unversioned-message-27-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_27_06
    .incbin "unversioned-message-27-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_27_08
    .incbin "unversioned-message-27-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_27_10
.assert * = $C3F3, error, "unversioned message27 extent"
UnversionedMessage28:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_28_00
    .incbin "unversioned-message-28-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_28_02
    .incbin "unversioned-message-28-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_28_04
    .incbin "unversioned-message-28-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_28_06
    .incbin "unversioned-message-28-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_28_08
    .incbin "unversioned-message-28-09.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_28_10
    .incbin "unversioned-message-28-11.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_28_12
    .incbin "unversioned-message-28-13.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_28_14
.assert * = $C49E, error, "unversioned message28 extent"
UnversionedMessage29:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_29_00
    .incbin "unversioned-message-29-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_29_02
    .incbin "unversioned-message-29-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_29_04
    .incbin "unversioned-message-29-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_29_06
    .incbin "unversioned-message-29-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_29_08
    .incbin "unversioned-message-29-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_29_10
.assert * = $C515, error, "unversioned message29 extent"
UnversionedMessage30:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_30_00
    .incbin "unversioned-message-30-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_30_02
    .incbin "unversioned-message-30-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_30_04
    .incbin "unversioned-message-30-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_30_06
    .incbin "unversioned-message-30-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_30_08
    .incbin "unversioned-message-30-09.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_30_10
    .incbin "unversioned-message-30-11.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_30_12
    .incbin "unversioned-message-30-13.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_30_14
    .incbin "unversioned-message-30-15.bin"
    PpuStreamAbsolute $22C3 ; CONTROL_UNVERSIONED_MESSAGE_30_16
    .incbin "unversioned-message-30-17.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_30_18
.assert * = $C606, error, "unversioned message30 extent"
UnversionedMessage31:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_31_00
    .incbin "unversioned-message-31-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_31_02
    .incbin "unversioned-message-31-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_31_04
    .incbin "unversioned-message-31-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_31_06
    .incbin "unversioned-message-31-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_31_08
    .incbin "unversioned-message-31-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_31_10
    .incbin "unversioned-message-31-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_31_12
.assert * = $C693, error, "unversioned message31 extent"
UnversionedMessage32:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_32_00
    .incbin "unversioned-message-32-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_32_02
    .incbin "unversioned-message-32-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_32_04
    .incbin "unversioned-message-32-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_32_06
    .incbin "unversioned-message-32-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_32_08
    .incbin "unversioned-message-32-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_32_10
    .incbin "unversioned-message-32-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_32_12
.assert * = $C718, error, "unversioned message32 extent"
UnversionedMessage33:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_33_00
    .incbin "unversioned-message-33-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_33_02
    .incbin "unversioned-message-33-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_33_04
    .incbin "unversioned-message-33-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_33_06
    .incbin "unversioned-message-33-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_33_08
    .incbin "unversioned-message-33-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_33_10
.assert * = $C78E, error, "unversioned message33 extent"
UnversionedMessage34:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_34_00
    .incbin "unversioned-message-34-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_34_02
    .incbin "unversioned-message-34-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_34_04
    .incbin "unversioned-message-34-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_34_06
    .incbin "unversioned-message-34-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_34_08
    .incbin "unversioned-message-34-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_34_10
.assert * = $C80B, error, "unversioned message34 extent"
UnversionedMessage35:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_35_00
    .incbin "unversioned-message-35-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_35_02
    .incbin "unversioned-message-35-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_35_04
    .incbin "unversioned-message-35-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_35_06
    .incbin "unversioned-message-35-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_35_08
    .incbin "unversioned-message-35-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_35_10
.assert * = $C881, error, "unversioned message35 extent"
UnversionedMessage36:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_36_00
    .incbin "unversioned-message-36-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_36_02
    .incbin "unversioned-message-36-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_36_04
    .incbin "unversioned-message-36-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_36_06
    .incbin "unversioned-message-36-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_36_08
.assert * = $C8CD, error, "unversioned message36 extent"
UnversionedMessage37:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_37_00
    .incbin "unversioned-message-37-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_37_02
    .incbin "unversioned-message-37-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_37_04
    .incbin "unversioned-message-37-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_37_06
    .incbin "unversioned-message-37-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_37_08
.assert * = $C92B, error, "unversioned message37 extent"
UnversionedMessage38:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_38_00
    .incbin "unversioned-message-38-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_38_02
    .incbin "unversioned-message-38-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_38_04
    .incbin "unversioned-message-38-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_38_06
    .incbin "unversioned-message-38-07.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_38_08
    .incbin "unversioned-message-38-09.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_38_10
.assert * = $C998, error, "unversioned message38 extent"
UnversionedMessage39:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_39_00
    .incbin "unversioned-message-39-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_39_02
    .incbin "unversioned-message-39-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_39_04
    .incbin "unversioned-message-39-05.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_39_06
    .incbin "unversioned-message-39-07.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_39_08
.assert * = $C9F0, error, "unversioned message39 extent"
UnversionedMessage40:
    PpuStreamAbsolute $21C4 ; CONTROL_UNVERSIONED_MESSAGE_40_00
    .incbin "unversioned-message-40-01.bin"
    PpuStreamAbsolute $2204 ; CONTROL_UNVERSIONED_MESSAGE_40_02
    .incbin "unversioned-message-40-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_40_04
.assert * = $CA27, error, "unversioned message40 extent"
UnversionedMessage41:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_41_00
    .incbin "unversioned-message-41-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_41_02
    .incbin "unversioned-message-41-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_41_04
    .incbin "unversioned-message-41-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_41_06
    .incbin "unversioned-message-41-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_41_08
    .incbin "unversioned-message-41-09.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_41_10
    .incbin "unversioned-message-41-11.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_41_12
    .incbin "unversioned-message-41-13.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_41_14
    .incbin "unversioned-message-41-15.bin"
    PpuStreamAbsolute $2303 ; CONTROL_UNVERSIONED_MESSAGE_41_16
    .incbin "unversioned-message-41-17.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_41_18
.assert * = $CAF7, error, "unversioned message41 extent"
UnversionedMessage42:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_42_00
    .incbin "unversioned-message-42-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_42_02
    .incbin "unversioned-message-42-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_42_04
    .incbin "unversioned-message-42-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_42_06
    .incbin "unversioned-message-42-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_42_08
    .incbin "unversioned-message-42-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_42_10
    .incbin "unversioned-message-42-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_42_12
.assert * = $CB7E, error, "unversioned message42 extent"
UnversionedMessage43:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_43_00
    .incbin "unversioned-message-43-01.bin"
    PpuStreamAbsolute $20E3 ; CONTROL_UNVERSIONED_MESSAGE_43_02
    .incbin "unversioned-message-43-03.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_43_04
    .incbin "unversioned-message-43-05.bin"
    PpuStreamAbsolute $2123 ; CONTROL_UNVERSIONED_MESSAGE_43_06
    .incbin "unversioned-message-43-07.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_43_08
    .incbin "unversioned-message-43-09.bin"
    PpuStreamAbsolute $2163 ; CONTROL_UNVERSIONED_MESSAGE_43_10
    .incbin "unversioned-message-43-11.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_43_12
    .incbin "unversioned-message-43-13.bin"
    PpuStreamAbsolute $21A3 ; CONTROL_UNVERSIONED_MESSAGE_43_14
    .incbin "unversioned-message-43-15.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_43_16
    .incbin "unversioned-message-43-17.bin"
    PpuStreamAbsolute $21E3 ; CONTROL_UNVERSIONED_MESSAGE_43_18
    .incbin "unversioned-message-43-19.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_43_20
    .incbin "unversioned-message-43-21.bin"
    PpuStreamAbsolute $2223 ; CONTROL_UNVERSIONED_MESSAGE_43_22
    .incbin "unversioned-message-43-23.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_43_24
    .incbin "unversioned-message-43-25.bin"
    PpuStreamAbsolute $2263 ; CONTROL_UNVERSIONED_MESSAGE_43_26
    .incbin "unversioned-message-43-27.bin"
    PpuStreamAbsolute $2283 ; CONTROL_UNVERSIONED_MESSAGE_43_28
    .incbin "unversioned-message-43-29.bin"
    PpuStreamAbsolute $22A3 ; CONTROL_UNVERSIONED_MESSAGE_43_30
    .incbin "unversioned-message-43-31.bin"
    PpuStreamAbsolute $22C3 ; CONTROL_UNVERSIONED_MESSAGE_43_32
    .incbin "unversioned-message-43-33.bin"
    PpuStreamAbsolute $22E3 ; CONTROL_UNVERSIONED_MESSAGE_43_34
    .incbin "unversioned-message-43-35.bin"
    PpuStreamAbsolute $2303 ; CONTROL_UNVERSIONED_MESSAGE_43_36
    .incbin "unversioned-message-43-37.bin"
    PpuStreamAbsolute $2323 ; CONTROL_UNVERSIONED_MESSAGE_43_38
    .incbin "unversioned-message-43-39.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_43_40
.assert * = $CD79, error, "unversioned message43 extent"
UnversionedMessage44:
    PpuStreamAbsolute $20C3 ; CONTROL_UNVERSIONED_MESSAGE_44_00
    .incbin "unversioned-message-44-01.bin"
    PpuStreamAbsolute $2103 ; CONTROL_UNVERSIONED_MESSAGE_44_02
    .incbin "unversioned-message-44-03.bin"
    PpuStreamAbsolute $2143 ; CONTROL_UNVERSIONED_MESSAGE_44_04
    .incbin "unversioned-message-44-05.bin"
    PpuStreamAbsolute $2183 ; CONTROL_UNVERSIONED_MESSAGE_44_06
    .incbin "unversioned-message-44-07.bin"
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_44_08
    .incbin "unversioned-message-44-09.bin"
    PpuStreamAbsolute $2243 ; CONTROL_UNVERSIONED_MESSAGE_44_10
    .incbin "unversioned-message-44-11.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_44_12
.assert * = $CE1D, error, "unversioned message44 extent"
UnversionedMessage45:
    PpuStreamAbsolute $21C4 ; CONTROL_UNVERSIONED_MESSAGE_45_00
    .incbin "unversioned-message-45-01.bin"
    PpuStreamAbsolute $220A ; CONTROL_UNVERSIONED_MESSAGE_45_02
    .incbin "unversioned-message-45-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_45_04
.assert * = $CE48, error, "unversioned message45 extent"
UnversionedMessage46:
    PpuStreamAbsolute $21A8 ; CONTROL_UNVERSIONED_MESSAGE_46_00
    .incbin "unversioned-message-46-01.bin"
    PpuStreamAbsolute $21EC ; CONTROL_UNVERSIONED_MESSAGE_46_02
    .incbin "unversioned-message-46-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_46_04
.assert * = $CE67, error, "unversioned message46 extent"
UnversionedMessage47:
    PpuStreamAbsolute $21C3 ; CONTROL_UNVERSIONED_MESSAGE_47_00
    .incbin "unversioned-message-47-01.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_47_02
    .incbin "unversioned-message-47-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_47_04
.assert * = $CEA1, error, "unversioned message47 extent"
UnversionedMessage48:
    PpuStreamAbsolute $21C5 ; CONTROL_UNVERSIONED_MESSAGE_48_00
    .incbin "unversioned-message-48-01.bin"
    PpuStreamAbsolute $220A ; CONTROL_UNVERSIONED_MESSAGE_48_02
    .incbin "unversioned-message-48-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_48_04
.assert * = $CEC8, error, "unversioned message48 extent"
UnversionedMessage49:
    PpuStreamAbsolute $21CB ; CONTROL_UNVERSIONED_MESSAGE_49_00
    .incbin "unversioned-message-49-01.bin"
    PpuStreamAbsolute $2203 ; CONTROL_UNVERSIONED_MESSAGE_49_02
    .incbin "unversioned-message-49-03.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_49_04
.assert * = $CEF2, error, "unversioned message49 extent"
UnversionedMessage50:
    PpuStreamAbsolute $21E7 ; CONTROL_UNVERSIONED_MESSAGE_50_00
    .incbin "unversioned-message-50-01.bin"
    .byte PpuStreamTerminator ; CONTROL_UNVERSIONED_MESSAGE_50_02
.assert * = $CF07, error, "unversioned message50 extent"
; The shared ScriptCFC7 successor follows at this target's $CF07.
