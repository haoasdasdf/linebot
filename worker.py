import logging
import os
import sys

import dotenv
import redis
from rq import Connection, Queue, Worker

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)
if len(args) == 1:
	dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
else: 
	try:
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env.' + args[1])
	except:
		# logger.error('Can not find environment file named {0}'.format(args[1]))
		dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_CLOUD_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
