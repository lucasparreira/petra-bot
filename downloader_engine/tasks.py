
from celery import Celery

app = Celery('tasks', broker='amqp://guest@localhost//')
app.conf.CELERY_IMPORTS = ('tasks')
app.conf.CELERY_ALWAYS_EAGER = True


@app.task(name='tasks')
def go(seed_list):
    from local_scheduler import Scheduler

    seed_list = ['http://www.americanas.com.br', 'http://www.ricardoeletro.com.br', 'http://www.pucminas.br', 'http://www.extra.com.br']

    scheduler = Scheduler(seed_list)
    scheduler.start()