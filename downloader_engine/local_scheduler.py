# -*- coding: UTF-8 -*-

from Queue import PriorityQueue
import time
from helpers.url import parse_domain


class Scheduler(object):

    # tempo em segundos para fazer requisições
    request_waiting_time = 1

    @staticmethod
    def get_current_time_stamp():
        return int(time.time())

    def __init__(self, urls):

        # mantem ultimo acesso (timestamp) de cada dominio
        self.domains_access = dict()
        # organiza paginas para baixar em uma fila de prioridades
        self.pages_queue = PriorityQueue()

        # faz setup dos primeiros downloads
        for url in urls:
            domain_last_access = self.get_current_time_stamp() - 1
            self.domains_access[parse_domain(url)] = domain_last_access
            self.pages_queue.put((domain_last_access, url))

    def enqueue(self, url):
        domain = parse_domain(url)

        # busca ultimo tempo do dominio em questão
        domain_last_access = self.get_current_time_stamp() - 1
        if domain in self.domains_access:
            domain_last_access = self.domains_access[domain]
        else:
            self.domains_access[parse_domain(url)] = domain_last_access

        self.pages_queue.put((domain_last_access, url))

    def start(self):
        pass