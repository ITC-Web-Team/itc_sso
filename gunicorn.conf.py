import multiprocessing

# Gunicorn picks this file up automatically when run from the project root:
#   gunicorn config.wsgi:application
bind = "0.0.0.0:3000"
workers = min(multiprocessing.cpu_count() * 2 + 1, 9)
threads = 4
worker_class = "gthread"
timeout = 60
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
