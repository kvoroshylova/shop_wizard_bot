from pprint import pprint
import requests
from tg_bot import app
from flask import request, jsonify
from .handlers import MessageHandler, CallBackHandler


@app.route('/', methods=["POST"])
def hello():
    if message := request.json.get('message'):
        handler = MessageHandler(message)
    elif callback := request.json.get('callback_query'):
        handler = CallBackHandler(callback)
    handler.handle()
    return 'ok', 200

