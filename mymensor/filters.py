import django_filters
from mymensor.models import TagStatusTable

class TagStatusTableFilter(django_filters.FilterSet):
    class Meta:
        model = TagStatusTable
        fields = ('statusTagNumber','statusTagDescription','statusVpNumber', 'statusVpDescription', 'statusMediaTimeStamp', 'statusDBTimeStamp', 'statusTagStateEvaluated')

    @property
    def qs(self):
        parent = super(TagStatusTableFilter, self).qs
        return parent.filter(processedTag__media__vp__asset__assetOwner=self.request.user)