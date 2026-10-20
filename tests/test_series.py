"""The experimental series must apply to the pinned tree and stay in sync."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness import (TestPatchSeries, VENDOR, WORKSPACE, patch_created_paths,
                     patch_paths)
from lenos_projects import alias_for


class TestExperimentalSeries(TestPatchSeries):
    def test_reset_driver_includes_rename_destinations(self):
        spec = importlib.util.spec_from_file_location(
            "lenos_patch_tool", VENDOR / "tools/lenos-patch.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        patch = (VENDOR / "patches/packages_apps_Seedvault"
                 / "0001-grapheneos-app-id-prefix.patch")
        created = set(module.created_paths(patch))
        self.assertIn(
            "contactsbackup/default-permissions_app.grapheneos.backup.contacts.xml",
            created)
        self.assertIn(
            "storage/lib/src/main/java/app/grapheneos/backup/storage/restore/FileSplitter.kt",
            created)

    def test_settings_series_applies_in_series_order(self):
        """Each patch may apply alone, but the full Settings series must apply in order."""
        project = "packages/apps/Settings"
        pdir = VENDOR / "patches" / alias_for(project)
        names = [line.strip() for line in (pdir / "series").read_text().splitlines()
                 if line.strip() and not line.strip().startswith("#")]
        created = set()
        for name in names:
            created |= patch_created_paths(pdir / name)

        sandbox = Path(tempfile.mkdtemp(prefix="lenos-series-"))
        self.addCleanup(shutil.rmtree, sandbox, ignore_errors=True)
        copied = set()
        for name in names:
            for rel in patch_paths(pdir / name):
                if rel in copied:
                    continue
                copied.add(rel)
                src = WORKSPACE / project / rel
                if src.is_file():
                    dst = sandbox / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                else:
                    self.assertIn(rel, created,
                                  f"neither pinned nor created by the series: {rel}")

        for name in names:
            patch = pdir / name
            proc = subprocess.run(
                ["git", "apply", "--whitespace=nowarn", str(patch)],
                cwd=sandbox, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0,
                             f"{name} failed after earlier Settings patches:\n{proc.stderr}")


if __name__ == "__main__":
    unittest.main()
