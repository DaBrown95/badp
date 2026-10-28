# Slot-record access inventory

`make slot-record-flow` starts from the descriptor-derived script and record
candidates. For each possible descriptor base and script entry, it follows the
reviewed rules in the [script-flow inventory](SCRIPT_FLOW.md), then records
candidate `$00`, `$63` and direct `$16` accesses. A zero-mode access can install another
script pointer and schedule another candidate context. If its script-pointer
high byte is `$FF`, a normal return can retain the following command instead;
this is also traced as a candidate, not a guaranteed continuation. For a
direct `$16` pointer, the mode comes from untracked `$57`; zero, one, other
nonnegative and negative modes are explored as possible field-selection
classes. A zero pointer operand instead uses a dynamic slot value. Results and
fetched bytes are written only to ignored local analysis.

The `$00` and `$63` paths add an unsigned offset in nonnegative modes and
subtract it in negative modes; `$16` passes its pointer directly. The loader
fetches ten bytes, but selects fields based on mode and
sentinels. In negative mode it uses the first two bytes as a resource pointer
and byte 2 as flags; it does not install a script pointer. In zero mode it can
install bytes 2–3 as a script pointer, then use byte 4 and bytes 5–8 when the
resource pointer is present. Other modes read different subsets. The tenth
fetch byte may belong to a following record or script. When a ten-byte fetch
passes CPU address `$FFFF`, it wraps to internal RAM at `$0000`, rather than
continuing into another physical PRG bank. Such candidates include a fetch
plan, but RAM-dependent fields are not decoded or credited as source. The
cartridge-window mapping remains an assumption until independently established.
The plan covers effective data addresses; it is not a complete CPU bus-cycle
trace and does not account for possible dummy reads on page crossings.

This is a static candidate analysis. In particular, the assumption that a
script remains associated with a descriptor base is not proven for every
caller or slot lifecycle. Conditional paths, indexed-jump bounds and the bank
mapping remain provisional. The tool reports incomplete context traversals,
script traversal limits and overlapping decodes; it does not mark source as
owned. On the pinned v1.5 input it finds 176 contexts, 691 references and 213
distinct candidate addresses, with no unprocessed contexts. One context,
base `$6D56` and entry `$5D00`, has 11 bytes with competing script decodes.
The union of those script entries contains 2,532 candidate commands and 13
physical bytes with conflicting decodes across contexts. They
fall within the existing `$BD1B` and `$DC35` script regions. The competing
entries depend on possible record accesses at `$DA40` and `$ED71`, respectively;
their assumed descriptor associations and interpretations remain unverified.
The overlaps do not establish which path actually executes.
A separate `make direct-record-flow` walk seeds every named bank-1 script
entry and checks direct `$16` targets against the resulting script graph.
The latest scan starts from 1,872 named candidate script entries and finds 30
possible direct-load commands with 28 distinct direct targets. Its widened
walk contains 10,021 bytes with overlapping script decodes and 81 possible
record/script overlap bytes. The added entries are candidate contexts, so
these counts do not establish execution or mutually incompatible behavior. The
possible record at `$B077` overlaps candidate script commands at `$B077`,
`$B07B` and `$B07E`; those views are represented, while the skipped low
script-pointer byte remains local.
The graph follows three observed `$F434` indices and 29 more candidates under
the `$F432` predecessor condition; other independent-entry indices remain open.
The `$B62C`, `$D48F` and `$E71C` tables likewise retain predecessor-specific
bounds and remain incomplete for independent entry.
In the directed 16,000-frame runs, the `$B05D` branch saw slot values `$0001`,
`$0005` and `$000B` for Noah, Moses and David, respectively, so its `$000F`
test did not select `$B080`. At `$B076`, the saved-pointer high byte was never
`$FF`, so those executions did not fall through to `$B077`. This only describes
the tested inputs; other slot states may take either path.
The same graph also finds one overlapping script byte at
`$F156-$F157`, where a candidate fallthrough conflicts with the existing
`$F157` entry. All of these paths remain provisional.
In the expanded native-event walk, one possible `$F156` record load associated
with base `$EF5A` reads a record at `$EF86`. Its putative script pointer comes
from two operand bytes in the existing `$EF87` script and points to `$C020`.
Following that candidate introduces thousands of additional overlapping
decodes. Neither the fallthrough nor this descriptor association is established
by the retained gameplay traces; the resulting graph does not resolve whether
those bytes have multiple uses.

`make contact-record-flow` separately models the native contact marker. Slot
initialization sets `$0790` bit 0, and a contact marker may queue offset `$09`
only when that bit is clear. The tool starts from descriptor scripts with a
candidate literal `$30` clear of bit 0, then follows the possible mode-zero
record and installed script. It finds 56 candidate records and 56 script seeds,
267 contexts and 7,088 script nodes. Their graph has 2,905 competing script
bytes and 456 record/script overlap bytes. For example, the `$FC81` contact candidate
can fall through to a record read at `$FC72`, overlapping the existing `$FC6A`
script. These are possible interpretations, not evidence that a clear,
contact, or subsequent path actually occurs; other ways to change the flag are
not covered. The [combined PRG inventory](STATUS.md) includes these candidates.

`make native-event-flow` extends that analysis across later scripts installed by
records, repeating native-event discovery to a fixed point. The
position event requests mode-zero offset `$1B` when bit 2 of `$0790` is clear
and the native position checks pass. Fixed controller discovery covers observed
controlled descriptors `$01` and `$09`; the configured action `$36` remains
restricted to descriptor `$01`, where it was observed. In the sampled Moses
and inventory frames descriptor `$09` had event flags and configured action
`$FF`; the current walker finds no literal flag-clear path enabling its fixed
actions. The separate directional `$36` path is gated by bit `$40` and is also
included as a static candidate. Other controlled descriptors, flag writes and
action values remain open. On v1.5 it finds 60 candidate contact, 10 position and three controller
records, 386 contexts and 8,264 script nodes in two rounds. Its graph contains
2,974 overlapping script bytes and 516 record/script overlap bytes. Following
the newly reviewed `$37-$3A` field setters accounts for most of this expansion;
the resulting competing decodes are static candidates, not resolved ownership
or runtime coverage.
The retained-pointer expansion also reaches candidate commands in referenced
map-chunk data. `make map-data` reports 29 candidate command entries overlapping
65 map bytes at bank-1 CPU `$80FF-$8104` and `$8118-$8152`. Noah's directed
trace sampled map reads within the latter range. These observations establish a map use in
the tested path but do not rule out a script use under other conditions; the
candidate command interpretation remains unaccepted.
The candidate map-area script originates from associating `$EDFC` with descriptor
`$1A` or `$1B` (base `$DB4E`): its offset `$1B` would read record `$DB69`,
whose script pointer is `$00FF`. The `$EDFC` entry was not observed in the
recorded exploratory inputs, and that descriptor association is unverified.

In the 12,000-frame Noah interaction run, descriptor index `$0E` (base
`$DA1C`) reached `$EA28` 18 times with slot flag `$D0` equal to `$80`. The
`$60` command there tests bit `$01` and branches to `$EA49` when it is clear,
so those observed iterations did not reach the `$EA3E` record load. The only
observed `$EA3E` entry used descriptor `$19`, base `$DA79`, with flag `$81`;
its offset `$24` selects the already represented `$DA9D` record. This is
context-specific emulator evidence, not proof that `$DA40` is unreachable
under other inputs or slot-state changes. The context trace remains local.
A second 16,000-frame input sequence reached `$EA28` with descriptor `$0E`
and flag `$80` 48 times, and reached `$EA3E` twice with descriptor `$19` and
flag `$81`. Its other `$EA28` observations used descriptor `$18` or `$19`,
both selecting base `$DA79`. These observations reinforce the tested-context
distinction but do not rule out the competing access in other states.

The three bounded v1.5 opening-gameplay runs observed 10,404, 10,822 and
11,102 entries to the bank-0 command fetcher, and 124, 83 and 145 entries to
the bank-0 record loader. None of the selected nine conflicting script
pointers or seven competing record pointers occurred at those entry points.
This does not rule out their use later, through another entry point, or under
different inputs; the emulator evidence is limited to those opening scenarios.
An exploratory extension to 8,000 frames per adventure, holding right and
periodically pressing A, also observed none of these selected pointers. It
does not establish that the paths are unreachable.

The tool also compares candidate command and table bytes against the fields a
record access would actually read, excluding unused bytes in the ten-byte fetch.
This finds 35 physical bytes with possible record/script conflicts: nine at
the existing `$ED71` script, 20 in six other candidate paths, and six at the
existing `$ED45` script. The last six appear when the possible `$DD0A` audio
restart continues at `$DD0B`; candidate descriptor `$56/$57` contexts can then
reach negative-mode record addresses `$ED4A` and `$ED4D`. Those associations
are unverified, and the `$DD0A` entry itself overlaps another command. The five
additional bytes at `$D57C-$D580` depend on a possible descriptor `$5D`
association at command `$D828`; that association and access are unverified. Their slot
contexts and interpretations require review.
The reference-only routes through the third-level entry and the earlier long,
interaction and directed runs observed neither `$ED4A` nor `$ED4D` as record
addresses. The maintained reference/build replay likewise did not observe
`$DD0A`; these negative observations do not exclude other paths.

The maintained source includes 95 additionally reviewed records: 51 full
zero-mode entries and 44 compact negative-mode entries. Each has a candidate
descriptor and command recorded alongside it. The selections were checked
against all candidate script paths and existing physical ownership; ambiguous
forms and conflicting ranges were left local at that checkpoint. Resource
payloads remain local. These findings
and byte matches do not establish gameplay reachability or hardware behavior.
Seventeen later candidate locations represent only the fields consumed by the
reviewed mode and sentinel checks. They have no observed runtime access yet;
their descriptor associations are provisional.

The later contact and contextual review represents 183 more bytes in 41
candidate records. It retains only mode-selected fields, leaving skipped fields
local, and excludes competing record interpretations and candidate script or
asset uses from these extents. These associations are still static candidates;
the separate source-change controls establish matching bytes, not execution.

Forty-two more negative-mode accesses are represented as compact resource
pointer and flag records. The current inventory has no competing record, script
or asset interpretation for their selected extents; the associations and
whether these paths execute remain unverified.

Twenty additional script regions from the merged trace are represented as
named commands. They were non-overlapping under the earlier trace; the expanded
`$18` successor now exposes the possible `$ED4A-$ED4F` record use described
above. This does not establish which interpretation executes. Independent entry
labels are retained after commands that change the script pointer or main
state; the static graph does not prove that execution falls through between
those entries.

Seven candidate script/record overlaps are represented as shared source
extents at `$B077`, `$D57C`, `$EE65`, `$EE7F`, `$EECD`, `$EEE5` and `$EEFD`.
The source asserts that each pair of interpretations has identical byte values,
but does not resolve descriptor associations, access modes or reachability.
The `$D57C` record's later fields overlap the previously represented compact
record at `$D581`; the overlay itself claims only the preceding five bytes.

The context and script graph limits are separate. Each context walk and the
merged walk use the same 65,536-node default; the native-event inventory
rejects incomplete individual and merged graphs. The limit bounds the 16-bit
encoded pointer space, not a claim that all possible game behavior is known.

The candidate `$DA40` zero-mode record has a structured six-byte prefix; its
last three visual fields overlap the existing `$DA46` record. Candidate
contact pointers at `$DA50`, `$E012` and `$E0FE` also decode as BOGUS commands,
and the source asserts both interpretations. The `$DB64` mode-1 flag is
represented separately. These static descriptor associations remain unverified.

The candidate mode-2 records at `$E01A` and `$E023` can also decode as BOGUS
voice-pointer commands. Their source asserts both nine-byte layouts; additional
possible script entry points inside them remain unresolved. The `$E106` record
represents only fields read in mode 2, leaving the two intervening bytes local.
Descriptor associations and execution are unverified.

For the `$F432` -> `$F434` sequence, a controlled handler probe established the
0-31 selector range and the 8-bit indexed-address calculation. This applies
only if the same slot continues without intervening changes; independent entry
can select any of 128 distinct read positions. The table inventory is kept
locally by `make indexed-jump-inventory`, and does not claim reachability of
its candidate entries.

Expanding the conditional `$F434` positions and other reviewed successors
produces 580 possible native-event contexts and 858 possible record/script
overlap bytes in the merged walk.
These downstream contexts can depend on the predecessor condition and do not
prove that the additional table positions, records or scripts execute.
