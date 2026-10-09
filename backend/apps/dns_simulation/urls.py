from django.urls import path

from .views import DnsResolveView

app_name = 'dns_simulation'

urlpatterns = [
    path("resolve/", DnsResolveView.as_view(), name="resolve_dns"),
]