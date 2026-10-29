; Own bank1 state-machine records, scripts, inventory PPU streams and menu.
; The $7C37 resource word is retained literally. Native sprite consumers use
; it as a CPU address below the ROM window; no $FC37 bank alias or verified
; visible sprite is inferred. Original purpose remains open.
UnversionedLiteralResource7C37 = $7C37
.macro UnversionedUpdateSlotFields00 first, second
    .byte $59
    .byte first
    .byte second
.endmacro
.macro UnversionedSetSlot05C0 value
    .byte $88
    .byte value
.endmacro
.macro UnversionedFillRowsAndSetMainState state
    .byte $7C
    .byte state
.endmacro
.macro UnversionedBank1MainScripts
UnversionedScriptCF07:
    BogusAddSlotValue $FF08 ; CONTROL_UNVERSIONED_MAIN_CF07
    BogusBranchIfSlotValueNotEqual UnversionedScriptCF17, $0004
    BogusQueueStateAB $4FC2
    BogusSetSlotD0Bits $01
    BogusJumpBank1 UnversionedScriptCF1A
UnversionedScriptCF17:
    BogusQueueStateAB $4FA6
UnversionedScriptCF1A:
    BogusMultiplySlotValueByArray $FF
    BogusClampSlotValueAtMost $0008
    BogusLoadSlotValueIndexedBank1 UnversionedPpuPointerCF9C
    BogusQueueStateAB $0000
    BogusQueueStateAB $4FD8
    BogusSetSlotValue $FFFF
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $0000
UnversionedScriptCF30:
    BogusSetDispatchCounter $8F
    BogusStoreSlotValueArray $FF
    BogusBranchIfSlotValueAtLeastArray $32, UnversionedScriptCF92
    BogusAddSlotValue $0033
    BogusSwapSlotValueBytes
    BogusLoadPage0140BySlotHigh
    BogusMaskSlotValue $00FF
    BogusBranchIfSlotD0BitsClear UnversionedScriptCF79, $01
    BogusBranchIfSlotValueEqual UnversionedScriptCF4D, $07, $00
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3D
    BogusSwapSlotValueBytes
UnversionedScriptCF4D:
    BogusXorSlotValue $8000
    BogusRemapSlotValue
    BogusRemapCase $8000, $5008
    BogusRemapCase $8001, $5011
    BogusRemapCase $8002, $501A
    BogusRemapCase $8003, $5023
    BogusRemapCase $8004, $502C
    BogusRemapCase $8005, $5035
    BogusRemapCase $8006, $503E
    BogusRemapCase $8007, $5047
    BogusRemapEnd
    BogusQueueStateAB $0000
    BogusJumpBank1 UnversionedScriptCF88
UnversionedScriptCF79:
    BogusBranchIfSlotValueEqual UnversionedScriptCF82, $06, $00
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3D
    BogusSwapSlotValueBytes
UnversionedScriptCF82:
    BogusLoadSlotValueIndexedBank1 UnversionedPpuPointerCFDC
    BogusQueueStateAB $0000
UnversionedScriptCF88:
    BogusSetDispatchCounter $8F
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $0001
    BogusJumpBank1 UnversionedScriptCF30
UnversionedScriptCF92:
    BogusBranchIfSelectedFlags UnversionedScriptCF99, $B0
    BogusJumpBank1 UnversionedScriptCF92
UnversionedScriptCF99:
    BogusClearSelected3E
    BogusClearSelected40
    BogusInitializeSplitAndMainState
UnversionedPpuPointerCF9C:
    .word (UnversionedPpuD050 - BankStart) ; CONTROL_UNVERSIONED_MAIN_CF9C
    .word (UnversionedPpuD082 - BankStart)
    .word (UnversionedPpuD0C4 - BankStart)
    .word (UnversionedPpuD10E - BankStart)
    .word (UnversionedPpuD15A - BankStart)
UnversionedPpuCFA6:
    PpuStreamAbsolute $208A
    .incbin "unversioned-ppu-inventory-cfa9.bin"
    PpuStreamRelative $0046
    .incbin "unversioned-ppu-inventory-cfb5.bin"
    .byte PpuStreamTerminator
UnversionedPpuCFC2:
    PpuStreamAbsolute $208C
    .incbin "unversioned-ppu-inventory-cfc5.bin"
    PpuStreamRelative $0045
    .incbin "unversioned-ppu-inventory-cfcc.bin"
    .byte PpuStreamTerminator
UnversionedPpuCFD8:
    PpuStreamAbsolute $2132
    .byte PpuStreamTerminator
UnversionedPpuPointerCFDC:
    .word (UnversionedPpuCFE4 - BankStart)
    .word (UnversionedPpuCFED - BankStart)
    .word (UnversionedPpuCFF6 - BankStart)
    .word (UnversionedPpuCFFF - BankStart)
UnversionedPpuCFE4:
    .incbin "unversioned-ppu-inventory-cfe4.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-cfe8.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuCFED:
    .incbin "unversioned-ppu-inventory-cfed.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-cff1.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuCFF6:
    .incbin "unversioned-ppu-inventory-cff6.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-cffa.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuCFFF:
    .incbin "unversioned-ppu-inventory-cfff.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d003.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD008:
    .incbin "unversioned-ppu-inventory-d008.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d00c.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD011:
    .incbin "unversioned-ppu-inventory-d011.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d015.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD01A:
    .incbin "unversioned-ppu-inventory-d01a.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d01e.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD023:
    .incbin "unversioned-ppu-inventory-d023.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d027.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD02C:
    .incbin "unversioned-ppu-inventory-d02c.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d030.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD035:
    .incbin "unversioned-ppu-inventory-d035.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d039.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD03E:
    .incbin "unversioned-ppu-inventory-d03e.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d042.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD047:
    .incbin "unversioned-ppu-inventory-d047.bin"
    PpuStreamRelative $0007
    .incbin "unversioned-ppu-inventory-d04b.bin"
    PpuStreamRelative $0039
    .byte PpuStreamTerminator
UnversionedPpuD050:
    PpuStreamAbsolute $2123
    .incbin "unversioned-ppu-inventory-d053.bin"
    PpuStreamAbsolute $2163
    .incbin "unversioned-ppu-inventory-d05a.bin"
    PpuStreamAbsolute $21A3
    .incbin "unversioned-ppu-inventory-d063.bin"
    PpuStreamAbsolute $21E3
    .incbin "unversioned-ppu-inventory-d06d.bin"
    PpuStreamAbsolute $2223
    .incbin "unversioned-ppu-inventory-d076.bin"
    PpuStreamAbsolute $2263
    .incbin "unversioned-ppu-inventory-d07d.bin"
    .byte PpuStreamTerminator
UnversionedPpuD082:
    PpuStreamAbsolute $2124
    .incbin "unversioned-ppu-inventory-d085.bin"
    PpuStreamAbsolute $2164
    .incbin "unversioned-ppu-inventory-d08e.bin"
    PpuStreamAbsolute $21A4
    .incbin "unversioned-ppu-inventory-d099.bin"
    PpuStreamAbsolute $21E4
    .incbin "unversioned-ppu-inventory-d0a1.bin"
    PpuStreamAbsolute $2224
    .incbin "unversioned-ppu-inventory-d0ac.bin"
    PpuStreamAbsolute $2264
    .incbin "unversioned-ppu-inventory-d0b5.bin"
    PpuStreamAbsolute $22A4
    .incbin "unversioned-ppu-inventory-d0bf.bin"
    .byte PpuStreamTerminator
UnversionedPpuD0C4:
    PpuStreamAbsolute $2124
    .incbin "unversioned-ppu-inventory-d0c7.bin"
    PpuStreamAbsolute $2164
    .incbin "unversioned-ppu-inventory-d0d0.bin"
    PpuStreamAbsolute $21A4
    .incbin "unversioned-ppu-inventory-d0d9.bin"
    PpuStreamAbsolute $21E4
    .incbin "unversioned-ppu-inventory-d0e3.bin"
    PpuStreamAbsolute $2224
    .incbin "unversioned-ppu-inventory-d0ef.bin"
    PpuStreamAbsolute $2264
    .incbin "unversioned-ppu-inventory-d0fd.bin"
    PpuStreamAbsolute $22A4
    .incbin "unversioned-ppu-inventory-d106.bin"
    .byte PpuStreamTerminator
UnversionedPpuD10E:
    PpuStreamAbsolute $2124
    .incbin "unversioned-ppu-inventory-d111.bin"
    PpuStreamAbsolute $2164
    .incbin "unversioned-ppu-inventory-d118.bin"
    PpuStreamAbsolute $21A4
    .incbin "unversioned-ppu-inventory-d122.bin"
    PpuStreamAbsolute $21E4
    .incbin "unversioned-ppu-inventory-d12b.bin"
    PpuStreamAbsolute $2224
    .incbin "unversioned-ppu-inventory-d133.bin"
    PpuStreamAbsolute $2264
    .incbin "unversioned-ppu-inventory-d13d.bin"
    PpuStreamAbsolute $22A4
    .incbin "unversioned-ppu-inventory-d145.bin"
    PpuStreamAbsolute $22E4
    .incbin "unversioned-ppu-inventory-d14d.bin"
    PpuStreamAbsolute $2324
    .incbin "unversioned-ppu-inventory-d155.bin"
    .byte PpuStreamTerminator
UnversionedPpuD15A:
    PpuStreamAbsolute $2124
    .incbin "unversioned-ppu-inventory-d15d.bin"
    PpuStreamAbsolute $2164
    .incbin "unversioned-ppu-inventory-d167.bin"
    PpuStreamAbsolute $21A4
    .incbin "unversioned-ppu-inventory-d172.bin"
    PpuStreamAbsolute $21E4
    .incbin "unversioned-ppu-inventory-d17a.bin"
    PpuStreamAbsolute $2224
    .incbin "unversioned-ppu-inventory-d183.bin"
    PpuStreamAbsolute $2264
    .incbin "unversioned-ppu-inventory-d189.bin"
    PpuStreamAbsolute $22A4
    .incbin "unversioned-ppu-inventory-d191.bin"
    PpuStreamAbsolute $22E4
    .incbin "unversioned-ppu-inventory-d199.bin"
    .byte PpuStreamTerminator
UnversionedRecordD19E:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame090, (UnversionedScriptD1B0 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD1A7:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD1B9 - BankStart), $40, $FF, $00, $00, $00
UnversionedScriptD1B0:
    BogusClearMatchingSlotFlag20 $01, $01, $00
    BogusClearSlot0790Bits $01
UnversionedScriptD1B6:
    BogusJumpBank1 UnversionedScriptD1B6
UnversionedScriptD1B9:
    BogusWait $0A
    BogusLoadSlotValueArray $3D
    BogusBranchIfSlotValueEqual UnversionedScriptD1C4, $00, $00
    BogusWait $28
UnversionedScriptD1C4:
    BogusSelectStateTableValue $0F
    BogusAddSlotValue $00F7
    BogusStoreSlotValueArray $3D
    BogusSetMainState $11
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $00
    BogusSaveStateAndPlaceSlots $13
    BogusSetDispatchCounter $8F
    BogusSelectStateTableValue $AA
    BogusConfigureBanksFromOperand $00
    BogusSelectStateTableValue $4E
    BogusSetSpritePalettePointer $0000
    BogusSelectStateTableValue $4D
    BogusSetBackgroundPalettePointer $0000
    BogusSetSlotValue $2E00
    BogusStoreSlotValueArray $3D
UnversionedScriptD1E9:
    BogusStoreSlotValueArray $FF
    BogusLoadPage0140BySlotHigh
    BogusMaskSlotValue $00FF
    BogusRemapSlotValue
    BogusRemapCase $000E, $3302
    BogusRemapCase $0015, $3304
    BogusRemapCase $0011, $3402
    BogusRemapCase $0012, $3404
    BogusRemapCase $001C, $3502
    BogusRemapCase $001D, $3504
    BogusRemapCase $001A, $3602
    BogusRemapCase $001B, $3604
    BogusRemapCase $002A, $3702
    BogusRemapCase $002B, $3704
    BogusRemapCase $0018, $3802
    BogusRemapCase $0019, $3804
    BogusRemapCase $002E, $3302
    BogusRemapCase $002F, $3304
    BogusRemapCase $0030, $3402
    BogusRemapCase $0031, $3404
    BogusRemapCase $0032, $3502
    BogusRemapCase $0033, $3504
    BogusRemapCase $0034, $3602
    BogusRemapCase $0035, $3604
    BogusRemapCase $0036, $3702
    BogusRemapCase $0037, $3704
    BogusRemapCase $0023, $3802
    BogusRemapCase $0024, $3804
    BogusRemapCase $0038, $3902
    BogusRemapCase $0039, $3904
    BogusRemapCase $0027, $3302
    BogusRemapCase $0028, $3304
    BogusRemapCase $003C, $3402
    BogusRemapCase $003D, $3404
    BogusRemapCase $003E, $3502
    BogusRemapCase $003F, $3504
    BogusRemapCase $0042, $3602
    BogusRemapCase $0043, $3604
    BogusRemapCase $0044, $3702
    BogusRemapCase $0045, $3704
    BogusRemapCase $0048, $3802
    BogusRemapCase $0049, $3804
    BogusRemapCase $004A, $3902
    BogusRemapCase $004B, $3904
    BogusRemapCase $004C, $3302
    BogusRemapCase $004D, $3304
    BogusRemapCase $004E, $3402
    BogusRemapCase $004F, $3404
    BogusRemapCase $0050, $3502
    BogusRemapCase $0051, $3504
    BogusRemapCase $0052, $3602
    BogusRemapCase $0053, $3604
    BogusRemapCase $0054, $3702
    BogusRemapCase $0055, $3704
    BogusRemapCase $0025, $3802
    BogusRemapCase $0026, $3804
    BogusRemapCase $0056, $3902
    BogusRemapCase $0057, $3904
    BogusRemapCase $0058, $3A02
    BogusRemapCase $0059, $3A04
    BogusRemapCase $0016, $3B02
    BogusRemapCase $0017, $3B04
    BogusRemapCase $005A, $3301
    BogusRemapCase $005B, $3401
    BogusRemapCase $0010, $3501
    BogusRemapCase $005E, $3601
    BogusRemapCase $005C, $3701
    BogusRemapCase $005F, $3801
    BogusRemapCase $0068, $3901
    BogusRemapCase $0069, $3A01
    BogusRemapEnd
    BogusBranchIfSlotValueEqual UnversionedScriptD34B, $FF, $FF
    BogusSetDispatchCounter $0C
    BogusStoreSlotValueArray $3D
    BogusLoadPage0140BySlotHigh
    BogusAddSlotValueFromArray $3D
    BogusSwapSlotValueBytes
    BogusStoreSlotValueArray $3D
    BogusSwapSlotValueBytes
    BogusMaskSlotValue $00FF
    BogusClampSlotValueAtMost $0007
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $3D
    BogusSwapSlotValueBytes
    BogusStoreSlotLowAtIndexedPage
    BogusSetDispatchCounter $08
    BogusLoadSlotValueArray $FF
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptD32C, $2B00
    BogusLookupCaseBank1 UnversionedScriptD334, $2C00
    BogusLookupCaseBank1 UnversionedScriptD33C, $2D00
    BogusLookupCaseBank1 UnversionedScriptD344, $2E00
    BogusLookupEnd
UnversionedScriptD32C:
    BogusClearRelatedSlotBit20 $01
    BogusMarkRelatedSlotAtDepth $28, $01
    BogusJumpBank1 UnversionedScriptD349
UnversionedScriptD334:
    BogusClearRelatedSlotBit20 $02
    BogusMarkRelatedSlotAtDepth $28, $02
    BogusJumpBank1 UnversionedScriptD349
UnversionedScriptD33C:
    BogusClearRelatedSlotBit20 $03
    BogusMarkRelatedSlotAtDepth $28, $03
    BogusJumpBank1 UnversionedScriptD349
UnversionedScriptD344:
    BogusClearRelatedSlotBit20 $04
    BogusMarkRelatedSlotAtDepth $28, $04
UnversionedScriptD349:
    BogusWait $14
UnversionedScriptD34B:
    BogusLoadSlotValueArray $FF
    BogusAddSlotValue $FF00
    BogusBranchIfSlotValueAtLeast UnversionedScriptD1E9, $2B00
    BogusSetDispatchCounter $83
    BogusMarkMatchingSlots $00, $01, $13, $00
    BogusSetCurrentSlotBit20
    BogusJumpBank1 ($8000 + $3069)
UnversionedRecordD360:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame269, (UnversionedScriptD369 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptD369:
    BogusSetSlot0640Pair $00, $40
    BogusSetSlotBit40 $01
UnversionedScriptD36E:
    BogusBranchIfSlot0760Equal UnversionedScriptD375, $01
    BogusJumpBank1 UnversionedScriptD36E
UnversionedScriptD375:
    BogusBranchIfSelectedFieldEqual UnversionedScriptD37C, $10
    BogusJumpBank1 UnversionedScriptD36E
UnversionedScriptD37C:
    BogusRestartVoice4 $266A
    BogusReadSlotValue $00
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusSetDispatchCounter $04
    BogusReadSelectedSlot0520 $00
    BogusAddSlotValue $0004
    BogusClampSlotValueAtMost $00FF
    BogusWriteSelectedSlot0520 $00
    BogusYieldAndSlotAction $01
UnversionedRecordD393:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame215, (UnversionedScriptD3A5 - BankStart), $00, $FE, $20, $61, $10 ; CONTROL_UNVERSIONED_MAIN_D393
UnversionedRecordD39C:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame215, (UnversionedScriptD3C1 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptD3A5:
    BogusSetDispatchCounter $86
    BogusSetSlot05F0Pair $78, $78
    BogusSetDirectionalSlotFields40 $40, $E0
    BogusSetSlotC0 $04
    BogusSetSlot0640Pair $40, $00
    BogusSetSlot0670Pair $04, $00
    BogusInitializeSlotMotionFields
    BogusClearSlot0790Bits $01
UnversionedScriptD3B8:
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptD3C1
    BogusBranchIfSlotB0AtMost UnversionedScriptD3B8, $E4
    BogusYieldAndSlotAction $00
UnversionedScriptD3C1:
    BogusSetDispatchCounter $84
    BogusLoadSlotRecord $09, $02
    BogusSetSlotFields80 $00, $E0
    BogusSetDirectionalSlotFields40 $C0, $FF
    BogusRestartVoice4 $2694
    BogusJumpBank1 UnversionedScriptD3B8
UnversionedCompactD3D2:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation027, $00
UnversionedRecordD3D5:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame104, (UnversionedScriptD42F - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordD3DE:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD58B - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD3E7:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD853 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD3F0:
    SlotRuntimeRecord $FFFF, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordD3F9:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD871 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD402:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation028, (UnversionedScriptD820 - BankStart), $40, $01, $C4, $65, $21
UnversionedRecordD40B:
    SlotRuntimeRecord $FFFF, $FFFF, $40, $FF, $00, $00, $00
UnversionedRecordD414:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation024, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordD41D:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation025, (UnversionedScriptD65E - BankStart), $23, $FE, $61, $61, $32
UnversionedRecordD426:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation026, $FFFF, $40, $FF, $00, $00, $00
UnversionedScriptD42F:
    BogusBranchIfMatchingSlotReady UnversionedScriptD42F, $01, $79, $00
    BogusSetSlotD0Bits $52
    BogusJumpBank1 UnversionedScriptD507
UnversionedRecordD43A:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame227, (UnversionedScriptD48B - BankStart), $40, $FE, $45, $62, $31
UnversionedRecordD443:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame230, (UnversionedScriptD518 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD44C:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD853 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD455:
    SlotRuntimeRecord $FFFF, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordD45E:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD871 - BankStart), $40, $FE, $45, $62, $31
UnversionedRecordD467:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation090, (UnversionedScriptD80D - BankStart), $40, $FE, $45, $62, $31
UnversionedRecordD470:
    SlotRuntimeRecord $FFFF, $FFFF, $40, $FF, $00, $00, $00
UnversionedRecordD479:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame227, $FFFF, $40, $FE, $45, $62, $31
UnversionedRecordD482:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation090, (UnversionedScriptD65E - BankStart), $23, $FE, $45, $62, $31
UnversionedScriptD48B:
    BogusSetSlotD0Bits $52
    BogusJumpBank1 UnversionedScriptD507
    UnversionedUpdateSlotFields00 $B6, $40
UnversionedRecordD493:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame239, (UnversionedScriptD4ED - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD49C:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD518 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD4A5:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD853 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD4AE:
    SlotRuntimeRecord $FFFF, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordD4B7:
    SlotRuntimeRecord $FFFF, (UnversionedScriptD871 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD4C0:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation095, (UnversionedScriptD810 - BankStart), $40, $FE, $25, $61, $11
UnversionedRecordD4C9:
    SlotRuntimeRecord $FFFF, $FFFF, $40, $FF, $00, $00, $00
UnversionedRecordD4D2:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame239, $FFFF, $40, $FF, $00, $00, $00
UnversionedRecordD4DB:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation099, (UnversionedScriptD65E - BankStart), $23, $FE, $25, $61, $11
UnversionedRecordD4E4:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation097, (UnversionedScriptD718 - BankStart), $40, $00, $60, $08, $12
UnversionedScriptD4ED:
    BogusSetSlotD0Bits $02
    BogusReadSlotValue $02
    BogusBranchIfSlotValueNotEqual UnversionedScriptD500, $0002
    BogusSetSlotValue $1000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $08
    BogusJumpBank1 UnversionedScriptD507
UnversionedScriptD500:
    BogusSetSlotD0Bits $10
    BogusSetSlotD0Bits $40
    BogusJumpBank1 UnversionedScriptD507
UnversionedScriptD507:
    BogusSetDispatchCounter $05
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $08, $00
    BogusSetSlot05F0Pair $3C, $FF
    BogusCheckSlotFlagsAndRestorePointer
    BogusSetSlotFields80 $01, $00
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD518:
    BogusSetDispatchCounter $08
    BogusBranchIfSlot06D0Present UnversionedScriptD614
    BogusSubtractSlotPriorityFromField0520
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusReadSlotValue $24
    BogusBranchIfSlotValueEqual ($8000 + $2BD8), $07, $00
    BogusSetSlot07F0 $80
    BogusBranchIfSlot0520AtMost UnversionedScriptD577, $00
    BogusBranchIfSelectedFieldEqual UnversionedScriptD5ED, $10
    BogusReadSlotValue $24
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptD546, $0000
    BogusLookupCaseBank1 UnversionedScriptD554, $0006
    BogusLookupCaseBank1 UnversionedScriptD577, $001D
    BogusLookupEnd
UnversionedScriptD546:
    BogusSetDispatchCounter $04
    BogusSetLinkedSlotFieldsC0 $18, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptD554, $40
    BogusWait $01
    BogusJumpBank1 UnversionedScriptD56A
UnversionedScriptD554:
    BogusSetDispatchCounter $85
    BogusSetLinkedSlotFieldsC0 $60, $B8
    BogusAdvanceAndBranchState1B UnversionedScriptD560, $80
    BogusAddSlotFields00 $00, $E8
UnversionedScriptD560:
    BogusSetDispatchCounter $03
    BogusStartVoice4 $2694
    BogusWait $06
    BogusJumpBank1 UnversionedScriptD56A
UnversionedScriptD56A:
    BogusSetSlotD0Bits $20
    BogusBranchIfSlot0520AtMost UnversionedScriptD572, $04
UnversionedScriptD570:
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD572:
    BogusSetSlotD0Bits $40
    BogusJumpBank1 UnversionedScriptD570
UnversionedScriptD577:
    BogusStartVoice4 $2694
    BogusSetSlotFields80 $D0, $88
    BogusSetSlotMode $FF
    BogusSetSlot0360 $28
UnversionedScriptD581:
    BogusBranchIfSlot0360AtMost UnversionedScriptD589, $01
    BogusBranchIfSlotB0AtMost UnversionedScriptD581, $E6
UnversionedScriptD589:
    BogusYieldAndSlotAction $01
UnversionedScriptD58B:
    BogusSetDispatchCounter $84
    BogusSetSlot0670Pair $40, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptD5AC, $FF, $50
UnversionedScriptD595:
    BogusSetSlot0670Pair $01, $00
    BogusSetSlotFields80 $01, $FF
    BogusLoadSlotRecord $3F, $02
    BogusWait $14
    BogusLoadRecordAndClearSavedState $48
UnversionedRecordD5A2:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame072, $FFFF, $00, $FF, $00, $00, $00
UnversionedRetainedD5AB:
; Separate retained byte after the nine selected record fields. It is
; copied as the loader's unused tenth-byte lookahead; D5AC is a branch target.
    .byte $00
UnversionedScriptD5AC:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptD595, $FF, $2C
    BogusLoadSlotRecord $51, $02
    BogusSetLinkedSlotFieldsC0 $40, $C0
    BogusWait $14
    BogusSetDispatchCounter $05
    BogusLoadSlotRecordAtPointer (UnversionedRecordD5A2 - BankStart)
    BogusSetSlotFields80 $00, $A0
UnversionedScriptD5C1:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptD5C1
    BogusSetState03BC $01
    BogusWait $01
    BogusSetState03BC $05
    BogusWait $01
    BogusSetState03BC $01
    BogusWait $01
    BogusSetState03BC $05
    BogusWait $01
    BogusSetState03BC $03
    BogusSetVoicePointers $29FD, $2A15, $0000, $0000
    BogusLoadSlotRecord $03, $FF
    BogusWait $5A
    BogusSetSlotValue $0029
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusSetMainState $FF
UnversionedScriptD5ED:
    BogusBranchIfSlotD0Bits UnversionedScriptD570, $40
    BogusSetSlot0790Bits $FF
    BogusLoadRecordAndClearSavedState $1B
    BogusFollowLinkedSlotsAndYield $FF, $FF, $01, $01, $00
    BogusSetLinkedFieldsAndYield $FF, $FC
    BogusSetLinkedFieldsAndYield $FF, $F8
    BogusSetLinkedFieldsAndYield $FF, $F0
    BogusSetLinkedFieldsAndYield $FF, $E8
    BogusSetLinkedFieldsAndYield $01, $E2
UnversionedScriptD60A:
    BogusSetSlot07F0 $18
    BogusSetSlot0630Bit04UnlessFF $01
UnversionedScriptD60E:
    BogusCopyLinkedMotionFields
    BogusClearSlot0790Bits $01
    BogusJumpBank1 UnversionedScriptD60E
UnversionedScriptD614:
    BogusBranchIfSelectedFieldEqual UnversionedScriptD61F, $11
    BogusWait $0A
    BogusLoadRecordAndClearSavedState $1B
    BogusJumpBank1 UnversionedScriptD60A
UnversionedScriptD61F:
    BogusSetDispatchCounter $87
    BogusSetSlot05F0Pair $7F, $7F
    BogusCopyLinkedMotionFields
    BogusSetDirectionalSlotFields40 $28, $00
    BogusAddSlotFields00 $00, $A0
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusRelinkSlots
UnversionedScriptD630:
    BogusSetDispatchCounter $03
    BogusAddSlotFields00 $00, $F8
    BogusBranchIfSlotFieldsWithin UnversionedScriptD641, $FF, $08
    BogusBranchIfSlotB0AtMost UnversionedScriptD630, $E6
    BogusLoadRecordAndClearSavedState $1E
UnversionedRetainedD640:
; The preceding 00/1E load selects the A1E5 record and its A1F7 script.
; This retained 01 lies before the independently targeted D641 entry. Later
; releases retain the corresponding single-byte gap; no padding is inferred.
    .byte $01
UnversionedScriptD641:
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusSetSlot07F0 $44
UnversionedScriptD649:
    BogusBranchIfSlot0620Bit10 UnversionedScriptD652
    BogusBranchIfSlotB0AtMost UnversionedScriptD649, $E6
    BogusYieldAndSlotAction $01
UnversionedScriptD652:
    BogusStartVoice4 $2694
    BogusSubtractSlotPriorityFromField0520
    BogusBranchIfSlot0520AtMost UnversionedScriptD577, $00
    BogusWait $0A
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD65E:
    BogusSetDispatchCounter $06
    BogusSetSlot07F0 $44
    BogusClearSlot0790Bits $FF
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusBranchIfSlot0620Bit10 UnversionedScriptD677
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptD66E:
    BogusSetSlotFields80 $01, $FF
    BogusLoadRecordAndClearSavedState $3F
    BogusWait $14
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD677:
    BogusSetDispatchCounter $84
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptD6B9, $FF, $07
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptD690, $00, $00
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfSlot0620Bit10 UnversionedScriptD7A6
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptD690:
    BogusBranchIfSlotD0Bits UnversionedScriptD6B9, $10
    BogusWait $14
    BogusBranchIfSlotCoordinates01 UnversionedScriptD6B9, $FF, $07
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptD6B9, $01, $00
    BogusBranchIfSlotD0BitsClear UnversionedScriptD6B4, $01
    BogusBranchIfSlotCoordinates01 UnversionedScriptD6B4, $40, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptD6B4, $80
    BogusBranchIfSlotCoordinates01 UnversionedScriptD74A, $FF, $30
UnversionedScriptD6B4:
    BogusSetSlotValue $0001
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptD6B9:
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD766, $00
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD760, $08
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD760, $10
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptD70D, $28, $FF
    BogusBranchIfSlotD0BitsClear UnversionedScriptD739, $08
    BogusConfigureSlot0750 $01, $00
    BogusLoadSlotValueArray $FF
    BogusSetSlot0670Pair $00, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptD6F0, $40, $10
UnversionedScriptD6E7:
    BogusConfigureSlot0750 $01, $00
    BogusSetSlot0670Pair $01, $00
    BogusJumpBank1 UnversionedScriptD739
UnversionedScriptD6F0:
    BogusSetDispatchCounter $85
    BogusSetSlotFields80 $01, $00
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD6E7, $20
UnversionedScriptD6F9:
    BogusSetSlotFields80 $20, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptD70B, $10, $08
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptD853
    BogusBranchIfSlotCoordinates01 UnversionedScriptD6F9, $40, $10
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD70B:
    BogusLoadRecordAndClearSavedState $51
UnversionedScriptD70D:
    BogusBranchIfSlotCoordinates01 UnversionedScriptD715, $FF, $10
    BogusJumpBank1 UnversionedScriptD66E
UnversionedScriptD715:
    BogusJumpBank1 UnversionedScriptD7F1
UnversionedScriptD718:
    BogusWait $07
    BogusMarkRelatedSlotAtDepth $38, $02
    BogusFindLinkedSlot
    BogusBranchIfSlotValueEqual UnversionedScriptD737, $FF, $FF
    BogusLoadSlotRecord $03, $FF
    BogusSetDirectionalSlotFields40 $10, $D8
    BogusMarkRelatedSlotAtDepth $1A, $01
    BogusRestartVoice4 $26EA
    BogusSetSlotFields80 $00, $00
    BogusWait $05
    BogusMarkRelatedSlotAtDepth $1A, $01
UnversionedScriptD737:
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD739:
    BogusBranchIfSlotD0BitsClear UnversionedScriptD750, $01
    BogusBranchIfSlotCoordinates01 UnversionedScriptD750, $40, $FF
    BogusBranchIfSlotCoordinates01 UnversionedScriptD74A, $FF, $30
    BogusJumpBank1 UnversionedScriptD750
UnversionedScriptD74A:
    BogusAdvanceAndBranchState1B UnversionedScriptD750, $40
    BogusLoadRecordAndClearSavedState $36
UnversionedScriptD750:
    BogusBranchIfSlotD0Bits UnversionedScriptD75A, $60
    BogusSetSlotFields80 $18, $00
    BogusJumpBank1 UnversionedScriptD677
UnversionedScriptD75A:
    BogusSetSlotFields80 $20, $00
    BogusJumpBank1 UnversionedScriptD677
UnversionedScriptD760:
    BogusSetSlotFields80 $08, $00
    BogusJumpBank1 UnversionedScriptD677
UnversionedScriptD766:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadRecordAndClearSavedState $3F
    BogusWait $14
    BogusBranchIfSlotD0Bits UnversionedScriptD791, $10
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD781, $08
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD781, $00
    BogusJumpBank1 UnversionedScriptD78B
UnversionedScriptD781:
    BogusSetSlotValue $0002
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $20, $00
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptD78B:
    BogusLoadSlotRecord $48, $02
    BogusJumpBank1 UnversionedScriptD677
UnversionedScriptD791:
    BogusLoadSlotRecord $48, $02
    BogusSetDirectionalSlotFields40 $F0, $FF
    BogusWait $02
    BogusSetDirectionalSlotFields40 $F0, $FF
    BogusWait $02
    BogusSetDirectionalSlotFields40 $F0, $FF
    BogusWait $02
    BogusJumpBank1 UnversionedScriptD66E
UnversionedScriptD7A6:
    BogusSetDispatchCounter $04
    BogusBranchIfSlotD0BitsClear UnversionedScriptD7BA, $01
    BogusBranchIfSlotCoordinates01 UnversionedScriptD7BA, $40, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptD7BA, $80
    BogusBranchIfSlotCoordinates01 UnversionedScriptD74A, $FF, $30
UnversionedScriptD7BA:
    BogusBranchIfOffsetProbe UnversionedScriptD7E1, $04
    BogusBranchOnDirectionalOffset UnversionedScriptD7E9, $04
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD766, $08
    BogusSetSlotFields80 $18, $FF
    BogusConfigureSlot0750 $01, $00
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfDirectionalOffsetClear UnversionedScriptD766, $08
    BogusBranchIfSlotCoordinates01 UnversionedScriptD66E, $10, $FF
    BogusConfigureSlot0750 $01, $00
    BogusJumpBank1 UnversionedScriptD677
UnversionedScriptD7E1:
    BogusSetSlotFields80 $01, $00
    BogusSetSlotValue $0000
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptD7E9:
    BogusSetSlotValue $0003
    BogusSetSlotFields80 $01, $00
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptD7F1:
    BogusSetDispatchCounter $86
    BogusLoadRecordAndClearSavedState $3F
    BogusSetSlotFields80 $01, $00
    BogusSetSlot0370 $01
    BogusBranchIfSlotD0BitsClear UnversionedScriptD800, $60
    BogusSetSlot0370 $01
UnversionedScriptD800:
    BogusBranchIfSlot0370AtMost UnversionedScriptD80B, $01
    BogusBranchIfSlotCoordinates01 UnversionedScriptD800, $28, $0F
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD80B:
    BogusLoadRecordAndClearSavedState $2D
UnversionedScriptD80D:
    BogusSetSlotFields80 $3C, $D8
UnversionedScriptD810:
    BogusSetSlotFields80 $20, $00
    BogusSetSlotFields80 $08, $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptD81C
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD81C:
    BogusClearSlotD0Bits $20
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD820:
    BogusSetSlotFields80 $20, $00
    BogusSetSlotFields80 $20, $00
    BogusSetSlotFields80 $08, $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusRestartVoice4 $2694
    BogusSetState03BC $01
    BogusWait $01
    BogusSetState03BC $05
    BogusWait $01
    BogusSetState03BC $01
    BogusWait $01
    BogusSetState03BC $05
    BogusWait $01
    BogusSetState03BC $03
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptD844
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD844:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $3F, $02
    BogusWait $14
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD853:
    BogusSetDispatchCounter $03
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
UnversionedScriptD85B:
    BogusBranchIfSlot0620Bit10 UnversionedScriptD864
    BogusBranchIfSlotB0AtMost UnversionedScriptD85B, $E6
    BogusYieldAndSlotAction $01
UnversionedScriptD864:
    BogusSetSlot05F0Pair $3C, $60
    BogusBranchIfSlotCoordinates01 UnversionedScriptD86E, $28, $10
    BogusLoadRecordAndClearSavedState $48
UnversionedScriptD86E:
    BogusJumpBank1 UnversionedScriptD7F1
UnversionedScriptD871:
    BogusSetDispatchCounter $04
    BogusBranchIfSlotValueEqual UnversionedScriptD8C0, $01, $00
    BogusBranchIfSlotValueEqual UnversionedScriptD8B3, $02, $00
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusBranchIfSlotD0BitsClear UnversionedScriptD897, $04
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
UnversionedScriptD897:
    BogusSetSlotFields80 $FF, $B0
    BogusSetSlotFields80 $FF, $C8
    BogusBranchIfSlotValueEqual UnversionedScriptD8A4, $03, $00
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptD8A4:
    BogusAddSlotFields00 $08, $00
    BogusWait $02
    BogusAddSlotFields00 $10, $00
    BogusWait $02
    BogusAddSlotFields00 $10, $00
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptD8B3:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $A0
    BogusJumpBank1 UnversionedScriptD897
UnversionedScriptD8C0:
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusBranchIfSlot0620Bit10 UnversionedScriptD8CE
    BogusSetSlotFields80 $FF, $E0
    BogusWait $04
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptD8CE:
    BogusLoadSlotRecord $48, $01
    BogusSetSlotFields80 $18, $FF
UnversionedScriptD8D4:
    BogusConfigureSlot0750 $01, $00
    BogusSetDispatchCounter $04
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptD8F7, $01, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptD8F7, $FF, $07
    BogusBranchIfSlotCoordinates01 UnversionedScriptD66E, $02, $FF
    BogusBranchIfSlotFieldsWithin UnversionedScriptD8F7, $07, $FF
    BogusConfigureSlot0750 $01, $00
    BogusBranchIfSlot0620Bit10 UnversionedScriptD8D4
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptD8F7:
    BogusLoadRecordAndClearSavedState $48
UnversionedCompactD8F9:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation013, $22
UnversionedCompactD8FC:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation012, $00
UnversionedRecordD8FF:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation013, (UnversionedScriptE97F - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordD908:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD911:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame040, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordD91A:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation012, (UnversionedScriptEA43 - BankStart), $00, $FF, $00, $00, $00
UnversionedCompactD923:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation011, $22
UnversionedCompactD926:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation010, $00
UnversionedRecordD929:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation011, (UnversionedScriptE97D - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordD932:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD93B:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame032, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordD944:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation010, (UnversionedScriptEA43 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordD94D:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation011, (UnversionedScriptEA7B - BankStart), $22, $FE, $27, $62, $21
UnversionedCompactD956:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation064, $22
UnversionedCompactD959:
    SlotCompactRecord Bank0::UnversionedSpriteFrame167, $00
UnversionedRecordD95C:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation064, (UnversionedScriptE97D - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordD965:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD96E:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame167, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordD977:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation063, (UnversionedScriptEA43 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordD980:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation064, (UnversionedScriptEA7B - BankStart), $22, $FE, $27, $62, $21
UnversionedCompactD989:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactD98C:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordD98F:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptED98 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordD998:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD9A1:
    SlotRuntimeRecord UnversionedLiteralResource7C37, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactD9AA:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation016, $22
UnversionedCompactD9AD:
    SlotCompactRecord Bank0::UnversionedSpriteFrame044, $00
UnversionedRecordD9B0:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation016, (UnversionedScriptED96 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordD9B9:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD9C2:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation014, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordD9CB:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation015, (UnversionedScriptEEB5 - BankStart), $00, $FF, $00, $00, $00
UnversionedCompactD9D4:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactD9D7:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordD9DA:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptED98 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordD9E3:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordD9EC:
    SlotRuntimeRecord UnversionedLiteralResource7C37, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactD9F5:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation077, $22
UnversionedCompactD9F8:
    SlotCompactRecord Bank0::UnversionedSpriteFrame191, $00
UnversionedRecordD9FB:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation077, (UnversionedScriptE693 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDA04:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDA0D:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation076, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA16:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame193, (UnversionedScriptE74C - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA1F:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame188, (UnversionedScriptE75C - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA28:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation075, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactDA31:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation074, $22
UnversionedCompactDA34:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation073, $00
UnversionedRecordDA37:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation074, (UnversionedScriptE693 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDA40:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDA49:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation072, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA52:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame199, (UnversionedScriptE74C - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA5B:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame194, (UnversionedScriptE75C - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA64:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation073, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactDA6D:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation117, $22
UnversionedCompactDA70:
    SlotCompactRecord Bank0::UnversionedSpriteFrame295, $00
UnversionedRecordDA73:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation117, (UnversionedScriptE693 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDA7C:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDA85:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation118, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA8E:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation118, (UnversionedScriptE74C - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDA97:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame292, (UnversionedScriptE75C - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDAA0:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame295, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactDAA9:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation092, $23
UnversionedCompactDAAC:
    SlotCompactRecord Bank0::UnversionedSpriteFrame234, $00
UnversionedRecordDAAF:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation092, (UnversionedScriptEE33 - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordDAB8:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedCompactDAC1:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation071, $22
UnversionedCompactDAC4:
    SlotCompactRecord Bank0::UnversionedSpriteFrame186, $00
UnversionedRecordDAC7:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation071, (UnversionedScriptDAE2 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDAD0:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDAD9:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation070, (UnversionedScriptDB3B - BankStart), $00, $01, $25, $FF, $12
UnversionedScriptDAE2:
    BogusSetDispatchCounter $86
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot0670Pair $F8, $00
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $40
    BogusSetSlot05F0Pair $20, $FF
    BogusClearSlot0790Bits $01
    BogusSetUnlinkedFields $00, $00
    BogusBranchIfSlotD0Bits UnversionedScriptDB29, $20
    BogusSetSlot0660LowBits $01
    BogusSetSlot0360 $28
UnversionedScriptDB01:
    BogusAddSlotFields00 $08, $00
    BogusSetDispatchCounter $03
    BogusBranchIfSlotCoordinates01 UnversionedScriptDB4A, $0C, $08
    BogusBranchIfSlotCoordinates01 UnversionedScriptDB1F, $10, $08
    BogusBranchIfSlot0700AtMost UnversionedScriptDB01, $FC
    BogusBranchIfSlot0360Above UnversionedScriptDB01, $01
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDB01, $C8, $20
    BogusYieldAndSlotAction $00
UnversionedScriptDB1F:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptDB29:
    BogusClearSlotD0Bits $20
    BogusSetSlot05F0Pair $60, $FF
    BogusSetSlotFields40Signed $60, $FF
    BogusSetSlotFields80 $FF, $C0
    BogusStartVoice4 $26EA
    BogusWait $0A
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDB3B:
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueEqual UnversionedScriptDB44, $05, $00
    BogusClearSlotD0Bits $40
UnversionedScriptDB44:
    BogusWait $28
    BogusSetSlotD0Bits $40
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDB4A:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptDB64, $0080
UnversionedScriptDB59:
    BogusAdjustSlotBounds $FF, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDB59, $10, $FF
    BogusJumpBank1 UnversionedScriptDB1F
UnversionedScriptDB64:
    BogusAdjustSlotBounds $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDB64, $10, $FF
    BogusJumpBank1 UnversionedScriptDB1F
UnversionedCompactDB6F:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation022, $00
UnversionedCompactDB72:
    SlotCompactRecord Bank0::UnversionedSpriteFrame062, $00
UnversionedCompactDB75:
    SlotCompactRecord Bank0::UnversionedSpriteFrame062, $00
UnversionedCompactDB78:
    SlotCompactRecord Bank0::UnversionedSpriteFrame061, $00
UnversionedRecordDB7B:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation023, (UnversionedScriptDB96 - BankStart), $23, $00, $16, $61, $22
UnversionedRecordDB84:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDB8D:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation023, $FFFF, $23, $00, $16, $61, $22
UnversionedScriptDB96:
    BogusSetSlot05F0Pair $40, $60
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot0670Pair $01, $00
    BogusSetUnlinkedFields $00, $00
    BogusClearSlot0790Bits $01
UnversionedScriptDBA4:
    BogusBranchIfSlotD0BitsClear UnversionedScriptDBB1, $20
    BogusRestartVoice4 $26EA
    BogusLoadSlotRecord $06, $FF
    BogusSetLinkedSlotFieldsC0 $18, $A0
UnversionedScriptDBB1:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptDBB1
    BogusLoadSlotRecord $00, $02
    BogusBranchIfSlotFieldsWithin UnversionedScriptDC26, $07, $FF
UnversionedScriptDBBC:
    BogusSetSlot0620Bit20
    BogusBranchIfAbsSlot0700Below UnversionedScriptDC0F, $18
    BogusBranchIfDirectionalOffsetClear UnversionedScriptDC0F, $0C
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptDBD4, $0080
    BogusBranchIfSlotOffset UnversionedScriptDC0F, $02, $00
    BogusJumpBank1 UnversionedScriptDBD9
UnversionedScriptDBD4:
    BogusBranchIfSlotOffset UnversionedScriptDC0F, $FE, $00
UnversionedScriptDBD9:
    BogusSetSlot0620Bit20
    BogusBranchIfSlotCoordinates01 UnversionedScriptDC33, $28, $18
    BogusBranchIfSlotCoordinates01 UnversionedScriptDC52, $48, $18
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDC0B, $FF, $17
    BogusSetSlot0620Bit20
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual UnversionedScriptDBF8, $0001
    BogusBranchIfOffsetProbe UnversionedScriptDC9E, $05
    BogusJumpBank1 UnversionedScriptDC0B
UnversionedScriptDBF8:
    BogusBranchIfSlotValueNotEqual UnversionedScriptDC0B, $0000
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusWait $03
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDC0B:
    BogusSetSlot0620Bit20
    BogusJumpBank1 UnversionedScriptDBA4
UnversionedScriptDC0F:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusSetSlot0620Bit20
    BogusWait $04
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusSetSlot0620Bit20
    BogusWait $08
    BogusSetDirectionalSlotFields40 $F8, $FF
    BogusJumpBank1 UnversionedScriptDBB1
UnversionedScriptDC26:
    BogusSetSlot0620Bit20
    BogusSetDispatchCounter $83
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $10, $FF
    BogusSetSlot0660LowBits $00
    BogusJumpBank1 UnversionedScriptDBBC
UnversionedScriptDC33:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $28, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetUnlinkedFields $18, $00
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptDCB6
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDC52:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $0C, $FF
    BogusWait $14
    BogusLoadSlotRecord $12, $02
    BogusBranchIfSlotCoordinates01 UnversionedScriptDC33, $28, $18
    BogusBranchIfSlotCoordinates01 UnversionedScriptDC6F, $48, $18
    BogusJumpBank1 UnversionedScriptDC26
UnversionedScriptDC6F:
    BogusSetDirectionalSlotFields40 $40, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlotFields80 $FF, $D0
    BogusSetUnlinkedFields $18, $00
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptDCB6
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDC9E:
    BogusSetDispatchCounter $84
    BogusLoadSlotRecord $06, $FF
    BogusSetSlotFields80 $00, $A0
    BogusSetDirectionalSlotFields40 $02, $FF
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDCB6:
    BogusWait $0A
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactDCBA:
    SlotCompactRecord Bank0::UnversionedSpriteFrame144, $00
UnversionedCompactDCBD:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation048, $22
UnversionedCompactDCC0:
    SlotCompactRecord Bank0::UnversionedSpriteFrame141, $00
UnversionedRecordDCC3:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation048, (UnversionedScriptDD6E - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDCCC:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDCD5:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation048, (UnversionedScriptDE31 - BankStart), $23, $00, $16, $61, $22
UnversionedRecordDCDE:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation047, (UnversionedScriptDE28 - BankStart), $00, $00, $25, $FF, $12
UnversionedCompactDCE7:
    SlotCompactRecord Bank0::UnversionedSpriteFrame135, $00
UnversionedCompactDCEA:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation049, $22
UnversionedCompactDCED:
    SlotCompactRecord Bank0::UnversionedSpriteFrame134, $00
UnversionedRecordDCF0:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation049, (UnversionedScriptDD6E - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDCF9:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDD02:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation049, (UnversionedScriptDE31 - BankStart), $23, $00, $16, $61, $22
UnversionedRecordDD0B:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation050, (UnversionedScriptDE28 - BankStart), $00, $01, $65, $FF, $12
UnversionedCompactDD14:
    SlotCompactRecord Bank0::UnversionedSpriteFrame180, $00
UnversionedCompactDD17:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation069, $22
UnversionedCompactDD1A:
    SlotCompactRecord Bank0::UnversionedSpriteFrame177, $00
UnversionedRecordDD1D:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation069, (UnversionedScriptDD6E - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDD26:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDD2F:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation069, (UnversionedScriptDE31 - BankStart), $23, $00, $16, $61, $22
UnversionedRecordDD38:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation068, (UnversionedScriptDE28 - BankStart), $00, $01, $25, $FF, $12
UnversionedCompactDD41:
    SlotCompactRecord Bank0::UnversionedSpriteFrame129, $00
UnversionedCompactDD44:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation046, $22
UnversionedCompactDD47:
    SlotCompactRecord Bank0::UnversionedSpriteFrame130, $00
UnversionedRecordDD4A:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation046, (UnversionedScriptDD6E - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordDD53:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDD5C:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation046, (UnversionedScriptDE31 - BankStart), $23, $00, $16, $61, $22
UnversionedRecordDD65:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation045, (UnversionedScriptDE28 - BankStart), $00, $01, $25, $FF, $12
UnversionedScriptDD6E:
    BogusSetDispatchCounter $86
    BogusSetSlot0640Pair $04, $00
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlot05F0Pair $20, $60
    BogusClearSlot0790Bits $01
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0660LowBits $01
UnversionedScriptDD82:
    BogusSetSlot0670Pair $40, $00
    BogusReadSlotValue $07
    BogusBranchIfSlotValueEqual UnversionedScriptDDC3, $FF, $FF
    BogusBranchIfSlotCoordinates01 UnversionedScriptDE03, $14, $08
    BogusBranchIfSlotCoordinates01 UnversionedScriptDDB9, $1C, $08
    BogusSetDispatchCounter $84
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDDB1, $FF, $40
UnversionedScriptDD9D:
    BogusBranchIfAbsSlot0700Below UnversionedScriptDDA9, $40
    BogusSetDirectionalSlotFields40 $08, $FF
    BogusWait $04
    BogusJumpBank1 UnversionedScriptDD82
UnversionedScriptDDA9:
    BogusSetSlotFields40Signed $08, $00
    BogusWait $02
    BogusJumpBank1 UnversionedScriptDD82
UnversionedScriptDDB1:
    BogusSetSlotFields80 $20, $FF
    BogusWait $04
    BogusJumpBank1 UnversionedScriptDD82
UnversionedScriptDDB9:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadRecordAndClearSavedState $1B
UnversionedScriptDDC3:
    BogusSetDispatchCounter $05
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptDDD8, $40, $28
    BogusAdvanceAndBranchState1B UnversionedScriptDD9D, $80
    BogusAdvanceAndBranchState1B UnversionedScriptDDE4, $80
    BogusJumpBank1 UnversionedScriptDD9D
UnversionedScriptDDD8:
    BogusSetDispatchCounter $84
    BogusSetSlot0660LowBits $00
    BogusSetSlot05F0Pair $60, $60
    BogusSetDirectionalSlotFields40 $30, $FF
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptDDE4:
    BogusBranchIfSlot0700AtMost UnversionedScriptDD9D, $40
    BogusBranchIfSlot0700AtMost UnversionedScriptDDEF, $60
    BogusJumpBank1 UnversionedScriptDD9D
UnversionedScriptDDEF:
    BogusSetSlot0360 $50
UnversionedScriptDDF1:
    BogusSetSlotFields80 $00, $FF
    BogusSetSlot0670Pair $41, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDD82, $80, $28
    BogusBranchIfSlot0360Above UnversionedScriptDDF1, $01
    BogusJumpBank1 UnversionedScriptDD82
UnversionedScriptDE03:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptDE1D, $0080
UnversionedScriptDE12:
    BogusAdjustSlotBounds $FF, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDE12, $18, $FF
    BogusJumpBank1 UnversionedScriptDDB9
UnversionedScriptDE1D:
    BogusAdjustSlotBounds $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDE1D, $18, $FF
    BogusJumpBank1 UnversionedScriptDDB9
UnversionedScriptDE28:
    BogusSetSlot0670Pair $40, $00
    BogusSetSlot0620Bit20
    BogusWait $3C
    BogusSetSlot0620Bit20
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptDE31:
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $FF, $B0
    BogusSetSlotMode $03
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
UnversionedScriptDE4A:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptDE4A
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactDE4F:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation049, $23
UnversionedCompactDE52:
    SlotCompactRecord Bank0::UnversionedSpriteFrame136, $00
UnversionedRecordDE55:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation050, (UnversionedScriptDE70 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDE5E:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDE67:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame135, $FFFF, $00, $00, $25, $D9, $22
UnversionedScriptDE70:
    BogusSetDispatchCounter $86
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot05F0Pair $40, $60
    BogusSetSlotD0Bits $40
    BogusClearSlot0790Bits $01
    BogusSetSlot0670Pair $00, $08
    BogusBranchIfSlotD0Bits UnversionedScriptDF4A, $20
UnversionedScriptDE83:
    BogusReadSlotValue $07
    BogusBranchIfSlotValueNotEqual UnversionedScriptDE95, $FFFF
    BogusLoadSlotRecord $00, $01
    BogusSetUnlinkedFields $18, $00
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptDE83
UnversionedScriptDE95:
    BogusLoadSlotRecord $06, $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0660LowBits $01
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $10, $FF
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDF0B, $48, $28
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDEAF, $58, $FF
    BogusSetSlotFields80 $20, $FF
UnversionedScriptDEAF:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDEE3, $FF, $08
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptDECA, $01, $00
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusWait $01
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusJumpBank1 UnversionedScriptDEDD
UnversionedScriptDECA:
    BogusBranchIfOffsetProbe UnversionedScriptDED3, $05
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptDE83
UnversionedScriptDED3:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotMode $03
    BogusSetSlotFields80 $FF, $A0
UnversionedScriptDEDD:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptDEDD
    BogusJumpBank1 UnversionedScriptDE83
UnversionedScriptDEE3:
    BogusBranchIfDirectionalOffsetClear UnversionedScriptDEFE, $28
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptDEF6, $0080
    BogusBranchIfSlotOffset UnversionedScriptDEFE, $02, $00
    BogusJumpBank1 UnversionedScriptDEFB
UnversionedScriptDEF6:
    BogusBranchIfSlotOffset UnversionedScriptDEFE, $FE, $00
UnversionedScriptDEFB:
    BogusJumpBank1 UnversionedScriptDE83
UnversionedScriptDEFE:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $A0
    BogusSetDirectionalSlotFields40 $30, $FF
    BogusSetSlotMode $03
    BogusJumpBank1 UnversionedScriptDEDD
UnversionedScriptDF0B:
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptDF1A, $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDF1A, $FF, $08
    BogusJumpBank1 UnversionedScriptDEAF
UnversionedScriptDF1A:
    BogusLoadSlotRecord $12, $02
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $40, $D8
    BogusSetSlotMode $03
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptDF2C, $FF, $10
    BogusSetSlotFields80 $FF, $B0
UnversionedScriptDF2C:
    BogusSetSlot0620Bit20
    BogusAddSlotFields00 $00, $F0
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusSetSlot0620Bit20
    BogusWait $01
    BogusLoadSlotRecord $06, $FF
    BogusSetUnlinkedFields $18, $00
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptDE83
UnversionedScriptDF4A:
    BogusLoadSlotRecord $12, $01
    BogusSetLinkedSlotFieldsC0 $40, $B0
    BogusSetUnlinkedFields $18, $00
    BogusClearSlotD0Bits $20
UnversionedScriptDF55:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptDF55
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactDF5A:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation062, $00
UnversionedCompactDF5D:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation061, $00
UnversionedCompactDF60:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation062, $00
UnversionedCompactDF63:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation062, $00
UnversionedCompactDF66:
    SlotCompactRecord Bank0::UnversionedSpriteFrame164, $00
UnversionedRecordDF69:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation061, (UnversionedScriptDF8D - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDF72:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDF7B:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation062, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordDF84:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation062, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptDF8D:
    BogusSetSlotD0Bits $03
    BogusSetSlotValue $0007
    BogusJumpBank1 UnversionedScriptE081
UnversionedCompactDF95:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation114, $00
UnversionedCompactDF98:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation113, $00
UnversionedCompactDF9B:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation115, $00
UnversionedCompactDF9E:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation114, $00
UnversionedCompactDFA1:
    SlotCompactRecord Bank0::UnversionedSpriteFrame281, $00
UnversionedRecordDFA4:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation112, (UnversionedScriptDFC8 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDFAD:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDFB6:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation114, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordDFBF:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation114, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptDFC8:
    BogusSetSlotD0Bits $02
    BogusSetSlotValue $0007
    BogusJumpBank1 UnversionedScriptE081
UnversionedCompactDFD0:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation017, $00
UnversionedCompactDFD3:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation018, $00
UnversionedCompactDFD6:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation018, $00
UnversionedCompactDFD9:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation019, $00
UnversionedCompactDFDC:
    SlotCompactRecord Bank0::UnversionedSpriteFrame056, $00
UnversionedRecordDFDF:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame056, (UnversionedScriptE003 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordDFE8:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordDFF1:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation017, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordDFFA:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation017, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptE003:
    BogusSetSlotD0Bits $02
    BogusSetSlotValue $0007
    BogusJumpBank1 UnversionedScriptE081
UnversionedCompactE00B:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation004, $00
UnversionedCompactE00E:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation006, $00
UnversionedCompactE011:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation005, $00
UnversionedCompactE014:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation004, $00
UnversionedCompactE017:
    SlotCompactRecord Bank0::UnversionedSpriteFrame023, $00
UnversionedRecordE01A:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame023, (UnversionedScriptE03E - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE023:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE02C:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation004, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordE035:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation004, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptE03E:
    BogusSetSlotD0Bits $0B
    BogusSetSlotValue $0007
    BogusJumpBank1 UnversionedScriptE081
UnversionedCompactE046:
    SlotCompactRecord Bank0::UnversionedSpriteFrame030, $00
UnversionedCompactE049:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation008, $00
UnversionedCompactE04C:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation008, $00
UnversionedCompactE04F:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation007, $00
UnversionedCompactE052:
    SlotCompactRecord Bank0::UnversionedSpriteFrame029, $00
UnversionedRecordE055:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame029, (UnversionedScriptE079 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE05E:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE067:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation007, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordE070:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation007, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptE079:
    BogusSetSlotD0Bits $1E
    BogusSetSlotValue $0007
    BogusJumpBank1 UnversionedScriptE081
UnversionedScriptE081:
    BogusSetDispatchCounter $04
    BogusStoreSlotValueArray $FF
    BogusSetSlotC0 $FF
    BogusClearSlot0790Bits $01
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptE081
    BogusSetSlot0640Pair $04, $00
    BogusSetSlot05F0Pair $40, $60
    BogusSetSlot0660LowBits $00
    BogusSetSlot0660HighBits $00
UnversionedScriptE096:
    BogusBranchIfSlotD0BitsClear UnversionedScriptE0A2, $08
    BogusSetSlot0670Pair $28, $04
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE0DA, $28, $10
UnversionedScriptE0A2:
    BogusBranchIfSlotD0BitsClear UnversionedScriptE0AE, $03
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE106, $40, $40
UnversionedScriptE0AE:
    BogusSetDispatchCounter $84
    BogusBranchIfSlotD0BitsClear UnversionedScriptE0C1, $04
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FF, $FF
    BogusBranchIfDirectionalOffsetClear UnversionedScriptE0C1, $28
    BogusJumpBank1 UnversionedScriptE1E1
UnversionedScriptE0C1:
    BogusWait $03
    BogusAdvanceAndBranchState1B UnversionedScriptE096, $E8
    BogusAdvanceAndBranchState1B UnversionedScriptE096, $80
    BogusAdvanceAndBranchState1B UnversionedScriptE0D3, $80
    BogusBranchIfSlotD0Bits UnversionedScriptE1AC, $10
UnversionedScriptE0D3:
    BogusLoadSlotRecord $09, $FF
    BogusWait $14
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE0DA:
    BogusLoadSlotRecord $00, $02
    BogusSetSlot0670Pair $28, $04
    BogusSetSlot0660LowBits $01
    BogusSetSlotC0 $FF
    BogusSetUnlinkedFields $18, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE0F8, $10, $10
    BogusSetSlotFields80 $08, $C0
    BogusWait $07
UnversionedScriptE0F1:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE0DA, $28, $10
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE0F8:
    BogusSetSlotFields80 $01, $FF
    BogusLoadSlotRecord $0C, $FF
UnversionedScriptE0FE:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE0FE, $10, $10
    BogusJumpBank1 UnversionedScriptE0F1
UnversionedScriptE106:
    BogusBranchIfSlotD0BitsClear UnversionedScriptE1AC, $01
    BogusBranchIfSlotB0AtMost UnversionedScriptE11A, $30
    BogusBranchIfOffsetProbe UnversionedScriptE136, $05
    BogusBranchIfSlotB0AtMost UnversionedScriptE11A, $60
    BogusBranchIfOffsetProbe UnversionedScriptE168, $0B
UnversionedScriptE11A:
    BogusBranchIfSlotB0AtMost UnversionedScriptE121, $B8
    BogusJumpBank1 UnversionedScriptE130
UnversionedScriptE121:
    BogusBranchIfPositiveOffsetProbe UnversionedScriptE185, $06
    BogusBranchIfSlotB0AtMost UnversionedScriptE12C, $88
    BogusJumpBank1 UnversionedScriptE130
UnversionedScriptE12C:
    BogusBranchIfOffsetProbe UnversionedScriptE185, $0C
UnversionedScriptE130:
    BogusBranchIfSlotD0Bits UnversionedScriptE1AC, $02
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE136:
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptE11A, $01, $00
    BogusLoadSlotRecord $12, $02
    BogusRestartVoice4 $27C6
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $F8
    BogusSetSlotMode $03
UnversionedScriptE14E:
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE168:
    BogusLoadSlotRecord $12, $02
    BogusRestartVoice4 $27C6
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotC0 $00
    BogusSetSlotFields80 $00, $F8
    BogusSetSlotMode $03
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusAddSlotFields00 $00, $F8
    BogusJumpBank1 UnversionedScriptE14E
UnversionedScriptE185:
    BogusReadSlotValue $1A
    BogusBranchIfSlotValueEqual UnversionedScriptE193, $00, $00
    BogusReadSlotValue $08
    BogusBranchIfSlotValueEqual UnversionedScriptE130, $00, $00
UnversionedScriptE193:
    BogusLoadSlotRecord $12, $02
    BogusRestartVoice4 $27C6
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotC0 $02
    BogusWait $04
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptE1A8
    BogusBranchIfSlotD0BitsClear UnversionedScriptE168, $02
UnversionedScriptE1A8:
    BogusSetSlotMode $02
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE1AC:
    BogusLoadSlotRecord $0F, $FF
    BogusSetSlotC0 $04
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $02
    BogusSetSlot0660HighBits $00
    BogusSetSlotFields80 $40, $E0
    BogusWait $08
    BogusSetSlotC0 $00
    BogusLoadSlotRecord $1B, $02
    BogusRestartVoice4 $27C6
UnversionedScriptE1C9:
    BogusSetSlotFields40Signed $08, $08
    BogusSetDispatchCounter $83
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusBranchIfPositiveOffsetProbe UnversionedScriptE1DF, $06
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusJumpBank1 UnversionedScriptE1C9
UnversionedScriptE1DF:
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE1E1:
    BogusSetSlot05F0Pair $40, $78
    BogusSetSlotC0 $20
    BogusSetUnlinkedFields $18, $00
UnversionedScriptE1E9:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $88
    BogusSetDirectionalSlotFields40 $08, $FF
    BogusLoadSlotRecord $00, $02
UnversionedScriptE1F4:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptE1F4
    BogusSetDispatchCounter $06
    BogusSetSlot0670Pair $28, $04
    BogusBranchIfSlotCoordinates01 UnversionedScriptE0DA, $1E, $10
    BogusBranchIfAbsSlot0700Below UnversionedScriptE22E, $18
    BogusBranchIfDirectionalOffsetClear UnversionedScriptE22E, $0C
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptE218, $0080
    BogusBranchIfSlotOffset UnversionedScriptE22E, $02, $00
    BogusJumpBank1 UnversionedScriptE21D
UnversionedScriptE218:
    BogusBranchIfSlotOffset UnversionedScriptE22E, $FE, $00
UnversionedScriptE21D:
    BogusAdvanceAndBranchState1B UnversionedScriptE239, $20
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE1DF, $28, $28
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE1E9
UnversionedScriptE22E:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusJumpBank1 UnversionedScriptE1E9
UnversionedScriptE239:
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0360 $14
    BogusSetSlot0670Pair $01, $00
UnversionedScriptE249:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE255, $28, $28
    BogusBranchIfSlot0360Above UnversionedScriptE249, $01
    BogusJumpBank1 UnversionedScriptE1E9
UnversionedScriptE255:
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactE257:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactE25A:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordE25D:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptE278 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE266:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE26F:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptE2D4 - BankStart), $40, $01, $14, $11, $11
UnversionedScriptE278:
    BogusSetSlot0640Pair $04, $00
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $40, $60
    BogusClearSlot0790Bits $01
UnversionedScriptE288:
    BogusSetSlotFields80 $00, $FF
    BogusSetSlot0670Pair $00, $01
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE2E7, $40, $22
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE29E, $80, $10
    BogusJumpBank1 UnversionedScriptE288
UnversionedScriptE29E:
    BogusLoadSlotRecord $06, $FF
    BogusSetSlot0660LowBits $01
UnversionedScriptE2A3:
    BogusAddSlotFields00 $08, $00
UnversionedScriptE2A6:
    BogusSetSlot0670Pair $00, $01
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE2E7, $40, $22
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptE2C4, $10, $10
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptE2A6
    BogusBranchIfDirectionalOffsetClear UnversionedScriptE2C9, $10
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE2A3, $80, $10
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE2C4:
    BogusSetSlotFields80 $00, $00
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptE2C9:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $C0
    BogusSetDirectionalSlotFields40 $40, $FF
    BogusJumpBank1 UnversionedScriptE2A6
UnversionedScriptE2D4:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $01, $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadSlotRecord $06, $FF
    BogusSetSlotFields80 $C0, $00
    BogusWait $06
    BogusSetSlotFields80 $01, $00
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE2E7:
    BogusLoadSlotRecord $06, $FF
UnversionedScriptE2EA:
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $10, $FF
    BogusWait $04
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE2EA, $40, $22
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactE2F8:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation082, $23
UnversionedCompactE2FB:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation080, $00
UnversionedRecordE2FE:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation082, (UnversionedScriptE488 - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordE307:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE310:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame207, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE319:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation081, (UnversionedScriptE529 - BankStart), $13, $FF, $00, $00, $00
UnversionedRecordE322:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame210, (UnversionedScriptE594 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE32B:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation083, (UnversionedScriptE5AC - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE334:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation082, (UnversionedScriptE607 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE33D:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation079, (UnversionedScriptE642 - BankStart), $00, $FF, $00, $00, $00
UnversionedCompactE346:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation104, $23
UnversionedCompactE349:
    SlotCompactRecord Bank0::UnversionedSpriteFrame262, $00
UnversionedRecordE34C:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation104, (UnversionedScriptE486 - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordE355:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE35E:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame258, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE367:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation103, (UnversionedScriptE529 - BankStart), $13, $FF, $00, $00, $00
UnversionedRecordE370:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame259, (UnversionedScriptE594 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE379:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation105, (UnversionedScriptE5AC - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE382:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation104, (UnversionedScriptE607 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE38B:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation101, (UnversionedScriptE642 - BankStart), $00, $FF, $00, $00, $00
UnversionedCompactE394:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation060, $23
UnversionedCompactE397:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation057, $00
UnversionedRecordE39A:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation060, (UnversionedScriptE490 - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordE3A3:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE3AC:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame157, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE3B5:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation056, (UnversionedScriptE529 - BankStart), $13, $FF, $00, $00, $00
UnversionedRecordE3BE:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame158, (UnversionedScriptE594 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE3C7:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation058, (UnversionedScriptE5AC - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE3D0:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation060, (UnversionedScriptE607 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE3D9:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation059, (UnversionedScriptE642 - BankStart), $00, $FF, $00, $00, $00
UnversionedCompactE3E2:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation055, $23
UnversionedCompactE3E5:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation052, $00
UnversionedRecordE3E8:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation055, (UnversionedScriptE490 - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordE3F1:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE3FA:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame148, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE403:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation051, (UnversionedScriptE529 - BankStart), $13, $FF, $00, $00, $00
UnversionedRecordE40C:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame149, (UnversionedScriptE594 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE415:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation053, (UnversionedScriptE5AC - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE41E:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation055, (UnversionedScriptE607 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE427:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation054, (UnversionedScriptE642 - BankStart), $00, $FF, $00, $00, $00
UnversionedCompactE430:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation040, $23
UnversionedCompactE433:
    SlotCompactRecord Bank0::UnversionedSpriteFrame120, $00
UnversionedRecordE436:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation040, (UnversionedScriptE47E - BankStart), $23, $FF, $00, $00, $00
UnversionedRecordE43F:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE448:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame120, (UnversionedScriptE8B5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE451:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation041, (UnversionedScriptE529 - BankStart), $13, $FF, $00, $00, $00
UnversionedRecordE45A:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame121, (UnversionedScriptE594 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE463:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation040, (UnversionedScriptE5AC - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordE46C:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation040, (UnversionedScriptE607 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordE475:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation042, (UnversionedScriptE642 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptE47E:
    BogusSetSlotD0Bits $01
    BogusSetSlotValue $0000
    BogusJumpBank1 UnversionedScriptE493
UnversionedScriptE486:
    BogusSetSlotD0Bits $04
UnversionedScriptE488:
    BogusSetSlotValue $0000
    BogusSetSlotD0Bits $02
    BogusJumpBank1 UnversionedScriptE493
UnversionedScriptE490:
    BogusSetSlotValue $0002
UnversionedScriptE493:
    BogusSetDispatchCounter $0A
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00 ; CONTROL_UNVERSIONED_MAIN_E497
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual UnversionedScriptE4A9, $0005
    BogusSetSlotD0Bits $40
UnversionedScriptE4A9:
    BogusBranchIfSlotD0Bits UnversionedScriptE564, $20
UnversionedScriptE4AD:
    BogusClearSlot0790Bits $05
    BogusBranchIfSlot0620Bit10 UnversionedScriptE4B4
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptE4B4:
    BogusBranchIfSlotD0Bits UnversionedScriptE51E, $01
    BogusSetSlot0670Pair $10, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE507, $80, $30
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE505, $40, $10
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual UnversionedScriptE4D7, $0000
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE4D7, $FF, $30
    BogusJumpBank1 UnversionedScriptE592
UnversionedScriptE4D7:
    BogusSetDispatchCounter $84
    BogusBranchIfSlotFieldsWithin UnversionedScriptE4F5, $18, $FF
    BogusBranchIfAbsSlot0700Below UnversionedScriptE4FD, $18
    BogusAdvanceAndBranchState1B UnversionedScriptE4AD, $C8
    BogusSetDispatchCounter $85
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $20, $FF
    BogusSetSlot0660LowBits $00
    BogusJumpBank1 UnversionedScriptE640
UnversionedScriptE4F5:
    BogusSetSlotFields40Signed $18, $FF
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE4AD
UnversionedScriptE4FD:
    BogusSetDirectionalSlotFields40 $D0, $FF
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE4AD
UnversionedScriptE505:
    BogusLoadRecordAndClearSavedState $36
UnversionedScriptE507:
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $18, $FF
    BogusWait $04
UnversionedScriptE50E:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE516, $14, $10
    BogusJumpBank1 UnversionedScriptE4B4
UnversionedScriptE516:
    BogusSetSlotFields80 $01, $C0
    BogusWait $08
    BogusJumpBank1 UnversionedScriptE50E
UnversionedScriptE51E:
    BogusSetSlotFields40Signed $08, $00
    BogusSetSlotFields80 $FF, $E0
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptE51E
UnversionedScriptE529:
    BogusSetDispatchCounter $05
    BogusSetSlot0660LowBits $00
    BogusClearSlot0790Bits $01
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotFields80 $00, $D0
    BogusSetDispatchCounter $0C
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusBranchIfSlot0700AtMost UnversionedScriptE545, $E4
    BogusJumpBank1 UnversionedScriptE553
UnversionedScriptE545:
    BogusBranchIfSlotOffset UnversionedScriptE570, $0C, $00
    BogusBranchIfSlotOffset UnversionedScriptE570, $04, $00
    BogusBranchIfSlot0700AtMost UnversionedScriptE55D, $1A
UnversionedScriptE553:
    BogusBranchIfSlotOffset UnversionedScriptE578, $F4, $00
    BogusBranchIfSlotOffset UnversionedScriptE578, $FC, $00
UnversionedScriptE55D:
    BogusBranchIfSlotB0AtMost UnversionedScriptE564, $18
    BogusClearSlot0790Bits $05
    BogusMarkSlot05A0AndYield
UnversionedScriptE564:
    BogusSetDispatchCounter $83
    BogusClearSlotD0Bits $20
    BogusSetSlotFields40Signed $40, $00
    BogusRestartVoice4 $26EA
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptE570:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $20, $C0
    BogusJumpBank1 UnversionedScriptE57D
UnversionedScriptE578:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $E0, $C0
UnversionedScriptE57D:
    BogusSetDispatchCounter $03
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusWait $04
    BogusSetDispatchCounter $84
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusSetSlotFields80 $00, $FF
    BogusWait $04
UnversionedScriptE592:
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptE594:
    BogusSetDispatchCounter $04
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusBranchIfSlotB0AtMost UnversionedScriptE5AA, $40
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
UnversionedScriptE5AA:
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptE5AC:
    BogusSetDispatchCounter $89
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $01, $00
    BogusBranchIfSlotD0Bits UnversionedScriptE5F4, $02
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual UnversionedScriptE5EE, $0005
    BogusReadSlotValue $02
    BogusBranchIfSlotValueNotEqual UnversionedScriptE5E8, $002C
    BogusAdvanceAndBranchState1B UnversionedScriptE5E0, $80
    BogusAdvanceAndBranchState1B UnversionedScriptE5D8, $80
    BogusCreateLinkedSlot $10, $10, $10, $2C
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptE5D8:
    BogusCreateLinkedSlot $5E, $10, $10, $2C
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptE5E0:
    BogusCreateLinkedSlot $5A, $10, $10, $2C
    BogusCheckSlotFlagsAndRestorePointer
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptE5E8:
    BogusSetSlotValue $005B
    BogusJumpBank1 UnversionedScriptE5F7
UnversionedScriptE5EE:
    BogusSetSlotValue $0021
    BogusJumpBank1 UnversionedScriptE5F7
UnversionedScriptE5F4:
    BogusSetSlotValue $003A
UnversionedScriptE5F7:
    BogusSetSlot0790Bits $01
    BogusCreateLinkedSlot $00, $10, $10, $00
    BogusCheckSlotFlagsAndRestorePointer
    BogusBranchIfSlotD0Bits UnversionedScriptE605, $04
    BogusWait $0A
UnversionedScriptE605:
    BogusLoadRecordAndClearSavedState $3F
UnversionedScriptE607:
    BogusLoadSlotValueArray $FF
    BogusStartVoice4FromIndexedPair $2640
    BogusSetSlot0670Pair $01, $00
UnversionedScriptE60F:
    BogusBranchIfAbsSlot0700Below UnversionedScriptE61B, $30
    BogusSetSlot0660LowBits $02
    BogusSetSlotFields80 $40, $FF
    BogusJumpBank1 UnversionedScriptE624
UnversionedScriptE61B:
    BogusSetSlotFields40Signed $40, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptE624, $C8
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptE624:
    BogusBranchIfOffsetProbe UnversionedScriptE63D, $05
    BogusBranchIfDirectionalOffsetClear UnversionedScriptE640, $10
    BogusBranchIfSlotCoordinates01 UnversionedScriptE640, $20, $10
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE638, $40, $10
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE638:
    BogusBranchIfSlot0620Bit10 UnversionedScriptE60F
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptE63D:
    BogusSetSlotFields80 $00, $FF
UnversionedScriptE640:
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptE642:
    BogusClearSlot0790Bits $01
    BogusBranchIfSlot0620Bit10 UnversionedScriptE649
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptE649:
    BogusBranchIfSlotD0Bits UnversionedScriptE649, $01
    BogusAdvanceAndBranchState1B UnversionedScriptE66B, $80
    BogusLoadSlotValueArray $FF
    BogusStartVoice4FromIndexedPair $2640
    BogusSetSlot0670Pair $10, $00
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual UnversionedScriptE66B, $0000
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE66B, $01, $FF
    BogusSetSlotMode $FF
    BogusWait $01
    BogusLoadRecordAndClearSavedState $12
UnversionedScriptE66B:
    BogusWait $14
    BogusSetSlot0670Pair $01, $00
    BogusReadSlotValue $08
    BogusBranchIfSlotValueNotEqual UnversionedScriptE687, $0000
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE689, $30, $28
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE687, $FF, $10
    BogusAdvanceAndBranchState1B UnversionedScriptE649, $80
    BogusLoadRecordAndClearSavedState $2D
UnversionedScriptE687:
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE689:
    BogusBranchIfSlotB0AtMost UnversionedScriptE691, $40
    BogusBranchIfOffsetProbe UnversionedScriptE640, $05
UnversionedScriptE691:
    BogusLoadRecordAndClearSavedState $36
UnversionedScriptE693:
    BogusSetDispatchCounter $06
    BogusSetSlotValue $8001
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
UnversionedScriptE6A3:
    BogusClearSlot0790Bits $01
    BogusAdvanceAndBranchState1B UnversionedScriptE6C1, $D4
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $12, $01
    BogusLoadSlotValueArray $FF
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $2654
    BogusWait $0A
    BogusLoadSlotRecord $00, $01
UnversionedScriptE6C1:
    BogusSetSlot0670Pair $28, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE6CC, $E0, $28
    BogusJumpBank1 UnversionedScriptE6DB
UnversionedScriptE6CC:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE6D9, $20, $10
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $18, $FF
    BogusJumpBank1 UnversionedScriptE744
UnversionedScriptE6D9:
    BogusLoadRecordAndClearSavedState $1B
UnversionedScriptE6DB:
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE6E6, $60, $10
    BogusJumpBank1 UnversionedScriptE704
UnversionedScriptE6E6:
    BogusSetSlotFields40Signed $40, $00
    BogusSetSlot0360 $12
UnversionedScriptE6EB:
    BogusBranchIfSlotCoordinates01 UnversionedScriptE702, $38, $20
    BogusBranchIfSlot0360Above UnversionedScriptE6EB, $00
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetSlotFields40Signed $01, $00
    BogusLoadSlotRecord $00, $02
    BogusJumpBank1 UnversionedScriptE6A3
UnversionedScriptE702:
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptE704:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusBranchIfAbsSlot0700Below UnversionedScriptE713, $20
    BogusJumpBank1 UnversionedScriptE716
UnversionedScriptE713:
    BogusSetSlotFields40Signed $02, $FF
UnversionedScriptE716:
    BogusReadSlotValue $05
    BogusMaskSlotValue $0007
    BogusJumpViaSlotIndexedTable
UnversionedIndexedTargetE71C:
; Eight indexed targets on the path after the preceding 0007 mask.
    BogusIndexedTargetBank1 UnversionedScriptE72C ; CONTROL_UNVERSIONED_MAIN_E71C
    BogusIndexedTargetBank1 UnversionedScriptE736
    BogusIndexedTargetBank1 UnversionedScriptE72E
    BogusIndexedTargetBank1 UnversionedScriptE73C
    BogusIndexedTargetBank1 UnversionedScriptE73C
    BogusIndexedTargetBank1 UnversionedScriptE73C
    BogusIndexedTargetBank1 UnversionedScriptE73C
    BogusIndexedTargetBank1 UnversionedScriptE73C
UnversionedScriptE72C:
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptE72E:
    BogusLoadSlotRecord $2D, $01
UnversionedScriptE731:
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptE6A3
UnversionedScriptE736:
    BogusLoadSlotRecord $12, $01
    BogusJumpBank1 UnversionedScriptE731
UnversionedScriptE73C:
    BogusLoadSlotRecord $1B, $01
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE6A3
UnversionedScriptE744:
    BogusLoadSlotRecord $00, $02
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE6A3
UnversionedScriptE74C:
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $01, $FF
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE74C, $20, $10
    BogusLoadSlotRecord $00, $02
    BogusJumpBank1 UnversionedScriptE6A3
UnversionedScriptE75C:
    BogusSetDirectionalSlotFields40 $10, $A0
    BogusWait $09
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE763:
    BogusSetDispatchCounter $07
    BogusBranchIfSelectedFieldEqual UnversionedScriptE831, $12
    BogusBranchIfSlot06D0Present UnversionedScriptE7E0
    BogusBranchIfSelectedFieldEqual UnversionedScriptE77B, $10
    BogusBranchIfSelectedFieldEqual UnversionedScriptE8C8, $1D
    BogusRestoreSavedScriptAndSlotFlags
UnversionedScriptE775:
    BogusSetSlotD0Bits $20
    BogusSetSlot07F0 $44
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE77B:
    BogusBranchIfSlotD0Bits UnversionedScriptE775, $40
    BogusSetDispatchCounter $06
    BogusSetSlot0790Bits $FF
    BogusLoadSlotRecord $03, $FF
    BogusFollowLinkedSlotsAndYield $FF, $FF, $23, $00, $00
    BogusSetSlot05E0Bit40 $01
    BogusStartVoice4 $278D
    BogusSetLinkedFieldsAndYield $FF, $FE
    BogusSetLinkedFieldsAndYield $FF, $FC
    BogusSetLinkedFieldsAndYield $FF, $F8
    BogusSetLinkedFieldsAndYield $FF, $F4
    BogusSetLinkedFieldsAndYield $80, $F2
    BogusSetSlot0360 $FC
UnversionedScriptE7A2:
    BogusSetSlot07F0 $14
    BogusSetSlot0630Bit04UnlessFF $01
    BogusSetSlot0660LowBits $00
    BogusSetSlot0660HighBits $00
    BogusClearSlot0640PairBits $04, $00
UnversionedScriptE7AD:
    BogusCopyLinkedMotionFields
    BogusClearSlot0790Bits $01
    BogusReadSlotValue $02
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptE7D6, $0052
    BogusLookupCaseBank1 UnversionedScriptE7D6, $0053
    BogusLookupEnd
UnversionedScriptE7BD:
    BogusBranchIfSlotD0BitsClear UnversionedScriptE7AD, $80
    BogusReadSlotValue $12
    BogusBranchIfSlotValueAtLeast UnversionedScriptE7CB, $0080
    BogusJumpBank1 UnversionedScriptE7AD
UnversionedScriptE7CB:
    BogusSetSlot0640PairBits $04, $00
    BogusSetSlotMode $03
    BogusRelinkSlots
    BogusSetSlot05E0Bit40 $FF
    BogusJumpBank1 UnversionedScriptE80F
UnversionedScriptE7D6:
    BogusBranchIfSlot0360Above UnversionedScriptE7BD, $A0
    BogusRestartVoice4 $27B4
    BogusJumpBank1 UnversionedScriptE7F7
UnversionedScriptE7E0:
    BogusBranchIfSelectedFieldEqual UnversionedScriptE7F7, $11
    BogusBranchIfSelectedFieldEqual UnversionedScriptE826, $13
    BogusBranchIfSelectedFieldEqual UnversionedScriptE8AB, $14
    BogusBranchIfSelectedFieldEqual UnversionedScriptE7F3, $1E
    BogusJumpBank1 UnversionedScriptE7A2
UnversionedScriptE7F3:
    BogusRelinkToLastRelatedSlot
    BogusJumpBank1 UnversionedScriptE7A2
UnversionedScriptE7F7:
    BogusSetDispatchCounter $88
    BogusLoadSlotRecord $03, $FF
    BogusSetSlot05F0Pair $7F, $7F
    BogusCopyLinkedMotionFields
    BogusSetDirectionalSlotFields40 $38, $FF
UnversionedScriptE803:
    BogusSetSlotMode $03
    BogusSetSlot07F0 $44
    BogusSetSlot0640PairBits $04, $00
    BogusRelinkSlots
    BogusSetSlot05E0Bit40 $FF
    BogusSetSlotC0 $FF
UnversionedScriptE80F:
    BogusSetSlot07F0 $44
UnversionedScriptE811:
    BogusBranchIfSlot0620Bit10 UnversionedScriptE81A
    BogusBranchIfSlotB0AtMost UnversionedScriptE811, $E6
    BogusYieldAndSlotAction $00
UnversionedScriptE81A:
    BogusStartVoice4 $2694
    BogusClearSlot0790Bits $01
    BogusWait $0A
    BogusSetUnlinkedFields $00, $00
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE826:
    BogusSetDispatchCounter $88
    BogusLoadSlotRecord $03, $FF
    BogusSetSlotFields80 $00, $E0
    BogusJumpBank1 UnversionedScriptE803
UnversionedScriptE831:
    BogusSetDispatchCounter $0E
    BogusRelinkSlots
    BogusSetSlot05E0Bit40 $FF
    BogusSetDispatchCounter $8F
    BogusSetSlot07F0 $44
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusSetSlotC0 $FF
    BogusSetSlot0790Bits $FF
    BogusLoadSlotRecord $06, $FF
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueEqual UnversionedScriptE869, $14, $00
    BogusSetSlotPositionFromOperands $60, $A7
    BogusSetSlot0660LowBits $00
    BogusSetSlotFields80 $01, $00
    BogusWait $14
    BogusSetSlotFields80 $18, $00
    BogusWait $21
    BogusSetSpriteAttribute20 $20
    BogusWait $0C
    BogusYieldAndSlotAction $01
UnversionedScriptE869:
    BogusSetSlotC0 $04
    BogusSetSlotFields80 $60, $00
    BogusSetVoicePointers $26F3, $FFFF, $0000, $0000
    BogusSetVoicePointers $FFFF, $26FC, $0000, $0000
UnversionedScriptE880:
    BogusBranchIfSlot0700AtMost UnversionedScriptE880, $80
    BogusSetSlotFields80 $00, $00
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusRestartVoice4 $2707
    BogusWait $0A
    BogusMarkMatchingSlots $00, $01, $1E, $00
    BogusWait $0C
    BogusRestartVoice4 $26EA
    BogusSetSlotFields80 $78, $00
UnversionedScriptE8A2:
    BogusBranchIfAbsSlot0700Below UnversionedScriptE8A9, $20
    BogusJumpBank1 UnversionedScriptE8A2
UnversionedScriptE8A9:
    BogusYieldAndSlotAction $00
UnversionedScriptE8AB:
    BogusReadSlotValue $02
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2A
    BogusSwapSlotValueBytes
    BogusStoreSlotLowAtIndexedPage
    BogusJumpBank1 UnversionedScriptE7A2
UnversionedScriptE8B5:
    BogusSetDispatchCounter $04
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
UnversionedScriptE8BD:
    BogusBranchIfSlot0620Bit10 UnversionedScriptE8C6
    BogusBranchIfSlotB0AtMost UnversionedScriptE8BD, $E6
    BogusYieldAndSlotAction $00
UnversionedScriptE8C6:
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE8C8:
    BogusLoadSlotRecord $03, $FF
    BogusClearSlotD0Bits $40
    BogusSetLinkedSlotFieldsC0 $20, $A0
    BogusSetSlotMode $03
    BogusSetUnlinkedFields $18, $00
    BogusSetSlot07F0 $0A
    BogusClearSlot0790Bits $01
    BogusWait $14
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $06
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $06
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $28
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $06
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $06
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $28
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $06
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusWait $06
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
    BogusAdjustSlotBounds $FF, $00
    BogusWait $01
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusWait $01
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusLoadSlotValueArray $FF
    BogusBranchIfSlotValueAtLeast UnversionedScriptE93C, $8000
    BogusStartVoice4FromIndexedPair $2640
    BogusJumpBank1 UnversionedScriptE942
UnversionedScriptE93C:
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $2654
UnversionedScriptE942:
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusWait $01
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusWait $01
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusWait $01
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusWait $01
    BogusAdjustSlotBounds $02, $00
    BogusWait $01
    BogusAdjustSlotBounds $FE, $00
    BogusWait $01
    BogusAdjustSlotBounds $01, $00
    BogusWait $14
    BogusSetSlot07F0 $44
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptE97D:
    BogusSetSlotD0Bits $01
UnversionedScriptE97F:
    BogusSetSlotD0Bits $80
    BogusSetSlotValue $8000
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot05F0Pair $60, $60
UnversionedScriptE98F:
    BogusClearSlot0790Bits $01
    BogusAdvanceAndBranchState1B UnversionedScriptE9AF, $D4
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $1B, $01
    BogusWait $07
    BogusLoadSlotValueArray $FF
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $2654
    BogusWait $0A
    BogusLoadSlotRecord $00, $01
UnversionedScriptE9AF:
    BogusSetSlot0670Pair $08, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE9BA, $E0, $28
    BogusJumpBank1 UnversionedScriptE9C9
UnversionedScriptE9BA:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptE9C7, $1E, $10
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $18, $FF
    BogusJumpBank1 UnversionedScriptEA3B
UnversionedScriptE9C7:
    BogusLoadRecordAndClearSavedState $1B
UnversionedScriptE9C9:
    BogusSetDispatchCounter $05
    BogusBranchIfSlotD0BitsClear UnversionedScriptE9EA, $01
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinates01 UnversionedScriptE9DA, $60, $10
    BogusJumpBank1 UnversionedScriptE9EA
UnversionedScriptE9DA:
    BogusBranchIfSlotCoordinates01 UnversionedScriptE9E1, $20, $FF
    BogusLoadRecordAndClearSavedState $24
UnversionedScriptE9E1:
    BogusLoadSlotRecord $00, $02
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusJumpBank1 UnversionedScriptEA07
UnversionedScriptE9EA:
    BogusSetSlot0660LowBits $00
    BogusBranchIfSlotD0BitsClear UnversionedScriptEA14, $01
    BogusAdvanceAndBranchState1B UnversionedScriptEA14, $80
    BogusSetDispatchCounter $85
    BogusLoadSlotRecord $00, $02
    BogusBranchIfAbsSlot0700Below UnversionedScriptEA0C, $20
    BogusSetSlotFields80 $F0, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptEA07, $80
    BogusSetSlotFields80 $10, $FF
UnversionedScriptEA07:
    BogusWait $0C
    BogusJumpBank1 UnversionedScriptEA3E
UnversionedScriptEA0C:
    BogusSetSlotFields40Signed $18, $00
    BogusWait $14
    BogusJumpBank1 UnversionedScriptEA3E
UnversionedScriptEA14:
    BogusBranchIfSlotFieldsWithin UnversionedScriptEA25, $07, $FF
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusBranchIfAbsSlot0700Below UnversionedScriptEA35, $20
UnversionedScriptEA25:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $1B, $01
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE98F
UnversionedScriptEA35:
    BogusSetSlotFields40Signed $02, $FF
    BogusJumpBank1 UnversionedScriptEA25
UnversionedScriptEA3B:
    BogusLoadSlotRecord $00, $02
UnversionedScriptEA3E:
    BogusWait $04
    BogusJumpBank1 UnversionedScriptE98F
UnversionedScriptEA43:
    BogusSetSlot0660LowBits $01
    BogusSetSlotFields80 $01, $FF
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEA58, $14, $FF
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEA43, $1E, $10
    BogusLoadSlotRecord $00, $02
    BogusJumpBank1 UnversionedScriptE98F
UnversionedScriptEA58:
    BogusLoadSlotRecord $00, $02
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptEA6D, $0080
UnversionedScriptEA62:
    BogusAdjustSlotBounds $FF, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEA62, $14, $FF
    BogusJumpBank1 UnversionedScriptEA75
UnversionedScriptEA6D:
    BogusAdjustSlotBounds $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEA6D, $14, $FF
UnversionedScriptEA75:
    BogusLoadSlotRecord $1B, $02
    BogusJumpBank1 UnversionedScriptEA43
UnversionedScriptEA7B:
    BogusSetDirectionalSlotFields40 $40, $FF
    BogusWait $08
    BogusSetSlotFields80 $00, $00
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactEA85:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation003, $22
UnversionedCompactEA88:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation003, $22
UnversionedCompactEA8B:
    SlotCompactRecord Bank0::UnversionedSpriteFrame015, $00
UnversionedRecordEA8E:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation003, (UnversionedScriptEC2E - BankStart), $22, $00, $16, $61, $22
UnversionedRecordEA97:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEAA0:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame016, $FFFF, $00, $FF, $00, $00, $00
UnversionedRetainedEAA9:
; Separate retained two-byte tail between a normal record and compact
; records. Only the first byte is fetched as unused lookahead. The same
; boundaries survive in later releases; neither byte is an extra field.
    .byte $00, $00 ; CONTROL_UNVERSIONED_MAIN_EAA9
UnversionedCompactEAAB:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation003, $22
UnversionedCompactEAAE:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation003, $22
UnversionedCompactEAB1:
    SlotCompactRecord Bank0::UnversionedSpriteFrame017, $00
UnversionedRecordEAB4:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation003, (UnversionedScriptEC2E - BankStart), $22, $00, $16, $61, $22
UnversionedRecordEABD:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEAC6:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation001, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactEACF:
    SlotCompactRecord Bank0::UnversionedSpriteFrame216, $22
UnversionedCompactEAD2:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation086, $22
UnversionedCompactEAD5:
    SlotCompactRecord Bank0::UnversionedSpriteFrame216, $00
UnversionedRecordEAD8:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation086, (UnversionedScriptEAF3 - BankStart), $22, $00, $16, $41, $22
UnversionedRecordEAE1:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEAEA:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation084, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptEAF3:
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $42
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0640Pair $04, $00
    BogusClearSlot0790Bits $01
    BogusJumpBank1 UnversionedScriptEC5E
UnversionedCompactEB05:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation065, $22
UnversionedCompactEB08:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation065, $22
UnversionedCompactEB0B:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation066, $00
UnversionedRecordEB0E:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation065, (UnversionedScriptEC28 - BankStart), $22, $00, $16, $61, $22
UnversionedRecordEB17:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEB20:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation067, $FFFF, $00, $FF, $00, $00, $00
UnversionedRetainedEB29:
; Separate retained two-byte tail between a normal record and compact
; records. Only the first byte is fetched as unused lookahead. The same
; boundaries survive in later releases; neither byte is an extra field.
    .byte $00, $00 ; CONTROL_UNVERSIONED_MAIN_EB29
UnversionedCompactEB2B:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation089, $22
UnversionedCompactEB2E:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation089, $22
UnversionedCompactEB31:
    SlotCompactRecord Bank0::UnversionedSpriteFrame225, $00
UnversionedRecordEB34:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation089, (UnversionedScriptEB4F - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEB3D:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEB46:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation087, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptEB4F:
    BogusSetSlot0670Pair $08, $00
    BogusSetSlotValue $0008
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $02
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0640Pair $04, $08
    BogusClearSlot0790Bits $01
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueAtLeast UnversionedScriptEB6B, $000C
    BogusJumpBank1 UnversionedScriptEC5E
UnversionedScriptEB6B:
    BogusSetSlotD0Bits $04
    BogusJumpBank1 UnversionedScriptEC5E
UnversionedCompactEB70:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedCompactEB73:
    SlotCompactRecord UnversionedLiteralResource7C37, $27
UnversionedCompactEB76:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordEB79:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEC0A - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEB82:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEB8B:
    SlotRuntimeRecord UnversionedLiteralResource7C37, $FFFF, $00, $FF, $00, $00, $00
UnversionedCompactEB94:
    SlotCompactRecord Bank0::UnversionedSpriteFrame277, $00
UnversionedCompactEB97:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation111, $27
UnversionedCompactEB9A:
    SlotCompactRecord Bank0::UnversionedSpriteFrame278, $00
UnversionedRecordEB9D:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame275, (UnversionedScriptEC19 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEBA6:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEBAF:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation109, $FFFF, $00, $01, $25, $FF, $12
UnversionedCompactEBB8:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedCompactEBBB:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactEBBE:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordEBC1:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEC00 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEBCA:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEBD3:
    SlotRuntimeRecord UnversionedLiteralResource7C37, $FFFF, $40, $FF, $00, $00, $00
UnversionedCompactEBDC:
    SlotCompactRecord Bank0::UnversionedSpriteFrame127, $00
UnversionedCompactEBDF:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation044, $22
UnversionedCompactEBE2:
    SlotCompactRecord Bank0::UnversionedSpriteFrame126, $00
UnversionedRecordEBE5:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame126, (UnversionedScriptEC45 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEBEE:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEBF7:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation043, $FFFF, $40, $FF, $00, $00, $00
UnversionedScriptEC00:
    BogusSetSlotD0Bits $01
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusJumpBank1 UnversionedScriptEC56
UnversionedScriptEC0A:
    BogusSetSlot0670Pair $80, $00
    BogusSetSlotC0 $0A
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $40
    BogusJumpBank1 UnversionedScriptEC56
UnversionedScriptEC19:
    BogusSetSlot0670Pair $40, $00
    BogusSetSlotValue $0000
    BogusSetSlotC0 $08
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $40
    BogusJumpBank1 UnversionedScriptEC56
UnversionedScriptEC28:
    BogusSetSlot0670Pair $20, $00
    BogusJumpBank1 UnversionedScriptEC31
UnversionedScriptEC2E:
    BogusSetSlot0670Pair $00, $02
UnversionedScriptEC31:
    BogusSetSlotC0 $18
    BogusSetSlotValue $0000
    BogusStoreSlotValueArray $FF
    BogusSetSlotD0Bits $42
    BogusSetUnlinkedFields $00, $00
    BogusSetSlot0640Pair $04, $00
    BogusClearSlot0790Bits $01
    BogusJumpBank1 UnversionedScriptEC5E
UnversionedScriptEC45:
    BogusSetSlot0670Pair $08, $00
    BogusSetSlotValue $0008
    BogusStoreSlotValueArray $FF
    BogusReadSlotValue $0F
    BogusBranchIfSlotValueNotEqual UnversionedScriptEC56, $0005
    BogusSetSlotD0Bits $40
UnversionedScriptEC56:
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $18, $00
    BogusClearSlot0790Bits $01
UnversionedScriptEC5E:
    BogusBranchIfSlotD0Bits UnversionedScriptEC6A, $20
    BogusSetDispatchCounter $02
    BogusBranchIfSlot0620Bit10 UnversionedScriptECA8
    BogusJumpBank1 UnversionedScriptEC5E
UnversionedScriptEC6A:
    BogusSetDispatchCounter $02
    BogusRestartVoice4 $26EA
    BogusSetDispatchCounter $86
    BogusBranchIfSlotD0Bits UnversionedScriptEC78, $02
    BogusSetSlotFields80 $FF, $A0
UnversionedScriptEC78:
    BogusSetSlotFields80 $00, $FF
    BogusSetSlotFields40Signed $20, $00
    BogusJumpBank1 UnversionedScriptEC9F
UnversionedScriptEC81:
    BogusSetDispatchCounter $86
    BogusBranchIfSlotD0Bits UnversionedScriptEC91, $02
    BogusSetSlotFields80 $FF, $C0
    BogusBranchIfSlotD0BitsClear UnversionedScriptEC91, $01
    BogusStartVoice4 $27B4
UnversionedScriptEC91:
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $0C, $FF
    BogusBranchIfSlotCoordinates01 UnversionedScriptEC9F, $28, $10
    BogusSetDirectionalSlotFields40 $0C, $FF
UnversionedScriptEC9F:
    BogusLoadSlotRecord $09, $FF
    BogusSetSlot0620Bit20
    BogusClearSlotD0Bits $20
    BogusJumpBank1 UnversionedScriptEC5E
UnversionedScriptECA8:
    BogusLoadSlotRecord $00, $02
    BogusSetSlot0620Bit20
    BogusWait $02
    BogusBranchIfSlotD0BitsClear UnversionedScriptECBA, $01
    BogusLoadSlotRecord $12, $02
    BogusWait $0A
    BogusLoadSlotRecord $00, $02
UnversionedScriptECBA:
    BogusBranchIfSlotCoordinates01 UnversionedScriptED82, $1E, $10
    BogusBranchIfAbsSlot0700Below UnversionedScriptECE3, $18
    BogusBranchIfDirectionalOffsetClear UnversionedScriptECE3, $0C
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptECD6, $0080
    BogusBranchIfSlotOffset UnversionedScriptECE3, $02, $00
    BogusJumpBank1 UnversionedScriptECDB
UnversionedScriptECD6:
    BogusBranchIfSlotOffset UnversionedScriptECE3, $FE, $00
UnversionedScriptECDB:
    BogusSetSlot0620Bit20
    BogusAdvanceAndBranchState1B UnversionedScriptED5F, $20
    BogusJumpBank1 UnversionedScriptEC81
UnversionedScriptECE3:
    BogusSetDispatchCounter $83
    BogusBranchIfSlotD0Bits UnversionedScriptECF4, $04
UnversionedScriptECE9:
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptEC81
UnversionedScriptECF4:
    BogusSetSlotValue $0F00
    BogusReadMapAtSlotOffset
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptED0C, $00A2
    BogusLookupCaseBank1 UnversionedScriptED0C, $00A3
    BogusLookupCaseBank1 UnversionedScriptED0C, $000E
    BogusLookupEnd
    BogusSetDispatchCounter $83
    BogusJumpBank1 UnversionedScriptECE9
UnversionedScriptED0C:
    BogusSetDispatchCounter $87
    UnversionedSetSlot05C0 $02
    BogusSetSlotFields80 $20, $FF
    BogusYieldAndSlotAction $02
    BogusRestartVoice4 $266A
    BogusLoadSlotValueArray $2A
    BogusAddSlotValue $0001
    BogusStoreSlotValueArray $2A
    BogusBranchIfSlotValueAtLeast UnversionedScriptED2D, $0004
    BogusSetSlotValue $002F
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusYieldAndSlotAction $01
UnversionedScriptED2D:
    BogusRestartVoice4 $0000
    BogusSetVoicePointers $29FD, $2A15, $0000, $0000
    BogusSetSlotValue $0030
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusReadSlotValue $0F
    BogusAddSlotValue $0001
    BogusBranchIfSlotValueNotEqual UnversionedScriptED5D, $0010
    BogusSetSlotValue $0027
    BogusStoreSlotValueArray $3D
    BogusSaveStateAndPlaceSlots $11
    BogusSetSlotValue $0010
UnversionedScriptED5D:
    BogusSetMainState $00
UnversionedScriptED5F:
    BogusSetDispatchCounter $84
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $12, $02
    BogusLoadSlotValueArray $FF
    BogusBranchIfSlotValueAtLeast UnversionedScriptED77, $8000
    BogusStartVoice4FromIndexedPair $2640
    BogusJumpBank1 UnversionedScriptED7D
UnversionedScriptED77:
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $2654
UnversionedScriptED7D:
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptEC81
UnversionedScriptED82:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusLoadSlotRecord $12, $02
    BogusClearSlotD0Bits $40
UnversionedScriptED8F:
    BogusBranchIfSlotCoordinates01 UnversionedScriptED8F, $1E, $10
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptED96:
    BogusSetSlotD0Bits $02
UnversionedScriptED98:
    BogusSetSlotValue $0001
    BogusSetSlotD0Bits $01
    BogusJumpBank1 UnversionedScriptEE36
UnversionedCompactEDA0:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactEDA3:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordEDA6:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEDCA - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEDAF:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEDB8:
    SlotRuntimeRecord $FFFF, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordEDC1:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEEC4 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEDCA:
    BogusSetSlotValue $0000
    BogusSetSlotD0Bits $02
    BogusSetSlot05F0Pair $08, $60
    BogusJumpBank1 UnversionedScriptEE36
UnversionedCompactEDD5:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactEDD8:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordEDDB:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEDF6 - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEDE4:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEDED:
    SlotRuntimeRecord UnversionedLiteralResource7C37, $FFFF, $00, $FF, $00, $00, $00
UnversionedScriptEDF6:
    BogusSetSlotValue $0009
    BogusSetSlotD0Bits $09
    BogusSetSlot05F0Pair $10, $60
    BogusJumpBank1 UnversionedScriptEE36
UnversionedCompactEE01:
    SlotCompactRecord UnversionedLiteralResource7C37, $22
UnversionedCompactEE04:
    SlotCompactRecord UnversionedLiteralResource7C37, $00
UnversionedRecordEE07:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEE2B - BankStart), $22, $FF, $00, $00, $00
UnversionedRecordEE10:
    SlotRuntimeRecord $FFFF, (UnversionedScriptE763 - BankStart), $40, $FF, $00, $00, $00
UnversionedRecordEE19:
    SlotRuntimeRecord $FFFF, $FFFF, $00, $FF, $00, $00, $00
UnversionedRecordEE22:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEED1 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEE2B:
    BogusSetSlotValue $0000
    BogusSetSlotD0Bits $04
    BogusJumpBank1 UnversionedScriptEE36
UnversionedScriptEE33:
    BogusSetSlotValue $0003
UnversionedScriptEE36:
    BogusStoreSlotValueArray $FF
    BogusSetSlot0640Pair $04, $00
    BogusSetUnlinkedFields $00, $00
    BogusClearSlot0790Bits $01
    BogusBranchIfSlotFieldsWithin UnversionedScriptEE48, $07, $FF
    BogusJumpBank1 UnversionedScriptEE52
UnversionedScriptEE48:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $00
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusWait $0A
UnversionedScriptEE52:
    BogusSetDispatchCounter $06
    BogusBranchIfSlotD0BitsClear UnversionedScriptEE61, $08
    BogusAdvanceAndBranchState1B UnversionedScriptEE61, $E8
    BogusInitializeOtherSlotRelative $04, $00, $F0, $00
UnversionedScriptEE61:
    BogusBranchIfDirectionalOffsetClear UnversionedScriptEEA6, $0C
    BogusBranchIfAbsSlot0700Below UnversionedScriptEEA6, $20
    BogusReadSlotValue $11
    BogusBranchIfSlotValueAtLeast UnversionedScriptEE78, $0080
    BogusBranchIfSlotOffset UnversionedScriptEEA6, $02, $00
    BogusJumpBank1 UnversionedScriptEE7D
UnversionedScriptEE78:
    BogusBranchIfSlotOffset UnversionedScriptEEA6, $02, $00
UnversionedScriptEE7D:
    BogusSetSlot0670Pair $05, $00
    BogusBranchIfSlotD0BitsClear UnversionedScriptEE8D, $02
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEE8D, $30, $FF
    BogusAdvanceAndBranchState1B UnversionedScriptEEB3, $10
UnversionedScriptEE8D:
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEE97, $28, $FF
    BogusBranchIfSlotCoordinates01 UnversionedScriptEF0E, $30, $10
UnversionedScriptEE97:
    BogusBranchIfSlotD0BitsClear UnversionedScriptEE52, $04
    BogusSetSlot0670Pair $01, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptEEB3, $40, $40
    BogusJumpBank1 UnversionedScriptEE52
UnversionedScriptEEA6:
    BogusSetDispatchCounter $83
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $E8, $FF
    BogusWait $0A
    BogusJumpBank1 UnversionedScriptEE52
UnversionedScriptEEB3:
    BogusLoadRecordAndClearSavedState $1B
UnversionedScriptEEB5:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusWait $28
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptEEC4:
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusWait $28
    BogusSetDirectionalSlotFields40 $18, $FF
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptEED1:
    BogusSetDispatchCounter $82
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $FE, $FF
    BogusRestartVoice4 $277B
    BogusCreateLinkedSlot $64, $F8, $04, $00
    BogusWait $14
    BogusSetDirectionalSlotFields40 $E8, $FF
    BogusLoadRecordAndClearSavedState $00
UnversionedRecordEEE8:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEEF2 - BankStart), $23, $00, $20, $11, $11
UnversionedRetainedEEF1:
; Unused tenth-byte fetch lookahead after the EEE8 record's nine fields.
; Its explicit script word selects EEF2, which begins the normal 0C command.
    .byte $00
UnversionedScriptEEF2:
    BogusSetSlot0670Pair $01, $00
    BogusSetSlotC0 $00
    BogusInitializeSlotMotionFields
    BogusSetSlot0660LowBits $01
    BogusSetSlot0660HighBits $01
    BogusSetSlot05F0Pair $20, $20
    BogusSetSlot0360 $28
UnversionedScriptEF01:
    BogusAddSlotFields00 $08, $08
    BogusSetSlot0620Bit20
    BogusBranchAndClearSlot0620Bit08 UnversionedScriptEF0C
    BogusBranchIfSlot0360Above UnversionedScriptEF01, $01
UnversionedScriptEF0C:
    BogusYieldAndSlotAction $00
UnversionedScriptEF0E:
    BogusLoadSlotValueArray $FF
    BogusBranchIfSlotValueAtLeast UnversionedScriptEF2E, $8000
    BogusStartVoice4FromIndexedPair $2640
    BogusBranchIfSlotD0BitsClear UnversionedScriptEF2C, $01
    BogusSetDispatchCounter $84
    BogusLoadSlotRecord $12, $01
    BogusSetSlotFields80 $00, $FF
    BogusSetDirectionalSlotFields40 $01, $FF
    BogusWait $0A
    BogusSetDirectionalSlotFields40 $18, $FF
UnversionedScriptEF2C:
    BogusLoadRecordAndClearSavedState $00
UnversionedScriptEF2E:
    BogusMaskSlotValue $7FFF
    BogusSetVoicesFromIndexedRecord $2654
    BogusLoadRecordAndClearSavedState $00
UnversionedCompactEF36:
    SlotCompactRecord Bank0::UnversionedSpriteAnimation000, $00
UnversionedRecordEF39:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame006, (UnversionedScriptEF4B - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF42:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame006, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEF4B:
    BogusSetSlot0640Pair $00, $50
    BogusSetSlotD0Bits $01
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedRecordEF53:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame078, (UnversionedScriptF0E4 - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordEF5C:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF65:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame076, (UnversionedScriptF0F0 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF6E:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF77:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame288, (UnversionedScriptF0E4 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF80:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF89:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame013, (UnversionedScriptEF9B - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEF92:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEF9B:
    BogusSetSlot0640Pair $00, $44
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedRecordEFA1:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame291, (UnversionedScriptEFB3 - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordEFAA:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEFB3:
    BogusSetSlot0640Pair $40, $40
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedRecordEFB9:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation038, (UnversionedScriptEFDD - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordEFC2:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEFCB:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEFDD - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordEFD4:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEFDD:
    BogusSetSlot0640Pair $00, $42
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedRecordEFE3:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptEFF5 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordEFEC:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptEFF5:
    BogusSetSlot0640Pair $00, $41
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedRecordEFFB:
    SlotRuntimeRecord UnversionedLiteralResource7C37, (UnversionedScriptF00D - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF004:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptF00D:
    BogusSetSlot0640Pair $80, $40
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedRecordF013:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame181, (UnversionedScriptF0F0 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF01C:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF025:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame182, (UnversionedScriptF0F0 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF02E:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF037:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame007, (UnversionedScriptF0F0 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF040:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF049:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame008, (UnversionedScriptF0F7 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF052:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF05B:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame000, (UnversionedScriptF09A - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordF064:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF06D:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame036, (UnversionedScriptF09A - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordF076:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedRecordF07F:
    SlotRuntimeRecord Bank0::UnversionedSpriteFrame215, (UnversionedScriptF091 - BankStart), $00, $00, $20, $D9, $11
UnversionedRecordF088:
    SlotRuntimeRecord $FFFF, (UnversionedScriptF116 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptF091:
    BogusSetSlot0640Pair $00, $40
    BogusSetSlotC0 $0C
    BogusBranchIfSlot0780Equal UnversionedScriptF0FA, $00
UnversionedScriptF09A:
    BogusSetSlot0640Pair $20, $40
    BogusSetDispatchCounter $8C
    BogusSetSlot05F0Pair $60, $60
    BogusSetSlot0670Pair $01, $00
    BogusSetSlot0660LowBits $01
    BogusSetSlot0730 $80
    BogusLoadSlotValueArray $3C
    BogusSetSlotMode $00
    BogusSetSlotFields80 $00, $A0
    BogusRelinkSlots
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptF0C9, $10, $FF
    BogusAddSlotFields00 $10, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptF0C9, $30, $FF
    BogusAddSlotFields00 $10, $00
    BogusBranchIfSlotCoordinatesA3 UnversionedScriptF0C9, $60, $FF
    BogusAddSlotFields00 $20, $00
UnversionedScriptF0C9:
    BogusSetSlot0620Bit20
    BogusBranchIfSlot0620Bit10 UnversionedScriptF0D3
    BogusBranchIfSlotB0AtMost UnversionedScriptF0C9, $E6
    BogusYieldAndSlotAction $00
UnversionedScriptF0D3:
    BogusSetDispatchCounter $03
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusClearSlot0790Bits $01
    BogusWait $14
    BogusSetSlotMode $FF
    BogusJumpBank1 UnversionedScriptF0C9
UnversionedScriptF0E4:
    BogusSetSlot0640Pair $08, $40
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedScriptF0EA:
    BogusSetSlot0640Pair $20, $40
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedScriptF0F0:
    BogusBranchIfSlot0780Equal UnversionedScriptF09A, $2C
    BogusJumpBank1 UnversionedScriptF0EA
UnversionedScriptF0F7:
    BogusSetSlot0640Pair $10, $40
UnversionedScriptF0FA:
    BogusSetSlotC0 $FF
    BogusClearSlot0790Bits $01
    BogusClearSlotD0Bits $02
UnversionedScriptF100:
    BogusBranchIfSlotD0Bits UnversionedScriptF107, $01
    BogusJumpBank1 UnversionedScriptF100
UnversionedScriptF107:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptF0FA
    BogusBranchIfSlotD0Bits UnversionedScriptF100, $02
    BogusSetSlotD0Bits $02
    BogusLoadSlotRecord $03, $FF
    BogusJumpBank1 UnversionedScriptF100
UnversionedScriptF116:
    BogusSetDispatchCounter $07
    BogusBranchIfSelectedFieldEqual UnversionedScriptF152, $12
    BogusBranchIfSlot06D0Present UnversionedScriptF176
    BogusBranchIfSelectedFieldEqual UnversionedScriptF12C, $10
    BogusBranchIfSelectedFieldEqual UnversionedScriptF1DB, $1F
    BogusBranchIfSelectedFieldEqual UnversionedScriptF1DF, $07
    BogusRestoreSavedScriptAndSlotFlags
UnversionedScriptF12C:
    BogusSetSlot0790Bits $FF
    BogusFollowLinkedSlotsAndYield $FF, $FF, $23, $00, $00
    BogusSetSlot05E0Bit40 $01
    BogusSetLinkedFieldsAndYield $FF, $FE
    BogusSetLinkedFieldsAndYield $FF, $FC
    BogusSetLinkedFieldsAndYield $FF, $F8
    BogusSetLinkedFieldsAndYield $FF, $F4
    BogusSetLinkedFieldsAndYield $80, $F2
UnversionedScriptF145:
    BogusSetSlot07F0 $14
    BogusSetSlot0630Bit04UnlessFF $01
    BogusClearSlot0640PairBits $00, $40
UnversionedScriptF14C:
    BogusCopyLinkedMotionFields
    BogusClearSlot0790Bits $01
    BogusJumpBank1 UnversionedScriptF14C
UnversionedScriptF152:
    BogusRelinkSlots
    BogusSetDispatchCounter $8F
    BogusSetSlotC0 $FF
    BogusReadSlotValue $13
    BogusSetSlotMode $00
    BogusSetSlotMode $02
    BogusSetSlot05E0Bit40 $FF
    BogusSetSlot05F0Pair $60, $60
    BogusSetSlot0730 $80
    BogusSetSlotPositionFromOperands $60, $A7
    BogusSetSlot0660LowBits $00
    BogusSetSlotFields80 $38, $A0
UnversionedScriptF16C:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptF16C
    BogusWait $01
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptF16C
    BogusYieldAndSlotAction $01
UnversionedScriptF176:
    BogusBranchIfSelectedFieldEqual UnversionedScriptF18D, $11
    BogusBranchIfSelectedFieldEqual UnversionedScriptF1C1, $13
    BogusBranchIfSelectedFieldEqual UnversionedScriptF1F0, $14
    BogusBranchIfSelectedFieldEqual UnversionedScriptF189, $1E
    BogusJumpBank1 UnversionedScriptF145
UnversionedScriptF189:
    BogusRelinkToLastRelatedSlot
    BogusJumpBank1 UnversionedScriptF145
UnversionedScriptF18D:
    BogusSetDispatchCounter $88
    BogusSetSlot05F0Pair $7F, $7F
    BogusCopyLinkedMotionFields
    BogusSetDirectionalSlotFields40 $38, $FF
    BogusSetSlot0730 $80
    BogusSetSlotMode $03
    BogusSetSlot0640PairBits $00, $40
    BogusRelinkSlots
    BogusSetSlot07F0 $44
    BogusSetSlot05E0Bit40 $FF
    BogusClearSlot0790Bits $01
    BogusBranchIfSlotD0BitsClear UnversionedScriptF1AC, $01
    BogusBranchIfSlot0760Equal UnversionedScriptF1FA, $02
UnversionedScriptF1AC:
    BogusSetSlot0620Bit20
    BogusBranchIfSlot0620Bit10 UnversionedScriptF1B6
    BogusBranchIfSlotB0AtMost UnversionedScriptF1AC, $E6
    BogusYieldAndSlotAction $00
UnversionedScriptF1B6:
    BogusStartVoice4 $2694
    BogusWait $01
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptF1AC
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedScriptF1C1:
    BogusSetDispatchCounter $87
    BogusSetSlotFields80 $00, $E0
    BogusSetSlotMode $03
    BogusSetSlot0640PairBits $00, $40
    BogusRelinkSlots
    BogusSetSlot07F0 $44
    BogusSetSlot05E0Bit40 $FF
    BogusClearSlot0790Bits $01
UnversionedScriptF1D2:
    BogusBranchIfSlot0620Bit10Clear UnversionedScriptF1D2
    BogusStartVoice4 $2694
    BogusJumpBank1 UnversionedScriptF0FA
UnversionedScriptF1DB:
    BogusWait $1E
    BogusYieldAndSlotAction $00
UnversionedScriptF1DF:
    BogusSetDirectionalSlotFields40 $08, $FF
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusSetSlotFields80 $FF, $A0
    BogusClearSlot0790Bits $01
    BogusJumpBank1 UnversionedScriptF1AC
UnversionedScriptF1F0:
    BogusReadSlotValue $02
    BogusSwapSlotValueBytes
    BogusLoadSlotLowFromByteArray $2A
    BogusSwapSlotValueBytes
    BogusStoreSlotLowAtIndexedPage
    BogusJumpBank1 UnversionedScriptF145
UnversionedScriptF1FA:
    BogusSetSlotMode $FF
    BogusSetSlot05F0Pair $FF, $40
UnversionedScriptF1FF:
    BogusBranchIfRemainingVerticalOffsetAtMost UnversionedScriptF20A, $0028
    BogusBranchIfSecondWorldOffsetAtMost UnversionedScriptF1FF, $1EE5
UnversionedRetainedF209:
; The F1FF branch selects F20A. A normal return from the five-byte 9F at
; F204 instead enters this 00 byte: 00/2C, 85/2D and 00/00 overlap the
; F20A dispatch-counter and F20C pair command before rejoining at F20F.
; Record replacement depends on the loader path; ordinary execution of
; this alternative is not asserted. Preserve both views without extra bytes.
    .byte $00
UnversionedScriptF20A:
    BogusSetDispatchCounter $85
UnversionedScriptF20C:
    BogusSetSlotFields80 $00, $00
    BogusSetSlotC0 $00
    BogusSetSlot0640Pair $00, $00
    BogusRestartVoice4 $27F7
    BogusInitializeOtherSlotRelative $77, $00, $02, $00
    BogusWait $05
    BogusYieldAndSlotAction $00
UnversionedRecordF220:
    SlotRuntimeRecord Bank0::UnversionedSpriteAnimation106, (UnversionedScriptF229 - BankStart), $00, $FF, $00, $00, $00
UnversionedScriptF229:
    BogusSetDispatchCounter $8F
    BogusSetSlotC0 $00
    BogusQueueState6E $73EE, $0B, $0C, $00, $09 ; CONTROL_UNVERSIONED_MAIN_F22D
    BogusQueueState6E $73F7, $0C, $0C, $00, $09
    BogusQueueState6E $7400, $0D, $0C, $00, $11
    BogusQueueState6E $7411, $0E, $0C, $00, $11
    BogusQueueState6E $73CC, $19, $0A, $00, $12
    BogusQueueState6E $73DE, $1A, $0F, $00, $08
    BogusQueueState6E $73E6, $1B, $0F, $00, $08
    BogusReadSlotValue $00
    BogusBranchIfSlotValueNotEqual UnversionedScriptF284, $0000
    BogusQueueState6E $73A6, $10, $11, $00, $01
    BogusQueueState6E $73A7, $11, $0D, $00, $0A
    BogusQueueState6E $73B1, $13, $0D, $00, $0A
    BogusQueueState6E $73BB, $15, $0D, $00, $11
    BogusJumpBank1 UnversionedScriptF299
UnversionedScriptF284:
    BogusQueueState6E $738B, $11, $0D, $00, $0A
    BogusQueueState6E $7381, $13, $0D, $00, $0A
    BogusQueueState6E $7395, $15, $0D, $00, $11
UnversionedScriptF299:
    BogusBranchIfState07ZeroAndClear UnversionedScriptF2A5
    UnversionedBogusSetSelectedPair $00, $0000
    BogusSetSlotValue $0001
    BogusSetInvertedState3B $FF
UnversionedScriptF2A5:
    BogusSetInvertedState18 $FF
    BogusSetState03BC $00
    BogusSetInvertedState03ED $01
    BogusSetSlotAssociation $00
    BogusSetSelectedField $02, $01
    BogusSetVoicePointers $2802, $284D, $0000, $0000
    BogusJumpBank1 UnversionedScriptF2D0
UnversionedScriptF2BC:
    BogusSetSlotPositionFromOperands $58, $78
    BogusWait $03
UnversionedScriptF2C1:
    BogusBranchIfSelectedFlags UnversionedScriptF2D0, $24
    BogusBranchIfSelectedFlags UnversionedScriptF2E4, $08
    BogusBranchIfSelectedFlags UnversionedScriptF2F8, $D0
    BogusJumpBank1 UnversionedScriptF2C1
UnversionedScriptF2D0:
    BogusSetSlotPositionFromOperands $58, $88
    BogusWait $03
UnversionedScriptF2D5:
    BogusBranchIfSelectedFlags UnversionedScriptF2E4, $24
    BogusBranchIfSelectedFlags UnversionedScriptF2BC, $08
    BogusBranchIfSelectedFlags UnversionedScriptF2F8, $D0
    BogusJumpBank1 UnversionedScriptF2D5
UnversionedScriptF2E4:
    BogusSetSlotPositionFromOperands $58, $98
    BogusWait $03
UnversionedScriptF2E9:
    BogusBranchIfSelectedFlags UnversionedScriptF2BC, $24
    BogusBranchIfSelectedFlags UnversionedScriptF2D0, $08
    BogusBranchIfSelectedFlags UnversionedScriptF2F8, $D0
    BogusJumpBank1 UnversionedScriptF2E9
UnversionedScriptF2F8:
    BogusReadSlotValue $00
    BogusBranchIfSlotValueEqual UnversionedScriptF337, $00, $00
    BogusSetDispatchCounter $8F
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusClearSlotBitset $FF
    BogusClearState13Bits $0F
    BogusReadSlotValue $52
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptF323, $0078
    BogusLookupCaseBank1 UnversionedScriptF31F, $0088
    BogusLookupCaseBank1 UnversionedScriptF335, $0098
    BogusLookupEnd
UnversionedScriptF31F:
    BogusLoadSlotValueArray $3A
    BogusSetMainState $00
UnversionedScriptF323:
    BogusLoadSlotValueArray $3A
    BogusBranchIfSlotValueAtLeast UnversionedScriptF32C, $0006
    BogusSetMainState $01
UnversionedScriptF32C:
    BogusBranchIfSlotValueAtLeast UnversionedScriptF333, $000C
    BogusSetMainState $06
UnversionedScriptF333:
    BogusSetMainState $0C
UnversionedScriptF335:
    BogusSetMainState $FF
UnversionedScriptF337:
    BogusSetDispatchCounter $8F
    BogusClearSlotBitset $FF
    BogusSetVoicePointers $0000, $0000, $0000, $0000
    BogusClearState13Bits $0F
    BogusSetBackgroundPalettePointer Bank0::UnversionedPalette05
    BogusSetSpritePalettePointer Bank0::UnversionedPalette05
    BogusReadSlotValue $52
    BogusLookupSlotValue
    BogusLookupCaseBank1 UnversionedScriptF35D, $0078
    BogusLookupCaseBank1 UnversionedScriptF368, $0088
    BogusLookupCaseBank1 UnversionedScriptF373, $0098
    BogusLookupEnd
UnversionedScriptF35D:
    BogusSetSlotValue $000A
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $0001
    BogusJumpBank1 UnversionedScriptF422
UnversionedScriptF368:
    BogusSetSlotValue $002B
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $0006
    BogusJumpBank1 UnversionedScriptF422
UnversionedScriptF373:
    BogusSetSlotValue $0012
    BogusStoreSlotValueArray $3D
    BogusSetSlotValue $000C
    BogusJumpBank1 UnversionedScriptF422
UnversionedRetainedF37E:
; Three retained prefix bytes lie outside all14 menu tile payloads.
; The preceding branch leaves this region; original purpose is unknown.
    .byte $00, $00, $20
UnversionedMenuPayloadF381:
    .incbin "unversioned-menu-tiles.bin"
UnversionedScriptF422:
    BogusSaveStateAndPlaceSlots $11
    BogusSetMainState $00
UnversionedScriptF426:
    BogusReleaseOtherSlots ; CONTROL_UNVERSIONED_MAIN_F426
    BogusSetSlotPositionFromOperands $FE, $C0
    UnversionedFillRowsAndSetMainState $00
.assert * = $F42C, error, "own main scripts end"
UnversionedConditionalF209 = UnversionedRetainedF209
UnversionedConditionalF20B = UnversionedScriptF20A + 1
UnversionedConditionalF20D = UnversionedScriptF20C + 1
.endmacro
