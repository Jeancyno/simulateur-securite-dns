from django.urls import path

from .views import DnsResolveView


urlpatterns = [
    path("resolve/", DnsResolveView.as_view(), name="dns-resolve"),
]