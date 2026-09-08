from django.urls import path

from .views import  (
    resolve_dns, 
    create_dns_record, 
    poison_dns_cache,
)  



urlpatterns = [
    path("resolve/", resolve_dns, name="resolve_dns"),
    path("create/", create_dns_record, name="create_dns_record"),  
    path("poison/", poison_dns_cache, name="poison_dns_cache"),
]