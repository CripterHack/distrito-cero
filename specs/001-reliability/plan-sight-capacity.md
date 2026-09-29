# Sight capacity and transparent producer timing

> Execute with superpowers:executing-plans. Regressions first, own review.

**Goal:** measure the existing sight producer by section and operation so the next capacity correction is based on evidence, without weakening acceptance.
**Architecture:** local diagnostic timers wrap existing calls once and rethrow failures. Python measures host wall duration; browser timing separates render/inspection inside that wall duration. Measurements are not added across clocks and never determine pass/fail. Optimize or redistribute only after a completed measurement identifies a cause.
**Tech Stack:** Python standard library, native JavaScript, existing Playwright producer. No game dependency.
**Spec:** [SPEC-001](spec.md), REL-01/02, supports issue #6 / SPEC-003.

## Constraints and baseline

Remote base 5f222410ec48473c371c3e4a84052667d354cc7e, tree d168a059695c62be7b96da4ab6fcecd1eb2d3bc7. Product 0.20.19, HTML SHA-256 1bb962d383f570ce1468c038feb4c1d8516a1b145f9645c0b3492d00aec4078c. Keep runtime, assets, gameplay and version unchanged. Keep all 112 sight checks, twenty exchanges, 61 states per exchange, 820x680 resolution, every capture, existing order/isolation, five strict guards and -2 mm sampled criterion. Keep three sight runners, 1800 s/producer and 40 minutes/job. No branch deletion or retry of blocked cleanup.

The verified #57 push measured 1766.227 / 1673.322 / 1374.602 seconds for its three producers. Base had only 33.773 seconds remaining. Those totals do not identify the slow operation. Local source snapshot matches all 951 versioned files and the exact tree, but has synthetic history.

## Review focus

Timers must not change return values, argument identity, exception identity, call count or order. Failed calls remain failures. Timing records survive completed-section logging and preserve failed sections; killed producers remain failed without claiming a complete report. Snapshots cannot mutate the recorded data. Browser timings are nested in host wall time, not GPU queries, physical hardware benchmarks or FPS. Removing timing wrappers must recover the original producer's behavior before any optimization.

## Tasks

- [x] Baseline build, targeted Python and full Node on restored exact tree.
- [x] RED tests for transparent call timing, failure propagation, independent sections/snapshots and non-bundling.
- [x] Implement diagnostics in tools/qa and instrument the existing producer. Keep tests in CI's existing Node glob / qa_reporting suite.
- [ ] Verify producer equivalence after removing wrappers and diagnostic statements. Run a full instrumented partition and inspect measured operations before selecting a fix.
- [x] Evaluate a proposed screenshot correction without committing it. Same-frame and fresh-render ABBA probes kept pixel hashes and simulation state but did not establish a controlled speedup. The unimplemented experimental caret regression is retained with diagnostic evidence, not shipped. All original screenshot options remain unchanged.
- [ ] Use the complete phase data to select a separately verified capacity correction. This instrumentation-only unit does not claim to remove the 33.773-second margin risk.
- [ ] Full applicable tests, docs STATE/HANDOFF/QA, PR with exact remote parent. Review real CI and artifacts before merge, then check push separately.

## Scope ruling

The first deliverable is diagnostic instrumentation, not an unmeasured optimization. Local timing ran with brief overlapping probes and tests, using system Chromium 144 because installation of the pinned development browser failed DNS. Local wall duration is not a controlled throughput comparison. CI produces new measurements in its own pinned environment. Do not add browser and host time together, remove capture states, or raise timeouts to obtain a claimed improvement.

## Rollback

Revert this QA-only unit to restore previous producer/diagnostics without changing game or saves. Keep recorded failures and state all uncompleted checks explicitly. #5/#6/#7 remain globally open.
