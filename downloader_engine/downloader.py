# -*- coding: UTF-8 -*-
import urllib2
from helpers import parse_domain, parse_links, parse_address, guid_time
import os


def perform_job(scheduler):
    next_page = scheduler.get_next()

    while next_page:
        print next_page

        try:

            req = urllib2.Request(next_page, headers={'User-Agent': "petra-bot"})
            response = urllib2.urlopen(req)

            if response.headers.type.lower() == 'text/html':

                document = response.read()
                domain = parse_domain(next_page)
                domain_dir = '%s%s' % (scheduler.save_path, domain)

                if not os.path.exists(domain_dir):
                    os.makedirs(domain_dir)

                with open('%s/%s.html' % (domain_dir, guid_time()), 'w') as the_file:
                    the_file.write(document)

                # extrai novas páginas para baixar
                links = parse_links(document, parse_address(next_page), restricted_domain=domain)

                for link in links:
                    scheduler.enqueue(link)
            else:
                response.close()
        except Exception as e:
            print e

        next_page = scheduler.get_next()