import django_tables2 as tables
from mymensor.models import Tag, Vp, Media, ProcessedTag

class TagStatusTable(tables.Table):
    vpNumber = tables.Column(accessor='vp.vpNumber')
    vpDescription = tables.Column(accessor='vp.vpDescription')
    latestValue = tables.Column(accessor='processedtag.valValueEvaluated')
    valueState = tables.Column(accessor='processedtag.tagStateEvaluated')
    class Meta:
        sequence = ('tagNumber','tagDescription','vpNumber','vpDescription','latestValue','tagUnit', 'valueState')