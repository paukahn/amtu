import os

from classes.config.base import ConfigError, config_path, parse_sections, read_config_text, save_sections, warn_print


class FTPConfig:
    """Cuentas de transporte FTP/SFTP (ftp_accounts.amzaccs, cifrado).

    Pase 2: la clase queda como configuración + política (is_active); la
    mecánica de red vive en library.ftp_transport. Sin singleton (la CLI ya no
    necesita el hack `FTPConfig._instance = None` tras guardar).

    Pase 3: `host_key` (huella SHA256 del host SFTP) entra en las claves
    permitidas y se exige key/hmac_key — sin fallback a texto plano.
    """

    CONFIG_FILE = "ftp_accounts.amzaccs"
    ALLOWED_KEYS = {"ftp_mode", "host", "username", "password", "folder_in", "port", "is_active", "host_key"}

    def __init__(self, directory=".", key=None, hmac_key=None):
        self.directory = directory
        self.key = key
        self.hmac_key = hmac_key
        self.accounts = {}  # account_name -> {ftp_mode:..., host:...}
        self.load_config()

    def load_config(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        if not os.path.exists(path):
            print(f"ℹ️ Archivo '{self.CONFIG_FILE}' no encontrado. Inicializando vacío.")
            self.accounts = {}
            return

        if not (self.key and self.hmac_key):
            raise ConfigError(
                f"'{self.CONFIG_FILE}' es un almacén cifrado: se requieren key/hmac_key."
            )
        content = read_config_text(path, self.key, self.hmac_key)

        sections = parse_sections(content, on_warning=lambda m: warn_print(f"[{self.CONFIG_FILE}] {m}"))
        for name, pairs in sections.items():
            account = name.strip().lower()
            if not account:
                continue
            data = self.accounts.setdefault(account, {k: None for k in self.ALLOWED_KEYS})
            for k, v in pairs:
                k = k.lower()
                if k in self.ALLOWED_KEYS:
                    data[k] = v

    def save(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        save_sections(path, self.accounts, self.key, self.hmac_key)

    def get_account_params(self, account_name):
        return self.accounts.get(account_name.lower(), {}).copy()

    def is_active(self, account_name) -> bool:
        cfg = self.get_account_params(account_name)
        return str(cfg.get("is_active", "false")).lower() in ["true", "1", "yes"]

    def has_transport(self, account_name) -> bool:
        """¿Hay transporte configurado Y activo para la cuenta?"""
        cfg = self.get_account_params(account_name)
        return bool(cfg.get("host")) and self.is_active(account_name)

    def send_file(self, account_name, local_path):
        from library.ftp_transport import send_file
        from library.logging_helpers import error

        cfg = self.get_account_params(account_name)
        if not cfg or not cfg.get("host"):
            error(f"No hay configuración de transporte para '{account_name}'", type="warning")
            return False

        if not self.is_active(account_name):
            return False

        try:
            return send_file(cfg, local_path)
        except Exception as e:
            error(f"Error enviando a {account_name}: {e}")
            return False
