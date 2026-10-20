# lenOS experimental implementations

Source-complete implementations for lenOS that **cannot be built or validated in the current
environment**. This is the companion staging repository to
[`ntrop6/lenos-patches`](https://github.com/ntrop6/lenos-patches), the main lenOS 1.0 patch
series for the Nothing Phone (3a)/(3a) Pro (`asteroids`).

The main repository must stay applicable to a pristine LineageOS 23.2 tree and buildable as the
1.0 product. Work that needs a full build, a booted device, a vendor HAL, or a product decision
lives here instead. Nothing in this repository is part of the 1.0 series, is applied by the main
patchkit, or is claimed to boot.

## Why a separate repository

The VM used for lenOS builds is currently unreachable. These changes are therefore **source-only**:

* no `m`/`soong` build has been run;
* no image has been flashed;
* no boot-time, install-time, Settings UI, or performance behavior has been observed.

Keeping them here means a failed experiment cannot make the 1.0 patchkit un-appliable, while the
implementations remain reviewable, testable at the source level, and ready for the first build
window. Every patch is still a strict `git apply` diff against the same pinned trees.

## Current contents

| Feature | Files | State |
|---|---|---|
| **#20** fs-verity enforcement for system-app updates | `frameworks_base/0001-system-app-update-verity.patch` | Implemented; static checks pass; **not built or booted** |
| **#21** reject same/older system-app updates across reboot | same patch (GrapheneOS `PackageVerityExt` pair) | Implemented; static checks pass; **not built or booted** |
| **#25** screenshot sound follows the system sound-effects setting | `frameworks_base/0002-screenshot-sound-settings.patch` | Implemented; static checks pass; **not built or booted** |

`STATUS.md` tracks the remaining untestable workstreams and the exact reason each is not in this
first batch. Do not read the table above as a statement that the rest of the roadmap is done.

## Apply / check

The patches target the pinned workspace used by the main repository
(`/mnt/sda/AI WORKSPACE/lenos-workspace` by default). The workspace must be pristine before
checking; the main patch series must **not** be applied on top.

```bash
WS="/mnt/sda/AI WORKSPACE/lenos-workspace"
PY=/tmp/opencode/lenv/bin/python

# never writes
$PY tools/lenos-patch.py --tree "$WS" --check
$PY tools/lenos-patch.py --tree "$WS" --status

# apply / remove only this repository's patches
$PY tools/lenos-patch.py --tree "$WS" --apply
$PY tools/lenos-patch.py --tree "$WS" --reset
```

`--reset` restores tracked files and deletes files these patches created
(`PackageVerityExt.java`). The main repository's driver does not know about this repository; do not
merge the two series blindly.

## Tests

```bash
cd tests
LENOS_WORKSPACE="/mnt/sda/AI WORKSPACE/lenos-workspace" \
LENOS_PYTHON=/tmp/opencode/lenv/bin/python ./run-tests.sh
```

The suite proves:

* every patch applies cleanly to the pinned tree and is listed in `series`;
* the new Java file parses with tree-sitter;
* the boot scan, install-time checks, fs-verity loop, versionCode comparison, and signing
  capability checks are present and ordered correctly;
* the debug escape hatches are guarded by `Build.IS_DEBUGGABLE`;
* the screenshot-sound patch is limited to the two SystemUI classes and keeps the forced-shutter
  path intact.

These are **not** runtime tests. The real verification list is in `docs/verification.md`.

## Safety

The binding build/flash/lock rules remain
[`BUILD-FLASH-LOCK.md`](https://github.com/ntrop6/lenos-patches/blob/lenos-1.0/LENOS-1.0-BUILD-FLASH-LOCK.md).
No patch here changes verified boot, encryption, SELinux enforcement, emergency calling, or
recovery. Do not flash an experimental build without explicit approval and a recovery plan.

## Provenance

The implementations are ports of GrapheneOS code. The upstream source revisions, files, and the
lenOS deviations are recorded in `docs/provenance.md`. New files carry Apache-2.0 headers crediting
GrapheneOS and The lenOS Project. The repository is licensed under Apache-2.0 (`LICENSE`).
