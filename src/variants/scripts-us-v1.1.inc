; These BOGUS forms use the already reconstructed shared handlers. Opcode
; $3A has three bytes, while the $38 alias has an additional ignored byte.
.macro BogusAddSelectedField3A selector, delta
    .byte $3A, selector, delta
.endmacro
.macro BogusReadSelectedField selector
    .byte $73, selector
.endmacro

; The encoded word after the $15 byte selects this fallthrough, while the
; preceding unconditional jump selects InteractionScriptAF05. Their targets
; coincide in later versions. Original purpose and ordinary entry are unknown.
V11AF02Fallthrough:
    BogusAddSelectedField3A $02, $FF ; CONTROL_V11_AF02_SCRIPT
    BogusReadSelectedField $02
    BogusBranchIfSlotValueEqual InteractionScriptAF05, $00, $00
    BogusBranchIfRemainingVerticalOffsetAtMost V11AF02Continue, $0004
    BogusSetSlotValue $000C
    BogusStoreSlotValueArray $26
    BogusSetSlot0520 $0C
    BogusLoadRecordAndClearSavedState $48
V11AF02Continue:
    BogusReadSlotValue $0F
    BogusJumpBank1 CandidateScriptF40A
