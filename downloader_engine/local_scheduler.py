# -*- coding: UTF-8 -*-
from Queue import PriorityQueue
import time
from threading import Thread
from downloader import perform_job
from helpers import parse_domain, get_current_time_stamp


class EnumSchedulerStatus(object):
    stopped = 1
    running = 2


class Scheduler(object):

    # tempo em segundos para fazer requisições
    request_waiting_time = 1
    # threads disponiveis
    number_of_threads = 4
    #caminho para salvar na maquina local
    save_path = '/home/lucas/Crawling/'

    def __init__(self, urls):

        # mantem ultimo acesso (timestamp) de cada dominio
        self._domains_access = dict()
        # organiza paginas para baixar em uma fila de prioridades
        self._pages_queue = PriorityQueue()
        # dados do contexto de ecução
        self._context = {'status': EnumSchedulerStatus.stopped, 'threads': []}
        #mantem lista de já processados
        self.already_visited = {}

        # faz setup dos primeiros downloads
        for url in urls:
            domain_last_access = get_current_time_stamp() - 1
            self._domains_access[parse_domain(url)] = domain_last_access
            self._pages_queue.put((domain_last_access, url))

    def enqueue(self, url):
        domain = parse_domain(url)

        # busca ultimo tempo do dominio em questão
        domain_last_access = get_current_time_stamp() - 1
        if domain in self._domains_access:
            domain_last_access = self._domains_access[domain]
        else:
            self._domains_access[parse_domain(url)] = domain_last_access

        self._pages_queue.put((domain_last_access, url))

    def start(self):

        if self._context['status'] == EnumSchedulerStatus.running:
            raise Exception('Already running.')

        self._context['status'] = EnumSchedulerStatus.running

        # inicia todas as threads permitidas
        for i in range(0, self.number_of_threads):
            current_thread = Thread(target=perform_job, args=(self,))
            self._context['threads'].append(current_thread)
            current_thread.start()

    def get_next(self):

        # obtem proxima pagina para baixar
        next_page = self._pages_queue.get()

        if next_page:
            next_domain = parse_domain(next_page[1])
            while (get_current_time_stamp() - self._domains_access[next_domain] < self.request_waiting_time):
                time.sleep(0.1)

            return next_page[1]

        return None

    def update_domain(self, url):
        self._domains_access[parse_domain(url)] = get_current_time_stamp()