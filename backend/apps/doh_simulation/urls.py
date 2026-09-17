from django.urls import path

from .views import DohCompareView


urlpatterns = [
    path("compare/", DohCompareView.as_view(), name="doh-compare"),
]
