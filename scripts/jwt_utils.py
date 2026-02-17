import jwt
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from dataclass import JWTToken, JWTHeader, JWTClaims


def decode_jwt_unverified(token: str) -> JWTToken:
    """
    Декодирует JWT токен без проверки подписи

    Args:
        token: JWT токен в виде строки

    Returns:
        JWTToken с информацией о токене
    """
    decoded = jwt.decode(token, options={"verify_signature": False})
    header_data = jwt.get_unverified_header(token)

    header = JWTHeader(
        kid=header_data.get('kid'),
        typ=header_data.get('typ'),
        alg=header_data.get('alg')
    )

    claims = JWTClaims(
        sub=decoded.get('sub'),
        aud=decoded.get('aud'),
        iss=decoded.get('iss'),
        exp=decoded.get('exp'),
        iat=decoded.get('iat'),
        jti=decoded.get('jti'),
        scope_services=decoded.get('scope_services'),
        scope_claims=decoded.get('scope_claims')
    )

    return JWTToken(
        token=token,
        header=header,
        claims=claims,
        is_signature_valid=False
    )


def verify_jwt_with_certificate(token: str) -> JWTToken:
    """
    Проверяет JWT токен с использованием сертификата

    Args:
        token: JWT токен в виде строки

    Returns:
        JWTToken с информацией о токене и результатом проверки подписи
    """
    with open("cert.cer", "rb") as cert_file:
        cert_data = cert_file.read()

    try:
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    except ValueError:
        cert = x509.load_der_x509_certificate(cert_data, default_backend())

    public_key = cert.public_key()

    decoded = jwt.decode(
        token,
        public_key,
        algorithms=['RS256'],
        options={"verify_signature": True}
    )

    header_data = jwt.get_unverified_header(token)

    header = JWTHeader(
        kid=header_data.get('kid'),
        typ=header_data.get('typ'),
        alg=header_data.get('alg')
    )

    claims = JWTClaims(
        sub=decoded.get('sub'),
        aud=decoded.get('aud'),
        iss=decoded.get('iss'),
        exp=decoded.get('exp'),
        iat=decoded.get('iat'),
        jti=decoded.get('jti'),
        scope_services=decoded.get('scope_services'),
        scope_claims=decoded.get('scope_claims')
    )

    return JWTToken(
        token=token,
        header=header,
        claims=claims,
        is_signature_valid=True
    )
