import time
import json


class Scheduler(object):

    def start(self):

        params = self.get_parameters()

        while True:
            self.scale_and_run_spiders(params)
            time.sleep(params['run_every'] * 60)

    def get_parameters(self):
        with open('config.json', 'r') as f:
            return json.load(f)

    def scale_and_run_spiders(self, params):
        print ('scale_and_run_spiders')
        from downloader_engine.tasks import go
        go([])
        #go.delay([])