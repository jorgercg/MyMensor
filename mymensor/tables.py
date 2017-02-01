import django_tables2 as tables
from mymensor.models import Tag, Vp, Media, ProcessedTag

class TagStatusTable(tables.Table):

    class Meta:
        model = Tag
        attrs = {'class': 'paleblue'}
        fields = ('tagNumber','tagDescription','tagUnit')