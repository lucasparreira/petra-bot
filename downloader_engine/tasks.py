
from celery import Celery
from downloader_engine.caching import LocalMemCaching
from downloader_engine.plugins import validate_americanas, validate_saraiva
from downloader_engine.plugins import validate_extra

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
app.conf.CELERY_IMPORTS = ('plugins', 'helpers', 'downloader', 'local_scheduler', 'tasks', )
app.conf.CELERY_ALWAYS_EAGER = True


@app.task(name='tasks')
def go(seed_list):
    from local_scheduler import Scheduler

    seed_list = {'http://www.americanas.com.br': validate_americanas,
                 'http://www.extra.com.br': validate_extra,
                 'http://www.saraiva.com.br': validate_saraiva}
    black_list = ['busca.americanas.com.br', 'checkout.saraiva.com', 'busca.extra.com.br']

    scheduler = Scheduler(seed_list, visit_cache=LocalMemCaching(),
                          dns_cache=LocalMemCaching(),
                          robots_cache=LocalMemCaching(), black_list=black_list)
    scheduler.start()