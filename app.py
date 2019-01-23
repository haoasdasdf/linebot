
import datetime
import logging

import redis
from flask import Flask, Response, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (FollowEvent, LocationMessage, MessageEvent,
	TextMessage, TextSendMessage, UnfollowEvent)
from rq import Queue

from actions import *
# from actions import (check_my_push_secret, delete_from_firebase, reply_line, push_message_to_line)
from config import Config
from fire_db import DBAPI
from linebot_job import LineCallback
from rq_worker import conn
from weather import Weather

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

handler = line_bot.handler

JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

@app.route('/')
def hello_world():
	return 'hello world!'

@app.route('/line/push', methods=['POST'])
def push_content():
	if 'My-Push-Secret' not in request.headers or not check_my_push_secret(request.headers['My-Push-Secret']):
		logger.info('Push secret is incorrect')
		return abort(403)
	logger.info('request push secret : {0}'.format(request.headers['My-Push-Secret']))
	# logger.info(request.json)
	if 'content' not in request.json:
		logger.info('Bad request because no content')
		return abort(400)
	if 'user_id' in request.json:
		logger.info('Push to {0}'.format(request.json['user_id']))
		q.enqueue(push_message, args=(request.json['user_id'], request.json['content']))
	else:
		logger.info('Push to all active users')
		q.enqueue(push_to_all_active_users, request.json['content'])
	return Response(status=200)

@app.route('/line/weather-push')
@app.route('/line/weather-push/<user_id>')
def push_weather(user_id=None, internal=None):
	if 'My-Push-Secret' not in request.headers or not check_my_push_secret(request.headers['My-Push-Secret']):
		if not internal:
			logger.info('Push secret is incorrect')
			return abort(403)
		else:
			logger.info('Get push weather request from internal')
	try:
		now = datetime.datetime.now(JST)
		if user_id is None:
			q.enqueue(push_weather_to_users, now)
		else:
			q.enqueue(push_weather_to_users, args=(now, user_id))
	except:
		logger.error('failed to push weather')
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
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	try:
		reply_token = event.reply_token
		user_id = event.source.user_id
		# reply if token is not for webhook test
		logger.info(event.reply_token)
		if(event.reply_token != '00000000000000000000000000000000'):
			if(event.message.text == 'delete'):
				q.enqueue(delete_from_firebase, args=(reply_token, user_id))

			else:
				q.enqueue(reply_line, args=(reply_token, event.message.text))
		else:
			logger.info('A webhook test')
	except Exception as e:
		logger.error('reply error')
		logger.error(e)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
	logger.info('token: {0}'.format(event.reply_token))
	try:
		now = datetime.datetime.now(JST)
		reply_token = event.reply_token
		data = {}
		data['latitude'] = event.message.latitude
		data['longitude'] = event.message.longitude
		data['user_id'] = event.source.user_id
		data['address'] = event.message.address
		logger.info(data)
		q.enqueue(received_location, args=(reply_token, now, data))
	except Exception as e:
		logger.error('handle_location error')
		logger.error(e)

@handler.add(FollowEvent)
def handle_follow(event):
	q.enqueue(received_follow, args=(event.reply_token, event.source.user_id))


@handler.add(UnfollowEvent)
def handle_unfollow(event):
	q.enqueue(received_unfollow, event.source.user_id)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
