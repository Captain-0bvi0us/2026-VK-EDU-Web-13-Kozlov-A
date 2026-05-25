""" Конфиг gunicorn для Django (application.wsgi).

Запуск:
    gunicorn -c gunicorn/django.conf.py application.wsgi:application
"""

bind = "0.0.0.0:8000"

workers = 2
worker_class = "sync"

timeout = 60
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'

proc_name = "cupofq-django"
