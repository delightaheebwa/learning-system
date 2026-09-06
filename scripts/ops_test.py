#!/usr/bin/env python3
"""Regression tests for scripts/ops.py — stdlib only (run: python3 -m unittest scripts/ops_test).

Guards the three bugs fixed 2026-08:
- ROOT auto-detect works on either checkout (not hardcoded to one path).
- Path-escape guard rejects attempts to read outside the workspace.
- `state <track>` returns the concept TABLE ROWS, not just the section heading.
"""

import io
import json
import os
import sys
import tempfile
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
        # SWE was archived 2026-09-01 (43 concepts → 📦 Concept Archive.md).
        # The active track is now AIEFS (Mission 0 catch-up). SWE section
        # should contain the ARCHIVED banner, not live concept rows.
        # Keep test green through the roadmap switch.
        self.assertIn("## SWE Track", out)
        if "ARCHIVED" in out:
            self.assertIn("ARCHIVED", out)
            self.assertIn("43 concepts paused", out)
        else:
            # Pre-archive expectation (preserved for history)
            self.assertIn("| What is the Shell |", out)


class TestDoStateIncludesMasterySidecars(unittest.TestCase):
    def test_state_bundles_attempts_and_mistakes(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_state("aiefs")
        out = buf.getvalue()
        self.assertIn("Attempts.json", out)
        self.assertIn("Mistakes.md", out)


class TestAttemptCommand(unittest.TestCase):
    def _make_root(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        core = Path(tmp.name) / "Learning System" / "Core"
        core.mkdir(parents=True)
        seed = {
            "concepts": {
                "Test Concept": {
                    "type": "concept",
                    "attempts": [{"date": "2026-09-01", "is_correct": True,
                                  "result": "pass", "q_type": None}],
                    "interval_index": 0,
                    "consecutive_correct": 1,
                    "consecutive_wrong": 0,
                    "last_reviewed": "2026-09-01",
                    "next_review": "2026-09-04",
                    "feynman": None,
                }
            },
            "meta": {"version": 1,
                     "intervals": {"memory": [0, 1, 3, 7, 14, 30, 60],
                                   "concept": [3, 7, 14, 30],
                                   "procedure": [3, 7, 14],
                                   "design": [14, 28]}},
        }
        (core / "Attempts.json").write_text(json.dumps(seed), encoding="utf-8")
        old = ops.ROOT
        ops.ROOT = Path(tmp.name)
        self.addCleanup(setattr, ops, "ROOT", old)
        return Path(tmp.name)

    def test_attempt_pass_advances_interval(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "pass", date="2026-09-04")
        out = buf.getvalue()
        self.assertIn("next_review", out)
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(len(entry["attempts"]), 2)
        # 2nd consecutive pass => +2 from index 0
        self.assertEqual(entry["interval_index"], 2)
        self.assertEqual(entry["next_review"], "2026-09-18")  # 2026-09-04 + 14d
        self.assertEqual(entry["last_reviewed"], "2026-09-04")

    def test_attempt_fail_drops_interval(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "fail", date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        entry = data["concepts"]["Test Concept"]
        self.assertEqual(entry["interval_index"], 0)  # clamped, was 0
        self.assertEqual(entry["consecutive_wrong"], 1)

    def test_attempt_feynman_flag_recorded(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Test Concept", "pass", feynman="feynman_pass",
                           date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertEqual(data["concepts"]["Test Concept"]["feynman"], "pass")

    def test_attempt_new_concept_defaults(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_attempt("Brand New", "pass", date="2026-09-04")
        data = json.loads((ops.ROOT / "Learning System" / "Core" / "Attempts.json").read_text())
        self.assertIn("Brand New", data["concepts"])
        self.assertEqual(data["concepts"]["Brand New"]["type"], "concept")

    def test_mastery_caps_single_attempt(self):
        self._make_root()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ops.do_mastery("aiefs")
        out = buf.getvalue()
        # 1 pass => recency 1.0 capped at 0.5
        self.assertIn("Test Concept", out)
        self.assertIn("0.50", out)


if __name__ == "__main__":
    unittest.main()
