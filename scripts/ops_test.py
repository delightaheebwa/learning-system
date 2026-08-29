#!/usr/bin/env python3
"""Regression tests for scripts/ops.py — stdlib only (run: python3 -m unittest scripts/ops_test).

Guards the three bugs fixed 2026-08:
- ROOT auto-detect works on either checkout (not hardcoded to one path).
- Path-escape guard rejects attempts to read outside the workspace.
- `state <track>` returns the concept TABLE ROWS, not just the section heading.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# Allow running as a standalone module or via `python3 -m unittest scripts.ops_test`
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops  # noqa: E402


class TestRootDetection(unittest.TestCase):
    def test_root_resolves_to_a_checkout_with_core(self):
        # The directory containing this test must have "Learning System/Core".
        self.assertTrue((ops.ROOT / "Learning System" / "Core").is_dir())

    def test_env_override_is_honored(self):
        # LEARNING_SYSTEM_ROOT pointing at a dir without the Core substructure
        # must NOT be selected (falls through to a real checkout).
        os.environ["LEARNING_SYSTEM_ROOT"] = "/tmp/definitely-not-a-checkout"
        try:
            root = ops._detect_root()
        finally:
            del os.environ["LEARNING_SYSTEM_ROOT"]
        self.assertTrue((root / "Learning System" / "Core").is_dir())


class TestPathEscape(unittest.TestCase):
    def test_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            ops._resolve("../etc/passwd")
        with self.assertRaises(ValueError):
            ops._resolve("/etc/passwd")

    def test_internal_path_is_allowed(self):
        p = ops._resolve("Learning System/Core/💡 Learning Profile.md")
        self.assertTrue(str(p).startswith(str(ops.ROOT)))


class TestSectionSlice(unittest.TestCase):
    def test_section_captures_table_rows_not_just_heading(self):
        lines = [
            "# KNOWLEDGE BASE",
            "## SWE Track — Shell & Terminal",
            "| Concept | Type |",
            "| --- | --- |",
            "| What is the Shell | concept |",
            "## aie Track — archived",
            "| old concept | concept |",
        ]
        text, err = ops._section_slice(lines, r"^## swe\b")
        self.assertIsNone(err)
        self.assertIn("What is the Shell", text)
        self.assertNotIn("old concept", text)  # next section excluded
        self.assertIn("## SWE Track", text)

    def test_section_missing_returns_error(self):
        lines = ["# title", "## Other"]
        text, err = ops._section_slice(lines, r"^## nope\b")
        self.assertIsNone(text)
        self.assertIn("no matching section", err)


class TestDoStateActiveConcepts(unittest.TestCase):
    def test_state_swe_returns_concept_rows(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_state("swe")
        out = buf.getvalue()
        # Active Concepts section must include actual concept table rows.
        self.assertIn("| What is the Shell |", out)
        self.assertIn("## SWE Track", out)


if __name__ == "__main__":
    unittest.main()
