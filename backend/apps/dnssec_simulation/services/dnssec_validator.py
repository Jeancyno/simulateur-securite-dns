"""
Service de validation DNSSEC utilisant dnspython.
Ce service effectue des requêtes DNS réelles pour valider la chaîne de confiance DNSSEC.
"""

import logging
import dns.resolver
import dns.dnssec
import dns.name
import dns.rdatatype
import dns.rdataclass
import dns.rdataset
from datetime import datetime
from typing import Dict, Optional, Tuple

logger = logging.getLogger("dns_simulator")


class DnssecValidator:
    """Validateur DNSSEC utilisant dnspython"""

    # Résolveurs DNS à utiliser pour la validation DNSSEC
    RESOLVERS = [
        '8.8.8.8',      # Google DNS
        '1.1.1.1',      # Cloudflare DNS
        '9.9.9.9',      # Quad9 DNS
    ]

    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.nameservers = self.RESOLVERS
        self.resolver.timeout = 5.0  # Timeout de 5 secondes
        self.resolver.lifetime = 10.0  # Lifetime maximum de 10 secondes

    def is_domain_valid(self, domain: str) -> bool:
        """Valide le format d'un domaine"""
        if not domain or not isinstance(domain, str):
            return False

        if len(domain) > 253:
            return False

        # Validation basique du format de domaine
        parts = domain.split('.')
        if len(parts) < 2:
            return False

        for part in parts:
            if not part:
                return False
            if not part.replace('-', '').replace('_', '').isalnum():
                return False
            if part.startswith('-') or part.endswith('-'):
                return False

        return True

    def verify_dnssec(self, domain: str) -> Dict:
        """
        Vérifie la validation DNSSEC d'un domaine.

        Retourne:
        {
            "success": True/False,
            "domain": "example.com",
            "status": "VALID" | "UNSIGNED" | "INVALID",
            "dnskey": {...},
            "ds": {...},
            "rrsig": {...},
            "error": "message d'erreur" (si échec)
        }
        """
        if not self.is_domain_valid(domain):
            logger.warning(
                "DNSSEC - domaine invalide : %s",
                domain
            )
            return {
                "success": False,
                "error": "Format de domaine invalide"
            }

        try:
            logger.info(
                "DNSSEC - début de validation pour : %s",
                domain
            )

            # 1. Vérifier si le domaine a des enregistrements DNSKEY
            dnskey_info = self._get_dnskey_info(domain)
            if not dnskey_info['exists']:
                logger.info(
                    "DNSSEC - domaine non signé (pas de DNSKEY) : %s",
                    domain
                )
                return {
                    "success": True,
                    "domain": domain,
                    "status": "UNSIGNED",
                    "dnskey": dnskey_info,
                    "ds": {"exists": False, "error": "Domaine non signé"},
                    "rrsig": {"exists": False, "error": "Domaine non signé"},
                    "message": "Le domaine n'est pas signé avec DNSSEC"
                }

            # 2. Vérifier les enregistrements DS (Delegation Signer)
            ds_info = self._get_ds_info(domain)

            # 3. Vérifier les signatures RRSIG
            rrsig_info = self._get_rrsig_info(domain)

            # 4. Tenter une validation complète de la chaîne de confiance
            validation_result = self._validate_chain_of_trust(domain)

            logger.info(
                "DNSSEC - validation terminée pour %s : statut=%s",
                domain,
                validation_result['status']
            )

            return {
                "success": True,
                "domain": domain,
                "status": validation_result['status'],
                "dnskey": dnskey_info,
                "ds": ds_info,
                "rrsig": rrsig_info,
                "chain_details": validation_result.get('details', {}),
                "message": validation_result.get('message', '')
            }

        except dns.resolver.NXDOMAIN:
            logger.warning(
                "DNSSEC - domaine inexistant : %s",
                domain
            )
            return {
                "success": False,
                "error": "Le domaine n'existe pas (NXDOMAIN)"
            }

        except dns.resolver.Timeout:
            logger.error(
                "DNSSEC - timeout lors de la validation : %s",
                domain
            )
            return {
                "success": False,
                "error": "Timeout lors de la résolution DNS"
            }

        except dns.resolver.NoAnswer:
            logger.warning(
                "DNSSEC - pas de réponse pour : %s",
                domain
            )
            return {
                "success": False,
                "error": "Pas de réponse DNS pour ce domaine"
            }

        except Exception as e:
            logger.error(
                "DNSSEC - erreur lors de la validation de %s : %s",
                domain,
                str(e)
            )
            return {
                "success": False,
                "error": f"Erreur lors de la validation DNSSEC : {str(e)}"
            }

    def _get_dnskey_info(self, domain: str) -> Dict:
        """Récupère les informations DNSKEY du domaine"""
        try:
            answer = self.resolver.resolve(domain, 'DNSKEY', raise_on_no_answer=False)

            if not answer or len(answer) == 0:
                return {
                    "exists": False,
                    "error": "Pas d'enregistrement DNSKEY trouvé"
                }

            dnskey_records = []
            for rdata in answer:
                dnskey_records.append({
                    "flags": rdata.flags,
                    "protocol": rdata.protocol,
                    "algorithm": rdata.algorithm,
                    "key_tag": self._calculate_key_tag(rdata),
                    "key_length": len(rdata.key) * 8  # en bits
                })

            return {
                "exists": True,
                "count": len(dnskey_records),
                "records": dnskey_records[:3],  # Limiter à 3 enregistrements
                "description": f"{len(dnskey_records)} clé(s) DNSKEY trouvée(s)"
            }

        except Exception as e:
            logger.error(
                "DNSSEC - erreur récupération DNSKEY pour %s : %s",
                domain,
                str(e)
            )
            return {
                "exists": False,
                "error": f"Erreur lors de la récupération DNSKEY : {str(e)}"
            }

    def _get_ds_info(self, domain: str) -> Dict:
        """Récupère les informations DS (Delegation Signer) du domaine"""
        try:
            # Pour les enregistrements DS, il faut interroger le serveur parent
            # On va essayer de récupérer les DS pour le domaine
            answer = self.resolver.resolve(domain, 'DS', raise_on_no_answer=False)

            if not answer or len(answer) == 0:
                return {
                    "exists": False,
                    "error": "Pas d'enregistrement DS trouvé (domaine non signé ou racine)"
                }

            ds_records = []
            for rdata in answer:
                ds_records.append({
                    "key_tag": rdata.key_tag,
                    "algorithm": rdata.algorithm,
                    "digest_type": rdata.digest_type,
                    "digest": rdata.digest.hex() if hasattr(rdata.digest, 'hex') else str(rdata.digest)
                })

            return {
                "exists": True,
                "count": len(ds_records),
                "records": ds_records[:3],
                "description": f"{len(ds_records)} enregistrement(s) DS trouvé(s)"
            }

        except dns.resolver.NoAnswer:
            # Pas de DS = domaine non signé ou zone racine
            return {
                "exists": False,
                "error": "Pas d'enregistrement DS (domaine non signé ou zone racine)"
            }

        except Exception as e:
            logger.error(
                "DNSSEC - erreur récupération DS pour %s : %s",
                domain,
                str(e)
            )
            return {
                "exists": False,
                "error": f"Erreur lors de la récupération DS : {str(e)}"
            }

    def _get_rrsig_info(self, domain: str) -> Dict:
        """Récupère les informations RRSIG du domaine"""
        try:
            # On essaie de récupérer les RRSIG pour un enregistrement A
            answer = self.resolver.resolve(domain, 'A', raise_on_no_answer=False)

            if not answer or len(answer) == 0:
                return {
                    "exists": False,
                    "error": "Pas d'enregistrement A trouvé pour vérifier RRSIG"
                }

            # Maintenant on essaie de récupérer les RRSIG pour l'enregistrement A
            try:
                rrsig_answer = self.resolver.resolve(domain, 'RRSIG', raise_on_no_answer=False)

                if not rrsig_answer or len(rrsig_answer) == 0:
                    return {
                        "exists": False,
                        "error": "Pas d'enregistrement RRSIG trouvé"
                    }

                rrsig_records = []
                for rdata in rrsig_answer:
                    if rdata.covers() == dns.rdatatype.A:  # On s'intéresse aux signatures pour les enregistrements A
                        rrsig_records.append({
                            "type_covered": dns.rdatatype.to_text(rdata.covers()),
                            "algorithm": rdata.algorithm,
                            "labels": rdata.labels,
                            "original_ttl": rdata.original_ttl,
                            "signature_expiration": datetime.fromtimestamp(rdata.expiration).isoformat(),
                            "signature_inception": datetime.fromtimestamp(rdata.inception).isoformat(),
                            "key_tag": rdata.key_tag,
                            "signer_name": str(rdata.signer)
                        })

                if len(rrsig_records) == 0:
                    return {
                        "exists": False,
                        "error": "Pas de signature RRSIG pour les enregistrements A"
                    }

                return {
                    "exists": True,
                    "count": len(rrsig_records),
                    "records": rrsig_records[:3],
                    "description": f"{len(rrsig_records)} signature(s) RRSIG trouvée(s)"
                }

            except Exception as e:
                return {
                    "exists": False,
                    "error": f"Erreur lors de la récupération RRSIG : {str(e)}"
                }

        except Exception as e:
            logger.error(
                "DNSSEC - erreur récupération RRSIG pour %s : %s",
                domain,
                str(e)
            )
            return {
                "exists": False,
                "error": f"Erreur lors de la récupération RRSIG : {str(e)}"
            }

    def _validate_chain_of_trust(self, domain: str) -> Dict:
        """
        Tente de valider la chaîne de confiance DNSSEC complète.

        Note: La validation complète de la chaîne de confiance avec dnspython
        nécessite une configuration complexe avec les ancrages de confiance.
        Pour ce simulateur pédagogique, nous utilisons une approche simplifiée
        basée sur la présence des enregistrements DNSSEC requis.
        """
        try:
            # Vérifier si nous avons DNSKEY
            dnskey_answer = self.resolver.resolve(domain, 'DNSKEY', raise_on_no_answer=False)
            has_dnskey = dnskey_answer and len(dnskey_answer) > 0

            if not has_dnskey:
                return {
                    "status": "UNSIGNED",
                    "message": "Le domaine n'est pas signé avec DNSSEC (pas de DNSKEY)",
                    "details": {
                        "has_dnskey": False,
                        "has_ds": False,
                        "has_rrsig": False
                    }
                }

            # Vérifier si nous avons DS (pour les zones non-racines)
            try:
                ds_answer = self.resolver.resolve(domain, 'DS', raise_on_no_answer=False)
                has_ds = ds_answer and len(ds_answer) > 0
            except:
                has_ds = False

            # Vérifier si nous avons RRSIG
            try:
                rrsig_answer = self.resolver.resolve(domain, 'RRSIG', raise_on_no_answer=False)
                has_rrsig = rrsig_answer and len(rrsig_answer) > 0
            except:
                has_rrsig = False

            # Logique simplifiée de validation
            if has_dnskey and has_rrsig:
                # Si nous avons DNSKEY et RRSIG, on considère que c'est signé
                # La validation cryptographique complète nécessiterait plus de configuration
                if has_ds:
                    return {
                        "status": "VALID",
                        "message": "La chaîne de confiance DNSSEC semble valide (DNSKEY, DS et RRSIG présents)",
                        "details": {
                            "has_dnskey": True,
                            "has_ds": True,
                            "has_rrsig": True,
                            "validation_method": "simplified_presence_check"
                        }
                    }
                else:
                    # Pour la zone racine ou TLD, il peut ne pas y avoir de DS
                    return {
                        "status": "VALID",
                        "message": "La chaîne de confiance DNSSEC semble valide (DNSKEY et RRSIG présents, zone racine/TLD)",
                        "details": {
                            "has_dnskey": True,
                            "has_ds": False,
                            "has_rrsig": True,
                            "validation_method": "simplified_presence_check",
                            "note": "Pas de DS attendu pour cette zone (racine ou TLD)"
                        }
                    }
            elif has_dnskey and not has_rrsig:
                return {
                    "status": "INVALID",
                    "message": "DNSKEY présent mais pas de signatures RRSIG - chaîne incomplète",
                    "details": {
                        "has_dnskey": True,
                        "has_ds": has_ds,
                        "has_rrsig": False,
                        "validation_method": "simplified_presence_check"
                    }
                }
            else:
                return {
                    "status": "UNSIGNED",
                    "message": "Le domaine n'est pas signé avec DNSSEC",
                    "details": {
                        "has_dnskey": has_dnskey,
                        "has_ds": has_ds,
                        "has_rrsig": has_rrsig,
                        "validation_method": "simplified_presence_check"
                    }
                }

        except Exception as e:
            logger.error(
                "DNSSEC - erreur validation chaîne pour %s : %s",
                domain,
                str(e)
            )
            return {
                "status": "INVALID",
                "message": f"Erreur lors de la validation de la chaîne de confiance : {str(e)}",
                "details": {
                    "error": str(e)
                }
            }

    def _calculate_key_tag(self, dnskey_rdata) -> int:
        """Calcule le key tag d'un DNSKEY (simplifié)"""
        try:
            # dnspython a une méthode pour calculer le key tag
            return dns.dnssec.key_tag(dnskey_rdata)
        except:
            # Fallback: utiliser une valeur basée sur les flags
            return dnskey_rdata.flags % 65535


# Instance singleton du validateur DNSSEC
dnssec_validator = DnssecValidator()
