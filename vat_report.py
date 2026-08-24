"""Módulo VAT: reporte GET_VAT_TRANSACTION_DATA (async).

Pase 2:
- Contrato nuevo del runner (recibe `clients` y `ctx`).
- La cadena create -> poll -> RDT -> download es ahora una llamada a
  AmazonClient.run_report; la descompresión gzip la decide el cliente según
  `compressionAlgorithm` del documento (antes este módulo asumía gzip).
- La ventana «mes anterior» se calcula AQUÍ: era política de negocio de este
  módulo y estaba enterrada como default en el cliente de la API.
- El bucle de reintentos de creación desaparece: los errores transitorios
  (5xx / red) ya se reintentan en el transporte; reintentar un 400 era inútil.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from io import StringIO

import pandas as pd

from library.logging_helpers import info, error, set_log_context
from library.runner import run_module_sync
from library.file_explorer import save_vat_report
from library.mailer import notify_error_mail
from library.marketplaces import get_store_identifier
from library.exceptions import AmazonReportNotReadyError, AmazonThrottleError


def _prev_month_window(now=None):
    """(start, end) ISO-8601 UTC del mes natural anterior, AMBOS dentro del
    mismo mes calendario.

    ⚠️ Restricción verificada en producción: GET_VAT_TRANSACTION_DATA termina
    en FATAL si el rango cruza la frontera de mes — un dataEndTime en el
    primer instante del mes corriente (2026-07-01T00:00:00Z) hizo fallar el
    reporte, mientras que la versión síncrona original, que envía
    <último día>T23:59:59Z, descarga sin problemas. Por eso el límite superior
    es el ÚLTIMO segundo del mes anterior, exactamente como el original.

    Se mantiene del pase 3 el cálculo en UTC (el original usaba hora local con
    sufijo 'Z'): ejecutar el cron el día 1 a partir de las 03:00 UTC.
    """
    now = now or datetime.now(timezone.utc)
    first_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_prev = first_this - timedelta(seconds=1)  # <último día>T23:59:59
    first_prev = last_prev.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return first_prev.strftime(fmt), last_prev.strftime(fmt)


def _tsv_text_to_dataframe(text: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(text), sep='\t', dtype=str)


async def process_vat_account(clients, account_name, account_info, ctx):
    markets = account_info.get("mercados", [])
    tiendas = account_info.get("tiendas", [])

    if not markets or not tiendas:
        error(f"Faltan datos de configuración para '{account_name}'.")
        return

    target_market = markets[0]
    set_log_context(f"{account_name}/{target_market}")
    first_tienda_name = tiendas[0]
    shop_id = get_store_identifier(first_tienda_name)
    client = clients.client(target_market)

    info(f"🚀 Iniciando reporte VAT para '{account_name}' vía {first_tienda_name} ({shop_id})")

    try:
        start_date, end_date = _prev_month_window()
        run = await client.run_report(
            shop_id, "GET_VAT_TRANSACTION_DATA",
            start_date=start_date, end_date=end_date, section="vat_reports",
        )

        if not run.content:
            error(f"⚠️ Reporte VAT {run.reportId} terminó sin documento (¿período sin transacciones?).")
            return

        df = await asyncio.to_thread(_tsv_text_to_dataframe, run.content)
        await asyncio.to_thread(save_vat_report, df, account_name, "UNIFIED_EU")
        info(f"💾 Reporte VAT guardado para {account_name}.")

    except AmazonReportNotReadyError:
        error(f"❌ Reporte VAT no completado tras {ctx.polling_cfg.get_max_attempts('vat_reports')} intentos.")
    except AmazonThrottleError as e:
        error(f"❌ Throttled durante reporte VAT: {e}")
    except Exception as e:
        # Alerta por correo, como en orders/stock/trackings: un informe FISCAL
        # que falla (p.ej. FATAL de Amazon) no puede quedarse solo en el log.
        msg = f"✖ Error crítico en VAT para {account_name}: {e}"
        error(msg)
        await asyncio.to_thread(notify_error_mail, f"Error VAT: {account_name}", msg)


def main():
    info("🏁 Iniciando sincronización de reportes VAT...")
    run_module_sync("vat", process_vat_account)
    info("🏁 Proceso VAT finalizado.")


if __name__ == "__main__":
    main()
