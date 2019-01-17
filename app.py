
import datetime
import logging

from flask import Flask, Response, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (FollowEvent, LocationMessage, MessageEvent,
                            TextMessage, TextSendMessage, UnfollowEvent)

from actions import Actions
from config import Config
from fire_db import DBAPI
from weather import Weather

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
# from line import LineCallback





app = Flask(__name__)

line_bot_api = LineBotApi(Config.LINE_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

fire = DBAPI()
actions = Actions()
weather = Weather()
JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
# line_callback = LineCallback()

def push_message(user_id, content=None):
	if content is None:
		return('Nothing to send')
	try:
		line_bot_api.push_message(user_id, TextSendMessage(text=content))
	except Exception as e:
		logger.error(e)
		return ('Some thing wrong')
	return ('OK!')

@app.route('/')
def hello_world():
	return 'hello world!'

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
	if 'user_id' in request.json:
		result = push_message(request.json['user_id'], request.json['content'])
		logger.info('Push result')
		logger.info(result)
	else:
		try:
			users = fire.get_active_users()
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

@app.route('/line/weather-push')
@app.route('/line/weather-push/<user_id>')
def push_weather(user_id=None, internal=None):
	if 'My-Push-Secret' not in request.headers or not actions.check_my_push_secret(request.headers['My-Push-Secret']):
		if not internal:
			logger.info('Push secret is incorrect')
			return abort(403)
		else:
			logger.info('Get push weather request from internal')
	try:
		now = datetime.datetime.now(JST)
		if user_id is None:
			users = fire.get_active_users()
		else:
			users = [user_id]
		if len(users) > 0:
			results = []
			for user in users:
				result = {}
				loc = fire.get_location_info(user)
				if loc is None:
					result[user] = push_message(user)
				else:
					logger.info('get weather info')

					weather_raw,city_info = weather.get_weather(loc['latitude'], loc['longitude'], int(now.timestamp()))
					content = None
					if((weather_raw is not None) and (city_info is not None)):
						content = weather.format_weather_data(weather_raw, city_info)
					else:
						logger.info('Unknown location for user {0}'.format(user))

					logger.info('Push weather info to user')
					result[user] = push_message(user, content)
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
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	try:
		# reply if token is not for webhook test
		logger.info(event.reply_token)
		if(event.reply_token != '00000000000000000000000000000000'):
			if(event.message.text == 'delete'):
				logger.info('delete request')
				result = fire.delete_user(event.source.user_id)
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
			else:
				line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
		else:
			logger.info('A webhook test')
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
		# fire = DBAPI()
		result = fire.add_user(data)
		line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
		push_weather(data['user_id'], True)

	except Exception as e:
		logger.error('handle_location error')
		logger.error(e)

@handler.add(FollowEvent)
def handle_follow(event):
	try:
		# reply if token is not for webhook test
		logger.info(event.reply_token)
		if(event.reply_token != '00000000000000000000000000000000'):
			logger.info('Get a follow event')
			username = ''
			try:
				profile = line_bot_api.get_profile(event.source.user_id)
				username = profile.display_name
				logger.info('username: {0}'.format(username))
			except:
				logger.error('Failed to get user profile')
			greeting_message = ('Hello {0}! \n \n Thank you for follow me! \n \n Please send me your location'.format(username))
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text=greeting_message))
		else:
			logger.info('A webhook test')
	except:
		logger.error('reply for follow event error')

@handler.add(UnfollowEvent)
def handle_unfollow(event):
	logger.info('Get an unfollow event')
	try:
		logger.info('delete request')
		result = fire.delete_user(event.source.user_id)
		logger.info(result)
	except:
		logger.error('delete failed')

if __name__ == '__main__':
	app.run()
