"""Construcción del feed JSON_LISTINGS_FEED de stock/precios.

Descompone el god-method `stock_json_convert` (~120 líneas que mezclaban
parseo del DataFrame, validación, la regla de negocio de rangos de precio y
el formato del feed) en pasos con una responsabilidad cada uno.

Pase 3 — cambio de semántica DELIBERADO en handling-time: antes un
handling-time vacío o no numérico descartaba el patch de stock COMPLETO
(ValueError silencioso), es decir, una columna ausente en el fichero del
proveedor dejaba TODO el catálogo sin actualizar stock sin un solo aviso.
Ahora quantity se parsea por separado y un handling-time inválido degrada a
0 días con warning. Los golden tests de tests/test_transforms.py fijan la
nueva semántica. La regla de min/max de precio se mantiene: min/max no
numérico sigue descartando el patch de precio entero (publicar «sin mínimo»
podría romper el suelo de precio del vendedor).

Regla de negocio conservada: si el precio cae fuera de [min, max], el
producto NO se publica en absoluto (ni siquiera su stock).

Pase 3b (a petición del operador): `stock_json_convert` ahora también
devuelve la lista de SKU excluidos por rango de precio, para que el llamador
(stock.py) pueda avisar por correo — antes solo quedaba un warning en el log,
fácil de pasar por alto salvo que el sanity-guard bloqueara el feed entero.

Pase 3c — BUG CONFIRMADO en producción (cuentas vietaprecios/vietapreciosfba):
el TSV publicado desde Google Sheets en español exporta los decimales con
COMA ('41,98', '399,00'), no con punto. `float('41,98')` lanza ValueError;
como ese error se capturaba igual que un dato ausente, TODAS las filas de
esas hojas perdían precio Y cantidad a la vez ('sin precio ni stock —
omitido') sin que hubiera ningún problema real de datos. `_parse_locale_number`
centraliza el parseo de precio/min/max/quantity/handling-time para aceptar
coma decimal, punto decimal, y ambos separadores combinados (formato europeo
1.234,56 o estadounidense 1,234.56).
"""

from __future__ import annotations

import pandas as pd

from library.marketplaces import currency, locale_of_country


def _parse_locale_number(raw: str) -> float:
    """Convierte a float un número que puede venir en cualquiera de estos
    formatos: '41.98' (punto decimal), '41,98' (coma decimal — el real
    exportado por Google Sheets en español), '1.234,56' (miles con punto,
    decimal con coma) o '1,234.56' (miles con coma, decimal con punto).

    Si aparecen los dos separadores, el que va MÁS A LA DERECHA es el
    decimal; el otro se trata como separador de miles y se descarta. Si
    aparece solo uno de los dos, se asume que es el decimal (nunca hemos
    visto separador de miles solo, sin parte decimal, en los ficheros reales
    de este proyecto — asumirlo sería más arriesgado que útil).
    """
    s = raw.strip()
    if "," in s and "." in s:
        if s.rindex(",") > s.rindex("."):
            s = s.replace(".", "").replace(",", ".")   # '1.234,56' -> '1234.56'
        else:
            s = s.replace(",", "")                      # '1,234.56' -> '1234.56'
    elif "," in s:
        s = s.replace(",", ".")                          # '41,98' -> '41.98'
    return float(s)

# Defaults del sanity-guard del stock (configurables en common.ini).
DEFAULT_MIN_VALID_RATIO = 0.5   # < 50% de filas con SKU válido => sospechoso
DEFAULT_GUARD_MIN_ROWS = 10     # no aplicar el guard a feeds diminutos


def stock_sanity_check(n_in: int, n_msg: int, min_ratio: float, min_rows: int):
    """¿Es seguro publicar este feed al catálogo vivo?

    Protege contra un fichero remoto corrupto/truncado que dejaría la mayoría
    de SKU sin mensaje válido (p.ej. caída masiva de stock por un CSV a medio
    descargar). Devuelve (ok: bool, reason: str).

    - Feeds pequeños (< min_rows) se dejan pasar: el ratio no es fiable ahí.
    - Si la fracción de filas que produjo mensaje válido cae por debajo de
      min_ratio, se considera NO seguro.
    """
    if n_in < min_rows:
        return True, ""
    ratio = (n_msg / n_in) if n_in else 0.0
    if ratio < min_ratio:
        return False, (
            f"solo {n_msg}/{n_in} SKU válidos ({ratio:.0%} < {min_ratio:.0%} mínimo); "
            f"posible fichero de stock corrupto/incompleto"
        )
    return True, ""


def _fulfillment_patch(row, sku="?") -> dict | None:
    """Patch de stock (quantity + handling time), o None si no aplica.

    quantity y handling-time se parsean POR SEPARADO: un handling-time vacío
    («» no es NaN: float('') lanzaba ValueError) o basura ya no arrastra
    consigo un quantity perfectamente válido — degrada a 0 días con warning.
    """
    quantity_raw = row.get("quantity", "")
    try:
        if pd.isna(quantity_raw):
            return None
        quantity = int(_parse_locale_number(str(quantity_raw)))
    except ValueError:
        return None

    days = 0
    days_raw = row.get("handling-time", "")
    if pd.notna(days_raw) and str(days_raw).strip():
        try:
            days = int(_parse_locale_number(str(days_raw)))
        except ValueError:
            from library.logging_helpers import error
            error(
                f"⚠️ SKU {sku}: handling-time inválido ('{days_raw}') — se publica con 0 días",
                type="warning",
            )
    return {
        "op": "replace",
        "path": "/attributes/fulfillment_availability",
        "value": [
            {
                "fulfillment_channel_code": "DEFAULT",
                "quantity": quantity,
                "lead_time_to_ship_max_days": days,
            }
        ],
    }


def _price_patch(row, region) -> tuple[dict | None, dict | None]:
    """Patch de precio. Devuelve (patch | None, info_fuera_de_rango | None).

    `info_fuera_de_rango` solo es distinto de None cuando el precio es
    numéricamente válido pero cae fuera de [min, max] (para poder reportarlo
    con los valores reales); un min/max NO numérico sigue descartando el
    patch de precio en silencio (semántica heredada, sin cambios)."""
    price_raw = row.get("Price", "")
    min_raw = row.get("minimum-seller-allowed-price", None)
    max_raw = row.get("maximum-seller-allowed-price", None)

    try:
        if pd.isna(price_raw) or not str(price_raw).strip():
            return None, None
        price_val = round(_parse_locale_number(str(price_raw)), 2)

        min_val = None
        if pd.notna(min_raw) and str(min_raw).strip():
            min_val = round(_parse_locale_number(str(min_raw)), 2)

        max_val = None
        if pd.notna(max_raw) and str(max_raw).strip():
            max_val = round(_parse_locale_number(str(max_raw)), 2)
    except ValueError:
        return None, None

    if (min_val is not None and price_val < min_val) or \
       (max_val is not None and price_val > max_val):
        return None, {"price": price_val, "min": min_val, "max": max_val}

    patch_value = {
        "currency": currency(region),
        "our_price": [{"schedule": [{"value_with_tax": price_val}]}],
    }
    if min_val is not None:
        patch_value["minimum_seller_allowed_price"] = [{"schedule": [{"value_with_tax": min_val}]}]
    if max_val is not None:
        patch_value["maximum_seller_allowed_price"] = [{"schedule": [{"value_with_tax": max_val}]}]

    return {
        "op": "replace",
        "path": "/attributes/purchasable_offer",
        "value": [patch_value],
    }, None


def stock_json_convert(dataframe, region, seller_id):
    """Devuelve (feed, out_of_range): `feed` es el JSON_LISTINGS_FEED listo
    para enviar; `out_of_range` es la lista de SKU omitidos por precio fuera
    de [min, max] (uno de estos dicts por SKU: sku, ean, price, min, max),
    para que el llamador pueda avisar por correo con las cifras reales."""
    from library.logging_helpers import error

    feed = {
        "header": {
            "sellerId": seller_id,
            "version": "2.0",
            "issueLocale": locale_of_country(region),
        },
        "messages": [],
    }
    out_of_range = []

    # to_dict('records') en vez de iterrows(): misma semántica de row.get(),
    # sin boxing de una Series por fila (~5-10x en la conversión) y sin la
    # dependencia oculta de que el índice sea RangeIndex para messageId.
    for index, row in enumerate(dataframe.to_dict("records")):
        ean = str(row.get("EAN", row.get("ean", f"fila {index + 1}"))).strip()

        raw_sku = row.get("sku", "")
        if pd.isna(raw_sku) or str(raw_sku).strip().lower() == "nan" or not str(raw_sku).strip():
            error(f"⚠️ Fila {index + 1} (EAN: {ean}) sin SKU — omitida", type="warning")
            continue
        sku = str(raw_sku).strip()

        patches = []
        fulfillment = _fulfillment_patch(row, sku=sku)
        if fulfillment:
            patches.append(fulfillment)

        price, range_info = _price_patch(row, region)
        if range_info is not None:
            # Precio fuera de rango => no publicar este producto en absoluto.
            error(
                f"⚠️ SKU {sku} (EAN: {ean}) precio {range_info['price']} fuera de rango "
                f"[{range_info['min']}, {range_info['max']}] — producto omitido",
                type="warning",
            )
            out_of_range.append({"sku": sku, "ean": ean, **range_info})
            continue
        if price:
            patches.append(price)

        if not patches:
            error(f"⚠️ SKU {sku} (EAN: {ean}) sin precio ni stock — omitido", type="warning")
            continue

        feed["messages"].append({
            "messageId": index + 1,
            "sku": sku,
            "operationType": "PATCH",
            "productType": row.get("product-type", "PRODUCT"),
            "patches": patches,
        })

    return feed, out_of_range
