import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _
from mymensor.models import TagStatusTable

class TagStatusTableClass(tables.Table):
    TAG_STATUS_CHOICES = (
    ('NP', _('NOT PROCESSED')), ('PR', _('PROCESSED')), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'),
    ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED'),)

    statusTagNumber = tables.Column(verbose_name=_('Tag#'))
    statusTagDescription = tables.Column(verbose_name=_('Tag Description'))
    statusVpNumber = tables.Column(verbose_name=_('VP#'))
    statusVpDescription = tables.Column(verbose_name=_('VP Description'))
    statusValValueEvaluated = tables.Column(verbose_name=_('Value'))
    statusTagUnit = tables.Column(verbose_name=_('Unit'))
    statusMediaTimeStamp = tables.Column(verbose_name=_('Media Time'))
    statusDBTimeStamp = tables.Column(verbose_name=_('Processing Time'))
    statusTagStateEvaluated = tables.Column(verbose_name=_('Status'))

    class Meta:
        model = TagStatusTable
        # add class="paleblue" to <table> tag
        attrs = {'class': 'table-sm table-striped table-bordered table-hover table-responsive mym-table'}
        exclude = ('id','processedTag','statusMediaMillisSinceEpoch')