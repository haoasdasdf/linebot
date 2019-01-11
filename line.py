import logging
import os

import dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (LocationMessage, MessageEvent, TextMessage,
	TextSendMessage)

from fire_db import DBAPI

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)



class LineCallback():
	def __init__(self, *args, **kwargs):
		self.line_bot_api = LineBotApi(os.environ.get('LINE_ACCESS_TOKEN'))
		self.handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
		# self.add_handlers()

	# handler add
	# def add_handlers(self):
	# 	self.handler.add(MessageEvent, message=TextMessage)
	# 	def handle_message(self, event):
	# 		try:
	# 			logger.info(event.reply_token)
	# 			if(event.reply_token != '00000000000000000000000000000000'):
	# 				if(event.message.text == 'delete'):
	# 					logger.info('delete request')
	# 					result = self.fire.delete_user(event.source.user_id)
	# 					self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
	# 				else:
	# 					self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
	# 			else:
	# 				logger.info('A webhook test')
	# 		except:
	# 			logger.error('reply error')
	# 	self.handler.add(MessageEvent, message=LocationMessage)
	# 	def handle_location(self, event):
	# 		logger.info('token: {0}'.format(event.reply_token))
	# 		try:
	# 			data = {}
	# 			data['latitude'] = event.message.latitude
	# 			data['longitude'] = event.message.longitude
	# 			data['user_id'] = event.source.user_id
	# 			data['address'] = event.message.address
	# 			logger.info(data)
	# 			result = self.fire.add_user(data)
	# 			self.line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))

	# 		except Exception as e:
	# 			logger.error('error')
	# 			logger.error(e)
