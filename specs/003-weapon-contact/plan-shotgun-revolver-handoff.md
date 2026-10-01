# Shotgun / revolver handoff implementation plan

> Execute inline with superpowers:executing-plans and test-driven-development.

**Goal:** preserve the visible body, hands and returning piece when switching shotgun/revolver, freely or from reload.
**Architecture:** extend only the measured route in captureSwitch. Reuse canonical finger fitting, captured visible mount, 0.90 s presentation and existing frontal clearance. Do not create another solver, tracker, clock or concurrent model.
**Tech stack:** native JavaScript/WebGL2, Node regression tests, Python/Playwright QA.
**Spec:** [SPEC-003](spec.md), CONTACT-04/05, issue #6.

## Global constraints

Base master 39b7647f1c763ab9e35e8c507723fc4cf5cfc57f, product 0.20.21, tree 1820cda051434f5596c20c2b3c5fa9de2afc7661. PR #60 and its post-merge checks are complete. This continuation recovered actual Git history from the verified branch-audit bundle, not synthetic parents.

Native standalone runtime, unchanged ammunition, saves, availability, geometry, 49-bone rig, segment lengths and foot memory. Real fire/reload/select take precedence. Preserve every existing test, 130 sight checks, 24 exchanges, 61 sampled states, 820x680 screenshots and five canonical guards per partition. Keep three producers, 1800 s per producer and 40 minutes per job. Do not weaken the existing 30 mm prepared-step and 2 mm sampled-penetration criteria.

## Review focus

Frozen selector must capture the displayed pose after inputs are cleared. Reversal must retain the returning piece before and after its single replacement. Third displayed models stay excluded. Cold and warm canonical finger caches give identical results. Restore/fire/reload preserve their immediate logical ownership.

## Task 1: regress and fix the omitted route

Files: src/weapon-handling.js, tests/cross-family-handoff.test.cjs, tests/sidearm-handoff.test.cjs.
Consumes: WeaponHandling.captureSwitch(sim,next,actorOverride,shown), present and existing equipment UI selection. No new public interface.

- [x] Add both directions to the existing four-configuration/eight-phase sweep and shared frozen/reversal/actions/motion/stock tests.
- [x] Add cold/warm cache, all frozen reload phases, retargeted piece and third-model regressions using the existing helpers.
- [x] Run the regression against untouched 0.20.21 and preserve expected failures.
- [x] Extend the explicit capture route, duration and clearance with third-model rejection.
- [x] Run directed and complete Node tests, preserving old exclusions for unmeasured equipment.

## Task 2: renderer evidence and integration

Files: tools/qa/sight_contract.py, tests/qa_selection.test.py, version/build, current documentation.

- [x] Add a failing contract for four appended real-key scenarios, retaining prior partition order.
- [x] Distribute the four scenarios to cross-family/revolver-reload, leaving base unchanged because its prior PR took 1554.493 s. Inspect actual cost before further expansion.
- [x] Run current Python contracts, authoring/build/export invariance and documentation links.
- [ ] Review full production-renderer sequences and preserve all previous data/guard checks. Numeric continuity alone is not artistic acceptance.
- [ ] Publish a bounded PR with exact parent/tree, review applicable CI and images before merge, then verify actual push and Pages separately.

## Other issues and recovery

#5 needs a separate UV/source/art/hardware work unit; #7 depends on the artistic/contact gates and real playtests. Do not close global issues from this pair alone. User renewed permission to retire obsolete branches: the old no-retry note is superseded, not a permanent repository policy. Existing 16 obsolete refs were audited and retired with verified full-history backups, master unchanged. Record the cleanup in current documentation.

Revert this unit together with its version/build. Do not delete or migrate saves. Preserve historical evidence, source assets and validation reports.

## Local evidence before remote publication

Baseline full658/658. Directed RED4 failures +1 safeguard pass, GREEN5/5. Full
candidate667/667 Node, exit0, no skips/cancelled/TODO, TAP229420.210672ms.
Current Python148/148 in15 suites, authoring/build/export and96 document links
checked. Two stale synthetic fixture counts were detected in the first Python
run and updated explicitly to44/48, never by relaxing guards. The first full-file
RED attempt was interrupted; it is not a complete test result.

Twelve directed routes,384 selections,912 sampled stock poses, minimum across
the admitted cohort -0.352865mm. New-pair maximum prepared palm steps25.995/17.974mm
in the Node fixture. Browser/CI remains a separate gate; do not equate these
values with FPS, CCD, hardware or mechanical handling certification.
