from classes.config.base import ConfigError, config_path, parse_sections, read_config_text, save_sections, warn_print


class ApplicationsConfig:
    """Credenciales LWA de las aplicaciones (applications.amzapps, cifrado)."""

    CONFIG_FILE = 'applications.amzapps'
    REQUIRED_KEYS = ['client_id', 'client_secret']

    def __init__(self, directory=".", key=None, hmac_key=None, original=False):
        self.directory = directory
        self.key = key
        self.hmac_key = hmac_key
        self.original = original
        self.applications = {}  # clave lower-case -> dict con info
        self.applications_original = {} if original else None  # clave original -> dict con info
        self.load_config()

    def load_config(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        if not self.key or not self.hmac_key:
            raise ConfigError("Se requieren 'key' y 'hmac_key' para descifrar el archivo de aplicaciones.")

        content = read_config_text(path, self.key, self.hmac_key)
        sections = parse_sections(content, on_warning=lambda m: warn_print(f"[{self.CONFIG_FILE}] {m}"))

        for original_name, pairs in sections.items():
            lower_name = original_name.lower()
            app = self.applications.setdefault(lower_name, {})
            app_original = None
            if self.original:
                app_original = self.applications_original.setdefault(original_name, {})

            for key, value in pairs:
                key = key.lower()
                if key == "enabled":
                    value = value.lower() in ["true", "1", "yes", "on"]
                app[key] = value
                if app_original is not None:
                    app_original[key] = value

        # Marcar enabled=True si no está definido
        for values in self.applications.values():
            values.setdefault("enabled", True)

        # Validar requeridos solo en apps activadas
        for app_key, values in self.applications.items():
            if values.get("enabled", True):
                for required in self.REQUIRED_KEYS:
                    if not values.get(required):
                        raise ConfigError(f"La aplicación '{app_key}' no tiene definido '{required}'.")

    def save(self):
        """Serializa y guarda el archivo cifrado con el estado actual de las apps.

        keep_empty=True: el save antiguo escribía también los campos vacíos;
        sin esto, una app desactivada con un campo en blanco lo perdería al
        guardar desde la CLI.
        """
        data = self.applications_original if self.original else self.applications
        path = config_path(self.directory, self.CONFIG_FILE)
        save_sections(path, data, self.key, self.hmac_key, keep_empty=True)

    def set_enabled(self, app_name, enabled: bool):
        if self.original:
            matched = None
            for k in self.applications_original:
                if k.lower() == app_name.lower():
                    matched = k
                    break
            if matched:
                self.applications_original[matched]["enabled"] = enabled
                self.applications[matched.lower()]["enabled"] = enabled
                return True
        else:
            key = app_name.lower()
            if key in self.applications:
                self.applications[key]["enabled"] = enabled
                return True
        return False

    def get_applications(self):
        return self.applications

    def get_applications_original(self):
        if not self.original:
            print("Warning: No cargado con original=True, 'applications_original' no disponible")
            return None
        return self.applications_original

    def get_active_applications(self):
        return {k: v for k, v in self.applications.items() if v.get("enabled", True)}

    def get_active_applications_original(self):
        if not self.original:
            print("Warning: No cargado con original=True, 'applications_original' no disponible")
            return None
        return {k: v for k, v in self.applications_original.items() if v.get("enabled", True)}

    def get_application(self, name):
        if not name:
            return None
        return self.applications.get(name.lower())

    def get_application_original(self, name):
        if not self.original:
            print("Warning: No cargado con original=True, 'applications_original' no disponible")
            return None
        if not name:
            return None
        return self.applications_original.get(name)

    def get_client_id(self, app_name):
        app = self.get_application(app_name)
        return app.get("client_id") if app else None

    def get_client_secret(self, app_name):
        app = self.get_application(app_name)
        return app.get("client_secret") if app else None

    def is_enabled(self, app_name):
        app = self.get_application(app_name)
        return app.get("enabled", True) if app else False
