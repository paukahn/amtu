"""Módulo de trackings: feed POST_FLAT_FILE_FULFILLMENT_DATA (async).

Pase 2: contrato nuevo del runner (recibe `clients` y `ctx`); metadatos de
país desde library.marketplaces — tiendas como 'be' o 'nl' ya no se saltan en
silencio por falta de región. Las operaciones de disco/pandas/SMTP siguen en
asyncio.to_thread.
"""

import os
import time
import shutil
import asyncio

import pandas as pd

from classes.config import CommonConfig, AcronymsConfig
from library.logging_helpers import info, error, set_log_context
from library.runner import run_module_sync
from library.file_explorer import load_trackings, save_tracking_result, parse_amazon_report
from library.mailer import notify_error_mail
from library.marketplaces import region_of_country, get_store_identifier
from library.exceptions import AmazonFeedNotReadyError, AmazonThrottleError

RESULTS_DIR = "tracking_results"


def _belongs_to_acronym(filename: str, acronym: str) -> bool:
    """¿El fichero pertenece a esta cuenta? Prefijo `acronimo_` SIN distinguir
    mayúsculas: acronyms.txt trae el acrónimo en mayúsculas (p.ej. COS) pero los
    ficheros llegan en minúsculas (cos_uk_trackings_output.txt). Antes el match
    era sensible a mayúsculas y descartaba el fichero en silencio."""
    return filename.lower().startswith(f"{acronym}_".lower())


def _prepare_upload_file(df, base_dir, acronym, shop):
    df.rename(
        columns={
            "order_id": "order-id", "tracking_number": "tracking-number",
            "carrier_code": "carrier-code", "ship_date": "ship-date",
        },
        inplace=True, errors="ignore",
    )
    # Aplanar tabs/saltos dentro de los valores: to_csv con quoting=3
    # (QUOTE_NONE) sin escapechar LANZA si un campo contiene el separador, y
    # ese fallo abortaba la cuenta entera a mitad de lote.
    #
    # option_context (pase 3e): confirmado en producción que un fichero con
    # una columna COMPLETAMENTE vacía (p.ej. carrier_code sin rellenar en todo
    # el lote) dispara FutureWarning de pandas ("Downcasting behavior in
    # `replace`..."). No es un fallo, pero ensucia el log/correo de cron en
    # cada ejecución. Verificado que con esta opción la salida de to_csv es
    # BYTE A BYTE idéntica a la actual (sin la opción) — no cambia el fichero
    # generado, solo silencia el aviso de una migración interna de pandas que
    # no aplica aquí (todo el DataFrame ya es dtype=str desde load_trackings).
    with pd.option_context("future.no_silent_downcasting", True):
        df = df.replace({r"[\t\r\n]+": " "}, regex=True)
    temp_dir = os.path.join(base_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    # PID en el nombre: dos procesos simultáneos compartían un único temp fijo
    # y el segundo pisaba el TSV del primero entre to_csv y el envío del feed.
    temp_file = os.path.join(temp_dir, f"{acronym}_{shop}_upload_{os.getpid()}.tsv")
    df.to_csv(temp_file, sep="\t", index=False, quoting=3)
    return temp_file


def _cleanup_temp(temp_file):
    """Borra el TSV temporal cuando el envío del feed falló (no llega a archivarse)."""
    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)


def _archive_and_cleanup(item, account_name, shop):
    archive_dir = os.path.join(RESULTS_DIR, account_name, "ficheros_enviados")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    shutil.move(item["temp_file"], os.path.join(archive_dir, f"{shop}_upload_{timestamp}.tsv"))
    if os.path.exists(item["original_file"]):
        os.remove(item["original_file"])
        info(f"🗑 Deleted: {os.path.basename(item['original_file'])}")


async def process_account(clients, account_name, account_info, ctx):
    base_dir = CommonConfig("config").get_trackings_folder()
    acronym = AcronymsConfig("config").get_acronym(account_name)

    info(f"🚀 Processing account '{account_name}' (prefix: '{acronym}')")
    feeds_to_verify = []

    if not base_dir or not os.path.exists(base_dir):
        error(f"❌ BASE_DIR does not exist: {base_dir}")
        return

    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)
        if not _belongs_to_acronym(filename, acronym) or not os.path.isfile(file_path):
            continue

        parts = filename.split("_")
        if len(parts) < 2:
            continue

        shop = parts[1].lower()
        region = region_of_country(shop)
        if region is None:
            # Código de tienda desconocido (p.ej. typo en el nombre del
            # fichero): antes se ignoraba PARA SIEMPRE sin una sola línea de log.
            error(f"⚠️ Región desconocida para tienda '{shop}' en '{filename}' — fichero ignorado.", type="warning")
            continue

        for market in clients.markets:
            if region != market.upper():
                continue
            set_log_context(f"{account_name}/{market}")

            info(f"📦 Processing '{filename}' for shop '{shop}' in market '{market}'")

            trackings_df = await asyncio.to_thread(load_trackings, account_name, shop, base_dir, filename=filename)
            if trackings_df is None or trackings_df.empty:
                info(f"⚠️ No trackings in {filename}. Skipping.")
                continue

            temp_file = None
            try:
                # Dentro del try: un fallo preparando ESTE fichero (p.ej. datos
                # imposibles de serializar) no debe abortar el resto del lote.
                temp_file = await asyncio.to_thread(_prepare_upload_file, trackings_df, base_dir, acronym, shop)
                client = clients.client(market)
                marketplace_id = get_store_identifier(shop)
                feed_result = await client.send_tracking_feed(marketplace_id, temp_file)
                info(f"✅ Feed {feed_result.feedId} submitted for {acronym}/{shop}")
                feeds_to_verify.append({
                    "feed_id": feed_result.feedId,
                    "market": market,
                    "shop": shop,
                    "region": region,
                    "original_file": file_path,
                    "temp_file": temp_file,
                })
            except Exception as e:
                error(f"❌ Error sending trackings {shop} → {market}: {e}")
                await asyncio.to_thread(notify_error_mail, f"Error in {account_name} -- {shop}", str(e))
                # El item no entra en feeds_to_verify, así que _archive_and_cleanup
                # nunca moverá este temp_file: lo limpiamos aquí para no dejarlo
                # huérfano en base_dir/temp (el fichero ORIGINAL se conserva).
                await asyncio.to_thread(_cleanup_temp, temp_file)

    for item in feeds_to_verify:
        f_id = item["feed_id"]
        f_shop = item["shop"]
        set_log_context(f"{account_name}/{item['market']}")
        client = clients.client(item["market"])

        info(f"🔍 Checking feed {f_id} ({f_shop})...")
        try:
            result = await client.get_feed_status(f_id, section="trackings")
            info(f"🏁 Feed {f_id} → {result.processingStatus}")

            try:
                has_critical_errors = False
                if result.resultFeedDocumentId:
                    # Descarga + gunzip según compressionAlgorithm, centralizado
                    # en el cliente (misma lógica que stock y reports).
                    report_content = await client.download_feed_result_content(result.resultFeedDocumentId)
                    await asyncio.to_thread(save_tracking_result, report_content, account_name, item["region"])

                    clean_report, has_critical_errors = await asyncio.to_thread(parse_amazon_report, report_content)
                    if has_critical_errors:
                        error(f"⚠️ Feed {f_id} finished with errors.")
                        await asyncio.to_thread(notify_error_mail, f"Errors: {account_name} - {f_shop}", clean_report)
                    else:
                        info(f"✅ All orders updated for {f_shop}.")

                # Borrar el fichero ORIGINAL solo si el feed terminó DONE y SIN
                # errores críticos. Antes se borraba siempre — también en
                # CANCELLED/FATAL o con errores de fila — perdiendo los trackings.
                if result.processingStatus == "DONE" and not has_critical_errors:
                    await asyncio.to_thread(_archive_and_cleanup, item, account_name, f_shop)
                else:
                    error(
                        f"⚠️ Feed {f_id} no exitoso ({result.processingStatus}, "
                        f"errores={has_critical_errors}): se conserva el fichero original."
                    )
                    await asyncio.to_thread(_cleanup_temp, item["temp_file"])
            except Exception as e:
                error(f"⚠️ Cleanup/result error for feed {f_id}: {e}")

        except AmazonFeedNotReadyError:
            error(f"❌ Feed {f_id} no completado tras {ctx.polling_cfg.get_max_attempts('trackings')} intentos.")
        except AmazonThrottleError as e:
            error(f"❌ Feed {f_id} throttled: {e}")


def main():
    run_module_sync("trackings", process_account)
    info("🏁 Trackings synchronization finished.")


if __name__ == "__main__":
    main()
