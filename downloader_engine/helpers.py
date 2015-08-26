# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import time
import tldextract
import uuid


def parse_domain(uri):
    try:
        result = tldextract.extract(uri)
        return ('%s.%s' % (result.domain, result.suffix)).lower()
    except:
        raise


def parse_address(uri):
    result = tldextract.extract(uri)
    addr = 'http://'
    if result.subdomain:
        addr += result.subdomain + '.'
    addr += result.domain
    if result.suffix:
        addr += '.' + result.suffix

    return addr.lower()


def parse_host(uri):
    result = tldextract.extract(uri)
    return ('%s.%s.%s' % (result.subdomain, result.domain, result.suffix)).lower()


def parse_links(html, origin_domain, restricted_domain=None):
    soup = BeautifulSoup(html)
    links = []
    for link in soup.findAll("a"):
        href = link.get("href")

        if href and href[0].strip() != u'#' and \
                (not restricted_domain or parse_domain(href).lower() == restricted_domain.lower()):

            if href[0] == u'/':
                links.append(origin_domain + href)
            else:
                links.append(href)

    return links


def guid_time():
    return str(uuid.uuid1())


def get_current_time_stamp():
        return int(time.time())


class VisitCache(object):

    """
    Implements a visiting cache through a dictionary.
    It should be replaced by other solution in case of bigger number of urls.
    e.g. Bloom Filter
    """

    def __init__(self):
        self._already_visited = dict()

    def add(self, url):
        if url not in self._already_visited:
            self._already_visited[url] = 1
        else:
            self._already_visited[url] += 1

    def already_visited(self, url):
        return url in self._already_visited