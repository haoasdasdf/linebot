web: gunicorn app:app(env=local,redis=cloud) --log-file -
worker: python -u rq_worker.py --env local --redis cloud
