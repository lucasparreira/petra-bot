import urllib2

def perform_job(scheduler):
    next_page = scheduler.get_next()

    if next_page:
        response = urllib2.urlopen(next_page)
        document = response.read()
        print document
