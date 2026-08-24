from classes.config.base import ConfigError, config_path, parse_flat, read_config_text
from library.security import encrypt


class MailConfig:
    """Cuenta SMTP raíz (mail.email, cifrado).

    Novedad del pase 2: `smtp_host` y `smtp_port` son configurables en el
    fichero (antes 'smtp.gmail.com:465' estaba hardcodeado en send_mail).
    Si no están definidos se mantienen los valores de siempre.
    """

    CONFIG_FILE = 'mail.email'
    REQUIRED_KEYS = ['email', 'password']
    DEFAULT_SMTP_HOST = "smtp.gmail.com"
    DEFAULT_SMTP_PORT = 465

    def __init__(self, directory=".", key=None, hmac_key=None):
        self.directory = directory
        self.key = key
        self.hmac_key = hmac_key
        self.email = None
        self.password = None
        self.smtp_host = self.DEFAULT_SMTP_HOST
        self.smtp_port = self.DEFAULT_SMTP_PORT
        self.load_config()

    def load_config(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        if not self.key or not self.hmac_key:
            raise ConfigError("Se requieren 'key' y 'hmac_key' para descifrar el archivo de correo.")

        content = read_config_text(path, self.key, self.hmac_key)
        config = {k.lower(): v for k, v in parse_flat(content, on_warning=lambda _m: None)}

        for required in self.REQUIRED_KEYS:
            if required not in config:
                raise ConfigError(f"Campo requerido '{required}' no encontrado en '{self.CONFIG_FILE}'.")

        self.email = config["email"]
        self.password = config["password"]
        self.smtp_host = config.get("smtp_host", self.DEFAULT_SMTP_HOST)
        try:
            self.smtp_port = int(config.get("smtp_port", self.DEFAULT_SMTP_PORT))
        except ValueError:
            raise ConfigError(f"smtp_port no numérico en '{self.CONFIG_FILE}'.")

    def save_config(self):
        lines = [f"email = {self.email}", f"password = {self.password}"]
        # Solo persistimos host/puerto si difieren del valor por defecto, para
        # no cambiar el formato de ficheros existentes.
        if self.smtp_host != self.DEFAULT_SMTP_HOST:
            lines.append(f"smtp_host = {self.smtp_host}")
        if self.smtp_port != self.DEFAULT_SMTP_PORT:
            lines.append(f"smtp_port = {self.smtp_port}")
        content = "\n".join(lines) + "\n"
        path = config_path(self.directory, self.CONFIG_FILE)
        encrypted = encrypt(content.encode("utf-8"), self.key, self.hmac_key)
        # Atómico + .bak: una escritura parcial del blob cifrado lo invalida entero.
        from library.atomic_io import atomic_write_bytes
        atomic_write_bytes(path, encrypted, backup=True)

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_smtp_host(self):
        return self.smtp_host

    def get_smtp_port(self):
        return self.smtp_port

    def set_credentials(self, email, password):
        self.email = email
        self.password = password
        self.save_config()
