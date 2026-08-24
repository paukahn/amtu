import os

from classes.config.base import ConfigError, config_path, parse_flat


class CommonConfig:
    """
    Maneja configuración global común desde common.ini.
    reports_folder es obligatorio.
    mode es opcional: si no existe, se asume 'production' por defecto.
    """

    CONFIG_FILE = 'common.ini'
    DEFAULT_CONTENT = """# Configuración común global
reports_folder=reports
"""

    VALID_MODES = {'debug', 'production'}
    VALID_ENVIRONMENTS = {'production', 'sandbox'}

    def __init__(self, directory="."):
        self.directory = directory
        self.config_values = {}
        self.load_config()

    def load_config(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        if not os.path.exists(path):
            self.create_default_config(path)

        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.config_values = {k.lower(): v for k, v in parse_flat(text, on_warning=lambda _m: None)}

        if not self.config_values.get('reports_folder'):
            raise ConfigError(f"El archivo de configuración común '{self.CONFIG_FILE}' debe contener 'reports_folder'.")

        mode = self.config_values.get('mode')
        if mode is not None and mode.lower() not in self.VALID_MODES:
            raise ConfigError(f"El modo '{mode}' no es válido. Use 'debug' o 'production'.")

        environment = self.config_values.get('environment')
        if environment is not None and environment.lower() not in self.VALID_ENVIRONMENTS:
            raise ConfigError(f"El environment '{environment}' no es válido. Use 'production' o 'sandbox'.")

    def create_default_config(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.DEFAULT_CONTENT)

    def get_reports_folder(self):
        return self.config_values.get('reports_folder')

    def get_stock_folder(self):
        return self.config_values.get('stock_folder')

    def get_trackings_folder(self):
        return self.config_values.get('trackings_folder')

    def get_orders_folder(self):
        return self.config_values.get('orders_folder')

    def get_mode(self):
        # Por defecto 'production' si no está definido en config
        return self.config_values.get('mode', 'production').lower()

    def get_environment(self):
        """'production' (defecto) o 'sandbox' — endpoint SP-API a usar."""
        return self.config_values.get('environment', 'production').lower()

    def get_retention_days(self, key: str, default: int) -> int:
        """Días de retención para housekeeping (<=0 desactiva la regla)."""
        try:
            return int(self.config_values.get(key, default))
        except (TypeError, ValueError):
            return default

    def get_stock_min_valid_ratio(self) -> float:
        """Fracción mínima de filas con SKU válido para publicar el feed (sanity-guard)."""
        from library.stock_feed import DEFAULT_MIN_VALID_RATIO
        try:
            return float(self.config_values.get('stock_min_valid_ratio', DEFAULT_MIN_VALID_RATIO))
        except (TypeError, ValueError):
            return DEFAULT_MIN_VALID_RATIO

    def get_stock_guard_min_rows(self) -> int:
        """Nº de filas a partir del cual aplicar el sanity-guard del stock."""
        from library.stock_feed import DEFAULT_GUARD_MIN_ROWS
        try:
            return int(self.config_values.get('stock_guard_min_rows', DEFAULT_GUARD_MIN_ROWS))
        except (TypeError, ValueError):
            return DEFAULT_GUARD_MIN_ROWS
