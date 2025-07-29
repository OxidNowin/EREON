# Первые приготовления
1) Необходимо создать .env по примеру
```bash
    cp .env.example .env
```
Заполните ее информацией

2) Создайте папку certs
```bash
    mkdir certs
```

3) Скопируйте туда сертификаты полученный от АльфаБанка
4) Туда же поместите данный [сертификат](https://developers.alfabank.ru/assets/developers-portal.docs.alfa-api/articles/alfa-id/articles/expansion/articles/signature-checking/files/cert.cer)
5) Далее необходимо запустить скрипт и пройти процедуру получения rsa сертификатов и приватного ключа
```bash
  python scripts/get_test_token.py
```