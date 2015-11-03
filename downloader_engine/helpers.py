# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import time
import tldextract
import uuid


user_agent_name = 'petra-bot'


def parse_domain(uri):
    """
    Parse only master domain, e.g nytimes.com.
    """

    try:
        result = tldextract.extract(uri)
        return ('%s.%s' % (result.domain, result.suffix)).lower()
    except:
        raise


def parse_address(uri):
    """
    Parse full address, e.g http://www.nytimes.com.
    """

    result = tldextract.extract(uri)
    addr = 'http://'
    if result.subdomain:
        addr += result.subdomain + '.'
    addr += result.domain
    if result.suffix:
        addr += '.' + result.suffix

    return addr.lower()


def parse_host(uri):
    """
    Parse address without web protocol, e.g www.nytimes.com.
    """

    result = tldextract.extract(uri)
    return ('%s.%s.%s' % (result.subdomain, result.domain, result.suffix)).lower()


def parse_links(html, origin_domain, restricted_domain=None):
    """
    Parse absolute links according to the restrictions.
    """

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
    """
    Return a time-based-seed guid.
    """

    return str(uuid.uuid1())


def get_current_time_stamp():
    """
    Return the current time stamp.
    """
    return int(time.time())
