"""
Résolveur DNS fictif pour la simulation pédagogique.
Ce résolveur utilise uniquement des données fictives et n'effectue aucune résolution DNS réelle.
"""

from .dns_cache import dns_cache, CacheStatus, DnsCacheEntry


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
    
    def is_domain_known(self, domain: str) -> bool:
        """Vérifie si le domaine est connu dans le simulateur"""
        return domain in FAKE_DOMAINS
    
    def get_legitimate_ip(self, domain: str) -> str:
        """Récupère l'IP légitime d'un domaine"""
        if not self.is_domain_known(domain):
            raise ValueError(f"Domaine inconnu dans le simulateur: {domain}")
        return FAKE_DOMAINS[domain]
    
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
        if not self.is_domain_known(domain):
            return {
                "success": False,
                "error": f"Domaine inconnu dans le simulateur: {domain}"
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
        if not self.is_domain_known(domain):
            return {
                "success": False,
                "error": f"Domaine inconnu dans le simulateur: {domain}"
            }
        
        # Valider l'IP falsifiée
        if not self._is_valid_ip(falsified_ip):
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
        
        Retourne:
        {
            "success": true,
            "message": "Cache réinitialisé avec succès"
        }
        """
        self.cache.reset()
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
