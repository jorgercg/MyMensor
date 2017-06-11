import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _
from mymensor.models import TagStatusTable

class TagStatusTableClass(tables.Table):
    class Meta:
        TAG_STATUS_CHOICES = (
        ('NP', _('NOT PROCESSED')), ('PR', _('PROCESSED')), ('LR', 'LOW RED'), ('LY', 'LOW YELLOW'), ('GR', 'GREEN'),
        ('HY', 'HIGH YELLOW'), ('HR', 'HIGH RED'),)
        model = TagStatusTable
        # add class="paleblue" to <table> tag
        attrs = {'class': 'table-sm table-striped table-bordered table-hover table-responsive mym-table'}
        exclude = ('id','processedTag','statusMediaMillisSinceEpoch')