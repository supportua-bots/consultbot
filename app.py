from flask import Flask, request, Response, json, jsonify
from multiprocessing import Process
# from telegrambot import main as tgbot
from jivochat import main as jivo
from vibertelebot import main as vbbot
from db_func.database import create_table
from loguru import logger


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
        flask_server = Process(target=server_launch).start()
        # telegram_bot = Process(target=tgbot.main).start()
    except KeyboardInterrupt:
        flask_server.terminate()
        # telegram_bot.terminate()
        flask_server.join()
        # telegram_bot.join()
