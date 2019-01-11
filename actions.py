import logging
import os
import os.path

import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

MY_PUSH_SECRET = os.environ.get('MY_PUSH_SECRET')


class Actions():
	def __init__(self, *args, **kwargs):
		self.my_push_secret = MY_PUSH_SECRET

	def check_my_push_secret(self, push_secret):

		logger.info('Check push secret: {0}'.format(push_secret == self.my_push_secret))
		return True if push_secret == self.my_push_secret else False
