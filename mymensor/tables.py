import django_tables2 as tables
from mymensor.models import TagStatusTable

class TagStatusTableClass(tables.Table):
    class Meta:
        model = TagStatusTable
        # add class="paleblue" to <table> tag
        attrs = {'class': 'table-sm table-striped table-bordered table-hover table-responsive mym-table'}
        exclude = ('id','processedTag','statusMediaMillisSinceEpoch')