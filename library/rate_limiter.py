"""Async rate limiter for the Amazon SP-API (token-bucket per region:endpoint).

Reemplaza a classes.RateLimiter.AmazonRateLimiter, cuyo `wait()` leía la
marca de tiempo del diccionario equivocado (`_rates` en lugar de `_last_call`),
de modo que `wait_for` siempre salía negativo y NUNCA dormía: el rate limiting
era un no-op silencioso.

Modelo: por clave `region:endpoint` mantenemos un cubo de fichas que se rellena
a `rate` fichas/seg (valor que Amazon devuelve en `x-amzn-RateLimit-Limit`) hasta
una capacidad `burst`. `wait()` consume una ficha y, si no hay, duerme lo justo
para que se genere. La reserva temporal se calcula bajo el lock y el `sleep` se
hace fuera del lock, de forma que varias corrutinas concurrentes se serializan
correctamente sin bloquear el event loop.
"""

from __future__ import annotations

import asyncio
import time


class AsyncTokenBucket:
    def __init__(self, default_rate: float | None = None, default_burst: float | None = None,
                 seed: dict[str, tuple[float, float]] | None = None):
        # Si no conocemos el rate de una clave (aún no hemos visto la cabecera),
        # usamos primero el `seed` (cuotas oficiales por endpoint, pase 3) y
        # después default_rate. None => no limitar (passthrough), igual que el
        # comportamiento original cuando no había rate.
        #
        # `seed`: {endpoint: (rate, burst)}. Antes del primer respuesta de
        # Amazon el limiter era un no-op y la primera oleada paralela podía
        # estrellarse en 429; con el seed arranca ya dentro de cuota. La
        # cabecera x-amzn-RateLimit-Limit sigue teniendo la última palabra.
        self._default_rate = default_rate
        self._default_burst = default_burst
        self._seed = dict(seed or {})
        self._rates: dict[str, float] = {}
        self._capacity: dict[str, float] = {}
        self._tokens: dict[str, float] = {}
        self._last: dict[str, float] = {}
        self._lock = asyncio.Lock()

    def _seeded(self, endpoint: str) -> tuple[float | None, float | None]:
        pair = self._seed.get(endpoint)
        return pair if pair else (None, None)

    def _key(self, region: str, endpoint: str) -> str:
        return f"{region}:{endpoint}"

    def update(self, region: str, endpoint: str, headers) -> None:
        """Actualiza el rate desde la cabecera de respuesta de Amazon.

        Es síncrono y hace asignaciones atómicas de dict (seguras bajo el GIL).
        Una lectura levemente desactualizada en `wait()` es inocua.
        """
        raw = headers.get("x-amzn-RateLimit-Limit")
        if raw is None:
            return
        try:
            rate = float(raw)
        except (TypeError, ValueError):
            return
        if rate <= 0:
            return
        key = self._key(region, endpoint)
        self._rates[key] = rate
        # Capacidad: burst del seed si lo hay; si no, ~1s de ráfaga (o burst explícito).
        seed_burst = self._seeded(endpoint)[1]
        self._capacity.setdefault(key, seed_burst or self._default_burst or max(rate, 1.0))

    async def wait(self, region: str, endpoint: str) -> None:
        key = self._key(region, endpoint)
        sleep_for = 0.0
        async with self._lock:
            rate = self._rates.get(key)
            seed_rate, seed_burst = self._seeded(endpoint)
            if rate is None:
                rate = seed_rate if seed_rate is not None else self._default_rate
            if not rate or rate <= 0:
                return  # rate desconocido => no limitamos
            capacity = self._capacity.get(key) or seed_burst or (self._default_burst or max(rate, 1.0))
            now = time.monotonic()
            last = self._last.get(key, now)
            tokens = self._tokens.get(key, capacity)
            # Rellenar según el tiempo transcurrido.
            tokens = min(capacity, tokens + (now - last) * rate)
            if tokens >= 1.0:
                tokens -= 1.0
                self._last[key] = now
            else:
                # Reservar el instante futuro en el que habrá 1 ficha.
                sleep_for = (1.0 - tokens) / rate
                tokens = 0.0
                self._last[key] = now + sleep_for
            self._tokens[key] = tokens
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)
