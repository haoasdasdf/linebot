from rq import Queue
from worker import conn
import time
q = Queue(connection=conn)

from utils import count_words_at_url

flag = False
while not flag:
	try:
		result = q.enqueue(count_words_at_url, 'http://heroku.com')
	except:
		print('enqueue error, retry')
		time.sleep(2)
		continue
	flag = True

print(result)
