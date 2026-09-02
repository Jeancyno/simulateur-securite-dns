"""
URL configuration for DNS poisoning API.
"""

from django.urls import path
from .views import resolve_dns, simulate_poisoning, reset_cache, get_fake_domains

app_name = 'dns_poisoning'

urlpatterns = [
    path('resolve/', resolve_dns, name='resolve_dns'),
    path('poison/', simulate_poisoning, name='simulate_poisoning'),
    path('reset/', reset_cache, name='reset_cache'),
    path('domains/', get_fake_domains, name='get_fake_domains'),
]
