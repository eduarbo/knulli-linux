"""Check the resume decision with separate state slots and changed battery progress."""
import os
from pathlib import Path
import runpy
import tempfile
import unittest
import re

module = runpy.run_path(str(Path(__file__).resolve().parents[1] / "resume/emulatorlauncher"))
Resume = module["Resume"]
namespace = Resume.__init__.__globals__


class ResumePolicy(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        namespace["RECORDS"] = self.root / "history"
        self.imported = 0
        namespace["download_time"] = lambda rom, system: self.imported

    def mark(self, name, content, second):
        file = self.root / ("Demo." + name)
        file.write_bytes(content)
        os.utime(file, (second, second))

    def policy(self):
        return Resume(self.root / "Demo.gb", "gb", "gambatte", self.root, self.root,
                      re.compile(r"Demo\.state(\.auto|[0-9]*)"))

    def test_download_then_local_progress(self):
        self.mark("state.auto", b"auto", 90)
        self.mark("state2", b"slot", 100)
        self.mark("srm", b"on console", 104)
        self.assertEqual(self.policy().newest()[1], 2)
        self.policy().finish()
        self.imported = 110
        self.mark("srm", b"from TV", 10)  # copied with an older timestamp
        after_download = self.policy()
        self.assertIsNone(after_download.newest())
        after_download.finish()
        self.assertIsNone(self.policy().newest())
        resumed = self.policy()
        self.mark("state.auto", b"new local", 120)
        resumed.finish()
        self.assertEqual(self.policy().newest()[1], -1)
        self.assertEqual((self.root / "Demo.state2").read_bytes(), b"slot")

    def test_unknown_progress_and_other_games(self):
        self.imported = None
        self.mark("state1", b"local", 20)
        self.mark("srm", b"unknown", 5)
        (self.root / "Demo sequel.state4").write_bytes(b"other")
        self.assertIsNone(self.policy().newest())
        (self.root / "Demo.srm").unlink()
        self.assertEqual(self.policy().newest()[1], 1)

    def test_new_slot_written_after_manual_load(self):
        self.mark("srm", b"same battery", 1)
        self.mark("state", b"first", 10)
        self.mark("state1", b"second", 20)
        self.policy().finish()
        explicit = self.policy()
        self.mark("state2", b"continued from first", 30)
        explicit.finish(0)
        self.assertEqual(self.policy().newest()[1], 2)
        self.imported = 40
        self.mark("srm", b"different battery", 2)
        self.assertIsNone(self.policy().newest())

    def test_fresh_auto_and_specific_slot(self):
        overlay = self.root / "entry.cfg"
        for requested, auto, args in ((-2, "false", []), (-1, "true", []), (2, "false", ["-e", "2"])):
            command = ["retroarch"]
            module["set_ra_entry"](command, overlay, requested)
            self.assertEqual(command[1:], args)
            self.assertIn(f'savestate_auto_load = "{auto}"', overlay.read_text())
            self.assertIn('block_sram_overwrite = "true"', overlay.read_text())

    def test_manual_state_updated_outside_last_launch_without_battery(self):
        self.mark("state.auto", b"automatic", 20)
        self.policy().finish()
        self.mark("state", b"manual", 30)
        self.assertEqual(self.policy().newest()[1], 0)
        self.mark("state.auto", b"automatic again", 40)
        self.assertEqual(self.policy().newest()[1], -1)

    def test_sync_changes_progress_during_session(self):
        self.mark("srm", b"old", 10)
        self.mark("state1", b"old scene", 20)
        active = self.policy()
        self.imported = 30
        self.mark("srm", b"new from TV", 5)
        active.finish()
        self.assertIsNone(self.policy().newest())

    def test_no_state(self):
        self.assertIsNone(self.policy().newest())


if __name__ == "__main__":
    unittest.main()
