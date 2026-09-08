from django.utils import timezone
from .models import DNSRecord, DNSCacheEntry, DNSQuery
from .dnssec.validator import DNSSECValidator


class DNSResolver:
    def __init__(self):
        self.dnssec_validator = DNSSECValidator()

    def resolve(self, domain_name, record_type="A", client_ip=None):
        domain_name = domain_name.strip().lower()
        record_type = record_type.strip().upper()

        cache_entry = DNSCacheEntry.objects.filter(
            domain_name=domain_name,
            record_type=record_type
        ).first()

        if cache_entry:
            age = (timezone.now() - cache_entry.cached_at).total_seconds()

            if age < cache_entry.ttl:
                if cache_entry.dnssec_status == "UNKNOWN":
                    validation_result = self.dnssec_validator.validate_response(
                        domain_name,
                        record_type,
                        cache_entry.value
                    )
                    cache_entry.dnssec_status = validation_result["status"]
                    cache_entry.validated_at = validation_result["validated_at"]
                    cache_entry.save()

                DNSQuery.objects.create(
                    domain_name=domain_name,
                    record_type=record_type,
                    client_ip=client_ip,
                    response_value=cache_entry.value,
                    status="poisoned" if cache_entry.poisoned else "cache_hit"
                )

                return {
                    "success": True,
                    "domain_name": domain_name,
                    "record_type": record_type,
                    "value": cache_entry.value,
                    "status": "poisoned" if cache_entry.poisoned else "cache_hit",
                    "from_cache": True,
                    "poisoned": cache_entry.poisoned,
                    "dnssec_status": cache_entry.dnssec_status,
                    "validated_at": cache_entry.validated_at.isoformat() if cache_entry.validated_at else None
                }

        dns_records = DNSRecord.objects.filter(
            domain_name=domain_name,
            record_type=record_type
        )

        if not dns_records.exists():
            DNSQuery.objects.create(
                domain_name=domain_name,
                record_type=record_type,
                client_ip=client_ip,
                response_value=None,
                status="not_found"
            )
            return {
                "success": False,
                "domain_name": domain_name,
                "record_type": record_type,
                "value": None,
                "status": "not_found",
                "from_cache": False,
                "poisoned": False,
                "dnssec_status": "UNKNOWN"
            }

        dns_record = dns_records.first()

        validation_result = self.dnssec_validator.validate_response(
            domain_name,
            record_type,
            dns_record.value
        )

        cache_entry = DNSCacheEntry.objects.create(
            domain_name=domain_name,
            record_type=record_type,
            value=dns_record.value,
            ttl=dns_record.ttl,
            poisoned=False,
            dnssec_status=validation_result["status"],
            validated_at=validation_result["validated_at"]
        )

        status = f"dnssec_{validation_result['status'].lower()}"
        DNSQuery.objects.create(
            domain_name=domain_name,
            record_type=record_type,
            client_ip=client_ip,
            response_value=dns_record.value,
            status=status
        )

        return {
            "success": True,
            "domain_name": domain_name,
            "record_type": record_type,
            "value": dns_record.value,
            "status": "cache_miss",
            "from_cache": False,
            "poisoned": False,
            "dnssec_status": validation_result["status"],
            "dnssec_chain": validation_result.get("chain", []),
            "dnssec_message": validation_result.get("message", ""),
            "validated_at": validation_result["validated_at"].isoformat()
        }


class DNSCachePoisoningSimulator:
    def poison(self, domain_name, record_type="A", malicious_value="203.0.113.50", ttl=300):
        domain_name = domain_name.strip().lower()
        record_type = record_type.strip().upper()
        malicious_value = malicious_value.strip()

        dns_records = DNSRecord.objects.filter(
            domain_name=domain_name,
            record_type=record_type,
        )

        if not dns_records.exists():
            return {
                "success": False,
                "error": f"Aucun enregistrement DNS légitime trouvé pour {domain_name} ({record_type})",
            }

        is_legitimate = dns_records.filter(value=malicious_value).exists()

        if is_legitimate:
            return {
                "success": False,
                "error": f"L'IP {malicious_value} est déjà un enregistrement légitime pour {domain_name}",
            }

        validator = DNSSECValidator()
        validation_result = validator.validate_response(
            domain_name,
            record_type,
            malicious_value
        )

        DNSCacheEntry.objects.filter(
            domain_name=domain_name,
            record_type=record_type,
        ).delete()

        cache_entry = DNSCacheEntry.objects.create(
            domain_name=domain_name,
            record_type=record_type,
            value=malicious_value,
            ttl=ttl,
            poisoned=True,
            dnssec_status=validation_result["status"],
            validated_at=validation_result["validated_at"]
        )

        return {
            "success": True,
            "message": "Empoisonnement DNS simulé avec succès",
            "domain_name": domain_name,
            "record_type": record_type,
            "legitimate_values": [r.value for r in dns_records],
            "poisoned_value": cache_entry.value,
            "ttl": cache_entry.ttl,
            "poisoned": cache_entry.poisoned,
            "dnssec_status": cache_entry.dnssec_status,
            "validated_at": cache_entry.validated_at.isoformat()
        }