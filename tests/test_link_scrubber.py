"""OPS-5: strip known tracking parameters from shared text.

This is a local text transformation. The app never opens the links, resolves
them, or uploads the text; only the sanitized string is handed to the target
app or the clipboard.
"""
from __future__ import annotations

import unittest

from harness import LenosPatchTest, VENDOR, patch_paths

PATCH = "0001-opsec-tools.patch"


class TestLinkScrubber(LenosPatchTest):
    PROJECT = "vendor/lenos"
    PATCHES = [PATCH]

    def test_patch_adds_the_text_share_target(self):
        patch = VENDOR / "patches" / "vendor_lenos" / PATCH
        paths = sorted(patch_paths(patch))
        self.assertIn("app/LenosOpsec/src/org/lenos/opsec/LinkScrubber.java", paths)
        self.assertIn("app/LenosOpsec/src/org/lenos/opsec/ScrubTextActivity.java", paths)
        self.assertIn("app/LenosOpsec/res/layout/activity_scrub_text.xml", paths)

    def test_scrubber_is_conservative_and_offline(self):
        self.assert_contains(
            "app/LenosOpsec/src/org/lenos/opsec/LinkScrubber.java",
            "URL_PATTERN",
            "utm_",
            "fbclid",
            "gclid",
            "msclkid",
            "srsltid",
            "split(\"&\", -1)",
            "java.util.Locale.ROOT",
        )
        self.assert_not_contains(
            "app/LenosOpsec/src/org/lenos/opsec/LinkScrubber.java",
            "HttpURLConnection",
            "openConnection",
            "Socket",
            "URLConnection",
            "java.net.",
        )

    def test_activity_only_shares_text(self):
        self.assert_contains(
            "app/LenosOpsec/src/org/lenos/opsec/ScrubTextActivity.java",
            "Intent.ACTION_SEND",
            'setType("text/plain")',
            "Intent.EXTRA_TEXT",
            "ClipboardManager",
            "setPrimaryClip",
            "ClipData.newPlainText",
        )
        self.assert_not_contains(
            "app/LenosOpsec/src/org/lenos/opsec/ScrubTextActivity.java",
            "INTERNET",
            "HttpURLConnection",
            "openConnection",
        )

    def test_manifest_filters_text_only(self):
        self.assert_contains(
            "app/LenosOpsec/AndroidManifest.xml",
            'android:name=".ScrubTextActivity"',
            'android:mimeType="text/plain"',
        )
        self.assert_contains(
            "app/LenosOpsec/res/values/strings.xml",
            "scrub_text_title",
            "scrub_text_explanation",
            "scrub_text_removed",
            "scrub_text_copied",
        )

    def test_resources_and_java_parse(self):
        for rel in (
                "app/LenosOpsec/res/layout/activity_scrub_text.xml",
                "app/LenosOpsec/res/values/strings.xml",
                "app/LenosOpsec/AndroidManifest.xml"):
            self.assert_xml(rel)
        for rel in (
                "app/LenosOpsec/src/org/lenos/opsec/LinkScrubber.java",
                "app/LenosOpsec/src/org/lenos/opsec/ScrubTextActivity.java"):
            self.assert_java_syntax(rel)


if __name__ == "__main__":
    unittest.main()
