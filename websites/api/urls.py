from django.conf.urls import  url
from websites.api.views import (
    DubicarsAdRetrieveAPIView,
    DubicarsAdListAPIView,
    )


urlpatterns = [
    url(r'^dubicars/ads$', DubicarsAdListAPIView.as_view(), name='dubicarsad_list_api'),
    url(r'^dubicars/ads/(?P<pk>\d+)/$', DubicarsAdRetrieveAPIView.as_view(), name='dubicarsad_detail_api'),
]