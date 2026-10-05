# Domain pack: audio plugins

First pack (Decision 85). Seed proposed by horde in brief hypersaw-005 §5;
**every entry is UNVERIFIED** until the pack's own research pass (method step
2) attaches a primary source a reader opened. horde's B446 P0 is that pass.
An audio plugin runs inside the user's DAW with the DAW's privileges, so a
crafted preset or session file that corrupts memory in our loader is a route
into that machine.

| Surface | Vulnerability class | Proposed guard (strongest first) |
|---|---|---|
| Preset, state and session loading (CLAP/VST3 state chunks, preset files, samples) | trusting declared lengths, counts or channel numbers: heap/stack overflow (CWE-122/121), out-of-bounds read (CWE-125) | one bounded-reader type for all parsing; libFuzzer harnesses on every loader under ASan/UBSan; a banned-raw-read check |
| The real-time audio thread | locks, allocation, I/O or syscalls in `process`: stalls, priority inversion, denial of service | allocation and lock counter test over a scripted session; RealtimeSanitizer where available; preallocate at `activate` |
| DSP index and integer math | unclamped host or modulation values reaching table indices (CWE-190/125) | clamp at one boundary choke point; fuzz extreme parameter values, sample rates, block sizes; UBSan |
| File names and paths | names used as paths: traversal (CWE-22) | one path API; ban string-built paths; fuzz the sanitiser |
| Embedded web-view GUIs | preset or user text reaching HTML: script injection; a JS→native bridge reachable from injected script | escape all text; strict Content-Security-Policy; no remote content; validate every bridge argument; fuzz the bridge |
| Host-supplied values | NaN or infinity, out-of-range parameters, odd sample rates and block sizes | sanitise at the boundary; fuzz the host-facing API |
| Plugin-format boundaries | state-chunk size limits (hosts can silently drop large chunks); latency and tail changes; wrapper translation quirks | size caps with tests; latency as a plugin constant; never signal tail or latency changes from audio paths |
| Distribution | unsigned or unnotarized binaries; installer tampering | signing and notarization in the release pipeline; checksums; an SBOM |

Inheritors: horde first; the audio siblings that ship inside it (dynamics,
reverb, saturation, the morphable FX network) share its attack surface.
