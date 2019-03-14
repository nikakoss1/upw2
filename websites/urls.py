from django.conf.urls import url
from django.contrib import admin
from .views import WebsiteDetailView, update, update_stop

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', WebsiteDetailView.as_view(), name="website_detail"),
    url(r'^update$', update, name="update"),
    url(r'^update-stop$', update_stop, name="update_stop"),
]