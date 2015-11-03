# -*- coding: UTF-8 -*-
import time
from threading import Thread, Lock
from downloader import download_pages
from helpers import parse_domain, get_current_time_stamp, parse_host, parse_address, user_agent_name
import socket
import robotexclusionrulesparser


class EnumSchedulerStatus(object):
    """
    Every possible status for the scheduler.
    """
    stopped = 1
    running = 2


class Scheduler(object):
    # minimum waiting time before any consecutive hit to the same server
    request_waiting_time = 1
    # max number of threads running concurrently
    max_number_of_threads = 16

    def __init__(self, urls, visit_cache, dns_cache, robots_cache, black_list, save_path='/home/lucas/Crawling/'):

        # destination
        self.save_path = save_path
        # keep track of visits
        self._visit_cache = visit_cache
        # dns resolution cache
        self._dns_cache = dns_cache
        # robots.txt cache
        self._robot_cache = robots_cache
        # black list
        self._black_list = black_list

        # used to sync threads
        self.lock_obj = Lock()
        # "priority queue" of next visit
        self.domains_queue = []
        # pages to visit
        self.domain_pages = {}
        # execution context data
        self._context = {'status': EnumSchedulerStatus.stopped, 'threads': []}

        # stats (for debug)
        self.stats = {}

        # calculate a time to allow instant visit
        domain_last_access = get_current_time_stamp() - self.request_waiting_time

        # domains and their plugins
        self.domain_plugins = {}

        # faz setup dos primeiros downloads
        for url in urls.keys():
            current_domain = parse_domain(url)
            self.domain_plugins[current_domain] = urls[url]
            self.domains_queue.append([domain_last_access, current_domain])
            self.domain_pages[current_domain] = [url]
            self.stats[current_domain] = {'collected': 0, 'discard': 0,
                                          'start': get_current_time_stamp(), 'discard_robots': 0,
                                          'codes': {}}

        self.number_of_threads = min(self.max_number_of_threads, len(self.domain_pages.keys()))
        # self.number_of_threads = 1

    def add_code(self, page, code):

        """
        Add new code to the stats (http code).
        """

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

        """
        Enqueue new page to visit.
        """

        # must be thread-safe
        with self.lock_obj:

            if url:
                url_lower = url.lower()
                if url_lower in self._black_list:
                    return

            if not self._visit_cache.exists(url):

                addr = parse_address(url)
                domain = parse_domain(url)
                if not self._robot_cache.exists(addr):
                    robot_parser = robotexclusionrulesparser.RobotExclusionRulesParser()
                    robot_parser.user_agent = user_agent_name
                    robot_parser.fetch(addr + "/robots.txt")
                    self._robot_cache.add(addr, robot_parser)

                if self._robot_cache.get(addr).is_allowed("petra-bot", url):
                    self.domain_pages[domain].append(url)
                else:
                    self.stats[domain]['discard_robots'] += 1

            self._visit_cache.add(url, 0)

    def replace_host_addr(self, full_url):

        with self.lock_obj:
            try:
                full_domain = parse_host(full_url)
                if not self._dns_cache.exists(full_domain):
                    self._dns_cache.add(full_domain, socket.gethostbyname(full_domain))

                return full_url.replace(full_domain, self._dns_cache.get(full_domain))
            except:
                return None

    def start(self):

        """
        Start the job.
        """

        if self._context['status'] == EnumSchedulerStatus.running:
            raise Exception('Already running.')

        self._context['status'] = EnumSchedulerStatus.running

        # start all threads
        for i in range(0, self.number_of_threads):
            current_thread = Thread(target=download_pages, args=(self,))
            self._context['threads'].append(current_thread)
            current_thread.start()

    def get_next(self):

        """
        Get the next page to visit.
        :return: page to visit.
        """

        with self.lock_obj:
            # sort by priority (last access)
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
                # move it to the end
                last_access = current_domain_tuple[0]
                current_time = get_current_time_stamp()
                while (current_time - last_access) < self.request_waiting_time:
                    time.sleep(0.05)
                    current_time = get_current_time_stamp()

                self._update_domain(next_page, current_time)
                self._visit_cache.add(next_page, 0)

            return next_page

    def _update_domain(self, url, current_time):

        """
        Update the domain's last access.
        :param url: url with the domain
        :param current_time: last access
        """

        domain = parse_domain(url)
        for domain_tuple in self.domains_queue:
            if domain_tuple[1] == domain:
                domain_tuple[0] = current_time
                break