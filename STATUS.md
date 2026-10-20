# Untestable-work status

This file is the honest boundary between what is implemented here and what is still only a
workstream. "Implemented" means the source patch exists and the static tests in `tests/` pass. It
does **not** mean the code compiles, boots, or behaves correctly on a device.

## Implemented in this repository

| ID | Feature | Patch | Why it cannot be tested yet |
|---|---|---|---|
| #20 | fs-verity enforcement for system-app updates | `frameworks_base/0001` | Needs a full system image and a booted device to exercise `scanPackageForInitLI` and the PackageInstaller path |
| #21 | Reject same/older system-app updates at boot | `frameworks_base/0001` | Same; the failure mode only appears across a reboot with a `/data` update |
| #25 | Screenshot sound follows `SOUND_EFFECTS_ENABLED`; forced shutter regions unchanged | `frameworks_base/0002` | Needs SystemUI build and a device with/without a forced-shutter region |

## Still to implement (in rough order)

These are in the experimental repo's scope, but are not implemented yet. Each entry names the
blocker rather than pretending the work is a small patch.

| ID | Feature | Blocker / prerequisite | Size |
|---|---|---|---|
| #22 | USB-C port control (data off / charging-only / when-locked) | Needs `UsbManager` API, `UsbService` port-security enforcement, keyguard hooks, HAL support and a per-device capability flag; the `asteroids` USB HAL has not been validated | L |
| #23 | Native debugging (ptrace) block with per-app toggles | Depends on the `GosPackageState` / SELinux-flags core; a standalone block would not provide the per-app UI and would diverge from GrapheneOS | L |
| #27 | Seedvault backup update | Needs an app fork/update and a decision on vendoring the GrapheneOS chunker; not a framework patch | M–L |
| #28 | Setup Wizard bootloader/unlocked-device warning | Needs a product spec (when to show, exact wording, links, whether to block); the LineageOS SetupWizard checkout is not in the workspace | M |
| #30 | Storage Scopes / Contact Scopes | XL port of the 64-file `GosPackageState` PackageManager core plus Settings/UI; cannot be done safely without a build loop | XL |
| #31 | Two-factor fingerprint unlock (`LockDomain`) | XL backport (tens of files) with lock-screen and credential logic; needs a build/device loop | XL |
| #33 | Runtime/allocator hardening | bionic/ART changes, not a small patch; needs performance and compatibility validation | XL |
| #34 | SELinux/seccomp tightening | Device-specific sepolicy; must be validated with `neverallow` and a boot loop before shipping | XL |
| #35 | Browser/WebView replacement | Product decision (Vanadium vs Cromite vs Jelly) and an update channel; not a source-only framework patch | decision |

Tier 2 #17 (log viewer/crash reporting) remains deferred pending a usable GrapheneOS UI app;
Tier 2 #26 (call recording), #24 (uncompressed APEX), #29 (always-on VPN), and the rest of the
1.0 series stay in the main patch repository.
