from classes.config.base import ConfigError, config_path, parse_sections, read_config_text, warn_print


class StockConfig:
    """
    Carga la configuración de stocks desde stock.ini.
    Claves permitidas: las que empiezan por 'stock' o 'sellerid'.
    Claves duplicadas dentro de una tienda: se conserva la primera (como antes).
    """

    CONFIG_FILE = "stock.ini"
    ALLOWED_KEYS_PREFIXES = ("stock", "sellerid")

    def __init__(self, directory="."):
        self.directory = directory
        self.stocks = {}
        self.load_stocks()

    def load_stocks(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        text = read_config_text(path)

        sections = parse_sections(
            text, inline_comments=True, block_comments=True,
            on_warning=lambda m: warn_print(f"[{self.CONFIG_FILE}] {m}"),
        )
        for name, pairs in sections.items():
            store = name.strip().lower()
            data = self.stocks.setdefault(store, {})
            for key, value in pairs:
                if not any(key.lower().startswith(prefix) for prefix in self.ALLOWED_KEYS_PREFIXES):
                    warn_print(f"[{self.CONFIG_FILE}] Clave no reconocida '{key}' en tienda '{store}'")
                    continue
                if key in data:
                    warn_print(f"[{self.CONFIG_FILE}] Clave duplicada '{key}' en tienda '{store}'")
                    continue
                data[key] = value

    def get_all_stocks(self):
        return {store: dict(data) for store, data in self.stocks.items()}

    def get_store_stock(self, store_name):
        return self.stocks.get(store_name.lower())

    def get_stock_url(self, store_name, region):
        store = self.get_store_stock(store_name)
        if store is None:
            return None
        key = f"stock{region.upper()}"
        return store.get(key)

    def get_seller_id(self, store_name, region):
        store = self.get_store_stock(store_name)
        if store is None:
            raise ConfigError(f"Store '{store_name}' no encontrada o no tiene configuración.")
        key = f"sellerId{region.upper()}"
        seller_id = store.get(key)

        if not seller_id:
            raise ConfigError(f"Seller ID no encontrado para región {region.upper()} en tienda {store_name}")

        return seller_id

    @property
    def stocks_list(self):
        return self.get_all_stocks()
