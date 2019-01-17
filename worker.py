import logging
from config import Config

import redis
from rq import Connection, Queue, Worker


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

listen = ['high', 'default', 'low']

redis_url = Config.REDIS_CLOUD_URL

conn = redis.from_url(redis_url)

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()
