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
script overlaps.

The maintained source includes 95 additionally reviewed records: 51 full
zero-mode entries and 44 compact negative-mode entries. Each has a candidate
descriptor and command recorded alongside it. The selections were checked
against all candidate script paths and existing physical ownership; ambiguous
forms, conflicting ranges and resource payloads remain local. These findings
and byte matches do not establish gameplay reachability or hardware behavior.
