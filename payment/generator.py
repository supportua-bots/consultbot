import os
import hashlib
import urllib
import requests
import hmac
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from payment.settings import product_name, product_price, merchant_account, merchant_domain


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

URL = 'https://api.wayforpay.com/api'
secretkey = os.getenv('SECRET_KEY_WAYFORPAY')


def get_payment_link(product_count, chat_id, platform):
    order_date = int(datetime.today().timestamp())
    amount = int(product_price) * int(product_count)
    order_reference = f'{chat_id}%%{str(order_date)}%%{platform}'
    signature_data = [merchant_account,
                      merchant_domain,
                      order_reference,
                      order_date,
                      amount,
                      "UAH",
                      product_name,
                      product_count,
                      product_price]

    message = ';'.join(str(e) for e in signature_data)
    signature = hmac.new(secretkey.encode(), message.encode(),
                         hashlib.md5).hexdigest()
    request_data = {
                     "transactionType": "CREATE_INVOICE",
                     "merchantAccount": merchant_account,
                     "merchantDomainName": merchant_domain,
                     "merchantSignature": signature,
                     "orderReference": order_reference,
                     "apiVersion": 1,
                     "orderDate": order_date,
                     "amount": amount,
                     "currency": "UAH",
                     "productName": [product_name],
                     "productCount": [product_count],
                     "productPrice": [product_price],
                     "clientFirstName": chat_id,
                     "clientLastName": platform
                    }
    x = requests.post(URL, json=request_data)
    # x = urllib.parse.urlencode(request_data).encode()
    # req = urllib.request.Request(URL, data=x)
    # resp = urllib.request.urlopen(req)
    # link = urllib.request.urlopen(URL, data=request_data).geturl()
    return x.json()["invoiceUrl"]


def get_response_data(data):
    order_time = int(datetime.now().timestamp())
    order_reference = data["orderReference"]
    signature_data = [order_reference,
                      "accept",
                      order_time]
    message = ';'.join(str(e) for e in signature_data)
    signature = hmac.new(secretkey.encode(), message.encode(),
                         hashlib.md5).hexdigest()
    request_data = {
                     "orderReference": order_reference,
                     "status": "accept",
                     "time": order_time,
                     "signature": signature}
    return request_data
