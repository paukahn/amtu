class AmazonAPIError(Exception):
    """Errores generales de la API.

    `status_code`/`body` permiten a los llamadores decidir por tipo de fallo
    (p.ej. orders solo cambia de reportType ante un 400, no ante cualquier
    error transitorio).

    `request_id` (pase 3f): el `x-amzn-RequestId` que la SP-API devuelve en
    CADA respuesta, éxito o error (documentado en
    developer-docs.amazon.com/sp-api/docs/response-format). Es el primer dato
    que pide el soporte de Amazon para investigar un caso — y errores como
    'InvalidInput: Invalid request parameters' con `details` vacío (confirmado:
    un fallo conocido y sin causa clara del lado de Amazon, reportado por
    terceros en distintos tipos de feed a lo largo de varios años) solo se
    pueden escalar con este identificador. Antes se descartaba junto al resto
    de cabeceras de la respuesta.
    """

    def __init__(self, message, status_code=None, body=None, request_id=None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.request_id = request_id


class AmazonThrottleError(AmazonAPIError):
    """Error 429 / Quota Exceeded"""
    pass


class AmazonServerError(AmazonAPIError):
    """Error 5xx de la SP-API (transitorio: se reintenta en el transporte)"""
    pass


class AmazonFeedNotReadyError(AmazonAPIError):
    """Feed processing (IN_QUEUE / IN_PROGRESS)"""
    pass


class AmazonReportNotReadyError(AmazonAPIError):
    """Report processing (IN_QUEUE / IN_PROGRESS)"""
    pass


class AmazonAuthError(AmazonAPIError):
    """Error 401 (Unauthorized)"""
    pass
