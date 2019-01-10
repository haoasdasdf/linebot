
import logging
import os
import os.path

import dotenv
from flask import Flask, abort, request
from flask_ngrok import run_with_ngrok
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationMessage
from fire_db import DBAPI
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
# run_with_ngrok(app)

line_bot_api = LineBotApi(os.environ.get('LINE_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
logger.debug('*' * 20)
logger.debug(os.environ.get('LINE_ACCESS_TOKEN'))
logger.debug(os.environ.get('LINE_CHANNEL_SECRET'))

@app.route('/')
def hello_world():
    return 'hello world!'

@app.route('/line/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    logger.debug('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        
        logger.info(event.reply_token)
        if(event.reply_token != '00000000000000000000000000000000'):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
        else:
            logger.info('A webhook test')

            dummy_data = {
                'user_id': 'U816d9966f1e0af6c123cdb3a6522b7c4',
                'latitude': 35.691455,
                'longitude': 139.767683,
                'address': 'Japan, 〒101-0047 Tōkyō-to, Chiyoda-ku, Uchikanda, 2 Chome−12−５ 内山ビル'

            }
            fire = DBAPI()
            fire.add_user(dummy_data)
    except:
        logger.error('reply error')

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    logger.info('token: {0}'.format(event.reply_token))
    try:
        data = {}
        data['latitude'] = event.message.latitude
        data['longitude'] = event.message.longitude
        data['user_id'] = event.source.user_id
        data['address'] = event.message.address
        logger.info(data)
        fire = DBAPI()
        result = fire.add_user(data)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

    except Exception as e:
        logger.error('error')
        logger.error(e)


if __name__ == '__main__':
    app.run()
