import os

from classes.config.base import ConfigError, config_path, parse_sections, read_config_text, save_sections, warn_print


class TokensConfig:
    """Refresh tokens por cuenta y región (tokens.amztok, cifrado).

    Sin singleton: el anterior ignoraba `key`/`hmac_key` a partir de la
    segunda construcción, devolviendo silenciosamente la primera instancia.
    """

    CONFIG_FILE = "tokens.amztok"
    ALLOWED_KEYS = {"refresh_token_na", "refresh_token_eu"}

    def __init__(self, directory=".", key=None, hmac_key=None):
        self.directory = directory
        self.key = key
        self.hmac_key = hmac_key
        self.tokens = {}  # account_name -> {refresh_token_na:..., refresh_token_eu:...}
        self.load_tokens()

    def load_tokens(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        if not os.path.exists(path):
            print(f"ℹ️ Archivo '{self.CONFIG_FILE}' no encontrado. Inicializando vacío.")
            self.tokens = {}
            return

        # Pase 3: sin fallback a texto plano. El fichero es un almacén de
        # refresh-tokens; leer «sin llaves» solo podía significar un bug del
        # llamador, y save() sin llaves lo habría REESCRITO descifrado.
        if not (self.key and self.hmac_key):
            raise ConfigError(
                f"'{self.CONFIG_FILE}' es un almacén cifrado: se requieren key/hmac_key."
            )
        content = read_config_text(path, self.key, self.hmac_key)

        sections = parse_sections(content, on_warning=lambda m: warn_print(f"[{self.CONFIG_FILE}] {m}"))
        for name, pairs in sections.items():
            account = name.strip().lower()
            data = self.tokens.setdefault(account, {k: None for k in self.ALLOWED_KEYS})
            for k, v in pairs:
                k = k.lower()
                if k not in self.ALLOWED_KEYS:
                    warn_print(f"[{self.CONFIG_FILE}] Clave no reconocida '{k}' en cuenta '{account}'")
                    continue
                data[k] = v

    def save(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        save_sections(path, self.tokens, self.key, self.hmac_key)

    def get_all_tokens(self):
        return {acc: data.copy() for acc, data in self.tokens.items()}

    def get_account_tokens(self, account_name):
        return self.tokens.get(account_name.lower(), {}).copy()

    def set_tokens(self, account_name, region_dict):
        account_name = account_name.lower()
        if account_name not in self.tokens:
            self.tokens[account_name] = {
                "refresh_token_na": None,
                "refresh_token_eu": None,
            }

        for region, token in region_dict.items():
            key = f"refresh_token_{region.lower()}"
            if key in self.ALLOWED_KEYS:
                if token and token.strip():
                    self.tokens[account_name][key] = token.strip()
                else:
                    self.tokens[account_name][key] = None

    def delete_account(self, account_name):
        key = account_name.lower()
        if key in self.tokens:
            del self.tokens[key]
            return True
        return False

    @property
    def accounts_list(self):
        return list(self.tokens.keys())
