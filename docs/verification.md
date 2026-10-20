# Verification checklist (after the first build)

Nothing in this repository has been built or booted. Run these checks only in a build window that
follows the binding `BUILD-FLASH-LOCK.md`; flashing needs explicit approval.

## Build-time

1. Apply this repository's patches to a pristine `frameworks/base`.
2. Build the full `asteroids` product with the main lenOS product config.
3. Confirm `PackageVerityExt.java` is compiled into `services.jar`:
   ```bash
   adb shell cmd package path android
   # and inspect the build log for services/core/java/.../PackageVerityExt.java
   ```
4. Confirm no `neverallow` or hidden-API failure was introduced. This patch uses only existing
   `@hide` framework APIs; it must not need a sepolicy change.

## #20/#21 — system-app update verification

These checks are intentionally destructive to a **test** system-app update, not to a production
device. Use a disposable userdata image or a test device.

1. Boot and filter logcat:
   ```bash
   adb logcat -b all -s PackageVerityExt
   ```
   A normal boot with no `/data` system-app updates should be quiet. If a system app has an
   update, expect `Performing verification of system package update <package>`.
2. Install a test update for a debuggable system app signed with the platform key. It should
   install if its `versionCode` is greater and every split has fs-verity.
3. Try the same `versionCode` as the system image package. The install must fail; the log should
   contain `Not allowed to update system package to the same versionCode`.
4. Try an update without fs-verity (remove the `.idsig`, or use an APK that does not get fs-verity
   set up). The install must fail with the fs-verity message. A debug build can bypass with
   `adb shell setprop persist.disable_install_time_fsverity_check true`; a user build must not.
5. Reboot with a lower-version `/data` update already installed. The boot-time scan must reject it
   and the system image version must be active again. Confirm with:
   ```bash
   adb shell dumpsys package <package> | grep -E 'versionCode|codePath'
   ```
6. Reboot with a valid update. It must survive the reboot and remain the active code path.
7. Verify a mismatched signing certificate is rejected with `INSTALL_FAILED_BAD_SIGNATURE`.

## #25 — screenshot sound

1. With **Settings → Sound & vibration → Touch sounds** (the `SOUND_EFFECTS_ENABLED` setting) on,
   take a screenshot: the normal screenshot sound must play.
2. Turn it off, take a screenshot: no sound.
3. On a device/region where `MediaActionSound.mustPlayShutterSound()` is true, open the camera and
   take a screenshot with sound effects off: the forced shutter sound must still play.
4. Repeat with the camera closed: no forced sound.
5. Check that screenshot capture latency and SystemUI crashes are unchanged in logcat.

## Rollback

If the build fails or the device misbehaves, use `lenos-patch.py --reset` on the source tree and
rebuild. Do not attempt to recover a device by weakening verified boot or locking state. Follow
`BUILD-FLASH-LOCK.md`.
