import json
import os
import sys
import textwrap
import urllib3
import subprocess
from pathlib import Path

from dotenv import load_dotenv
import requests

from jwt_utils import decode_jwt_unverified, JWTToken, verify_jwt_with_certificate
from dataclass import (
    ResponseIssueRsaCertificate,
    OperationResponse,
    RequestType,
    GetRequestResponse,
    RequestStatus,
    BaseGetRequestObject,
    ResponseActivationRsaCertificate,
)
from utils import from_dict

# Отключаем предупреждения о небезопасных SSL соединениях
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.makedirs("certs", exist_ok=True)

load_dotenv()

client_id = os.getenv("ALFA_CLIENT_ID")
client_secret = os.getenv("ALFA_CLIENT_SECRET")
base_url = os.getenv("ALFA_BASE_URL")

session = requests.Session()

def is_production() -> bool:
    if "baas" in base_url:
        return True
    elif "sandbox" in base_url:
        return False
    else:
        raise ValueError("Неверный base_url")

if is_production():
    # Используем комбинацию: открытый ключ + расшифрованный закрытый ключ + цепочка сертификатов УЦ
    session.cert = ("certs/sandbox_cert_2025.cer", "certs/sandbox_key_2025_decrypted.key")
    session.verify = True
else:
    # Используем комбинацию: открытый ключ + расшифрованный закрытый ключ + цепочка сертификатов УЦ
    session.cert = ("certs/sandbox_cert_2025.cer", "certs/sandbox_key_2025_decrypted.key") # Заменить на НЕтестовые сертификаты
    session.verify = False # Временно отключаем проверку SSL для тестового окружения


def get_client_secret() -> str:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/connection/articles/clientsecret/clientsecret
    :return: clientSecret
    """
    url = f"{base_url}/oidc/clients/{client_id}/client-secret"
    headers = {'Accept': 'application/json'}
    response = session.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")
    data = response.json()
    return data["clientSecret"]


def get_sandbox_acf_url() -> str:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/alfa-id/articles/acf/articles/get-auth-code/v1/get-auth-code
    :return: Вернет ссылку по которой нужно перейти в браузере
    """
    return "https://id-sandbox.alfabank.ru/oidc/authorize?"\
           "response_type=code&"\
           f"client_id={client_id}&"\
           "redirect_uri=http://localhost&"\
           "scope=signature&"\
           f"state=8f814df3-582c-4393-96d4-ca668f00d97d"


def get_prod_acf_url() -> str:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/alfa-id/articles/acf/articles/get-auth-code/v1/get-auth-code
    :return: Вернет ссылку по которой нужно перейти в браузере
    """
    return "https://id.alfabank.ru/oidc/authorize?"\
           "response_type=code&"\
           f"client_id={client_id}&"\
           "redirect_uri=http://localhost&"\
           "scope=signature&"\
           f"state=8f814df3-582c-4393-96d4-ca668f00d97d"


def get_acf_token(code: str) -> JWTToken:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/alfa-id/articles/acf/articles/get-access-token/v1/get-access-token
    :param code: код, полученный из `acf_url`
    :return: Декодированный Access-Token
    """

    url = f"{base_url}/oidc/token"
    payload = (
        'grant_type=authorization_code'
        f'&code={code}'
        f'&client_id={client_id}'
        f'&client_secret={client_secret}'
        '&redirect_uri=http://localhost'
    )
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = session.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")
    response.encoding = "utf-8"
    data = response.json()

    if is_production():
        func = verify_jwt_with_certificate
    else:
        func = decode_jwt_unverified
    return func(data['access_token'])


def get_dn(token: JWTToken) -> None:
    """
    Получаем готовый сгенерированный файл certs/dn.cnf
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/get-dn-file/v2/get-dn-file
    :param token: access token
    :return:
    """

    url = f"{base_url}/api/jp/v2/signature/users/{token.claims.sub}/dn/file"
    headers = {
        'Authorization': f'Bearer {token.token}',
        'Accept': 'text/plain'
    }
    response = session.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

    with open("certs/dn.cnf", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("Файл успешно сохранён: certs/dn.cnf")


def generate_private_key() -> str:
    """
    Выпуск RSA-сертификата, пункт 2
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/intro/intro
    :return: pkcs10Content одной строкой
    """

    if is_production():
        private_key_path = Path("certs/prod_private.key")
        csr_path = Path("certs/prod_csr.csr")
    else:
        private_key_path = Path("certs/sandbox_private.key")
        csr_path = Path("certs/sandbox_csr.csr")
    config_path = Path("certs/dn.cnf")

    # 1. Генерация закрытого ключа
    print("Генерируем закрытый ключ...")

    while True:
        key_password = input("Введите пароль для private_key (от 4 до 1024 символов)")
        if 4 <= len(key_password) <= 1024:
            break
        else:
            print("Неверная длина пароля!!!")

    subprocess.run(
        [
            "openssl", "genrsa",
            "-des3",
            f"-passout", f"pass:{key_password}",
            "-out", str(private_key_path),
            "2048"
        ],
        check=True
    )
    print(f"Закрытый ключ сгенерировался в {private_key_path}")

    # 2. Генерация запроса на сертификат (CSR)
    print("Создаём запрос на сертификат...")
    subprocess.run(
        [
            "openssl", "req",
            "-new",
            "-utf8",
            "-nameopt", "multiline,utf8",
            "-config", str(config_path),
            "-key", str(private_key_path),
            "-passin", f"pass:{key_password}",
            "-out", str(csr_path)
        ],
        check=True
    )
    print(f"Запрос на сертификат сохранен в {csr_path}")

    # 3. Чтение CSR-файла и преобразование в однострочную строку
    print("Читаем файл CSR и преобразуем в строку с \\n...")
    csr_text = csr_path.read_text(encoding="utf-8").strip()
    if not is_production():
        # https://developers.alfabank.ru/products/alfa-api/documentation/articles/sandbox/articles/check-signature/check-signature
        return "-----BEGIN CERTIFICATE REQUEST-----\nMIIC/DCCAeQCAQAwgacxJTAjBgkqhkiG9w0BCQEWFlVzZXI1MDRAcG9jaHRvY2hr\nYS5jb20xOzA5BgNVBAMMMtCa0YPQtNGA0Y/QstGG0LXQsiDQldGA0LzQvtC70LDQ\nuSDQmNCz0L7RgNC10LLQuNGHMQswCQYDVQQGEwJSVTEbMBkGA1UEBAwS0JrRg9C0\n0YDRj9Cy0YbQtdCyMRcwFQYDVQQqDA7QldGA0LzQvtC70LDQuTCCASIwDQYJKoZI\nhvcNAQEBBQADggEPADCCAQoCggEBANGTN2bX/kaOHuuEfMiOKg1f8y3SY1AseVjQ\nceoHKdaSeLoUIscPgEsuDsbtF6ezsZqV7bwyRYuJK+kMprczDWKiQNxmZPOafiKG\n5MKOcxysgX9LV+R8JhVoycfQqmSqfImQBcPZ6s9bqq6J8cs04FCzy+nhPYoFUs2l\nX+ZrFfLF135fO4LlRxfj4dfIbHZ4NVogiezIteBE3SPTtEeXiYj2c7SyB0Z17gbQ\ndTmtWIolrb5GTZ6SyjjcMZY3U2ZR+4eyn2l1MFt5F/K9Ke47zu4DYTF7zkitST11\nnr5gR64zjVZRtmrVqMU9iB7NmQ8/gS8YEsC3PTSECvqioSDHwNcCAwEAAaAPMA0G\nCSqGSIb3DQEJDjEAMA0GCSqGSIb3DQEBCwUAA4IBAQBazGrfYMfeUdJ7ofbQ5lom\nEsHO/cA312QUpyzFEsHbjYhy9OZTjiVXLfVExf8QrcRchi4/6IECp01S2Ed+nfMm\nE/MtD3rtE2oBtH6FjA9APtZb9NZuiSYCzl7nL3rd0ui+F32Dy/JNkudktn64jsMH\nYVt5u8Ik0dtxl0axa3E5RUkpJTTl7iIOWD+P8UkOOpa9EMPA2hrtrZvPr8xr60IS\nd2t4vKFcHIdgdI2Qe5ATvaYfbccLGjxdWm05lXVuxRjpEOXjuhc5mRkEj06bPavD\n9k7h/Tsz4Jb9gNKDZ3TEzfynQkDFFse8in6IDDkwPO21J6onTMd7KOP1gqMSYjrh\n-----END CERTIFICATE REQUEST-----"
    return csr_text.replace("\n", "\\n")


def issue_rsa(access_token: JWTToken, pkcs10_content: str) -> ResponseIssueRsaCertificate:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/issue-rsa/v2/issue-rsa
    :param access_token:
    :param pkcs10_content: Контент PKCS#10. Необходимо заменить переносы строк на \n
    :return: объект ответа от эндпоинта
    """

    url = f"{base_url}/api/jp/v2/signature/users/{access_token.claims.sub}/rsa-certificates/requests/issue"
    payload = json.dumps({"pkcs10Content": pkcs10_content})
    headers = {
        'Authorization': f'Bearer {access_token.token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = session.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

    return ResponseIssueRsaCertificate(**response.json())


def send_request(access_token: JWTToken, operation_id: str, request_type: RequestType) -> OperationResponse:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/send-request/v2/send-request
    :param access_token:
    :param operation_id: Идентификатор заявки, связанной с rsa сертификатами
    :param request_type: тип заявки
    :return: объект ответа от эндпоинта
    """
    url = f"{base_url}/api/jp/v2/signature/users/{access_token.claims.sub}/requests/{operation_id}/operations"
    payload = json.dumps({"requestType": request_type.value})
    headers = {
        'Authorization': f'Bearer {access_token.token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = session.post(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

    return OperationResponse(**response.json())


def sign_with_sms(access_token: JWTToken, operation_id: str, code: str) -> None:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/sign-with-sms/v2/sign-with-sms
    :param access_token:
    :param operation_id:Идентификатор заявки, связанной с rsa сертификатами
    :param code: код из смс
    :return:
    """
    url = f"{base_url}/api/jp/v2/signature/users/{access_token.claims.sub}/requests/operations/{operation_id}"
    payload = json.dumps({"code": code})
    headers = {
        'Authorization': f'Bearer {access_token.token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = session.put(url, headers=headers, data=payload)

    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

    data = response.json()
    if not data["isSigned"]:
        raise Exception(f"Заявка не подписана {__name__}: {response.status_code}\n{response.text}")


def get_request(access_token: JWTToken, operation_id: str, request_type: RequestType) -> GetRequestResponse:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/get-request/v2/get-request
    :param access_token:
    :param operation_id: айди заявки, по которой нужно получить статус
    :param request_type: тип заявки, которую нужно дождаться
    :return:
    """
    url = f"{base_url}/api/jp/v2/signature/users/{access_token.claims.sub}/rsa-certificates/requests/{operation_id}"
    headers = {
        'Authorization': f'Bearer {access_token.token}',
        'Accept': 'application/json'
    }

    while True:
        response = session.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

        data = from_dict(GetRequestResponse, response.json())

        request_data = getattr(data, request_type.value)
        if request_data is None:
            raise Exception(f"Ошибка в получении данных заявки")

        sorted_requests = sorted(request_data, key=lambda req: req.createdDate, reverse=True)
        # берем самую последнюю заявку по времени
        request: BaseGetRequestObject = sorted_requests[0]
        if request.status == RequestStatus.FAILED:
            raise Exception(f"Ошибка в идентификаторе заявок {request.id}")
        elif request.status == RequestStatus.FINISHED:
            print(f"Заявка {request.id} исполнена, сертификат выпущен")
            break
        elif request.status == RequestStatus.CREATED:
            print(f"Необходимо подписать заявку {request.id}")
        elif request.status == RequestStatus.SIGNED:
            print(f"Заявка {request.id} находится на подписании")
        elif request.status == RequestStatus.IN_PROGRESS:
            print(f"Заявка {request.id} находится на исполнении")

    return data


def get_rsa(access_token: JWTToken, issued_certificate_id: str) -> str:
    """
    https://developers.alfabank.ru/products/alfa-api/documentation/articles/signature/articles/get-rsa/v2/get-rsa
    :param access_token:
    :param issued_certificate_id:
    :return: serialNumber сертификата
    """
    url = f"{base_url}/api/jp/v2/signature/users/{access_token.claims.sub}/rsa-certificates/{issued_certificate_id}"
    headers = {
        'Authorization': f'Bearer {access_token.token}',
        'Accept': 'application/json',
    }

    response = session.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

    data = response.json()
    with open("certs/certificate.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    base64_cert = data["content"]

    # Шаг 2: декодируем экранированные символы (например, \\r\\n → \r\n)
    decoded_base64_cert = base64_cert.encode().decode('unicode_escape')

    # Шаг 3: удаляем перевод строки (если хотим сделать PEM вручную)
    raw_base64 = decoded_base64_cert.replace("\r", "").replace("\n", "")

    # Шаг 4: оборачиваем в PEM-структуру (с отступами по 64 символа)
    pem_lines = [
        "-----BEGIN CERTIFICATE-----",
        *textwrap.wrap(raw_base64, 64),
        "-----END CERTIFICATE-----"
    ]

    # Шаг 5: сохраняем в файл
    cer_name = "prod_private_key.pem" if is_production() else "sandbox_private_key.pem"
    with open(f"certs/{cer_name}", "w", encoding="utf-8") as f:
        f.write("\n".join(pem_lines))
    print(f"Сертификат был сохранен в certs/{cer_name}")
    print("Данные сертификата были сохранены в certs/certificate.json")
    return data["certificate"]["serialNumber"]


def activation_rsa(access_token: JWTToken, issued_certificate_id: str):
    url = f"{base_url}/api/jp/v2/signature/users/{access_token.claims.sub}/rsa-certificates/{issued_certificate_id}/requests/activation"
    headers = {
        'Authorization': f'Bearer {access_token.token}',
        'Accept': 'application/json'
    }

    response = session.post(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Ошибка в {__name__}: {response.status_code}\n{response.text}")

    return ResponseActivationRsaCertificate(**response.json())


if __name__ == '__main__':
    if not client_secret:
        client_secret = get_client_secret()
        print("Необходимо занести этот ключ в .env и заново запустить скрипт")
        print(client_secret)
        sys.exit()

    url = get_prod_acf_url() if is_production() else get_sandbox_acf_url()
    print(f"Необходимо перейти по ссылке, авторизоваться и ввести code из ссылки на которую редиректнет")
    print(url)
    code = input("Введите code")
    token = get_acf_token(code)
    # Выпуск RSA-сертификата
    # шаг 1
    get_dn(token)
    # шаг 2
    pkcs10_content = generate_private_key()
    # шаг 3
    response_issue_rsa = issue_rsa(access_token=token, pkcs10_content=pkcs10_content)
    # шаг 4
    issue_operation_response = send_request(
        access_token=token,
        operation_id=response_issue_rsa.id,
        request_type=RequestType.issueRsaCertificate
    )
    # шаг 5
    code = input("Введите код из смс")
    sign_with_sms(access_token=token, operation_id=issue_operation_response.id, code=code)
    # шаг 6
    request_issue_data = get_request(
        access_token=token,
        operation_id=response_issue_rsa.id,
        request_type=RequestType.issueRsaCertificate
    )
    # шаг 7
    rsa = get_rsa(
        access_token=token,
        issued_certificate_id=request_issue_data.requestIssueRsaCertificate[-1].results[-1].issuedCertificateId
    )

    # Активация способа подписи RSA-сертификатом
    # шаг 1
    response_activate_rsa = activation_rsa(
        access_token=token,
        issued_certificate_id=request_issue_data.requestIssueRsaCertificate[-1].results[-1].issuedCertificateId
    )
    # шаг 2
    activate_operation_response = send_request(
        access_token=token,
        operation_id=response_activate_rsa.id,
        request_type=RequestType.activationRsaCertificate
    )
    # шаг 3
    code = input("Введите код из смс")
    sign_with_sms(access_token=token, operation_id=activate_operation_response.id, code=code)
    print("СМС принята! Проверяем статус заявки пока он не перешел с статус FINISHED")
    # шаг 4
    activate_issue_data = get_request(
        access_token=token,
        operation_id=response_issue_rsa.id,
        request_type=RequestType.issueRsaCertificate
    )
    print("Успешно завершено!")
