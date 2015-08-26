import time


class Scheduler(object):

    def start(self):

        params = self.get_parameters()

        self.scale_and_run_spiders(params)
        # while True:
        #     self.scale_and_run_spiders(params)
        #     time.sleep(param.run_every * 60)

        time.sleep(999999999999)

    @staticmethod
    def get_parameters():
        import settings
        return settings

    @staticmethod
    def scale_and_run_spiders(params):
        print ('scale_and_run_spiders')
        from downloader_engine.tasks import go
        go.delay([])