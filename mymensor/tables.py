import django_tables2 as tables
from mymensor.models import TagStatusTable

class TagSatatusTableClass(tables.Table):
    class Meta:
        model = TagStatusTable
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
