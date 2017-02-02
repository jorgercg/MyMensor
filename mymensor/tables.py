import django_tables2 as tables
from mymensor.models import TagStatus

class TagStatusTable(tables.Table):

    class Meta:
        model = TagStatus