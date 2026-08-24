from classes.config.base import ConfigError, config_path, parse_sections, read_config_text, warn_print


class PollingConfig:
    """Parámetros de backoff del polling por sección (polling.ini)."""

    CONFIG_FILE = "polling.ini"
    ALLOWED_KEYS = {"base_delay", "factor", "max_delay", "jitter", "max_attempts"}
    DEFAULTS = {
        "base_delay":   5,
        "factor":       1.5,
        "max_delay":    60,
        "jitter":       0.2,
        "max_attempts": 50,
    }

    def __init__(self, directory="."):
        self.directory = directory
        self.sections = {}
        self.load_config()

    def load_config(self):
        path = config_path(self.directory, self.CONFIG_FILE)
        text = read_config_text(path)

        sections = parse_sections(
            text, inline_comments=True,
            on_warning=lambda m: warn_print(f"[{self.CONFIG_FILE}] {m}"),
        )
        for name, pairs in sections.items():
            section = self.sections.setdefault(name.strip().lower(), {})
            for key, value in pairs:
                key = key.lower()
                if key not in self.ALLOWED_KEYS:
                    warn_print(f"[{self.CONFIG_FILE}] [{name}] Clave no reconocida '{key}'")
                    continue
                try:
                    section[key] = float(value)
                except ValueError:
                    raise ConfigError(f"Valor no numérico en '{key} = {value}' (sección [{name}]).")

    def get_max_attempts(self, section: str) -> int:
        return int(self.sections.get(section.lower(), {}).get("max_attempts", self.DEFAULTS["max_attempts"]))

    def get_base_delay(self, section: str) -> float:
        return self.sections.get(section.lower(), {}).get("base_delay", self.DEFAULTS["base_delay"])

    def get_factor(self, section: str) -> float:
        return self.sections.get(section.lower(), {}).get("factor", self.DEFAULTS["factor"])

    def get_max_delay(self, section: str) -> float:
        return self.sections.get(section.lower(), {}).get("max_delay", self.DEFAULTS["max_delay"])

    def get_jitter(self, section: str) -> float:
        return self.sections.get(section.lower(), {}).get("jitter", self.DEFAULTS["jitter"])

    def get_section(self, section: str) -> dict:
        return self.sections.get(section.lower(), dict(self.DEFAULTS))
