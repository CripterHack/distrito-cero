# Static basic-material program implementation plan

> Execute inline with superpowers:executing-plans and test-driven-development.

**Goal:** reduce sight render cost without omitting scene geometry, captures or checks.
**Architecture:** compile the existing fragment shader twice. A basic-material variant folds only detailed material comparisons (30–49) to false. Select it only for non-skinned, immutable batches proven at upload to contain integer material IDs 0–25. Unclassified, mixed, dynamic and skinned batches keep the original program. Both programs receive current scene, reflection and texture uniforms without GPU readback. Shadow/sky/post programs and geometry remain unchanged.
**Tech stack:** native WebGL2/JavaScript, Node tests and existing Python/Playwright QA.
**Spec:** [SPEC-001](spec.md), REL-01/02/07; supports SPEC-003 issue #6.

## Base, evidence and constraints

Remote base f65a9e6218e2c3b6b3bf3a2d55671c6591512627, tree 99f6edda835f838c921faece5754aecd2c240aaa. #58 instrumentation and push verification are complete. Local snapshot history is synthetic, never a remote parent.

Three synchronized diagnostic frames attributed 5584.2 ms to scene boxes, versus approximately 7725 ms total. This is software-renderer wall time, not physical GPU timing. A controlled static-material shader probe retained warm PNG hashes and simulation data while reducing three-render-and-capture blocks from approximately 8 s to 5.6 s. This is not full-suite acceptance or FPS.

Keep all 112 sight checks, twenty exchanges, 61 states plus before, 820×680 screenshots, every capture and five guards. Keep three producers, 1800 s/producer, 40 minutes/job. No changes to gameplay, saves, rig, geometry, draw order, lighting formulas, rendering resolution or capture options. Unlike instrumentation-only #58, this unit changes renderer source and requires product 0.20.20 plus deterministic generated outputs.

## Review focus

Reject mixed/unknown/malformed material batches and missing metadata from specialization. Never infer eligibility from a mesh name. Preserve transparency order and dynamic/skinned fallback. Upload all program-specific uniforms to the program actually bound, including reflection pass and human texture assignments. Restore the incoming program and propagate identical exceptions. Own the additional program in the existing generation resource ledger. Preserve every shader formula, aperture, lighting and discard rule reachable by IDs 0–25.

## Tasks

- [x] RED: classifier boundaries and immutable upload metadata in both static upload paths.
- [x] RED: real draw traversal with a recording GL boundary validates program selection, uniforms, order, exceptions and fallback.
- [x] RED: constructor resource ownership and explicit uniform targeting.
- [x] Implement the minimum shader specialization, conservative batch classification and program routing. No shader-readback helper in runtime.
- [ ] Directed GREEN, full Node and current Python suites, authoring/build/export/invariance checks.
- [ ] Compare both production paths in one pinned local browser, exercise multiple scenes/materials/reflection, retain raw timings and all images. The existing complete sight producers remain separate gates.
- [ ] Update STATE/HANDOFF/capacity notes, publish exact tree with real remote parent, verify applicable PR CI and artifacts before merge. Verify any merge push separately.

## Alternatives and rollback

Light-distance cutoff and opaque chunk sorting did not establish a gain. Rigid-only vertex specialization produced only a small change. Removing unreachable discard statements alone did not improve throughput. Those experiments are not shipped. The selected change prunes detailed fragment branches, not sample coverage.

Revert the unit and rebuild the prior product identity to restore the single scene program. No save migration. #5/#6/#7 remain open. No branch cleanup retries or deletion, no new permissions, no transport helper in product ancestry, no independent review or artistic acceptance claim.
