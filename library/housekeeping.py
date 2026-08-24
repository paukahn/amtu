"""Retención de datos: limpieza de backups, temporales y logs (pase 3).

orders_backup/ guarda los informes CRUDOS de pedidos de Amazon (XML con
nombre y dirección del comprador). La Amazon Data Protection Policy exige no
retener PII más de 30 días tras la entrega; además el directorio crecía sin
límite (nadie lo leía ni lo limpiaba) igual que temp/ y logs/.

`run_retention()` se llama una vez al comienzo de cada ejecución del runner.
Es best-effort: cualquier fallo se registra y JAMÁS interrumpe el lote.
Los días son configurables en common.ini; un valor <= 0 desactiva esa regla.
"""

from __future__ import annotations

import os
import time

# (ruta, clave en common.ini, días por defecto, borrar directorios enteros)
DEFAULT_RULES = (
    ("orders_backup", "retention_backup_days", 30, True),
    ("temp", "retention_temp_days", 7, False),
    ("logs", "retention_logs_days", 90, False),
)


def _purge_old_entries(root: str, days: int, *, remove_dirs: bool) -> int:
    """Elimina entradas de `root` con mtime anterior a `days` días. Devuelve nº borrados."""
    if days <= 0 or not os.path.isdir(root):
        return 0
    cutoff = time.time() - days * 86400
    removed = 0
    for dirpath, _dirnames, files in os.walk(root):
        for name in files:
            full = os.path.join(dirpath, name)
            try:
                if os.path.getmtime(full) < cutoff:
                    os.remove(full)
                    removed += 1
            except OSError:
                continue
    if remove_dirs:
        # orders_backup/<cuenta>/<region>/<timestamp>/ — retirar los directorios
        # que quedaron vacíos tras borrar sus ficheros antiguos.
        for dirpath, dirnames, _files in os.walk(root, topdown=False):
            for d in dirnames:
                full = os.path.join(dirpath, d)
                try:
                    if not os.listdir(full):
                        os.rmdir(full)
                except OSError:
                    continue
    return removed


def run_retention(common_cfg) -> None:
    """Aplica las reglas de retención. BLOQUEANTE: llamar con asyncio.to_thread."""
    from library.logging_helpers import info, error

    for root, cfg_key, default_days, remove_dirs in DEFAULT_RULES:
        try:
            days = common_cfg.get_retention_days(cfg_key, default_days)
            removed = _purge_old_entries(root, days, remove_dirs=remove_dirs)
            if removed:
                info(f"🧹 Retención: {removed} elementos de más de {days} días eliminados de {root}/")
        except Exception as e:  # la limpieza nunca debe tumbar el lote
            error(f"Retención de {root}/ falló (se continúa): {e}", type="warning")


__all__ = ["run_retention", "DEFAULT_RULES"]
