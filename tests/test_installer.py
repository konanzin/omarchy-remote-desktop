from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def test_installer_refuses_background_execution(self):
        result = subprocess.run([sys.executable, str(ROOT / "bin/install-backend")],
                                stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=3)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("terminal", result.stderr)

    def test_recipe_binds_source_and_dependencies(self):
        recipe = (ROOT / "backend/PKGBUILD").read_text()
        self.assertRegex(recipe, r"_commit=[0-9a-f]{40}\n")
        # One pinned checksum per source: the archive plus each local patch.
        sources = re.search(r"source=\(([^)]*)\)", recipe).group(1).split()
        sums = re.search(r"sha256sums=\(([^)]*)\)", recipe).group(1).split()
        self.assertEqual(len(sums), len(sources))
        for value in sums:
            self.assertRegex(value, r"^'[0-9a-f]{64}'$")
        for patch in sorted((ROOT / "backend").glob("*.patch")):
            self.assertIn(f"'{patch.name}'", sources)
        self.assertIn("cargo fetch --locked", recipe)
        self.assertIn("cargo build --frozen --release", recipe)
        self.assertNotIn("SKIP", recipe)
        self.assertNotIn("systemctl", recipe)


if __name__ == "__main__":
    unittest.main()
