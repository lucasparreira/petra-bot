
from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
app.conf.CELERY_IMPORTS = ('helpers', 'downloader', 'local_scheduler', 'tasks', )
app.conf.CELERY_ALWAYS_EAGER = False


@app.task(name='tasks')
def go(seed_list):
    from local_scheduler import Scheduler

    seed_list = ['http://www.extra.com.br', 'http://www.americanas.com.br']#'http://www.americanas.com.br', 'http://www.extra.com.br', 'http://www.pucminas.br']#, 'http://www.extra.com.br']

    scheduler = Scheduler(seed_list)
    scheduler.start()