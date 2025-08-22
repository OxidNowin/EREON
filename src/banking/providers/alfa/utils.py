import ssl

from core.config import settings


def get_ssl_context() -> ssl.SSLContext | None:
    if not settings.alfa_tsl_enable:
        return None

    ssl_context = ssl.create_default_context()
    ssl_context.load_cert_chain(
        certfile=settings.alfa_tsl_cert_path,
        keyfile=settings.alfa_tsl_private_key_path
    )
    return ssl_context


ssl_context = get_ssl_context()
