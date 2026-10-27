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
fetch byte may belong to a following record or script. Fetches crossing a
physical bank boundary are reported rather than interpreted.

This is a static candidate analysis. In particular, the assumption that a
script remains associated with a descriptor base is not proven for every
caller or slot lifecycle. Conditional paths, indexed-jump bounds and the bank
mapping remain provisional. The tool reports incomplete context traversals,
script traversal limits and overlapping decodes; it does not mark source as
owned. On the pinned v1.5 input it finds 176 contexts, 679 references and 210
distinct candidate addresses, with no unprocessed contexts or per-context
script overlaps. The union of those script entries contains 2,518 candidate
commands and 13 physical bytes with conflicting decodes across contexts. They
fall within the existing `$BD1B` and `$DC35` script regions. The competing
entries depend on possible record accesses at `$DA40` and `$ED71`, respectively;
their assumed descriptor associations and interpretations remain unverified.
The overlaps do not establish which path actually executes.
A separate `make direct-record-flow` walk seeds every named bank-1 script
entry and checks direct `$16` targets against the resulting script graph.
It finds 16 candidate commands with 14 distinct direct targets. The possible
record at `$B077` overlaps two candidate script bytes; neither interpretation
is accepted there.
In the directed 16,000-frame runs, the `$B05D` branch saw slot values `$0001`,
`$0005` and `$000B` for Noah, Moses and David, respectively, so its `$000F`
test did not select `$B080`. At `$B076`, the saved-pointer high byte was never
`$FF`, so those executions did not fall through to `$B077`. This only describes
the tested inputs; other slot states may take either path.
The same graph also finds one overlapping script byte at
`$F156-$F157`, where a candidate fallthrough conflicts with the existing
`$F157` entry. All of these paths remain provisional.
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
This finds 29 physical bytes with possible record/script conflicts: nine at
the existing `$ED71` script and 20 in six other candidate paths. The five
additional bytes at `$D57C-$D580` depend on a possible descriptor `$5D`
association at command `$D828`; that association and access are unverified. Their slot
contexts and interpretations require review.

The maintained source includes 95 additionally reviewed records: 51 full
zero-mode entries and 44 compact negative-mode entries. Each has a candidate
descriptor and command recorded alongside it. The selections were checked
against all candidate script paths and existing physical ownership; ambiguous
forms, conflicting ranges and resource payloads remain local. These findings
and byte matches do not establish gameplay reachability or hardware behavior.
Seventeen later candidate locations represent only the fields consumed by the
reviewed mode and sentinel checks. They have no observed runtime access yet;
their descriptor associations are provisional.

Twenty additional script regions from the merged trace are represented as
named commands. Their physical bytes do not overlap the reported conflicting
decodes, possible record reads or previously owned records. Independent entry
labels are retained after commands that change the script pointer or main
state; the static graph does not prove that execution falls through between
those entries.
