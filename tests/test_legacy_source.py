"""Typed source operands and physical layouts use synthetic values only."""
import unittest

from tools.legacy_source import compact_constant_maps, typed_fields
from tools.source_variants import Layout


class LegacySourceTests(unittest.TestCase):
    def layout(self):
        return Layout(((0, 0x9000, 0xa000, 16), (1, 0x9000, 0xa000, -8),
                       (1, 0xc000, 0xd000, -8)))

    def test_branch_resource_native_ram_and_numeric_namespaces_stay_distinct(self):
        source = '''.include "nes.inc"
.macro BogusJumpBank1 target
    .byte $04
    .word target - $8000
.endmacro
.scope Bank1
BogusJumpBank1 $9000
BogusStartVoice4 $9000
BogusStartVoice4 $1000
BogusStartVoice4 $FFFF
BogusCallNativeEncoded $0FFF
BogusCallNativeEncoded $7FFF
BogusCallNativeEncoded $FFFF
BogusStoreSlotLowAt $9000
BogusSetSlotValue $9000
SlotScriptOnlyRecord $FF, ($1000), $00, $00, $00, $00, $00
AudioScriptWord BogusRestartVoice4, $49, $1000, $00, $00
'''
        rendered = compact_constant_maps(typed_fields(source, self.layout()), self.layout())
        self.assertIn('BogusJumpBank1 (($9000 + (-8)))', rendered)
        self.assertIn('BogusStartVoice4 (($9000 + (16)))', rendered)
        self.assertIn('BogusStartVoice4 (($1000 + (-8)))', rendered)
        self.assertIn('BogusCallNativeEncoded (($0FFF + (-8)))', rendered)
        for unchanged in ('BogusStartVoice4 $FFFF', 'BogusCallNativeEncoded $7FFF',
                          'BogusCallNativeEncoded $FFFF', 'BogusStoreSlotLowAt $9000',
                          'BogusSetSlotValue $9000', 'AudioScriptWord BogusRestartVoice4, $49, $1000'):
            self.assertIn(unchanged, rendered)
        self.assertIn('SlotScriptOnlyRecord $FF, (($1000 + (-8)))', rendered)

    def test_text_inventory_and_pointer_remap_tables_keep_their_declared_roles(self):
        source = '''.include "nes.inc"
.scope Bank1
DataBE82:
 .word $C010, $C020
.assert 1, error, "table end"
DataD05F:
 .word $1000
.assert 1, error, "table end"
NumericTable:
 .word $C010, $1000
BogusRemapCase $8000, $9000
ScriptD00D:
BogusRemapCase $8000, $9000
BogusRemapEnd
BogusRemapCase $8000, $9000
'''
        rendered = compact_constant_maps(typed_fields(source, self.layout()), self.layout())
        self.assertIn('.word (($C010 + (-8))), (($C020 + (-8)))', rendered)
        self.assertIn('.word (($1000 + (-8)))', rendered)
        self.assertIn('.word $C010, $1000', rendered)
        self.assertEqual(rendered.count('BogusRemapCase $8000, $9000'), 2)
        self.assertIn('BogusRemapCase $8000, (($9000 + (16)))', rendered)

    def test_literal_bank_offsets_require_their_actual_physical_bank(self):
        source = '''.scope Bank0
First = BankStart + (TargetOffset {$1000})
.endscope
.scope Bank1
Second = BankStart + (TargetOffset {$1000})
'''
        rendered = compact_constant_maps(source, self.layout())
        self.assertIn('First = BankStart + (($1000 + (16)))', rendered)
        self.assertIn('Second = BankStart + (($1000 + (-8)))', rendered)
        with self.assertRaises(ValueError):compact_constant_maps('Alias = TargetOffset {$1000}', self.layout())
