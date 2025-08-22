import ssl

from core.config import settings


def get_ssl_context() -> ssl.SSLContext | None:
    ssl_context = ssl.create_default_context()
    ssl_context.load_cert_chain(
        certfile=settings.alfa_tls_cert_path,
        keyfile=settings.alfa_tls_private_key_path
    )
    if not settings.alfa_tls_enable:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


ssl_context = get_ssl_context()
