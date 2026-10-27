.setcpu "6502"
.include "nes.inc"

; Both 32 KiB PRG banks contain this tail at the same CPU addresses.
; NMI state addresses differ; its called routines and timing remain to be traced.
.macro BankTail nmiValue, nmiIndex, padding
SwitchBank:
    sta BankValues,y             ; CONTROL_SWITCH
    rts

; Each byte selects a CHR bank and PRG bank. The matching byte at the write
; address also prevents conflicting values from being driven on the ROM bus.
BankValues:
    .repeat 8, chrBank
        .byte ($0C | (chrBank << 4)), ($0D | (chrBank << 4)) ; CONTROL_TABLE
    .endrepeat

NmiHandler:
    pha
    tya
    pha
    lda nmiValue
    sta NmiSavedValue
    lda nmiIndex
    sta NmiSavedIndex
    jsr $FE9F
    jsr $8211
    lda NmiSavedValue
    ldy NmiSavedIndex            ; CONTROL_NMI
    jsr SwitchBank
    pla
    tay
    pla
IrqHandler:
    rti

ResetEntry:
    ldx #$FF                     ; CONTROL_RESET
    txs
    lda #$0C
    sta BankValues
    jmp $8000

    .incbin padding              ; Unclassified six-byte local region.
    .word NmiHandler, ResetEntry, IrqHandler ; CONTROL_VECTORS
.endmacro

.segment "HEADER"
; Exact NES 2.0 container header for the pinned reference. This is metadata.
.byte $4E, $45, $53, $1A, $04, $08, $B1, $08
.byte $00, $00, $00, $00, $00, $00, $00, $01

.segment "PRG0"
.scope Bank0
BankStart:
Boot:
    sei                          ; CONTROL_BOOT
    lda #$00
    sta PPUCTRL
    jsr WaitVBlank
    jsr WaitVBlank
    lda #$06
    sta PPUMASK

    .incbin "bank0_8011_9ed0.bin"
.assert (* - BankStart) = $1ED0, error, "bank 0 wait routine offset"
WaitVBlank:
    lda PPUSTATUS                ; CONTROL_WAIT
    bpl WaitVBlank
    rts

    .incbin "bank0_9ed6_ffb3.bin"
.assert (* - BankStart) = $7FB3, error, "bank 0 tail offset"
    BankTail $03C0, $03C1, "bank0_fff4_fffa.bin"
.assert (* - BankStart) = $8000, error, "bank 0 size"
.endscope

.segment "PRG1"
.scope Bank1
BankStart:
    .incbin "bank1_8000_ffb3.bin"
.assert (* - BankStart) = $7FB3, error, "bank 1 tail offset"
    BankTail $03C2, $03C3, "bank1_fff4_fffa.bin"
.assert (* - BankStart) = $8000, error, "bank 1 size"
.endscope

.segment "CHR"
    .incbin "chr.bin"             ; Local, unconverted graphics data.
