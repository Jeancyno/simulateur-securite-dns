"""
Service de cache DNS simulé pour la pédagogie.
Ce cache est stocké en mémoire et ne persiste pas entre les redémarrages.
"""

from datetime import datetime
from enum import Enum


class CacheStatus(Enum):
    """États possibles du cache DNS"""
    CLEAN = "CLEAN"
    POISONED = "POISONED"


class DnsCacheEntry:
    """Entrée de cache DNS"""
    
    def __init__(self, domain: str, ip: str, source: str, status: CacheStatus):
        self.domain = domain
        self.ip = ip
        self.source = source
        self.status = status
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Convertit l'entrée en dictionnaire"""
        return {
            "domain": self.domain,
            "ip": self.ip,
            "source": self.source,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


class DnsCache:
    """Cache DNS simulé en mémoire"""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, domain: str) -> DnsCacheEntry:
        """Récupère une entrée du cache"""
        return self._cache.get(domain)
    
    def set(self, entry: DnsCacheEntry):
        """Ajoute ou met à jour une entrée dans le cache"""
        self._cache[entry.domain] = entry
    
    def exists(self, domain: str) -> bool:
        """Vérifie si une entrée existe dans le cache"""
        return domain in self._cache
    
    def remove(self, domain: str):
        """Supprime une entrée du cache"""
        if domain in self._cache:
            del self._cache[domain]
    
    def reset(self):
        """Réinitialise complètement le cache"""
        self._cache.clear()
    
    def get_status(self, domain: str) -> CacheStatus:
        """Récupère le statut d'une entrée"""
        entry = self.get(domain)
        if entry:
            return entry.status
        return CacheStatus.CLEAN
    
    def get_all_entries(self):
        """Récupère toutes les entrées du cache"""
        return [entry.to_dict() for entry in self._cache.values()]
    
    def is_poisoned(self, domain: str) -> bool:
        """Vérifie si une entrée est empoisonnée"""
        return self.get_status(domain) == CacheStatus.POISONED


# Instance singleton du cache DNS
dns_cache = DnsCache()
