# -*- coding: UTF-8 -*-
import urllib2
from helpers import parse_domain, parse_links, parse_address, guid_time, get_current_time_stamp, parse_host, \
    user_agent_name
import os


def download_pages(scheduler):

    """

    :param scheduler:
    :return:
    """

    next_page = scheduler.get_next()

    while next_page:
        print next_page

        try:

            # DEBUG purposes
            try:
                if get_current_time_stamp() % 600 == 0:
                    print scheduler.stats
            except:
                pass

            next_page_resolved = scheduler.replace_host_addr(next_page)
            if next_page_resolved:

                req = urllib2.Request(next_page_resolved, headers={'User-Agent': user_agent_name,
                                                                   'Host': parse_host(next_page)})
                response = urllib2.urlopen(req)

                if response.headers.type.lower() == 'text/html':

                    scheduler.add_code(next_page, response.code)

                    document = response.read()
                    domain = parse_domain(next_page)
                    domain_dir = '%s%s' % (scheduler.save_path, domain)

                    if not os.path.exists(domain_dir):
                        os.makedirs(domain_dir)

                    if scheduler.domain_plugins[domain](document):
                        with open('%s/%s.html' % (domain_dir, guid_time()), 'w') as the_file:
                            the_file.write(document)
                        scheduler.stats[domain]['collected'] += 1
                    else:
                        scheduler.stats[domain]['discard'] += 1

                    # extract new links
                    links = parse_links(document, parse_address(next_page), restricted_domain=domain)
                    for link in links:
                        scheduler.enqueue(link)
                else:
                    response.close()
        except Exception as e:

            try:
                if '302' in str(e):
                    scheduler.add_code(next_page, 302)
                elif '400' in str(e):
                    scheduler.add_code(next_page, 400)
            except:
                pass

            if next_page_resolved:
                print next_page_resolved
            print e

        next_page = scheduler.get_next()

    print ('!@#$ END - %s' % str(get_current_time_stamp()))
    print scheduler.stats