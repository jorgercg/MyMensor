import django_tables2 as tables
from mymensor.models import Tag, Vp, Media, ProcessedTag

class TagStatusTable(tables.Table):
    vpNumber = tables.Column(accessor='Vp.vpNumber')
    vpDescription = tables.Column(accessor='Vp.vpDescription')
    class Meta:
        model = Tag
        attrs = {'class': 'paleblue'}
        fields = ('tagNumber','tagDescription','tagUnit')
        sequence = ('tagNumber','tagDescription','vpNumber','vpDescription','tagUnit')