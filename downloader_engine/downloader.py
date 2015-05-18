from celery import Celery
from downloader_engine.local_scheduler import Scheduler

app = Celery('downloader', broker='amqp://guest@localhost//')


@app.task(name='downloader')
def go(seed_list=[]):
    print ('go')

    scheduler = Scheduler(seed_list)
    scheduler.start()