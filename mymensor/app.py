from django.apps import AppConfig


class MyMensorConfig(AppConfig):
    name = 'mymensor'

    def ready(self):
        import mymensor.signals
