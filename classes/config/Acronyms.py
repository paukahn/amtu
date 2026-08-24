import os

from classes.config.base import config_path, parse_flat


class AcronymsConfig:
    """Acrónimos por cuenta (acronyms.txt). Fichero ausente => sin acrónimos.

    Sin singleton: antes `AcronymsConfig()` sin argumentos heredaba el
    directorio de la PRIMERA construcción del proceso, así que el resultado
    dependía del orden de imports. Ahora cada llamada usa su `directory`.
    """

    def __init__(self, directory="."):
        self.path = config_path(directory, "acronyms.txt")
        self.data = {}
        self.load()

    def load(self):
        self.data = {}
        if not os.path.exists(self.path):
            return

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                text = f.read()
        except OSError as e:
            print(f"⚠️ Error al leer acronyms.txt: {e}")
            return

        for key, val in parse_flat(text, on_warning=lambda _m: None):
            if key and val:
                self.data[key.lower()] = val

    def get(self, account_name, default=None):
        return self.get_acronym(account_name)

    def get_acronym(self, account_name):
        if not account_name:
            return "unknown"
        return self.data.get(account_name.lower(), account_name)

    def reload(self):
        self.load()
