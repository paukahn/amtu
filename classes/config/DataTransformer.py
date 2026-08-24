import re, json, os, csv
from datetime import datetime

from classes.config.Acronyms import AcronymsConfig
from classes.config.base import ConfigError


class DataTransformer:
    def __init__(self, client_name, country_code, config_path="config/mappings"):
        self.client_name = client_name
        self.country_code = country_code.upper()
        self.config_path = config_path
        self.config = self._load_config()

        self.region_data = self._get_region_data()
        self.sap_columns = self.region_data.get("sap_columns", [])

        now = datetime.now()
        self.context_vars = {
            "date": now.strftime("%Y%m%d"),
            "year": now.strftime("%Y"),
            "month": now.strftime("%m"),
            "day": now.strftime("%d"),
            "time": now.strftime("%H%M%S"),
            "acronym": AcronymsConfig("config").get(self.client_name),
            "account": self.client_name,
            "country": self.country_code
        }

    def _load_config(self):
        from library.logging_helpers import error

        file_path = os.path.join(self.config_path, f"{self.client_name.lower()}.json")
        if not os.path.exists(file_path):
            # Aviso (no excepción): hay llamadores/tests que inyectan
            # sap_columns a mano. El guard duro está en transform(): sin
            # sap_columns NUNCA se genera un fichero «exitoso» vacío.
            error(f"No existe el mapping '{file_path}' para '{self.client_name}'.", type="warning")
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            # Un mapping ilegible debe sonar como error de configuración claro,
            # no como un traceback anónimo a mitad de la transformación.
            raise ConfigError(f"Mapping '{file_path}' ilegible o mal formado: {e}") from e

    def _get_region_data(self):
        country_rules = self.config.get("country_rules", {})
        if self.country_code in country_rules:
            return country_rules[self.country_code]

        groups = self.config.get("groups", {})
        for group_name, countries in groups.items():
            if self.country_code in countries:
                return country_rules.get(group_name, {})
        return {}

    def _expand_template(self, template, row):
        """Expande una plantilla de CONFIG con context_vars + fila.

        Tolera plantillas mal formadas (clave ausente, índice, formato): en vez
        de tumbar toda la transformación, deja la plantilla sin expandir y avisa.
        """
        try:
            return template.format_map({**self.context_vars, **row})
        except (KeyError, IndexError, ValueError, AttributeError) as e:
            from library.logging_helpers import error
            error(f"Plantilla SAP invalida '{template}': {e}", type="warning")
            return template

    def _apply_logic(self, row, xml_info):
        new_row = {}
        order_id = row.get("order-id", "")
        order_xml_data = xml_info.get(order_id, {})

        for col in self.sap_columns:
            target_name = col["name"]
            source = col.get("source", "tsv")
            val = ""
            # `is_template`: solo expandimos con format_map los valores que vienen
            # de la CONFIG (plantillas), nunca los datos crudos de Amazon. Antes
            # se hacía format_map sobre cualquier valor con "{", incluidos campos
            # como buyer-name o gift-message: un valor "{Jr}" -> KeyError (caída
            # de la transformación) y "{x.__class__}" era inyección de format-string.
            is_template = False

            if source == "xml":
                val = order_xml_data.get(col.get("key"), "")
            elif source == "logic":
                val = col.get("value", "")
                is_template = True
            else:
                amz_key = col.get("amz_name", target_name)
                val = row.get(amz_key, "")

            if "rules" in col:
                for rule in col["rules"]:
                    check_val = row.get(rule.get("source_key"), val)
                    if re.match(rule["regex"], str(check_val)):
                        val = self._expand_template(rule["result"], row)
                        is_template = False  # ya expandido aquí
                        break

            if is_template and isinstance(val, str) and "{" in val:
                val = self._expand_template(val, row)

            new_row[target_name] = val

        return new_row

    @staticmethod
    def _clean_field(value) -> str:
        """Aplana tab/CR/LF dentro de un valor: el consumidor (SAP) corta por
        '\t' sin parser CSV, así que un tab embebido descuadraría las columnas
        y un salto de línea rompería la fila."""
        text = "" if value is None else str(value)
        return text.replace("\t", " ").replace("\r", " ").replace("\n", " ")

    def transform(self, raw_tsv_path, output_path, xml_info):
        from library.logging_helpers import error

        if not os.path.exists(raw_tsv_path): return False

        # Guard: sin reglas de mapping para este país, ANTES se generaba un
        # fichero de filas vacías y se devolvía True — orders lo daba por
        # bueno y lo enviaba a SAP/FTP como si nada.
        if not self.sap_columns:
            error(
                f"Sin 'sap_columns' para {self.client_name}/{self.country_code} "
                f"(¿falta el país en config/mappings/{self.client_name.lower()}.json?). No se genera fichero.",
            )
            return False

        transformed_rows = []
        with open(raw_tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

            for row in reader:
                row = {k.strip() if k else k: v for k, v in row.items()}

                if not row.get("order-id"):
                    continue

                transformed_rows.append(self._apply_logic(row, xml_info))

        if not transformed_rows:
            error(f"⚠️ No rows transformed for {self.country_code}", type="warning")
            return False

        headers = [col["name"] for col in self.sap_columns]
        # Escritura ATÓMICA en el directorio destino: el consumidor (SAP) sondea
        # la carpeta y antes podía llevarse un fichero a medio escribir —
        # válido en apariencia, incompleto en contenido. temp en el MISMO dir
        # (os.replace no cruza sistemas de ficheros) y publicación de golpe.
        # Formato: TSV plano con CRLF, idéntico al que producía DictWriter,
        # pero con los valores aplanados (sin tabs/saltos embebidos) en vez de
        # confiar en un quoting que el consumidor no interpreta.
        tmp_path = f"{output_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, 'w', encoding='utf-8', newline='') as f:
                f.write("\t".join(headers) + "\r\n")
                for row in transformed_rows:
                    f.write("\t".join(self._clean_field(row.get(h, "")) for h in headers) + "\r\n")
            os.replace(tmp_path, output_path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
        return True