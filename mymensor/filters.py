import django_filters
from mymensor.models import TagStatusTable

class TagStatusTableFilter(django_filters.FilterSet):
    class Meta:
        model = TagStatusTable
        fields = ('statusTagNumber','statusTagDescription','statusVpNumber', 'statusVpDescription', 'statusMediaTimeStamp', 'statusDBTimeStamp', 'statusTagStateEvaluated')

