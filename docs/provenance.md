# Provenance and deviations

The patches were produced by reading the GrapheneOS trees and re-applying the logic to the pinned
LineageOS 23.2 checkouts. They are not cherry-picks with hidden context: each patch is a complete
diff against the commit below.

## Pinned targets

| Project | Revision | Used by |
|---|---|---|
| `frameworks/base` | `958afcc3d647d57571650cee4172afe0da619171` (`lineage-23.2`, 2026-10-15) | Both patches |

## GrapheneOS references

The local reference tree is `graphene-repos/fwb-full` at `ef402132a` (branch `17`). The relevant
upstream files are:

| lenOS patch | GrapheneOS source |
|---|---|
| `0001-system-app-update-verity.patch` | `services/core/java/com/android/server/pm/PackageVerityExt.java`; hooks in `services/core/java/com/android/server/pm/InstallPackageHelper.java` (`scanPackageForInitLI`, `preparePackageLI`) |
| `0002-screenshot-sound-settings.patch` | `packages/SystemUI/src/com/android/systemui/screenshot/ScreenshotSoundController.kt` and `ScreenshotSoundPolicy.kt` |

## Deliberate deviations

### #20/#21 — system-app update verification

* The GrapheneOS class is ported in full for the normal package path, including static shared
  library handling. The AndroidPackageUtils original-package exception used by GrapheneOS for its
  browser and PDF viewer is **not** ported; lenOS does not ship those packages, and adding an
  allowlist without a concrete renamed system app would weaken the check.
* The boot-time signature check uses the same `INSTALLED_DATA` / `ROLLBACK` capability decision as
  GrapheneOS. LineageOS's additional signing-lineage helpers do not change that decision.
* The debug-only properties (`persist.disable_boot_time_fsverity_check`,
  `persist.disable_same_versionCode_sys_pkg_update_check`,
  `persist.disable_install_time_fsverity_check`) are retained so a debuggable build can recover
  from a bad test APK. They are never read on user builds.
* `PackageVerityExt` is not wired into `AndroidPackageUtils.getRealPackageOrNull`; this only
  matters for renamed system packages, which are not present in this product.

### #25 — screenshot sound

* The GrapheneOS diff is applied to the same two SystemUI classes. The `screenshotRemoveNonforcedSound`
  aconfig flag remains in place (it is a separate GrapheneOS feature that removes the non-forced
  sound on devices where it should not exist); only the `screenshotForceShutterSound` gate around
  registration and playback is removed.
* The forced-shutter path is unchanged: `MediaActionSound.mustPlayShutterSound()` still forces the
  sound when the camera is open, even if sound effects are disabled.
* The GrapheneOS implementation moved `registerAvailabilityCallback` into an application-scoped
  coroutine and made `shouldForceShutterSound()` suspend. That is a required consequence of
  removing the aconfig guard: the callback must exist on every build, not only on builds where the
  flag was compiled in.

## License

New files carry the Apache-2.0 header and credit both GrapheneOS and The lenOS Project. Modified
AOSP files keep their original headers. See `LICENSE`.
