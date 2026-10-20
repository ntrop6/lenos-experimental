"""OPSEC tools that GrapheneOS does not provide (experimental).

Two user-facing tools are added to the existing lenOS companion app tree:

* a share target that re-encodes an image so EXIF/GPS/XMP/file-name metadata
  cannot leak to the receiving app; and
* an "Offline" Quick Settings tile that turns airplane mode and the remaining
  radios off in one action.

Both are local-only. The app has no INTERNET permission and no network code.
"""
from __future__ import annotations

import unittest

from harness import LenosPatchTest, VENDOR, patch_paths

PATCH = "0001-opsec-tools.patch"


class TestOpsecTools(LenosPatchTest):
    PROJECT = "vendor/lenos"
    PATCHES = [PATCH]

    def test_patch_scope(self):
        patch = VENDOR / "patches" / "vendor_lenos" / PATCH
        paths = sorted(patch_paths(patch))
        self.assertIn("config/lenos.mk", paths)
        self.assertIn("app/LenosOpsec/AndroidManifest.xml", paths)
        self.assertIn("app/LenosOpsec/src/org/lenos/opsec/ImageScrubber.java", paths)
        self.assertIn("app/LenosOpsec/src/org/lenos/opsec/OfflineTileService.java", paths)
        self.assertIn("app/LenosOpsec/src/org/lenos/opsec/ScrubActivity.java", paths)

    def test_image_scrubber_reencodes_without_metadata(self):
        self.assert_contains(
            "app/LenosOpsec/src/org/lenos/opsec/ImageScrubber.java",
            "ImageDecoder.decodeBitmap",
            "bitmap.compress",
            "UUID.randomUUID()",
            "MAX_DIMENSION",
            "image/png",
            "image/webp",
            "image/jpeg",
        )
        # Re-encoding is the metadata removal mechanism; no EXIF copy path.
        self.assert_not_contains(
            "app/LenosOpsec/src/org/lenos/opsec/ImageScrubber.java",
            "ExifInterface",
            "setAttribute",
            "TAG_GPS",
        )

    def test_share_target_and_save_path(self):
        self.assert_contains(
            "app/LenosOpsec/src/org/lenos/opsec/ScrubActivity.java",
            "Intent.ACTION_SEND",
            "Intent.ACTION_SEND_MULTIPLE",
            "FileProvider.getUriForFile",
            "FLAG_GRANT_READ_URI_PERMISSION",
            "MediaStore.Images.Media",
            "RELATIVE_PATH",
            "IS_PENDING",
            "ClipData",
        )
        self.assert_contains(
            "app/LenosOpsec/AndroidManifest.xml",
            'android:name=".ScrubActivity"',
            'android:name="android.intent.action.SEND"',
            'android:name="android.intent.action.SEND_MULTIPLE"',
            'android:mimeType="image/*"',
            'androidx.core.content.FileProvider',
        )

    def test_app_has_no_network_permission_or_code(self):
        manifest = self.text("app/LenosOpsec/AndroidManifest.xml")
        self.assertNotIn("android.permission.INTERNET", manifest)
        for rel in (
                "app/LenosOpsec/src/org/lenos/opsec/ImageScrubber.java",
                "app/LenosOpsec/src/org/lenos/opsec/ScrubActivity.java",
                "app/LenosOpsec/src/org/lenos/opsec/OfflineTileService.java"):
            body = self.text(rel)
            self.assertNotIn("java.net.", body, rel)
            self.assertNotIn("HttpURLConnection", body, rel)
            self.assertNotIn("Socket", body, rel)

    def test_offline_tile_is_a_radio_kill_switch(self):
        self.assert_contains(
            "app/LenosOpsec/src/org/lenos/opsec/OfflineTileService.java",
            "TileService",
            "setAirplaneMode",
            "AIRPLANE_MODE_ON",
            "setWifiEnabled(false)",
            "bluetooth.disable()",
        )
        self.assert_contains(
            "app/LenosOpsec/AndroidManifest.xml",
            "android.permission.NETWORK_SETTINGS",
            "android.permission.WRITE_SECURE_SETTINGS",
            "android.permission.BLUETOOTH_PRIVILEGED",
        )

    def test_product_integration(self):
        self.assert_contains("config/lenos.mk", "LenosOpsec")
        self.assert_contains(
            "app/LenosOpsec/Android.bp",
            'name: "LenosOpsec"',
            "platform_apis: true",
            'certificate: "platform"',
        )

    def test_resources_and_java_parse(self):
        for rel in (
                "app/LenosOpsec/AndroidManifest.xml",
                "app/LenosOpsec/res/layout/activity_scrub.xml",
                "app/LenosOpsec/res/values/strings.xml",
                "app/LenosOpsec/res/xml/file_paths.xml",
                "app/LenosOpsec/res/drawable/ic_offline.xml"):
            self.assert_xml(rel)
        for rel in (
                "app/LenosOpsec/src/org/lenos/opsec/ImageScrubber.java",
                "app/LenosOpsec/src/org/lenos/opsec/ScrubActivity.java",
                "app/LenosOpsec/src/org/lenos/opsec/OfflineTileService.java"):
            self.assert_java_syntax(rel)


if __name__ == "__main__":
    unittest.main()
