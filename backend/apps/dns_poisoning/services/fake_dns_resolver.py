"""
Résolveur DNS fictif pour la simulation pédagogique.
Ce résolveur utilise uniquement des données fictives et n'effectue aucune résolution DNS réelle.
"""

import logging
import hashlib

from .dns_cache import dns_cache, CacheStatus, DnsCacheEntry


logger = logging.getLogger("dns_simulator")


# Données fictives des domaines et leurs IP légitimes
FAKE_DOMAINS = {
    "www.banque-demo.test": "192.168.1.10",
    "www.exemple.test": "192.168.1.20",
    "www.dns-demo.test": "192.168.1.30",
    "www.secure-demo.test": "192.168.1.40",
    "www.corp-demo.test": "192.168.1.50",
}


class FakeDnsResolver:
    """Résolveur DNS fictif"""

    def __init__(self):
        self.cache = dns_cache

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
            if not part.replace('-', '').isalnum():
                return False
            if part.startswith('-') or part.endswith('-'):
                return False

        return True

    def is_domain_known(self, domain: str) -> bool:
        """Vérifie si le domaine est connu dans le simulateur"""
        return domain in FAKE_DOMAINS

    def get_legitimate_ip(self, domain: str) -> str:
        """Récupère l'IP légitime d'un domaine"""
        if self.is_domain_known(domain):
            return FAKE_DOMAINS[domain]
        # Générer une IP simulée déterministe pour les domaines inconnus
        return self._generate_simulated_ip(domain)

    def _generate_simulated_ip(self, domain: str) -> str:
        """
        Génère une adresse IP simulée de manière déterministe à partir du domaine.
        Utilise une plage privée (10.x.x.x) pour clairement identifier les données de simulation.
        Le même domaine produit toujours la même IP.
        """
        # Utiliser un hash du domaine pour générer des octets déterministes
        hash_obj = hashlib.md5(domain.lower().encode())
        hash_bytes = hash_obj.digest()

        # Prendre les 3 premiers octets du hash pour générer une IP
        # Format: 10.byte1.byte2.byte3
        octet1 = 10  # Plage privée
        octet2 = hash_bytes[0] % 256
        octet3 = hash_bytes[1] % 256
        octet4 = hash_bytes[2] % 256

        return f"{octet1}.{octet2}.{octet3}.{octet4}"

    def resolve(self, domain: str) -> dict:
        """
        Résout un domaine de manière normale.

        Retourne:
        {
            "success": true,
            "domain": "www.banque-demo.test",
            "legitimate_ip": "192.168.1.10",
            "resolved_ip": "192.168.1.10",
            "cache_status": "CLEAN",
            "response_source": "LEGITIMATE"
        }
        """
        # Valider le format du domaine
        if not self.is_domain_valid(domain):
            logger.warning(
                "DNS Poisoning - domaine invalide : %s",
                domain
            )
            return {
                "success": False,
                "error": f"Format de domaine invalide: {domain}"
            }

        legitimate_ip = self.get_legitimate_ip(domain)

        # Vérifier si le domaine est dans le cache
        if self.cache.exists(domain):
            cache_entry = self.cache.get(domain)
            resolved_ip = cache_entry.ip
            cache_status = cache_entry.status.value
            response_source = cache_entry.source
        else:
            # Ajouter au cache avec l'IP légitime
            cache_entry = DnsCacheEntry(
                domain=domain,
                ip=legitimate_ip,
                source="LEGITIMATE",
                status=CacheStatus.CLEAN
            )
            self.cache.set(cache_entry)
            resolved_ip = legitimate_ip
            cache_status = CacheStatus.CLEAN.value
            response_source = "LEGITIMATE"

        logger.info(
            "DNS Poisoning - résolution - domaine=%s, ip=%s, statut_cache=%s, source=%s",
            domain,
            resolved_ip,
            cache_status,
            response_source
        )

        return {
            "success": True,
            "domain": domain,
            "legitimate_ip": legitimate_ip,
            "resolved_ip": resolved_ip,
            "cache_status": cache_status,
            "response_source": response_source
        }

    def simulate_poisoning(self, domain: str, falsified_ip: str) -> dict:
        """
        Simule un empoisonnement DNS.

        Retourne:
        {
            "success": true,
            "domain": "www.banque-demo.test",
            "legitimate_ip": "192.168.1.10",
            "resolved_ip": "192.168.1.99",
            "cache_status": "POISONED",
            "response_source": "FALSIFIED"
        }
        """
        # Valider le format du domaine
        if not self.is_domain_valid(domain):
            logger.warning(
                "DNS Poisoning - domaine invalide : %s",
                domain
            )
            return {
                "success": False,
                "error": f"Format de domaine invalide: {domain}"
            }

        # Valider l'IP falsifiée
        if not self._is_valid_ip(falsified_ip):
            logger.warning(
                "DNS Poisoning - IP falsifiée invalide : domaine=%s, ip=%s",
                domain,
                falsified_ip
            )
            return {
                "success": False,
                "error": f"IP falsifiée invalide: {falsified_ip}"
            }

        legitimate_ip = self.get_legitimate_ip(domain)

        # Injecter l'IP falsifiée dans le cache
        cache_entry = DnsCacheEntry(
            domain=domain,
            ip=falsified_ip,
            source="FALSIFIED",
            status=CacheStatus.POISONED
        )
        self.cache.set(cache_entry)

        logger.warning(
            "DNS Poisoning - empoisonnement simulé : domaine=%s, ip_legitime=%s, ip_falsifiee=%s",
            domain,
            legitimate_ip,
            falsified_ip
        )

        return {
            "success": True,
            "domain": domain,
            "legitimate_ip": legitimate_ip,
            "resolved_ip": falsified_ip,
            "cache_status": CacheStatus.POISONED.value,
            "response_source": "FALSIFIED"
        }

    def reset_cache(self) -> dict:
        """
        Réinitialise le cache DNS simulé.
        """
        self.cache.reset()

        logger.info(
            "DNS Poisoning - cache DNS simulé réinitialisé"
        )

        return {
            "success": True,
            "message": "Cache réinitialisé avec succès"
        }

    def _is_valid_ip(self, ip: str) -> bool:
        """Valide le format d'une adresse IP"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False

        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    def get_all_fake_domains(self) -> list:
        """Retourne la liste des domaines fictifs disponibles"""
        return list(FAKE_DOMAINS.keys())


# Instance singleton du résolveur DNS fictif
fake_dns_resolver = FakeDnsResolver()