# lenOS OPSEC additions

These are lenOS-original controls, not GrapheneOS ports. GrapheneOS is a security-hardened
Android; its defaults assume an adversary with physical access, but it does not ship a metadata
sanitizer, a one-tap radio kill switch, or a screen-off clipboard wipe. lenOS adds these as
separate, opt-in tools so they can be evaluated without changing the 1.0 series.

The design rule is the same as the rest of lenOS: local-only, fail closed, no new trust anchors,
and no silent weakening of verified boot, encryption, SELinux or emergency calling.

## OPS-1 — metadata-scrubbing share target

**Problem.** Sharing a photo or screenshot can leak GPS coordinates, capture time, device model,
software version, thumbnail images, XMP history and original file names. Android's share sheet
hands the receiving app the original bytes unless the sending app sanitizes first.

**Implementation.** `LenosOpsec` registers a share target for `image/*` and `image/*` with
`ACTION_SEND` / `ACTION_SEND_MULTIPLE`. It decodes the image with `ImageDecoder`, re-encodes the
pixels with `Bitmap.compress` into a new cache file with a random UUID name, and shares only that
file through a non-exported `FileProvider` with a one-shot read grant. Re-encoding drops EXIF,
GPS, XMP, ICC and file-name metadata; the output name is unrelated to the source. A copy can also
be saved to `Pictures/lenOS` through MediaStore.

**Limits.**

* Re-encoding is not a cryptographic sanitizer. The source app, MediaStore thumbnails, caches and
  the original file may still contain the metadata. The user must delete the source separately.
* JPEG/WebP quality is recompressed (quality 95). A 4096 px longest-edge cap prevents pathological
  memory use; larger images are downsampled.
* Animated GIF is rejected. HEIF/AVIF is decoded and written as JPEG. PDF and video metadata are
  not handled by this tool.
* The app has no `INTERNET` permission and no network code. It cannot phone home, and it does not
  use a cloud OCR/classification service.

**Verification.** Share a geotagged JPEG; run `exiftool` on the received file and confirm there is
no GPS/EXIF/XMP, that the file name is randomized, and that the image still opens. Repeat with a
multi-select share and with the “save sanitized copy” path.

## OPS-2 — one-tap Offline tile

**Problem.** A user who needs to cut connectivity quickly has to open Settings and toggle airplane
mode, Wi-Fi and Bluetooth separately. Each extra step is a window in which a radio can remain
associated with a network.

**Implementation.** `OfflineTileService` is a Quick Settings `TileService` in `LenosOpsec`. On tap
it turns off Wi-Fi and Bluetooth first, then calls `ConnectivityManager.setAirplaneMode(true)`.
The tile is active when airplane mode is on; tapping again turns airplane mode off and leaves
Wi-Fi/Bluetooth off for the user to re-enable deliberately. If the platform call is denied it
falls back to the `AIRPLANE_MODE_ON` setting plus the protected broadcast, and never crashes the
tile.

**Limits.**

* Airplane mode is an Android/telephony policy, not a hardware power cut. It cannot prove the
  baseband, Wi-Fi or Bluetooth firmware has stopped transmitting. A faraday bag is the only
  physical guarantee.
* NFC is not toggled. Some devices keep NFC available in airplane mode.
* The tile needs the platform certificate for `NETWORK_SETTINGS`, `WRITE_SECURE_SETTINGS` and
  `BLUETOOTH_PRIVILEGED`. It is built into the experimental product only.
* The tile does not erase Wi-Fi history, saved networks, eSIMs or accounts. Use the duress/auto-BFU
  controls for destruction.

**Verification.** On a test device, enable Wi-Fi and Bluetooth, tap the tile, and confirm all
three are off and the tile shows active. Tap again and confirm only airplane mode is off. Repeat
while the screen is locked and while a call is active; observe telephony behavior rather than
assuming.

## OPS-3 — clear clipboard on screen off

**Problem.** Android keeps the primary clip after the screen turns off. A locked device prevents
apps from reading it while locked, but the content survives until the app reads it or AOSP's
one-hour auto-clear timer fires. A user who copies a password, recovery phrase or address and then
puts the phone down leaves that content resident.

**Implementation.** A new `Settings.Secure.CLIPBOARD_CLEAR_ON_SCREEN_OFF` key (per user, default 0)
is read by `ClipboardService` when the protected `ACTION_SCREEN_OFF` broadcast arrives. For every
user who opted in, the service clears each clipboard for that user through the existing internal
clear path, which revokes URI grants and notifies listeners. The switch lives in
**Settings → Security & privacy → More security & privacy → Clipboard privacy**.

**Limits.**

* This is off by default. It is a deliberate user choice, not a forced data-loss policy.
* It clears the system clipboard, not copies kept by apps (clipboard managers, password managers,
  some keyboards) or autofill/IME histories.
* A lock without screen-off (for example, an app calling `lockNow()` while the display stays on)
  does not trigger the wipe. The feature is bound to screen-off because that is the reliable
  system broadcast.
* The AOSP one-hour auto-clear remains in place. A user setting a shorter timer is not part of this
  batch; the screen-off wipe is the OPSEC control.

**Verification.** Enable the switch; copy text, an image URI and a text URI; turn the screen off
and on; confirm `getPrimaryClip` is empty and URI grants are revoked for a test app. Confirm the
setting is per-user and survives a reboot.

## Future OPSEC backlog (not implemented)

| Idea | Why it is not in this batch |
|---|---|
| Per-app clipboard read toggles via `AppOpsManager.OP_READ_CLIPBOARD` | Needs a Settings app-op surface and a decision on how it composes with the 1.0 Secure Paste global default; best done with a build loop |
| Tor-only / Orbot routing | Requires an external Tor daemon/VpnService and a product decision about supported apps; not a source-only framework patch |
| Screenshot redaction / secure-screen automation | Needs a per-app policy and window-manager coordination; high risk of breaking banking/DRM apps |
| File timestamp and filesystem metadata scrubbing | Needs a privileged file manager and careful handling of media sync; not a share-sheet-sized feature |
| Panic destruction beyond duress/auto-BFU | Already covered by the 1.0 duress credential and auto-BFU timer; a new panic path needs a hardware/UX decision and is dangerous to add without device testing |
| Browser choice and update channel | Product decision; the experimental series deliberately ships no browser |

## Threat model summary

These controls are aimed at:

* a device that is about to be handed to another person or left unattended;
* metadata leakage when sharing media;
* radio persistence after the user believes connectivity is off;
* clipboard remnants after the user copies a secret.

They do **not** defend against a compromised OS, a malicious app with root, a hardware implant, or
an adversary who can image the storage before the wipe. They are not a substitute for verified
boot, full-disk encryption, the duress credential, or the auto-BFU timer.
