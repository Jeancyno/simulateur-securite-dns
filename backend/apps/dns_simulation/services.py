from django.utils import timezone

from .models import DNSRecord, DNSCacheEntry, DNSQuery


class DNSResolver:

    def resolve(self, domain_name, record_type="A", client_ip=None):
        domain_name = domain_name.strip().lower()
        record_type = record_type.upper() 

        #1. Verifier le cache

        cache_entry = DNSCacheEntry.objects.filter(domain_name=domain_name, record_type=record_type).first()

        if cache_entry:
            # Verification simple de l'expiration du TTL
            elapsed_time = (timezone.now() - cache_entry.cached_at).total_seconds()

            if elapsed_time < cache_entry.ttl:
                status = (
                    "poisoned" 
                    if cache_entry.poisoned 
                    else "cache_hit"
                )

                DNSQuery.objects.create(
                    domain_name=domain_name,
                    record_type=record_type,
                    client_ip=client_ip,
                    response_value=cache_entry.value,
                    status=status
                )
                return {
                    "success": True,
                    "domain_name": domain_name,
                    "record_type": record_type,
                    "value": cache_entry.value,
                    "status": status,
                    "from_cache": True,
                    "poisoned": cache_entry.poisoned,
                }

            # Le TTL a expiré, donc on supprime l'entrée du cache
            cache_entry.delete()

        #2. Si pas dans le cache, on cherche dans les enregistrements DNS
        dns_records = DNSRecord.objects.filter(
            domain_name=domain_name, 
            record_type=record_type
        ).first()

        if not dns_records:
            DNSQuery.objects.create(
                domain_name=domain_name,
                record_type=record_type,
                client_ip=client_ip,
                response_value=None,
                status="cache_miss",
            )

            return {
                "success": False,
                "domain_name": domain_name,
                "record_type": record_type,
                "value": None,
                "status": "not_found",
                "from_cache": False,
                "poisoned": False,
            }

        #3. Si trouvé, on ajoute au cache et on retourne la réponse
        DNSCacheEntry.objects.create(
            domain_name=domain_name,
            record_type=record_type,
            value=dns_record.value,
            ttl=dns_record.ttl,
            poisoned=False
        )

        #4. On enregistre la requête DNS
        DNSQuery.objects.create(
            domain_name=domain_name,
            record_type=record_type,
            client_ip=client_ip,
            response_value=dns_record.value,
            status="cache_miss"
        )

        return {
            "success": True,
            "domain_name": domain_name,
            "record_type": record_type,
            "value": dns_record.value,
            "status": "cache_miss",
            "from_cache": False,
            "poisoned": False,
        }

class DNSCachePoisoningSimulator:

    def poison(self, domain_name, record_type="A", malicious_value="    ", ttl=300):
        domain_name = domain_name.strip().lower()
        record_type = record_type.upper()
        malicious_value = malicious_value.strip()

        # On vérifie si l'enregistrement DNS existe
        dns_record = DNSRecord.objects.filter(
            domain_name=domain_name, 
            record_type=record_type
        ).first()

        if not dns_record:
            return {
                "success": False,
                "error": "Enregistrement DNS non trouvé pour le domaine et le type spécifiés.",
            }

        DNSCacheEntry.objects.filter(
            domain_name=domain_name, 
            record_type=record_type
        ).delete()

        # On crée ou met à jour l'entrée du cache avec la valeur malveillante
        cache_entry, created = DNSCacheEntry.objects.update_or_create(
            domain_name=domain_name,
            record_type=record_type,
            defaults={
                "value": malicious_value,
                "ttl": ttl,
                "poisoned": True,
            }
        )

        return {
            "success": True,
            "message": "Cache DNS empoisonné avec succès.",
            "domain_name": domain_name,
            "record_type": record_type,
            "legitimate_value": dns_record.value,
            "poisoned_value": cache_entry.value,
            "ttl": cache_entry.ttl,
            "poisoned": cache_entry.poisoned,   
        }  