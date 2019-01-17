import logging

import redis
from rq import Connection, Queue, Worker

from config import Config

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

listen = ['high', 'default', 'low']
redis_config = Config.REDIS_CLOUD_CONFIG
redis_url = 'redis://{0}:{1}@{2}'.format(redis_config['DATABASE_NAME'], redis_config['PASSWORD'], redis_config['URL'])

conn = redis.from_url(redis_url)

def main():
	r = redis.Redis.from_url(redis_url)
	for key in r.keys('*'):
		print (key)
if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
	# main()
