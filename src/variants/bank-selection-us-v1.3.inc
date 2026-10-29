; v1.3 bank-selection producer, CPU $EB6A-$EB8D. The packed input remains
; in Y while X selects the paired ROM conflict-table entry. Reset state $0A
; uses the first sixteen entries ($08/$09 per CHR bank); other reset states
; select the following sixteen ($0C/$0D). Preserve both return paths.
ComputeBankSelection:
    tay                           ; CONTROL_COMPUTE_BANK_SELECTION
    and #$01
    sta $11
    tya
    jsr ShiftARight3
    ora $11
    tax
    tya
    ora #$08
    tay
    lda $04DE
    and #$7F
    cmp #$0A
    beq BankSelectionReturnSaved
    txa
    clc
    adc #$10
    tax
    tya
    ora #$04
    rts
BankSelectionReturnSaved:
    tya
    rts
