import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from .services import DNSResolver, DNSCachePoisoningSimulator
from .models import DNSRecord, TrustAnchor
from .dnssec.validator import DNSSECValidator


@require_GET
def resolve_dns(request):
    domain_name = request.GET.get("domain_name", "").strip()
    record_type = request.GET.get("record_type", "A").strip().upper()
    client_ip = request.META.get("REMOTE_ADDR")

    if not domain_name:
        return JsonResponse(
            {"error": "Le paramètre 'domain_name' est requis"},
            status=400
        )

    resolver = DNSResolver()
    result = resolver.resolve(domain_name, record_type, client_ip)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def create_dns_record(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Le corps de la requête doit être un JSON valide"},
            status=400
        )

    domain_name = data.get("domain_name", "").strip().lower()
    record_type = data.get("record_type", "A").strip().upper()
    value = data.get("value", "").strip()
    ttl = data.get("ttl", 300)
    is_dnssec_signed = data.get("is_dnssec_signed", False)
    algorithm = data.get("algorithm", None)
    key_tag = data.get("key_tag", None)

    if not domain_name or not value:
        return JsonResponse(
            {"error": "Les champs 'domain_name' et 'value' sont requis"},
            status=400
        )

    dns_record, created = DNSRecord.objects.get_or_create(
        domain_name=domain_name,
        record_type=record_type,
        value=value,
        defaults={
            "ttl": ttl,
            "authoritative": True,
            "is_dnssec_signed": is_dnssec_signed,
            "algorithm": algorithm,
            "key_tag": key_tag,
        }
    )

    if not created:
        dns_record.ttl = ttl
        dns_record.is_dnssec_signed = is_dnssec_signed
        dns_record.algorithm = algorithm
        dns_record.key_tag = key_tag
        dns_record.save()

    return JsonResponse({
        "success": True,
        "created": created,
        "domain_name": dns_record.domain_name,
        "record_type": dns_record.record_type,
        "value": dns_record.value,
        "ttl": dns_record.ttl,
        "is_dnssec_signed": dns_record.is_dnssec_signed,
        "algorithm": dns_record.algorithm,
        "key_tag": dns_record.key_tag
    }, status=201 if created else 200)


@csrf_exempt
@require_POST
def poison_dns_cache(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Le corps de la requête doit être un JSON valide"},
            status=400
        )

    domain_name = data.get("domain_name", "").strip().lower()
    record_type = data.get("record_type", "A").strip().upper()
    malicious_value = data.get("malicious_value", "203.0.113.50").strip()
    ttl = data.get("ttl", 300)

    if not domain_name:
        return JsonResponse(
            {"error": "Le paramètre 'domain_name' est requis"},
            status=400
        )

    if not malicious_value:
        return JsonResponse(
            {"error": "Le paramètre 'malicious_value' est requis"},
            status=400
        )

    simulator = DNSCachePoisoningSimulator()
    result = simulator.poison(domain_name, record_type, malicious_value, ttl)

    if not result.get("success", False):
        return JsonResponse(result, status=400)

    return JsonResponse(result, status=201)


@csrf_exempt
@require_POST
def validate_dnssec(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Le corps de la requête doit être un JSON valide"},
            status=400
        )

    domain_name = data.get("domain_name", "").strip().lower()
    record_type = data.get("record_type", "A").strip().upper()
    response_value = data.get("response_value", "").strip()

    if not domain_name:
        return JsonResponse(
            {"error": "Le paramètre 'domain_name' est requis"},
            status=400
        )

    if not response_value:
        return JsonResponse(
            {"error": "Le paramètre 'response_value' est requis"},
            status=400
        )

    validator = DNSSECValidator()
    result = validator.validate_response(domain_name, record_type, response_value)

    return JsonResponse({
        "success": True,
        "domain_name": domain_name,
        "record_type": record_type,
        "dnssec_status": result["status"],
        "chain": result.get("chain", []),
        "message": result.get("message", ""),
        "validated_at": result["validated_at"].isoformat()
    })


@csrf_exempt
@require_POST
def add_trust_anchor(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Le corps de la requête doit être un JSON valide"},
            status=400
        )

    name = data.get("name", ".").strip()
    key_tag = data.get("key_tag")
    algorithm = data.get("algorithm")
    public_key = data.get("public_key", "").strip()

    if not key_tag or not algorithm or not public_key:
        return JsonResponse(
            {"error": "Les champs 'key_tag', 'algorithm' et 'public_key' sont requis"},
            status=400
        )

    anchor, created = TrustAnchor.objects.get_or_create(
        name=name,
        key_tag=key_tag,
        algorithm=algorithm,
        defaults={"public_key": public_key}
    )

    return JsonResponse({
        "success": True,
        "created": created,
        "name": anchor.name,
        "key_tag": anchor.key_tag,
        "algorithm": anchor.algorithm
    }, status=201 if created else 200)


@require_GET
def get_dnssec_status(request):
    domain_name = request.GET.get("domain_name", "").strip().lower()

    if not domain_name:
        return JsonResponse(
            {"error": "Le paramètre 'domain_name' est requis"},
            status=400
        )

    dnssec_records = DNSRecord.objects.filter(
        domain_name=domain_name,
        is_dnssec_signed=True
    )

    cache_entries = DNSCacheEntry.objects.filter(
        domain_name=domain_name
    )

    return JsonResponse({
        "domain_name": domain_name,
        "is_signed": dnssec_records.exists(),
        "signature_count": dnssec_records.count(),
        "cache_entries": [
            {
                "record_type": entry.record_type,
                "value": entry.value,
                "dnssec_status": entry.dnssec_status,
                "poisoned": entry.poisoned,
                "validated_at": entry.validated_at.isoformat() if entry.validated_at else None
            }
            for entry in cache_entries
        ]
    })