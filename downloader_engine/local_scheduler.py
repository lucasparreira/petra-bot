# -*- coding: UTF-8 -*-
import time
from threading import Thread, Lock
from downloader import perform_job
from downloader_engine.plugins import validate_americanas, validate_extra, validate_saraiva
from helpers import parse_domain, get_current_time_stamp, VisitCache, parse_host, parse_address
import socket
import robotexclusionrulesparser


class EnumSchedulerStatus(object):
    stopped = 1
    running = 2


class Scheduler(object):

    # tempo em segundos para fazer requisições
    request_waiting_time = 1
    # maximo de threads
    max_number_of_threads = 16
    # caminho para salvar na maquina local
    save_path = '/home/lucas/Crawling/'

    def __init__(self, urls):
        # objeto para sincronismo
        self.lock_obj = Lock()
        # mantem fila de prioridades de cada dominio
        self.domains_queue = []
        # mantem paginas a baixar dos dominios
        self.domain_pages = dict()
        # dados do contexto de execução
        self._context = {'status': EnumSchedulerStatus.stopped, 'threads': []}
        # mantem lista de já processados
        self._visit_cache = VisitCache()

        self.domain_plugins = {'americanas.com.br': validate_americanas,
                               'extra.com.br': validate_extra,
                               'saraiva.com.br': validate_saraiva}

        self._dns_cache = {}
        self._robot_cache = {}

        self.stats = dict()

        domain_last_access = get_current_time_stamp() - self.request_waiting_time

        # faz setup dos primeiros downloads
        for url in urls:
            current_domain = parse_domain(url)
            self.domains_queue.append([domain_last_access, current_domain])
            self.domain_pages[current_domain] = [url]
            self.stats[current_domain] = {'collected': 0, 'discard': 0,
                                          'start': get_current_time_stamp(), 'discard_robots': 0,
                                          'codes': {}}

        self.number_of_threads = min(self.max_number_of_threads, len(self.domain_pages.keys()))
        # self.number_of_threads = 1

    def add_code(self, page, code):
        with self.lock_obj:
            try:
                domain = parse_domain(page)
                if code in self.stats[domain]['codes']:
                    self.stats[domain]['codes'][code] += 1
                else:
                    self.stats[domain]['codes'][code] = 1
            except Exception as e:
                print e
                pass

    def enqueue(self, url):
        with self.lock_obj:

            if url:
                url_lower = url.lower()
                if 'busca.americanas.com.br' in url_lower or 'checkout.saraiva.com' in url_lower or \
                                'busca.extra.com.br' in url_lower:
                    return

            if not self._visit_cache.already_visited(url):

                addr = parse_address(url)
                domain = parse_domain(url)
                if addr not in self._robot_cache:
                    robot_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
                    robot_parser.user_agent = 'petra-bot'
                    robot_parser.fetch(addr + "/robots.txt")
                    self._robot_cache[addr] = robot_parser

                if self._robot_cache[addr].is_allowed("petra-bot", url):
                    self.domain_pages[domain].append(url)
                else:
                    self.stats[domain]['discard_robots'] += 1

            self._visit_cache.add(url)

    def replace_host_addr(self, full_url):

        with self.lock_obj:
            try:
                full_domain = parse_host(full_url)
                if full_domain not in self._dns_cache:
                    self._dns_cache[full_domain] = socket.gethostbyname(full_domain)

                return full_url.replace(full_domain, self._dns_cache[full_domain])
            except:
                return None

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
        with self.lock_obj:
            # lista ordenada de dominios (por prioridade)
            domains = sorted(self.domains_queue, key=lambda t: t[0])
            next_page = None
            current_domain_tuple = None
            for domain_tuple in domains:
                try:
                    next_page = self.domain_pages[domain_tuple[1]].pop()
                    current_domain_tuple = domain_tuple
                    break
                except IndexError:
                    pass

            if current_domain_tuple:
                # joga dominio para o final
                last_access = current_domain_tuple[0]
                current_time = get_current_time_stamp()
                while (current_time - last_access) < self.request_waiting_time:
                    time.sleep(0.05)
                    current_time = get_current_time_stamp()

                self._update_domain(next_page, current_time)
                self._visit_cache.add(next_page)

            return next_page

    def _update_domain(self, url, current_time):
        domain = parse_domain(url)
        for domain_tuple in self.domains_queue:
            if domain_tuple[1] == domain:
                domain_tuple[0] = current_time
                break