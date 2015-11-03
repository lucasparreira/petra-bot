import time


class Scheduler(object):
    """

    """

    def start(self):

        import settings as params

        self.scale_and_run_spiders(params)
        # while True:
        #     self.scale_and_run_spiders(params)
        #     time.sleep(param.run_every * 60)

        time.sleep(999999999999)

    @staticmethod
    def scale_and_run_spiders(params):
        print ('scale_and_run_spiders')
        from downloader_engine.tasks import go
        go.delay([])