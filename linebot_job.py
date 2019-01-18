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
		# self.fire = DBAPI()
		self.line_bot_api = LineBotApi(os.environ.get('LINE_ACCESS_TOKEN'))
		self.handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
		# self.add_handlers()

	def push_message(self, user_id, content):
		try:
			self.line_bot_api.push_message(user_id, TextSendMessage(text=content))
			logger.info('Push message OK to {0}'.format(user_id))
		except:
			logger.error('Push message failed to {0}'.format(user_id))
			return False
		return True
	def reply_message(self, reply_token, content):
		self.line_bot_api.reply_message(reply_token, TextSendMessage(text=content))
		return 

if __name__ == "__main__":
	user_id = 'U816d9966f1e0af6c123cdb3a6522b7c4'
	message = 'hello'
	line = LineCallback()
	line.push_message(user_id, message)

