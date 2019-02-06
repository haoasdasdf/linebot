import logging

from linebot.models import (FollowEvent, LocationMessage, MessageEvent,
	TextMessage, TextSendMessage, UnfollowEvent)
from rq import Queue
from config import Config
from fire_db import DBAPI
from linebot_job import LineCallback
from rq_worker import conn
from weather import Weather

logger = logging.getLogger(__name__)


logging.basicConfig(level=logging.DEBUG)

MY_PUSH_SECRET = Config.MY_PUSH_SECRET

line_bot = LineCallback()
fire = DBAPI('actions')
weather = Weather()

q = Queue(Config.RUN_ENV, connection=conn)

def check_my_push_secret(push_secret):

	logger.info('Check push secret: {0}'.format(push_secret == MY_PUSH_SECRET))
	return True if push_secret == MY_PUSH_SECRET else False

def delete_from_firebase( reply_token, user_id):
	try:
		logger.info('delete request')
		result = fire.delete_user(user_id)

		reply_line(reply_token, result)
	except:
		return False
	return True

def reply_line( reply_token, content):
	try:
		line_bot.reply_message(reply_token, content)
	except:
		return False
	return True

def push_message(user_id, content=None):
	if content is None:
		logger.info('Nothing to {0}'.format(user_id))
		return('Nothing to send')
	try:
		line_bot.push_message(user_id, content)
	except Exception as e:
		logger.error(e)
		return ('Some thing wrong')
	logger.info('Push to {0} OK!'.format(user_id))
	return ('OK!')

def push_to_all_active_users(content):
	try:
		users = fire.get_active_users()
		if len(users) > 0:
			results = []
			for user in users:
				result = {}
				result[user] = push_message(user, content)
				results.append(result)
			logger.info('Push result')
			logger.info(results)
		else:
			logger.info('No active user')
	except Exception as e:
		logger.error(e)
		return False
	return True

def push_weather_to_users(time, user_id=None):
	try:
		now = time
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
						content = weather.format_weather_data(weather_raw, city_info, timezone=loc.get('timezone'))
					else:
						logger.info('Unknown location for user {0}'.format(user))

					logger.info('Push weather info to user')
					result[user] = push_message(user, content)
					results.append(result)
			logger.info('Push result')
			logger.info(results)
	except Exception as e:
		logger.error(e)
		return False
	return True

def received_location(reply_token, time, data):
	try:
		data['timezone'] = fire.get_timezone_from_lat_long(data['latitude'], data['longitude'])
		result = fire.add_user(data)
		q.enqueue(reply_line,args=(reply_token, result))
		# line_bot.line_bot_api.reply_message(reply_token, TextSendMessage(text=result))
		q.enqueue(push_weather_to_users, args=(time, data['user_id']))
	except:
		return False
	return True

def received_follow(reply_token, user_id):
	try:
		# reply if token is not for webhook test
		logger.info(reply_token)
		if(reply_token != '00000000000000000000000000000000'):
			logger.info('Get a follow event')
			username = ''
			try:
				profile = line_bot.line_bot_api.get_profile(user_id)
				username = profile.display_name
				logger.info('username: {0}'.format(username))
			except:
				logger.error('Failed to get user profile')
			greeting_message = ('Hello {0}! \n \n Thank you for follow me! \n \n Please send me your location'.format(username))
			q.enqueue(reply_line,args=(reply_token, greeting_message))
			fire.activate_user(user_id)
		else:
			logger.info('A webhook test')
	except Exception as e:
		logger.error(e)
		logger.error('reply for follow event error')

def received_unfollow( user_id):
	try:
		logger.info('delete request')
		#deactivate_user
		fire.deactivate_user(user_id)
		# logger.info(result)
	except Exception as e:
		logger.error(e)
		logger.error('delete failed')

