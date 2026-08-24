"""Funciones de logging del proyecto (info / error / debug + contexto).

Pase 2: la configuración del logger es PEREZOSA. Antes este módulo leía
common.ini y creaba las carpetas de logs EN EL IMPORT, así que importar
cualquier módulo del proyecto tocaba disco (y podía abortar). Ahora el logger
se construye en el primer log; si la configuración falla, se degrada a un
logger de consola para que el logging nunca tumbe la aplicación.
"""

import contextvars
import logging
import threading

# Contexto de log por tarea async (p.ej. la cuenta). contextvars se copia por
# cada Task de asyncio y se propaga a asyncio.to_thread, así que el tag NO se
# mezcla entre cuentas concurrentes.
_log_context = contextvars.ContextVar("log_context", default="")


def set_log_context(value: str = "") -> None:
    _log_context.set(value or "")


_base_record_factory = logging.getLogRecordFactory()


def _ctx_record_factory(*args, **kwargs):
    record = _base_record_factory(*args, **kwargs)
    ctx = _log_context.get()
    record.ctx = f"[{ctx}] " if ctx else ""
    return record


logging.setLogRecordFactory(_ctx_record_factory)

_init_lock = threading.Lock()
_logger = None
_logger_auth = None
_logger_config = None


def _ensure() -> None:
    global _logger, _logger_auth, _logger_config
    if _logger is not None:
        return
    with _init_lock:
        if _logger is not None:
            return
        try:
            from classes.config import CommonConfig
            from classes.logging import Logger

            mode = CommonConfig("config").get_mode()
            _logger_config = Logger(mode=mode)
            _logger = _logger_config.get_logger()
            _logger_auth = _logger_config.get_auth_logger()
        except Exception as e:  # logging no debe tumbar la app
            fallback = logging.getLogger("fallback")
            if not fallback.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(ctx)s%(message)s'))
                fallback.addHandler(handler)
            fallback.setLevel(logging.INFO)
            fallback.warning(f"No se pudo configurar el logging completo: {e}")
            _logger = fallback
            _logger_auth = fallback
            _logger_config = None


def error(message, value=None, type='error'):
    """
    Imprime mensajes de error o advertencia.

    Args:
        message (str | bytes): Mensaje a registrar.
        value (str | None): None para log general, 'auth' para autenticación, o nombre de tienda.
        type (str): 'error' o 'warning'.
    """
    _ensure()
    if isinstance(message, bytes):
        message = message.decode('utf-8', errors='replace')

    match type:
        case 'error':
            if value is None:
                _logger.error(message)
            elif value == 'auth':
                _logger_auth.error(message)
            elif _logger_config is not None:
                _logger_config.get_store_logger(value, 'error').error(message)
            else:
                _logger.error(message)

        case 'warning':
            if value is None:
                _logger.warning(message)
            elif value == 'auth':
                _logger_auth.warning(message)
            elif _logger_config is not None:
                _logger_config.get_store_logger(value, 'error').warning(message)
            else:
                _logger.warning(message)


def info(message, value=None):
    """
    Imprime mensajes informativos (success).

    Args:
        message (str | bytes): Mensaje a registrar.
        value (str | None): None para log general, 'auth' para autenticación, o nombre de tienda.
    """
    _ensure()
    if isinstance(message, bytes):
        message = message.decode('utf-8', errors='replace')

    if value is None:
        _logger.info(message)
    elif value == 'auth':
        _logger_auth.info(message)
    elif _logger_config is not None:
        _logger_config.get_store_logger(value, 'success').info(message)
    else:
        _logger.info(message)


def debug(message):
    """
    Imprime mensajes de depuración (solo en modo debug).

    Args:
        message (str | bytes): Mensaje a registrar.
    """
    _ensure()
    if isinstance(message, bytes):
        message = message.decode('utf-8', errors='replace')

    _logger.debug(message)
