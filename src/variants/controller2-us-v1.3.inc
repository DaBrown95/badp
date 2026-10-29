; v1.3 NMI additions around the common first-controller work. JOY1 strobes
; both controllers. The second serial input is $4017; its current/changed
; states and repeat masks occupy the adjacent odd/even RAM fields below.
; These five expansions add 143 native bytes without duplicating common NMI.
.macro ReadSecondController
    .local readBit
    lda #$00
    sta $0390
    ldx #$08
readBit:
    lda $4017
    ror a
    rol $0390
    dex
    bne readBit
    lda $0390
    tax
    eor $038E
    sta $0390
    stx $038E
.endmacro

.macro FilterSecondControllerRepeat
    lda $038E
    and $0393
    sta $0393
    lda $038E
    and $0395
    sta $0395
.endmacro

.macro MergeSecondControllerRepeat
    lda $0393
    ora $0390
    sta $0390
.endmacro

.macro SaveSecondControllerRepeat
    lda $0395
    and #$0F
    sta $0393
    lda $038E
    sta $0395
.endmacro

; The first-controller dispatch's two empty/finished branches reach this
; second dispatch. Both controllers can call their corresponding handlers in
; one frame. Pause is shared; movement/action entry variants select the slot.
.macro DispatchSecondController
    .local handler1Done, handler2Done, handler3Done, handler4Done
    .local handler5Done, handler6Done, handler7Done
    lda $0390
    and $038E
    beq FrameEngineWork
    ror $0390
    bcc handler1Done
    jsr ControllerPositiveXSecond
handler1Done:
    ror $0390
    bcc handler2Done
    jsr ControllerNegativeXSecond
handler2Done:
    ror $0390
    bcc handler3Done
    jsr ControllerPositiveYSecond
handler3Done:
    ror $0390
    bcc handler4Done
    jsr ControllerNegativeYSecond
handler4Done:
    ror $0390
    bcc handler5Done
    jsr ControllerTogglePause
handler5Done:
    ror $0390
    bcc handler6Done
    jsr ControllerConfiguredActionSecond
handler6Done:
    ror $0390
    bcc handler7Done
    jsr ControllerAction2DSecond
handler7Done:
    ror $0390
    bcc FrameEngineWork
    jsr ControllerAction24Second
.endmacro
