"""Ancla de rutas del proyecto (pase 3).

Todas las rutas del proyecto (config/, cache/, temp/, orders/, tokens.amztok,
.env.secret, logs/…) se resuelven relativas al directorio de trabajo. Un cron
de Linux (o el Programador de Windows sin «Start in») arranca el proceso desde
otro cwd y el sistema, en vez de fallar, creaba una «copia paralela» vacía de
la configuración y escribía datos en el sitio equivocado.

`ensure_project_cwd()` fija el cwd a la raíz del proyecto (el directorio que
contiene library/) una vez al arrancar cada punto de entrada.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ensure_project_cwd() -> None:
    os.chdir(PROJECT_ROOT)
