"""Screenshot sound follows the system sound-effects setting (Tier 2 #25).

GrapheneOS removes the `screenshotForceShutterSound` aconfig gate around the
non-forced screenshot sound and gates it on `Settings.System.SOUND_EFFECTS_ENABLED`
instead. Forced shutter regions are unchanged: `MediaActionSound.mustPlayShutterSound()`
still wins when the camera is open.
"""
from __future__ import annotations

import unittest

from harness import VENDOR, LenosPatchTest, patch_paths

PATCH = "0002-screenshot-sound-settings.patch"
ALIAS = "frameworks_base"
CONTROLLER = ("packages/SystemUI/src/com/android/systemui/screenshot/"
              "ScreenshotSoundController.kt")
POLICY = ("packages/SystemUI/src/com/android/systemui/screenshot/"
          "ScreenshotSoundPolicy.kt")


class TestScreenshotSound(LenosPatchTest):
    PROJECT = "frameworks/base"
    PATCHES = [PATCH]

    def test_patch_is_limited_to_the_screenshot_sound_classes(self):
        patch = VENDOR / "patches" / ALIAS / PATCH
        self.assertEqual(sorted(patch_paths(patch)), sorted([CONTROLLER, POLICY]))

    def test_controller_honours_sound_effects_before_playing(self):
        body = self.text(CONTROLLER)
        check = body.index("Settings.System.SOUND_EFFECTS_ENABLED")
        play = body.index("withContext(bgDispatcher)")
        self.assertLess(check, play)
        self.assertIn("systemSettings.getInt(", body)
        self.assertIn("return", body[check:play])

    def test_policy_no_longer_uses_the_aconfig_gate(self):
        self.assert_not_contains(POLICY, "screenshotForceShutterSound")
        self.assert_not_contains(POLICY, "Flags.screenshotForceShutterSound")

    def test_forced_shutter_region_is_unchanged(self):
        self.assert_contains(
            POLICY,
            "suspend fun shouldForceShutterSound(): Boolean",
            "shutterPolicy.mustPlayShutterSound() && cameraOpen",
            "MediaActionSound.mustPlayShutterSound()",
        )

    def test_camera_availability_callback_is_registered_unconditionally(self):
        body = self.text(POLICY)
        self.assertIn("applicationScope.launch(bgDispatcher)", body)
        self.assertIn("registerAvailabilityCallback", body)
        # The old aconfig guard around registration is gone.
        self.assertNotIn("if (screenshotForceShutterSound())", body)

    def test_constructor_and_types_are_consistent(self):
        self.assert_contains(
            POLICY,
            "@Background private val bgDispatcher: CoroutineDispatcher",
            "@Application private val applicationScope: CoroutineScope",
            "suspend fun mustPlayShutterSound(): Boolean",
            "withContext(bgDispatcher) { MediaActionSound.mustPlayShutterSound() }",
        )
        self.assert_contains(
            CONTROLLER,
            "private val systemSettings: com.android.systemui.shared.settings.data.repository.SystemSettingsRepository",
        )
        self.assert_balanced(POLICY)
        self.assert_balanced(CONTROLLER)


if __name__ == "__main__":
    unittest.main()
