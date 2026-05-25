""" Конфиг gunicorn для отдельного WSGI-демо без Django.

Запуск:
    gunicorn -c gunicorn/demo.conf.py wsgi_demo.app:application
"""

bind = "0.0.0.0:8081"

workers = 2
worker_class = "sync"

timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"

proc_name = "cupofq-wsgi-demo"
