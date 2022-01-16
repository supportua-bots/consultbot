from flask import Flask, request, Response, json, jsonify
from multiprocessing import Process
# from telegrambot import main as tgbot
from jivochat import main as jivo
from vibertelebot import main as vbbot
from db_func.database import create_table
from loguru import logger
from payment.generator import get_response_data
from payment.handler import main as sender
from tasks.task import task_checker as taskfunel
from telegrambot import main as tgbot


app = Flask(__name__)


@app.route('/jivochatgram', methods=['GET', 'POST'])
def jivochat_endpoint_telegram():
    source = 'telegram'
    data = request.get_json()
    print(data)
    returned_data = jivo.main(data, source)
    response = app.response_class(
        response=json.dumps(returned_data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/jivochatviber', methods=['GET', 'POST'])
def jivochat_endpoint_viber():
    source = 'viber'
    data = request.get_json()
    print(data)
    returned_data = jivo.main(data, source)
    response = app.response_class(
        response=json.dumps(returned_data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/payment', methods=['POST'])
def payment_endpoint():
    raw_data = request.get_data()
    data = json.loads(raw_data.decode())
    logger.info(data)
    sender(data)
    returned_data = get_response_data(data)
    response = app.response_class(
        response=json.dumps(returned_data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/liqpay', methods=['POST'])
def liqpay_endpoint():
    raw_data = request.get_data()
    logger.info(raw_data)
    data = json.loads(raw_data.decode())
    logger.info(data)
    # sender(data)
    # returned_data = get_response_data(data)
    response = app.response_class(
        response={'result': 'ok'},
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/viber', methods=['POST'])
def viber_endpoint():
    source = 'viber'
    vbbot.main(request)
    return Response(status=200)


def server_launch():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    # flask_server = Process(target=server_launch).start()
    # telegram_bot = Process(target=tgbot.main).start()
    create_table()
    try:
        background_process = Process(target=taskfunel).start()
        flask_server = Process(target=server_launch).start()
        telegram_bot = Process(target=tgbot.main).start()
    except KeyboardInterrupt:
        flask_server.terminate()
        telegram_bot.terminate()
        background_process.terminate()
        flask_server.join()
        telegram_bot.join()
        background_process.join()
