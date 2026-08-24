import logging
import sys

from colorama import Fore, Style


class ColorFormatter(logging.Formatter):
    """Formatter de consola con colores ANSI — SOLO si la salida es un TTY.

    Bajo cron la salida es un pipe que acaba en el correo del operador: los
    escapes ANSI llegaban como basura literal ('[32m … [0m') en cada línea.
    La detección se hace una vez en el constructor (isatty del stream real de
    los StreamHandler del proyecto: stderr por defecto).
    """

    def __init__(self, fmt="%(ctx)s%(message)s", *args, stream=None, **kwargs):
        # Por defecto antepone el contexto de cuenta ([ctx]) al mensaje en consola.
        super().__init__(fmt, *args, **kwargs)
        target = stream if stream is not None else sys.stderr
        self._use_color = bool(getattr(target, "isatty", lambda: False)())

    def format(self, record):
        if not hasattr(record, "ctx"):
            record.ctx = ""

        if not self._use_color:
            return super().format(record)

        # Guardar el mensaje original sin modificarlo
        message = record.msg

        # Aplicar colores solo para la consola
        if record.levelno == logging.INFO:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Fore.RED}{Style.BRIGHT}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.DEBUG:
            record.msg = f"{Fore.CYAN}{record.msg}{Style.RESET_ALL}"

        # Formatear el mensaje coloreado
        formatted_message = super().format(record)

        # Restaurar el mensaje original para que el archivo de log no tenga colores
        record.msg = message

        return formatted_message
