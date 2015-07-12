
from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
app.conf.CELERY_IMPORTS = ('plugins', 'helpers', 'downloader', 'local_scheduler', 'tasks', )
app.conf.CELERY_ALWAYS_EAGER = True


@app.task(name='tasks')
def go(seed_list):
    from local_scheduler import Scheduler

    seed_list = ['http://www.americanas.com.br', 'http://www.extra.com.br', 'http://www.saraiva.com.br']

    scheduler = Scheduler(seed_list)
    scheduler.start()