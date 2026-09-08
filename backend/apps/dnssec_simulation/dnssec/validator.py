import dns.resolver
import dns.dnssec
import dns.rdatatype
import dns.rdataclass
import dns.name
from django.utils import timezone
from ..models import DNSRecord
from .crypto_utils import DNSSECCrypto
from .trust_anchors import TrustAnchorManager
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DNSSECStatus(Enum):
    """Statuts possibles de la validation DNSSEC"""
    VALID = "CHAÎNE VALIDE"
    UNSIGNED = "DOMAINE NON SIGNÉ"
    INVALID = "CHAÎNE ROMPUE OU INVALIDE"
    ERROR = "ERREUR DE VÉRIFICATION"


class DNSSECValidator:
    """Moteur de validation DNSSEC pour domaines réels et simulés"""

    def __init__(self):
        self.trust_anchors = TrustAnchorManager()
        self.resolver = dns.resolver.Resolver()
        
        self.resolver.edns = 4096
        

    # ============================================================
    # MÉTHODES EXISTANTES (pour la simulation)
    # ============================================================

    def validate_response(self, domain_name, record_type, response_value):
        """Valide une réponse DNS avec DNSSEC (mode simulation)"""
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
        """Construit la chaîne de confiance depuis l'ancre racine (simulation)"""
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
        """Valide la signature cryptographique (simulation)"""
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

    # ============================================================
    # NOUVELLES MÉTHODES POUR LES DOMAINES RÉELS
    # ============================================================

    def validate_real_domain(self, domain: str) -> Dict:
        """
        Valide la chaîne DNSSEC d'un domaine réel
        
        Args:
            domain: Nom de domaine à valider
            
        Returns:
            Dict avec le statut et les détails de la validation
        """
        domain = domain.strip().lower()
        
        # Nettoyer le domaine
        if not domain.endswith('.'):
            domain += '.'

        try:
            # 1. Récupérer les enregistrements DNSKEY
            dnskey_result = self._get_dnskey_real(domain)
            
            # 2. Récupérer les enregistrements DS
            ds_result = self._get_ds_real(domain)
            
            # 3. Récupérer les signatures RRSIG
            rrsig_result = self._get_rrsig_real(domain)
            
            # 4. Vérifier la chaîne de confiance
            chain_valid = self._verify_chain_real(domain, dnskey_result, ds_result)
            
            # 5. Déterminer le statut
            status, message = self._determine_status_real(
                dnskey_result,
                ds_result,
                rrsig_result,
                chain_valid
            )
            
            # 6. Construire la chaîne de confiance
            chain = self._build_trust_chain_real(domain, dnskey_result, ds_result)
            
            return {
                "domain": domain.rstrip('.'),
                "status": status.value,
                "has_dnskey": dnskey_result['found'],
                "has_ds": ds_result['found'],
                "has_rrsig": rrsig_result['found'],
                "is_signed": dnskey_result['found'] or ds_result['found'],
                "chain_valid": chain_valid,
                "message": message,
                "details": {
                    'dnskey': dnskey_result,
                    'ds': ds_result,
                    'rrsig': rrsig_result,
                },
                "trust_chain": chain,
                "status_icon": {
                    "CHAÎNE VALIDE": "🟢",
                    "DOMAINE NON SIGNÉ": "🟡",
                    "CHAÎNE ROMPUE OU INVALIDE": "🔴",
                    "ERREUR DE VÉRIFICATION": "⚪"
                }.get(status.value, "⚪")
            }
            
        except dns.resolver.NXDOMAIN:
            return {
                "domain": domain.rstrip('.'),
                "status": "ERREUR DE VÉRIFICATION",
                "has_dnskey": False,
                "has_ds": False,
                "has_rrsig": False,
                "is_signed": False,
                "chain_valid": False,
                "message": "Le domaine n'existe pas",
                "details": {},
                "trust_chain": [],
                "status_icon": "⚪"
            }
        except Exception as e:
            return {
                "domain": domain.rstrip('.'),
                "status": "ERREUR DE VÉRIFICATION",
                "has_dnskey": False,
                "has_ds": False,
                "has_rrsig": False,
                "is_signed": False,
                "chain_valid": False,
                "message": f"Erreur lors de la vérification: {str(e)}",
                "details": {'error': str(e)},
                "trust_chain": [],
                "status_icon": "⚪"
            }

    def _get_dnskey_real(self, domain: str) -> Dict:
        """Récupère les enregistrements DNSKEY pour un domaine réel"""
        try:
            answers = self.resolver.resolve(domain, dns.rdatatype.DNSKEY, dnssec=True)
            return {
                'found': True,
                'count': len(answers),
                'records': [
                    {
                        'flags': rdata.flags,
                        'protocol': rdata.protocol,
                        'algorithm': rdata.algorithm,
                        'key': rdata.key.hex()[:64] + '...' if hasattr(rdata, 'key') else str(rdata)
                    }
                    for rdata in answers
                ]
            }
        except dns.resolver.NoAnswer:
            return {'found': False, 'count': 0, 'records': []}
        except Exception as e:
            return {'found': False, 'count': 0, 'records': [], 'error': str(e)}

    def _get_ds_real(self, domain: str) -> Dict:
        """Récupère les enregistrements DS pour un domaine réel"""
        try:
            # Pour obtenir les DS, il faut interroger la zone parente
            parent = self._get_parent_zone(domain)
            if not parent:
                return {'found': False, 'count': 0, 'records': []}
                
            answers = self.resolver.resolve(parent, dns.rdatatype.DS, dnssec=True)
            return {
                'found': True,
                'count': len(answers),
                'records': [
                    {
                        'key_tag': rdata.key_tag,
                        'algorithm': rdata.algorithm,
                        'digest_type': rdata.digest_type,
                        'digest': rdata.digest.hex()[:32] + '...'
                    }
                    for rdata in answers
                ]
            }
        except dns.resolver.NoAnswer:
            return {'found': False, 'count': 0, 'records': []}
        except Exception as e:
            return {'found': False, 'count': 0, 'records': [], 'error': str(e)}

    def _get_rrsig_real(self, domain: str) -> Dict:
        """Récupère les signatures RRSIG pour un domaine réel"""
        try:
            # Interroger le type A pour obtenir les signatures associées
            answers = self.resolver.resolve(domain, dns.rdatatype.A, dnssec=True)
            
            # Extraire les RRSIG de la réponse
            rrsigs = []
            for rrset in answers.response.answer:
                for rdata in rrset:
                    if rdata.rdtype == dns.rdatatype.RRSIG:
                        rrsigs.append({
                            'covered': str(rdata.covered),
                            'algorithm': rdata.algorithm,
                            'labels': rdata.labels,
                            'original_ttl': rdata.original_ttl,
                            'key_tag': rdata.key_tag,
                            'signer': str(rdata.signer)
                        })
            
            return {
                'found': len(rrsigs) > 0,
                'count': len(rrsigs),
                'records': rrsigs
            }
        except dns.resolver.NoAnswer:
            return {'found': False, 'count': 0, 'records': []}
        except Exception as e:
            return {'found': False, 'count': 0, 'records': [], 'error': str(e)}

    def _get_parent_zone(self, domain: str) -> Optional[str]:
        """Détermine la zone parente pour un domaine"""
        parts = domain.rstrip('.').split('.')
        if len(parts) <= 1:
            return None
        return '.'.join(parts[1:]) + '.'

    def _verify_chain_real(self, domain: str, dnskey: Dict, ds: Dict) -> bool:
        """Vérifie la cohérence entre DS et DNSKEY"""
        # Si pas de DS, la zone peut être signée directement
        if not ds['found']:
            return dnskey['found']
            
        # Si DS trouvé, vérifier qu'il correspond à un DNSKEY
        if ds['found'] and dnskey['found']:
            ds_tags = [r['key_tag'] for r in ds['records']]
            dnskey_tags = [r.get('key_tag', 0) for r in dnskey['records']]
            return any(tag in ds_tags for tag in dnskey_tags)
            
        return False

    def _determine_status_real(self, dnskey: Dict, ds: Dict, rrsig: Dict, chain_valid: bool) -> Tuple[DNSSECStatus, str]:
        """Détermine le statut final de la validation"""
        # Cas 1: Chaîne valide
        if chain_valid and dnskey['found'] and rrsig['found']:
            return DNSSECStatus.VALID, "La chaîne de confiance DNSSEC est valide"
            
        # Cas 2: Domaine non signé
        if not dnskey['found'] and not ds['found'] and not rrsig['found']:
            return DNSSECStatus.UNSIGNED, "Le domaine n'est pas signé avec DNSSEC"
            
        # Cas 3: Chaîne rompue
        if dnskey['found'] and not chain_valid:
            return DNSSECStatus.INVALID, "La chaîne de confiance est rompue (DS/DNSKEY incohérents)"
            
        if dnskey['found'] and not rrsig['found']:
            return DNSSECStatus.INVALID, "DNSKEY présent mais pas de signature RRSIG"
            
        if ds['found'] and not dnskey['found']:
            return DNSSECStatus.INVALID, "DS présent mais pas de DNSKEY correspondant"
            
        return DNSSECStatus.INVALID, "Configuration DNSSEC incomplète"

    def _build_trust_chain_real(self, domain: str, dnskey: Dict, ds: Dict) -> List[Dict]:
        """Construit la chaîne de confiance pour l'affichage"""
        chain = []
        parts = domain.rstrip('.').split('.')
        
        # Ajouter la racine
        chain.append({
            'level': 'root',
            'name': '.',
            'status': 'TRUST_ANCHOR',
            'message': 'Ancre de confiance racine'
        })
        
        # Construire la chaîne
        current = ''
        for part in reversed(parts):
            if current:
                current = f"{part}.{current}"
            else:
                current = part
                
            chain.append({
                'level': 'zone',
                'name': current,
                'has_ds': ds['found'] and current == domain.rstrip('.'),
                'has_dnskey': dnskey['found'] and current == domain.rstrip('.'),
                'status': 'DELEGATION' if ds['found'] and current == domain.rstrip('.') else 'ZONE',
                'message': f"Zone: {current}"
            })
        
        return chain