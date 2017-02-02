import django_tables2 as tables
from mymensor.models import TagStatusDjango

class TagStatusTable(tables.Table):

    class Meta:
        model = TagStatusDjango