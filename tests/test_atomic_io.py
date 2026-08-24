"""atomic_write_bytes: publicación atómica + .bak (pase 3)."""

import os
import tempfile
import unittest

from library.atomic_io import atomic_write_bytes


class TestAtomicWrite(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "store.bin")

    def tearDown(self):
        self.dir.cleanup()

    def _read(self, path):
        with open(path, "rb") as f:
            return f.read()

    def test_creates_file(self):
        atomic_write_bytes(self.path, b"v1")
        self.assertEqual(self._read(self.path), b"v1")

    def test_overwrite_and_backup_keeps_previous_version(self):
        atomic_write_bytes(self.path, b"v1")
        atomic_write_bytes(self.path, b"v2", backup=True)
        self.assertEqual(self._read(self.path), b"v2")
        self.assertEqual(self._read(self.path + ".bak"), b"v1")

    def test_no_backup_without_flag(self):
        atomic_write_bytes(self.path, b"v1")
        atomic_write_bytes(self.path, b"v2")
        self.assertFalse(os.path.exists(self.path + ".bak"))

    def test_no_temp_leftovers(self):
        atomic_write_bytes(self.path, b"v1", backup=True)
        atomic_write_bytes(self.path, b"v2", backup=True)
        leftovers = [n for n in os.listdir(self.dir.name) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])

    def test_creates_parent_directory(self):
        nested = os.path.join(self.dir.name, "sub", "dir", "f.bin")
        atomic_write_bytes(nested, b"x")
        self.assertEqual(self._read(nested), b"x")


if __name__ == "__main__":
    unittest.main()
