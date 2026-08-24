"""Módulo de stock/precios: feed JSON_LISTINGS_FEED (async).

Pase 2:
- Contrato nuevo del runner: recibe `clients` ya construidos y `ctx`.
- La comprobación región↔mercado se hace ANTES de descargar el fichero
  remoto: antes cada fichero se descargaba una vez por mercado y se tiraba
  si no correspondía (con 2 mercados, todo se bajaba dos veces).
- El resultado del feed se descarga con el cliente compartido (httpx con
  timeout) en lugar de `requests` sin timeout, y se descomprime respetando
  doc.compressionAlgorithm (gunzip solo si GZIP).
- Si el feed termina sin resultFeedDocumentId se registra y se sigue (antes
  se pedía el documento "None" y fallaba más abajo).
- El feed se sube como JSON plano con Content-Type coincidente (F21): se
  eliminó el content_encoding="gzip" espurio tras verificar el contrato
  SP-API (createFeedDocument solo admite contentType; la subida no contempla
  Content-Encoding). Ver REFACTORING.md.

Pase 3b (a petición del operador): cada SKU con precio fuera de [min, max]
dispara un correo con las cifras (antes solo quedaba un warning en el log,
visible únicamente si alguien lo miraba o si el sanity-guard bloqueaba el
feed entero por volumen). Un email por región y ejecución, no uno por SKU.
"""

import asyncio
import json

from classes.config import StockConfig, CommonConfig
from library.logging_helpers import info, error, set_log_context
from library.runner import run_module_sync
from library.file_explorer import read_remote_file, save_stock_result, archive_sent_stock_tsv
from library.stock_feed import stock_json_convert, stock_sanity_check
from library.mailer import notify_error_mail
from library.marketplaces import region_of_country, get_store_identifier
from library.exceptions import AmazonFeedNotReadyError, AmazonThrottleError


def _out_of_range_email_body(out_of_range):
    lines = [
        f"- SKU {item['sku']} (EAN {item['ean']}): precio {item['price']} fuera de "
        f"[{item['min']}, {item['max']}]"
        for item in out_of_range
    ]
    return f"{len(out_of_range)} producto(s) con precio fuera de rango, NO publicados:\n\n" + "\n".join(lines)


async def _send_region_feed(client, stocks_cfg, account_name, store_name, region, url, guard):
    """Descarga el stock remoto de una región, construye el feed y lo envía.

    `guard` = (min_valid_ratio, guard_min_rows) para el sanity-check.
    Devuelve (region, feed_id) si el feed se envió, None en caso contrario.
    """
    info(f"Procesando stock {store_name} - {region} → {url}")

    df = await asyncio.to_thread(read_remote_file, url)
    info(f"  ✔ {len(df)} filas cargadas para {region}")

    seller_id = stocks_cfg.get_seller_id(account_name, region_of_country(region))

    src_feed, out_of_range = await asyncio.to_thread(stock_json_convert, df, region, seller_id)

    if out_of_range:
        # ANTES de mirar `messages`: si TODOS los SKU caen fuera de rango, el
        # feed queda vacío y se sale más abajo — el aviso no puede depender
        # de que sobrevivan mensajes.
        await asyncio.to_thread(
            notify_error_mail,
            f"Precios fuera de rango: {account_name} -- {region}",
            _out_of_range_email_body(out_of_range),
        )

    messages = src_feed.get("messages", []) if src_feed else []
    if not messages:
        error(f"No hay SKUs válidos para {region} en {store_name}.", type="warning")
        return None

    # Sanity-guard: NO publicar al catálogo vivo si una fracción excesiva de
    # filas no produjo SKU válido (fichero remoto corrupto/truncado).
    min_ratio, min_rows = guard
    ok, reason = stock_sanity_check(len(df), len(messages), min_ratio, min_rows)
    if not ok:
        msg = f"⛔ Stock guard {store_name}/{region}: {reason} — feed NO enviado."
        error(msg)
        await asyncio.to_thread(notify_error_mail, f"Stock guard {account_name} -- {region}", msg)
        return None

    feed_data = json.dumps(src_feed, separators=(', ', ': '), ensure_ascii=False)

    # Sin gzip: el cuerpo es JSON plano. La especificación de createFeedDocument
    # (2021-06-30) solo acepta contentType; la subida exige que el Content-Type
    # coincida y NO contempla Content-Encoding. Antes se declaraba gzip en ambos
    # lados (campo ignorado por Amazon + cabecera Content-Encoding sobre un
    # cuerpo NO comprimido), lo que como mucho hacía fallar el procesado del
    # feed. El feed es pequeño; comprimir no aporta. Content-Type idéntico en
    # create y put, como pide el contrato.
    feed_doc = await client.create_feed_document(content_type="application/json")
    status_code = await client.s3_put(feed_doc.url, feed_data, "application/json")
    if status_code != 200:
        error(f"No se pudo subir el feed de {region} a S3 (HTTP {status_code})")
        return None

    try:
        feed_result = await client.send_feed(get_store_identifier(region), feed_doc.feedDocumentId)
    except Exception as e:
        error(f"No se pudo enviar el feed para {region}: {e}")
        return None

    await asyncio.to_thread(archive_sent_stock_tsv, df, account_name, region, "stock_results")
    return region, feed_result.feedId


async def _verify_feed(client, account_name, region, feed_id, polling_cfg):
    info(f"🔍 Comprobando feed {feed_id} para {region}...")
    try:
        result = await client.get_feed_status(feed_id)
        info(f"✅ Feed {feed_id} completado: {result.processingStatus}")

        if not result.resultFeedDocumentId:
            error(f"⚠️ Feed {feed_id} terminó sin documento de resultado ({result.processingStatus})", type="warning")
            return

        try:
            # Descarga + gunzip según compressionAlgorithm, centralizado en el
            # cliente (misma lógica que trackings y reports).
            text = await client.download_feed_result_content(result.resultFeedDocumentId)
            data = json.loads(text)
            issues = data.get("issues", [])
            if issues:
                await asyncio.to_thread(
                    notify_error_mail,
                    f"Errores en {account_name} -- {region}",
                    json.dumps(issues, indent=2, ensure_ascii=False),
                )
            await asyncio.to_thread(save_stock_result, data, account_name, region, "stock_results")
        except Exception as e:
            error(f"⚠️ Error procesando resultado del feed {feed_id}: {e}")

    except AmazonFeedNotReadyError:
        error(f"❌ Feed {feed_id} no completado tras {polling_cfg.get_max_attempts('feeds')} intentos.")
    except AmazonThrottleError as e:
        error(f"❌ Feed {feed_id} throttled: {e}")


async def process_account(clients, account_name, account_info, ctx):
    stocks_cfg = StockConfig("config")
    stocks_data = stocks_cfg.get_all_stocks()

    common = CommonConfig("config")
    guard = (common.get_stock_min_valid_ratio(), common.get_stock_guard_min_rows())

    info(f"Procesando cuenta '{account_name}'")

    for market in clients.markets:
        set_log_context(f"{account_name}/{market}")
        store_name = account_name.lower()
        store_stocks = stocks_data.get(store_name)
        if not store_stocks:
            error(f"No hay stocks configurados para '{store_name}'", type="warning")
            continue

        client = clients.client(market)
        feeds_sends = []

        for region_key, url in store_stocks.items():
            if not region_key.lower().startswith("stock"):
                continue

            region = region_key.replace("stock", "").upper()

            # Filtrar ANTES de descargar: este mercado solo procesa sus regiones.
            if region_of_country(region) != market.upper():
                continue

            try:
                sent = await _send_region_feed(client, stocks_cfg, account_name, store_name, region, url, guard)
                if sent:
                    feeds_sends.append(sent)
            except Exception as e:
                error(f"  ✖ Error procesando {region} para {store_name}: {e}")

        for region, feed_id in feeds_sends:
            await _verify_feed(client, account_name, region, feed_id, ctx.polling_cfg)


def main():
    run_module_sync("stock", process_account)
    info("🏁 Stock synchronization finished.")


if __name__ == "__main__":
    main()
