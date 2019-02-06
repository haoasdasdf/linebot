import logging

import redis
from rq import Connection, Queue, Worker
from rq.handlers import move_to_failed_queue

from config import Config

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

listen = [Config.RUN_ENV]
redis_config = Config.REDIS_CLOUD_CONFIG
if redis_config['REDIS_HOST_FROM'] == 'cloud':
	redis_url = 'redis://{0}:{1}@{2}'.format(redis_config['DATABASE_NAME'], redis_config['PASSWORD'], redis_config['URL'])
else:
	redis_url = 'redis://redis:6379'

conn = redis.from_url(redis_url)

if __name__ == '__main__':
	logger.debug(redis_url)
	logger.debug('listen: {0}'.format(listen))
	with Connection(conn):
		worker = Worker(map(Queue, listen))

		worker.work()
	# main()
