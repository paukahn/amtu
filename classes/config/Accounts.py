from classes.config.base import ConfigError, config_path, parse_sections, read_config_text, warn_print


class AccountsConfig:
    """Cuentas de vendedor (accounts.ini).

    Ya no es singleton: cada construcción relee el fichero (barato) y respeta
    sus argumentos. El singleton anterior ignoraba `directory` a partir de la
    segunda llamada, lo que creaba dependencias ocultas del orden de
    inicialización. Errores fatales → ConfigError (antes print + sys.exit).
    """

    CONFIG_FILE = "accounts.ini"
    ALLOWED_KEYS = {"mercados", "tiendas", "aplicacion", "modulos", "formato_de_pedidos"}

    def __init__(self, directory="."):
        self.directory = directory
        self.accounts = {}
        self.load_accounts()

    def load_accounts(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        text = read_config_text(path)
        # Prefijo con el nombre del fichero: sin él, un «línea malformada o
        # fuera de sección» no dice QUÉ fichero está mal (p.ej. un common.ini
        # pegado por error dentro de accounts.ini en el despliegue).
        sections = parse_sections(
            text, inline_comments=True, block_comments=True,
            on_warning=lambda m: warn_print(f"[{self.CONFIG_FILE}] {m}"),
        )

        for name, pairs in sections.items():
            account = name.strip().lower()
            data = self.accounts.setdefault(account, {
                "mercados": set(),
                "tiendas": set(),
                "modulos": set(),
                "aplicacion": None,
                "formato_de_pedidos": "tsv",
            })
            for key, values in pairs:
                key = key.lower()
                if key not in self.ALLOWED_KEYS:
                    warn_print(f"[{self.CONFIG_FILE}] [{account}] Clave no reconocida '{key}'")
                    continue
                if key == "aplicacion":
                    data["aplicacion"] = values
                elif key == "formato_de_pedidos":
                    data["formato_de_pedidos"] = values.lower()
                else:
                    # Las claves de lista se acumulan entre líneas repetidas,
                    # igual que en el parser original.
                    for val in values.split(","):
                        val = val.strip().lower()
                        if val:
                            data[key].add(val)

        for cuenta, data in self.accounts.items():
            if not data["aplicacion"]:
                raise ConfigError(f"Cuenta '{cuenta}' no tiene 'aplicacion' definida.")

    def get_all_accounts(self):
        return {
            cuenta: {
                "mercados": sorted(list(data.get("mercados", []))),
                "tiendas": sorted(list(data.get("tiendas", []))),
                "modulos": sorted(list(data.get("modulos", []))),
                "formato_de_pedidos": data.get("formato_de_pedidos", "tsv"),
                "aplicacion": data.get("aplicacion"),
            } for cuenta, data in self.accounts.items()
        }

    def get_account(self, name):
        data = self.accounts.get(name.lower())
        if data is None:
            return None
        return {
            "mercados": sorted(list(data.get("mercados", []))),
            "tiendas": sorted(list(data.get("tiendas", []))),
            "formato_de_pedidos": data.get("formato_de_pedidos", "tsv"),
            "aplicacion": data.get("aplicacion"),
        }

    def get_application_name_for_account(self, account_name):
        cuenta = self.get_account(account_name)
        return cuenta.get("aplicacion") if cuenta else None

    def get_accounts_by_application(self, app_name):
        return {
            name: data for name, data in self.accounts.items()
            if data.get("aplicacion") == app_name
        }

    @property
    def accounts_list(self):
        return self.get_all_accounts()
