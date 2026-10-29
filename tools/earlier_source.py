"""Explicit v1.2 differences applied to the shared v1.3 native forms.

These are source transformations. They read no ROM and never patch output.
Geometry, local assets and target acceptance are separate requirements.
"""
from __future__ import annotations

import re

from .source_variants import replace_once


def macro_body(source: str, name: str) -> tuple[int, int]:
    matches = list(re.finditer(r'(?m)^\.macro ' + re.escape(name) + r'(?:[ \t][^\n]*)?\n', source))
    if len(matches) != 1:
        raise ValueError('missing or ambiguous shared native macro: ' + name)
    match = matches[0]
    end = source.find('\n.endmacro', match.end())
    if end < 0:
        raise ValueError('missing native macro end: ' + name)
    return match.end(), end


def bank_inlines(source: str) -> str:
    """Restore inline mapper stores and the older return sequences."""
    # These original call sites occur in the shared bank helpers, wrapper and
    # NMI. The PPU-control tail's new JSR is inserted later and remains a call.
    source, count = re.subn(r'(?m)^(\s*)jsr SwitchBank(?=\s|;|$)',
                             lambda m: m[1] + 'sta BankValues,y', source)
    if count != 8:
        raise ValueError('unexpected earlier mapper call count: ' + str(count))
    source = replace_once(source, '    jmp SwitchBank\nSharedReturn:',
                          '    sta BankValues,y\nSharedReturn:')
    for name, expected, ending in (('BankHelpers', 2, ''), ('BankScriptNativeCall', 1, '\n    rts')):
        start, end = macro_body(source, name)
        body = source[start:end]
        if body.count('    jmp RestoreDefaultBank') != expected:
            raise ValueError('changed earlier default-bank return sites')
        body = body.replace('    jmp RestoreDefaultBank', '    V12RestoreDefaultBankInline' + ending)
        source = source[:start] + body + source[end:]
    start, end = macro_body(source, 'BankTail')
    body = replace_once(source[start:end], '    jsr RestoreDefaultBank',
                        '    V12RestoreDefaultBankInline')
    source = source[:start] + body + source[end:]
    # v1.3's first sixteen entries are not present in v1.2. Keep the original
    # $0C/$0D table and its separate supported SwitchBank entry.
    source = replace_once(source,
        'BankValues:\n    .repeat 8, chrBank\n'
        '        .byte ($08 | (chrBank << 4)), ($09 | (chrBank << 4))\n'
        '    .endrepeat\n    .repeat 8, chrBank\n',
        'BankValues:\n    .repeat 8, chrBank\n')
    return source


def native_forms(source: str) -> str:
    """Restore the reset/NMI, PPU and coordinate forms supported by v1.2."""
    source = replace_once(source, 'InitializeGame:\n    lda #$FF\n    sta $04DD\n', 'InitializeGame:\n')
    source = replace_once(source,
        '    dec $04DD\n    bne ReadController\n    lda $04DE\n    and #$7F\n'
        '    sta $04DE\n    eor #$FF\n    sta $04DF\n', '')
    source = replace_once(source, '    jmp EnablePpuNmi', '    jsr EnablePpuNmi\n    rts')
    source = replace_once(source, '    jmp RestoreDefaultBank', '    V12RestoreDefaultBankByCall')
    source = replace_once(source, '    jmp LoadMapChunkPointer', '    jsr LoadMapChunkPointer\n    rts')
    source = replace_once(source, '    jmp SetPaletteStreamPending',
                          '    ora $0387\n    sta $0387\n    rts')
    source = replace_once(source, '\nStopAudioVoiceReturn:',
                          '\n    V12AudioShadowReturnTail\nStopAudioVoiceReturn:')
    start = source.index('\nSetInitialMapTilePosition:')
    end = source.index('\nReadMapDimensions:', start)
    # Retain the explanatory map-header comment with ReadMapDimensions.
    comment = source.index('\n; The two-byte map header', start)
    source = source[:start] + '\nSetInitialMapTilePosition:\n    V12InitialMapTilePosition\n' + source[comment:]
    for coordinate in ('X', 'Y'):
        name = 'Scroll' + coordinate + 'TileCoordinate'
        source, count = re.subn(r'(?m)^(\s*)jsr ' + name + r'(?=\s|;|$)',
                                 lambda m: m[1] + 'V12ReadScroll' + coordinate + 'TileCoordinate', source)
        if count != 4:
            raise ValueError('unexpected earlier coordinate consumers: ' + name + ' ' + str(count))
    source = replace_once(source,
        'ScrollXTileCoordinate:\n    ldx ScrollCurrentXLow                    ; CONTROL_SCROLL_X_TILE_COORDINATE\n'
        '    ldy ScrollCurrentXHigh\n', '')
    source = replace_once(source,
        'ScrollYTileCoordinate:\n    ldx ScrollCurrentYLow                    ; CONTROL_SCROLL_Y_TILE_COORDINATE\n'
        '    ldy ScrollCurrentYHigh\n    jmp ShiftXYRight3\n', '')
    for direction, following in (('Right', 'ShiftXYLeft3'), ('Left', 'ShiftXYRight1')):
        start = source.index('\nShiftXY' + direction + '3:')
        end = source.index('\n' + following + ':', start)
        body = replace_once(source[start:end], '    jmp ShiftXY' + direction + '1',
                            '    jsr ShiftXY' + direction + '1\n    rts')
        source = source[:start] + body + source[end:]
    start = source.index('\nMainPrepareMap:')
    end = source.index('\n.assert', start)
    body = source[start:end]
    if body.count('jsr ShiftXYRight3') != 2:
        raise ValueError('changed main-state coordinate callers')
    body = body.replace('jsr ShiftXYRight3', 'jsr MainShiftXYRight3')
    source = source[:start] + body + source[end:]
    marker = '.assert (* - BankStart) = $4C8C, error, "bank 0 shift helper end"'
    source = replace_once(source, marker, 'MainShiftXYRight3:\n    V12MainShiftXYRight3\n' + marker)
    source = replace_once(source, '    LegacyModeGateReturnTail\n', '    V12ModeGateReturnTail\n')
    return source


def prepare(source: str, selector: str, definitions: str) -> str:
    """Prepare v1.2 from already-expanded shared legacy source."""
    source = bank_inlines(source)
    source = native_forms(source)
    start = source.index('\nComputeBankSelection:')
    end = source.index('\n.assert', start)
    selector_body = selector[selector.index('ComputeBankSelection:'):]
    if source[start:end].strip() != selector_body.strip():
        raise ValueError('earlier selector differs from its prepared source input')
    return replace_once(source, '.include "nes.inc"', '.include "nes.inc"\n' + definitions)
