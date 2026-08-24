"""E/S de ficheros locales y remotos de los módulos.

Cambios del pase 2:
- Sin side-effects de import: antes el módulo construía CommonConfig al
  importarse y congelaba `base_folder` como valor por defecto de argumentos.
  Ahora la carpeta se resuelve al llamar.
- `read_remote_file` usa httpx CON timeout (antes requests sin timeout: un
  servidor colgado bloqueaba el hilo para siempre). follow_redirects=True
  para conservar el comportamiento de requests.
- `save_vat_report` crea el directorio real del fichero (antes el parámetro
  `folder` se concatenaba dentro del NOMBRE de fichero y el subdirectorio
  nunca se creaba, así que el guardado fallaba siempre).
- `load_market_csv` y `save_report` (solo brand analytics) eliminados junto
  con el módulo.

Pase 3d — BUG CONFIRMADO en producción (vietapreciosfba): `read_remote_file`
hacía UN solo intento; un timeout de red puntual entre el servidor y Google
Sheets (confirmado transitorio: la misma URL respondió en <1s al reintentar
manualmente segundos después) tiraba la cuenta entera sin una segunda
oportunidad. El resto del proyecto ya reintenta este tipo de fallo
(`transport.py` para la SP-API, `spapi_client._s3_request` para S3) — aquí
faltaba el mismo tratamiento porque esta función quedó fuera de esa pila.
"""

import os, json, time
from datetime import datetime
import csv

import httpx
import pandas as pd
from io import StringIO
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential, wait_random

from classes.config import CommonConfig
from library.logging_helpers import error, info

REMOTE_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

# Reintento del fichero remoto de stock: solo fallos TRANSITORIOS (red/timeout
# o 5xx del lado de Google) — un 404 (gid/enlace realmente inválido) no se
# arregla reintentando, así que no entra aquí.
def _is_transient_remote_error(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return False


def _reports_folder() -> str:
    return CommonConfig("config").get_reports_folder()


def detect_separator(text: str) -> str:
    """
    Detecta automáticamente si el contenido está separado por tabulaciones o comas u otro.
    """
    try:
        sample = text[:2048]
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except Exception:
        return "\t"


def read_remote_file(url: str) -> pd.DataFrame:
    """
    Lee archivo remoto (CSV o TSV) detectando automáticamente el separador.
    BLOQUEANTE: llamar con asyncio.to_thread desde código async.

    dtype=str en TODO el fichero (pase 3): los consumidores (stock_feed) ya
    parsean números vía str()/float(), y dejar que pandas infiera tipos
    convertía EAN/códigos en floats con notación científica.

    Reintenta (pase 3d) ante fallos transitorios de red/timeout o 5xx del
    lado remoto — 3 intentos, backoff exponencial + jitter, igual que el
    resto del proyecto. Un 404/403 (enlace realmente roto) falla al primer
    intento, sin reintentar en vano.
    """
    try:
        for attempt in Retrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=15) + wait_random(0, 1),
            retry=retry_if_exception(_is_transient_remote_error),
            reraise=True,
        ):
            with attempt:
                response = httpx.get(url, timeout=REMOTE_TIMEOUT, follow_redirects=True)
                response.raise_for_status()
                content = response.text
        sep = detect_separator(content)
        return pd.read_csv(StringIO(content), sep=sep, dtype=str)
    except Exception as e:
        raise RuntimeError(f"No se pudo leer {url}: {e}")


def save_stock_result(json_unzipped, account, store_code, folder=None):
    if not json_unzipped:
        error(f"⚠️ No hay datos para guardar el stock resultado de {store_code.upper()} en {account}.")
        return

    folder = folder or _reports_folder()
    date = datetime.today().strftime("%Y%m%d_%H%M%S")
    filename = f"{store_code}_{date}.json"
    foldername = os.path.join(folder, account)
    os.makedirs(foldername, exist_ok=True)
    full_foldername = os.path.join(foldername, filename)
    with open(full_foldername, "w", encoding='utf-8') as f:
        json.dump(json_unzipped, f, indent=2, ensure_ascii=False)


def save_tracking_result(report_content, account, store_code, folder="tracking_results"):
    if not report_content:
        error(f"⚠️ No hay contenido de reporte para {store_code.upper()} en {account}.")
        return

    date = datetime.today().strftime("%m%Y")
    filename = f"{store_code}_{date}.log"

    foldername = os.path.join(folder, account)
    os.makedirs(foldername, exist_ok=True)

    full_path = os.path.join(foldername, filename)

    mode = "a" if os.path.exists(full_path) else "w"

    with open(full_path, mode, encoding='utf-8') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n--- REPORT START: {timestamp} ---\n")
        f.write(report_content)
        f.write("\n--- REPORT END ---\n")

    info(f"📋 Report saved to {full_path}")


def archive_sent_stock_tsv(df, account, region, folder="stock_results"):
    archive_dir = os.path.join(folder, account, "ficheros_enviados")
    os.makedirs(archive_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{region}_upload_{timestamp}.tsv"
    full_path = os.path.join(archive_dir, filename)

    df.to_csv(full_path, sep="\t", index=False, encoding='utf-8')
    info(f"📁 Stock backup archived to: {full_path}")


def load_mails(folder="config"):
    filename = "emails.txt"
    foldername = os.path.join(folder, filename)
    if not os.path.isfile(foldername):
        error(f"file {foldername} no existe")
        return
    with open(foldername, "r", encoding='utf-8') as f:
        emails = [line.strip() for line in f if line.strip()]
    return emails


def load_trackings(account, shop, folder="trackings", filename=None):
    foldername = folder

    if not os.path.exists(foldername):
        error(f"⚠️ La carpeta {foldername} no encontrada. Saltando {account}/{shop}.", type="warning")
        return None

    if not filename:
        filename = f"{shop}_trackings_output.txt"

    route = os.path.join(foldername, filename)

    if not os.path.isfile(route):
        error(f"⚠️ El archivo {route} no encontrado. Saltando {account}/{shop}.", type="warning")
        return None

    try:
        # Codificación: los ficheros los deja una ERP externa; en Windows suele
        # ser cp1252 (una 'ñ' en el transportista rompía el utf-8 estricto y el
        # fichero entero se saltaba en silencio).
        encoding = "utf-8-sig"
        try:
            with open(route, "r", encoding=encoding) as fh:
                sample = fh.read(2048)
        except UnicodeDecodeError:
            encoding = "cp1252"
            with open(route, "r", encoding=encoding) as fh:
                sample = fh.read(2048)
        sep = detect_separator(sample)
        # dtype=str en TODO el fichero (pase 3). El dtype anterior apuntaba a
        # "order-id", columna que aquí aún se llama "order_id" (el rename llega
        # después, en trackings), así que NO aplicaba a nada: tracking_number
        # se parseaba como número — los de 20 dígitos (DHL/GLS) desbordaban
        # int64 a float64 y salían como '1.23e+19', y los ceros a la izquierda
        # se perdían. A Amazon llegaban trackings corruptos.
        df = pd.read_csv(route, sep=sep, dtype=str, encoding=encoding)
        return df
    except Exception as e:
        error(f"⚠️ Error leyendo {route}: {e}. Saltando.", type="warning")
        return None


def save_vat_report(data, account, store_code, folder='reportes_vat'):
    """
    Guarda los datos del reporte fiscal (ya procesados) en un archivo TSV
    bajo <reports_folder>/reportes_fiscales/<folder>/.
    """
    from dateutil.relativedelta import relativedelta

    if data is None or (isinstance(data, pd.DataFrame) and data.empty):
        error(f"⚠️ No hay datos para guardar el reporte fiscal de {store_code.upper()} en {account}.")
        return

    date_str = (datetime.today() - relativedelta(months=1)).strftime("%m%Y")
    filename = f"{folder}/VAT_{account}_{date_str}.csv"

    foldername = os.path.join(_reports_folder(), "reportes_fiscales")

    try:
        full_path = os.path.join(foldername, filename)
        # `filename` lleva un subdirectorio: crear la ruta REAL del fichero
        # (el makedirs anterior solo creaba `foldername` y el to_csv fallaba).
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)

        df.to_csv(full_path, index=False, encoding='utf-8', sep='\t')

        info(f"✅ [file_explorer] Reporte fiscal (TSV) guardado en: {full_path}")
        return full_path

    except Exception as e:
        error(f"❌ [file_explorer] Error al escribir el archivo TSV para {account}: {e}")


def parse_amazon_report(report_content):
    if not report_content:
        return None, False

    lines = report_content.strip().split('\n')
    error_messages = []
    summary_lines = []

    for line in lines:
        line = line.strip('\r')
        cols = line.split('\t')

        if "Number of records" in line:
            summary_lines.append(line.strip())

        if "Error" in cols:
            try:
                err_idx = cols.index("Error")

                order_id = cols[1].strip() if len(cols) > 1 and cols[1].strip() else "N/A"
                err_code = cols[err_idx - 1].strip() if err_idx > 0 else "???"
                err_msg = cols[err_idx + 1].strip() if len(cols) > err_idx + 1 else "No message"

                error_messages.append(f"{order_id}: \tError ({err_code})\t{err_msg}")
            except Exception:
                error_messages.append(f"Raw Error Line: {line.strip()}")

    if not error_messages:
        return None, False

    body = "The following errors were found during Amazon Feed processing:\n\n"
    body += "\n".join(error_messages)
    body += "\n\nFeed Processing Summary:\n\t"
    body += "\n\t".join(summary_lines)

    return body, True
