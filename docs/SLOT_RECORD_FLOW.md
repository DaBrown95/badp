# Slot-record access inventory

`make slot-record-flow` starts from the descriptor-derived script and record
candidates. For each possible descriptor base and script entry, it follows the
reviewed rules in the [script-flow inventory](SCRIPT_FLOW.md), then records
candidate `$00` and `$63` accesses. A zero-mode access can install another
script pointer and schedule another candidate context. Results and fetched bytes
are written only to ignored local analysis.

The loader adds an unsigned offset in nonnegative modes and subtracts it in
negative modes. It fetches ten bytes, but selects fields based on mode and
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
owned. On the pinned v1.5 input it finds 141 contexts, 458 references and 186
distinct candidate addresses, with no unprocessed contexts or per-context
script overlaps. The union of those script entries contains 2,209 candidate
commands and 13 physical bytes with conflicting decodes across contexts. They
fall within the existing `$BD1B` and `$DC35` script regions. The competing
entries depend on possible record accesses at `$DA40` and `$ED71`, respectively;
their assumed descriptor associations and interpretations remain unverified.
The overlaps do not establish which path actually executes.

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
This finds 24 physical bytes with possible record/script conflicts: nine at
the existing `$ED71` script and 15 in five other candidate paths. Their slot
contexts and interpretations require review.

The maintained source includes 95 additionally reviewed records: 51 full
zero-mode entries and 44 compact negative-mode entries. Each has a candidate
descriptor and command recorded alongside it. The selections were checked
against all candidate script paths and existing physical ownership; ambiguous
forms, conflicting ranges and resource payloads remain local. These findings
and byte matches do not establish gameplay reachability or hardware behavior.

Twenty additional script regions from the merged trace are represented as
named commands. Their physical bytes do not overlap the reported conflicting
decodes, possible record reads or previously owned records. Independent entry
labels are retained after commands that change the script pointer or main
state; the static graph does not prove that execution falls through between
those entries.
