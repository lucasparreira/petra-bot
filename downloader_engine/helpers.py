# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import time
import tldextract
import uuid

def parse_domain(uri):
    try:
        result = tldextract.extract(uri)
        return '%s.%s' % (result.domain, result.suffix)
    except:
        raise


def parse_address(uri):
    result = tldextract.extract(uri)
    return 'http://%s.%s.%s' % (result.subdomain, result.domain, result.suffix)


def parse_links(html, origin_domain, restricted_domain=None):
    soup = BeautifulSoup(html)
    links = []
    for link in soup.findAll("a"):
        href = link.get("href")

        if href and href[0].strip() != u'#' and (not restricted_domain or parse_domain(href).lower() == restricted_domain.lower()):

            if href[0] == u'/':
                links.append(origin_domain + href)
            else:
                links.append(href)

    return links


def guid_time():
    return str(uuid.uuid1())


def get_current_time_stamp():
        return int(time.time())