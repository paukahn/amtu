"""ModuleLock: exclusión de dobles ejecuciones (pase 3)."""

import os
import tempfile
import unittest

from library.proc_lock import ModuleLock


class TestModuleLock(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def test_second_acquire_fails_while_held(self):
        a = ModuleLock("orders", lock_dir=self.dir.name)
        b = ModuleLock("orders", lock_dir=self.dir.name)
        self.assertTrue(a.acquire())
        try:
            self.assertFalse(b.acquire())
        finally:
            a.release()

    def test_reacquire_after_release(self):
        a = ModuleLock("orders", lock_dir=self.dir.name)
        self.assertTrue(a.acquire())
        a.release()
        b = ModuleLock("orders", lock_dir=self.dir.name)
        self.assertTrue(b.acquire())
        b.release()

    def test_different_modules_do_not_conflict(self):
        a = ModuleLock("orders", lock_dir=self.dir.name)
        b = ModuleLock("stock", lock_dir=self.dir.name)
        self.assertTrue(a.acquire())
        try:
            self.assertTrue(b.acquire())
            b.release()
        finally:
            a.release()


if __name__ == "__main__":
    unittest.main()
