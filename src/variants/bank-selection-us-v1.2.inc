; v1.2 bank selector, CPU $EB80-$EB8F. Y preserves the packed input;
; X selects the paired conflict-table entry. There is one sixteen-entry
; table, without v1.3's reset-state-dependent second half.
ComputeBankSelection:
    tay                           ; CONTROL_COMPUTE_BANK_SELECTION
    and #$01
    sta $11
    tya
    lsr a
    lsr a
    lsr a
    ora $11
    tax
    tya
    ora #$0C
    rts
