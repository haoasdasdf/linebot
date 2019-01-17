import logging
import os
import sys

import dotenv

args = sys.argv
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
# from line import LineCallback
if len(args) == 1:
	dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
else: 
	try:
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env.' + args[1])
		logger.info('Used {0} environment'.format(args[1]))
	except:
		logger.error('Can not find environment file named {0}, so used default env file'.format(args[1]))
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
# os.environ.get('')
class Config:
	LINE_CHANNEL_ID = os.environ.get('LINE_CHANNEL_ID')
	LINE_ACCESS_TOKEN = os.environ.get('LINE_ACCESS_TOKEN')
	LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
	FIREBASE_DATABASE_SECRET = os.environ.get('FIREBASE_DATABASE_SECRET')
	FIREBASE_DATABASE_COLLECTION_NAME = os.environ.get('FIREBASE_DATABASE_COLLECTION_NAME')
	GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
	MY_PUSH_SECRET = os.environ.get('MY_PUSH_SECRET')
	OPEN_WEATHER_MAP_API_KEY = os.environ.get('OPEN_WEATHER_MAP_API_KEY')
	OPEN_WEATHER_MAP_BASE_URL = os.environ.get('OPEN_WEATHER_MAP_BASE_URL')
	DARKSKY_API_SECRET_KEY = os.environ.get('DARKSKY_API_SECRET_KEY')
	DARKSKY_API_BASE_URL = os.environ.get('DARKSKY_API_BASE_URL')
	REDIS_CLOUD_URL = os.environ.get('REDIS_CLOUD_URL')
