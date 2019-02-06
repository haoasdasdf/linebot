import logging
import os
import sys
from argparse import ArgumentParser
import dotenv

parser = ArgumentParser()
parser.add_argument('--redis', default='cloud', type=str, choices=['local', 'cloud'], dest='redis_from')
parser.add_argument('--env', default='local', type=str, choices=['local', 'dev', 'prod'], dest='env')
# args = sys.argv
args = parser.parse_args()
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
# from line import LineCallback
if args.env == 'local':
	dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
else: 
	try:
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env.' + args.env)
		logger.info('Used {0} environment'.format(args.env))
	except:
		logger.error('Can not find environment file named {0}, so used default env file'.format(args.env))
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
os.environ.get('')
class Config:
	LINE_CONFIG = {
	'CHANNEL_ID': os.environ.get('LINE_CHANNEL_ID'),
	'ACCESS_TOKEN': os.environ.get('LINE_ACCESS_TOKEN'),
	'CHANNEL_SECRET': os.environ.get('LINE_CHANNEL_SECRET')
	}
	FIREBASE_CONFIG = {
	'SECRET': os.environ.get('FIREBASE_DATABASE_SECRET'),
	'COLLECTION_NAME': os.environ.get('FIREBASE_DATABASE_COLLECTION_NAME')
	}
	GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
	MY_PUSH_SECRET = os.environ.get('MY_PUSH_SECRET')
	OWM_API_CONFIG = {
	'KEY': os.environ.get('OPEN_WEATHER_MAP_API_KEY'),
	'BASE_URL': os.environ.get('OPEN_WEATHER_MAP_BASE_URL')
	}
	DARKSKYAPI_CONFIG = {
	'SECRET_KEY': os.environ.get('DARKSKY_API_SECRET_KEY'),
	'BASE_URL': os.environ.get('DARKSKY_API_BASE_URL')
	}
	REDIS_CLOUD_CONFIG = {
	'REDIS_HOST_FROM': args.redis_from,
	'URL': os.environ.get('REDIS_CLOUD_URL'),
	'PASSWORD': os.environ.get('REDIS_CLOUD_PASSWORD'),
	'DATABASE_NAME': os.environ.get('REDIS_CLOUD_DATABASE_NAME')
	}

if __name__ == "__main__":
	print(args.redis_from)
	print(args.env)

