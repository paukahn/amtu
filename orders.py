"""Módulo de pedidos: reportes de órdenes (TSV + XML) -> SAP -> FTP (async).

Pase 2:
- Contrato nuevo del runner: recibe `clients` ya construidos y `ctx`.
- Las REGIONES de una cuenta se procesan EN PARALELO (asyncio.gather): EU y NA
  usan endpoints distintos con límites independientes, y el polling de cada
  reporte tarda minutos; antes iban en serie.
- La cadena create->poll->download usa AmazonClient.run_report.
- El fallback al tipo GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL solo
  se dispara si Amazon rechaza el tipo (HTTP 400). Antes CUALQUIER error
  (incluido un 5xx transitorio) cambiaba de tipo de reporte en silencio.
- El envío FTP se decide preguntando a FTPConfig (host + is_active). La
  comprobación anterior (`account_info.get("ftp_host")`) miraba claves que
  accounts.ini no admite, así que SIEMPRE era False y el FTP no se enviaba
  nunca. Ver REFACTORING.md antes del primer despliegue.

Comportamiento conservado (pase 3b, confirmado por el operador): ventana de
7 días hasta «ahora», nombres de fichero '{id}_{acronimo}_amz.{fmt}' en
minúsculas, heurística de limpieza del TSV, archivado.
"""

import os
import shutil
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from library.logging_helpers import info, error, set_log_context
from library.runner import run_module_sync
from library.mailer import notify_error_mail
from library.marketplaces import region_of_country, get_store_identifier
from classes.config import AcronymsConfig, CommonConfig, DataTransformer, FTPConfig
from library.exceptions import AmazonReportNotReadyError, AmazonThrottleError, AmazonAPIError

TEMP_DIR = "temp"
BACKUP_DIR = "orders_backup"


# ── helpers puros / bloqueantes ────────────────────────────────────────────
def extract_xml_info(xml_content):
    try:
        root = ET.fromstring(xml_content)
        xml_info = {}
        for message in root.findall('.//Message'):
            order_report = message.find('.//OrderReport')
            if order_report is not None:
                order_id = order_report.findtext('.//AmazonOrderID')
                billing_name = order_report.findtext('.//BillingData/Address/Name') or ''
                cancel_reason = order_report.findtext('.//Item/BuyerRequestedCancelReason') or ''
                xml_info[order_id] = {'billingName': billing_name, 'cancelReason': cancel_reason}
        return xml_info
    except Exception as e:
        error(f"Error parseando XML: {e}")
        return {}


def _clean_tsv_lines(content_tsv):
    clean_lines = []
    for line in content_tsv.splitlines():
        if not line.strip():
            continue
        if line.startswith("order-id") or (line[0].isdigit() and "-" in line[:5]):
            clean_lines.append(line)
        elif clean_lines:
            clean_lines[-1] = clean_lines[-1].strip() + " " + line.strip()
    return "\n".join(clean_lines)


def archive_raw(account_name, region_name, xml_data, tsv_data):
    """Guarda el backup DURABLE de los datos crudos de Amazon y devuelve la ruta.

    Se llama ANTES de transformar: si la transformación SAP lanza, los datos
    crudos (irreemplazables) ya están a salvo. Antes el archivado iba después
    de _transform_and_deliver, así que un fallo de transformación perdía el
    backup crudo por completo.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(BACKUP_DIR, account_name, region_name, timestamp)
    os.makedirs(archive_path, exist_ok=True)
    with open(os.path.join(archive_path, "raw_amazon_data.xml"), "w", encoding="utf-8") as f:
        f.write(xml_data)
    with open(os.path.join(archive_path, "raw_amazon_data.tsv"), "w", encoding="utf-8") as f:
        f.write(tsv_data)
    info(f"📁 Backup crudo guardado en: {archive_path}")
    return archive_path


def archive_final(archive_path, final_csv_path):
    """Copia el CSV final transformado al mismo backup (best-effort, tras transformar)."""
    if archive_path and final_csv_path and os.path.exists(final_csv_path):
        shutil.copy(final_csv_path, os.path.join(archive_path, "exportacion_final.csv"))


def _write_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _safe_remove(path):
    if os.path.exists(path):
        os.remove(path)


def _transform_and_deliver(account_name, mapping_code, temp_raw_tsv,
                           path_local, path_ftp, name_local, name_ftp, xml_info, ftp_manager):
    transformer = DataTransformer(account_name, mapping_code)
    if not transformer.transform(temp_raw_tsv, path_local, xml_info=xml_info):
        # Antes esto era un skip silencioso: sin fichero local, sin FTP y sin
        # alerta. Un mapping ausente o un TSV sin filas válidas debe SONAR —
        # el guard de _process_region_guarded lo convierte en error + correo.
        raise RuntimeError(
            f"Transformación sin resultado para {account_name}/{mapping_code}: "
            f"no se generó {name_local} (¿mapping ausente o reporte sin filas válidas?)"
        )
    info(f"   ✅ Guardado local: {name_local}")
    if ftp_manager.has_transport(account_name):
        # Copia del fichero ya transformado: la segunda transformación completa
        # (releer + reprocesar todo el TSV) producía un byte-a-byte idéntico.
        shutil.copyfile(path_local, path_ftp)
        if ftp_manager.send_file(account_name, path_ftp):
            info(f"   🚀 Enviado FTP: {name_ftp}")
        _safe_remove(path_ftp)
    else:
        info("   ℹ️ Sin transporte FTP configurado/activo. Solo guardado local.")


def _local_output_name(report_id, acronym, orders_format):
    """Nombre del fichero local de pedidos: acrónimo y 'amz' en MINÚSCULAS.

    DECISIÓN CONFIRMADA POR EL OPERADOR (pase 3b): el consumidor espera
    '..._cos_amz.txt'. Los ficheros históricos en MAYÚSCULAS
    ('..._COS_AMZ.txt') que produjo la versión síncrona eran el defecto, no la
    referencia. acronyms.txt guarda el acrónimo en mayúsculas (COS), así que
    se baja aquí."""
    return f"{report_id}_{acronym.lower()}_amz.{orders_format}"


def _orders_date_range(now):
    """Ventana de pedidos: desde las 00:00 UTC de hace 7 días hasta AHORA.

    DECISIÓN CONFIRMADA POR EL OPERADOR (pase 3b): 7 días es lo correcto — los
    14 días de la versión síncrona antigua eran demasiado. `end` = momento
    actual (incluye el día en curso). Devuelve (start_date, end_date) en
    ISO-8601 con sufijo Z.
    """
    end_dt = now
    start_dt = (end_dt - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return start_dt.strftime(fmt), end_dt.strftime(fmt)


# ── creación / polling de reportes ─────────────────────────────────────────
def _report_types(is_na):
    rt_xml = "GET_ORDER_REPORT_DATA_SHIPPING" if is_na else "GET_ORDER_REPORT_DATA_INVOICING"
    rt_tsv = "GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING" if is_na else "GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING"
    return rt_xml, rt_tsv


async def _run_report_safe(client, kind, mkt_ids, report_type, start_date, end_date):
    """run_report degradando «no completado»/«throttled» a None (como antes)."""
    try:
        run = await client.run_report(mkt_ids, report_type, start_date=start_date, end_date=end_date)
    except (AmazonReportNotReadyError, AmazonThrottleError) as e:
        error(f"⚠️ Reporte {kind.upper()} no completado: {e}")
        return None
    if not run.content:
        info(f"ℹ️ Reporte {kind.upper()} completado sin documentos (período sin pedidos)")
    return run


async def _run_tsv(client, mkt_ids, start_date, end_date, is_na):
    rt_tsv = _report_types(is_na)[1]
    try:
        return rt_tsv, await _run_report_safe(client, "tsv", mkt_ids, rt_tsv, start_date, end_date)
    except AmazonAPIError as e:
        # Cambiar de tipo de reporte SOLO si Amazon rechazó el tipo (400):
        # un error transitorio ya viene reintentado desde el transporte.
        if e.status_code != 400:
            raise
        rt_tsv = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
        return rt_tsv, await _run_report_safe(client, "tsv", mkt_ids, rt_tsv, start_date, end_date)


async def _run_xml(client, mkt_ids, start_date, end_date, is_na):
    rt_xml = _report_types(is_na)[0]
    try:
        return rt_xml, await _run_report_safe(client, "xml", mkt_ids, rt_xml, start_date, end_date)
    except AmazonAPIError as e:
        error(f"⚠️ No se pudo obtener el reporte XML (opcional): {e}")
        return rt_xml, None


# ── orquestación por región / cuenta ───────────────────────────────────────
async def _process_region(clients, account_name, acronym, orders_format,
                          ftp_manager, region_name, all_tiendas, start_date, end_date, output_dir):
    region_upper = region_name.upper()
    region_lower = region_upper.lower()
    set_log_context(f"{account_name}/{region_upper}")

    valid_stores = [str(t).strip().lower() for t in all_tiendas
                    if region_of_country(str(t).strip()) == region_upper]
    if not valid_stores:
        return

    mkt_ids = [get_store_identifier(s) for s in valid_stores]
    client = clients.client(region_lower)
    is_na = region_upper == 'NA'

    # return_exceptions=True: esperamos SIEMPRE a ambas tareas. Sin ello, si
    # la rama TSV lanza, gather propaga al instante y la tarea XML queda
    # huérfana consultando la API hasta morir sobre el cliente ya cerrado.
    tsv_result, xml_result = await asyncio.gather(
        _run_tsv(client, mkt_ids, start_date, end_date, is_na),
        _run_xml(client, mkt_ids, start_date, end_date, is_na),
        return_exceptions=True,
    )
    if isinstance(tsv_result, BaseException):
        raise tsv_result
    _rt_tsv, run_tsv = tsv_result
    if isinstance(xml_result, BaseException):
        error(f"⚠️ Reporte XML (opcional) falló de forma inesperada: {xml_result}")
        run_xml = None
    else:
        _rt_xml, run_xml = xml_result

    if not run_tsv or not run_tsv.content:
        info(f"ℹ️ Sin pedidos en el período {start_date[:10]} – {end_date[:10]} para {region_upper}. Saltando.")
        return

    content_tsv = _clean_tsv_lines(run_tsv.content)

    content_xml, xml_info = "", {}
    if run_xml and run_xml.content:
        content_xml = run_xml.content
        xml_info = extract_xml_info(content_xml)

    id_tsv = run_tsv.reportId
    name_local = _local_output_name(id_tsv, acronym, orders_format)
    path_local = os.path.join(output_dir, name_local)
    prefix = "ROW" if region_upper == "EU" else "USA"
    name_ftp = f"{prefix}_{id_tsv}.{orders_format}"
    path_ftp = os.path.join(TEMP_DIR, name_ftp)
    temp_raw_tsv = os.path.join(TEMP_DIR, f"raw_{id_tsv}.tsv")

    await asyncio.to_thread(_write_text, temp_raw_tsv, content_tsv)
    try:
        # Archivar el crudo ANTES de transformar: si _transform_and_deliver lanza,
        # los datos de Amazon ya están respaldados (antes se perdían).
        archive_path = await asyncio.to_thread(archive_raw, account_name, region_upper, content_xml, content_tsv)
        mapping_code = "usa" if is_na else valid_stores[0]
        await asyncio.to_thread(
            _transform_and_deliver, account_name, mapping_code, temp_raw_tsv,
            path_local, path_ftp, name_local, name_ftp, xml_info, ftp_manager,
        )
        await asyncio.to_thread(archive_final, archive_path, path_local)
    finally:
        # También en fallo: sin esto el raw_<id>.tsv (con PII de compradores)
        # quedaba huérfano en temp/ para siempre.
        await asyncio.to_thread(_safe_remove, temp_raw_tsv)


async def _process_region_guarded(clients, account_name, acronym, orders_format,
                                  ftp_manager, region_name, all_tiendas, start_date, end_date, output_dir):
    try:
        await _process_region(
            clients, account_name, acronym, orders_format,
            ftp_manager, region_name, all_tiendas, start_date, end_date, output_dir,
        )
    except Exception as e:
        msg = f"Error crítico en {account_name}/{region_name.upper()}: {e}"
        error(msg)
        await asyncio.to_thread(notify_error_mail, f"Error Pedidos: {account_name}", msg)


async def process_orders_account(clients, account_name, account_info, ctx):
    info(f"🚀 Iniciando proceso para: {account_name}")
    acronym = AcronymsConfig("config").get_acronym(account_name)
    orders_format = account_info.get("formato_de_pedidos", "csv")
    output_dir = CommonConfig("config").get_orders_folder()
    for d in (TEMP_DIR, output_dir, BACKUP_DIR):
        if d:
            os.makedirs(d, exist_ok=True)

    # to_thread: FTPConfig descifra ftp_accounts.amzaccs (AES+HMAC) + lee disco;
    # E/S bloqueante fuera del event loop, como el resto del I/O de este módulo.
    ftp_manager = await asyncio.to_thread(FTPConfig, key=ctx.key, hmac_key=ctx.hmac_key)

    now = datetime.now(timezone.utc)
    start_date, end_date = _orders_date_range(now)

    all_tiendas = account_info.get("tiendas", [])
    config_mercados = account_info.get("mercados", [])

    await asyncio.gather(*(
        _process_region_guarded(
            clients, account_name, acronym, orders_format,
            ftp_manager, region_name, all_tiendas, start_date, end_date, output_dir,
        )
        for region_name in config_mercados
    ))


def main():
    info("🏁 Iniciando exportación de pedidos...")
    run_module_sync("orders", process_orders_account)
    info("🔚 Proceso finalizado.")


if __name__ == "__main__":
    main()
