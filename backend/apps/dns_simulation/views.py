import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import DNSRecord
from .services import DNSResolver, DNSCachePoisoningSimulator


@require_GET
def resolve_dns(request):
    domain_name = request.GET.get("domain_name", "").strip().lower()
    record_type = request.GET.get("record_type", "A").strip().upper()
    client_ip = request.GET.get("client_ip", "")

    if not domain_name:
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'domain_name' est requis.",
            },
            status=400,
        )

    resolver = DNSResolver()

    result = resolver.resolve(
        domain_name=domain_name,
        record_type=record_type,
        client_ip=client_ip,
    )

    return JsonResponse(result)


@csrf_exempt
@require_POST
def create_dns_record(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "error": "Le corps de la requête doit être un JSON valide.",
            },
            status=400,
        )

    domain_name = data.get("domain_name", "").strip().lower()
    record_type = data.get("record_type", "A").strip().upper()
    value = data.get("value", "").strip()
    ttl = data.get("ttl", 300)

    if not domain_name:
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'domain_name' est requis.",
            },
            status=400,
        )

    if not value:
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'value' est requis.",
            },
            status=400,
        )

    try:
        ttl = int(ttl)

        if ttl <= 0:
            raise ValueError

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'ttl' doit être un entier positif.",
            },
            status=400,
        )

    dns_record, created = DNSRecord.objects.update_or_create(
        domain_name=domain_name,
        record_type=record_type,
        defaults={
            "value": value,
            "ttl": ttl,
            "authoritative": True,
        },
    )

    return JsonResponse(
        {
            "success": True,
            "created": created,
            "message": (
                "Enregistrement DNS créé avec succès."
                if created
                else "Enregistrement DNS mis à jour avec succès."
            ),
            "dns_record": {
                "id": dns_record.id,
                "domain_name": dns_record.domain_name,
                "record_type": dns_record.record_type,
                "value": dns_record.value,
                "ttl": dns_record.ttl,
                "authoritative": dns_record.authoritative,
            },
        },
        status=201 if created else 200,
    )

@csrf_exempt
@require_POST
def poison_dns_cache(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "error": "Le corps de la requête doit être un JSON valide.",
            },
            status=400,
        )

    domain_name = data.get("domain_name", "").strip().lower()
    record_type = data.get("record_type", "A").strip().upper()
    malicious_value = data.get(
        "malicious_value", ""
    ).strip()
    ttl = data.get("ttl", 300)

    if not domain_name:
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'domain_name' est requis.",
            },
            status=400,
        )

    if not malicious_value:
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'malicious_value' est requis.",
            },
            status=400,
        )

    try:
        ttl = int(ttl)

        if ttl <= 0:
            raise ValueError

    except (ValueError, TypeError):
        return JsonResponse(
            {
                "success": False,
                "error": "Le paramètre 'ttl' doit être un entier positif.",
            },
            status=400,
        )

    simulator = DNSCachePoisoningSimulator()
    result = simulator.poison(
        domain_name=domain_name,
        record_type=record_type,
        malicious_value=malicious_value,
        ttl=ttl
    )

    if not result["success"]:
        return JsonResponse(result, status=404)

    return JsonResponse(result)