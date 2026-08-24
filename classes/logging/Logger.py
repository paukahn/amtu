import logging, os
from datetime import datetime
from pathlib import Path
from classes.logging.ColorFormatter import ColorFormatter

class Logger:
    def __init__(self, mode):
        self.logger = logging.getLogger(__name__)
        self.mode = mode.lower()
        self.set_log_level()
        self.configure_logger()

    def set_log_level(self):
        if self.mode == 'production':
            self.logger.setLevel(logging.INFO)
        elif self.mode == 'debug':
            self.logger.setLevel(logging.DEBUG)

    # (pase 3) El antiguo remove_debug hacía rmtree de logs/<año>/<mes>/debug
    # al arrancar en production: cambiar debug→production destruía la
    # diagnóstica ya recogida del mes. Ahora simplemente no se crea la carpeta.

    def configure_logger(self) -> None:
        """Configurar el logger con separación entre operaciones exitosas, errores y depuración."""
        LOGS_FOLDER = "logs"
        current_year = datetime.now().strftime('%Y')
        current_month = datetime.now().strftime('%m')
        current_day = datetime.now().strftime('%d')
        YEAR_FOLDER = os.path.join(LOGS_FOLDER, current_year)
        MONTH_FOLDER = os.path.join(YEAR_FOLDER, current_month)
        SUCCESS_FOLDER = os.path.join(MONTH_FOLDER, "success")
        ERROR_FOLDER = os.path.join(MONTH_FOLDER, "error")
        DEBUG_FOLDER = os.path.join(MONTH_FOLDER, "debug")

        # Crear las carpetas si no existen
        os.makedirs(SUCCESS_FOLDER, exist_ok=True)
        os.makedirs(ERROR_FOLDER, exist_ok=True)
        if self.mode == "debug":
            os.makedirs(DEBUG_FOLDER, exist_ok=True)

        # Definir los archivos de log
        success_log_file = os.path.join(SUCCESS_FOLDER, f"success_{current_year}_{current_month}_{current_day}.log")
        error_log_file = os.path.join(ERROR_FOLDER, f"error_{current_year}_{current_month}_{current_day}.log")
        debug_log_file = os.path.join(DEBUG_FOLDER, f"debug_{current_year}_{current_month}_{current_day}.log")

        # Configurar los manejadores. Cerrar los anteriores ANTES de limpiar
        # evita fugar descriptores de fichero (ResourceWarning) al reconfigurar.
        for handler in self.logger.handlers[:]:
            handler.close()
        self.logger.handlers.clear()

        # Configurar el manejador para la consola
        console_handler = logging.StreamHandler()
        console_formatter = ColorFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Configurar el manejador para operaciones exitosas
        success_handler = logging.FileHandler(success_log_file, encoding="utf-8")
        success_handler.setLevel(logging.INFO)
        success_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(ctx)s%(message)s'))
        success_handler.addFilter(lambda record: record.levelno < logging.WARNING)  # Filtrar INFO y DEBUG
        self.logger.addHandler(success_handler)

        # Configurar el manejador para errores
        error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
        error_handler.setLevel(logging.WARNING)  # Solo capturar WARNING y niveles superiores
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(ctx)s%(message)s'))
        self.logger.addHandler(error_handler)

        # Configurar el manejador para depuración si el modo es debug
        if self.mode == 'debug':
            debug_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(ctx)s%(message)s'))
            self.logger.addHandler(debug_handler)

    def get_logger(self) -> logging.Logger:
        """Devuelve el logger configurado."""
        return self.logger

    def get_store_logger(self, store_name: str, level: str = "success") -> logging.Logger:
        """
        Obtiene un logger específico para una tienda y nivel (success/error).
        store_name: nombre de la tienda (por ejemplo, "tienda_X")
        level: "success" o "error"
        """
        assert level in ['success', 'error'], "Level must be 'success' or 'error'"

        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%Y_%m_%d')

        store_folder = Path("logs") / year / month / level / store_name
        store_folder.mkdir(parents=True, exist_ok=True)
        log_file = store_folder / f"store_{day}.log"

        store_logger = logging.getLogger(f"{store_name}_{level}")
        store_logger.setLevel(logging.WARNING if level == "error" else logging.INFO)
        store_logger.propagate = False

        if not store_logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            store_logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(ColorFormatter())
            store_logger.addHandler(console_handler)

        return store_logger

    def get_auth_logger(self, level: str = "success") -> logging.Logger:
        assert level in ['success', 'error'], "El nivel debe ser 'success' o 'error'"

        logger_name = f"auth_{level}"
        auth_logger = logging.getLogger(logger_name)
        auth_logger.propagate = False

        if auth_logger.handlers:
            return auth_logger

        now = datetime.now()
        year, month, day = now.strftime('%Y'), now.strftime('%m'), now.strftime('%Y_%m_%d')
        auth_folder = Path("logs") / year / month / level / "auth"
        auth_folder.mkdir(parents=True, exist_ok=True)
        log_file = auth_folder / f"auth_{day}.log"

        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        auth_logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = ColorFormatter()
        console_handler.setFormatter(console_formatter)
        auth_logger.addHandler(console_handler)

        auth_logger.setLevel(logging.INFO if level == "success" else logging.WARNING)
        return auth_logger
