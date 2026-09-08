from django.utils import timezone
from ..models import DNSRecord
from .crypto_utils import DNSSECCrypto
from .trust_anchors import TrustAnchorManager


class DNSSECValidator:
    def __init__(self):
        self.trust_anchors = TrustAnchorManager()

    def validate_response(self, domain_name, record_type, response_value):
        domain_name = domain_name.strip().lower()
        record_type = record_type.strip().upper()

        dnssec_records = DNSRecord.objects.filter(
            domain_name=domain_name,
            is_dnssec_signed=True
        )

        if not dnssec_records.exists():
            return {
                "status": "INSECURE",
                "chain": [],
                "message": "La zone n'est pas signée avec DNSSEC",
                "validated_at": timezone.now()
            }

        chain = self._build_trust_chain(domain_name)

        if not chain:
            return {
                "status": "BOGUS",
                "chain": [],
                "message": "Impossible de construire une chaîne de confiance valide",
                "validated_at": timezone.now()
            }

        is_valid = self._validate_signature(
            domain_name,
            record_type,
            response_value,
            chain
        )

        if is_valid:
            return {
                "status": "SECURE",
                "chain": chain,
                "message": "Validation DNSSEC réussie",
                "validated_at": timezone.now()
            }
        else:
            return {
                "status": "BOGUS",
                "chain": chain,
                "message": "Échec de la validation cryptographique",
                "validated_at": timezone.now()
            }

    def _build_trust_chain(self, domain_name):
        chain = []
        labels = domain_name.rstrip('.').split('.')
        current_name = ""

        root_anchor = self.trust_anchors.get_root_anchor()
        if not root_anchor:
            return []

        chain.append({
            "name": ".",
            "key_tag": root_anchor.key_tag,
            "algorithm": root_anchor.algorithm,
            "status": "TRUST_ANCHOR",
            "message": "Ancre de confiance racine"
        })

        for label in reversed(labels):
            if current_name:
                current_name = f"{label}.{current_name}"
            else:
                current_name = label

            ds_records = DNSRecord.objects.filter(
                domain_name=current_name,
                record_type="DS",
                is_dnssec_signed=True
            )

            if ds_records.exists():
                dnskey_records = DNSRecord.objects.filter(
                    domain_name=current_name,
                    record_type="DNSKEY",
                    is_dnssec_signed=True
                )

                for ds in ds_records:
                    for dnskey in dnskey_records:
                        ds_hash = DNSSECCrypto.hash_ds(
                            dnskey.value.encode('utf-8'),
                            algorithm=2
                        )
                        if ds_hash.hex() == ds.value[:64]:
                            chain.append({
                                "name": current_name,
                                "ds_record": ds.value,
                                "dnskey": dnskey.value,
                                "key_tag": dnskey.key_tag,
                                "algorithm": dnskey.algorithm,
                                "status": "DELEGATION_VALID",
                                "message": f"Délégation validée pour {current_name}"
                            })
                            break
                    else:
                        continue
                    break
                else:
                    return []
            else:
                dnskey_records = DNSRecord.objects.filter(
                    domain_name=current_name,
                    record_type="DNSKEY",
                    is_dnssec_signed=True
                )

                if dnskey_records.exists():
                    chain.append({
                        "name": current_name,
                        "dnskey": dnskey_records.first().value,
                        "key_tag": dnskey_records.first().key_tag,
                        "algorithm": dnskey_records.first().algorithm,
                        "status": "ZONE_SIGNED",
                        "message": f"Zone {current_name} signée"
                    })

        if len(chain) > 0 and chain[-1].get("status") in ["DELEGATION_VALID", "ZONE_SIGNED"]:
            return chain

        return []

    def _validate_signature(self, domain_name, record_type, value, chain):
        rrsig_record = DNSRecord.objects.filter(
            domain_name=domain_name,
            record_type="RRSIG",
            is_dnssec_signed=True
        ).first()

        if not rrsig_record:
            return False

        dnskey_value = None
        for link in reversed(chain):
            if "dnskey" in link:
                dnskey_value = link["dnskey"]
                break

        if not dnskey_value:
            return False

        rrset_data = f"{domain_name}. 300 IN {record_type} {value}".encode('utf-8')
        algorithm = rrsig_record.algorithm or 8

        try:
            return DNSSECCrypto.verify_rrsig(
                rrset_data,
                rrsig_record.value,
                dnskey_value,
                algorithm
            )
        except Exception:
            return False