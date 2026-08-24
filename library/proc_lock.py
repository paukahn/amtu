"""Lock exclusivo por módulo contra dobles ejecuciones (pase 3).

El proyecto usa ficheros planos como única base de datos: dos instancias del
mismo módulo a la vez (cron + lanzamiento manual) producían feeds duplicados
en Amazon, dobles entregas a SAP y carreras sobre los temporales de trackings.

Implementación multiplataforma sobre un fichero de lock:
- Linux/producción: fcntl.flock (LOCK_EX | LOCK_NB) — el lock muere con el
  proceso, así que un crash NUNCA deja el lock pegado.
- Windows/desarrollo: msvcrt.locking (LK_NBLCK) con la misma semántica.

El PID se escribe en el fichero solo como diagnóstico para el operador; la
exclusión real la da el lock del SO, no el contenido.
"""

from __future__ import annotations

import os

LOCK_DIR = "locks"


class ModuleLock:
    def __init__(self, name: str, lock_dir: str = LOCK_DIR):
        self._path = os.path.join(lock_dir, f"{name}.lock")
        self._fh = None

    def acquire(self) -> bool:
        """True si obtuvo el lock; False si otra instancia lo mantiene."""
        directory = os.path.dirname(self._path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        fh = open(self._path, "a+", encoding="utf-8")
        try:
            fh.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            return False
        self._fh = fh
        try:
            fh.seek(0)
            fh.truncate()
            fh.write(str(os.getpid()))
            fh.flush()
        except OSError:
            pass  # el PID es solo informativo
        return True

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if os.name == "nt":
                import msvcrt
                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            self._fh.close()
            self._fh = None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *_exc):
        self.release()
