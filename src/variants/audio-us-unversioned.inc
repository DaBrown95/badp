; Own audio bank: indexed voice-4 pointers, two four-voice records and
; interpreter-format effects/music. Native consumers B3 and78 select the
; tables through script operands. Eight loop words name actual command
; boundaries. This source does not assert ordinary playback of every entry.
.macro UnversionedBank1Audio
UnversionedIndexedVoice4A640:
    AudioPointerEntry (UnversionedAudioA669 - BankStart) ; CONTROL_UNVERSIONED_AUDIO_POINTER
    AudioPointerEntry (UnversionedAudioA76E - BankStart)
    AudioPointerEntry (UnversionedAudioA719 - BankStart)
    AudioPointerEntry (UnversionedAudioA6B5 - BankStart)
    AudioPointerEntry (UnversionedAudioA7AB - BankStart)
    AudioPointerEntry (UnversionedAudioA7B4 - BankStart)
    AudioPointerEntry (UnversionedAudioA7BD - BankStart)
    AudioPointerEntry (UnversionedAudioA7C6 - BankStart)
    AudioPointerEntry (UnversionedAudioA79E - BankStart)
    AudioPointerEntry (UnversionedAudioA7DC - BankStart)
.assert * = $A654, error, "own voice4 table end"
UnversionedIndexedVoiceRecordsA654:
    AudioVoicePointerRecord $FFFF, $FFFF, (UnversionedAudioA74A - BankStart), (UnversionedAudioA75B - BankStart)
    AudioVoicePointerRecord $FFFF, $FFFF, (UnversionedAudioA664 - BankStart), (UnversionedAudioA665 - BankStart)
.assert * = $A664, error, "own four-voice records end"
UnversionedAudioA664:
    AudioStopVoice
UnversionedAudioA665:
    AudioStopVoice
UnversionedAudioA666:
    AudioDelay $B4
    AudioStopVoice
UnversionedAudioA669:
    AudioStopVoice
UnversionedAudioA66A:
    AudioSelectChannel $00
    AudioWriteFive $9D, $BB, $50, $BC ; CONTROL_UNVERSIONED_AUDIO_REGISTER_VALUES
    AudioDelay $08
    AudioRestartChannel
    AudioDelay $02
    AudioSelectChannel $00
    AudioWriteFive $9D, $BB, $50, $BB
    AudioDelay $08
    AudioRestartChannel
    AudioDelay $02
    AudioSelectChannel $00
    AudioWriteFive $9D, $BB, $50, $BA
    AudioDelay $08
    AudioRestartChannel
    AudioDelay $02
    AudioSelectChannel $00
    AudioWriteFive $9D, $BB, $50, $B9
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA694:
    AudioSelectChannel $03
    AudioSetChannelMask
    AudioWriteFive $5F, $00, $8F, $00
    AudioDelay $0F
    AudioClearChannelMask
    AudioStopVoice
UnversionedAudioA69F:
    AudioSelectChannel $00
    AudioWriteFive $C1, $85, $44, $30
    AudioDelay $04
    AudioLoop $07, (UnversionedAudioA69F - BankStart)
    AudioStopVoice
UnversionedAudioA6AC:
    AudioSelectChannel $01
    AudioWriteFive $6A, $97, $A0, $C8
    AudioDelay $12
    AudioStopVoice
UnversionedAudioA6B5:
    AudioSelectChannel $03
    AudioWriteFive $E0, $AC, $00, $F3
    AudioDelay $12
    AudioStopVoice
UnversionedAudioA6BE:
    AudioSelectChannel $01
    AudioWriteFive $85, $8B, $8D, $59
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA6C7:
    AudioSelectChannel $00
    AudioWriteFive $CA, $D7, $FF, $0C
    AudioDelay $18
    AudioStopVoice
UnversionedAudioA6D0:
    AudioSelectChannel $03
    AudioWriteFive $94, $D9, $7B, $38
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA6D9:
    AudioSelectChannel $03
    AudioWriteFive $94, $D9, $7A, $38
    AudioDelay $02
    AudioSelectChannel $03
    AudioWriteFive $94, $D9, $7B, $38
    AudioDelay $01
    AudioStopVoice
UnversionedAudioA6EA:
    AudioSelectChannel $00
    AudioWriteFive $9A, $8B, $FF, $DC
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA6F3:
    AudioSelectChannel $00
    AudioWriteFive $AE, $8E, $00, $99
    AudioDelay $18
    AudioStopVoice
UnversionedAudioA6FC:
    AudioSelectChannel $01
    AudioDelay $04
    AudioWriteFive $AE, $8E, $00, $99
    AudioDelay $18
    AudioStopVoice
UnversionedAudioA707:
    AudioSelectChannel $00
    AudioWriteFive $A3, $9B, $FF, $07
    AudioDelay $18
    AudioStopVoice
UnversionedAudioA710:
    AudioSelectChannel $00
    AudioWriteFive $A0, $8B, $00, $03
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA719:
    AudioSelectChannel $01
    AudioWriteFive $1E, $92, $EF, $28
    AudioDelay $03
    AudioSelectChannel $01
    AudioWriteFive $1E, $96, $EF, $28
    AudioDelay $03
UnversionedAudioA729:
    AudioSelectChannel $01
    AudioWriteFive $1E, $92, $EF, $28
    AudioDelay $03
    AudioLoop $02, (UnversionedAudioA729 - BankStart)
    AudioSelectChannel $01
    AudioWriteFive $1E, $94, $EF, $28
    AudioDelay $03
UnversionedAudioA73D:
    AudioSelectChannel $01
    AudioWriteFive $1E, $98, $EF, $28
    AudioDelay $03
    AudioLoop $03, (UnversionedAudioA73D - BankStart)
    AudioStopVoice
UnversionedAudioA74A:
    AudioSelectChannel $00
    AudioWriteFive $3E, $AE, $FF, $25
    AudioDelay $0C
    AudioSelectChannel $00
    AudioWriteFive $3E, $A6, $FF, $24
    AudioDelay $10
    AudioStopVoice
UnversionedAudioA75B:
    AudioSelectChannel $01
    AudioDelay $02
    AudioWriteFive $3E, $AE, $FF, $25
    AudioDelay $0C
    AudioSelectChannel $01
    AudioWriteFive $3E, $A6, $FF, $24
    AudioDelay $10
    AudioStopVoice
UnversionedAudioA76E:
    AudioSelectChannel $00
    AudioWriteFive $C0, $82, $4D, $B0
    AudioDelay $0C
    AudioLoop $02, (UnversionedAudioA76E - BankStart)
    AudioStopVoice
UnversionedAudioA77B:
    AudioSelectChannel $01
    AudioWriteFive $1C, $9C, $EE, $27
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA784:
    AudioSelectChannel $03
    AudioWriteFive $00, $00, $00, $00
    AudioDelay $04
    AudioStopVoice
UnversionedAudioA78D:
    AudioSelectChannel $01
    AudioWriteFive $98, $BB, $D0, $BB
    AudioDelay $03
    AudioSelectChannel $01
    AudioWriteFive $98, $BA, $D0, $BB
    AudioDelay $04
    AudioStopVoice
UnversionedAudioA79E:
    AudioSelectChannel $00
    AudioWriteFive $C0, $9C, $00, $83
    AudioDelay $02
    AudioLoop $08, (UnversionedAudioA79E - BankStart)
    AudioStopVoice
UnversionedAudioA7AB:
    AudioSelectChannel $01
    AudioWriteFive $8E, $8B, $00, $8B
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA7B4:
    AudioSelectChannel $01
    AudioWriteFive $9F, $FC, $00, $FF
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA7BD:
    AudioSelectChannel $00
    AudioWriteFive $DA, $9C, $1D, $88
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA7C6:
    AudioSelectChannel $03
    AudioWriteFive $DF, $00, $02, $1A
    AudioDelay $02
    AudioLoop $08, (UnversionedAudioA7C6 - BankStart)
    AudioStopVoice
UnversionedAudioA7D3:
    AudioSelectChannel $00
    AudioWriteFive $9F, $99, $01, $19
    AudioDelay $04
    AudioStopVoice
UnversionedAudioA7DC:
    AudioSelectChannel $01
    AudioDelay $08
    AudioWriteFive $1B, $9D, $00, $83
    AudioDelay $14
    AudioWriteFive $1B, $9D, $00, $83
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA7EE:
    AudioSelectChannel $01
    AudioWriteFive $7D, $8C, $20, $8C
    AudioDelay $08
    AudioStopVoice
UnversionedAudioA7F7:
    AudioSelectChannel $03
    AudioSetChannelMask
    AudioWriteFive $EC, $34, $04, $F1
    AudioDelay $28
    AudioClearChannelMask
    AudioStopVoice
UnversionedAudioA802:
    AudioSelectChannel $00
    AudioInstrument $01
    AudioNote $01, $1F ; CONTROL_UNVERSIONED_AUDIO_NOTE
    AudioNote $01, $11
    AudioNote $01, $13
    AudioNote $01, $15
    AudioNote $01, $18
    AudioNote $01, $16
    AudioNote $01, $16
    AudioNote $01, $1A
    AudioNote $01, $18
    AudioNote $01, $18
    AudioNote $01, $1D
    AudioNote $01, $1C
    AudioNote $01, $1D
    AudioNote $01, $18
    AudioNote $01, $15
    AudioNote $01, $11
    AudioNote $01, $13
    AudioNote $01, $15
    AudioNote $01, $16
    AudioNote $01, $18
    AudioNote $01, $1A
    AudioNote $01, $18
    AudioNote $01, $16
    AudioNote $01, $15
    AudioNote $01, $13
    AudioNote $01, $15
    AudioNote $01, $11
    AudioNote $01, $10
    AudioNote $01, $11
    AudioNote $01, $13
    AudioNote $01, $0C
    AudioNote $01, $10
    AudioNote $01, $13
    AudioNote $01, $16
    AudioNote $01, $15
    AudioNote $01, $13
    AudioNote $01, $15
    AudioNote $01, $11
    AudioNote $01, $13
    AudioNote $01, $15
    AudioNote $01, $18
    AudioNote $01, $16
    AudioNote $01, $16
    AudioNote $01, $1A
    AudioNote $01, $18
    AudioNote $01, $18
    AudioNote $01, $1D
    AudioNote $01, $1C
    AudioNote $01, $1D
    AudioNote $01, $18
    AudioNote $01, $15
    AudioNote $01, $11
    AudioNote $01, $13
    AudioNote $01, $15
    AudioNote $01, $0E
    AudioNote $01, $18
    AudioNote $01, $16
    AudioNote $01, $15
    AudioNote $01, $13
    AudioNote $01, $11
    AudioNote $01, $0C
    AudioNote $01, $11
    AudioNote $01, $10
    AudioNote $01, $11
    AudioNote $01, $15
    AudioNote $01, $18
    AudioNote $01, $1D
    AudioNote $01, $18
    AudioNote $01, $15
    AudioNote $01, $11
    AudioNote $01, $15
    AudioNote $01, $18
    AudioRestorePointer
UnversionedAudioA84D:
    AudioSelectChannel $01
    AudioInstrument $0F
    AudioNote $02, $05
    AudioNote $01, $1F
    AudioNote $02, $11
    AudioNote $01, $1F
    AudioNote $02, $02
    AudioNote $01, $1F
    AudioNote $01, $09
    AudioNote $01, $07
    AudioNote $01, $09
    AudioNote $02, $02
    AudioNote $01, $1F
    AudioNote $02, $02
    AudioNote $01, $1F
    AudioNote $01, $07
    AudioNote $01, $09
    AudioNote $01, $0A
    AudioNote $02, $09
    AudioNote $01, $1F
    AudioNote $02, $0A
    AudioNote $01, $1F
    AudioNote $02, $00
    AudioNote $01, $1F
    AudioNote $02, $04
    AudioNote $01, $1F
    AudioNote $02, $00
    AudioNote $01, $1F
    AudioNote $01, $05
    AudioNote $01, $07
    AudioNote $01, $09
    AudioNote $02, $02
    AudioNote $01, $1F
    AudioNote $02, $0A
    AudioNote $01, $1F
    AudioNote $02, $09
    AudioNote $01, $1F
    AudioNote $02, $02
    AudioNote $01, $1F
    AudioNote $02, $00
    AudioNote $01, $1F
    AudioNote $01, $0A
    AudioNote $01, $0C
    AudioNote $01, $0E
    AudioNote $02, $00
    AudioNote $01, $1F
    AudioNote $02, $00
    AudioNote $01, $1F
    AudioNote $03, $05
    AudioNote $02, $1F
    AudioNote $02, $00
    AudioNote $01, $1F
    AudioRestorePointer
UnversionedAudioA882:
    AudioSelectChannel $02
    AudioInstrument $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $1B, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $0F
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $0F
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $7E, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $0F
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $0F
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $1B, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $7E, $02
    AudioDelay $1D
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $07
    AudioWriteFive $60, $00, $7E, $02
    AudioDelay $07
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $07
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $07
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $07
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $07
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $1B, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $0F
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $0F
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $7E, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $0F
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $0F
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $C3, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $1B, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $7E, $02
    AudioDelay $1D
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $1D
    AudioWriteFive $60, $00, $A1, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioDelay $10
UnversionedAudioA9BA:
    AudioWriteFive $60, $00, $FB, $01
    AudioDelay $0F
    AudioLoop $06, (UnversionedAudioA9BA - BankStart)
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $1D
    AudioWriteFive $16, $9F, $0D, $9B
    AudioDelay $0F
    AudioWriteFive $60, $00, $37, $02
    AudioDelay $0F
    AudioWriteFive $60, $00, $37, $02
    AudioDelay $0F
    AudioDelay $10
UnversionedAudioA9E3:
    AudioWriteFive $60, $00, $37, $02
    AudioDelay $0F
    AudioLoop $06, (UnversionedAudioA9E3 - BankStart) ; CONTROL_UNVERSIONED_AUDIO_LOOP
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $1D
    AudioWriteFive $60, $00, $AB, $01
    AudioDelay $0F
    AudioRestorePointer
UnversionedAudioA9FD:
    AudioSelectChannel $00
    AudioInstrument $01
    AudioNote $00, $16
    AudioNote $00, $14
    AudioNote $00, $12
    AudioNote $00, $14
    AudioNote $00, $16
    AudioNote $00, $14
    AudioNote $00, $12
    AudioNote $00, $14
    AudioNote $00, $16
    AudioNote $00, $14
    AudioNote $00, $12
    AudioNote $00, $14
    AudioNote $00, $16
    AudioNote $00, $14
    AudioNote $00, $12
    AudioNote $00, $14
    AudioNote $02, $18
    AudioNote $01, $1F
    AudioNote $01, $16
    AudioNote $02, $15
    AudioNote $02, $18
    AudioStopVoice
UnversionedAudioAA15:
    AudioSelectChannel $01
    AudioInstrument $0F
    AudioNote $00, $06
    AudioNote $00, $08
    AudioNote $00, $0A
    AudioNote $00, $08
    AudioNote $00, $06
    AudioNote $00, $08
    AudioNote $00, $0A
    AudioNote $00, $08
    AudioNote $00, $06
    AudioNote $00, $08
    AudioNote $00, $0A
    AudioNote $00, $08
    AudioNote $00, $06
    AudioNote $00, $08
    AudioNote $00, $0A
    AudioNote $00, $08
    AudioNote $02, $05
    AudioNote $01, $1F
    AudioNote $01, $05
    AudioNote $02, $05
    AudioNote $02, $05
    AudioStopVoice
UnversionedAudioAA2D:
    AudioSelectChannel $00
    AudioInstrument $01
    AudioNote $01, $0C
    AudioNote $01, $0F
    AudioNote $01, $0E
    AudioNote $01, $0C
    AudioNote $01, $13
    AudioNote $00, $11
    AudioNote $00, $10
    AudioNote $01, $11
    AudioNote $00, $10
    AudioNote $00, $0E
    AudioNote $03, $0C
    AudioNote $03, $0E
    AudioRestorePointer
UnversionedAudioAA3C:
    AudioSelectChannel $01
    AudioInstrument $0F
    AudioNote $02, $00
    AudioNote $02, $00
    AudioNote $02, $00
    AudioNote $02, $00
    AudioNote $03, $00
    AudioNote $03, $07
    AudioRestorePointer
.assert * = $AA45, error, "own audio bank end"
.endmacro
