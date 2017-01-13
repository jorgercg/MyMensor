from __future__ import unicode_literals

from django.apps import AppConfig


class MymensorConfig(AppConfig):
    name = 'mymensor'

    def ready(self):
        import mymensor.signals