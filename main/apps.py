from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        from . import utils
        utils.start_scheduler()
