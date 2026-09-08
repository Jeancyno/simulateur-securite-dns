from django.urls import path
from .views import (
    resolve_dns,
    create_dns_record,
    poison_dns_cache,
    validate_dnssec,
    add_trust_anchor,
    get_dnssec_status,
    validate_real_domain,
)

urlpatterns = [
    path("resolve/", resolve_dns, name="resolve_dns"),
    path("create/", create_dns_record, name="create_dns_record"),
    path("poison/", poison_dns_cache, name="poison_dns_cache"),
    path("dnssec/validate/", validate_dnssec, name="validate_dnssec"),
    path("dnssec/trust-anchor/", add_trust_anchor, name="add_trust_anchor"),
    path("dnssec/status/", get_dnssec_status, name="get_dnssec_status"),
    path("dnssec/validate-real-domain/", validate_real_domain, name="validate_real_domain"),
]