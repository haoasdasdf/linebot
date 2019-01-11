
import logging
import os

import dotenv
from flask import Flask, Response, abort, request
# from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (LocationMessage, MessageEvent, TextMessage,
	TextSendMessage)

from actions import Actions
from fire_db import DBAPI
from line import LineCallback

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

# fire = DBAPI()
actions = Actions()
line_callback = LineCallback()

def push_message(user_id, content):
	try:
		line_callback.line_bot_api.push_message(user_id, TextSendMessage(text=content))
	except Exception as e:
		logger.error(e)
		return ('Some thing wrong')
	return ('OK!')

@app.route('/')
def hello_world():
	return 'hello world!'

# @app.route('/line/push')
# def push():
# 	try:
# 		users = fire.get_active_users()
# 		if len(users) > 0:
# 			results = []
# 			for user in users:
# 				result = {}
# 				result[user] = push_message(user)
# 				results.append(result)
# 			logger.info('Push result')
# 			logger.info(results)
# 	except Exception as e:
# 		logger.error(e)
# 	return 'OK'

@app.route('/line/push', methods=['POST'])
def push_content():
	if 'My-Push-Secret' not in request.headers or not actions.check_my_push_secret(request.headers['My-Push-Secret']):
		logger.info('Push secret is incorrect')
		return abort(403)
	logger.info('request push secret : {0}'.format(request.headers['My-Push-Secret']))
	# logger.info(request.json)
	if 'content' not in request.json:
		logger.info('Bad request because no content')
		return abort(400)
	try:
		users = line_callback.get_active_users()
		if len(users) > 0:
			results = []
			for user in users:
				result = {}
				result[user] = push_message(user, request.json['content'])
				results.append(result)
			logger.info('Push result')
			logger.info(results)
	except Exception as e:
		logger.error(e)
		return abort(401)
	return Response(status=200)

@app.route('/line/callback', methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	logger.debug('Request body: ' + body)

	# handle webhook body
	try:
		line_callback.handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'

if __name__ == '__main__':
	app.run()
