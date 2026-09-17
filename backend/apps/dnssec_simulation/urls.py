from django.urls import path

from .views import DnssecVerifyView


urlpatterns = [
    path("verify/", DnssecVerifyView.as_view(), name="dnssec-verify"),
]
