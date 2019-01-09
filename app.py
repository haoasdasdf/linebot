
import logging
import os
import os.path

import dotenv
from flask import Flask, abort, request
from flask_ngrok import run_with_ngrok
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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

@app.route("/")
def hello_world():
	return "hello world!"

@app.route("/webhook", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	logger.debug("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    except:
        logger.error('reply token error')

if __name__ == "__main__":
	app.run()
