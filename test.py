import requests

URL = 'https://api.wayforpay.com/api'

request_data = {"transactionType": "P2P_CREDIT",
                "merchantAccount": "p2p_credit",
                "merchantAuthType": "SimpleSignature",
                "merchantSignature": "flk3409refn54t54t*FNJRET",
                "apiVersion": 1,
                "orderReference": "myOrder1",
                "amount": 1.13,
                "currency": "UAH",
                "cardBeneficiary": "5375414102723888"}
x = requests.post(URL, json=request_data)
print(x.text)
print(x.json())
