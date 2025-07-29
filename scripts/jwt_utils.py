import jwt
from typing import Optional
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import requests

from dataclass import JWTToken, JWTHeader, JWTClaims


def decode_jwt_unverified(token: str) -> JWTToken:
    """
    Декодирует JWT токен без проверки подписи
    
    Args:
        token: JWT токен в виде строки
        
    Returns:
        JWTToken с информацией о токене
    """
    # Декодируем токен без проверки подписи
    decoded = jwt.decode(token, options={"verify_signature": False})
    header_data = jwt.get_unverified_header(token)

    # Создаем объекты
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
        cert_path: Путь к сертификату для проверки подписи
        
    Returns:
        JWTToken с информацией о токене и результатом проверки подписи
    """
    # Загружаем сертификат
    with open("cert.cer", "rb") as cert_file:
        cert_data = cert_file.read()

    # Парсим сертификат (поддерживаем оба формата)
    try:
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    except:
        cert = x509.load_der_x509_certificate(cert_data, default_backend())

    # Получаем публичный ключ
    public_key = cert.public_key()

    # Декодируем с проверкой подписи
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=['RS256'],
        options={"verify_signature": True}
    )

    header_data = jwt.get_unverified_header(token)

    # Создаем объекты
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


def verify_jwt_with_jwks(token: str, issuer_url: str) -> JWTToken:
    """
    Проверяет JWT токен с использованием JWKS (JSON Web Key Set)
    
    Args:
        token: JWT токен в виде строки
        issuer_url: URL издателя токена
        
    Returns:
        JWTToken с информацией о токене и результатом проверки подписи
    """
    try:
        # Получаем заголовок токена для извлечения kid
        header_data = jwt.get_unverified_header(token)
        kid = header_data.get('kid')
        
        if not kid:
            unverified = decode_jwt_unverified(token)
            unverified.verification_error = "No 'kid' in token header"
            return unverified
        
        # Получаем JWKS
        jwks_url = f"{issuer_url}/.well-known/jwks.json"
        response = requests.get(jwks_url)
        response.raise_for_status()
        
        jwks = response.json()
        
        # Ищем нужный ключ
        public_key = None
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                # Здесь нужно преобразовать JWK в PEM формат
                # Для простоты пока возвращаем неверифицированный токен
                break
        
        if not public_key:
            unverified = decode_jwt_unverified(token)
            unverified.verification_error = "Public key not found in JWKS"
            return unverified
        
        # Декодируем с проверкой подписи
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        
        # Создаем объекты
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
        
    except Exception as e:
        unverified = decode_jwt_unverified(token)
        unverified.verification_error = str(e)
        return unverified


def extract_sub_from_token(token: str) -> Optional[str]:
    """
    Быстрая функция для извлечения только значения sub из токена
    
    Args:
        token: JWT токен в виде строки
        
    Returns:
        Значение sub или None
    """
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get('sub')
    except:
        return None


def print_token_info(token_obj: JWTToken) -> None:
    """
    Выводит информацию о токене в удобном формате
    
    Args:
        token_obj: Объект JWTToken
    """
    print("=== JWT Token Information ===")
    print()
    
    print("Header:")
    print(f"  Algorithm: {token_obj.header.alg}")
    print(f"  Type: {token_obj.header.typ}")
    print(f"  Key ID: {token_obj.header.kid}")
    print()
    
    print("Claims:")
    if token_obj.claims.sub:
        print(f"  Subject (sub): {token_obj.claims.sub}")
    if token_obj.claims.aud:
        print(f"  Audience (aud): {token_obj.claims.aud}")
    if token_obj.claims.iss:
        print(f"  Issuer (iss): {token_obj.claims.iss}")
    if token_obj.claims.jti:
        print(f"  JWT ID (jti): {token_obj.claims.jti}")
    print()
    
    print("Timing:")
    if token_obj.claims.issued_at:
        print(f"  Issued at: {token_obj.claims.issued_at}")
    if token_obj.claims.expires_at:
        print(f"  Expires at: {token_obj.claims.expires_at}")
    if token_obj.claims.time_remaining is not None:
        if token_obj.claims.time_remaining > 0:
            print(f"  Time remaining: {token_obj.claims.time_remaining} seconds")
        else:
            print("  ⚠️  Token has expired!")
    print()
    
    if token_obj.claims.scope_services:
        print("Permissions:")
        print(f"  Scope services: {token_obj.claims.scope_services}")
    if token_obj.claims.scope_claims:
        print(f"  Scope claims: {token_obj.claims.scope_claims}")
    print()
    
    print("Verification:")
    if token_obj.is_signature_valid:
        print("  ✅ Signature verified")
    else:
        print("  ⚠️  Signature not verified")
        if token_obj.verification_error:
            print(f"  Error: {token_obj.verification_error}")
    print()
