# El import ansioso `from .Auth import Auth` se eliminó: era la raíz del import
# circular (classes -> Auth -> classes.config -> DataTransformer -> ...). La
# autenticación vive ahora en library.auth_provider.AsyncTokenProvider.
