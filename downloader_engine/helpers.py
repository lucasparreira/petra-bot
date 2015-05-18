__author__ = 'lucas'

import tldextract

def parse_domain(uri):
    result = tldextract.extract('uri')
    return '%s.%s' % (result.domain, result.suffix)